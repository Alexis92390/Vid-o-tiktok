"""Vidéo TikTok 9:16 narrée : « Le poulpe, l'animal le plus étrange de l'océan ».

Usage :
  python3 voix.py WORK && python3 musique.py 52 WORK/musique.wav
  python3 poulpe.py WORK sortie.mp4 [--preview]
WORK contient voix.wav, timeline.json, musique.wav (produits par voix.py et musique.py).
"""
import colorsys
import json
import math
import os
import random
import subprocess
import sys

import cairo

from render import ease_io, ease_out_back, glow_circle, hexc, lerp, rrect, sparkle, src
from script_poulpe import KEYWORDS

W, H, FPS = 1080, 1920, 30
FONT = "Inter Display Black"
TAIL = 1.4  # secondes gardées après la fin de la voix

INK = hexc("0B1026")
WHITE = hexc("FFFFFF")
YELLOW = hexc("FFD23F")
BODY = hexc("FF6B8B")
BODY_D = hexc("D93A63")
BODY_L = hexc("FFB3C4")
BLUE = hexc("3DA9FF")
BLUE_D = hexc("1565C0")
RED = hexc("FF3B4E")
GREEN = hexc("3DFFA2")
SAND = hexc("E8C27A")
SAND_D = hexc("C99A4E")


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


# ---------------------------------------------------------------- texte
def text_path_w(c, s, size):
    c.select_font_face(FONT)
    c.set_font_size(size)
    return c.text_extents(s).x_advance


def txt(c, s, x, y, size, fill=WHITE, a=1.0, scale=1.0, stroke=INK, lw=None, glow=None, anchor="c", shadow=True):
    """Texte gras centré verticalement sur y, contour épais (style sous-titre TikTok)."""
    if a <= 0 or scale <= 0.001:
        return
    c.save()
    c.select_font_face(FONT)
    c.set_font_size(size)
    w = c.text_extents(s).x_advance
    c.translate(x, y)
    c.scale(scale, scale)
    ox = -w / 2 if anchor == "c" else 0
    c.move_to(ox, size * 0.36)
    c.text_path(s)
    path = c.copy_path()
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    if glow:
        for i in range(6, 0, -1):
            src(c, glow, 0.08 * a)
            c.set_line_width(size * 0.06 * i)
            c.stroke_preserve()
    if shadow:
        c.save(); c.translate(0, size * 0.07)
        c.new_path(); c.append_path(path)
        src(c, INK, 0.55 * a); c.set_line_width(lw or size * 0.2); c.stroke_preserve(); c.fill()
        c.restore()
        c.new_path(); c.append_path(path)
    if stroke:
        src(c, stroke, a)
        c.set_line_width(lw or size * 0.18)
        c.stroke_preserve()
    src(c, fill, a)
    c.fill()
    c.restore()


def pop(x, d=0.3):
    return ease_out_back(x / d) if x > 0 else 0.0


# ---------------------------------------------------------------- décor océan
rnd = random.Random(7)
PARTICLES = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1.5, 5), rnd.uniform(0.2, 1)) for _ in range(90)]
BUBBLES = [(rnd.uniform(0, W), rnd.uniform(0, 1), rnd.uniform(6, 22), rnd.uniform(60, 160)) for _ in range(26)]


def ocean(c, t, depth=0.5, tint=None):
    top = [lerp(a, b, depth) for a, b in zip(hexc("1E8FC7"), hexc("06244A"))]
    bot = [lerp(a, b, depth) for a, b in zip(hexc("063A6B"), hexc("020A1C"))]
    if tint:
        top = [lerp(a, b, 0.35) for a, b in zip(top, tint)]
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *top[:3])
    g.add_color_stop_rgb(1, *bot[:3])
    c.set_source(g)
    c.paint()
    # rayons de lumière
    for i in range(5):
        x0 = 120 + i * 220 + 60 * math.sin(t * 0.4 + i)
        a = (0.07 + 0.04 * math.sin(t * 0.7 + i * 2)) * (1 - depth * 0.7)
        g = cairo.LinearGradient(0, 0, 0, H * 0.85)
        g.add_color_stop_rgba(0, 1, 1, 1, a)
        g.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.set_source(g)
        c.move_to(x0 - 40, -10); c.line_to(x0 + 40, -10)
        c.line_to(x0 + 260 + 40 * i, H * 0.85); c.line_to(x0 + 60 + 20 * i, H * 0.85)
        c.close_path(); c.fill()
    # plancton
    for (x, y, r, sp) in PARTICLES:
        yy = (y - t * 18 * sp) % H
        xx = x + 10 * math.sin(t * sp + y)
        src(c, WHITE, 0.10 + 0.15 * sp)
        c.arc(xx, yy, r * 0.6, 0, 2 * math.pi); c.fill()
    # bulles
    for (x, y0, r, sp) in BUBBLES:
        yy = H + 50 - ((y0 * (H + 100) + t * sp) % (H + 100))
        xx = x + 14 * math.sin(t * 2 + x)
        src(c, WHITE, 0.25); c.set_line_width(2.5)
        c.arc(xx, yy, r, 0, 2 * math.pi); c.stroke()
        src(c, WHITE, 0.45)
        c.arc(xx - r * 0.35, yy - r * 0.35, r * 0.25, 0, 2 * math.pi); c.fill()


def sand(c, y, t):
    c.move_to(0, y)
    for x in range(0, W + 41, 40):
        c.line_to(x, y + 14 * math.sin(x * 0.012 + 1.3))
    c.line_to(W, H); c.line_to(0, H); c.close_path()
    src(c, SAND); c.fill()
    rr = random.Random(3)
    for _ in range(40):
        src(c, SAND_D, 0.6)
        c.arc(rr.uniform(0, W), rr.uniform(y + 30, H), rr.uniform(3, 8), 0, 2 * math.pi); c.fill()
    # algues
    for k, bx in enumerate((90, 200, 880, 990)):
        src(c, hexc("1FA37A") if k % 2 else hexc("168A66"))
        c.set_line_width(22); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(bx, y + 20)
        for j in range(1, 8):
            c.line_to(bx + 22 * math.sin(t * 1.6 + j * 0.7 + k), y + 20 - j * 45)
        c.stroke()


# ---------------------------------------------------------------- formes
def heart(c, x, y, s, col, a=1.0, outline=True):
    if s <= 0.001:
        return
    c.save(); c.translate(x, y); c.scale(s / 100, s / 100)
    c.move_to(0, 35)
    c.curve_to(-10, 25, -60, 0, -60, -30)
    c.curve_to(-60, -60, -20, -70, 0, -40)
    c.curve_to(20, -70, 60, -60, 60, -30)
    c.curve_to(60, 0, 10, 25, 0, 35)
    c.close_path()
    src(c, col, a)
    c.fill_preserve()
    if outline:
        src(c, INK, a); c.set_line_width(9); c.stroke()
    else:
        c.new_path()
    src(c, WHITE, 0.5 * a)
    c.arc(-30, -35, 10, 0, 2 * math.pi); c.fill()
    c.restore()


def drop(c, x, y, s, col, a=1.0):
    if s <= 0.001:
        return
    c.save(); c.translate(x, y); c.scale(s / 100, s / 100)
    c.move_to(0, -110)
    c.curve_to(30, -60, 70, -10, 70, 30)
    c.curve_to(70, 70, 38, 100, 0, 100)
    c.curve_to(-38, 100, -70, 70, -70, 30)
    c.curve_to(-70, -10, -30, -60, 0, -110)
    c.close_path()
    src(c, col, a); c.fill_preserve()
    src(c, INK, a); c.set_line_width(8); c.stroke()
    src(c, WHITE, 0.55 * a)
    c.save(); c.translate(-30, 20); c.scale(1, 1.8); c.arc(0, 0, 12, 0, 2 * math.pi); c.restore(); c.fill()
    c.restore()


def element_tile(c, x, y, s, sym, num, name, col, a=1.0):
    if s <= 0.001:
        return
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -110, -130, 220, 260, 28)
    src(c, col, a); c.fill_preserve()
    src(c, INK, a); c.set_line_width(9); c.stroke()
    txt(c, num, -62, -88, 40, WHITE, a, stroke=None, shadow=False)
    txt(c, sym, 0, -5, 120, WHITE, a, lw=14, shadow=False)
    txt(c, name, 0, 90, 38, WHITE, a, stroke=None, shadow=False)
    c.restore()


def arm_points(i, t, mode, length=330, n=20):
    """Polyligne d'un bras (repère local du poulpe, tête de rayon ~150)."""
    k = i - 3.5
    bx, by = k * 26, 95
    if mode == "swim":
        ang = math.pi / 2 + k * 0.07
        amp, freq = 0.07, 7
    elif mode == "crawl":
        ang = math.pi / 2 + k * 0.42
        amp, freq = 0.10, 3
    elif mode == "wave" and i == 7:
        ang = -0.2
        amp, freq = 0.0, 0
    else:
        ang = math.pi / 2 + k * 0.30
        amp, freq = 0.11, 2.2
    seg = length / n
    pts = [(bx, by)]
    x, y = bx, by
    curl = (1 if k > 0 else -1) * 0.022
    for j in range(n):
        u = j / n
        if mode == "wave" and i == 7:
            ang += -0.07 + 0.09 * math.sin(t * 7 - j * 0.4)
        else:
            ang += amp * math.sin(t * freq + i * 0.9 - j * 0.45) + curl * u * 6 * (0.3 if mode == "swim" else 1)
        x += seg * math.cos(ang)
        y += seg * math.sin(ang)
        pts.append((x, y))
    return pts


def draw_arm(c, pts, col, dark, w0=30, suckers=False, sucker_lit=None):
    n = len(pts) - 1
    left, right = [], []
    for j, (x, y) in enumerate(pts):
        x2, y2 = pts[min(j + 1, n)]
        x1, y1 = pts[max(j - 1, 0)]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = w0 * (1 - j / n) ** 0.8 + 3
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    c.move_to(*left[0])
    for p in left[1:]:
        c.line_to(*p)
    for p in reversed(right):
        c.line_to(*p)
    c.close_path()
    src(c, col); c.fill_preserve()
    src(c, INK); c.set_line_width(6); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
    if suckers:
        for j in range(1, n - 2, 2):
            x, y = right[j]
            x0, y0 = pts[j]
            sx, sy = lerp(x0, x, 0.55), lerp(y0, y, 0.55)
            r = w0 * 0.32 * (1 - j / n) + 2.5
            lit = sucker_lit(j / n) if sucker_lit else 0
            if lit > 0:
                glow_circle(c, sx, sy, r * 4, YELLOW, 0.6 * lit)
            src(c, BODY_L if lit <= 0 else YELLOW)
            c.arc(sx, sy, r, 0, 2 * math.pi); c.fill_preserve()
            src(c, dark); c.set_line_width(2.5); c.stroke()


def octopus(c, x, y, s, t, mode="idle", body=BODY, dark=BODY_D, expr="happy", look=(0, 0), tilt=0.0, alpha=1.0):
    if s <= 0.001:
        return
    if alpha < 1:
        c.push_group()
    c.save()
    c.translate(x, y); c.rotate(tilt); c.scale(s, s)
    # bras arrière puis avant
    for i in list(range(1, 8, 2)) + list(range(0, 8, 2)):
        col = dark if i % 2 else body
        draw_arm(c, arm_points(i, t, mode), col, dark, suckers=(i % 2 == 0))
    # manteau
    c.save(); c.translate(0, -40); c.scale(1.0, 1.18)
    c.arc(0, 0, 150, 0, 2 * math.pi); c.restore()
    g = cairo.RadialGradient(-50, -120, 20, 0, -40, 200)
    g.add_color_stop_rgb(0, *[lerp(a, 1, 0.35) for a in body[:3]])
    g.add_color_stop_rgb(1, *body[:3])
    c.set_source(g); c.fill_preserve()
    src(c, INK); c.set_line_width(8); c.stroke()
    for (sx, sy, r) in ((-60, -140, 16), (40, -170, 11), (75, -95, 14), (-85, -60, 9), (10, -115, 8)):
        src(c, dark, 0.55); c.arc(sx, sy, r, 0, 2 * math.pi); c.fill()
    # yeux
    blink = 1.0
    ph = (t * 0.7) % 3.1
    if ph < 0.12:
        blink = abs(ph - 0.06) / 0.06
    for ex in (-58, 58):
        c.save(); c.translate(ex, 25); c.scale(1, max(blink, 0.08))
        src(c, WHITE); c.arc(0, 0, 40, 0, 2 * math.pi); c.fill_preserve()
        src(c, INK); c.set_line_width(6); c.stroke()
        if expr == "sad":
            src(c, INK); c.arc(look[0] * 12, 8 + look[1] * 12, 20, 0, 2 * math.pi); c.fill()
        else:
            src(c, INK); c.arc(look[0] * 12, look[1] * 12, 22, 0, 2 * math.pi); c.fill()
        src(c, WHITE); c.arc(look[0] * 12 - 8, look[1] * 12 - 9, 7, 0, 2 * math.pi); c.fill()
        c.restore()
        if expr == "sad":
            src(c, INK); c.set_line_width(7); c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.move_to(ex - 30 * (1 if ex < 0 else -1), -22); c.line_to(ex + 25 * (1 if ex < 0 else -1), -40); c.stroke()
    # joues + bouche
    for ex in (-100, 100):
        src(c, hexc("FF3D6E"), 0.45); c.save(); c.translate(ex, 70); c.scale(1.4, 1); c.arc(0, 0, 16, 0, 2 * math.pi); c.restore(); c.fill()
    src(c, INK); c.set_line_width(7); c.set_line_cap(cairo.LINE_CAP_ROUND)
    if expr == "sad":
        c.arc(0, 98, 18, math.pi * 1.15, math.pi * 1.85)
    elif expr == "wow":
        c.new_sub_path(); c.arc(0, 82, 14, 0, 2 * math.pi)
    else:
        c.arc(0, 66, 22, math.pi * 0.15, math.pi * 0.85)
    c.stroke()
    c.restore()
    if alpha < 1:
        c.pop_group_to_source()
        c.paint_with_alpha(alpha)


def title(c, s, lt0, y=330, size=110, col=YELLOW, glow=None, sub=None):
    if lt0 <= 0:
        return
    sc = pop(lt0, 0.35)
    while text_path_w(c, s, size) > 960:
        size -= 4
    txt(c, s, W / 2, y, size, col, scale=sc, glow=glow, lw=size * 0.2)
    if sub:
        txt(c, sub, W / 2, y + size * 0.85, size * 0.42, WHITE, a=clamp((lt0 - 0.2) / 0.3))


# ---------------------------------------------------------------- scènes
class Scene:
    def __init__(self, line, t, nxt):
        self.line = line
        self.start = line["start"]
        self.end = nxt
        self.dur = nxt - self.start
        self.t = t
        self.lt = t - self.start
        self.p = clamp(self.lt / self.dur)

    def at(self, word, k=0):
        """Instant local du k-ième mot contenant `word` (insensible à la casse)."""
        hits = [w for w in self.line["words"] if word.lower() in w["w"].lower()]
        return hits[min(k, len(hits) - 1)]["s"] - self.start

    def since(self, word, k=0):
        return self.lt - self.at(word, k)


def sc_hook(c, S):
    ocean(c, S.t, 0.95)
    z = 1.3 + 0.15 * S.p
    a = 0.55 + 0.45 * clamp(S.since("sang") / 0.4)
    octopus(c, W / 2, 1020, z, S.t, body=hexc("101A3A"), dark=hexc("0A1230"), alpha=a, expr="wow")
    ts = S.lt + 0.3  # visible dès la 1re image (miniature + accroche)
    for k, (hx, hy) in enumerate(((W / 2 - 250, 640), (W / 2, 570), (W / 2 + 250, 640))):
        d = ts - k * 0.12
        if d <= 0:
            continue
        beat = 1 + 0.08 * math.sin(S.t * 9 + k)
        blue = clamp(S.since("bleu") / 0.3)
        col = [lerp(a, b, blue) for a, b in zip(RED, BLUE)]
        glow_circle(c, hx, hy, 170, col, 0.5)
        heart(c, hx, hy, 180 * pop(d) * beat, col)
    if S.since("bleu") < 0:
        title(c, "3 CŒURS", ts, size=150, col=WHITE, glow=RED)
    else:
        title(c, "SANG BLEU", S.since("bleu") + 0.15, size=150, col=BLUE, glow=BLUE)
        d = S.since("bleu")
        for k in range(7):
            yy = 700 + ((d * 900 + k * 160) % 900)
            drop(c, 150 + k * 130, yy, 30, BLUE, a=clamp(d / 0.2))


def sc_reveal(c, S):
    ocean(c, S.t, 0.45)
    d = S.since("poulpe")
    s = 1.25 * pop(d + 0.25, 0.45)
    if s > 0:
        octopus(c, W / 2, 1010 + 20 * math.sin(S.t * 2), s, S.t, mode="idle", look=(0.3 * math.sin(S.t), 0))
    for k in range(10):
        if 0 < d < 0.8:
            ang = k * 2 * math.pi / 10
            r = 200 + d * 600
            sparkle(c, W / 2 + r * math.cos(ang), 950 + r * math.sin(ang), 30 * (1 - d / 0.8), YELLOW)
    title(c, "LE POULPE", d + 0.2, size=150, col=YELLOW, sub="(et ce n'est que le début)" if S.since("début") > 0 else None)


def sc_cuivre(c, S):
    ocean(c, S.t, 0.55)
    title(c, "POURQUOI BLEU ?", S.lt + 0.3, size=110, col=WHITE, glow=BLUE)
    split = clamp(S.since("Nous") / 0.5)
    lx = lerp(W / 2, 290, ease_io(split))
    bob = 12 * math.sin(S.t * 3)
    drop(c, lx, 900 + bob, 240 * pop(S.lt, 0.4), BLUE)
    octopus(c, lx, 600 + bob, 0.32 * pop(S.lt - 0.2, 0.4), S.t)
    d = S.since("cuivre")
    if d > 0:
        element_tile(c, lx, 1180, 0.9 * pop(d), "Cu", "29", "CUIVRE", hexc("D9822B"))
    if split > 0:
        rx = lerp(W + 200, 790, ease_io(split))
        drop(c, rx, 900 - bob, 240, RED)
        # mini humain
        c.save(); c.translate(rx, 600 - bob)
        src(c, hexc("FFC9A3")); c.arc(0, -40, 50, 0, 2 * math.pi); c.fill_preserve()
        src(c, INK); c.set_line_width(7); c.stroke()
        rrect(c, -60, 15, 120, 90, 40); src(c, hexc("4C6FFF")); c.fill_preserve(); src(c, INK); c.stroke()
        c.restore()
        df = S.since("fer")
        if df > 0:
            element_tile(c, rx, 1180, 0.9 * pop(df), "Fe", "26", "FER", hexc("8A94A6"))
        txt(c, "VS", W / 2, 900, 90, YELLOW, a=split)


def sc_coeurs(c, S):
    ocean(c, S.t, 0.6)
    title(c, "3 CŒURS, 3 MISSIONS", S.lt + 0.3, size=96, col=YELLOW)
    octopus(c, W / 2, 1030, 1.55, S.t * 0.6, alpha=0.45)
    bpm = 1 + 0.1 * max(0, math.sin(S.t * 8))
    d2 = S.since("Deux")
    d3 = S.since("troisième")
    for k, hx in enumerate((W / 2 - 190, W / 2 + 190)):
        if d2 - k * 0.15 > 0:
            heart(c, hx, 920, 110 * pop(d2 - k * 0.15) * bpm, RED)
    if S.since("branchies") > 0:
        db = S.since("branchies")
        for k, side in enumerate((-1, 1)):
            # flux vers les branchies
            for j in range(6):
                u = ((S.t * 0.9 + j / 6) % 1)
                src(c, BLUE, 0.9)
                c.arc(W / 2 + side * (230 + u * 220), 920 - u * 100, 12, 0, 2 * math.pi); c.fill()
            txt(c, "BRANCHIES", W / 2 + side * 330, 800, 46, WHITE, scale=pop(db))
    if d3 > 0:
        heart(c, W / 2, 790, 190 * pop(d3) * bpm, RED)
        glow_circle(c, W / 2, 790, 230, RED, 0.35 * clamp(d3))
    dc = S.since("corps")
    if dc > 0:
        for j in range(10):
            u = ((S.t * 0.8 + j / 10) % 1)
            ang = math.pi / 2 + (j % 5 - 2) * 0.35
            src(c, RED, 0.9)
            c.arc(W / 2 + math.cos(ang) * u * 520, 790 + math.sin(ang) * u * 620, 11, 0, 2 * math.pi); c.fill()
        txt(c, "TOUT LE CORPS", W / 2, 600, 52, WHITE, scale=pop(dc))


def ecg(c, x, y, w, h, t, flat, label):
    rrect(c, x, y, w, h, 30)
    src(c, hexc("08131F"), 0.92); c.fill_preserve()
    src(c, GREEN if flat < 1 else RED); c.set_line_width(6); c.stroke()
    col = [lerp(a, b, flat) for a, b in zip(GREEN, RED)]
    src(c, col); c.set_line_width(7); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for i in range(0, 121):
        u = i / 120
        ph = (u * 3 - t * 1.4) % 1
        v = 0
        if 0.40 < ph < 0.44:
            v = -1
        elif 0.44 < ph < 0.48:
            v = 0.6
        elif 0.30 < ph < 0.36:
            v = -0.15
        v *= (1 - flat)
        px, py = x + 30 + u * (w - 60), y + h * 0.58 + v * h * 0.38
        (c.move_to if i == 0 else c.line_to)(px, py)
    c.stroke()
    txt(c, label, x + w / 2, y + 42, 38, WHITE, stroke=None, shadow=False)


def sc_nage(c, S):
    crawl = S.since("Voilà") > 0
    ocean(c, S.t, 0.5)
    stop = clamp(S.since("s'arrête") / 0.3) * (0 if crawl else 1)
    if not crawl:
        y = 1150 - 260 * S.p / max(S.at("Voilà") / S.dur, 0.01) + 30 * math.sin(S.t * 5)
        octopus(c, W / 2, y, 0.95, S.t, mode="swim", tilt=0.05 * math.sin(S.t * 3), expr="wow" if stop > 0 else "happy")
        for k in range(8):
            u = (S.t * 1.5 + k / 8) % 1
            src(c, WHITE, 0.6 * (1 - u)); c.set_line_width(3)
            c.arc(W / 2 + 25 * math.sin(k * 3), y + 380 + u * 300, 8 + 10 * u, 0, 2 * math.pi); c.stroke()
    else:
        sand(c, 1560, S.t)
        dx = S.since("Voilà")
        octopus(c, 280 + dx * 140, 1380, 0.8, S.t, mode="crawl", look=(1, 0.2))
        title(c, "IL RAMPE !", S.since("ramper") + 0.1, y=760, size=120)
    ecg(c, 140, 230, 800, 300, S.t, stop, "CŒUR N°3 · 0 BPM" if stop > 0.5 else "CŒUR N°3")


NET = [(rnd.uniform(60, W - 60), rnd.uniform(560, 1300)) for _ in range(60)]


def sc_neurones(c, S):
    ocean(c, S.t, 0.85, tint=hexc("5B2BFF"))
    dn = S.since("cinq")
    # réseau
    for i, (x, y) in enumerate(NET):
        for j in range(i + 1, min(i + 4, len(NET))):
            x2, y2 = NET[j]
            if math.hypot(x2 - x, y2 - y) < 260:
                src(c, hexc("9C7BFF"), 0.25); c.set_line_width(2)
                c.move_to(x, y); c.line_to(x2, y2); c.stroke()
        fl = 0.5 + 0.5 * math.sin(S.t * 6 + i * 1.7)
        glow_circle(c, x, y, 30, hexc("B69CFF"), 0.4 * fl)
        src(c, WHITE, 0.6 + 0.4 * fl); c.arc(x, y, 5, 0, 2 * math.pi); c.fill()
    # compteur
    if dn > -0.2:
        u = ease_io(clamp((dn + 0.2) / max(S.at("neurones") - S.at("cinq") + 0.3, 0.3)))
        n = int(500_000_000 * u)
        s = f"{n:,}".replace(",", " ")
        txt(c, s, W / 2, 330, 130, YELLOW, glow=hexc("FF8A00"), scale=pop(dn + 0.2))
        txt(c, "NEURONES", W / 2, 460, 64, WHITE, a=clamp(S.since("neurones") / 0.2))
    dd = S.since("deux")
    if dd > 0:
        k = pop(dd, 0.4)
        c.save(); rrect(c, 140, 600, 800, 520, 50); src(c, INK, 0.75 * clamp(dd / 0.3)); c.fill(); c.restore()
        octopus(c, W / 2, 790, 0.62 * k, S.t)
        for i in range(8):
            pts = arm_points(i, S.t, "idle")
            for j in range(4, 20, 4):
                px, py = pts[j]
                glow_circle(c, W / 2 + px * 0.62 * k, 790 + py * 0.62 * k, 22, YELLOW, 0.8)
        txt(c, "2/3 DANS LES BRAS", W / 2, 1060, 70, YELLOW, scale=pop(S.since("bras")))


def sc_bras(c, S):
    ocean(c, S.t, 0.4)
    # un grand bras qui traverse l'écran
    c.save(); c.translate(-80, 1350); c.scale(2.6, 2.6)
    pts = []
    for j in range(31):
        u = j / 30
        pts.append((u * 470, -u * 260 + 40 * math.sin(u * 5 - S.t * 2) - 120 * u ** 3))
    marks = [S.at("toucher"), S.at("goûter"), S.at("réagir")]
    lit = lambda u: clamp((S.lt - marks[0] - u * 1.6) / 0.2)
    draw_arm(c, pts, BODY, BODY_D, w0=48, suckers=True, sucker_lit=lit)
    c.restore()
    for k, (word, label, x, y, col) in enumerate((
        ("toucher", "TOUCHER", 300, 480, WHITE), ("goûter", "GOÛTER", 760, 640, YELLOW), ("réagir", "RÉAGIR", 330, 820, GREEN))):
        d = S.since(word)
        if d > 0:
            rot = (-0.08, 0.06, -0.05)[k]
            c.save(); c.translate(x, y); c.rotate(rot)
            txt(c, label, 0, 0, 100, col, scale=pop(d))
            c.restore()
    dc = S.since("cerveau")
    if dc > 0:
        txt(c, "…SANS LE CERVEAU", W / 2, 1050, 66, WHITE, scale=pop(dc), glow=BLUE)


PALETTE = [hexc(h) for h in ("FF6B8B", "FFB020", "3DFFA2", "3DA9FF", "B06BFF", "FF3B4E", "F5F0E1", "8B5A2B")]


def sc_couleurs(c, S):
    ocean(c, S.t, 0.45)
    dch = S.since("change")
    blind = S.since("Pourtant")
    if blind < 0:
        if dch > 0:
            k = int(S.t * 9) % len(PALETTE)
            body = PALETTE[k]
            dark = [x * 0.75 for x in body[:3]] + [1]
        else:
            body, dark = BODY, BODY_D
        octopus(c, W / 2, 980, 1.15, S.t, body=body, dark=dark, expr="wow" if dch > 0 else "happy")
        title(c, "< 1 SECONDE", S.since("fraction") + 0.1, size=140, col=YELLOW, sub="pour changer de couleur")
    else:
        octopus(c, W / 2, 1000, 1.15, S.t, look=(0, -0.3))
        # désaturation : ce que « voit » le poulpe
        k = clamp(blind / 0.6)
        c.set_operator(cairo.OPERATOR_HSL_SATURATION)
        src(c, (0.5, 0.5, 0.5), k); c.paint()
        c.set_operator(cairo.OPERATOR_OVER)
        title(c, "DALTONIEN ?", blind + 0.1, size=140, col=WHITE)


def jar(c, x, y, lid_open, t):
    c.save(); c.translate(x, y)
    rrect(c, -230, -260, 460, 560, 80)
    src(c, hexc("BFE8FF"), 0.22); c.fill_preserve()
    src(c, WHITE, 0.85); c.set_line_width(10); c.stroke()
    src(c, WHITE, 0.35); rrect(c, -190, -200, 40, 380, 20); c.fill()
    # couvercle
    c.save()
    c.translate(lid_open * 260, -290 - lid_open * 330); c.rotate(lid_open * 2.2)
    rrect(c, -200, -45, 400, 90, 20)
    src(c, RED); c.fill_preserve(); src(c, INK); c.set_line_width(8); c.stroke()
    for k in range(-3, 4):
        c.move_to(k * 50, -35); c.line_to(k * 50, 35)
    src(c, hexc("B3202F")); c.set_line_width(6); c.stroke()
    c.restore()
    c.restore()


def sc_bocal(c, S):
    ocean(c, S.t, 0.5)
    dv = S.since("dévisse")
    de = S.since("s'échappe")
    dr = S.since("reconnaît")
    lid = ease_io(clamp(dv / 1.0))
    if dr < 0:
        if de < 0:
            octopus(c, W / 2 + 20 * math.sin(S.t * 2), 1030, 0.65, S.t, look=(0, -1))
            jar(c, W / 2, 1000, lid, S.t)
        else:
            jar(c, W / 2, 1000, 1, S.t)
            u = clamp(de / 0.9)
            ox = lerp(W / 2, 820, u)
            oy = 1030 - 700 * u + 650 * u * u
            octopus(c, ox, oy, 0.65, S.t, mode="swim", tilt=u * 0.6, expr="wow")
            txt(c, "ÉVASION !", W / 2, 480, 120, YELLOW, scale=pop(S.since("aquariums")))
        title(c, "DÉVISSE LES BOCAUX", dv + 0.1, size=92, col=WHITE)
    else:
        octopus(c, 330, 1050, 0.75, S.t, look=(1, -0.2))
        # humain
        k = pop(dr)
        c.save(); c.translate(790, 980); c.scale(max(k, 0.001), max(k, 0.001))
        src(c, hexc("FFC9A3")); c.arc(0, -120, 110, 0, 2 * math.pi); c.fill_preserve()
        src(c, INK); c.set_line_width(9); c.stroke()
        src(c, hexc("3B2A20")); c.arc(0, -150, 112, math.pi * 1.05, math.pi * 1.95); c.fill()
        for ex in (-38, 38):
            src(c, INK); c.arc(ex, -110, 11, 0, 2 * math.pi); c.fill()
        c.set_line_width(7); c.arc(0, -80, 32, 0.2 * math.pi, 0.8 * math.pi); c.stroke()
        rrect(c, -140, 10, 280, 300, 90); src(c, hexc("4C6FFF")); c.fill_preserve(); src(c, INK); c.stroke()
        c.restore()
        heart(c, 560, 720 - 30 * math.sin(S.t * 3), 110 * pop(dr - 0.3), RED)
        title(c, "IL TE RECONNAÎT", dr + 0.1, size=104, col=YELLOW)


def sc_vie(c, S):
    ocean(c, S.t, 0.75)
    x, y = W / 2 + 160, 1000
    u = clamp(S.p * 1.1)
    c.save(); c.translate(x, y)
    # sablier
    src(c, hexc("8B5A2B")); rrect(c, -170, -330, 340, 40, 14); c.fill(); rrect(c, -170, 290, 340, 40, 14); c.fill()
    c.move_to(-130, -290); c.curve_to(-130, -60, -20, -40, -20, 0); c.curve_to(-20, 40, -130, 60, -130, 290)
    c.line_to(130, 290); c.curve_to(130, 60, 20, 40, 20, 0); c.curve_to(20, -40, 130, -60, 130, -290); c.close_path()
    src(c, hexc("D6F1FF"), 0.25); c.fill_preserve(); src(c, WHITE, 0.9); c.set_line_width(8); c.stroke()
    top = 240 * (1 - u)
    src(c, SAND)
    c.move_to(-120 * (1 - u) - 20, -40 - top); c.line_to(120 * (1 - u) + 20, -40 - top); c.line_to(0, -10); c.close_path(); c.fill()
    hb = 240 * u
    c.move_to(-125, 285); c.line_to(125, 285); c.line_to(60, 285 - hb); c.line_to(-60, 285 - hb); c.close_path(); c.fill()
    c.rectangle(-4, -10, 8, 290 - hb); c.fill()
    c.restore()
    octopus(c, 300, 1150, 0.6, S.t, expr="sad" if S.since("vivent") > 0 else "happy", look=(1, -0.5))
    d = S.since("deux")
    title(c, "1 À 2 ANS", d + 0.1, size=170, col=YELLOW, glow=RED, sub="d'espérance de vie")


def sc_outro(c, S):
    ocean(c, S.t, 0.35)
    octopus(c, W / 2, 1020 + 15 * math.sin(S.t * 2), 1.0, S.t, mode="wave")
    d = S.since("Abonne")
    k = pop(d, 0.35) * (1 + 0.05 * math.sin(S.t * 8))
    if k > 0:
        c.save(); c.translate(W / 2, 360); c.scale(k, k)
        rrect(c, -330, -85, 660, 170, 85); src(c, RED); c.fill_preserve(); src(c, INK); c.set_line_width(10); c.stroke()
        txt(c, "+ ABONNE-TOI", 0, 0, 82, WHITE, lw=12)
        c.restore()
    df = S.since("faits")
    txt(c, "D'AUTRES FAITS FOUS ↓", W / 2, 540, 56, YELLOW, scale=pop(df))


SCENES = {k[3:]: v for k, v in globals().items() if k.startswith("sc_")}


# ---------------------------------------------------------------- sous-titres
def chunks(words, maxw=3, maxc=16):
    out, cur = [], []
    for w in words:
        if cur and (len(cur) >= maxw or len(" ".join(x["w"] for x in cur + [w])) > maxc):
            out.append(cur); cur = []
        cur.append(w)
        if w["w"][-1] in ".,!?…":
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def captions(c, CH, t):
    cur = None
    for i, ch in enumerate(CH):
        nxt = CH[i + 1][0]["s"] if i + 1 < len(CH) else ch[-1]["e"] + 0.6
        end = min(nxt, ch[-1]["e"] + 0.6)
        if ch[0]["s"] - 0.05 <= t < end:
            cur = ch
    if not cur:
        return
    size = 92
    words = [w["w"].upper().rstrip(",.") for w in cur]
    sp = text_path_w(c, " ", size) + size * 0.22
    widths = [text_path_w(c, w, size) for w in words]
    total = sum(widths) + sp * (len(words) - 1)
    sc = min(1.0, 940 / total)
    appear = pop(t - cur[0]["s"] + 0.05, 0.18)
    sc *= appear
    x = W / 2 - total * sc / 2
    y = 1430
    for w, ww, wd in zip(cur, widths, words):
        active = w["s"] - 0.03 <= t < w["e"] + 0.08
        key = w["w"] in KEYWORDS
        col = YELLOW if key else WHITE
        bump = 1 + 0.12 * max(0, 1 - (t - w["s"]) / 0.15) if t >= w["s"] else 1
        a = 1.0 if t >= w["s"] - 0.03 else 0.55
        if active and not key:
            col = hexc("7CF5FF")
        txt(c, wd, x + ww * sc / 2, y, size, col, a=a, scale=sc * bump, lw=size * 0.22)
        x += (ww + sp) * sc


# ---------------------------------------------------------------- image
def frame(c, t, TL, CH):
    lines = TL["lines"]
    idx = 0
    for i, l in enumerate(lines):
        if t >= l["start"] - (0.15 if i else 0):
            idx = i
    line = lines[idx]
    nxt = lines[idx + 1]["start"] if idx + 1 < len(lines) else TL["total"] + TAIL
    S = Scene(line, t, nxt)
    c.save()
    z = 1 + 0.07 * math.exp(-max(S.lt, 0) / 0.15) + 0.03 * S.p
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    SCENES[line["scene"]](c, S)
    c.restore()
    captions(c, CH, t)
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.78)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0.04, 0.5)
    c.set_source(g); c.paint()
    if idx > 0 and -0.15 <= S.lt < 0.0:
        src(c, WHITE, 0.25 * (1 + S.lt / 0.15)); c.paint()


def main():
    work, out = sys.argv[1], sys.argv[2]
    TL = json.load(open(os.path.join(work, "timeline.json")))
    CH = chunks([w for l in TL["lines"] for w in l["words"]])
    total = TL["total"] + TAIL
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    if "--preview" in sys.argv:
        for i, l in enumerate(TL["lines"]):
            for k, f in enumerate((0.35, 0.8)):
                frame(c, l["start"] + f * (l["end"] - l["start"]), TL, CH)
                surf.write_to_png(f"{out}_{i:02d}{'ab'[k]}.png")
        return
    n = int(total * FPS)
    voice, music = os.path.join(work, "voix.wav"), os.path.join(work, "musique.wav")
    # voix : léger EQ/compression + normalisation ; musique sous la voix, atténuée par sidechain
    af = (
        "[1:a]aresample=44100,highpass=f=80,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,"
        "volume=1.6,aformat=channel_layouts=stereo,asplit=2[v][vsc];"
        "[2:a]volume=0.22[m];[m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
        "[v][md]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]"
    )
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", voice, "-i", music, "-filter_complex", af, "-map", "0:v", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n):
        frame(c, f / FPS, TL, CH)
        surf.flush()
        ff.stdin.write(surf.get_data())
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main()
