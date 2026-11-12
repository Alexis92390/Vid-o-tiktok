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
