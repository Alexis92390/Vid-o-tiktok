#!/usr/bin/env python3
"""Assemble plusieurs clips 9:16 en une seule vidéo avec des effets « monde des sorciers ».

Effets dessinés image par image (pycairo) par-dessus les clips :
  - bougies flottantes, poussière dorée, vignette chaude ;
  - balais qui traversent l'écran avec traînée d'étincelles ;
  - balle dorée ailée qui zigzague, hibou qui apporte une lettre ;
  - transitions : gros balai + flash doré + gerbe d'étoiles ;
  - éclair au début, texte de fin.
Bruitages (souffles, carillons, hululement) synthétisés et mixés sous la voix.

Usage : python3 magic_montage.py OUT.mp4 clip1.mov clip2.mov ...
"""
import math
import subprocess
import sys
import wave

import cairo
import numpy as np

W, H, FPS = 1080, 1920, 30
SR = 48000
rng = np.random.default_rng(7)

GOLD = (1.0, 0.82, 0.35)
WHITE_GOLD = (1.0, 0.95, 0.75)


def probe_duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                   "-show_entries", "stream=duration", "-of", "csv=p=0", path])
    return float(out.strip())


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- formes
def sparkle(cr, x, y, r, a, color=WHITE_GOLD):
    """Étoile à 4 branches + halo."""
    if a <= 0.01 or r <= 0.3:
        return
    g = cairo.RadialGradient(x, y, 0, x, y, r * 2.6)
    g.add_color_stop_rgba(0, *color, 0.55 * a)
    g.add_color_stop_rgba(1, *color, 0)
    cr.set_source(g)
    cr.arc(x, y, r * 2.6, 0, 2 * math.pi)
    cr.fill()
    cr.set_source_rgba(1, 1, 0.95, a)
    k = r * 0.22
    cr.move_to(x, y - r)
    cr.curve_to(x + k, y - k, x + k, y - k, x + r, y)
    cr.curve_to(x + k, y + k, x + k, y + k, x, y + r)
    cr.curve_to(x - k, y + k, x - k, y + k, x - r, y)
    cr.curve_to(x - k, y - k, x - k, y - k, x, y - r)
    cr.fill()


def draw_broom(cr, x, y, ang, s, wobble):
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(s, s)
    # ombre douce
    cr.set_source_rgba(0, 0, 0, 0.18)
    cr.save(); cr.translate(6, 10); _broom_shape(cr, wobble, shadow=True); cr.restore()
    _broom_shape(cr, wobble)
    cr.restore()


def _broom_shape(cr, wobble, shadow=False):
    # manche
    if not shadow:
        g = cairo.LinearGradient(0, -6, 0, 6)
        g.add_color_stop_rgb(0, 0.55, 0.33, 0.17)
        g.add_color_stop_rgb(0.5, 0.42, 0.24, 0.11)
        g.add_color_stop_rgb(1, 0.25, 0.13, 0.06)
        cr.set_source(g)
    cr.move_to(-70, -5)
    cr.curve_to(40, -7, 150, -4 + wobble, 205, -2 + wobble)
    cr.arc(205, 1 + wobble, 4.5, -math.pi / 2, math.pi / 2)
    cr.curve_to(150, 5 + wobble, 40, 6, -70, 5)
    cr.close_path()
    cr.fill()
    # brindilles (éventail)
    if not shadow:
        g = cairo.LinearGradient(-190, 0, -60, 0)
        g.add_color_stop_rgb(0, 0.78, 0.6, 0.28)
        g.add_color_stop_rgb(1, 0.6, 0.42, 0.18)
        cr.set_source(g)
    cr.move_to(-62, -9)
    cr.curve_to(-110, -16, -150, -34, -195, -40 - wobble * 2)
    cr.curve_to(-185, -10, -185, 10, -195, 40 + wobble * 2)
    cr.curve_to(-150, 34, -110, 16, -62, 9)
    cr.close_path()
    cr.fill()
    if shadow:
        return
    cr.set_line_width(1.6)
    for i in range(-6, 7):
        cr.set_source_rgba(0.4, 0.26, 0.1, 0.55)
        cr.move_to(-66, i * 1.2)
        cr.curve_to(-120, i * 2.5, -160, i * 5, -190 - abs(i) * 0.6, i * 6 + wobble * (i / 6))
        cr.stroke()
    # ligature
    cr.set_source_rgb(0.35, 0.12, 0.08)
    cr.rectangle(-72, -11, 12, 22)
    cr.fill()
    cr.set_source_rgba(1, 0.85, 0.5, 0.35)
    cr.rectangle(-72, -11, 12, 4)
    cr.fill()


def draw_golden_ball(cr, x, y, s, flap):
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    # ailes
    for side in (-1, 1):
        cr.save()
        cr.scale(side, 1)
        cr.translate(10, -2)
        cr.rotate(-0.35 + 0.7 * flap)
        for i, (ln, w) in enumerate([(46, 9), (38, 8), (28, 7)]):
            cr.save()
            cr.rotate(-0.25 + i * 0.22)
            cr.set_source_rgba(0.97, 0.95, 0.88, 0.85)
            cr.save(); cr.scale(ln / 2, w / 2); cr.arc(1, 0, 1, 0, 2 * math.pi); cr.restore()
            cr.fill()
            cr.restore()
        cr.restore()
    g = cairo.RadialGradient(-4, -5, 1, 0, 0, 12)
    g.add_color_stop_rgb(0, 1, 0.97, 0.7)
    g.add_color_stop_rgb(0.5, 0.98, 0.78, 0.25)
    g.add_color_stop_rgb(1, 0.6, 0.4, 0.05)
    cr.set_source(g)
    cr.arc(0, 0, 11, 0, 2 * math.pi)
    cr.fill()
    cr.set_source_rgba(0.55, 0.35, 0.05, 0.6)
    cr.set_line_width(1)
    cr.arc(0, 0, 7, 0.3, 2.8)
    cr.stroke()
    cr.restore()


def draw_owl(cr, x, y, s, flap, t):
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    body = (0.45, 0.36, 0.28)
    dark = (0.28, 0.21, 0.16)
    # lettre tenue dans les serres
    cr.save()
    cr.translate(0, 70)
    cr.rotate(0.12 * math.sin(t * 3))
    cr.set_source_rgb(0.93, 0.87, 0.72)
    cr.rectangle(-30, 0, 60, 40)
    cr.fill()
    cr.set_source_rgba(0.6, 0.5, 0.35, 1)
    cr.set_line_width(1.5)
    cr.move_to(-30, 0); cr.line_to(0, 22); cr.line_to(30, 0); cr.stroke()
    cr.set_source_rgb(0.65, 0.08, 0.08)
    cr.arc(0, 22, 6, 0, 2 * math.pi)
    cr.fill()
    cr.restore()
    cr.set_source_rgb(*dark)
    cr.set_line_width(3)
    for dx in (-8, 8):
        cr.move_to(dx, 45); cr.line_to(dx * 0.8, 72); cr.stroke()
    # ailes
    for side in (-1, 1):
        cr.save()
        cr.scale(side, 1)
        cr.translate(18, -5)
        cr.rotate(-0.9 * flap + 0.2)
        cr.set_source_rgb(*dark)
        cr.move_to(0, 0)
        cr.curve_to(40, -30, 90, -20, 115, 10)
        cr.curve_to(95, 8, 90, 18, 75, 16)
        cr.curve_to(65, 26, 50, 22, 40, 24)
        cr.curve_to(25, 26, 10, 22, 0, 18)
        cr.close_path()
        cr.fill()
        cr.restore()
    # corps
    cr.set_source_rgb(*body)
    cr.save(); cr.scale(28, 42); cr.arc(0, 0.25, 1, 0, 2 * math.pi); cr.restore()
    cr.fill()
    cr.set_source_rgb(0.85, 0.8, 0.7)
    cr.save(); cr.scale(17, 28); cr.arc(0, 0.6, 1, 0, 2 * math.pi); cr.restore()
    cr.fill()
    # tête
    cr.set_source_rgb(*body)
    cr.arc(0, -30, 25, 0, 2 * math.pi)
    cr.fill()
    cr.move_to(-22, -45); cr.line_to(-14, -62); cr.line_to(-8, -48); cr.fill()
    cr.move_to(22, -45); cr.line_to(14, -62); cr.line_to(8, -48); cr.fill()
    for dx in (-10, 10):
        cr.set_source_rgb(0.95, 0.92, 0.85)
        cr.arc(dx, -32, 10, 0, 2 * math.pi); cr.fill()
        cr.set_source_rgb(1, 0.7, 0.1)
        cr.arc(dx, -32, 6, 0, 2 * math.pi); cr.fill()
        cr.set_source_rgb(0.05, 0.05, 0.05)
        cr.arc(dx, -32, 3.5, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgb(0.85, 0.6, 0.15)
    cr.move_to(-4, -24); cr.line_to(4, -24); cr.line_to(0, -15); cr.fill()
    cr.restore()


def draw_candle(cr, x, y, s, t, seed):
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    flick = 1 + 0.12 * math.sin(t * 13 + seed) + 0.08 * math.sin(t * 29 + seed * 2)
    # halo
    cr.set_operator(cairo.OPERATOR_ADD)
    g = cairo.RadialGradient(0, -38, 0, 0, -38, 110 * flick)
    g.add_color_stop_rgba(0, 1, 0.75, 0.35, 0.35)
    g.add_color_stop_rgba(1, 1, 0.6, 0.2, 0)
    cr.set_source(g)
    cr.arc(0, -38, 110 * flick, 0, 2 * math.pi)
    cr.fill()
    cr.set_operator(cairo.OPERATOR_OVER)
    # cire
    g = cairo.LinearGradient(-11, 0, 11, 0)
    g.add_color_stop_rgb(0, 0.82, 0.77, 0.66)
    g.add_color_stop_rgb(0.4, 0.99, 0.96, 0.88)
    g.add_color_stop_rgb(1, 0.75, 0.69, 0.58)
    cr.set_source(g)
    cr.rectangle(-11, -20, 22, 80)
    cr.fill()
    cr.save(); cr.scale(11, 4); cr.arc(0, -5, 1, 0, 2 * math.pi); cr.restore()
    cr.fill()
    cr.set_source_rgb(0.97, 0.94, 0.85)
    cr.move_to(4, -20); cr.curve_to(6, -5, 9, 2, 6, 10); cr.curve_to(3, 2, 2, -5, 0, -20); cr.fill()
    # mèche + flamme
    cr.set_source_rgb(0.15, 0.1, 0.05)
    cr.rectangle(-1, -27, 2, 8)
    cr.fill()
    sway = 2.5 * math.sin(t * 7 + seed)
    fh = 26 * flick
    g = cairo.RadialGradient(0, -30, 1, 0, -32, fh)
    g.add_color_stop_rgba(0, 1, 1, 0.9, 1)
    g.add_color_stop_rgba(0.45, 1, 0.8, 0.3, 0.95)
    g.add_color_stop_rgba(1, 1, 0.45, 0.1, 0)
    cr.set_source(g)
    cr.move_to(0, -24)
    cr.curve_to(9, -28, 6, -40, sway, -24 - fh)
    cr.curve_to(-6, -40, -9, -28, 0, -24)
    cr.fill()
    cr.restore()


def draw_bolt(cr, cx, cy, s, a):
    pts = [(-0.15, -1), (0.35, -1), (0.05, -0.2), (0.4, -0.2), (-0.3, 1), (-0.05, 0.1), (-0.4, 0.1)]
    cr.save()
    cr.translate(cx, cy)
    cr.scale(s, s)
    for lw, col, al in [(0.12, (1, 0.85, 0.4), 0.35), (0.05, (1, 0.95, 0.7), 0.8)]:
        cr.move_to(*pts[0])
        for p in pts[1:]:
            cr.line_to(*p)
        cr.close_path()
        cr.set_line_width(lw)
        cr.set_line_join(cairo.LINE_JOIN_MITER)
        cr.set_source_rgba(*col, al * a)
        cr.stroke_preserve()
        cr.set_source_rgba(1, 0.97, 0.85, 0.9 * a)
        cr.fill()
    cr.restore()


# ---------------------------------------------------------------- trajectoires
def broom_path(ev, t):
    """Position / angle d'un balai pour l'évènement ev au temps t."""
    u = (t - ev["t0"]) / ev["dur"]
    d = ev["dir"]
    x0, x1 = (-400, W + 400) if d > 0 else (W + 400, -400)
    x = x0 + (x1 - x0) * u
    y = ev["y"] + ev["amp"] * math.sin(u * math.pi * ev["waves"]) - ev.get("climb", 0) * u
    return x, y


def snitch_path(ev, t):
    u = (t - ev["t0"]) / ev["dur"]
    cx, cy = ev["cx"], ev["cy"]
    x = cx + 380 * math.sin(u * 2 * math.pi * 1.3 + ev["ph"]) + (u - 0.5) * 900 * ev["dir"]
    y = cy + 140 * math.sin(u * 2 * math.pi * 2.1 + ev["ph"] * 1.7) + 60 * math.sin(u * 37)
    return x, y


def owl_path(ev, t):
    u = (t - ev["t0"]) / ev["dur"]
    d = ev["dir"]
    x = (-250 + (W + 500) * u) if d > 0 else (W + 250 - (W + 500) * u)
    y = ev["y"] + 40 * math.sin(u * 2 * math.pi * 2) - 120 * u
    return x, y


# ---------------------------------------------------------------- scénario
def build_schedule(bounds):
    total = bounds[-1]
    ev = {"brooms": [], "snitch": [], "owl": [], "trans": [], "bursts": []}
    # transitions : gros balai + flash
    for i, b in enumerate(bounds[1:-1]):
        d = 1 if i % 2 == 0 else -1
        ev["trans"].append(b)
        ev["brooms"].append(dict(t0=b - 0.45, dur=0.9, y=H * 0.5, amp=120, waves=1, dir=d,
                                 s=2.6, big=True))
        ev["bursts"].append((b, W / 2, H * 0.5, 1.4))
    # petits balais en arrière-plan (zone haute, loin du visage)
    small = [(2.6, 1), (11.5, -1), (19.0, 1), (19.5, 1), (30.5, -1), (37.5, 1), (46.0, -1),
             (57.0, 1), (57.4, 1)]
    for k, (t0, d) in enumerate(small):
        if t0 + 2.4 < total:
            y = H * (0.13 + 0.12 * ((k * 37) % 5) / 4)
            ev["brooms"].append(dict(t0=t0, dur=2.4, y=y, amp=50, waves=2, dir=d,
                                     s=0.75 + 0.15 * (k % 3), climb=60, big=False))
    for t0, d, cy in [(5.2, 1, H * 0.22), (15.5, -1, H * 0.25), (34.0, 1, H * 0.2), (60.0, -1, H * 0.22)]:
        if t0 + 2.8 < total:
            ev["snitch"].append(dict(t0=t0, dur=2.8, cx=W / 2, cy=cy, dir=d, ph=t0))
    for t0, d in [(23.5, 1), (42.0, -1)]:
        if t0 + 4.5 < total:
            ev["owl"].append(dict(t0=t0, dur=4.5, y=H * 0.2, dir=d))
            ev["bursts"].append((t0 + 2.25, None, None, 0.6))  # étincelles au passage
    return ev


# ---------------------------------------------------------------- rendu image
class Particles:
    def __init__(self, n=55):
        self.x = rng.uniform(0, W, n)
        self.y0 = rng.uniform(0, H, n)
        self.v = rng.uniform(20, 70, n)
        self.r = rng.uniform(3, 9, n)
        self.ph = rng.uniform(0, 2 * math.pi, n)
        self.sw = rng.uniform(15, 45, n)

    def draw(self, cr, t, a):
        for i in range(len(self.x)):
            y = (self.y0[i] - self.v[i] * t) % (H + 40) - 20
            x = self.x[i] + self.sw[i] * math.sin(t * 0.8 + self.ph[i])
            tw = 0.5 + 0.5 * math.sin(t * 3 + self.ph[i] * 3)
            # plus discret au centre (visage)
            cen = 1 - 0.7 * math.exp(-(((x - W / 2) / 300) ** 2 + ((y - H * 0.5) / 420) ** 2))
            sparkle(cr, x, y, self.r[i] * (0.5 + tw), a * 0.55 * tw * cen)


def draw_burst(cr, t, tb, x, y, power):
    u = (t - tb) / 1.1
    if u < 0 or u > 1:
        return
    rr = np.random.default_rng(int(tb * 100))
    n = int(28 * power)
    ang = rr.uniform(0, 2 * math.pi, n)
    spd = rr.uniform(300, 900, n) * power
    rad = rr.uniform(6, 16, n)
    for i in range(n):
        d = spd[i] * (1 - (1 - u) ** 2)
        px = x + math.cos(ang[i]) * d
        py = y + math.sin(ang[i]) * d + 200 * u * u
        sparkle(cr, px, py, rad[i] * (1 - u * 0.6), (1 - u) ** 1.3)


def render_overlay(cr, t, ev, bounds, particles):
    total = bounds[-1]
    intro = ease(t / 1.2)
    # bougies flottantes
    cands = [(130, 250, 0.9, 0), (330, 140, 0.7, 1.3), (760, 170, 0.75, 2.1), (950, 290, 0.95, 3.7),
             (560, 70, 0.55, 5.0)]
    for cx, cy, s, sd in cands:
        bob = 14 * math.sin(t * 1.3 + sd)
        cr.push_group()
        draw_candle(cr, cx, cy + bob, s * 1.3, t, sd)
        cr.pop_group_to_source()
        cr.paint_with_alpha(intro)
    particles.draw(cr, t, intro)

    # balle dorée ailée
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
            draw_golden_ball(cr, x, y, 1.6, 0.5 + 0.5 * math.sin(t * 60))
            cr.pop_group_to_source()
            cr.paint_with_alpha(fade)

    # hibou + lettre
    for e in ev["owl"]:
        if e["t0"] <= t <= e["t0"] + e["dur"]:
            x, y = owl_path(e, t)
            flap = 0.5 + 0.5 * math.sin(t * 9)
            cr.save()
            if e["dir"] < 0:
                cr.translate(2 * x, 0); cr.scale(-1, 1)
            draw_owl(cr, x, y, 1.15, flap, t)
            cr.restore()

    # balais
    for e in ev["brooms"]:
        if e["t0"] <= t <= e["t0"] + e["dur"]:
            x, y = broom_path(e, t)
            x2, y2 = broom_path(e, t + 0.01)
            ang = math.atan2(y2 - y, x2 - x)
            # traînée
            nk = 22 if e["big"] else 14
            for k in range(1, nk):
                tt = t - k * 0.02
                if tt < e["t0"]:
                    break
                px, py = broom_path(e, tt)
                off = -e["dir"] * 150 * e["s"] * 0.5
                jit = 25 * e["s"] * math.sin(k * 2.3 + t * 20)
                sparkle(cr, px + off, py + jit, (10 - k * 0.4) * e["s"] * 0.6,
                        0.8 * (1 - k / nk), GOLD)
            draw_broom(cr, x, y, ang, e["s"], 3 * math.sin(t * 25))

    # transitions : flash doré
    for b in ev["trans"]:
        d = abs(t - b)
        if d < 0.35:
            a = (1 - d / 0.35) ** 2
            cr.set_source_rgba(1, 0.9, 0.6, 0.75 * a)
            cr.paint()
    for tb, bx, by, p in ev["bursts"]:
        if bx is None:
            e = next(o for o in ev["owl"] if abs(o["t0"] + 2.25 - tb) < 1e-6)
            bx, by = owl_path(e, tb)
        draw_burst(cr, t, tb, bx, by, p)

    # éclair d'ouverture
    if t < 0.8:
        a = 1 - t / 0.8
        cr.set_source_rgba(1, 1, 1, 0.9 * a ** 2)
        cr.paint()
        draw_bolt(cr, W / 2, H * 0.32, 330 * (1 + 0.3 * t), a)
    if t < 1.3:
        draw_burst(cr, t, 0.05, W / 2, H * 0.32, 1.6)

    # texte de fin
    te = total - 2.3
    if t > te:
        u = ease((t - te) / 0.6)
        txt = "Méfait accompli"
        cr.select_font_face("DejaVu Serif", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(92)
        ext = cr.text_extents(txt)
        tx, ty = (W - ext.width) / 2 - ext.x_bearing, H * 0.16
        # bandeau parchemin
        cr.set_source_rgba(0.12, 0.07, 0.03, 0.55 * u)
        cr.rectangle(0, ty - 120, W, 175)
        cr.fill()
        cr.save()
        cr.rectangle(0, 0, tx + ext.width * u + 20, H)  # révélation gauche→droite
        cr.clip()
        cr.move_to(tx + 4, ty + 4)
        cr.text_path(txt)
        cr.set_source_rgba(0, 0, 0, 0.6 * u)
        cr.fill()
        cr.move_to(tx, ty)
        cr.text_path(txt)
        g = cairo.LinearGradient(0, ty - 70, 0, ty + 10)
        g.add_color_stop_rgb(0, 1, 0.95, 0.7)
        g.add_color_stop_rgb(1, 0.85, 0.6, 0.2)
        cr.set_source(g)
        cr.fill()
        cr.restore()
        sx = tx + ext.width * u
        if u < 1:
            sparkle(cr, sx, ty - 30, 30, 1)
        for k in range(6):
            sparkle(cr, tx + ext.width * ((k * 0.19 + t * 0.4) % 1), ty - 80 + 100 * ((k * 0.37) % 1),
                    10, u * (0.5 + 0.5 * math.sin(t * 6 + k)))
    # fondu final
    if t > total - 0.35:
        cr.set_source_rgba(0, 0, 0, (t - (total - 0.35)) / 0.35)
        cr.paint()


# ---------------------------------------------------------------- audio
def synth_sfx(ev, total):
    n = int(total * SR) + SR
    out = np.zeros((n, 2))

    def add(sig, t0, pan=0.0):
        i = int(t0 * SR)
        if i < 0:
            sig = sig[-i:]; i = 0
        j = min(n, i + len(sig))
        if j <= i:
            return
        sig = sig[: j - i]
        if sig.ndim == 1:
            l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
            out[i:j, 0] += sig * l
            out[i:j, 1] += sig * r
        else:
            out[i:j] += sig

    def whoosh(dur, gain, d):
        m = int(dur * SR)
        noise = rng.standard_normal(m)
        tt = np.linspace(0, 1, m)
        env = np.exp(-((tt - 0.5) / 0.22) ** 2)
        cutoff = 0.02 + 0.25 * env  # filtre passe-bas variable
        y = np.zeros(m)
        acc = 0.0
        for k in range(m):
            acc += cutoff[k] * (noise[k] - acc)
            y[k] = acc
        y = y / (np.abs(y).max() + 1e-9) * env * gain
        pan = (tt * 2 - 1) * d
        st = np.stack([y * np.cos((pan + 1) * np.pi / 4), y * np.sin((pan + 1) * np.pi / 4)], 1)
        return st

    def chime(gain):
        sig = np.zeros(int(1.6 * SR))
        for k, f in enumerate([1568, 2093, 2637, 3136, 4186]):
            m = len(sig) - int(k * 0.06 * SR)
            tt = np.arange(m) / SR
            tone = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt * 4)
            sig[int(k * 0.06 * SR):] += tone
        return sig / np.abs(sig).max() * gain

    def flutter(dur, gain):
        m = int(dur * SR)
        tt = np.arange(m) / SR
        noise = rng.standard_normal(m)
        hp = np.diff(noise, prepend=0)
        am = 0.5 + 0.5 * np.sin(2 * np.pi * 38 * tt)
        env = np.minimum(1, np.minimum(tt / 0.2, (dur - tt) / 0.3))
        return hp * am * env * gain / 3

    def hoot(gain):
        parts = []
        for f, d in [(390, 0.28), (0, 0.12), (370, 0.5)]:
            tt = np.arange(int(d * SR)) / SR
            if f == 0:
                parts.append(np.zeros_like(tt)); continue
            env = np.sin(np.pi * tt / d) ** 0.7
            parts.append(np.sin(2 * np.pi * f * tt + 3 * np.sin(2 * np.pi * 5 * tt) / 5) * env)
        return np.concatenate(parts) * gain

    for e in ev["brooms"]:
        if e["big"]:
            add(whoosh(e["dur"] + 0.4, 0.55, e["dir"]), e["t0"] - 0.2)
        else:
            add(whoosh(e["dur"], 0.16, e["dir"]), e["t0"])
    for b in ev["trans"]:
        add(chime(0.22), b - 0.05)
    add(chime(0.3), 0.0)
    add(whoosh(0.8, 0.4, 1), 0.0)
    for e in ev["snitch"]:
        add(flutter(e["dur"], 0.1), e["t0"], pan=0.0)
    for e in ev["owl"]:
        add(hoot(0.12), e["t0"] + 1.0, pan=-0.3 * e["dir"])
        add(chime(0.12), e["t0"] + 2.2)
    add(chime(0.25), total - 2.3)
    return np.clip(out, -1, 1)


def write_wav(path, data):
    pcm = (data * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- main
def main():
    out = sys.argv[1]
    clips = sys.argv[2:]
    durs = [probe_duration(c) for c in clips]
    bounds = [0.0]
    for d in durs:
        bounds.append(bounds[-1] + d)
    total = bounds[-1]
    ev = build_schedule(bounds)
    particles = Particles()

    tmp = out + ".tmp"
    sfx_path, voice_path, video_path = tmp + "_sfx.wav", tmp + "_voice.wav", tmp + "_v.mp4"

    # voix : chaque clip normalisé puis concaténé
    inputs = sum([["-i", c] for c in clips], [])
    fc = "".join(f"[{i}:a]aresample={SR},loudnorm=I=-15:TP=-1.5:LRA=11,aresample={SR}[a{i}];"
                 for i in range(len(clips)))
    fc += "".join(f"[a{i}]" for i in range(len(clips))) + f"concat=n={len(clips)}:v=0:a=1[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[a]",
                    "-ac", "2", voice_path], check=True)
    write_wav(sfx_path, synth_sfx(ev, total))

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", video_path], stdin=subprocess.PIPE)
    grade = ("scale=1080:1920:flags=lanczos,fps=30,"
             "eq=contrast=1.07:saturation=0.9:gamma=0.97,"
             "colorbalance=rs=0.05:bs=-0.06:rm=0.04:bm=-0.04:rh=0.03:bh=-0.03,"
             "vignette=angle=PI/4.5,format=bgra")
    canvas = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    frame_bytes = W * H * 4
    fi = 0
    for ci, clip in enumerate(clips):
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", clip, "-vf", grade, "-f", "rawvideo",
                                "-pix_fmt", "bgra", "-"], stdout=subprocess.PIPE)
        nlocal = 0
        while True:
            raw = dec.stdout.read(frame_bytes)
            if len(raw) < frame_bytes:
                break
            t = fi / FPS
            if t >= total:
                break
            buf = bytearray(raw)
            src = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_RGB24, W, H)
            cr = cairo.Context(canvas)
            # zoom lent dans le clip + petit « punch » à l'entrée
            lt = nlocal / FPS
            z = 1.0 + 0.05 * (lt / durs[ci]) + 0.10 * (1 - ease(lt / 0.45))
            cr.translate(W / 2, H * 0.45)
            cr.scale(z, z)
            cr.translate(-W / 2, -H * 0.45)
            cr.set_source_surface(src, 0, 0)
            cr.paint()
            cr.identity_matrix()
            render_overlay(cr, t, ev, bounds, particles)
            canvas.flush()
            enc.stdin.write(bytes(canvas.get_data()))
            fi += 1
            nlocal += 1
            if fi % 150 == 0:
                print(f"  {t:5.1f}/{total:.1f} s", flush=True)
        dec.stdout.close()
        dec.wait()
    enc.stdin.close()
    enc.wait()

    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video_path, "-i", voice_path, "-i", sfx_path,
                    "-filter_complex",
                    "[1:a]volume=1.0[v];[2:a]volume=0.9[s];[v][s]amix=inputs=2:normalize=0:duration=first,"
                    "alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    for p in (sfx_path, voice_path, video_path):
        subprocess.run(["rm", "-f", p])
    print("OK", out, f"{total:.1f} s")


if __name__ == "__main__":
    main()
