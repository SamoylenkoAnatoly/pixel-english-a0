# -*- coding: utf-8 -*-
"""Генератор пиксельных персонажей: сэр Бруно (бульдог), мистер Уискерс (кот), кит Океанус."""
import os
from PIL import Image

W = H = 48
OUT = os.path.join(os.path.dirname(__file__), "..", "site", "assets", "chars")
os.makedirs(OUT, exist_ok=True)


class Grid:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.d = [[None] * w for _ in range(h)]

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.d[y][x] = c

    def get(self, x, y):
        return self.d[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def rect(self, x0, y0, x1, y1, fill, border=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                on_edge = x in (x0, x1) or y in (y0, y1)
                self.px(x, y, border if (border and on_edge) else fill)

    def ellipse(self, cx, cy, rx, ry, fill, border=None):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                dx, dy = (x - cx) / rx, (y - cy) / ry
                d = dx * dx + dy * dy
                if fill and d <= 1.0:
                    self.px(x, y, fill)
                elif border and d <= 1.0 + 1.6 / min(rx, ry):
                    self.px(x, y, border)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy; x0 += sx
            if e2 < dx:
                err += dx; y0 += sy

    def tri(self, p0, p1, p2, fill, border=None):
        minx = max(0, int(min(p0[0], p1[0], p2[0])))
        maxx = min(self.w - 1, int(max(p0[0], p1[0], p2[0])))
        miny = max(0, int(min(p0[1], p1[1], p2[1])))
        maxy = min(self.h - 1, int(max(p0[1], p1[1], p2[1])))
        def sign(a, b, c):
            return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                p = (x, y)
                d1, d2, d3 = sign(p, p0, p1), sign(p, p1, p2), sign(p, p2, p0)
                neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
                pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
                if not (neg and pos):
                    self.px(x, y, fill)
        for a, b in ((p0, p1), (p1, p2), (p2, p0)):
            self.line(a[0], a[1], b[0], b[1], border or fill)

    def ellipse_border(self, cx, cy, rx, ry, c):
        import math
        steps = max(32, int(6 * (rx + ry)))
        pts = set()
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            pts.add((int(round(cx + rx * math.cos(a))), int(round(cy + ry * math.sin(a)))))
        for x, y in pts:
            self.px(x, y, c)

    def mirror_x(self, axis=None):
        """Копирует левую половину на правую (ось симметрии)."""
        if axis is None:
            axis = self.w // 2 - 0.5
        for y in range(self.h):
            for x in range(self.w):
                if x < axis:
                    mx = int(2 * axis - x)
                    if 0 <= mx < self.w:
                        self.d[y][mx] = self.d[y][x]

    def outline(self, c):
        """Обводит прозрачные пиксели, соседние с цветными (изнутри фигуры)."""
        edge = []
        for y in range(self.h):
            for x in range(self.w):
                if self.d[y][x] is None:
                    continue
                for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if not (0 <= nx < self.w and 0 <= ny < self.h) or self.d[ny][nx] is None:
                        edge.append((x, y))
                        break
        for x, y in edge:
            self.d[y][x] = c

    def save(self, palette, name, scale=1):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for y in range(self.h):
            for x in range(self.w):
                c = self.d[y][x]
                if c:
                    img.putpixel((x, y), palette[c])
        if scale > 1:
            img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        img.save(os.path.join(OUT, name))
        print("saved", name)


# Палитры
PAL_DOG = {
    "O": (43, 22, 8, 255),      # контур
    "B": (186, 131, 79, 255),   # шерсть
    "D": (140, 89, 48, 255),    # шерсть тень
    "L": (222, 178, 130, 255),  # морда светлая
    "M": (240, 208, 168, 255),  # светлее
    "W": (205, 210, 220, 255),  # сталь
    "G": (150, 158, 172, 255),  # сталь тень
    "K": (90, 97, 110, 255),    # сталь тёмная
    "H": (240, 244, 250, 255),  # сталь блик
    "R": (196, 60, 56, 255),    # плюмаж
    "r": (140, 36, 36, 255),    # плюмаж тень
    "Y": (230, 180, 60, 255),   # золото
    "E": (250, 250, 245, 255),  # белок
    "P": (28, 22, 18, 255),     # зрачок
    "N": (30, 20, 16, 255),     # нос
    "T": (216, 120, 132, 255),  # язык
    "Q": (90, 50, 30, 255),     # рот открытый
}

PAL_CAT = {
    "O": (60, 30, 10, 255),
    "C": (226, 148, 62, 255),   # рыжий
    "S": (186, 110, 40, 255),   # полосы
    "s": (255, 190, 120, 255),  # светлый
    "W": (252, 248, 240, 255),  # белая грудка
    "P": (110, 74, 168, 255),   # плащ
    "p": (84, 55, 132, 255),    # плащ тень
    "l": (196, 168, 240, 255),  # плащ свет
    "Y": (240, 200, 70, 255),   # золото
    "E": (247, 249, 245, 255),
    "G": (96, 190, 90, 255),    # зелёные глаза
    "K": (30, 25, 20, 255),     # зрачок/контур
    "N": (232, 130, 140, 255),  # носик розовый
    "M": (150, 70, 70, 255),    # рот
    "B": (120, 62, 30, 255),    # лютня
    "b": (160, 96, 48, 255),    # лютня свет
    "n": (90, 50, 26, 255),     # гриф
    "R": (196, 60, 56, 255),    # шапка красная
    "F": (255, 216, 120, 255),  # пёрышко
}

PAL_WHALE = {
    "O": (14, 26, 52, 255),
    "U": (74, 124, 200, 255),   # спина
    "u": (52, 92, 160, 255),    # спина тень
    "V": (188, 216, 245, 255),  # брюхо
    "v": (150, 186, 224, 255),  # брюхо тень
    "P": (110, 74, 168, 255),   # колпак
    "p": (84, 55, 132, 255),    # колпак тень
    "l": (196, 168, 240, 255),  # колпак свет
    "Y": (240, 200, 70, 255),   # звёзды золото
    "W": (252, 252, 250, 255),  # блик/очки
    "K": (30, 34, 44, 255),     # контур/зрачок
    "E": (250, 250, 245, 255),
    "M": (40, 40, 55, 255),     # рот
    "T": (216, 120, 132, 255),  # язык
    "A": (140, 200, 240, 255),  # фонтан/пузыри
    "a": (100, 160, 220, 255),
    "S": (255, 230, 120, 255),  # звёздочки
}


# ─────────────────────────── БУЛЬДОГ ───────────────────────────
def bulldog_base():
    g = Grid()
    # тело и лапы (симметрично)
    g.ellipse(24, 38, 13, 9, "B", "O")
    g.rect(14, 40, 20, 45, "B", "O"); g.rect(16, 45, 21, 46, "L", "O")   # левая лапа+стопа
    # нагрудник
    g.rect(18, 34, 30, 41, "W", "K")
    g.px(19, 35, "H"); g.px(29, 35, "G"); g.px(24, 37, "Y"); g.px(24, 39, "Y")
    # голова
    g.ellipse(24, 23, 16, 12, "B", "O")
    # уши висячие
    for sx, ex in ((7, 15), (33, 41)):
        g.tri((sx, 16), (ex, 16), (sx + 3 if sx < 24 else ex - 3, 27), "D", "O")
    # морда светлая
    g.ellipse(24, 27, 12, 7, "L", None)
    # складки на лбу
    g.line(15, 17, 21, 16, "D"); g.line(27, 16, 33, 17, "D")
    g.line(16, 19, 32, 19, "D")
    # брови суровые
    g.line(14, 22, 21, 21, "D"); g.line(27, 21, 34, 22, "D")
    # глаза (левый, потом зеркалим)
    g.rect(15, 23, 20, 26, "E", "O")
    g.rect(17, 24, 18, 25, "P")
    # нос
    g.rect(20, 25, 28, 28, "N", "O"); g.px(21, 26, "M")
    # рот: линия + клыки снизу (недокус)
    g.line(17, 31, 31, 31, "O")
    g.rect(19, 30, 21, 32, "W", "O"); g.rect(27, 30, 29, 32, "W", "O")
    # зеркало по оси 24 (глаза/брови/складки уже симметричны, но уши тоже)
    g.mirror_x(axis=23.5)
    # шлем: купол
    g.ellipse(24, 13, 15, 8, "W", "K")
    g.rect(9, 12, 39, 15, "W", "K")            # поля шлема
    g.line(10, 13, 38, 13, "H")
    g.line(12, 9, 36, 9, "G"); g.px(24, 7, "H")
    # плюмаж (толще)
    g.line(23, 8, 23, 2, "R"); g.line(24, 8, 24, 1, "R"); g.line(25, 8, 25, 3, "r")
    g.px(23, 1, "R"); g.px(22, 5, "r"); g.px(26, 6, "r"); g.px(24, 0, "R")
    # золотые заклёпки на полях
    g.px(11, 14, "Y"); g.px(37, 14, "Y")
    # носовая пластина шлема короткая
    g.rect(22, 15, 26, 17, "G", "K")
    # воротник
    g.rect(15, 33, 33, 34, "K", None)
    return g


def bulldog_talk(g):
    g2 = Grid()
    g2.d = [row[:] for row in g.d]
    # открытая пасть
    g2.rect(18, 30, 30, 34, "Q", "O")
    g2.rect(20, 33, 28, 34, "T")
    g2.px(19, 31, "W"); g2.px(29, 31, "W")
    return g2


# ─────────────────────────── КОТ ───────────────────────────
def cat_base():
    g = Grid()
    # хвост (слева, несимметричен — рисуем после зеркала)
    # голова
    g.ellipse(24, 21, 13, 11, "C", "O")
    # уши (левое)
    g.tri((13, 14), (21, 10), (12, 4), "C", "O")
    g.tri((14, 12), (18, 10), (13, 7), "N", None)
    # полосы на голове
    g.line(18, 11, 20, 13, "S"); g.line(24, 10, 24, 12, "S"); g.line(28, 11, 30, 13, "S")
    # белая мордочка
    g.ellipse(24, 25, 8, 5, "s", None)
    # глаза (левый зелёный)
    g.rect(15, 19, 20, 24, "E", "O")
    g.rect(17, 20, 18, 23, "G")
    g.rect(17, 21, 18, 22, "K")
    g.px(16, 20, "W"); g.px(19, 23, "K")
    # носик и ротик
    g.tri((22, 26), (26, 26), (24, 28), "N", "O")
    g.line(24, 28, 24, 29, "O"); g.px(22, 30, "O"); g.px(26, 30, "O")
    g.line(22, 29, 24, 30, "O"); g.line(24, 30, 26, 29, "O")
    # усы
    g.line(6, 24, 14, 26, "W"); g.line(6, 28, 14, 28, "W"); g.px(7, 32, "W"); g.line(7, 32, 14, 30, "W")
    g.mirror_x(axis=23.5)
    # плащ-туловище
    g.tri((14, 32), (34, 32), (36, 47), "P", "O")
    g.tri((14, 32), (34, 32), (12, 47), "p", None)
    g.line(15, 34, 33, 34, "l")
    g.px(24, 36, "Y"); g.px(24, 39, "Y"); g.px(24, 42, "Y")  # застёжки-звёзды
    # белая грудка
    g.ellipse(24, 35, 5, 4, "W", "O")
    g.px(22, 34, "Y"); g.px(26, 34, "Y")
    # хвост слева
    g.line(14, 42, 8, 42, "C"); g.line(14, 43, 8, 43, "S")
    g.line(8, 42, 5, 38, "C"); g.line(8, 43, 5, 39, "S")
    g.line(5, 38, 6, 34, "C"); g.px(6, 34, "S"); g.px(5, 33, "s")
    # красная шапочка барда с пером
    g.ellipse(24, 11, 12, 5, "R", "O")
    g.rect(13, 9, 35, 11, "R", "O"); g.line(14, 10, 34, 10, "F")
    g.line(30, 8, 36, 2, "F"); g.px(35, 3, "F"); g.px(36, 1, "F")
    # лютня (в правой части)
    g.line(38, 26, 44, 20, "n")             # гриф
    g.ellipse(39, 34, 5, 6, "b", "O")       # корпус
    g.ellipse(39, 34, 2, 3, "B", None)      # розетка
    g.line(38, 29, 38, 38, "W"); g.line(40, 29, 40, 38, "W")  # струны
    # лапка на лютне
    g.rect(33, 30, 38, 33, "C", "O")
    g.px(34, 31, "s")
    return g


def cat_talk(g):
    g2 = Grid()
    g2.d = [row[:] for row in g.d]
    g2.rect(21, 28, 27, 32, "M", "O")
    g2.px(23, 31, "N"); g2.px(25, 31, "N")
    return g2


# ─────────────────────────── КИТ ───────────────────────────
def whale_base():
    g = Grid()
    # тело (морда слева)
    g.ellipse(24, 28, 17, 12, "U", "O")
    # брюхо
    g.ellipse(23, 33, 14, 7, "V", None)
    g.line(10, 31, 36, 31, "v")
    for x in range(12, 36, 4):
        g.px(x, 38, "v"); g.px(x + 1, 38, "v")
    # хвост (справа): стебель и два плавника-лопасти
    g.rect(36, 25, 40, 30, "U", "O")
    g.tri((39, 25), (46, 16), (47, 23), "u", "O")
    g.tri((39, 30), (46, 39), (47, 32), "u", "O")
    # левый плавничок
    g.ellipse(11, 36, 5, 3, "v", "O")
    # большой глаз
    g.rect(10, 22, 16, 27, "E", "O")
    g.rect(12, 23, 14, 26, "K")
    g.px(11, 23, "W")
    # тонкое кольцо-монокль вокруг глаза
    g.ellipse_border(13.5, 24.5, 5, 4, "K")
    g.line(19, 22, 23, 20, "K")             # дужка очков
    # рот-улыбка крупный
    g.line(7, 30, 8, 31, "O"); g.line(8, 31, 12, 33, "O")
    g.line(12, 33, 18, 35, "O"); g.line(18, 35, 21, 35, "O"); g.px(21, 34, "O")
    # волшебный колпак (спереди-сверху)
    g.rect(12, 12, 34, 15, "P", "O")
    g.line(13, 13, 33, 13, "l")
    g.tri((14, 12), (32, 12), (23, 1), "P", "O")
    g.px(23, 2, "Y"); g.px(21, 5, "Y"); g.px(25, 8, "l"); g.px(23, 11, "Y")
    g.ellipse(23, 1, 2, 1, "Y", "O")
    # звёздная пыль вокруг
    g.px(6, 14, "S"); g.px(10, 9, "S"); g.px(38, 9, "S"); g.px(44, 13, "S")
    g.px(42, 42, "S"); g.px(6, 42, "A"); g.px(44, 20, "A")
    return g


def whale_talk(g):
    g2 = Grid()
    g2.d = [row[:] for row in g.d]
    g2.rect(9, 32, 21, 36, "M", "O")
    g2.rect(11, 35, 18, 36, "T")
    return g2


if __name__ == "__main__":
    bd = bulldog_base(); bd.outline("O")
    bd.save(PAL_DOG, "bulldog_idle.png")
    bulldog_talk(bd).save(PAL_DOG, "bulldog_talk.png")
    ct = cat_base(); ct.outline("O")
    ct.save(PAL_CAT, "cat_idle.png")
    cat_talk(ct).save(PAL_CAT, "cat_talk.png")
    wh = whale_base(); wh.outline("O")
    wh.save(PAL_WHALE, "whale_idle.png")
    whale_talk(wh).save(PAL_WHALE, "whale_talk.png")
    print("OK")
