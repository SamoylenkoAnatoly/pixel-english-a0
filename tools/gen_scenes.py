# -*- coding: utf-8 -*-
"""Генератор пиксельных сцен для историй кита: фон-палитра + эмодзи-спрайты + рамка."""
import os
import json
import glob
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "site", "assets", "scenes")
os.makedirs(OUT, exist_ok=True)
EMOJI_FONT = r"C:\Windows\Fonts\seguiemj.ttf"

W, H = 128, 72
_c = {}
def emoji_font(size):
    if size not in _c:
        _c[size] = ImageFont.truetype(EMOJI_FONT, size)
    return _c[size]

def vgrad(d, x0, x1, y0, y1, c0, c1):
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        c = tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(4))
        d.line([(x0, y), (x1, y)], fill=c)

BGS = {
    "dawn":   {"sky": ((70, 60, 110, 255), (250, 170, 110, 255)), "ground": (86, 62, 52, 255), "ground2": (64, 46, 40, 255), "stars": 8},
    "day":    {"sky": ((110, 170, 235, 255), (190, 225, 250, 255)), "ground": (98, 140, 80, 255), "ground2": (76, 112, 62, 255), "stars": 0},
    "sunset": {"sky": ((90, 70, 130, 255), (240, 140, 90, 255)), "ground": (80, 58, 52, 255), "ground2": (58, 42, 40, 255), "stars": 5},
    "night":  {"sky": ((14, 16, 40, 255), (40, 40, 80, 255)), "ground": (34, 30, 52, 255), "ground2": (24, 22, 40, 255), "stars": 26},
    "market": {"sky": ((120, 160, 220, 255), (250, 210, 150, 255)), "ground": (150, 120, 85, 255), "ground2": (120, 95, 68, 255), "stars": 0},
    "castle": {"sky": ((40, 45, 90, 255), (120, 110, 170, 255)), "ground": (70, 66, 90, 255), "ground2": (50, 48, 70, 255), "stars": 16},
    "forest": {"sky": ((90, 140, 190, 255), (160, 210, 230, 255)), "ground": (60, 110, 60, 255), "ground2": (44, 84, 46, 255), "stars": 0},
    "sea":    {"sky": ((100, 150, 210, 255), (180, 220, 240, 255)), "ground": (50, 100, 170, 255), "ground2": (36, 76, 140, 255), "stars": 0},
}

def emoji_sprite(ch, logical=22):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((24, 24), ch, font=emoji_font(36), embedded_color=True, anchor="mm")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    s = logical / max(img.size)
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.NEAREST)

def make_scene(emojis, bg):
    p = BGS[bg]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    vgrad(d, 0, W, 0, 52, *p["sky"])
    # земля
    vgrad(d, 0, W, 52, H, p["ground"], p["ground2"])
    d.line([(0, 52), (W, 52)], fill=tuple(max(0, c - 30) for c in p["ground"]))
    # звёзды
    import random
    rnd = random.Random(bg + str(len(emojis)))
    for i in range(p["stars"]):
        x, y = rnd.randrange(4, W - 4), rnd.randrange(3, 44)
        c = (240, 235, 180, 255) if i % 3 else (180, 200, 250, 255)
        d.rectangle([x, y, x + 1, y], fill=c)
        if i % 3 == 0:
            d.rectangle([x - 1, y, x + 2, y], fill=c)
            d.rectangle([x, y - 1, x, y + 2], fill=c)
    # облака днём
    if p["stars"] < 8 and bg != "night":
        for cx in (24, 84):
            d.rectangle([cx, 12, cx + 20, 16], fill=(250, 250, 252, 230))
            d.rectangle([cx + 4, 9, cx + 14, 12], fill=(250, 250, 252, 230))
    # холмы
    d.rectangle([0, 44, 30, 52], fill=p["ground2"])
    d.rectangle([96, 42, W, 52], fill=p["ground2"])
    # спрайты
    pos = [(64, 34), (30, 38), (98, 30), (14, 40), (112, 42), (46, 44), (82, 46)]
    for i, ch in enumerate(emojis[:7]):
        sp = emoji_sprite(ch)
        px, py = pos[i % len(pos)]
        img.alpha_composite(sp, (px - sp.width // 2, py - sp.height // 2 + 6))
    # виньетка-рамка
    dark = (16, 12, 28, 255)
    gold = (212, 175, 55, 255)
    d.rectangle([0, 0, W - 1, H - 1], outline=dark)
    d.rectangle([1, 1, W - 2, H - 2], outline=gold)
    d.rectangle([2, 2, W - 3, H - 3], outline=dark)
    return img

def load_lessons():
    lessons = []
    for f in sorted(glob.glob(os.path.join(DATA, "module*.json"))):
        mod = json.load(open(f, encoding="utf-8"))
        lessons.extend(mod["lessons"])
    return lessons

def main():
    made = 0
    for l in load_lessons():
        for i, part in enumerate(l["story"]["parts"]):
            sc = part["scene"]
            img = make_scene(sc["emoji"], sc.get("bg", "day"))
            img.save(os.path.join(OUT, f"s{l['n']}_{i}.png"))
            made += 1
    print(f"сцен: {made}")
    # превью
    files = sorted(os.listdir(OUT))
    cols = 6
    rows = (len(files) + cols - 1) // cols
    sw, sh = 256, 144
    sheet = Image.new("RGBA", (cols * (sw + 4) + 4, rows * (sh + 4) + 4), (24, 18, 40, 255))
    for i, f in enumerate(files):
        img = Image.open(os.path.join(OUT, f)).resize((sw, sh), Image.NEAREST)
        r, c = divmod(i, cols)
        sheet.alpha_composite(img, (4 + c * (sw + 4), 4 + r * (sh + 4)))
    sheet.save(os.path.join(ROOT, "..", "preview_scenes.png"))
    print("превью: preview_scenes.png")

if __name__ == "__main__":
    main()
