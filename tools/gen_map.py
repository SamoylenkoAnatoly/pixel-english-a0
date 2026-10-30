# -*- coding: utf-8 -*-
"""Хаб-карта волшебного городка Wordsburg: пиксельная фэнтези-карта 160x96."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "assets")
W, H = 160, 96

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

def vgrad(x0, x1, y0, y1, c0, c1):
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        c = tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(4))
        d.line([(x0, y), (x1, y)], fill=c)

def house(x, y, w, h, roof, wall, lit=2):
    # стена
    d.rectangle([x, y + h // 2, x + w - 1, y + h - 1], fill=wall, outline=(58, 38, 24, 255))
    # крыша (трапеция)
    rh = h // 2 + 1
    for i in range(rh):
        half = w // 2 + (w % 2)
        inset = int(i * (w // 2) / rh)
        d.line([(x - 2 + inset, y + rh - i), (x + w + 1 - inset, y + rh - i)], fill=roof)
    d.line([(x - 2, y + rh), (x + w + 1, y + rh)], fill=(58, 38, 24, 255))
    # дверь
    d.rectangle([x + w // 2 - 1, y + h - 4, x + w // 2, y + h - 1], fill=(80, 50, 28, 255))
    # окна
    if lit >= 1:
        d.rectangle([x + 2, y + h - 4, x + 3, y + h - 3], fill=(255, 214, 110, 255))
    if lit >= 2 and w >= 9:
        d.rectangle([x + w - 4, y + h - 4, x + w - 3, y + h - 3], fill=(255, 214, 110, 255))

def tree(x, y, s=1):
    for i, (wd, col) in enumerate(((7, (40, 92, 46, 255)), (5, (56, 118, 60, 255)))):
        yy = y - i * 3 * s - 3 * s
        d.polygon([(x - wd * s, yy + 3 * s), (x + wd * s, yy + 3 * s), (x, yy - 3 * s)], fill=col)
    d.rectangle([x - s, y, x + s, y + 2 * s], fill=(92, 62, 36, 255))

def tower(x, y, w, h, roof):
    d.rectangle([x, y, x + w - 1, y + h], fill=(196, 190, 178, 255), outline=(110, 104, 96, 255))
    d.rectangle([x + 1, y + h - 4, x + 2, y + h], fill=(90, 84, 78, 255))
    for i in range(6):
        inset = i
        d.line([(x - 2 + inset, y - 6 + i), (x + w + 1 - inset, y - 6 + i)], fill=roof)
    d.line([(x - 2, y), (x + w + 1, y)], fill=(110, 104, 96, 255))

def flag(x, y):
    d.line([(x, y), (x, y - 5)], fill=(70, 60, 50, 255))
    d.polygon([(x, y - 5), (x + 5, y - 3), (x, y - 2)], fill=(212, 60, 56, 255))

# ── небо ──
vgrad(0, W, 0, 46, (110, 170, 235, 255), (196, 228, 250, 255))
d.rectangle([132, 6, 137, 11], fill=(255, 236, 150, 255))
d.rectangle([134, 4, 135, 13], fill=(255, 236, 150, 255))
d.rectangle([130, 8, 139, 9], fill=(255, 236, 150, 255))
for cx, cy, cw in ((18, 10, 22), (58, 18, 16), (100, 8, 20), (142, 22, 14)):
    d.rectangle([cx, cy, cx + cw, cy + 3], fill=(252, 252, 254, 235))
    d.rectangle([cx + 4, cy - 2, cx + cw - 4, cy], fill=(252, 252, 254, 235))

# ── дальние холмы ──
d.rectangle([0, 38, 36, 46], fill=(104, 148, 110, 255))
d.rectangle([120, 36, W, 46], fill=(104, 148, 110, 255))
d.polygon([(0, 46), (18, 30), (40, 46)], fill=(88, 132, 96, 255))
d.polygon([(118, 46), (142, 28), (160, 46)], fill=(88, 132, 96, 255))

# ── земля ──
vgrad(0, W, 46, H, (120, 160, 96, 255), (92, 128, 74, 255))

# ── река ──
for y in range(0, H):
    t = y / (H - 1)
    cx = 128 + int(t * 14)
    wid = 6 + int(t * 4)
    d.line([(cx - wid, y), (cx + wid, y)], fill=(74, 130, 190, 255))
    d.line([(cx - wid, y), (cx - wid + 1, y)], fill=(120, 175, 225, 255))
# мост через реку
for i in range(14):
    d.line([(94 + i, 36 + i // 2), (94 + i, 44 + i // 2)], fill=(146, 100, 58, 255) if i % 2 else (120, 80, 46, 255))
d.line([(94, 35), (108, 42)], fill=(90, 60, 34, 255))
d.line([(94, 45), (108, 51)], fill=(90, 60, 34, 255))

# ── замок на холме ──
d.polygon([(40, 34), (76, 34), (72, 22), (44, 22)], fill=(150, 144, 130, 255))
tower(42, 8, 8, 16, (178, 52, 48, 255)); flag(46, 8)
tower(66, 8, 8, 16, (178, 52, 48, 255)); flag(70, 8)
d.rectangle([50, 12, 66, 24], fill=(206, 200, 186, 255), outline=(110, 104, 96, 255))
for i in range(5):
    d.rectangle([50 + i * 4, 10, 51 + i * 4, 12], fill=(206, 200, 186, 255))
tower(56, 2, 8, 12, (66, 88, 180, 255)); flag(60, 2)
d.rectangle([56, 20, 60, 24], fill=(70, 50, 30, 255))
d.rectangle([54, 15, 55, 16], fill=(255, 214, 110, 255)); d.rectangle([62, 15, 63, 16], fill=(255, 214, 110, 255))

# ── западная сторожевая башня (урок 3) ──
tower(14, 24, 10, 18, (90, 70, 140, 255))
d.rectangle([17, 30, 20, 33], fill=(255, 214, 110, 255))
flag(19, 24)

# ── библиотека (урок 2) ──
house(28, 42, 14, 12, (70, 110, 170, 255), (222, 208, 178, 255))
d.rectangle([33, 43, 37, 46], fill=(146, 100, 58, 255), outline=(90, 60, 34, 255))
d.rectangle([34, 44, 36, 45], fill=(230, 200, 130, 255))

# ── пекарня (урок 6) ──
house(52, 42, 13, 12, (200, 120, 60, 255), (238, 226, 196, 255))
d.rectangle([61, 38, 63, 42], fill=(120, 80, 46, 255))
d.rectangle([55, 47, 57, 49], fill=(255, 214, 110, 255))
d.rectangle([58, 36, 64, 38], fill=(235, 235, 240, 200))

# ── дом у реки (урок 7) ──
house(104, 60, 13, 12, (66, 130, 90, 255), (230, 216, 188, 255))
d.rectangle([108, 65, 110, 67], fill=(255, 214, 110, 255))

# ── дом с драконом (урок 8) ──
house(122, 48, 13, 12, (160, 60, 110, 255), (226, 208, 184, 255))
d.rectangle([126, 53, 128, 55], fill=(255, 214, 110, 255))
from PIL import ImageFont
_ef = ImageFont.truetype(r"C:\Windows\Fonts\seguiemj.ttf", 36)
_dr = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
_ded = ImageDraw.Draw(_dr)
_ded.text((24, 24), "🐉", font=_ef, embedded_color=True, anchor="mm")
_bb = _dr.getbbox()
if _bb:
    _dr = _dr.crop(_bb)
_sc = 16 / max(_dr.size)
_dr = _dr.resize((max(1, int(_dr.width * _sc)), max(1, int(_dr.height * _sc))), Image.NEAREST)
img.alpha_composite(_dr, (126 - _dr.width // 2 + 3, 42 - _dr.height // 2))

# ── рядовые домики ──
house(88, 52, 10, 10, (178, 52, 48, 255), (224, 210, 184, 255), 1)
house(70, 72, 11, 11, (140, 90, 170, 255), (226, 214, 190, 255))
house(92, 70, 12, 11, (66, 110, 170, 255), (228, 218, 196, 255))
house(112, 74, 11, 10, (200, 130, 60, 255), (224, 212, 188, 255), 1)
house(38, 62, 10, 10, (178, 52, 48, 255), (226, 214, 192, 255), 1)
house(120, 62, 9, 9, (140, 90, 170, 255), (230, 220, 198, 255))

# ── рыночные прилавки (урок 4) ──
def stall(x, y, c1, c2):
    for i in range(10):
        d.line([(x + i, y), (x + i, y + 2)], fill=c1 if (i // 2) % 2 == 0 else c2)
    d.rectangle([x, y + 3, x + 9, y + 8], fill=(146, 100, 58, 255), outline=(90, 60, 34, 255))
    d.rectangle([x + 1, y + 4, x + 3, y + 6], fill=(240, 180, 90, 255))
stall(60, 58, (212, 60, 56, 255), (245, 245, 245, 255))
stall(74, 60, (66, 110, 170, 255), (245, 245, 245, 255))

# ── таверна (урок 5) ──
house(80, 62, 14, 13, (150, 60, 140, 255), (224, 206, 178, 255))
d.rectangle([84, 68, 86, 70], fill=(255, 214, 110, 255))
d.rectangle([88, 68, 90, 70], fill=(255, 214, 110, 255))
d.rectangle([85, 64, 89, 66], fill=(212, 175, 55, 255), outline=(90, 60, 34, 255))

# ── колокольная башня (урок 11) ──
tower(82, 20, 10, 18, (212, 175, 55, 255))
d.rectangle([85, 24, 89, 28], fill=(255, 240, 180, 255), outline=(120, 90, 40, 255))
d.line([(87, 24), (87, 26)], fill=(120, 90, 40, 255))
d.line([(85, 26), (89, 26)], fill=(120, 90, 40, 255))

# ── лес и арена героев (урок 10) ──
for tx, ty in ((132, 22), (140, 14), (150, 20), (128, 34), (148, 44), (156, 34), (136, 50), (152, 54), (44, 74), (34, 78), (50, 80), (24, 82)):
    tree(tx, ty, 1)
# арена: каменный круг
d.ellipse((138, 26, 156, 40), fill=(150, 144, 130, 255), outline=(96, 90, 84, 255))
d.ellipse((142, 29, 152, 37), fill=(104, 150, 88, 255))
d.rectangle([140, 24, 141, 28], fill=(212, 60, 56, 255))
d.rectangle([153, 24, 154, 28], fill=(66, 110, 170, 255))

# ── городские ворота (урок 1) ──
d.rectangle([6, 52, 10, 78], fill=(168, 160, 148, 255), outline=(110, 104, 96, 255))
d.rectangle([24, 52, 28, 78], fill=(168, 160, 148, 255), outline=(110, 104, 96, 255))
d.rectangle([6, 48, 28, 52], fill=(196, 190, 178, 255), outline=(110, 104, 96, 255))
for i in range(4):
    d.rectangle([7 + i * 6, 46, 8 + i * 6, 48], fill=(196, 190, 178, 255))
d.rectangle([11, 58, 23, 78], fill=(96, 66, 38, 255), outline=(58, 38, 24, 255))
for i in range(3):
    d.line([(12 + i * 4, 59), (12 + i * 4, 77)], fill=(70, 46, 26, 255))
d.rectangle([16, 66, 17, 68], fill=(212, 175, 55, 255))
flag(8, 48); flag(26, 48)

# ── дороги ──
sand = (206, 178, 128, 255)
sand2 = (186, 158, 110, 255)
def road(pts, wdt=3):
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0)) * 2 + 1
        for s in range(steps + 1):
            x = int(x0 + (x1 - x0) * s / steps)
            y = int(y0 + (y1 - y0) * s / steps)
            d.rectangle([x - wdt // 2, y - wdt // 2, x + wdt // 2, y + wdt // 2], fill=sand if (x + y) % 7 else sand2)
road([(17, 78), (18, 84), (40, 84), (70, 84), (110, 82), (128, 72)])
road([(17, 78), (34, 60), (48, 50)])
road([(48, 50), (66, 60), (84, 68)])
road([(84, 68), (104, 66), (112, 64)])
road([(84, 68), (100, 52), (100, 44)])
road([(100, 44), (116, 34), (132, 30), (146, 32)])
road([(48, 50), (58, 40), (64, 30), (62, 22)])
road([(87, 38), (86, 30), (84, 26)])

# ── персонажи на карте ──
def paste_char(name, cx, cy, s=22):
    ch = Image.open(os.path.join(ROOT, "site", "assets", "chars", name)).convert("RGBA")
    ch = ch.resize((s, s), Image.NEAREST)
    img.alpha_composite(ch, (cx - s // 2, cy - s // 2))
paste_char("bulldog_idle.png", 17, 80)
paste_char("cat_idle.png", 66, 80)
paste_char("whale_idle.png", 108, 16, 26)   # кит летит по небу — это же волшебный городок

# ── рамка ──
dark = (16, 12, 28, 255)
gold = (212, 175, 55, 255)
d.rectangle([0, 0, W - 1, H - 1], outline=dark)
d.rectangle([1, 1, W - 2, H - 2], outline=gold)
d.rectangle([2, 2, W - 3, H - 3], outline=dark)

img.save(os.path.join(OUT, "map.png"))
big = img.resize((W * 6, H * 6), Image.NEAREST)
big.save(os.path.join(ROOT, "..", "preview_map.png"))
print("map ok")
