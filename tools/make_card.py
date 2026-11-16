#!/usr/bin/env python3
"""Render a Rajpurohit Law Associates Instagram judgment card (1080x1350 JPEG).

Usage: make_card.py spec.json out.jpg
spec.json keys: topic, title, court, date, points (list of 3-4 short strings), source
Every card carries the firm's contact details in small type in the footer.
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, IVORY, MUTED = (14, 27, 51), (201, 162, 76), (244, 240, 230), (170, 180, 198)

ADDRESS = ("51 & 52, 6th Floor, Sanidhya Building, Opposite Sanyas Ashram, Near LIC Building, "
           "Ashram Road, Ellisbridge, Ahmedabad 380009")
CONTACT = ("Mobile: 09624912346  |  Landline: 07948996598  |  "
           "rajpurohit.janak@gmail.com  |  rajpurohit.office@gmail.com")


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
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main(spec_path, out_path):
    s = json.load(open(spec_path, encoding="utf-8"))
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    M = 90
    FOOT_TOP = H - 250  # footer block starts here

    d.rectangle([0, 0, W, 14], fill=GOLD)
    d.text((M, 64), "LEGAL UPDATE  |  " + s["topic"].upper(), font=font(SANS_B, 26), fill=GOLD)
    y = 130
    f_title = font(SERIF_B, 52)
    for ln in wrap(d, s["title"], f_title, W - 2 * M):
        d.text((M, y), ln, font=f_title, fill=IVORY)
        y += 66
    y += 10
    d.rectangle([M, y, M + 120, y + 5], fill=GOLD)
    y += 34
    f_meta = font(SANS_B, 29)
    for ln in wrap(d, s["court"], f_meta, W - 2 * M):
        d.text((M, y), ln, font=f_meta, fill=IVORY)
        y += 40
    f_date = font(SANS, 26)
    for ln in wrap(d, s["date"], f_date, W - 2 * M):
        d.text((M, y), ln, font=f_date, fill=MUTED)
        y += 36
    y += 22
    d.text((M, y), "KEY TAKEAWAYS", font=font(SANS_B, 24), fill=GOLD)
    y += 46

    # shrink bullet text until it fits above the footer
    avail = FOOT_TOP - 24 - y
    size = 33
    while True:
        f_pt = font(SANS, size)
        lh = int(size * 1.45)
        need = sum(len(wrap(d, p, f_pt, W - 2 * M - 50)) * lh + 20 for p in s["points"])
        if need <= avail or size <= 24:
            break
        size -= 1
    for p in s["points"]:
        d.ellipse([M, y + lh // 2 - 7, M + 14, y + lh // 2 + 7], fill=GOLD)
        for ln in wrap(d, p, f_pt, W - 2 * M - 50):
            d.text((M + 40, y), ln, font=f_pt, fill=IVORY)
            y += lh
        y += 20

    # footer
    d.line([M, FOOT_TOP, W - M, FOOT_TOP], fill=(60, 78, 110), width=2)
    fy = FOOT_TOP + 18
    d.text((M, fy), "Rajpurohit Law Associates", font=font(SERIF_B, 34), fill=IVORY)
    fy += 48
    f_small = font(SANS, 19)
    for ln in wrap(d, ADDRESS, f_small, W - 2 * M) + wrap(d, CONTACT, f_small, W - 2 * M):
        d.text((M, fy), ln, font=f_small, fill=MUTED)
        fy += 26
    fy += 6
    f_src = font(SANS, 17)
    for ln in wrap(d, "General information, not legal advice. Source: " + s["source"], f_src, W - 2 * M)[:2]:
        d.text((M, fy), ln, font=f_src, fill=(130, 142, 165))
        fy += 23
    img.save(out_path, "JPEG", quality=92)
    print("saved", out_path, img.size, "bullet font", size, "footer end", fy)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
