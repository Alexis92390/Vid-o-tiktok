# Générateur de lyric video TikTok (9:16)

Format : rap illustré en dessin vectoriel plat, une scène par ligne, karaoké mot par mot,
mot-clé géant lumineux, outro avec ton pseudo.

```bash
pip install pycairo numpy
cd generator
python3 beat.py 13 beat.wav                          # instru synthétique 90 BPM (13 mesures)
python3 render.py beat.wav ../output/lyric_video.mp4 # vidéo 1080x1920, 30 fps
python3 render.py beat.wav /tmp/prev --preview       # 1 image par scène, pour vérifier vite
```

Personnaliser (dans `generator/render.py`) :
- `LINES` : (texte, mot-clé, scène). Une ligne = une mesure (2,67 s à 90 BPM).
- `HANDLE` : pseudo affiché à la fin.
- Avec ta propre chanson : remplace `beat.wav` par ton audio et règle `BPM` dans `beat.py`
  pour que chaque ligne tombe sur une mesure.

## Version calée sur un son existant (à ajouter ensuite dans TikTok)

```bash
python3 render.py --mute ../output/video_75bpm_sans_son.mp4 --bpm 75 --offset 0.26 --no-text --no-outro
```
`--bpm` : tempo du son, `--offset` : instant du 1er temps (s), `--no-text` : pas de paroles à l'écran,
`--mute` : vidéo sans piste audio.

## Vidéo narrée « Le poulpe » (voix off + sous-titres mot par mot)

Résultat : `output/poulpe_tiktok.mp4` (49,6 s, 1080x1920, voix off FR, sous-titres incrustés, musique de fond).

```bash
pip install pycairo numpy piper-tts onnx onnxruntime
cd generator
python3 voix.py /tmp/work                       # voix Piper fr_FR-siwis + timeline.json (minutage exact de chaque mot)
python3 musique.py 52 /tmp/work/musique.wav     # fond musical synthétisé (libre de droits)
python3 poulpe.py /tmp/work ../output/poulpe_tiktok.mp4
python3 poulpe.py /tmp/work /tmp/prev --preview # 2 images par scène pour vérifier vite
```

- Texte de la voix : `generator/script_poulpe.py` (`LINES` = une scène par phrase, `KEYWORDS` = mots en jaune).
- Le modèle de voix (~63 Mo) est téléchargé depuis huggingface.co au premier lancement dans `generator/models/`.
- Le minutage des sous-titres vient des durées de phonèmes internes au modèle (nœud `/Ceil` exposé dans le graphe ONNX).
