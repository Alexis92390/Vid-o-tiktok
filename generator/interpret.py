"""Vidéo « interprétée » : la mascotte joue chaque passage du morceau, calée sur ses timings.

Aucune parole n'est affichée : le son et les sous-titres s'ajoutent dans TikTok.
Usage : python3 interpret.py sortie.mp4 [--preview]
"""
import math
import random
import subprocess
import sys

import cairo

import render as R
from render import (W, H, FPS, INK, KEY, GLOW, CAP, JACKET, HEAD, hexc, src, rrect, fill_stroke,
                    glow_circle, star_path, sparkle, ease_out_back, ease_io, lerp, sky, city,
                    mascot, moon, icon, clock, flame, draw_text)

BPM = 75
OFFSET = 0.26
R.BEAT = 60 / BPM
R.BAR = 4 * R.BEAT
BEAT = R.BEAT
TOTAL = 38.7

# ---------------------------------------------------------------- éléments
def cage_bars(c, x, y, w, h, open_k=0.0):
    src(c, hexc("8C7BD6"))
    c.set_line_width(14)
    n = 7
    for i in range(n):
        bx = x + i * w / (n - 1)
        if open_k > 0 and i >= n // 2:
            bx += open_k * 420
        c.move_to(bx, y); c.line_to(bx, y + h); c.stroke()
    rrect(c, x - 20, y - 26, w + 40, 30, 10); fill_stroke(c, hexc("5B4BA8"), 6)
    rrect(c, x - 20, y + h - 6, w + 40, 30, 10); fill_stroke(c, hexc("5B4BA8"), 6)

def zoo_sign(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for px in (-200, 180):
        rrect(c, px, 0, 22, 360, 6); fill_stroke(c, hexc("3B2A7A"), 6)
    rrect(c, -230, -40, 460, 110, 30); fill_stroke(c, hexc("2EE6D6"), 8)
    draw_text(c, "ZOO", 0, 18, 96, INK, anchor="c")
    c.restore()

def balloons(c, x, y, t, n=7):
    cols = [hexc("FF5C8A"), hexc("FFD23F"), hexc("2EE6D6"), hexc("FF9F1C"), hexc("B892FF")]
    rnd = random.Random(2)
    for i in range(n):
        bx = x + rnd.uniform(-150, 150) + 12 * math.sin(t * 2 + i)
        by = y - 260 - rnd.uniform(0, 220)
        src(c, hexc("FFFFFF"), 0.7); c.set_line_width(3)
        c.move_to(x, y); c.curve_to(x, y - 100, bx, by + 140, bx, by + 60); c.stroke()
        c.save(); c.translate(bx, by); c.scale(1, 1.18)
        c.arc(0, 0, 58, 0, 6.283); c.restore()
        fill_stroke(c, cols[i % len(cols)], 6)
        src(c, hexc("FFFFFF"), 0.45); c.arc(bx - 18, by - 24, 12, 0, 6.283); c.fill()

def rocket(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    flame(c, 0, 250, 1.1, t)
    for side in (-1, 1):
        c.move_to(side * 70, 120); c.line_to(side * 150, 230); c.line_to(side * 70, 200); c.close_path()
        fill_stroke(c, hexc("FF5C8A"), 7)
    c.move_to(0, -260)
    c.curve_to(110, -160, 95, 120, 70, 210); c.line_to(-70, 210); c.curve_to(-95, 120, -110, -160, 0, -260)
    c.close_path(); fill_stroke(c, hexc("F1EEFF"), 8)
    c.move_to(-60, -150); c.curve_to(-30, -240, 30, -240, 60, -150); c.close_path(); fill_stroke(c, hexc("FF5C8A"), 7)
    c.arc(0, -20, 62, 0, 6.283); fill_stroke(c, hexc("8C7BD6"), 8)
    c.save(); c.arc(0, -20, 54, 0, 6.283); c.clip()
    mascot(c, 0, 80, 0.42, t, "idle", "happy")
    c.restore()
    c.restore()

def smoke(c, y, t, k):
    rnd = random.Random(8)
    for i in range(14):
        x = rnd.uniform(-100, W + 100)
        r = rnd.uniform(90, 170) * (0.6 + k)
        src(c, hexc("E9E3FF"), 0.85)
        c.arc(x + (x - W / 2) * k * 0.5, y + rnd.uniform(-40, 60), r, 0, 6.283); c.fill()

def dream_cloud(c, x, y, s, t):
    s = max(s, 0.01)
    c.save(); c.translate(x, y); c.scale(s, s)
    pts = [(-220, 0, 120), (-90, -90, 150), (90, -100, 150), (220, -10, 120), (130, 90, 120), (-120, 90, 120), (0, 30, 170)]
    for (px, py, r) in pts:
        c.arc(px, py + 4 * math.sin(t * 2 + px), r + 8, 0, 6.283); src(c, INK); c.fill()
    for (px, py, r) in pts:
        c.arc(px, py + 4 * math.sin(t * 2 + px), r, 0, 6.283); src(c, hexc("D9CCFF")); c.fill()
    c.restore()
    for i, (dx, dy, r) in enumerate(((-60, 300, 28), (-90, 380, 18))):
        c.arc(x + dx * s, y + dy * s, r * s, 0, 6.283); fill_stroke(c, hexc("D9CCFF"), 5)

def balaclava(c, x, y, s):
    """Cagoule : recouvre la tête (pieds en x,y comme la mascotte)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.arc(0, -240, 66, 0, 6.283); fill_stroke(c, hexc("1C1240"), 6)
    src(c, hexc("2C1F66")); c.set_line_width(5)
    for k in range(-3, 4):
        c.move_to(k * 16, -300); c.line_to(k * 16, -180); c.stroke()
    rrect(c, -46, -252, 92, 40, 20); fill_stroke(c, HEAD, 5)
    for ex in (-20, 20):
        src(c, hexc("FFFFFF")); c.arc(ex, -232, 12, 0, 6.283); c.fill()
        src(c, INK); c.arc(ex, -230, 5, 0, 6.283); c.fill()
    c.arc(0, -310, 18, 0, 6.283); fill_stroke(c, hexc("FF5C8A"), 5)
    c.restore()

def glove(c, x, y, s, col):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -46, -40, 92, 80, 34); fill_stroke(c, col, 6)
    rrect(c, -36, 28, 72, 30, 8); fill_stroke(c, hexc("FFFFFF"), 5)
    c.restore()

def boxer(c, x, y, s, t, facing, jacket, punch):
    c.save(); c.translate(x, y); c.scale(facing, 1)
    old = R.JACKET
    R.JACKET = jacket
    mascot(c, 0, 0, s, t, "idle", "focus", look=(1, 0))
    R.JACKET = old
    ext = 150 * punch
    glove(c, (70 + ext) * s, -175 * s, s, hexc("FF3B3B"))
    glove(c, 40 * s, -140 * s, s * 0.9, hexc("FF3B3B"))
    c.restore()

def mountain(c, cx, base, w, h, col):
    c.move_to(cx - w / 2, base); c.line_to(cx, base - h); c.line_to(cx + w / 2, base); c.close_path()
    fill_stroke(c, col, 8)
    c.move_to(cx - w * 0.11, base - h * 0.78); c.line_to(cx, base - h); c.line_to(cx + w * 0.11, base - h * 0.78)
    c.line_to(cx + w * 0.04, base - h * 0.74); c.line_to(cx - w * 0.03, base - h * 0.8); c.close_path()
    fill_stroke(c, hexc("FFFFFF"), 6)

def pine(c, x, y, s):
    src(c, hexc("120A2E"))
    for k in range(3):
        w = (90 - k * 22) * s
        c.move_to(x - w, y - k * 60 * s); c.line_to(x, y - (k * 60 + 120) * s); c.line_to(x + w, y - k * 60 * s); c.close_path(); c.fill()

def path_point(k):
    """Sentier en zigzag sur la montagne (k 0..1)."""
    pts = [(300, 1750), (760, 1500), (320, 1230), (700, 990), (430, 760), (560, 560)]
    k = min(max(k, 0), 1) * (len(pts) - 1)
    i = min(int(k), len(pts) - 2)
    f = k - i
    return lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)

def fog(c, t, a):
    rnd = random.Random(21)
    for i in range(12):
        x = (rnd.uniform(0, W) + t * rnd.uniform(40, 120)) % (W + 400) - 200
        y = rnd.uniform(700, 1800)
        src(c, hexc("E9E3FF"), 0.28 * a)
        for (dx, r) in ((0, 120), (110, 150), (220, 110)):
            c.arc(x + dx, y, r, 0, 6.283); c.fill()

def signpost(c, x, y, t, spin):
    rrect(c, x - 10, y - 380, 20, 380, 6); fill_stroke(c, hexc("6B4A2E"), 6)
    for i in range(3):
        a = spin * (t * 6 + i * 2.1)
        d = 1 if math.cos(a) > 0 else -1
        c.save(); c.translate(x, y - 340 + i * 70); c.scale(d * max(0.3, abs(math.cos(a))), 1)
        c.move_to(0, -24); c.line_to(150, -24); c.line_to(185, 0); c.line_to(150, 24); c.line_to(0, 24); c.close_path()
        fill_stroke(c, hexc("F6E7C8"), 6)
        c.restore()

def flag(c, x, y, t, k):
    rrect(c, x - 7, y - 300 * k, 14, 300 * k, 5); fill_stroke(c, hexc("E9E3FF"), 5)
    if k >= 1:
        c.move_to(x + 7, y - 300)
        for i in range(9):
            c.line_to(x + 7 + i * 22, y - 300 + 8 * math.sin(t * 8 - i))
        c.line_to(x + 7 + 176, y - 200 + 8 * math.sin(t * 8 - 8))
        for i in range(8, -1, -1):
            c.line_to(x + 7 + i * 22, y - 200 + 8 * math.sin(t * 8 - i))
        c.close_path(); fill_stroke(c, KEY, 6)
        star_path(c, x + 95, y - 250, 26, 11); fill_stroke(c, hexc("FF5C8A"), 4)

def coins(c, x, y, n, t):
    for i in range(n):
        c.save(); c.translate(x + (i % 2) * 6, y - i * 22); c.scale(1, 0.35)
        c.arc(0, 0, 70, 0, 6.283); c.restore(); fill_stroke(c, KEY, 5)

def hourglass(c, x, y, s, k, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -90, -150, 180, 24, 8); fill_stroke(c, hexc("6B4A2E"), 6)
    rrect(c, -90, 126, 180, 24, 8); fill_stroke(c, hexc("6B4A2E"), 6)
    c.move_to(-70, -126); c.line_to(70, -126); c.line_to(8, 0); c.line_to(70, 126); c.line_to(-70, 126); c.line_to(-8, 0); c.close_path()
    fill_stroke(c, hexc("D9F7FF", 0.5), 6)
    src(c, hexc("FFD23F"))
    top = 1 - k
    if top > 0:
        c.move_to(-60 * top, -10 - 100 * top); c.line_to(60 * top, -10 - 100 * top); c.line_to(0, -6); c.close_path(); c.fill()
    c.move_to(-60 * k, 120); c.line_to(60 * k, 120); c.line_to(0, 120 - 100 * k); c.close_path(); c.fill()
    c.rectangle(-3, -6, 6, 126); c.fill()
    c.restore()

def crowd(c, t, lt, y0=1760):
    rnd = random.Random(5)
    for i in range(16):
        x = i * 72 + rnd.uniform(-10, 10)
        hb = y0 + rnd.uniform(0, 60) + 10 * math.sin(t * 6 + i)
        src(c, hexc("0A0620")); c.arc(x, hb, 44, 0, 6.283); c.fill(); c.rectangle(x - 55, hb + 30, 110, 260); c.fill()
        if i % 2 == 0 and lt > 0.12 * (i % 7):
            px, py = x + 30, hb - 120 + 6 * math.sin(t * 5 + i)
            src(c, hexc("0A0620")); c.set_line_width(22); c.move_to(x + 25, hb); c.line_to(px, py + 40); c.stroke()
            glow_circle(c, px, py, 70, hexc("FFFFFF"), 0.35)
            rrect(c, px - 22, py - 36, 44, 76, 8); fill_stroke(c, hexc("E9F7FF"), 5)

def beams(c, t, xs=(300, 780), a=0.35):
    for i, base in enumerate(xs):
        ang = math.sin(t * 1.3 + i * 2) * 0.35
        c.save(); c.translate(base, 1900); c.rotate(ang)
        g = cairo.LinearGradient(0, 0, 0, -1900)
        g.add_color_stop_rgba(0, 1, 0.85, 0.3, a); g.add_color_stop_rgba(1, 1, 0.85, 0.3, 0)
        c.set_source(g); c.move_to(-40, 0); c.line_to(-260, -1900); c.line_to(260, -1900); c.line_to(40, 0); c.fill()
        c.restore()

# ---------------------------------------------------------------- scènes (c, t, lt, p, d)
def s_zoo(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("261452"))
    city(c, t, seed=4, lit=0.25)
    zoo_sign(c, 540, 820, 0.9)
    src(c, hexc("120A2E")); c.rectangle(0, 1700, W, H); c.fill()
    mascot(c, 540, 1700, 1.6, t, "idle", "sleepy", look=(0, 1))
    cage_bars(c, 250, 1080, 580, 640)

def s_envol(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("2C1660"))
    lift = ease_io(p) * 700
    city(c, t, seed=4, lit=0.35, dy=lift * 0.5)
    src(c, hexc("120A2E")); c.rectangle(0, 1700 + lift * 0.5, W, H); c.fill()
    cage_bars(c, 250, 1080 + lift * 0.5, 580, 640, open_k=ease_out_back(p * 3))
    my = 1700 - lift * 0.9
    balloons(c, 540, my - 300 * 1.5, t)
    mascot(c, 540, my, 1.5, t, "up", "happy")

def s_decolle(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("33176E"))
    city(c, t, seed=5, lit=0.5, dy=p * 600)
    shake = 8 * math.sin(t * 60) * (1 - p)
    ry = lerp(1350, 700, ease_io(p) ** 1.6)
    glow_circle(c, 540, ry + 400, 500, GLOW, 0.4)
    rocket(c, 540 + shake, ry, 1.25, t)
    smoke(c, 1780 + p * 400, t, p)

def s_douze(c, t, lt, p, d):
    sky(c, t)
    city(c, t, seed=6, lit=0.4, dy=200)
    n = 1 + int(min(p * 1.15, 1) * 11.99)
    # calendrier qui défile
    c.save(); c.translate(540, 760); c.rotate(-0.04)
    rrect(c, -230, -230, 460, 440, 30); fill_stroke(c, hexc("FFF6E0"), 8)
    rrect(c, -230, -230, 460, 120, 30); fill_stroke(c, hexc("FF5C8A"), 8)
    for rx in (-120, 120):
        rrect(c, rx - 12, -270, 24, 80, 10); fill_stroke(c, hexc("8C7BD6"), 6)
    flip = (p * 12) % 1
    draw_text(c, f"{n}", 0, 70, 230, INK, scale=1 - 0.25 * math.exp(-flip * 8), anchor="c")
    c.restore()
    s = lerp(0.7, 1.55, ease_io(p))
    mascot(c, 540, 1760, s, t, "idle", "open")

def s_cagoule(c, t, lt, p, d):
    sky(c, t, hexc("090620"), hexc("231248"))
    city(c, t, seed=7, lit=0.3, dy=200)
    k = ease_out_back(min(lt / 0.6, 1))
    dream_cloud(c, 540, 820, 1.0 * k + 0.25 * p, t)
    items = ["house", "disc", "crown", "star", "note", "disc", "house", "crown", "star"]
    shown = min(len(items), int(lt / 0.42))
    rnd = random.Random(4)
    for i in range(shown):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(40, 200) * (1 + 0.25 * p)
        x = 540 + math.cos(a) * rr * 1.3
        y = 800 + math.sin(a) * rr * 0.6 + 8 * math.sin(t * 3 + i)
        icon(c, items[i], x, y, 46 * ease_out_back((lt - i * 0.42) / 0.3), t)
    mascot(c, 540, 1780, 1.55, t, "idle", "happy")
    balaclava(c, 540, 1780 - abs(math.sin(t * math.pi / BEAT)) * 6 * 1.55, 1.55)

def s_reves_grand(c, t, lt, p, d):
    sky(c, t, hexc("090620"), hexc("2C1660"))
    dream_cloud(c, 540, lerp(820, 900, p), lerp(1.25, 2.6, ease_io(p)), t)
    rnd = random.Random(9)
    kinds = ["house", "disc", "crown", "star", "note"]
    for i in range(int(8 + 22 * p)):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(60, 520)
        x = 540 + math.cos(a + t * 0.3) * rr
        y = 880 + math.sin(a + t * 0.3) * rr * 0.75
        icon(c, kinds[i % 5], x, y, rnd.uniform(36, 64), t)
    mascot(c, 540, 1800, 1.45, t, "up", "happy")
    balaclava(c, 540, 1800 - abs(math.sin(t * math.pi / BEAT)) * 6 * 1.45, 1.45)

def s_eclat(c, t, lt, p, d):
    sky(c, t, hexc("05041A"), hexc("1E0F44"))
    glow_circle(c, 540, 900, 700 * (1 - p * 0.5), KEY, 0.5 * (1 - p))
    rnd = random.Random(10)
    kinds = ["house", "disc", "crown", "star", "note"]
    for i in range(30):
        a = rnd.uniform(0, 6.28)
        sp = rnd.uniform(500, 1300)
        x = 540 + math.cos(a) * sp * lt
        y = 900 + math.sin(a) * sp * lt + 600 * lt * lt
        icon(c, kinds[i % 5], x, y, 50, t)
    mascot(c, 540, 1760, 1.4, t, "up", "happy")

def s_souvenir(c, t, lt, p, d):
    sky(c, t)
    city(c, t, seed=2, lit=0.3, dy=250)
    k = ease_out_back(min(lt / 0.45, 1))
    c.save(); c.translate(540, 820 + (1 - k) * -900); c.rotate(0.06 * math.sin(t * 2))
    rrect(c, -260, -280, 520, 600, 14); fill_stroke(c, hexc("FFFFFF"), 8)
    rrect(c, -220, -240, 440, 440, 6); src(c, hexc("2C1660")); c.fill()
    c.save(); c.rectangle(-220, -240, 440, 440); c.clip()
    glow_circle(c, 0, -40, 300, hexc("FFC94A"), 0.4)
    for (bx, col) in ((-100, hexc("8C7BD6")), (0, JACKET), (100, hexc("2EE6D6"))):
        old = R.JACKET; R.JACKET = col
        mascot(c, bx, 180, 0.62, t, "up" if bx == 0 else "idle", "happy")
        R.JACKET = old
    c.restore()
    c.restore()
    mascot(c, 540, 1780, 1.35, t, "hold", "happy", look=(0, -1))
    src(c, hexc("FF5C8A"))
    hx, hy = 540, 1780 - 160 * 1.35
    c.move_to(hx, hy + 18); c.curve_to(hx - 40, hy - 10, hx - 18, hy - 40, hx, hy - 18)
    c.curve_to(hx + 18, hy - 40, hx + 40, hy - 10, hx, hy + 18); c.fill()

def s_echange(c, t, lt, p, d):
    sky(c, t, hexc("120820"), hexc("33134A"))
    beams(c, t, (200, 880), 0.25)
    rrect(c, 40, 1640, 1000, 60, 10); fill_stroke(c, hexc("3B2A7A"), 6)
    for py in (1360, 1440, 1520):
        src(c, hexc("FF5C8A")); c.set_line_width(8); c.move_to(40, py); c.line_to(1040, py); c.stroke()
    period = 0.52
    ph = lt / period
    turn = int(ph) % 2
    f = ph - int(ph)
    punch = math.sin(min(f / 0.35, 1) * math.pi)
    boxer(c, 330, 1650, 1.25, t, 1, JACKET, punch if turn == 0 else 0)
    boxer(c, 750, 1650, 1.25, t + 0.4, -1, hexc("B892FF"), punch if turn == 1 else 0)
    if f < 0.3:
        hx = 590 if turn == 0 else 490
        for i in range(6):
            a = i * 1.05
            sparkle(c, hx + math.cos(a) * 70, 1430 + math.sin(a) * 70, 34 * (1 - f / 0.3), KEY)

def s_route(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("3A1A70"))
    mountain(c, 760, 1500, 900, 760 + 80 * p, hexc("4A2C8A"))
    mountain(c, 300, 1550, 700, 520, hexc("3A2272"))
    src(c, hexc("1C1240")); c.rectangle(0, 1500, W, H); c.fill()
    off = (lt * 260) % 360
    for i in range(5):
        pine(c, (i * 360 - off) % (W + 360) - 120, 1560, 1.2)
    mascot(c, 480, 1760, 1.45, t, "climb", "focus", look=(1, -0.5))
    # sac à dos
    c.save(); c.translate(480, 1760); c.scale(1.45, 1.45)
    rrect(c, -100, -195, 50, 110, 16); fill_stroke(c, hexc("FF5C8A"), 6)
    c.restore()

def s_egarer(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("3A1A70"))
    mountain(c, 540, 1950, 1600, 1500, hexc("4A2C8A"))
    src(c, hexc("FF8FC8")); c.set_line_width(22); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(60):
        x, y = path_point(i / 59)
        (c.move_to if i == 0 else c.line_to)(x, y)
    c.stroke()
    for (x, y) in ((150, 1500), (900, 1350), (180, 1050), (920, 900)):
        pine(c, x, y, 1.0)
    x, y = path_point(ease_io(p) * 0.85)
    wander = 30 * math.sin(lt * 5) * (1 - p)
    mascot(c, x + wander, y, 0.9, t, "climb", "open", look=(math.sin(lt * 3), 0))
    signpost(c, 860, 1700, t, 1 - p)
    fog(c, t, 1 - p * 0.7)

def s_sommet(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("4A1F7A"))
    k = ease_io(min(lt / 1.6, 1))
    peak_y = lerp(1250, 1100, k)
    beam_a = 0.45 * ease_io(min(lt / 0.5, 1))
    g = cairo.LinearGradient(0, 0, 0, peak_y)
    g.add_color_stop_rgba(0, 1, 0.85, 0.3, 0); g.add_color_stop_rgba(1, 1, 0.85, 0.3, beam_a)
    c.set_source(g); c.move_to(540, peak_y); c.line_to(300, 0); c.line_to(780, 0); c.close_path(); c.fill()
    mountain(c, 540, peak_y + 900, 1500, 900, hexc("4A2C8A"))
    for i in range(6):
        a = lt * 1.2 + i * 1.05
        sparkle(c, 540 + math.cos(a) * 330, peak_y - 200 + math.sin(a) * 160, 26, KEY, 0.9)
    star_path(c, 540, 420 - 20 * math.sin(t * 2), 90 * ease_out_back(lt / 0.5), 38); fill_stroke(c, KEY, 7)
    glow_circle(c, 540, 420, 260, KEY, 0.4)
    flag(c, 640, peak_y, t, min(1, max(0.01, (lt - 0.3) / 0.4)))
    mascot(c, 500, peak_y, 1.3, t, "wave" if lt > 0.8 else "up", "happy")

def s_balance(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("2C1660"))
    beams(c, t, (540,), 0.3)
    city(c, t, seed=9, lit=0.35, dy=300)
    tilt = 0.18 * math.sin(lt * 2.2)
    cx, cy = 540, 1050
    rrect(c, cx - 14, cy, 28, 520, 6); fill_stroke(c, hexc("8C7BD6"), 6)
    c.save(); c.translate(cx, cy); c.rotate(tilt)
    rrect(c, -380, -12, 760, 24, 10); fill_stroke(c, hexc("8C7BD6"), 6)
    c.restore()
    for side in (-1, 1):
        px = cx + side * 360 * math.cos(tilt)
        py = cy + side * 360 * math.sin(tilt)
        src(c, hexc("E9E3FF")); c.set_line_width(4)
        c.move_to(px, py); c.line_to(px - 110, py + 240); c.move_to(px, py); c.line_to(px + 110, py + 240); c.stroke()
        c.save(); c.translate(px, py + 250); c.scale(1, 0.3); c.arc(0, 0, 140, 0, math.pi); c.restore()
        fill_stroke(c, hexc("5B4BA8"), 6)
        if side < 0:
            coins(c, px, py + 230, 2 + int(6 * min(1, p * 1.4)), t)
        else:
            hourglass(c, px, py + 120, 0.75, p, t)
    mascot(c, 540, 1780, 1.3, t, "idle", "open", look=(math.sin(lt * 2.2), -1))

def s_pressé(c, t, lt, p, d):
    sky(c, t, hexc("140820"), hexc("3A1240"))
    city(c, t, seed=6, lit=0.45)
    shake = 10 * math.sin(t * 50)
    clock(c, 540 + shake, 820, 280, lt * (1 + 3 * p), 14)
    for side in (-1, 1):
        c.arc(540 + shake + side * 200, 560, 70, 0, 6.283); fill_stroke(c, hexc("FF5C8A"), 7)
    for i in range(3):
        a = (lt * 3 + i / 3) % 1
        src(c, hexc("FFFFFF"), 1 - a); c.set_line_width(8)
        c.arc(540, 820, 300 + a * 160, -2.4, -0.7); c.stroke()
    mascot(c, 540, 1780, 1.5, t, "up", "open")
    dy = (lt * 2 % 1) * 60
    src(c, hexc("7FD8FF"))
    dx, dyy = 540 + 70 * 1.5, 1780 - 290 * 1.5 + dy
    c.move_to(dx, dyy - 30); c.curve_to(dx + 22, dyy, dx + 16, dyy + 22, dx, dyy + 22); c.curve_to(dx - 16, dyy + 22, dx - 22, dyy, dx, dyy - 30); c.fill()

def s_bientot(c, t, lt, p, d):
    sky(c, t, hexc("05041A"), hexc("1E0F44"))
    city(c, t, seed=8, lit=p)
    w = 760
    rrect(c, 540 - w / 2, 860, w, 110, 55); fill_stroke(c, hexc("1C1240"), 8)
    fill = ease_io(min(p * 1.1, 1))
    if fill > 0.02:
        rrect(c, 540 - w / 2 + 12, 872, (w - 24) * fill, 86, 43); src(c, KEY); c.fill()
        glow_circle(c, 540 - w / 2 + (w - 24) * fill, 915, 140, GLOW, 0.6)
    draw_text(c, f"{int(fill * 100)}%", 540, 1080, 120, hexc("FFFFFF"), anchor="c")
    mascot(c, 540, 1780, 1.5, t, "hold", "happy", look=(0, -1))

def s_star(c, t, lt, p, d):
    sky(c, t)
    beams(c, t, (240, 540, 840), 0.3)
    rrect(c, 300, 1050, 480, 900, 8); fill_stroke(c, hexc("22175A"), 8)
    for wy in range(1110, 1700, 90):
        for wx in range(340, 760, 80):
            src(c, R.WIN_ON[(wx + wy) % 3] if (wx * 7 + wy) % 5 else R.WIN_OFF)
            c.rectangle(wx, wy, 40, 54); c.fill()
    glow_circle(c, 540, 860, 340, KEY, 0.4)
    mascot(c, 540, 1050, 1.3, t, "wave" if int(lt / (2 * BEAT)) % 2 else "up", "happy")
    crowd(c, t, lt)
    for i in range(int(lt * 3)):
        rnd = random.Random(i)
        a = (lt - i / 3) * 1.5
        sparkle(c, rnd.uniform(80, 1000), 1700 - a * 900, 20, KEY, max(0, 1 - a))

def s_outro(c, t, lt, p, d):
    sky(c, t, hexc("06051A"), hexc("150C3A"))
    glow_circle(c, 540, 1300, 500, KEY, 0.3 * (1 - p))
    bow = math.sin(min(lt / 0.8, 1) * math.pi)
    c.save(); c.translate(540, 1500); c.rotate(0)
    mascot(c, 0, 0, 1.6, t, "wave" if lt > 0.9 else "idle", "happy")
    c.restore()
    src(c, hexc("000000"), ease_io(max(0, (lt - 2.2) / 1.0))); c.paint()

# timings mesurés sur la vidéo d'origine (début, fin, scène)
TIMELINE = [
    (0.00, 1.45, s_zoo),
    (1.45, 2.45, s_envol),
    (2.45, 3.95, s_decolle),
    (3.95, 5.00, s_douze),
    (5.00, 8.45, s_cagoule),
    (8.45, 12.00, s_reves_grand),
    (12.00, 13.45, s_eclat),
    (13.45, 14.45, s_souvenir),
    (14.45, 16.45, s_echange),
    (16.45, 17.95, s_route),
    (17.95, 21.95, s_egarer),
    (21.95, 25.95, s_sommet),
    (25.95, 28.45, s_balance),
    (28.45, 30.45, s_pressé),
    (30.45, 31.45, s_bientot),
    (31.45, 35.50, s_star),
    (35.50, TOTAL, s_outro),
]

def frame(c, t):
    for (a, b, fn) in TIMELINE:
        if a <= t < b or b == TOTAL and t >= a:
            break
    lt = t - a
    d = b - a
    p = min(lt / d, 1)
    bt = max(0.0, t - OFFSET) % BEAT
    c.save()
    z = 1 + 0.06 * math.exp(-lt / 0.12) + 0.018 * math.exp(-bt / 0.09) + 0.02 * p
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    fn(c, t, lt, p, d)
    c.restore()
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0.05, 0.55)
    c.set_source(g); c.paint()
    if a > 0 and lt < 0.1:
        src(c, hexc("FFFFFF"), 0.35 * (1 - lt / 0.1)); c.paint()

def main():
    out = sys.argv[1]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    if "--preview" in sys.argv:
        for i, (a, b, fn) in enumerate(TIMELINE):
            frame(c, a + (b - a) * 0.65)
            surf.write_to_png(f"{out}_{i:02d}.png")
        return
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for f in range(int(round(TOTAL * FPS))):
        frame(c, f / FPS)
        surf.flush()
        ff.stdin.write(surf.get_data())
    ff.stdin.close()
    ff.wait()

if __name__ == "__main__":
    main()
