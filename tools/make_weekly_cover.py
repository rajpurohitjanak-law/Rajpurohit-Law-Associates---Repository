#!/usr/bin/env python3
"""Cover card for 'The Weekly Brief' (1080x1350 JPEG, navy and gold).
Usage: make_weekly_cover.py spec.json out.jpg
spec keys: issue (e.g. "Issue 1 · 22 November 2026"), title, subtitle, provisions (list of up to 3 short strings)
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_headline_card as m
from PIL import Image, ImageDraw
S, W, H, M = m.S, m.W, m.H, 72
def wrap(d, text, f, width):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) / S <= width: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out
def main(sp, out):
    s = json.load(open(sp, encoding="utf-8"))
    img = Image.new("RGB", (W * S, H * S), m.NAVY); d = ImageDraw.Draw(img)
    m.spaced(d, (M, 86), "THE WEEKLY BRIEF", m.sans(26, "Bold"), m.GOLD, 5)
    m.spaced(d, (M, 128), s["issue"].upper(), m.sans(20, "Medium"), m.MUTED, 1.5)
    f1, f2 = m.serif(44, 700), m.sans(17, "Bold"); w1 = d.textlength("Rajpurohit", font=f1) / S
    t2 = "LAW ASSOCIATES"; w2 = sum(d.textlength(c, font=f2) / S + 4 for c in t2) - 4; bw = max(w1, w2) + 68
    bx, by, bh = W - M - bw, 64, 132
    d.rounded_rectangle([m.P(bx), m.P(by), m.P(bx + bw), m.P(by + bh)], radius=m.P(10), fill=m.GOLD)
    d.text((m.P(bx + (bw - w1) / 2), m.P(by + 28)), "Rajpurohit", font=f1, fill=m.NAVY)
    m.spaced(d, (bx + (bw - w2) / 2, by + 88), t2, f2, m.NAVY, 4)
    d.rectangle([m.P(M), m.P(250), m.P(M + 8), m.P(640)], fill=m.GOLD)
    size = 70
    while True:
        ft = m.serif(size, 600); lines = wrap(d, s["title"], ft, W - M - 38 - M - 10)
        if len(lines) * size * 1.25 <= 390 or size <= 48: break
        size -= 2
    y = 258
    for l in lines: d.text((m.P(M + 38), m.P(y)), l, font=ft, fill=m.IVORY); y += size * 1.25
    fs = m.sans(28)
    y = max(y + 18, 560)
    for l in wrap(d, s["subtitle"], fs, W - 2 * M - 38): d.text((m.P(M + 38), m.P(y)), l, font=fs, fill=m.MUTED); y += 42
    y = 760
    m.spaced(d, (M, y), "INSIDE THIS ISSUE", m.sans(20, "Bold"), m.GOLD, 3); y += 44
    for p in s["provisions"][:3]:
        d.rectangle([m.P(M), m.P(y + 6), m.P(M + 10), m.P(y + 34)], fill=m.GOLD)
        d.text((m.P(M + 28), m.P(y)), p, font=m.serif(34, 600), fill=m.IVORY); y += 62
    m.dome(d, W - 56 - 400, H - 110 - 300, 400 / 440)
    d.rectangle([0, m.P(H - 110), m.P(W), m.P(H - 107)], fill=m.GOLD)
    d.text((m.P(M), m.P(H - 98)), "Rajpurohit Law Associates · Janak Rajpurohit – Advocate", font=m.sans(21, "SemiBold"), fill=m.GOLD)
    d.text((m.P(M), m.P(H - 66)), "rajpurohit.office@gmail.com · Land Line – 07948996598 · Mobile – 9624912346", font=m.sans(19), fill=m.IVORY)
    d.text((m.P(M), m.P(H - 34)), "Disclaimer: general information based on the author's own interpretation; not legal advice.", font=m.sans(15), fill=m.MUTED)
    img.resize((W, H), Image.LANCZOS).save(out, "JPEG", quality=93); print("saved", out)
if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
