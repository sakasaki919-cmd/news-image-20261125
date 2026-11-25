#!/usr/bin/env python3
"""news-image-20261125: draw a newspaper front page summing up the world news
of Wednesday 25 November 2026. Pure PIL, no network, no randomness:
two runs write byte-identical PNG bytes. Usage: python3 main.py [out.png]"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 683
PAPER = (246, 241, 229)
INK = (22, 22, 22)
RULE = (22, 22, 22)
ACCENT = (158, 27, 27)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def vgrad(draw, box, top, bottom, steps=48):
    x0, y0, x1, y1 = box
    for i in range(steps):
        t = i / (steps - 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        ya = y0 + (y1 - y0) * i // steps
        yb = y0 + (y1 - y0) * (i + 1) // steps
        draw.rectangle([x0, ya, x1, yb], fill=col)


def burst(draw, cx, cy, r, colour):
    pts = []
    for i in range(16):
        ang = 3.14159265 * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * __import__("math").cos(ang),
                    cy + rr * __import__("math").sin(ang)))
    draw.polygon(pts, fill=colour)


def hero_sea(draw, box):
    """Cargo ship Sparta II burning in the Gulf of Finland; drone overhead."""
    x0, y0, x1, y1 = box
    vgrad(draw, (x0, y0, x1, y0 + 118), (168, 196, 214), (214, 224, 228))
    draw.rectangle([x0, y0 + 118, x1, y1], fill=(28, 68, 104))
    for k in range(5):  # wave lines
        yy = y0 + 128 + k * 13
        for xx in range(x0, x1, 46):
            draw.arc([xx, yy, xx + 44, yy + 10], 200, 340, fill=(120, 170, 205))
    # distant shoreline
    draw.polygon([(x0, y0 + 112), (x0 + 300, y0 + 96), (x0 + 620, y0 + 108),
                  (x1, y0 + 100), (x1, y0 + 118), (x0, y0 + 118)], fill=(96, 116, 110))
    # hull
    draw.polygon([(x0 + 300, y0 + 132), (x0 + 700, y0 + 132),
                  (x0 + 672, y0 + 168), (x0 + 330, y0 + 168)], fill=(30, 30, 34))
    draw.rectangle([x0 + 300, y0 + 126, x0 + 700, y0 + 134], fill=(158, 27, 27))
    # containers
    cols = [(196, 84, 32), (38, 110, 140), (196, 160, 32), (120, 120, 120)]
    for r in range(2):
        for c in range(8):
            cx = x0 + 330 + c * 42
            cy = y0 + 100 - r * 16
            draw.rectangle([cx, cy, cx + 38, cy + 14], fill=cols[(r + c) % 4],
                           outline=(20, 20, 20))
    # bridge tower
    draw.rectangle([x0 + 668, y0 + 84, x0 + 692, y0 + 126], fill=(230, 230, 220))
    draw.rectangle([x0 + 672, y0 + 92, x0 + 688, y0 + 100], fill=(40, 90, 130))
    # smoke + fire at the bow
    for (sx, sy, sr, scol) in [(352, 96, 26, (90, 90, 90)), (372, 78, 32, (110, 110, 110)),
                               (398, 58, 38, (130, 130, 130)), (420, 40, 30, (150, 150, 150))]:
        draw.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr], fill=scol)
    burst(draw, x0 + 330, y0 + 118, 34, (240, 140, 20))
    burst(draw, x0 + 330, y0 + 118, 20, (250, 210, 60))
    # drone top right
    dx, dy = x0 + 880, y0 + 34
    draw.ellipse([dx - 22, dy - 5, dx - 10, dy + 5], outline=(30, 30, 30), width=2)
    draw.ellipse([dx + 10, dy - 5, dx + 22, dy + 5], outline=(30, 30, 30), width=2)
    draw.rectangle([dx - 12, dy - 3, dx + 12, dy + 3], fill=(30, 30, 30))
    draw.line([dx, dy + 3, dx, dy + 12], fill=(30, 30, 30), width=2)
    draw.ellipse([dx - 4, dy + 12, dx + 4, dy + 20], fill=(158, 27, 27))


def tower_panel(draw, box):
    """Riyadh's tallest tower, smoke rising beside it."""
    x0, y0, x1, y1 = box
    vgrad(draw, box, (238, 200, 150), (214, 150, 110))
    draw.ellipse([x0 + 100, y0 + 8, x0 + 128, y0 + 36], fill=(250, 220, 140))
    # tower: two slabs with an inverted arch opening
    draw.polygon([(x0 + 52, y1), (x0 + 52, y0 + 34), (x0 + 74, y0 + 18),
                  (x0 + 96, y0 + 34), (x0 + 96, y1)], fill=(52, 52, 58))
    draw.polygon([(x0 + 96, y1), (x0 + 96, y0 + 34), (x0 + 118, y0 + 18),
                  (x0 + 140, y0 + 34), (x0 + 140, y1)], fill=(40, 40, 46))
    draw.polygon([(x0 + 74, y0 + 34), (x0 + 96, y0 + 60), (x0 + 118, y0 + 34),
                  (x0 + 118, y0 + 18), (x0 + 74, y0 + 18)], fill=(238, 200, 150))
    for wy in range(y0 + 44, y1 - 8, 12):  # lit windows
        for wx in (60, 104):
            draw.rectangle([x0 + wx, wy, x0 + wx + 8, wy + 5], fill=(250, 220, 140))
    # smoke plume
    for (sx, sy, sr) in [(30, 70, 12), (24, 50, 16), (32, 30, 20), (26, 12, 14)]:
        draw.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                     fill=(120, 118, 112))
    draw.rectangle([x0, y1 - 14, x1, y1], fill=(70, 58, 46))


def outage_panel(draw, box):
    """A dark monitor with an error screen."""
    x0, y0, x1, y1 = box
    vgrad(draw, box, (200, 208, 220), (150, 162, 178))
    draw.rectangle([x0 + 18, y0 + 16, x1 - 18, y0 + 112], fill=(16, 42, 92),
                   outline=(10, 10, 10), width=3)
    draw.rectangle([x0 + 62, y0 + 112, x0 + 88, y0 + 128], fill=(40, 40, 40))
    draw.rectangle([x0 + 40, y0 + 128, x1 - 40, y0 + 134], fill=(40, 40, 40))
    draw.text((x0 + 34, y0 + 26), ":(", font=font(SANS_B, 34), fill=(255, 255, 255))
    draw.text((x0 + 34, y0 + 66), "SERVICE", font=font(SANS_B, 13), fill=(255, 255, 255))
    draw.text((x0 + 34, y0 + 86), "OUTAGE", font=font(SANS_B, 13), fill=(255, 180, 60))
    # red warning triangle
    tx, ty = x1 - 48, y0 + 30
    draw.polygon([(tx, ty), (tx + 26, ty), (tx + 13, ty + 24)], fill=(200, 30, 30))
    draw.text((tx + 10, ty + 6), "!", font=font(SANS_B, 14), fill=(255, 255, 255))


def space_panel(draw, box):
    """Earth's curve, a satellite, and a red warning star."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(8, 10, 24))
    for (sx, sy) in [(12, 20), (40, 60), (120, 14), (90, 90), (30, 110), (130, 70)]:
        draw.ellipse([x0 + sx, y0 + sy, x0 + sx + 3, y0 + sy + 3], fill=(255, 255, 255))
    draw.ellipse([x0 - 60, y0 + 96, x0 + 210, y0 + 260], fill=(30, 90, 170))
    draw.ellipse([x0 - 40, y0 + 104, x0 + 190, y0 + 220], fill=(46, 120, 200))
    draw.ellipse([x0 - 20, y0 + 110, x0 + 60, y0 + 150], fill=(40, 110, 70))
    draw.ellipse([x0 + 80, y0 + 118, x0 + 150, y0 + 150], fill=(40, 110, 70))
    draw.ellipse([x0, y0 + 96, x1, y0 + 112], fill=(120, 190, 240))
    # orbit
    draw.ellipse([x0 + 8, y0 + 8, x1 - 8, y0 + 120], outline=(150, 150, 170), width=2)
    # satellite
    sx, sy = x0 + 104, y0 + 30
    draw.rectangle([sx - 26, sy - 4, sx - 8, sy + 4], fill=(60, 110, 200))
    draw.rectangle([sx + 8, sy - 4, sx + 26, sy + 4], fill=(60, 110, 200))
    draw.rectangle([sx - 8, sy - 7, sx + 8, sy + 7], fill=(200, 200, 210),
                   outline=(120, 120, 130))
    draw.line([sx, sy - 7, sx + 6, sy - 18], fill=(200, 200, 210), width=2)
    burst(draw, x1 - 26, y0 + 26, 12, (220, 40, 40))


def rocket_panel(draw, box):
    """Shenzhou-24 lifting off."""
    x0, y0, x1, y1 = box
    vgrad(draw, box, (24, 48, 96), (120, 160, 210))
    for (sx, sy) in [(14, 18), (120, 30), (60, 10), (100, 60), (30, 70)]:
        draw.ellipse([x0 + sx, y0 + sy, x0 + sx + 3, y0 + sy + 3], fill=(255, 255, 255))
    # rocket body
    rx = x0 + 75
    draw.polygon([(rx - 10, y0 + 30), (rx, y0 + 12), (rx + 10, y0 + 30)], fill=(200, 30, 30))
    draw.rectangle([rx - 10, y0 + 30, rx + 10, y0 + 92], fill=(240, 240, 235))
    draw.rectangle([rx - 10, y0 + 52, rx + 10, y0 + 60], fill=(200, 30, 30))
    draw.polygon([(rx - 10, y0 + 92), (rx - 20, y0 + 108), (rx - 10, y0 + 100)], fill=(180, 30, 30))
    draw.polygon([(rx + 10, y0 + 92), (rx + 20, y0 + 108), (rx + 10, y0 + 100)], fill=(180, 30, 30))
    # flame + smoke
    draw.polygon([(rx - 7, y0 + 100), (rx, y0 + 132), (rx + 7, y0 + 100)], fill=(250, 170, 30))
    draw.polygon([(rx - 4, y0 + 100), (rx, y0 + 120), (rx + 4, y0 + 100)], fill=(250, 230, 90))
    for (sx, sy, sr) in [(40, 128, 18), (70, 136, 22), (104, 130, 18), (55, 142, 14)]:
        draw.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                     fill=(225, 225, 220))
    draw.rectangle([x0, y1 - 8, x1, y1], fill=(60, 70, 60))


def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # masthead
    title = font(SERIF_B, 58)
    d.text((W // 2, 12), "THE GLOBAL HERALD", font=title, fill=INK, anchor="mt")
    d.line([(16, 74), (W - 16, 74)], fill=RULE, width=2)
    small = font(SANS, 13)
    d.text((16, 80), "WEDNESDAY, 25 NOVEMBER 2026", font=small, fill=INK)
    d.text((W - 16, 80), "PRICE: ONE DOLLAR  •  No. 329", font=small, fill=INK, anchor="rt")
    d.line([(16, 98), (W - 16, 98)], fill=RULE, width=1)
    # hero picture + headline
    hero_sea(d, (16, 104, W - 16, 294))
    head = font(SERIF_B, 34)
    lines = wrap(d, "KYIV STRIKES RUSSIAN SHIPS IN TWO SEAS", head, W - 32)
    y = 302
    for ln in lines:
        d.text((W // 2, y), ln, font=head, fill=INK, anchor="mt")
        y += 40
    sub = font(SERIF, 16)
    d.text((W // 2, y + 2),
           "Zelenskiy confirms the Sparta II drone strike in the Gulf of Finland —",
           font=sub, fill=INK, anchor="mt")
    d.text((W // 2, y + 22),
           "and Kyiv claims a warship sunk off Libya. Moscow calls it terrorism.",
           font=sub, fill=INK, anchor="mt")
    d.line([(16, 402), (W - 16, 402)], fill=RULE, width=2)
    # 2 x 2 grid of stories
    stories = [
        (tower_panel, "HOUTHI MISSILE HITS RIYADH'S TALLEST TOWER",
         "Eleven wounded in a second strike in days, Saudi civil defence says."),
        (outage_panel, "MICROSOFT DECLARES 'CODE RED'",
         "Historic outage knocks out mail and Teams worldwide, memos show."),
        (space_panel, "NATO VOWS SPACE DEFENCE",
         "Alliance answers reports Russia is readying a nuclear-armed satellite."),
        (rocket_panel, "CHINA LAUNCHES SHENZHOU-24",
         "First Pakistani astronaut flies to the Tiangong space station."),
    ]
    cells = [(16, 412, 506, 535), (518, 412, 1008, 535),
             (16, 542, 506, 665), (518, 542, 1008, 665)]
    for (art, headline, deck), (cx0, cy0, cx1, cy1) in zip(stories, cells):
        art(d, (cx0, cy0, cx0 + 150, cy1))
        tx = cx0 + 162
        tw = cx1 - tx
        hf = font(SERIF_B, 19)
        for i, ln in enumerate(wrap(d, headline, hf, tw)):
            d.text((tx, cy0 + 4 + i * 23), ln, font=hf, fill=INK)
        nlines = len(wrap(d, headline, hf, tw))
        df = font(SANS, 13)
        for j, ln in enumerate(wrap(d, deck, df, tw)):
            d.text((tx, cy0 + 8 + nlines * 23 + j * 17), ln, font=df, fill=(60, 60, 60))
    d.line([(512, 412), (512, 665)], fill=(180, 172, 150), width=1)
    d.line([(16, 538), (W - 16, 538)], fill=(180, 172, 150), width=1)
    d.line([(16, 670), (W - 16, 670)], fill=RULE, width=1)
    foot = font(SANS, 11)
    d.text((W // 2, 673), "THE GLOBAL HERALD — ALL THE WORLD'S NEWS, IN ONE PAGE",
           font=foot, fill=(90, 90, 90), anchor="mt")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    img.save(out_path, "PNG")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    build(out)


if __name__ == "__main__":
    main()
