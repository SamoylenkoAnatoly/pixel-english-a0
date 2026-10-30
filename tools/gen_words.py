# -*- coding: utf-8 -*-
"""Генератор пиксельных карточек: слова (эмодзи→пиксель-арт), числа, буквы. Единая фэнтези-рамка."""
import os
import json
import glob
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT_WORDS = os.path.join(ROOT, "site", "assets", "words")
os.makedirs(OUT_WORDS, exist_ok=True)

CARD = 40            # размер карточки, логических пикселей
EMOJI_SIZE = 28      # размер эмодзи внутри
EMOJI_FONT = r"C:\Windows\Fonts\seguiemj.ttf"

_c = {}
def emoji_font(size):
    if size not in _c:
        _c[size] = ImageFont.truetype(EMOJI_FONT, size)
    return _c[size]

def render_emoji(ch, size=EMOJI_SIZE):
    img = Image.new("RGBA", (size + 8, size + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text(((size + 8) // 2, (size + 8) // 2), ch, font=emoji_font(size), embedded_color=True, anchor="mm")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    return img

def frame(content, card=CARD, ring=(212, 175, 55, 255), dark=(38, 28, 58, 255), deep=(18, 12, 30, 255)):
    """Помещает контент в фэнтези-рамку."""
    out = Image.new("RGBA", (card, card), deep)
    d = ImageDraw.Draw(out)
    # фон-пергамент чуть светлее
    d.rectangle([3, 3, card - 4, card - 4], fill=dark)
    # двойная рамка: золото + тёмный контур
    d.rectangle([0, 0, card - 1, card - 1], outline=deep)
    d.rectangle([1, 1, card - 2, card - 2], outline=ring)
    d.rectangle([4, 4, card - 5, card - 5], outline=(90, 70, 130, 255))
    # угловые самоцветы
    for cx, cy in ((2, 2), (card - 3, 2), (2, card - 3), (card - 3, card - 3)):
        d.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=(240, 230, 140, 255))
    # контент по центру с пиксельным масштабом (NEAREST уже на отрисовке размера)
    cw, ch = content.size
    scale = 1
    while (cw * (scale + 1) <= card - 10) and (ch * (scale + 1) <= card - 10):
        scale += 1
    content = content.resize((cw * scale, ch * scale), Image.NEAREST)
    out.alpha_composite(content, ((card - content.width) // 2, (card - content.height) // 2))
    return out

# пиксельный шрифт 3x5 для цифр и букв
DIGITS = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "001", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
}
LETTERS = {
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "G": ["011", "100", "101", "101", "011"],
    "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"],
    "J": ["001", "001", "001", "101", "010"],
    "K": ["101", "101", "110", "101", "101"],
    "L": ["100", "100", "100", "100", "111"],
    "M": ["101", "111", "111", "101", "101"],
    "N": ["101", "111", "111", "111", "101"],
    "O": ["010", "101", "101", "101", "010"],
    "P": ["110", "101", "110", "100", "100"],
    "Q": ["010", "101", "101", "110", "011"],
    "R": ["110", "101", "110", "101", "101"],
    "S": ["011", "100", "010", "001", "110"],
    "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"],
    "V": ["101", "101", "101", "010", "010"],
    "W": ["101", "101", "111", "111", "101"],
    "X": ["101", "101", "010", "101", "101"],
    "Y": ["101", "101", "010", "010", "010"],
    "Z": ["111", "001", "010", "100", "111"],
}

def draw_glyph(glyph, px, color):
    w = 3 * px
    h = 5 * px
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for ry, row in enumerate(glyph):
        for rx, bit in enumerate(row):
            if bit == "1":
                d.rectangle([rx * px, ry * px, rx * px + px - 1, ry * px + px - 1], fill=color)
    return img

def number_card(n):
    out = Image.new("RGBA", (CARD, CARD), (18, 12, 30, 255))
    d = ImageDraw.Draw(out)
    d.rectangle([1, 1, CARD - 2, CARD - 2], outline=(212, 175, 55, 255))
    d.rectangle([4, 4, CARD - 5, CARD - 5], outline=(90, 70, 130, 255))
    s = str(n)
    if len(s) == 1:
        g = draw_glyph(DIGITS[s], 4, (240, 200, 70, 255))
        out.alpha_composite(g, ((CARD - g.width) // 2, 5))
        # точки-счёт
        dot_col = (110, 200, 130, 255)
        rows = (n + 2) // 3
        size = 3 if rows <= 3 else 2
        gap = size + 1
        total_w = min(3, n) * gap - 1
        x0 = (CARD - total_w) // 2
        y0 = 24
        for i in range(n):
            r, cidx = divmod(i, 3)
            d.rectangle([x0 + cidx * gap, y0 + r * gap, x0 + cidx * gap + size - 1, y0 + r * gap + size - 1], fill=dot_col)
    else:
        g = draw_glyph(DIGITS[s[0]], 3, (240, 200, 70, 255))
        g2 = draw_glyph(DIGITS[s[1]], 3, (240, 200, 70, 255))
        total = g.width + g2.width + 2
        x = (CARD - total) // 2
        out.alpha_composite(g, (x, 12))
        out.alpha_composite(g2, (x + g.width + 2, 12))
        for i in range(3):
            d.rectangle([16 + i * 4, 28, 18 + i * 4, 30], fill=(110, 200, 130, 255))
    return out

def letter_card(ch):
    out = Image.new("RGBA", (CARD, CARD), (18, 12, 30, 255))
    d = ImageDraw.Draw(out)
    d.rectangle([1, 1, CARD - 2, CARD - 2], outline=(212, 175, 55, 255))
    d.rectangle([4, 4, CARD - 5, CARD - 5], outline=(90, 70, 130, 255))
    g = draw_glyph(LETTERS[ch], 5, (240, 200, 70, 255))
    out.alpha_composite(g, ((CARD - g.width) // 2, 7))
    # звёздочки-акценты
    for x, y in ((8, 30), (CARD - 9, 30)):
        d.rectangle([x - 1, y, x + 1, y], fill=(150, 200, 250, 255))
        d.rectangle([x, y - 1, x, y + 1], fill=(150, 200, 250, 255))
    return out

def color_card(hexcolor):
    """Карточка-самоцвет заданного цвета."""
    out = Image.new("RGBA", (CARD, CARD), (18, 12, 30, 255))
    d = ImageDraw.Draw(out)
    d.rectangle([1, 1, CARD - 2, CARD - 2], outline=(212, 175, 55, 255))
    d.rectangle([4, 4, CARD - 5, CARD - 5], outline=(90, 70, 130, 255))
    base = tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    dark = tuple(max(0, v - 60) for v in base[:3]) + (255,)
    light = tuple(min(255, v + 55) for v in base[:3]) + (255,)
    # пиксельный бриллиант: сужение к верху и низу
    top, bot = 8, 30
    mid = (top + bot) // 2
    for y in range(top, bot):
        if y <= mid:
            half = 1 + (y - top) * 10 // max(1, mid - top)
        else:
            half = 1 + (bot - 1 - y) * 10 // max(1, bot - 1 - mid)
        d.rectangle([20 - half, y, 20 + half, y], fill=base)
    for y in range(top, bot):
        if y <= mid:
            half = 1 + (y - top) * 10 // max(1, mid - top)
        else:
            half = 1 + (bot - 1 - y) * 10 // max(1, bot - 1 - mid)
        d.point([(20 - half, y), (20 + half, y)], fill=dark)
    d.line([(20 - 10, mid), (20, top), (20 + 10, mid), (20, bot - 1), (20 - 10, mid)], fill=dark)
    d.line([(11, mid - 1), (20, top + 1)], fill=light)
    d.rectangle([17, top + 5, 19, top + 7], fill=light)
    return out

def slug(s):
    s = s.lower().strip()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")

def load_lessons():
    lessons = []
    for f in sorted(glob.glob(os.path.join(DATA, "module*.json"))):
        mod = json.load(open(f, encoding="utf-8"))
        lessons.extend(mod["lessons"])
    return lessons

def draw_custom(kind):
    out = Image.new("RGBA", (CARD, CARD), (18, 12, 30, 255))
    d = ImageDraw.Draw(out)
    d.rectangle([1, 1, CARD - 2, CARD - 2], outline=(212, 175, 55, 255))
    d.rectangle([4, 4, CARD - 5, CARD - 5], outline=(90, 70, 130, 255))
    if kind == "window":
        # каменное окно с синим стеклом
        d.rectangle([11, 8, 28, 30], fill=(110, 80, 50, 255), outline=(60, 40, 25, 255))
        d.rectangle([14, 11, 25, 27], fill=(120, 190, 235, 255))
        d.rectangle([14, 11, 19, 27], fill=(150, 215, 250, 255))
        d.rectangle([19, 11, 20, 27], fill=(60, 40, 25, 255))
        d.rectangle([14, 18, 25, 19], fill=(60, 40, 25, 255))
        d.rectangle([15, 12, 17, 14], fill=(220, 245, 255, 255))
        d.rectangle([8, 31, 31, 33], fill=(90, 90, 105, 255), outline=(50, 50, 60, 255))
    elif kind == "table":
        # деревянный стол с кружкой
        d.rectangle([6, 18, 33, 22], fill=(150, 100, 55, 255), outline=(70, 45, 25, 255))
        d.rectangle([6, 18, 33, 19], fill=(180, 125, 70, 255))
        d.rectangle([9, 23, 12, 32], fill=(120, 78, 42, 255), outline=(70, 45, 25, 255))
        d.rectangle([27, 23, 30, 32], fill=(120, 78, 42, 255), outline=(70, 45, 25, 255))
        d.rectangle([15, 12, 21, 18], fill=(210, 215, 225, 255), outline=(90, 95, 105, 255))
        d.rectangle([21, 13, 23, 16], fill=(210, 215, 225, 255), outline=(90, 95, 105, 255))
        d.rectangle([16, 13, 18, 14], fill=(120, 80, 40, 255))
    return out

def detect_tofu(img):
    """Эмодзи не поддержан: рисуется полым прямоугольником."""
    rgb = img.convert("RGBA")
    w, h = rgb.size
    if w == 0 or h == 0:
        return True
    cx, cy = w // 2, h // 2
    center_empty = rgb.getpixel((cx, cy))[3] < 30 and rgb.getpixel((cx, h // 4))[3] < 30
    colors = rgb.convert("RGB").getcolors(16)
    few = colors is not None and len(colors) <= 3
    filled = sum(1 for x in range(0, w, 3) for y in range(0, h, 3)
                 if rgb.getpixel((x, y))[3] > 100) / (len(range(0, w, 3)) * len(range(0, h, 3)))
    return center_empty and few and filled < 0.55

def main():
    lessons = load_lessons()
    made = {}
    bad = []
    for l in lessons:
        for w in l.get("words", []):
            if "num" in w:
                name = f"num_{w['num']}.png"
                if name not in made:
                    frame(number_card(w["num"])).save(os.path.join(OUT_WORDS, name))
                    made[name] = 1
            elif "color" in w:
                name = f"{slug(w['en'])}.png"
                if name not in made:
                    frame(color_card(w["color"])).save(os.path.join(OUT_WORDS, name))
                    made[name] = 1
            elif "draw" in w:
                name = f"{slug(w['en'])}.png"
                if name not in made:
                    frame(draw_custom(w["draw"])).save(os.path.join(OUT_WORDS, name))
                    made[name] = 1
            elif "emoji" in w:
                name = f"{slug(w['en'])}.png"
                if name not in made:
                    e = render_emoji(w["emoji"])
                    if detect_tofu(e):
                        bad.append((w["en"], w["emoji"]))
                    frame(e).save(os.path.join(OUT_WORDS, name))
                    made[name] = 1
        for lt in l.get("letters", []):
            name = f"letter_{lt['letter']}.png"
            if name not in made:
                frame(letter_card(lt["letter"])).save(os.path.join(OUT_WORDS, name))
                made[name] = 1
    if bad:
        print("ПОДОЗРЕНИЕ НА НЕПОДДЕРЖАННЫЕ ЭМОДЗИ:")
        for en, em in bad:
            print("  ", en, em)
    print(f"карточек: {len(made)}")

    # превью-лист с именами файлов
    files = sorted(os.listdir(OUT_WORDS))
    cols = 14
    rows = (len(files) + cols - 1) // cols
    S = 60
    LBL = 12
    fnt = ImageFont.load_default(size=9)
    sheet = Image.new("RGBA", (cols * (S + 4) + 4, rows * (S + LBL + 4) + 4), (24, 18, 40, 255))
    dsheet = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        img = Image.open(os.path.join(OUT_WORDS, f)).resize((S, S), Image.NEAREST)
        r, c = divmod(i, cols)
        x, y = 4 + c * (S + 4), 4 + r * (S + LBL + 4)
        sheet.alpha_composite(img, (x, y))
        dsheet.text((x + 2, y + S + 1), f[:14], font=fnt, fill=(220, 220, 230, 255))
    sheet.save(os.path.join(ROOT, "..", "preview_words.png"))
    print("превью: preview_words.png")

if __name__ == "__main__":
    main()
