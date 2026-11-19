#!/usr/bin/env python3
"""Render a Rajpurohit Law Associates Instagram judgment card (1080x1350 JPEG).

Usage: make_card.py spec.json out.jpg
spec.json keys:
  topic    short field label, e.g. "Arbitration"
  title    one-line headline of the ruling
  sections list of [label, text] in order:
           Provision of Law, Field of Application, Citation, Ratio
           (Ratio is ONE paragraph, no bullets)
  (any "source" key is ignored: no source credit is ever shown on a card)
The footer (firm name, advocate, email, landline, mobile) is added to every card.
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, IVORY, MUTED = (14, 27, 51), (201, 162, 76), (244, 240, 230), (170, 180, 198)
M = 80
FOOT_TOP = H - 215

FOOTER = [
    "Janak Rajpurohit - Advocate",
    "rajpurohit.office@gmail.com",
    "Land Line - 07948996598   |   Mobile - 9624912346",
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

def draw_card(s, k):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=GOLD)
    d.text((M, 55), "LEGAL UPDATE  |  " + s["topic"].upper(), font=font(SANS_B, 24), fill=GOLD)
    y = 105
    f_title = font(SERIF_B, int(46 * k))
    for ln in wrap(d, s["title"], f_title, W - 2 * M):
        d.text((M, y), ln, font=f_title, fill=IVORY); y += int(58 * k)
    y += 6
    d.rectangle([M, y, M + 110, y + 5], fill=GOLD); y += 30
    for label, text in s["sections"]:
        is_ratio = label.lower().startswith("ratio")
        d.text((M, y), label.upper(), font=font(SANS_B, 21), fill=GOLD); y += 34
        f_b = font(SANS, int((30 if is_ratio else 25) * k))
        lh = int((42 if is_ratio else 34) * k)
        col = IVORY if is_ratio else (215, 220, 230)
        for ln in wrap(d, text, f_b, W - 2 * M):
            d.text((M, y), ln, font=f_b, fill=col); y += lh
        y += 20
    fits = y <= FOOT_TOP - 8
    d.line([M, FOOT_TOP, W - M, FOOT_TOP], fill=(60, 78, 110), width=2)
    d.text((M, FOOT_TOP + 16), "Rajpurohit Law Associates", font=font(SERIF_B, 34), fill=IVORY)
    f_c = font(SANS, 21)
    yy = FOOT_TOP + 66
    for ln in FOOTER:
        d.text((M, yy), ln, font=f_c, fill=MUTED); yy += 28
    f_src = font(SANS, 17)
    d.text((M, yy + 6), "Disclaimer: General information based on the author's own interpretation of the judgment;", font=f_src, fill=(130, 142, 165))
    d.text((M, yy + 28), "not legal advice. Please read the full judgment and take professional advice before acting.", font=f_src, fill=(130, 142, 165))
    return img, fits

def main(spec_path, out_path):
    s = json.load(open(spec_path, encoding="utf-8"))
    k = 1.0
    while True:
        img, fits = draw_card(s, k)
        if fits or k < 0.66:
            break
        k -= 0.03
    if not fits:
        sys.exit("Content too long for one card even at smallest size; shorten the text.")
    img.save(out_path, "JPEG", quality=92)
    print("saved", out_path, img.size, "scale", round(k, 2))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
