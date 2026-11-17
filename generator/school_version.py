#!/usr/bin/env python3
"""Version « oral d'anglais » du montage sorciers.

Par rapport à magic_montage.py :
  - titre d'ouverture et fin en anglais ;
  - cartes infos synchronisées sur ce qui est dit (prénom, âge, ville, matière, maison...) ;
  - longs silences coupés dans le clip 2 (jump cuts masqués par un léger zoom) ;
  - un balai passe quand elle dit « fly », bannière bleu et bronze sur « Ravenclaw » ;
  - balais d'arrière-plan plus gros, flashs de transition plus doux.

Usage : python3 school_version.py OUT.mp4 clip1 clip2 clip3 clip4   (ordre de la présentation)
"""
import math
import subprocess
import sys

import cairo
import numpy as np

import magic_montage as mm
from magic_montage import (W, H, FPS, SR, GOLD, ease, sparkle, draw_broom, draw_golden_ball,
                           draw_owl, draw_candle, draw_bolt, draw_burst, broom_path,
                           snitch_path, owl_path, Particles)

# Passages gardés dans chaque clip (temps locaux, s). None = clip entier.
KEEP = [
    None,
    [(0, 11.82), (13.80, 15.0), (16.03, 20.72), (21.80, 26.73), (28.87, 34.65), (35.47, None)],
    None,
    None,
]

# Cartes : (clip, début local, fin local, petit titre, valeur, style)
CARDS = [
    (0, 2.0, 3.1, "NAME", "Emma", "gold"),
    (0, 3.1, 4.6, "AGE", "12 years old", "gold"),
    (0, 4.7, 8.5, "FROM", "Villeneuve-la-Garenne, France", "gold"),
    (1, 2.1, 9.8, "TALENT", "Creative", "gold"),
    (1, 16.9, 23.5, "PASSION", "Magic", "gold"),
    (1, 23.8, 31.2, "DREAM", "Flying on a broomstick", "gold"),
    (1, 31.5, 36.9, "FAVOURITE SUBJECT", "Potions", "potion"),
    (1, 39.6, 43.1, "FAVOURITE HOUSE", "Ravenclaw", "raven"),
    (2, 0.0, 3.5, "FAVOURITE HOUSE", "Ravenclaw", "raven"),
    (3, 0.8, 7.3, "GOAL", "Learn magic", "gold"),
]


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                   "-show_entries", "stream=duration", "-of", "csv=p=0", path])
    return float(out.strip())


class Timeline:
    """Convertit (clip, temps local) -> temps global, après coupes."""

    def __init__(self, clips):
        self.segs = []          # (clip, local_in, local_out, global_in)
        self.clip_start = []
        g = 0.0
        for ci, c in enumerate(clips):
            d = probe(c)
            keep = KEEP[ci] or [(0, None)]
            self.clip_start.append(g)
            for a, b in keep:
                b = d if b is None else b
                n = round((b - a) * FPS)       # nombre entier d'images
                b = a + n / FPS
                self.segs.append((ci, a, b, g))
                g += b - a
        self.bounds = self.clip_start + [g]
        self.total = g

    def g(self, ci, lt):
        for c, a, b, g0 in self.segs:
            if c == ci and lt <= b:
                return g0 + max(lt, a) - a
        c, a, b, g0 = [s for s in self.segs if s[0] == ci][-1]
        return g0 + b - a


def build_schedule(tl):
    g = tl.g
    ev = {"brooms": [], "snitch": [], "owl": [], "trans": [], "bursts": []}
    for i, b in enumerate(tl.bounds[1:-1]):
        d = 1 if i % 2 == 0 else -1
        ev["trans"].append(b)
        ev["brooms"].append(dict(t0=b - 0.45, dur=0.9, y=H * 0.5, amp=120, waves=1, dir=d,
                                 s=2.6, big=True))
        ev["bursts"].append((b, W / 2, H * 0.5, 1.2))
    small = [((1, 6.0), -1), ((1, 18.0), 1), ((1, 18.4), 1), ((1, 33.0), -1), ((3, 1.5), 1),
             ((3, 1.9), 1)]
    for k, ((ci, lt), d) in enumerate(small):
        y = H * (0.14 + 0.08 * (k % 3))
        ev["brooms"].append(dict(t0=g(ci, lt), dur=2.6, y=y, amp=50, waves=2, dir=d,
                                 s=1.1 + 0.15 * (k % 3), climb=60, big=False))
    # « I would like to fly » : un balai (moyen) traverse
    ev["brooms"].append(dict(t0=g(1, 24.6), dur=1.8, y=H * 0.3, amp=90, waves=1, dir=1, s=1.7,
                             climb=150, big=False))
    for (ci, lt), d in [((0, 5.0), 1), ((1, 9.0), -1), ((1, 29.5), 1), ((3, 4.0), -1)]:
        ev["snitch"].append(dict(t0=g(ci, lt), dur=2.8, cx=W / 2, cy=H * 0.22, dir=d, ph=lt))
    for (ci, lt), d in [((1, 0.3), 1)]:
        t0 = g(ci, lt)
        ev["owl"].append(dict(t0=t0, dur=4.5, y=H * 0.2, dir=d))
        ev["bursts"].append((t0 + 2.25, None, None, 0.6))
    cards = [(g(c, a), g(c, b), k, v, st) for c, a, b, k, v, st in CARDS]
    # étincelles quand « Ravenclaw » apparaît
    ev["bursts"].append((g(1, 39.8), W / 2, H * 0.84, 1.0))
    ev["raven_t"] = g(1, 39.8)
    return ev, cards


def rounded_rect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def draw_potion(cr, x, y, s, t):
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    cr.set_source_rgba(0.85, 0.95, 1, 0.35)
    cr.arc(0, 10, 26, 0, 2 * math.pi)
    cr.fill()
    cr.rectangle(-8, -32, 16, 22)
    cr.fill()
    g = cairo.LinearGradient(0, 0, 0, 36)
    g.add_color_stop_rgb(0, 0.45, 1, 0.55)
    g.add_color_stop_rgb(1, 0.1, 0.55, 0.3)
    cr.set_source(g)
    cr.arc(0, 10, 22, 0.15 * math.pi + 0.05 * math.sin(t * 4), 0.85 * math.pi)
    cr.close_path()
    cr.fill()
    cr.set_source_rgb(0.5, 0.33, 0.18)
    cr.rectangle(-10, -40, 20, 10)
    cr.fill()
    for k in range(4):
        u = ((t * 0.9 + k * 0.27) % 1)
        cr.set_source_rgba(0.6, 1, 0.7, 0.8 * (1 - u))
        cr.arc(6 * math.sin(k * 2 + t * 3), -40 - 50 * u, 4 + 3 * u, 0, 2 * math.pi)
        cr.fill()
    cr.restore()


def draw_card(cr, t, t0, t1, label, value, style):
    if not (t0 - 0.01 <= t <= t1):
        return
    a_in = ease((t - t0) / 0.3)
    a_out = ease((t1 - t) / 0.25)
    a = min(a_in, a_out)
    slide = (1 - a_in) * 60
    cy = H * 0.845 + slide
    cr.select_font_face("DejaVu Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    size = 70
    cr.set_font_size(size)
    ext = cr.text_extents(value)
    while ext.width > W - 200:
        size -= 4
        cr.set_font_size(size)
        ext = cr.text_extents(value)
    bw = max(ext.width + 120, 420)
    if style == "potion":
        bw += 90
    bx, bh = (W - bw) / 2, 175
    by = cy - bh / 2
    if style == "raven":
        fill = [(0.08, 0.16, 0.38), (0.04, 0.08, 0.22)]
        edge, txtc, labc = (0.80, 0.55, 0.30), (0.95, 0.80, 0.55), (0.80, 0.62, 0.40)
    else:
        fill = [(0.20, 0.12, 0.06), (0.10, 0.06, 0.03)]
        edge, txtc, labc = (0.85, 0.65, 0.30), (1, 0.93, 0.72), (0.85, 0.70, 0.45)
    cr.push_group()
    cr.set_source_rgba(0, 0, 0, 0.35)
    rounded_rect(cr, bx + 6, by + 8, bw, bh, 26)
    cr.fill()
    g = cairo.LinearGradient(0, by, 0, by + bh)
    g.add_color_stop_rgba(0, *fill[0], 0.92)
    g.add_color_stop_rgba(1, *fill[1], 0.92)
    cr.set_source(g)
    rounded_rect(cr, bx, by, bw, bh, 26)
    cr.fill_preserve()
    cr.set_line_width(4)
    cr.set_source_rgb(*edge)
    cr.stroke()
    cr.set_line_width(1.5)
    rounded_rect(cr, bx + 10, by + 10, bw - 20, bh - 20, 18)
    cr.stroke()
    # petit titre
    cr.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(30)
    le = cr.text_extents(label)
    cr.set_source_rgb(*labc)
    cr.move_to(W / 2 - le.width / 2 - le.x_bearing, by + 55)
    cr.show_text(label)
    # valeur
    cr.select_font_face("DejaVu Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(size)
    tx = W / 2 - ext.width / 2 - ext.x_bearing + (45 if style == "potion" else 0)
    cr.move_to(tx, by + 135)
    cr.set_source_rgb(*txtc)
    cr.show_text(value)
    if style == "potion":
        draw_potion(cr, tx - 70, by + 105, 1.25, t)
    for k in range(3):
        sparkle(cr, bx + bw * (0.1 + 0.4 * k), by + 4 + 10 * math.sin(t * 2 + k), 12,
                0.5 + 0.5 * math.sin(t * 5 + k * 2))
    cr.pop_group_to_source()
    cr.paint_with_alpha(a)


def render_overlay(cr, t, ev, cards, tl, particles):
    total = tl.total
    intro = ease(t / 1.2)
    for cx, cy, s, sd in [(130, 250, 0.9, 0), (330, 140, 0.7, 1.3), (760, 170, 0.75, 2.1),
                          (950, 290, 0.95, 3.7), (560, 70, 0.55, 5.0)]:
        cr.push_group()
        draw_candle(cr, cx, cy + 14 * math.sin(t * 1.3 + sd), s * 1.3, t, sd)
        cr.pop_group_to_source()
        cr.paint_with_alpha(intro)
    particles.draw(cr, t, intro)

    for e in ev["snitch"]:
        if e["t0"] <= t <= e["t0"] + e["dur"]:
            fade = min(1, (t - e["t0"]) / 0.25, (e["t0"] + e["dur"] - t) / 0.25)
            for k in range(1, 14):
                tt = t - k * 0.018
                if tt >= e["t0"]:
                    px, py = snitch_path(e, tt)
                    sparkle(cr, px, py, 9 - k * 0.5, fade * 0.6 * (1 - k / 14), GOLD)
            x, y = snitch_path(e, t)
            cr.push_group()
            draw_golden_ball(cr, x, y, 1.7, 0.5 + 0.5 * math.sin(t * 60))
            cr.pop_group_to_source()
            cr.paint_with_alpha(fade)

    for e in ev["owl"]:
        if e["t0"] <= t <= e["t0"] + e["dur"]:
            x, y = owl_path(e, t)
            cr.save()
            if e["dir"] < 0:
                cr.translate(2 * x, 0); cr.scale(-1, 1)
            draw_owl(cr, x, y, 1.25, 0.5 + 0.5 * math.sin(t * 9), t)
            cr.restore()

    for e in ev["brooms"]:
        if e["t0"] <= t <= e["t0"] + e["dur"]:
            x, y = broom_path(e, t)
            x2, y2 = broom_path(e, t + 0.01)
            ang = math.atan2(y2 - y, x2 - x)
            nk = 22 if e["big"] else 16
            for k in range(1, nk):
                tt = t - k * 0.02
                if tt < e["t0"]:
                    break
                px, py = broom_path(e, tt)
                off = -e["dir"] * 150 * e["s"] * 0.5
                jit = 25 * e["s"] * math.sin(k * 2.3 + t * 20)
                sparkle(cr, px + off, py + jit, (10 - k * 0.4) * e["s"] * 0.6, 0.8 * (1 - k / nk), GOLD)
            draw_broom(cr, x, y, ang, e["s"], 3 * math.sin(t * 25))

    for t0, t1, lab, val, st in cards:
        draw_card(cr, t, t0, t1, lab, val, st)

    for b in ev["trans"]:
        d = abs(t - b)
        if d < 0.3:
            cr.set_source_rgba(1, 0.9, 0.6, 0.55 * (1 - d / 0.3) ** 2)
            cr.paint()
    for tb, bx, by, p in ev["bursts"]:
        if bx is None:
            e = next(o for o in ev["owl"] if abs(o["t0"] + 2.25 - tb) < 1e-6)
            bx, by = owl_path(e, tb)
        draw_burst(cr, t, tb, bx, by, p)

    # ouverture : éclair + titre anglais
    if t < 0.8:
        a = 1 - t / 0.8
        cr.set_source_rgba(1, 1, 1, 0.85 * a ** 2)
        cr.paint()
        draw_bolt(cr, W / 2, H * 0.30, 300 * (1 + 0.3 * t), a)
    if t < 1.3:
        draw_burst(cr, t, 0.05, W / 2, H * 0.30, 1.4)
    if t < 2.0:
        a = min(ease(t / 0.4), ease((2.0 - t) / 0.35))
        title_banner(cr, "My Hogwarts Application", H * 0.30, a, t)

    te = total - 2.0
    if t > te:
        u = ease((t - te) / 0.6)
        title_banner(cr, "Mischief managed!", H * 0.30, u, t, reveal=u)
    if t > total - 0.35:
        cr.set_source_rgba(0, 0, 0, (t - (total - 0.35)) / 0.35)
        cr.paint()


def title_banner(cr, txt, y, a, t, reveal=1.0):
    if a <= 0:
        return
    cr.select_font_face("DejaVu Serif", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
    size = 86
    cr.set_font_size(size)
    ext = cr.text_extents(txt)
    while ext.width > W - 120:
        size -= 2
        cr.set_font_size(size)
        ext = cr.text_extents(txt)
    tx = (W - ext.width) / 2 - ext.x_bearing
    cr.push_group()
    cr.set_source_rgba(0.12, 0.07, 0.03, 0.6)
    cr.rectangle(0, y - 115, W, 165)
    cr.fill()
    cr.set_source_rgba(0.85, 0.65, 0.3, 0.9)
    cr.rectangle(0, y - 115, W, 3); cr.fill()
    cr.rectangle(0, y + 47, W, 3); cr.fill()
    cr.save()
    cr.rectangle(0, 0, tx + ext.width * reveal + 20, H)
    cr.clip()
    cr.move_to(tx + 4, y + 4); cr.text_path(txt)
    cr.set_source_rgba(0, 0, 0, 0.6); cr.fill()
    cr.move_to(tx, y); cr.text_path(txt)
    g = cairo.LinearGradient(0, y - 70, 0, y + 10)
    g.add_color_stop_rgb(0, 1, 0.95, 0.7)
    g.add_color_stop_rgb(1, 0.85, 0.6, 0.2)
    cr.set_source(g); cr.fill()
    cr.restore()
    if reveal < 1:
        sparkle(cr, tx + ext.width * reveal, y - 30, 30, 1)
    for k in range(6):
        sparkle(cr, tx + ext.width * ((k * 0.19 + t * 0.4) % 1), y - 80 + 100 * ((k * 0.37) % 1),
                10, 0.5 + 0.5 * math.sin(t * 6 + k))
    cr.pop_group_to_source()
    cr.paint_with_alpha(a)


def main():
    out, clips = sys.argv[1], sys.argv[2:]
    tl = Timeline(clips)
    ev, cards = build_schedule(tl)
    particles = Particles()
    tmp = out + ".tmp"
    sfx_path, voice_path, video_path = tmp + "_sfx.wav", tmp + "_voice.wav", tmp + "_v.mp4"

    # voix : chaque passage gardé, micro-fondus anti-clic, normalisé par clip
    args, fc, labels = [], "", []
    for i, (ci, a, b, _) in enumerate(tl.segs):
        args += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", clips[ci]]
        d = b - a
        fc += (f"[{i}:a]aresample={SR},apad,atrim=0:{d:.3f},afade=t=in:d=0.015,"
               f"afade=t=out:st={max(0, d - 0.02):.3f}:d=0.02[s{i}];")
    # regroupe par clip pour normaliser chaque clip
    for ci in range(len(clips)):
        idx = [i for i, s in enumerate(tl.segs) if s[0] == ci]
        fc += "".join(f"[s{i}]" for i in idx) + f"concat=n={len(idx)}:v=0:a=1,loudnorm=I=-15:TP=-1.5:LRA=11,aresample={SR}[c{ci}];"
        labels.append(f"[c{ci}]")
    fc += "".join(labels) + f"concat=n={len(clips)}:v=0:a=1[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", fc, "-map", "[a]",
                    "-ac", "2", voice_path], check=True)
    sfx = mm.synth_sfx(ev, tl.total)
    mm.write_wav(sfx_path, sfx)

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", video_path],
                           stdin=subprocess.PIPE)
    grade = ("scale=1080:1920:flags=lanczos,fps=30,eq=contrast=1.07:saturation=0.9:gamma=0.97,"
             "colorbalance=rs=0.05:bs=-0.06:rm=0.04:bm=-0.04:rh=0.03:bh=-0.03,"
             "vignette=angle=PI/4.5,format=bgra")
    canvas = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    fb = W * H * 4
    last = None
    seg_in_clip = {}
    for si, (ci, a, b, g0) in enumerate(tl.segs):
        k = seg_in_clip.get(ci, 0)
        seg_in_clip[ci] = k + 1
        n = round((b - a) * FPS)
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", clips[ci],
                                "-vf", grade, "-frames:v", str(n), "-f", "rawvideo",
                                "-pix_fmt", "bgra", "-"], stdout=subprocess.PIPE)
        clip_dur = tl.bounds[ci + 1] - tl.bounds[ci]
        for j in range(n):
            raw = dec.stdout.read(fb)
            if len(raw) < fb:
                raw = last  # fin de clip un peu courte : on fige la dernière image
            last = raw
            t = g0 + j / FPS
            src = cairo.ImageSurface.create_for_data(bytearray(raw), cairo.FORMAT_RGB24, W, H)
            cr = cairo.Context(canvas)
            lt = t - tl.bounds[ci]
            z = 1.0 + 0.05 * (lt / clip_dur)
            if k == 0:
                z += 0.10 * (1 - ease(lt / 0.45))      # punch à l'entrée du clip
            elif k % 2 == 1:
                z += 0.07                               # jump cut : cadrage plus serré
            cr.translate(W / 2, H * 0.45)
            cr.scale(z, z)
            cr.translate(-W / 2, -H * 0.45)
            cr.set_source_surface(src, 0, 0)
            cr.paint()
            cr.identity_matrix()
            render_overlay(cr, t, ev, cards, tl, particles)
            canvas.flush()
            enc.stdin.write(bytes(canvas.get_data()))
        dec.stdout.close()
        dec.wait()
        print(f"  segment {si + 1}/{len(tl.segs)}", flush=True)
    enc.stdin.close()
    enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video_path, "-i", voice_path, "-i", sfx_path,
                    "-filter_complex",
                    "[2:a]volume=0.8[s];[1:a][s]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    for p in (sfx_path, voice_path, video_path):
        subprocess.run(["rm", "-f", p])
    print("OK", out, f"{tl.total:.1f} s")


if __name__ == "__main__":
    main()
