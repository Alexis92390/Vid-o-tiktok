"""Lyric video animé 9:16 (style vectoriel plat, karaoké mot par mot, mot-clé géant lumineux).

Usage : python3 render.py beat.wav sortie.mp4 [--preview]
"""
import math
import random
import subprocess
import sys

import cairo

from beat import BAR, BEAT

W, H, FPS = 1080, 1920, 30
FONT = "Inter Display Black"
HANDLE = "@TON_COMPTE"

# ---------------------------------------------------------------- palette
def hexc(h, a=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)

SKY_TOP = hexc("0B0826")
SKY_BOT = hexc("2C1660")
BLD = [hexc("1B1242"), hexc("22175A"), hexc("170F3A")]
WIN_OFF = hexc("33276E")
WIN_ON = [hexc("FFC94A"), hexc("FFB020"), hexc("4FF0E0")]
INK = hexc("0A0620")
JACKET = hexc("FF9F1C")
JACKET_D = hexc("D97706")
CAP = hexc("2EE6D6")
CAP_D = hexc("16A79B")
HEAD = hexc("2A1F55")
KEY = hexc("FFD23F")
GLOW = hexc("FF8A00")

# ---------------------------------------------------------------- paroles
# (texte, mot-clé, scène) — une ligne par mesure
LINES = [
    ("J'AI GRANDI SOUS LA PLUIE", "PLUIE", "pluie"),
    ("MAIS J'AI GARDÉ LE SOURIRE", "SOURIRE", "sourire"),
    ("UN CARNET, UN STYLO,", "STYLO,", "stylo"),
    ("J'ÉCRIS MES RÊVES EN GROS", "GROS", "reves"),
    ("LES NUITS SONT LONGUES,", "LONGUES,", "nuits"),
    ("MAIS LA FLAMME EST LÀ", "FLAMME", "flamme"),
    ("MARCHE APRÈS MARCHE,", "MARCHE,", "marches"),
    ("JE MONTE SANS BRUIT", "MONTE", "monte"),
    ("ILS DISAIENT « JAMAIS »", "« JAMAIS »", "jamais"),
    ("AUJOURD'HUI ILS ÉCOUTENT", "ÉCOUTENT", "foule"),
    ("TOUT LE QUARTIER S'ALLUME", "S'ALLUME", "allume"),
    ("ET NOUS ON VISE LA LUNE", "LUNE", "lune"),
]

# ---------------------------------------------------------------- utilitaires
def ease_out_back(x, s=1.9):
    x = min(max(x, 0), 1) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2

def ease_io(x):
    x = min(max(x, 0), 1)
    return x * x * (3 - 2 * x)

def lerp(a, b, x):
    return a + (b - a) * x

def src(c, col, a=None):
    if a is None:
        c.set_source_rgba(*col)
    else:
        c.set_source_rgba(col[0], col[1], col[2], a)

def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()

def fill_stroke(c, col, lw=6, ink=INK):
    src(c, col)
    c.fill_preserve()
    src(c, ink)
    c.set_line_width(lw)
    c.stroke()

def glow_circle(c, x, y, r, col, a=0.5):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.set_source(g)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.fill()

def star_path(c, x, y, r1, r2, n=5, rot=-math.pi / 2):
    for i in range(2 * n):
        r = r1 if i % 2 == 0 else r2
        a = rot + i * math.pi / n
        (c.move_to if i == 0 else c.line_to)(x + r * math.cos(a), y + r * math.sin(a))
    c.close_path()

def sparkle(c, x, y, r, col, a=1):
    src(c, col, a)
    c.move_to(x, y - r)
    for (dx, dy) in ((0.18, -0.18), (1, 0), (0.18, 0.18), (0, 1), (-0.18, 0.18), (-1, 0), (-0.18, -0.18), (0, -1)):
        c.line_to(x + dx * r, y + dy * r)
    c.fill()

# ---------------------------------------------------------------- texte
SX = 0.80  # compression horizontale -> rendu « condensed »

def text_w(c, s, size):
    c.select_font_face(FONT)
    c.set_font_size(size)
    return c.text_extents(s).x_advance * SX

def draw_text(c, s, x, y, size, col, a=1.0, glow=None, scale=1.0, anchor="l"):
    c.save()
    c.select_font_face(FONT)
    c.set_font_size(size)
    w = c.text_extents(s).x_advance * SX
    c.translate(x + (w / 2 if anchor == "l" else 0), y - size * 0.35)
    c.scale(scale * SX, scale)
    c.move_to(-w / 2 / SX, size * 0.35)
    c.text_path(s)
    if glow:
        for i in range(7, 0, -1):
            src(c, glow, 0.07 * a)
            c.set_line_width(size * 0.05 * i)
            c.set_line_join(cairo.LINE_JOIN_ROUND)
            c.stroke_preserve()
    src(c, col, a)
    c.fill()
    c.restore()

def lyric_layer(c, idx, lt):
    text, key, _ = LINES[idx]
    words = text.split(" ")
    span = 3.0 * BEAT
    wt = [i * span / len(words) for i in range(len(words))]
    key_words = key.split(" ")
    ki = next(i for i in range(len(words)) if words[i:i + len(key_words)] == key_words)
    key_t = wt[ki]

    size = 66
    # petite ligne karaoké (coupée en 2 si trop large)
    rows = [words]
    if text_w(c, text, size) > 940:
        mid = len(words) // 2
        rows = [words[:mid], words[mid:]]
    gi = 0
    for r, row in enumerate(rows):
        line = " ".join(row)
        lw = text_w(c, line, size)
        x = (W - lw) / 2
        y = 250 + r * 80
        for wd in row:
            ww = text_w(c, wd + " ", size)
            if lt >= wt[gi]:
                draw_text(c, wd, x, y, size, hexc("FFFFFF"))
            else:
                draw_text(c, wd, x, y, size, hexc("FFFFFF"), a=0.30)
            x += ww
            gi += 1

    # mot-clé géant
    if lt >= key_t:
        d = lt - key_t
        s = ease_out_back(d / 0.28)
        flick = 0.85 + 0.15 * math.sin(lt * 30) if d < 0.3 else 1
        ksize = 190 if len(key) <= 8 else 150
        ky = 250 + len(rows) * 80 + ksize * 0.55
        draw_text(c, key, W / 2, ky, ksize, KEY, a=flick, glow=GLOW, scale=max(s, 0.01), anchor="c")

# ---------------------------------------------------------------- décor
_CITY = {}

def city_layout(seed, ground, hmin=450, hmax=1150):
    k = (seed, ground, hmin, hmax)
    if k in _CITY:
        return _CITY[k]
    rnd = random.Random(seed)
    blds = []
    x = -60
    while x < W + 60:
        w = rnd.randint(130, 240)
        h = rnd.randint(hmin, hmax)
        wins = []
        for wy in range(int(ground - h + 50), int(ground - 60), 78):
            for wx in range(x + 24, x + w - 40, 52):
                wins.append((wx, wy, rnd.random(), rnd.choice(WIN_ON), rnd.random()))
        blds.append((x, w, h, rnd.choice(BLD), wins))
        x += w + rnd.randint(-10, 18)
    _CITY[k] = blds
    return blds

def sky(c, t, top=SKY_TOP, bot=SKY_BOT, stars=True):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *top)
    g.add_color_stop_rgba(1, *bot)
    c.set_source(g)
    c.paint()
    if stars:
        rnd = random.Random(3)
        for _ in range(70):
            x, y, ph = rnd.uniform(0, W), rnd.uniform(0, H * 0.75), rnd.uniform(0, 6.28)
            a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 3 + ph))
            src(c, hexc("FFFFFF"), a * 0.8)
            c.arc(x, y, rnd.uniform(1.5, 3.5), 0, 6.283)
            c.fill()

def city(c, t, seed=1, ground=1700, lit=0.35, dy=0, hmin=450, hmax=1150, light_order=None):
    for (x, w, h, col, wins) in city_layout(seed, ground, hmin, hmax):
        src(c, col)
        c.rectangle(x, ground - h + dy, w, h + 400)
        c.fill()
        src(c, INK, 0.5)
        c.rectangle(x + w - 14, ground - h + dy, 14, h + 400)
        c.fill()
        for (wx, wy, r, on, ph) in wins:
            key = r if light_order is None else light_order(wx, wy, r)
            if key < lit:
                fl = 0.85 + 0.15 * math.sin(t * 2 + ph * 10)
                src(c, on, fl)
            else:
                src(c, WIN_OFF)
            c.rectangle(wx, wy + dy, 26, 40)
            c.fill()
    src(c, hexc("120A2E"))
    c.rectangle(0, ground + dy, W, H)
    c.fill()

def moon(c, x, y, r, t):
    glow_circle(c, x, y, r * 2.4, hexc("FFE9A8"), 0.35)
    src(c, hexc("FFF1C1"))
    c.arc(x, y, r, 0, 6.283)
    c.fill()
    src(c, hexc("E8D49A"))
    for (dx, dy, rr) in ((-0.3, -0.2, 0.18), (0.25, 0.3, 0.14), (0.35, -0.35, 0.09)):
        c.arc(x + dx * r, y + dy * r, rr * r, 0, 6.283)
        c.fill()

# ---------------------------------------------------------------- mascotte
def mascot(c, x, y, s, t, pose="idle", eyes="open", look=(0, 0)):
    """Pieds en (x, y). ~300 unités de haut avant échelle s."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    bob = abs(math.sin(t * math.pi / BEAT)) * 6
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)

    # jambes + baskets
    for lx in (-30, 8):
        rrect(c, lx, -90, 22, 82, 8)
        fill_stroke(c, hexc("1C1240"), 5)
        rrect(c, lx - 8, -16, 44, 20, 9)
        fill_stroke(c, hexc("FFFFFF"), 5)
        src(c, CAP)
        c.rectangle(lx - 6, -2, 40, 4)
        c.fill()

    c.translate(0, -bob)

    def arm(x0, y0, x1, y1, x2, y2):
        for lw, col in ((34, INK), (24, JACKET)):
            c.set_line_width(lw)
            src(c, col)
            c.move_to(x0, y0)
            c.curve_to(x1, y1, x1, y1, x2, y2)
            c.stroke()
        src(c, HEAD)
        c.arc(x2, y2, 14, 0, 6.283)
        fill_stroke(c, HEAD, 5)

    sw = math.sin(t * math.pi / BEAT) * 8
    arms = {
        "idle": [(-52, -160, -78, -120, -70, -80 + sw), (52, -160, 78, -120, 70, -80 - sw)],
        "wave": [(-52, -160, -78, -120, -70, -80), (52, -160, 110, -190, 95 + 20 * math.sin(t * 9), -260)],
        "write": [(-52, -160, -40, -110, 10, -105), (52, -160, 90, -120, 60, -95 + 6 * math.sin(t * 14))],
        "hold": [(-52, -160, -78, -120, -70, -80), (52, -160, 100, -150, 105, -175)],
        "up": [(-52, -160, -110, -200, -95, -270 + sw), (52, -160, 110, -200, 95, -270 - sw)],
        "cross": [(-52, -160, -20, -120, 40, -125), (52, -160, 20, -110, -40, -118)],
        "climb": [(-52, -160, -90, -140, -80, -95 - sw), (52, -160, 80, -110, 90, -85 + sw)],
    }[pose]
    if pose != "cross":
        arm(*arms[0])

    # doudoune
    rrect(c, -64, -190, 128, 112, 30)
    fill_stroke(c, JACKET, 6)
    src(c, JACKET_D)
    c.set_line_width(5)
    for qy in (-160, -132, -104):
        c.move_to(-56, qy)
        c.curve_to(-20, qy + 6, 20, qy + 6, 56, qy)
        c.stroke()
    src(c, hexc("FFFFFF"), 0.9)
    c.set_line_width(4)
    c.move_to(0, -188)
    c.line_to(0, -82)
    c.stroke()
    if pose == "cross":
        arm(*arms[0])
    arm(*arms[1])

    # tête
    c.arc(0, -240, 62, 0, 6.283)
    fill_stroke(c, HEAD, 6)
    # casquette à l'envers
    c.new_path()
    c.arc(0, -252, 60, math.pi * 1.05, math.pi * 1.95)
    c.close_path()
    fill_stroke(c, CAP, 6)
    rrect(c, -98, -262, 52, 18, 8)
    fill_stroke(c, CAP_D, 5)
    src(c, hexc("FFFFFF"))
    c.arc(8, -296, 7, 0, 6.283)
    c.fill()

    # yeux
    blink = (t % 3.1) < 0.12
    lx, ly = look
    for ex in (-22, 22):
        if eyes == "happy" or blink:
            src(c, hexc("FFFFFF"))
            c.set_line_width(7)
            c.arc(ex, -228 if eyes == "happy" else -232, 12, math.pi * 1.1, math.pi * 1.9)
            c.stroke()
        else:
            ry = 10 if eyes == "sleepy" else 19
            c.save()
            c.translate(ex, -232)
            c.scale(1, ry / 14)
            c.arc(0, 0, 14, 0, 6.283)
            c.restore()
            src(c, hexc("FFFFFF"))
            c.fill()
            src(c, INK)
            c.arc(ex + lx * 5, -232 + ly * 5 + (3 if eyes == "sleepy" else 0), 6, 0, 6.283)
            c.fill()
            if eyes == "focus":
                src(c, HEAD)
                c.rectangle(ex - 16, -254, 32, 12)
                c.fill()
    if eyes == "happy":
        src(c, hexc("FF5C8A"))
        c.arc(0, -206, 10, 0, math.pi)
        c.fill()
    c.restore()

# ---------------------------------------------------------------- scènes (lt = temps local, p = progression 0..1)
def lamp(c, x, ground, warm):
    src(c, hexc("120A2E"))
    c.rectangle(x - 8, ground - 520, 16, 520)
    c.fill()
    rrect(c, x - 10, ground - 540, 90, 24, 10)
    c.fill()
    col = hexc("FFC94A") if warm else hexc("9AA7FF")
    g = cairo.LinearGradient(0, ground - 520, 0, ground)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], 0.35)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0.0)
    c.set_source(g)
    c.move_to(x + 45, ground - 516)
    c.line_to(x + 260, ground)
    c.line_to(x - 170, ground)
    c.close_path()
    c.fill()
    glow_circle(c, x + 45, ground - 516, 60, col, 0.8)

def rain(c, t, a):
    if a <= 0:
        return
    rnd = random.Random(11)
    src(c, hexc("9AB4FF"), 0.55 * a)
    c.set_line_width(3)
    for _ in range(140):
        x0, sp, ph = rnd.uniform(-200, W), rnd.uniform(1400, 2000), rnd.uniform(0, H)
        y = (ph + t * sp) % (H + 200) - 100
        x = x0 + y * 0.18
        c.move_to(x, y)
        c.line_to(x + 9, y + 50)
    c.stroke()

def sc_pluie(c, t, lt, p):
    sky(c, t, hexc("070616"), hexc("1E1C45"), stars=False)
    city(c, t, seed=4, lit=0.15)
    lamp(c, 230, 1700, warm=False)
    src(c, hexc("2A2E6E"), 0.6)
    c.save(); c.translate(560, 1712); c.scale(1, 0.18); c.arc(0, 0, 260, 0, 6.283); c.restore(); c.fill()
    mascot(c, 560, 1700, 1.75, t, "idle", "sleepy", look=(0, 1))
    rain(c, t, 1)

def sc_sourire(c, t, lt, p):
    sky(c, t, hexc("0A0820"), hexc("2C1660"))
    city(c, t, seed=4, lit=0.15 + 0.3 * p)
    lamp(c, 230, 1700, warm=True)
    mascot(c, 560, 1700, 1.75, t, "wave" if p > 0.35 else "idle", "happy")
    rain(c, t, 1 - p * 2.2)
    for i in range(6):
        a = (lt * 2 + i * 0.4) % 1.6
        ang = i * 1.05 + 0.3
        sparkle(c, 560 + math.cos(ang) * (250 + a * 60), 1240 + math.sin(ang) * 160, 22 * (1 - a / 1.6), KEY, 1 - a / 1.6)

def room(c, t):
    src(c, hexc("231848"))
    c.paint()
    rrect(c, 120, 520, 840, 620, 20)
    fill_stroke(c, hexc("0D0A2A"), 10, hexc("0A0620"))
    c.save()
    rrect(c, 130, 530, 820, 600, 16)
    c.clip()
    sky(c, t)
    city(c, t, seed=9, ground=1180, lit=0.4, hmin=200, hmax=520)
    c.restore()
    src(c, hexc("0A0620"))
    c.rectangle(530, 520, 20, 620); c.fill()
    c.rectangle(120, 820, 840, 16); c.fill()
    src(c, hexc("3A2464"))
    c.rectangle(0, 1450, W, H)
    c.fill()

def notebook(c, x, y, w, h, prog, t):
    c.save()
    c.translate(x, y)
    c.rotate(-0.05)
    rrect(c, -w / 2 + 10, -h / 2 + 12, w, h, 18)
    src(c, INK, 0.5); c.fill()
    rrect(c, -w / 2, -h / 2, w, h, 18)
    fill_stroke(c, hexc("FFF6E0"), 8)
    src(c, hexc("9EC9FF"), 0.7)
    c.set_line_width(3)
    for i in range(6):
        ly = -h / 2 + 70 + i * 60
        c.move_to(-w / 2 + 30, ly); c.line_to(w / 2 - 30, ly); c.stroke()
    src(c, hexc("FF5C8A"))
    c.move_to(-w / 2 + 70, -h / 2 + 20); c.line_to(-w / 2 + 70, h / 2 - 20); c.stroke()
    # écriture
    src(c, hexc("2A1F55"))
    c.set_line_width(7)
    total = 5 * (w - 160)
    rem = prog * total
    tip = None
    for i in range(5):
        if rem <= 0:
            break
        seg = min(rem, w - 160)
        ly = -h / 2 + 60 + i * 60
        x0 = -w / 2 + 90
        c.move_to(x0, ly)
        for k in range(int(seg / 6)):
            xx = x0 + k * 6
            c.line_to(xx, ly - 10 * abs(math.sin(k * 0.9 + i)) )
        c.stroke()
        tip = (x0 + seg, ly)
        rem -= seg
    c.restore()
    return tip

def pencil(c, x, y, ang):
    c.save(); c.translate(x, y); c.rotate(ang)
    rrect(c, 0, -14, 230, 28, 6); fill_stroke(c, hexc("FFD23F"), 6)
    c.move_to(0, -14); c.line_to(-40, 0); c.line_to(0, 14); c.close_path(); fill_stroke(c, hexc("F2C79B"), 6)
    src(c, INK); c.move_to(-28, -4); c.line_to(-40, 0); c.line_to(-28, 4); c.fill()
    rrect(c, 230, -14, 36, 28, 6); fill_stroke(c, hexc("FF5C8A"), 6)
    c.restore()

def sc_stylo(c, t, lt, p):
    room(c, t)
    mascot(c, 540, 1500, 1.35, t, "write", "focus", look=(0, 1))
    tip = notebook(c, 540, 1560, 720, 440, ease_io(p * 1.1), t)
    if tip:
        a = -0.05
        tx = 540 + tip[0] * math.cos(a) - tip[1] * math.sin(a)
        ty = 1560 + tip[0] * math.sin(a) + tip[1] * math.cos(a)
        pencil(c, tx, ty - 10 + 6 * math.sin(lt * 25), -0.6)

ICONS = ["star", "crown", "disc", "house", "star", "note", "crown", "disc"]

def icon(c, kind, x, y, r, t):
    c.save(); c.translate(x, y)
    if kind == "star":
        star_path(c, 0, 0, r, r * 0.45); fill_stroke(c, KEY, 6)
    elif kind == "crown":
        c.move_to(-r, r * 0.5); c.line_to(-r, -r * 0.4); c.line_to(-r * 0.5, 0); c.line_to(0, -r * 0.7)
        c.line_to(r * 0.5, 0); c.line_to(r, -r * 0.4); c.line_to(r, r * 0.5); c.close_path(); fill_stroke(c, KEY, 6)
    elif kind == "disc":
        c.arc(0, 0, r, 0, 6.283); fill_stroke(c, KEY, 6)
        c.arc(0, 0, r * 0.35, 0, 6.283); fill_stroke(c, hexc("FF5C8A"), 5)
        src(c, INK); c.arc(0, 0, r * 0.08, 0, 6.283); c.fill()
    elif kind == "house":
        c.move_to(-r, 0); c.line_to(0, -r); c.line_to(r, 0); c.line_to(r * 0.75, 0); c.line_to(r * 0.75, r * 0.8)
        c.line_to(-r * 0.75, r * 0.8); c.line_to(-r * 0.75, 0); c.close_path(); fill_stroke(c, CAP, 6)
        rrect(c, -r * 0.2, r * 0.25, r * 0.4, r * 0.55, 4); fill_stroke(c, KEY, 4)
    elif kind == "note":
        c.arc(-r * 0.35, r * 0.5, r * 0.3, 0, 6.283); fill_stroke(c, CAP, 6)
        rrect(c, -r * 0.1, -r * 0.8, r * 0.18, r * 1.3, 4); fill_stroke(c, CAP, 5)
        c.move_to(-r * 0.1, -r * 0.8); c.line_to(r * 0.6, -r * 0.5); c.line_to(r * 0.6, -r * 0.25); c.line_to(0, -r * 0.5); c.close_path(); fill_stroke(c, CAP, 5)
    c.restore()

def sc_reves(c, t, lt, p):
    room(c, t)
    mascot(c, 540, 1500, 1.35, t, "up" if p > 0.4 else "write", "happy")
    notebook(c, 540, 1560, 720, 440, 1, t)
    for i, kind in enumerate(ICONS):
        d = lt - i * 0.13
        if d <= 0:
            continue
        k = ease_out_back(d / 0.5)
        ang = -math.pi / 2 + (i - 3.5) * 0.36
        dist = 380 + 120 * (i % 2) + 40 * d
        x = 540 + math.cos(ang) * dist
        y = 1350 + math.sin(ang) * dist * 1.2 - 30 * math.sin(t * 3 + i)
        glow_circle(c, x, y, 110 * k, GLOW, 0.35)
        icon(c, kind, x, y, 62 * k, t)

def clock(c, x, y, r, t, speed):
    glow_circle(c, x, y, r * 1.6, CAP, 0.25)
    c.arc(x, y, r, 0, 6.283); fill_stroke(c, hexc("FF5C8A"), 10)
    c.arc(x, y, r * 0.84, 0, 6.283); fill_stroke(c, hexc("FFF6E0"), 6)
    src(c, INK); c.set_line_width(8)
    for i in range(12):
        a = i * math.pi / 6
        c.move_to(x + math.cos(a) * r * 0.7, y + math.sin(a) * r * 0.7)
        c.line_to(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78); c.stroke()
    for (len_, wdt, sp) in ((0.45, 14, speed / 12), (0.68, 9, speed)):
        a = -math.pi / 2 + t * sp
        c.set_line_width(wdt)
        c.move_to(x, y); c.line_to(x + math.cos(a) * r * len_, y + math.sin(a) * r * len_); c.stroke()
    c.arc(x, y, 14, 0, 6.283); fill_stroke(c, KEY, 5)

def sc_nuits(c, t, lt, p):
    sky(c, t)
    mx = lerp(150, 930, p)
    moon(c, mx, 820 - 220 * math.sin(p * math.pi), 90, t)
    city(c, t, seed=6, lit=0.5 - 0.35 * p)
    clock(c, 540, 1080, 230, lt, 9)
    mascot(c, 540, 1780, 1.5, t, "idle", "sleepy")

def flame(c, x, y, s, t):
    glow_circle(c, x, y - 60 * s, 380 * s, GLOW, 0.55)
    for (col, k) in ((hexc("FF5C2A"), 1.0), (hexc("FF9F1C"), 0.72), (hexc("FFE36E"), 0.42)):
        w = 70 * s * k
        h = 190 * s * k * (1 + 0.08 * math.sin(t * 22 + k * 5))
        sway = 14 * s * math.sin(t * 9 + k * 3)
        c.move_to(x, y)
        c.curve_to(x - w * 1.4, y - h * 0.3, x - w * 0.4 + sway, y - h * 0.7, x + sway, y - h)
        c.curve_to(x + w * 0.4 + sway, y - h * 0.7, x + w * 1.4, y - h * 0.3, x, y)
        c.close_path()
        src(c, col)
        c.fill()

def sc_flamme(c, t, lt, p):
    sky(c, t, hexc("050414"), hexc("140C34"), stars=True)
    city(c, t, seed=6, lit=0.12)
    fs = ease_out_back(min(1, max(0, (lt - 0.5) / 0.8)), 1.4) * (1 + 0.15 * p)
    # lumière ambiante
    if fs > 0:
        g = cairo.RadialGradient(720, 1180, 0, 720, 1180, 900)
        g.add_color_stop_rgba(0, 1, 0.55, 0.1, 0.35 * min(fs, 1))
        g.add_color_stop_rgba(1, 1, 0.55, 0.1, 0)
        c.set_source(g); c.paint()
    mascot(c, 520, 1720, 1.8, t, "hold", "open", look=(1, -0.6))
    if fs > 0:
        flame(c, 520 + 105 * 1.8, 1720 - 190 * 1.8, fs, t)

def stairs(c, cam_y, t):
    for i in range(16):
        x = 60 + i * 120
        y = 1820 - i * 150 + cam_y
        rrect(c, x - 600, y, 720, 60, 10)
        fill_stroke(c, hexc("3B2A7A"), 6)
        src(c, CAP, 0.8)
        c.rectangle(x - 590, y + 6, 700, 6); c.fill()

def stair_pos(k):
    i = int(k)
    f = k - i
    x = 60 + i * 120 + 60 + f * 120
    y = 1820 - i * 150 - math.sin(f * math.pi) * 40 - f * 150
    return x, y

def sc_marches(c, t, lt, p):
    sky(c, t)
    city(c, t, seed=2, lit=0.35, dy=300)
    stairs(c, 0, t)
    k = (lt / BEAT) * 1.0
    x, y = stair_pos(min(k, 4))
    mascot(c, x - 60, y, 1.2, t, "climb", "focus")

def sc_monte(c, t, lt, p):
    cam = ease_io(p) * 900 + 300
    sky(c, t, hexc("0B0826"), hexc("3A1A70"))
    city(c, t, seed=2, lit=0.5, dy=300 + cam * 0.4)
    # nuages
    for i in range(5):
        cx = (i * 260 + lt * 60) % (W + 400) - 200
        cy = 500 + i * 230 + cam * 0.7 - 400
        src(c, hexc("FFFFFF"), 0.12)
        for (dx, dy, r) in ((0, 0, 60), (60, -20, 70), (120, 0, 55)):
            c.arc(cx + dx, cy + dy, r, 0, 6.283); c.fill()
    stairs(c, cam, t)
    k = 4 + (lt / BEAT) * 1.6
    x, y = stair_pos(k)
    off_x = x - 640  # garde la mascotte cadrée
    c.save(); c.translate(-max(0, off_x), 0)
    mascot(c, x - 60, y + cam, 1.2, t, "climb", "focus")
    c.restore()

def bubble(c, x, y, txt, s, col):
    c.save(); c.translate(x, y); c.scale(s, s)
    w = text_w(c, txt, 70) + 70
    rrect(c, -w / 2, -60, w, 110, 40); fill_stroke(c, col, 7)
    c.move_to(-20, 48); c.line_to(-40, 95); c.line_to(10, 48); fill_stroke(c, col, 7)
    rrect(c, -w / 2 + 6, -54, w - 12, 30, 15); src(c, hexc("FFFFFF"), 0.25); c.fill()
    draw_text(c, txt, 0, 0, 70, INK, anchor="c")
    c.restore()

def sc_jamais(c, t, lt, p):
    sky(c, t, hexc("140820"), hexc("3A1240"))
    city(c, t, seed=7, lit=0.2)
    mascot(c, 540, 1760, 1.7, t, "cross", "focus")
    items = [(230, 1000, "NON"), (850, 920, "JAMAIS"), (190, 1350, "OUBLIE"), (880, 1300, "T'ES PERSONNE"), (540, 760, "IMPOSSIBLE")]
    for i, (x, y, txt) in enumerate(items):
        d = lt - 0.2 - i * 0.28
        if d <= 0:
            continue
        s = ease_out_back(d / 0.3) * 0.75
        shake = 6 * math.sin(t * 40 + i) if d < 0.25 else 0
        bubble(c, x + shake, y, txt, s, hexc("C9C3E6") if i % 2 else hexc("FF8FA3"))

def sc_foule(c, t, lt, p):
    sky(c, t)
    for i, base in enumerate((300, 780)):
        a = math.sin(t * 1.3 + i * 2) * 0.35
        c.save(); c.translate(base, 1900); c.rotate(a)
        g = cairo.LinearGradient(0, 0, 0, -1900)
        g.add_color_stop_rgba(0, 1, 0.85, 0.3, 0.35); g.add_color_stop_rgba(1, 1, 0.85, 0.3, 0)
        c.set_source(g); c.move_to(-40, 0); c.line_to(-260, -1900); c.line_to(260, -1900); c.line_to(40, 0); c.fill()
        c.restore()
    # immeuble central
    rrect(c, 300, 1050, 480, 900, 8); fill_stroke(c, hexc("22175A"), 8)
    for wy in range(1110, 1700, 90):
        for wx in range(340, 760, 80):
            src(c, WIN_ON[(wx + wy) % 3] if (wx * 7 + wy) % 5 else WIN_OFF)
            c.rectangle(wx, wy, 40, 54); c.fill()
    glow_circle(c, 540, 860, 320, KEY, 0.35)
    mascot(c, 540, 1050, 1.3, t, "wave" if p > 0.3 else "up", "happy")
    # foule + téléphones
    rnd = random.Random(5)
    for i in range(16):
        x = i * 72 + rnd.uniform(-10, 10)
        hb = 1780 + rnd.uniform(0, 60) + 10 * math.sin(t * 6 + i)
        src(c, hexc("0A0620"))
        c.arc(x, hb, 44, 0, 6.283); c.fill()
        c.rectangle(x - 55, hb + 30, 110, 200); c.fill()
        if (i * 3 + 1) % 2 == 0 and lt > 0.15 * (i % 6):
            px, py = x + 30, hb - 120 + 6 * math.sin(t * 5 + i)
            src(c, hexc("0A0620")); c.set_line_width(22); c.move_to(x + 25, hb); c.line_to(px, py + 40); c.stroke()
            glow_circle(c, px, py, 70, hexc("FFFFFF"), 0.35)
            rrect(c, px - 22, py - 36, 44, 76, 8); fill_stroke(c, hexc("E9F7FF"), 5)

def sc_allume(c, t, lt, p):
    sky(c, t)
    moon(c, 860, 520, 80, t)
    lit = ease_io(p * 1.15)
    order = lambda wx, wy, r: 0.75 * (1 - (wy - 600) / 1100) + 0.25 * r
    city(c, t, seed=8, lit=lit * 1.05, light_order=order, hmin=500, hmax=880)
    if lit > 0.05:
        g = cairo.LinearGradient(0, H, 0, 900)
        g.add_color_stop_rgba(0, 1, 0.7, 0.2, 0.3 * lit); g.add_color_stop_rgba(1, 1, 0.7, 0.2, 0)
        c.set_source(g); c.paint()
    tallest = max(city_layout(8, 1700, 500, 880), key=lambda b: b[2])
    mascot(c, tallest[0] + tallest[1] / 2, 1700 - tallest[2], 0.9, t, "up" if p > 0.5 else "idle", "happy")

def sc_lune(c, t, lt, p):
    sky(c, t, hexc("05041A"), hexc("241050"))
    # traînées d'étoiles
    rnd = random.Random(12)
    src(c, hexc("FFFFFF"), 0.6); c.set_line_width(3)
    for _ in range(50):
        x, ph, ln = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(40, 160)
        y = (ph + lt * 1600) % H
        c.move_to(x, y); c.line_to(x, y - ln * p * 2)
    c.stroke()
    moon(c, 540, lerp(700, 980, ease_io(p)), lerp(140, 300, ease_io(p)), t)
    city(c, t, seed=3, lit=0.9, dy=ease_io(p) * 900)
    y = lerp(1780, 1450, ease_io(p))
    # traînée de fusée
    for i in range(10):
        a = 1 - i / 10
        glow_circle(c, 540 + math.sin(t * 20 + i) * 8, y + 40 + i * 50, 70 * a, GLOW, 0.4 * a)
    flame(c, 540, y + 150, 0.9, t)
    mascot(c, 540, y, 1.3, t, "up", "happy")

def sc_outro(c, t, lt, p):
    sky(c, t, hexc("06051A"), hexc("150C3A"))
    k = ease_out_back(lt / 0.5)
    mascot(c, 540, 1150, 1.4 * max(k, 0.01), t, "wave", "happy")
    w = 760
    c.save(); c.translate(540, 1330); c.scale(max(k, 0.01), max(k, 0.01))
    rrect(c, -w / 2 - 6, -60, w + 12, 120, 60); src(c, CAP); c.fill()
    rrect(c, -w / 2, -54, w, 108, 54); src(c, hexc("0A0620")); c.fill()
    src(c, hexc("FFFFFF")); c.set_line_width(7)
    c.arc(-w / 2 + 70, -6, 20, 0, 6.283); c.stroke()
    c.move_to(-w / 2 + 84, 8); c.line_to(-w / 2 + 100, 24); c.stroke()
    n = int(min(len(HANDLE), max(0, (lt - 0.4) / 0.06)))
    draw_text(c, HANDLE[:n] + ("|" if int(lt * 4) % 2 else ""), 20, 4, 64, hexc("FFFFFF"), anchor="c")
    c.restore()
    if lt > 1.4:
        draw_text(c, "ABONNE-TOI", 540, 1520, 90, KEY, glow=GLOW, scale=ease_out_back((lt - 1.4) / 0.3), anchor="c")

SCENES = {
    "pluie": sc_pluie, "sourire": sc_sourire, "stylo": sc_stylo, "reves": sc_reves,
    "nuits": sc_nuits, "flamme": sc_flamme, "marches": sc_marches, "monte": sc_monte,
    "jamais": sc_jamais, "foule": sc_foule, "allume": sc_allume, "lune": sc_lune,
}

# ---------------------------------------------------------------- rendu
def frame(c, t):
    bar = int(t / BAR)
    lt = t - bar * BAR
    p = lt / BAR
    c.save()
    # « punch » de caméra sur chaque mesure + léger zoom continu
    z = 1 + 0.06 * math.exp(-lt / 0.12) + 0.025 * p
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    if bar < len(LINES):
        SCENES[LINES[bar][2]](c, t, lt, p)
    else:
        sc_outro(c, t, lt, p)
    c.restore()
    if bar < len(LINES):
        lyric_layer(c, bar, lt)
    # vignette
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0.05, 0.55)
    c.set_source(g); c.paint()
    # flash de transition
    if bar > 0 and lt < 0.1:
        src(c, hexc("FFFFFF"), 0.35 * (1 - lt / 0.1)); c.paint()

def main():
    wav, out = sys.argv[1], sys.argv[2]
    preview = "--preview" in sys.argv
    total = (len(LINES) + 1) * BAR
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    if preview:
        for i in range(len(LINES) + 1):
            frame(c, i * BAR + BAR * 0.7)
            surf.write_to_png(f"{out}_{i:02d}.png")
        return
    n = int(total * FPS)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out,
    ], stdin=subprocess.PIPE)
    for f in range(n):
        frame(c, f / FPS)
        surf.flush()
        ff.stdin.write(surf.get_data())
    ff.stdin.close()
    ff.wait()

if __name__ == "__main__":
    main()
