#!/usr/bin/env python3
"""Render a Rajpurohit Law Associates Instagram judgment card (1080x1350 JPEG).

Usage: make_card.py spec.json out.jpg
spec.json keys: topic, title, court, date, points (list of 3-4 short strings), source
Every card carries the firm's contact block in small type in the footer.
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, IVORY, MUTED = (14, 27, 51), (201, 162, 76), (244, 240, 230), (170, 180, 198)
M = 80

CONTACT = [
    "Janak Rajpurohit, Advocate  |  51 & 52, 6th Floor, Sanidhya Building, Opp. Sanyas Ashram,",
    "Near LIC Building, Ashram Road, Ellisbridge, Ahmedabad 380009",
    "Mobile: 09624912346  |  Landline: 07948996598",
    "rajpurohit.janak@gmail.com  |  rajpurohit.office@gmail.com",
]

def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

SERIF_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
SANS = ["/usr/share/fonts/opentype/inter/Inter-Regular.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
SANS_B = ["/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]

def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

FOOT_TOP = H - 290  # footer divider line

def draw_card(s, k):
    """k = scale for body text (1.0 = largest). Returns (img, fits)."""
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=GOLD)
    d.text((M, 60), "LEGAL UPDATE  |  " + s["topic"].upper(), font=font(SANS_B, 26), fill=GOLD)
    y = 125
    f_title = font(SERIF_B, int(52 * k))
    for ln in wrap(d, s["title"], f_title, W - 2 * M):
        d.text((M, y), ln, font=f_title, fill=IVORY); y += int(66 * k)
    y += 10
    d.rectangle([M, y, M + 110, y + 5], fill=GOLD); y += 34
    f_meta = font(SANS_B, int(28 * k))
    for ln in wrap(d, s["court"], f_meta, W - 2 * M):
        d.text((M, y), ln, font=f_meta, fill=IVORY); y += int(40 * k)
    f_date = font(SANS, int(26 * k))
    for ln in wrap(d, s["date"], f_date, W - 2 * M):
        d.text((M, y), ln, font=f_date, fill=MUTED); y += int(36 * k)
    y += 26
    d.text((M, y), "KEY TAKEAWAYS", font=font(SANS_B, 24), fill=GOLD); y += 46
    f_pt = font(SANS, int(31 * k))
    for p in s["points"]:
        d.ellipse([M, y + 12, M + 13, y + 25], fill=GOLD)
        for ln in wrap(d, p, f_pt, W - 2 * M - 44):
            d.text((M + 38, y), ln, font=f_pt, fill=IVORY); y += int(44 * k)
        y += 16
    fits = y <= FOOT_TOP - 10
    # footer
    d.line([M, FOOT_TOP, W - M, FOOT_TOP], fill=(60, 78, 110), width=2)
    d.text((M, FOOT_TOP + 16), "Rajpurohit Law Associates", font=font(SERIF_B, 34), fill=IVORY)
    f_c = font(SANS, 20)
    yy = FOOT_TOP + 68
    for ln in CONTACT:
        d.text((M, yy), ln, font=f_c, fill=MUTED); yy += 26
    f_src = font(SANS, 18)
    yy += 8
    for ln in wrap(d, "General information, not legal advice. Source: " + s["source"], f_src, W - 2 * M)[:2]:
        d.text((M, yy), ln, font=f_src, fill=(130, 142, 165)); yy += 23
    return img, fits

def main(spec_path, out_path):
    s = json.load(open(spec_path, encoding="utf-8"))
    k = 1.0
    while True:
        img, fits = draw_card(s, k)
        if fits or k < 0.7:
            break
        k -= 0.04
    if not fits:
        sys.exit("Content too long for one card even at smallest size; shorten the points.")
    img.save(out_path, "JPEG", quality=92)
    print("saved", out_path, img.size, "scale", round(k, 2))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
