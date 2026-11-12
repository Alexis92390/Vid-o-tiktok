"""Voix off française (Piper, voix « siwis ») + minutage exact de chaque mot.

Usage : python3 voix.py SORTIE_DIR
Produit SORTIE_DIR/voix.wav et SORTIE_DIR/timeline.json.

Le minutage vient du modèle lui-même : on expose le tenseur interne des durées
de phonèmes (nœud /Ceil du graphe ONNX), donc chaque mot est calé à l'échantillon près.
"""
import json
import os
import sys
import urllib.request
import wave

import numpy as np
import onnx
import onnxruntime as ort
from piper import PiperVoice

from script_poulpe import LINES

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
VOICE = "fr_FR-siwis-medium"
URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/"
HOP = 256              # échantillons audio par trame de durée
LENGTH = 0.86          # < 1 = débit plus rapide (rythme TikTok)
GAP_SENT = 0.22        # silence entre deux phrases d'une même scène (s)
GAP_LINE = 0.30        # silence entre deux scènes (s)
LEAD_IN = 0.15
PUNCT = set(",.;:!?…-")


def ensure_model():
    os.makedirs(MODELS, exist_ok=True)
    base = os.path.join(MODELS, VOICE)
    for ext in (".onnx", ".onnx.json"):
        if not os.path.exists(base + ext):
            print("téléchargement", VOICE + ext)
            urllib.request.urlretrieve(URL + VOICE + ext, base + ext)
    dur = base + ".dur.onnx"
    if not os.path.exists(dur):
        m = onnx.load(base + ".onnx")
        m.graph.output.append(onnx.helper.make_tensor_value_info("/Ceil_output_0", onnx.TensorProto.FLOAT, None))
        onnx.save(m, dur)
    return base + ".onnx", dur


def clean(tok):
    return tok.strip(",.;:!?…«»\"")


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    model, dur_model = ensure_model()
    pv = PiperVoice.load(model)
    sr = pv.config.sample_rate
    sess = ort.InferenceSession(dur_model)
    scales = np.array([0.667, LENGTH, 0.8], dtype=np.float32)

    audio = [np.zeros(int(LEAD_IN * sr), dtype=np.float32)]
    t = LEAD_IN
    timeline = []
    for scene, text in LINES:
        tokens = [w for w in text.split() if clean(w)]
        sentences = pv.phonemize(text)
        words, phon = [], []
        line_start = t
        for si, ph in enumerate(sentences):
            ids = pv.phonemes_to_ids(ph)
            wav, d = sess.run(None, {
                "input": np.array([ids], dtype=np.int64),
                "input_lengths": np.array([len(ids)], dtype=np.int64),
                "scales": scales,
            })
            wav = wav.flatten()
            d = d.flatten() * HOP / sr
            # ids = [^, _, p1, _, p2, _, ..., pN, _, $] -> phonème i aux indices 2+2i et 3+2i
            cur = t + d[0] + d[1]
            groups, acc_s, acc_e = [], None, None
            for i, p in enumerate(ph):
                a = cur
                cur += d[2 + 2 * i] + d[3 + 2 * i]
                if p == " ":
                    if acc_s is not None:
                        groups.append((acc_s, acc_e))
                    acc_s = None
                    continue
                if p in PUNCT:
                    continue
                phon.append((a, cur))
                if acc_s is None:
                    acc_s = a
                acc_e = cur
            if acc_s is not None:
                groups.append((acc_s, acc_e))
            words.append(groups)
            peak = np.abs(wav).max()
            audio.append(wav / max(peak, 1e-6) * 0.9)
            t += len(wav) / sr
            if si < len(sentences) - 1:
                audio.append(np.zeros(int(GAP_SENT * sr), dtype=np.float32))
                t += GAP_SENT
        groups = [g for s in words for g in s]
        if len(groups) != len(tokens):
            # espeak a fusionné des mots (« parce qu'il ») : on découpe la suite de phonèmes
            # au prorata du nombre de phonèmes de chaque mot prononcé seul
            n = [max(1, sum(1 for s in pv.phonemize(clean(w)) for p in s if p != " " and p not in PUNCT)) for w in tokens]
            cut = np.round(np.concatenate([[0], np.cumsum(n)]) / sum(n) * len(phon)).astype(int)
            cut = np.minimum(cut, len(phon) - 1)
            groups = [(phon[cut[k]][0], phon[max(cut[k + 1] - 1, cut[k])][1]) for k in range(len(tokens))]
            print(f"[{scene}] mots fusionnés par espeak -> découpage phonétique")
        timeline.append({
            "scene": scene, "text": text, "start": line_start, "end": t,
            "words": [{"w": w, "s": round(float(a), 3), "e": round(float(b), 3)} for w, (a, b) in zip(tokens, groups)],
        })
        audio.append(np.zeros(int(GAP_LINE * sr), dtype=np.float32))
        t += GAP_LINE

    pcm = (np.concatenate(audio) * 32767).astype(np.int16)
    with wave.open(os.path.join(out_dir, "voix.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    with open(os.path.join(out_dir, "timeline.json"), "w") as f:
        json.dump({"total": t, "lines": timeline}, f, ensure_ascii=False, indent=1)
    print(f"voix : {t:.1f} s, {len(timeline)} scènes")


if __name__ == "__main__":
    main()
