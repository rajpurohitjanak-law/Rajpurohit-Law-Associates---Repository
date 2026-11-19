#!/usr/bin/env python3
"""Render a Rajpurohit Law Associates headline-style judgment card (1080x1350 JPEG).
Blue (navy) and golden design, used for Instagram and LinkedIn from 19 Nov 2026.

Usage: make_headline_card.py spec.json out.jpg
spec.json keys:
  court      e.g. "Supreme Court of India"
  topic      short subject line, e.g. "Insolvency · Liquidation Auction"
  highlight  first part of the headline: the legal principle (shown on gold), ends with ";"
  rest       second part of the headline: the outcome (plain ivory text)
  bench      list of judge names, e.g. ["Justice A", "Justice B"] (max 3)
  case       case title, e.g. "X v. Y"
  citation   citation and date line, e.g. "2026 INSC 1062 · 28 September 2026"
No source credit is ever shown. The firm badge and contact footer are added to every card.
Exits with an error if the headline cannot fit; then shorten highlight/rest.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersample factor
W, H = 1080, 1350
NAVY, GOLD, IVORY, MUTED = (14, 27, 51), (201, 162, 76), (244, 240, 230), (170, 180, 198)
HERE = os.path.dirname(os.path.abspath(__file__))
NEWS = os.path.join(HERE, "fonts", "Newsreader.ttf")
SERIF_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
SANS_FALLBACK = {"Regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"}

def serif(size, weight=600):
    try:
        f = ImageFont.truetype(NEWS, int(size * S))
        f.set_variation_by_axes([weight, min(72, max(6, size))])
        return f
    except Exception:
        return ImageFont.truetype(SERIF_FALLBACK, int(size * S * 0.9))

def sans(size, style="Regular"):
    for p in (INTER % style, SANS_FALLBACK.get(style, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")):
        try:
            return ImageFont.truetype(p, int(size * S))
        except Exception:
            pass
    return ImageFont.load_default()

def P(v):
    return int(round(v * S))

def spaced(d, xy, text, fnt, fill, tracking):
    """Draw text with letter spacing (design px). Returns end x (design px)."""
    x, y = xy
    for ch in text:
        d.text((P(x), P(y)), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) / S + tracking
    return x

def headline_lines(d, hi, rest, fnt, width):
    words = [(w, True) for w in hi.split()] + [(w, False) for w in rest.split()]
    space = d.textlength(" ", font=fnt) / S
    lines, cur, cw = [], [], 0.0
    for w, flag in words:
        ww = d.textlength(w, font=fnt) / S
        add = ww if not cur else space + ww
        if cur and cw + add > width:
            lines.append(cur); cur, cw = [], 0.0; add = ww
        cur.append((w, flag, ww)); cw += add
    if cur: lines.append(cur)
    return lines, space

def dome(d, ox, oy, sc):
    def T(x, y): return (P(ox + x * sc), P(oy + y * sc))
    w = P(3)
    def line(a, b): d.line([T(*a), T(*b)], fill=GOLD, width=w)
    def rect(x, y, ww, hh):
        pts = [(x, y), (x + ww, y), (x + ww, y + hh), (x, y + hh), (x, y)]
        d.line([T(*p) for p in pts], fill=GOLD, width=w, joint="curve")
    def bez(p0, p1, p2, p3=None, n=40):
        pts = []
        for i in range(n + 1):
            t = i / n
            if p3 is None:
                x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0]
                y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]
            else:
                x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t*t*p2[0] + t**3*p3[0]
                y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t*t*p2[1] + t**3*p3[1]
            pts.append(T(x, y))
        d.line(pts, fill=GOLD, width=w, joint="curve")
    line((220, 8), (220, 34))
    c = T(220, 40); r = P(7 * sc)
    d.ellipse([c[0]-r, c[1]-r, c[0]+r, c[1]+r], outline=GOLD, width=w)
    bez((196, 62), (220, 44), (244, 62))
    bez((110, 168), (110, 92), (160, 62), (220, 62)); bez((220, 62), (280, 62), (330, 92), (330, 168))
    bez((150, 168), (152, 110), (180, 78), (220, 62)); bez((290, 168), (288, 110), (260, 78), (220, 62))
    line((220, 62), (220, 168))
    rect(96, 168, 248, 16); rect(112, 184, 216, 62)
    for x in range(136, 305, 24): line((x, 194), (x, 236))
    rect(80, 246, 280, 18); rect(30, 264, 380, 66)
    for x in (66, 102, 138, 174, 266, 302, 338, 374): line((x, 278), (x, 330))
    line((198, 330), (198, 296)); bez((198, 296), (220, 276), (242, 296)); line((242, 296), (242, 330))

def draw_card(s, size):
    img = Image.new("RGB", (W * S, H * S), NAVY)
    d = ImageDraw.Draw(img)
    M = 72
    # kicker
    spaced(d, (M, 86), s["court"].upper(), sans(22, "Bold"), GOLD, 3)
    spaced(d, (M, 124), s["topic"].upper(), sans(20, "Medium"), MUTED, 1.5)
    # firm badge (sized to the text so the name is never cut)
    f1, f2 = serif(44, 700), sans(17, "Bold")
    w1 = d.textlength("Rajpurohit", font=f1) / S
    t2 = "LAW ASSOCIATES"
    w2 = sum(d.textlength(c, font=f2) / S + 4 for c in t2) - 4
    bw = max(w1, w2) + 68
    bx, by, bh = W - M - bw, 64, 132
    d.rounded_rectangle([P(bx), P(by), P(bx + bw), P(by + bh)], radius=P(10), fill=GOLD)
    d.text((P(bx + (bw - w1) / 2), P(by + 28)), "Rajpurohit", font=f1, fill=NAVY)
    spaced(d, (bx + (bw - w2) / 2, by + 88), t2, f2, NAVY, 4)
    # bench block (anchored to the bottom)
    bench = s["bench"][:3]
    fb, fc = serif(32, 600), sans(20, "Medium")
    case_lines = []
    for txt in (s["case"], s["citation"]):
        cur = ""
        for wd in txt.split():
            t = (cur + " " + wd).strip()
            if d.textlength(t, font=fc) / S <= 500: cur = t
            else: case_lines.append(cur); cur = wd
        if cur: case_lines.append(cur)
    block_h = 22 + 14 + len(bench) * 42 + 14 + len(case_lines) * 29
    by0 = H - 150 - block_h
    y = by0
    spaced(d, (M, y), "BENCH", sans(18, "Bold"), GOLD, 2.5); y += 36
    for b in bench:
        d.text((P(M), P(y)), b, font=fb, fill=IVORY); y += 42
    y += 14
    for ln in case_lines:
        d.text((P(M), P(y)), ln, font=fc, fill=MUTED); y += 29
    # headline
    top, x0 = 262, M + 38
    fh = serif(size, 600)
    lines, space = headline_lines(d, s["highlight"], s["rest"], fh, W - M - x0 - 10)
    lh = size * 1.32
    fits = top + len(lines) * lh <= by0 - 40
    d.rectangle([P(M), P(top + 6), P(M + 8), P(top + len(lines) * lh - 6)], fill=GOLD)
    y = top
    for ln in lines:
        x = x0
        hi = [w for w in ln if w[1]]
        if hi:
            hw = sum(w[2] for w in hi) + space * (len(hi) - 1)
            d.rectangle([P(x - 10), P(y + size * 0.10), P(x + hw + 10), P(y + size * 1.22)], fill=GOLD)
        for w, flag, ww in ln:
            d.text((P(x), P(y + size * 0.12)), w, font=fh, fill=NAVY if flag else IVORY)
            x += ww + space
        y += lh
    # court drawing
    dome(d, W - 56 - 400, H - 110 - 300, 400 / 440)
    # footer
    d.rectangle([0, P(H - 110), P(W), P(H - 107)], fill=GOLD)
    d.text((P(M), P(H - 98)), "Rajpurohit Law Associates · Janak Rajpurohit – Advocate", font=sans(21, "SemiBold"), fill=GOLD)
    d.text((P(M), P(H - 66)), "rajpurohit.office@gmail.com · Land Line – 07948996598 · Mobile – 9624912346", font=sans(19, "Regular"), fill=IVORY)
    d.text((P(M), P(H - 34)), "Disclaimer: general information based on the author's own interpretation of the judgment; not legal advice.", font=sans(15, "Regular"), fill=MUTED)
    return img, fits

def main(spec_path, out_path):
    s = json.load(open(spec_path, encoding="utf-8"))
    for k in ("court", "topic", "highlight", "rest", "bench", "case", "citation"):
        if k not in s: sys.exit("spec is missing key: " + k)
    size = 68
    while True:
        img, fits = draw_card(s, size)
        if fits or size <= 46: break
        size -= 2
    if not fits:
        sys.exit("Headline too long for the card even at the smallest size; shorten highlight/rest.")
    img.resize((W, H), Image.LANCZOS).save(out_path, "JPEG", quality=93)
    print("saved", out_path, (W, H), "headline size", size)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
