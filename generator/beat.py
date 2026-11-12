"""Synthèse d'une instru rap (90 BPM, Do mineur) en numpy pur -> WAV stéréo."""
import sys
import wave

import numpy as np

SR = 44100
BPM = 90
BEAT = 60 / BPM
BAR = 4 * BEAT
STEP = BEAT / 4  # double-croche


def env(n, decay):
    return np.exp(-np.arange(n) / SR / decay)


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.22) * 1.0


def snare(rng):
    n = int(0.25 * SR)
    noise = rng.uniform(-1, 1, n)
    noise = np.diff(noise, prepend=0) * 0.6
    tone = np.sin(2 * np.pi * 190 * np.arange(n) / SR)
    return (noise * env(n, 0.09) + tone * env(n, 0.05) * 0.5) * 0.7


def clap(rng):
    n = int(0.2 * SR)
    out = np.zeros(n)
    for off in (0, 0.011, 0.022):
        o = int(off * SR)
        m = n - o
        out[o:] += np.diff(rng.uniform(-1, 1, m), prepend=0) * env(m, 0.03 if off < 0.02 else 0.08)
    return out * 0.35


def hat(rng, decay=0.035, amp=0.22):
    n = int(0.08 * SR)
    x = np.diff(np.diff(rng.uniform(-1, 1, n), prepend=0), prepend=0)
    return x * env(n, decay) * amp


def b808(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-t / 0.03))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.9)
    return np.tanh(x * 2.2) * 0.55


def onepole_lp(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for d in (-0.15, 0.15):
            x += 2 * ((t * f * (1 + d / 100)) % 1) - 1
    x /= len(freqs) * 2
    att = np.minimum(1, t / 0.25)
    rel = np.minimum(1, (dur - t) / 0.4).clip(0, 1)
    x = onepole_lp(x, 0.05)
    return x * att * rel * 0.32


def pluck(freq):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)
    return x * env(n, 0.18) * 0.16


def note(semi_from_a4):
    return 440 * 2 ** (semi_from_a4 / 12)


# Do mineur : Cm - Ab - Eb - Bb
PROG = [
    (note(-33), [note(-9), note(-6), note(-2)]),   # C2 ; C4 Eb4 G4
    (note(-37), [note(-13), note(-9), note(-6)]),  # Ab1 ; Ab3 C4 Eb4
    (note(-30), [note(-6), note(-2), note(1)]),    # Eb2 ; Eb4 G4 Bb4
    (note(-35), [note(-11), note(-7), note(-4)]),  # Bb1 ; Bb3 D4 F4
]
# arpège pentatonique (Do mineur) sur 16 pas, -1 = silence
ARP = [3, -1, 6, 10, -1, 6, 3, -1, 1, -1, 3, 6, -1, 10, 8, -1]


def render(n_bars, out_path, seed=7):
    rng = np.random.default_rng(seed)
    total = int((n_bars * BAR + 1.5) * SR)
    L = np.zeros(total)
    R = np.zeros(total)

    def add(sig, t, pan=0.0, gain=1.0):
        i = int(t * SR)
        j = min(total, i + len(sig))
        s = sig[: j - i] * gain
        L[i:j] += s * (1 - max(0, pan))
        R[i:j] += s * (1 + min(0, pan))

    K = kick()
    for b in range(n_bars):
        t0 = b * BAR
        root, chord = PROG[b % 4]
        outro = b == n_bars - 1
        add(pad(chord, BAR), t0, gain=1.0)
        if not outro:
            for s, semi in enumerate(ARP):
                if semi >= 0 and (b > 0 or s < 8):
                    add(pluck(note(semi - 9 + 12)), t0 + s * STEP, pan=0.35 if s % 2 else -0.35)
        if b == 0 or outro:
            # intro / outro : hats seuls
            for s in range(0, 16, 2):
                add(hat(rng, amp=0.12), t0 + s * STEP, pan=0.2)
            continue
        for s in (0, 7, 10):
            add(K, t0 + s * STEP)
        add(b808(root, BEAT * 1.8), t0)
        add(b808(root, BEAT * 1.2), t0 + 10 * STEP)
        for s in (4, 12):
            add(snare(rng), t0 + s * STEP)
            add(clap(rng), t0 + s * STEP, pan=0.1)
        roll = b % 2 == 1
        for s in range(16):
            if s % 2 == 0 or (roll and s >= 12):
                add(hat(rng, amp=0.2 if s % 4 == 0 else 0.14), t0 + s * STEP, pan=0.25)
            if roll and s >= 14:
                for k in (1, 2):  # triolets
                    add(hat(rng, amp=0.1), t0 + (s + k / 3) * STEP, pan=0.25)

    mix = np.stack([L, R], axis=1)
    mix = np.tanh(mix * 1.1)
    mix /= np.abs(mix).max() / 0.89
    fade = int(1.0 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    data = (mix * 32767).astype("<i2")
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    render(int(sys.argv[1]) if len(sys.argv) > 1 else 13, sys.argv[2] if len(sys.argv) > 2 else "beat.wav")
