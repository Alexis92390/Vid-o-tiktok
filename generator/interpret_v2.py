"""V2 : mêmes timings, mêmes idées par passage, mais mises en scène différentes de la vidéo de référence.

Usage : python3 interpret_v2.py sortie.mp4 [--preview]
"""
import math
import random

import cairo

import interpret as I
import render as R
from interpret import (W, H, INK, KEY, GLOW, CAP, JACKET, HEAD, hexc, src, rrect, fill_stroke, glow_circle,
                       star_path, sparkle, ease_out_back, ease_io, lerp, sky, city, mascot, icon, flame,
                       draw_text, balaclava, s_souvenir, s_echange, s_bientot, s_outro, TOTAL, BEAT)

# ---------------------------------------------------------------- éléments
def snow_globe(c, t, crack=0.0):
    cx, cy, r = 540, 1180, 430
    c.save()
    c.arc(cx, cy, r, 0, 6.283); c.clip()
    g = cairo.LinearGradient(0, cy - r, 0, cy + r)
    g.add_color_stop_rgba(0, *hexc("1A1046")); g.add_color_stop_rgba(1, *hexc("3A1F78"))
    c.set_source(g); c.paint()
    c.save(); c.translate(cx, cy + 240); c.scale(0.55, 0.55); c.translate(-W / 2, -1700)
    city(c, t, seed=13, lit=0.3, hmin=500, hmax=900)
    c.restore()
    mascot(c, cx, cy + 300, 1.15, t, "idle", "sleepy", look=(0, -1))
    rnd = random.Random(1)
    src(c, hexc("FFFFFF"), 0.85)
    for _ in range(60):
        x = cx + rnd.uniform(-r, r) + 20 * math.sin(t + rnd.uniform(0, 6))
        y = cy - r + (rnd.uniform(0, 2 * r) + t * rnd.uniform(40, 90)) % (2 * r)
        c.arc(x, y, rnd.uniform(3, 7), 0, 6.283); c.fill()
    c.restore()
    c.arc(cx, cy, r, 0, 6.283)
    src(c, hexc("D9F7FF"), 0.12); c.fill_preserve()
    src(c, INK); c.set_line_width(10); c.stroke()
    c.arc(cx - 160, cy - 220, 120, 3.6, 4.4); src(c, hexc("FFFFFF"), 0.55); c.set_line_width(16); c.stroke()
    c.move_to(cx - 330, cy + 300); c.line_to(cx + 330, cy + 300); c.line_to(cx + 380, cy + 470); c.line_to(cx - 380, cy + 470); c.close_path()
    fill_stroke(c, hexc("5B2E9E"), 8)
    rrect(c, cx - 150, cy + 340, 300, 90, 20); fill_stroke(c, hexc("2EE6D6"), 6)
    draw_text(c, "ZOO", cx, cy + 388, 74, INK, anchor="c")
    if crack > 0:
        src(c, hexc("FFFFFF")); c.set_line_width(6)
        rnd = random.Random(3)
        for k in range(7):
            a = rnd.uniform(0, 6.28)
            x, y = cx + math.cos(a) * r * 0.3, cy - 100 + math.sin(a) * r * 0.3
            c.move_to(x, y)
            for _ in range(4):
                a += rnd.uniform(-0.6, 0.6)
                x += math.cos(a) * 70 * crack; y += math.sin(a) * 70 * crack
                c.line_to(x, y)
            c.stroke()

def paper_plane(c, x, y, s, ang):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.move_to(260, 0); c.line_to(-220, -120); c.line_to(-120, 10); c.close_path(); fill_stroke(c, hexc("FFFFFF"), 7)
    c.move_to(260, 0); c.line_to(-120, 10); c.line_to(-200, 110); c.close_path(); fill_stroke(c, hexc("D9CCFF"), 7)
    c.move_to(260, 0); c.line_to(-120, 10); c.line_to(-150, 50); c.close_path(); fill_stroke(c, hexc("B8A6F5"), 6)
    c.restore()

def jet_board(c, x, y, s, ang, t):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    for k in range(6):
        glow_circle(c, -190 - k * 45, 10 + 6 * math.sin(t * 30 + k), 60 * (1 - k / 6), GLOW, 0.6)
    rrect(c, -170, -14, 340, 30, 15); fill_stroke(c, hexc("FF5C8A"), 6)
    for wx in (-110, 110):
        c.arc(wx, 34, 20, 0, 6.283); fill_stroke(c, hexc("FFD23F"), 5)
    rrect(c, -200, -20, 60, 44, 10); fill_stroke(c, hexc("8C7BD6"), 6)
    c.restore()

def speed_lines(c, t, a=0.5, horizontal=False, seed=4):
    rnd = random.Random(seed)
    src(c, hexc("FFFFFF"), a); c.set_line_width(4)
    for _ in range(40):
        if horizontal:
            y = rnd.uniform(0, H); ln = rnd.uniform(80, 260)
            x = W - (rnd.uniform(0, W + 400) + t * 2600) % (W + 400)
            c.move_to(x, y); c.line_to(x + ln, y)
        else:
            x = rnd.uniform(0, W); ln = rnd.uniform(80, 260)
            y = (rnd.uniform(0, H + 400) + t * 2600) % (H + 400) - 200
            c.move_to(x, y); c.line_to(x, y - ln)
    c.stroke()

def cake(c, x, y, n_lit, t):
    rrect(c, x - 260, y, 520, 200, 30); fill_stroke(c, hexc("FF8FC8"), 8)
    rrect(c, x - 200, y - 130, 400, 140, 30); fill_stroke(c, hexc("FFF6E0"), 8)
    src(c, hexc("FF5C8A"))
    for i in range(9):
        c.arc(x - 230 + i * 58, y + 6, 26, 0, math.pi); c.fill()
    for i in range(12):
        cx = x - 176 + i * 32
        rrect(c, cx - 8, y - 210, 16, 80, 6); fill_stroke(c, CAP if i % 2 else KEY, 4)
        if i < n_lit:
            c.save(); c.translate(cx, y - 214)
            glow_circle(c, 0, -14, 34, GLOW, 0.6)
            c.move_to(0, 0); c.curve_to(-14, -12, -4, -26, 0, -38); c.curve_to(4, -26, 14, -12, 0, 0)
            src(c, hexc("FFE36E")); c.fill()
            c.restore()
    draw_text(c, f"{n_lit} ANS", x, y + 110, 80, INK, anchor="c")

CONSTELLATIONS = [
    # (centre, points normalisés, segments)
    ((300, 520), [(-1, 0.2), (0, -0.9), (1, 0.2), (1, 1), (-1, 1)], [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]),        # maison
    ((780, 420), [(-1, 0.8), (-1, -0.5), (-0.5, 0.1), (0, -0.9), (0.5, 0.1), (1, -0.5), (1, 0.8)],
     [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0)]),                                                    # couronne
    ((560, 820), [(math.cos(a) , math.sin(a)) for a in [i * math.pi * 2 / 7 for i in range(7)]],
     [(i, (i + 1) % 7) for i in range(7)]),                                                                         # disque
    ((850, 860), [(-1, 0.4), (-0.6, -0.2), (0.5, -0.2), (1, 0.4), (-0.6, 0.6), (0.6, 0.6)],
     [(0, 1), (1, 2), (2, 3), (3, 0), (4, 4), (5, 5)]),                                                             # voiture
    ((240, 980), [(math.cos(-math.pi / 2 + i * 4 * math.pi / 5), math.sin(-math.pi / 2 + i * 4 * math.pi / 5)) for i in range(5)],
     [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]),                                                                     # étoile
]

def constellations(c, t, prog, gold=0.0, scale=110):
    for ci, ((cx, cy), pts, segs) in enumerate(CONSTELLATIONS):
        k = min(max(prog * len(CONSTELLATIONS) - ci, 0), 1)
        if k <= 0:
            continue
        P = [(cx + px * scale, cy + py * scale) for (px, py) in pts]
        col = (lerp(0.75, 1.0, gold), lerp(0.85, 0.82, gold), lerp(1.0, 0.25, gold))
        if gold > 0:
            glow_circle(c, cx, cy, scale * 2.2, KEY, 0.25 * gold)
        c.set_source_rgba(*col, 0.85); c.set_line_width(5 + 4 * gold)
        nseg = k * len(segs)
        for si, (a, b) in enumerate(segs):
            if si >= nseg:
                break
            f = min(1, nseg - si)
            c.move_to(*P[a]); c.line_to(lerp(P[a][0], P[b][0], f), lerp(P[a][1], P[b][1], f)); c.stroke()
        for (px, py) in P:
            sparkle(c, px, py, 18 + 6 * math.sin(t * 5 + px), (1, 1, 1, 1) if gold < 0.5 else KEY)

def rooftop(c, y):
    src(c, hexc("1C1240")); c.rectangle(0, y, W, H); c.fill()
    src(c, hexc("2C1F66")); c.rectangle(0, y, W, 24); c.fill()
    for x in (90, 960):
        rrect(c, x - 40, y - 140, 80, 140, 10); fill_stroke(c, hexc("3B2A7A"), 6)

def lying_mascot(c, x, y, s, t, sit=0.0):
    c.save(); c.translate(x, y); c.rotate(lerp(math.pi / 2, 0, sit))
    mascot(c, 0, 0, s, t, "up" if sit > 0.5 else "idle", "happy")
    balaclava(c, 0, -abs(math.sin(t * math.pi / BEAT)) * 6 * s, s)
    c.restore()

def shooting_stars(c, t, n, seed=5, speed=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.uniform(0, 1.2)
        k = ((t * speed + ph) % 1.2) / 1.2
        x0, y0 = rnd.uniform(-200, W), rnd.uniform(-200, 900)
        x, y = x0 + k * 900, y0 + k * 600
        g = cairo.LinearGradient(x, y, x - 220, y - 146)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.9 * (1 - k)); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.set_source(g); c.set_line_width(6); c.move_to(x, y); c.line_to(x - 220, y - 146); c.stroke()
        sparkle(c, x, y, 16, (1, 1, 1, 1 - k))

def scooter(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    for wx in (-120, 120):
        c.arc(wx, -30, 34, 0, 6.283); fill_stroke(c, hexc("1C1240"), 6)
        src(c, hexc("8C7BD6")); c.arc(wx, -30, 12, 0, 6.283); c.fill()
    rrect(c, -150, -80, 300, 30, 12); fill_stroke(c, hexc("2EE6D6"), 6)
    src(c, INK); c.set_line_width(14); c.move_to(120, -60); c.line_to(150, -280); c.stroke()
    rrect(c, 110, -300, 90, 20, 8); fill_stroke(c, hexc("FF5C8A"), 5)
    glow_circle(c, 170, -230, 90, KEY, 0.4)
    c.restore()

def road_sign(c, x, y, s, kind):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -8, -300, 16, 300, 5); fill_stroke(c, hexc("8C7BD6"), 5)
    rrect(c, -110, -400, 220, 120, 16); fill_stroke(c, hexc("2E9E5B") if kind else hexc("2E6BD9"), 6)
    src(c, hexc("FFFFFF")); c.set_line_width(10)
    c.move_to(-60, -340); c.line_to(50, -340); c.stroke()
    c.move_to(20, -365); c.line_to(60, -340); c.line_to(20, -315); c.stroke()
    c.restore()

def make_maze(cols, rows, seed=7):
    rnd = random.Random(seed)
    walls = {(x, y): {"N", "S", "E", "W"} for x in range(cols) for y in range(rows)}
    seen = {(0, rows - 1)}
    stack = [(0, rows - 1)]
    D = {"N": (0, -1, "S"), "S": (0, 1, "N"), "E": (1, 0, "W"), "W": (-1, 0, "E")}
    while stack:
        x, y = stack[-1]
        opts = [(d, x + dx, y + dy, o) for d, (dx, dy, o) in D.items() if (x + dx, y + dy) in walls and (x + dx, y + dy) not in seen]
        if not opts:
            stack.pop(); continue
        d, nx, ny, o = rnd.choice(opts)
        walls[(x, y)].discard(d); walls[(nx, ny)].discard(o)
        seen.add((nx, ny)); stack.append((nx, ny))
    # chemin entrée (bas-gauche) -> sortie (haut-droite)
    start, goal = (0, rows - 1), (cols - 1, 0)
    prev = {start: None}
    q = [start]
    while q:
        cur = q.pop(0)
        if cur == goal:
            break
        for d, (dx, dy, o) in D.items():
            n = (cur[0] + dx, cur[1] + dy)
            if d not in walls[cur] and n not in prev:
                prev[n] = cur; q.append(n)
    path = [goal]
    while prev[path[-1]] is not None:
        path.append(prev[path[-1]])
    return walls, path[::-1]

MAZE = make_maze(7, 10)

def maze(c, t, p):
    walls, path = MAZE
    cs, ox, oy = 130, 85, 520
    rrect(c, ox - 20, oy - 20, 7 * cs + 40, 10 * cs + 40, 24); fill_stroke(c, hexc("2A1C5E"), 8)
    src(c, hexc("FF8FC8")); c.set_line_width(14); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for (x, y), ws in walls.items():
        X, Y = ox + x * cs, oy + y * cs
        if "N" in ws and not (x, y) == (6, 0): c.move_to(X, Y); c.line_to(X + cs, Y)
        if "W" in ws: c.move_to(X, Y); c.line_to(X, Y + cs)
        if "S" in ws and not (x, y) == (0, 9): c.move_to(X, Y + cs); c.line_to(X + cs, Y + cs)
        if "E" in ws: c.move_to(X + cs, Y); c.line_to(X + cs, Y + cs)
    c.stroke()
    # position le long du chemin, avec hésitations
    k = ease_io(p) * (len(path) - 1)
    k += 0.35 * math.sin(p * 25) * (1 - p)
    k = min(max(k, 0), len(path) - 1)
    i = int(k); f = k - i
    a = path[i]; b = path[min(i + 1, len(path) - 1)]
    mx = ox + (lerp(a[0], b[0], f) + 0.5) * cs
    my = oy + (lerp(a[1], b[1], f) + 0.5) * cs
    # obscurité sauf autour de la mascotte
    g = cairo.RadialGradient(mx, my, 120, mx, my, 520 + 400 * p)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.02, 0.01, 0.08, 0.85)
    c.set_source(g); c.paint()
    glow_circle(c, ox + 6.5 * cs, oy - 40, 200, KEY, 0.6)
    star_path(c, ox + 6.5 * cs, oy - 60, 50, 22); fill_stroke(c, KEY, 5)
    mascot(c, mx, my + 40, 0.38, t, "climb", "open", look=(math.sin(t * 4), 0))
    return mx, my

def tower(c, cam, t):
    x = 540
    base = 1900 + cam
    rrect(c, x - 200, base - 900, 400, 900, 8); fill_stroke(c, hexc("22175A"), 8)
    for wy in range(int(base - 860), int(base - 40), 90):
        for wx in range(x - 160, x + 160, 80):
            src(c, R.WIN_ON[(wx + wy) % 3] if (wx + wy) % 4 else R.WIN_OFF); c.rectangle(wx, wy, 40, 54); c.fill()
    # pylône
    src(c, hexc("8C7BD6")); c.set_line_width(10)
    top = base - 2300
    c.move_to(x - 140, base - 900); c.line_to(x - 20, top); c.move_to(x + 140, base - 900); c.line_to(x + 20, top); c.stroke()
    c.set_line_width(6)
    for k in range(14):
        y1 = base - 900 - k * 100
        w1 = lerp(140, 20, (k * 100) / 1400)
        w2 = lerp(140, 20, ((k + 1) * 100) / 1400)
        c.move_to(x - w1, y1); c.line_to(x + w2, y1 - 100); c.move_to(x + w1, y1); c.line_to(x - w2, y1 - 100)
    c.stroke()
    c.arc(x, top - 20, 22, 0, 6.283)
    fill_stroke(c, hexc("FF3B3B") if int(t * 2) % 2 else hexc("7A1A2A"), 5)
    return top

def firework(c, x, y, age, col, seed):
    if age < 0 or age > 1.2:
        return
    rnd = random.Random(seed)
    r = 260 * ease_io(min(age / 0.6, 1))
    a = 1 - max(0, (age - 0.4) / 0.8)
    for i in range(18):
        ang = i * math.pi * 2 / 18 + rnd.uniform(-0.05, 0.05)
        px, py = x + math.cos(ang) * r, y + math.sin(ang) * r + 60 * age * age
        src(c, col, a); c.arc(px, py, 9, 0, 6.283); c.fill()
        src(c, col, a * 0.5); c.set_line_width(4)
        c.move_to(px, py); c.line_to(x + math.cos(ang) * r * 0.6, y + math.sin(ang) * r * 0.6 + 40 * age * age); c.stroke()
    glow_circle(c, x, y, 200, col, 0.3 * a)

def small_clock(c, x, y, r, t):
    c.arc(x, y, r, 0, 6.283); fill_stroke(c, hexc("FFF6E0"), 5)
    src(c, INK); c.set_line_width(5)
    c.move_to(x, y); c.line_to(x + math.cos(t * 8) * r * 0.7, y + math.sin(t * 8) * r * 0.7); c.stroke()
    c.move_to(x, y); c.line_to(x, y - r * 0.5); c.stroke()

def coin(c, x, y, r, t):
    c.save(); c.translate(x, y); c.scale(abs(math.cos(t * 6)) * 0.8 + 0.2, 1)
    c.arc(0, 0, r, 0, 6.283); fill_stroke(c, KEY, 5)
    draw_text(c, "€", 0, 4, r * 1.1, hexc("C98A00"), anchor="c")
    c.restore()

# ---------------------------------------------------------------- scènes
def v_zoo(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("261452"))
    snow_globe(c, t, crack=max(0, (p - 0.7) / 0.3))

def v_envol(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("2C1660"))
    city(c, t, seed=4, lit=0.35, dy=ease_io(p) * 500)
    rnd = random.Random(6)
    for i in range(14):  # éclats du globe
        a = rnd.uniform(0, 6.28); sp = rnd.uniform(400, 900)
        x = 540 + math.cos(a) * sp * lt; y = 1180 + math.sin(a) * sp * lt + 900 * lt * lt
        c.save(); c.translate(x, y); c.rotate(lt * 6 + i)
        c.move_to(0, -30); c.line_to(26, 20); c.line_to(-22, 16); c.close_path()
        src(c, hexc("D9F7FF"), 0.7); c.fill(); c.restore()
    k = ease_io(p)
    x, y = lerp(260, 640, k), lerp(1500, 820, k)
    mascot(c, x - 30, y - 10, 1.0, t, "up", "happy")
    paper_plane(c, x, y + 30, 1.0, -0.35)

def v_decolle(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("33176E"))
    city(c, t, seed=5, lit=0.5, dy=ease_io(p) * 900)
    k = ease_io(p)
    c.move_to(-50, 1950 + k * 900); c.line_to(500, 1950 + k * 900); c.curve_to(650, 1950 + k * 900, 700, 1800 + k * 900, 720, 1650 + k * 900)
    c.line_to(720, 1950 + k * 900); c.close_path(); fill_stroke(c, hexc("3B2A7A"), 8)
    speed_lines(c, t, 0.35 * p)
    x, y = lerp(300, 620, k), lerp(1650, 950, k)
    ang = lerp(0, -0.5, k)
    jet_board(c, x, y + 40, 1.0, ang, t)
    c.save(); c.translate(x, y); c.rotate(ang)
    mascot(c, 0, 0, 1.15, t, "up", "happy")
    c.restore()

def v_douze(c, t, lt, p, d):
    sky(c, t, hexc("140A30"), hexc("2C1660"))
    for i in range(10):
        rnd = random.Random(i)
        x = rnd.uniform(80, 1000); y = (rnd.uniform(0, H) + lt * 300) % H
        c.save(); c.translate(x, y); c.rotate(lt * 3 + i)
        rrect(c, -10, -18, 20, 36, 4); src(c, [KEY, CAP, hexc("FF5C8A")][i % 3]); c.fill(); c.restore()
    n = 1 + int(min(p * 1.15, 1) * 11.99)
    cake(c, 540, 820, n, t)
    mascot(c, 540, 1800, lerp(0.7, 1.5, ease_io(p)), t, "up" if n == 12 else "idle", "happy")

def v_cagoule(c, t, lt, p, d):
    sky(c, t, hexc("05041A"), hexc("1E0F44"))
    constellations(c, t, ease_io(min(p * 1.2, 1)))
    rooftop(c, 1600)
    rrect(c, 230, 1560, 620, 60, 26); fill_stroke(c, hexc("FF8FC8"), 6)
    lying_mascot(c, 300, 1555, 1.25, t)

def v_reves(c, t, lt, p, d):
    sky(c, t, hexc("05041A"), hexc("261452"))
    shooting_stars(c, t, int(2 + 6 * p))
    constellations(c, t, 1, gold=ease_io(p), scale=110 + 30 * p)
    rooftop(c, 1600)
    rrect(c, 230, 1560, 620, 60, 26); fill_stroke(c, hexc("FF8FC8"), 6)
    sit = ease_io(min(lt / 0.8, 1))
    lying_mascot(c, lerp(300, 540, sit), 1555, 1.25, t, sit=sit)

def v_pluie_etoiles(c, t, lt, p, d):
    sky(c, t, hexc("05041A"), hexc("1E0F44"))
    shooting_stars(c, t, 18, seed=9, speed=1.6)
    for ci, ((cx, cy), pts, segs) in enumerate(CONSTELLATIONS):
        for j, (px, py) in enumerate(pts):
            a = math.atan2(py, px) if (px or py) else j
            r = 110 + 900 * lt
            sparkle(c, cx + math.cos(a) * r, cy + math.sin(a) * r + 400 * lt * lt, 22, KEY, max(0, 1 - p))
    rooftop(c, 1600)
    mascot(c, 540, 1600, 1.25, t, "up", "happy")
    balaclava(c, 540, 1600 - abs(math.sin(t * math.pi / BEAT)) * 6 * 1.25, 1.25)

def v_route(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("3A1A70"))
    off = lt * 900
    c.save(); c.translate(-(off * 0.3) % 400, 0)
    city(c, t, seed=14, lit=0.4, ground=1500, hmin=300, hmax=700)
    c.restore()
    src(c, hexc("1C1240")); c.rectangle(0, 1500, W, H); c.fill()
    src(c, hexc("2A2060")); c.rectangle(0, 1560, W, 260); c.fill()
    src(c, KEY)
    for i in range(8):
        x = (i * 220 - off) % (W + 220) - 110
        c.rectangle(x, 1680, 120, 16)
    c.fill()
    for i in range(2):
        x = (i * 700 + 900 - off * 1.2) % (W + 700) - 200
        road_sign(c, x, 1560, 1.0, i)
    speed_lines(c, t, 0.25, horizontal=True)
    scooter(c, 520, 1800, 1.2, t)
    mascot(c, 520, 1800 - 80 * 1.2, 1.2, t, "hold", "happy", look=(1, 0))
    c.save(); c.translate(520, 1800 - 80 * 1.2); c.scale(1.2, 1.2)
    rrect(c, -100, -195, 50, 110, 16); fill_stroke(c, hexc("FF5C8A"), 6)
    c.restore()

def v_labyrinthe(c, t, lt, p, d):
    sky(c, t, hexc("05041A"), hexc("1E0F44"), stars=False)
    maze(c, t, p)

def v_sommet(c, t, lt, p, d):
    sky(c, t, hexc("05041A"), hexc("2C1660"))
    climb = ease_io(min(lt / 1.6, 1))
    cam = climb * 1500
    city(c, t, seed=3, lit=0.6, dy=cam * 0.6)
    top = tower(c, cam, t)
    my = lerp(1900 + cam - 900, top + 60, climb)
    if lt < 1.6:
        mascot(c, 540, my, 0.9, t, "climb", "focus", look=(0, -1))
    else:
        cols = [KEY, CAP, hexc("FF5C8A"), hexc("B892FF")]
        for i in range(8):
            ft = lt - 1.6 - i * BEAT / 2
            rnd = random.Random(i)
            firework(c, rnd.uniform(150, 930), rnd.uniform(250, 800), ft % 1.6 if ft > 0 else -1, cols[i % 4], i)
        glow_circle(c, 540, top, 300, KEY, 0.35)
        mascot(c, 540, top + 40, 1.0, t, "wave" if int(lt / BEAT) % 2 else "up", "happy")

def v_jongle(c, t, lt, p, d):
    sky(c, t, hexc("0A0820"), hexc("2C1660"))
    I.beams(c, t, (540,), 0.25)
    city(c, t, seed=9, lit=0.35, dy=300)
    mx, my = 540, 1780
    mascot(c, mx, my, 1.5, t, "up", "open", look=(math.sin(t * 4), -1))
    n = 3 + int(3 * p)
    for i in range(n):
        ph = (t * 1.25 + i / n) % 1
        x = mx + math.cos(ph * 2 * math.pi) * 300
        y = my - 430 * 1.5 / 1.5 - 300 - math.sin(ph * math.pi) * 520
        if i % 2 == 0:
            coin(c, x, y, 48, t + i)
        else:
            small_clock(c, x, y, 48, t + i)

def v_course(c, t, lt, p, d):
    sky(c, t, hexc("140820"), hexc("3A1240"))
    off = lt * 1500
    c.save(); c.translate(-(off * 0.4) % 400, 0)
    city(c, t, seed=6, lit=0.45, hmin=500, hmax=1000)
    c.restore()
    src(c, KEY)
    for i in range(8):
        x = (i * 220 - off) % (W + 220) - 110
        c.rectangle(x, 1800, 120, 14)
    c.fill()
    speed_lines(c, t, 0.35, horizontal=True, seed=8)
    # horloge géante qui roule derrière
    cx = lerp(-120, 220, p)
    c.save(); c.translate(cx, 1500); c.rotate(-t * 4)
    I.clock(c, 0, 0, 280, lt, 20)
    c.restore()
    bob = abs(math.sin(t * 10)) * 30
    mascot(c, 720, 1790 - bob, 1.3, t * 3, "climb", "open", look=(-1, 0))
    for i in range(3):  # gouttes de sueur
        a = (lt * 3 + i / 3) % 1
        src(c, hexc("7FD8FF"), 1 - a)
        c.arc(720 - 60 - a * 120, 1790 - 360 - bob + a * 80 - i * 30, 12, 0, 6.283); c.fill()

def v_star(c, t, lt, p, d):
    sky(c, t, hexc("05041A"), hexc("2C1660"))
    city(c, t, seed=8, lit=0.8, hmin=700, hmax=1000)
    # panneau géant
    bx, by, bw, bh = 140, 380, 800, 620
    rrect(c, bx - 20, by - 20, bw + 40, bh + 40, 24); fill_stroke(c, hexc("1C1240"), 8)
    c.save(); rrect(c, bx, by, bw, bh, 12); c.clip()
    g = cairo.LinearGradient(bx, by, bx + bw, by + bh)
    g.add_color_stop_rgba(0, *hexc("FF5C8A")); g.add_color_stop_rgba(1, *hexc("2E6BD9"))
    c.set_source(g); c.paint()
    mascot(c, 540, by + bh + 520, 2.6, t, "wave", "happy")
    src(c, hexc("FFFFFF"), 0.08)
    for y in range(by, by + bh, 8):
        c.rectangle(bx, y, bw, 3)
    c.fill()
    c.restore()
    for i in range(2):
        rrect(c, bx + 160 + i * 440, by + bh + 20, 30, 400, 6); fill_stroke(c, hexc("3B2A7A"), 6)
    # paparazzis + flashs
    rnd = random.Random(5)
    for i in range(9):
        x = 60 + i * 120 + rnd.uniform(-15, 15)
        hb = 1720 + rnd.uniform(0, 50)
        src(c, hexc("0A0620")); c.arc(x, hb, 46, 0, 6.283); c.fill(); c.rectangle(x - 58, hb + 30, 116, 260); c.fill()
        rrect(c, x - 30, hb - 120, 60, 44, 8); src(c, hexc("0A0620")); c.fill()
        flash_t = (lt * 1.7 + rnd.uniform(0, 1)) % 1
        if flash_t < 0.12:
            glow_circle(c, x, hb - 100, 220, hexc("FFFFFF"), 0.9 * (1 - flash_t / 0.12))
    if int(lt / BEAT) != int((lt - 1 / 30) / BEAT):
        src(c, hexc("FFFFFF"), 0.25); c.paint()

TIMELINE = [
    (0.00, 1.45, v_zoo),
    (1.45, 2.45, v_envol),
    (2.45, 3.95, v_decolle),
    (3.95, 5.00, v_douze),
    (5.00, 8.45, v_cagoule),
    (8.45, 12.00, v_reves),
    (12.00, 13.45, v_pluie_etoiles),
    (13.45, 14.45, s_souvenir),
    (14.45, 16.45, s_echange),
    (16.45, 17.95, v_route),
    (17.95, 21.95, v_labyrinthe),
    (21.95, 25.95, v_sommet),
    (25.95, 28.45, v_jongle),
    (28.45, 30.45, v_course),
    (30.45, 31.45, s_bientot),
    (31.45, 35.50, v_star),
    (35.50, TOTAL, s_outro),
]

if __name__ == "__main__":
    I.TIMELINE = TIMELINE
    I.main()
