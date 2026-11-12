"""Fond musical « sous-marin » (100 BPM, La mineur, Am-F-C-G) en numpy pur -> WAV stéréo 44,1 kHz.

Usage : python3 musique.py DUREE_S sortie.wav
"""
import sys
import wave

import numpy as np

SR = 44100
BPM = 100
BEAT = 60 / BPM
CHORDS = [  # notes MIDI
    [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62],
]


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def main():
    dur, out = float(sys.argv[1]), sys.argv[2]
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3)
    L = np.zeros(n)
    R = np.zeros(n)
    bar = 4 * BEAT

    # nappe : sinus désaccordés + légère modulation, accord change chaque mesure
    for b in range(int(dur / bar) + 1):
        s0 = int(b * bar * SR)
        s1 = min(n, int((b + 1) * bar * SR) + int(0.3 * SR))
        if s0 >= n:
            break
        tt = np.arange(s1 - s0) / SR
        envp = np.minimum(1, tt / 0.4) * np.minimum(1, (tt[-1] - tt) / 0.3 + 0.0)
        for k, note in enumerate(CHORDS[b % 4]):
            for det, side in ((-0.12, 0), (0.12, 1)):
                f = midi(note + det)
                v = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * 0.05 * envp
                (L if side == 0 else R)[s0:s1] += v
        # basse
        f = midi(CHORDS[b % 4][0] - 12)
        L[s0:s1] += np.sin(2 * np.pi * f * tt) * 0.16 * envp
        R[s0:s1] += np.sin(2 * np.pi * f * tt) * 0.16 * envp

    # arpège pluck en croches
    step = BEAT / 2
    pattern = [0, 1, 2, 1, 2, 0, 1, 2]
    for i in range(int(dur / step)):
        s0 = int(i * step * SR)
        chord = CHORDS[int(i * step / bar) % 4]
        note = chord[pattern[i % 8]] + 12
        m = int(0.5 * SR)
        tt = np.arange(min(m, n - s0)) / SR
        f = midi(note)
        v = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt / 0.18) * 0.09
        pan = 0.5 + 0.35 * np.sin(i * 0.9)
        L[s0:s0 + len(tt)] += v * (1 - pan)
        R[s0:s0 + len(tt)] += v * pan

    # kick doux sur 1 et 3, hi-hat léger sur les contretemps
    for i in range(int(dur / BEAT)):
        s0 = int(i * BEAT * SR)
        if i % 2 == 0:
            m = min(int(0.35 * SR), n - s0)
            tt = np.arange(m) / SR
            fk = 48 + 70 * np.exp(-tt / 0.03)
            k = np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tt / 0.16) * 0.35
            L[s0:s0 + m] += k
            R[s0:s0 + m] += k
        s1 = int((i + 0.5) * BEAT * SR)
        m = min(int(0.06 * SR), n - s1)
        if m > 0:
            h = np.diff(rng.uniform(-1, 1, m + 1)) * np.exp(-np.arange(m) / SR / 0.015) * 0.05
            L[s1:s1 + m] += h * 0.8
            R[s1:s1 + m] += h

    # bulles : petits « bloups » montants aléatoires
    for _ in range(int(dur * 0.6)):
        s0 = int(rng.uniform(0, dur - 0.2) * SR)
        m = int(0.08 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(500, 900) * (1 + 6 * tt)
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1]) * 0.03
        L[s0:s0 + m] += b
        R[s0:s0 + m] += b

    fade = np.minimum(1, np.minimum(t / 1.0, (dur - t) / 1.5))
    st = np.stack([L, R], 1) * fade[:, None]
    st = st / np.abs(st).max() * 0.85
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
