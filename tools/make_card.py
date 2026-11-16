#!/usr/bin/env python3
"""Render a Rajpurohit Law Associates Instagram judgment card (1080x1350 JPEG).

Usage: make_card.py spec.json out.jpg
spec.json keys: topic, title, court, date, points (list of 3-4 short strings), source
"""
import json, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, IVORY, MUTED = (14, 27, 51), (201, 162, 76), (244, 240, 230), (170, 180, 198)

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

def main(spec_path, out_path):
    s = json.load(open(spec_path, encoding="utf-8"))
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    M = 90
    d.rectangle([0, 0, W, 14], fill=GOLD)
    d.text((M, 70), "LEGAL UPDATE  |  " + s["topic"].upper(), font=font(SANS_B, 28), fill=GOLD)
    y = 150
    f_title = font(SERIF_B, 56)
    for ln in wrap(d, s["title"], f_title, W - 2 * M):
        d.text((M, y), ln, font=f_title, fill=IVORY); y += 72
    y += 14
    d.rectangle([M, y, M + 120, y + 5], fill=GOLD); y += 40
    f_meta = font(SANS_B, 30)
    for ln in wrap(d, s["court"], f_meta, W - 2 * M):
        d.text((M, y), ln, font=f_meta, fill=IVORY); y += 42
    f_date = font(SANS, 28)
    for ln in wrap(d, s["date"], f_date, W - 2 * M):
        d.text((M, y), ln, font=f_date, fill=MUTED); y += 40
    y += 30
    d.text((M, y), "KEY TAKEAWAYS", font=font(SANS_B, 26), fill=GOLD); y += 52
    f_pt = font(SANS, 33)
    for p in s["points"]:
        lines = wrap(d, p, f_pt, W - 2 * M - 50)
        d.ellipse([M, y + 14, M + 14, y + 28], fill=GOLD)
        for ln in lines:
            d.text((M + 40, y), ln, font=f_pt, fill=IVORY); y += 48
        y += 22
    d.line([M, H - 200, W - M, H - 200], fill=(60, 78, 110), width=2)
    d.text((M, H - 180), "Rajpurohit Law Associates", font=font(SERIF_B, 38), fill=IVORY)
    d.text((M, H - 128), "Advocates  |  Gujarat High Court, Ahmedabad", font=font(SANS, 26), fill=MUTED)
    f_src = font(SANS, 22)
    yy = H - 78
    for ln in wrap(d, "General information, not legal advice. Source: " + s["source"], f_src, W - 2 * M)[:2]:
        d.text((M, yy), ln, font=f_src, fill=MUTED); yy += 28
    img.save(out_path, "JPEG", quality=92)
    print("saved", out_path, img.size)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
