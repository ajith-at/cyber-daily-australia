#!/usr/bin/env python3
"""Sunday Special episode artwork, to Apple Podcasts art specs (3000x3000 RGB JPEG, under 512 KB).
Usage: python3 make_special_thumb.py <YYYY-MM-DD> "<short topic title>" <episode number> [--preview]
Writes /workspace/podcast/specials/<date>/thumb.jpg (and thumb-300.jpg with --preview). Run with system python3 (needs PIL).
publish.sh copies specials/<date>/thumb.jpg to site/episodes/<slug>.jpg and records it as the episode 'image'.
Design: U51 brand art palette (deep indigo night, brand blue, violet), the U51 mark, a SUNDAY SPECIAL pill,
the topic in large type (at most 3 lines, auto-sized), the episode number and date. Legible at 300px."""
import sys, os, io, datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 3000
NIGHT = (12, 14, 28); DEEP = (28, 24, 78); INDIGO = (92, 77, 224); BLUE = (24, 170, 255); VIOLET = (168, 85, 247)
WHITE = (247, 246, 255); MUTED = (180, 186, 212)
GF = "/usr/share/fonts/truetype/sand-box/google"
def font(size, weight=800, fam="Plus Jakarta Sans/PlusJakartaSans-VariableFont_wght.ttf"):
    try:
        f = ImageFont.truetype(f"{GF}/{fam}", size)
        try: f.set_variation_by_axes([weight])
        except Exception: pass
        return f
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)

def lerp(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
def hgrad(w, h, c1, c2):
    g = Image.new("RGB", (w, 1)); g.putdata([lerp(c1, c2, x / max(1, w - 1)) for x in range(w)]); return g.resize((w, h))

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); return lines

def render(date, title, num):
    img = Image.new("RGB", (W, H), NIGHT)
    # background: vertical night-to-deep-indigo gradient plus two soft glows (blue top-left, violet bottom-right)
    bg = Image.new("RGB", (1, H)); bg.putdata([lerp(NIGHT, DEEP, (y / H) ** 1.4) for y in range(H)]); img.paste(bg.resize((W, H)))
    glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((-700, -900, 1700, 1300), fill=(10, 70, 130)); gd.ellipse((1500, 1700, 3700, 3800), fill=(70, 30, 120))
    img = Image.blend(img, Image.composite(glow, img, Image.new("L", (W, H), 255)).filter(ImageFilter.GaussianBlur(420)), .55)
    d = ImageDraw.Draw(img)
    # gradient frame (blue -> violet), like the ring on the cover art
    m, r, bw = 110, 190, 26
    mask = Image.new("L", (W, H), 0); md = ImageDraw.Draw(mask)
    md.rounded_rectangle((m, m, W - m, H - m), r, fill=255); md.rounded_rectangle((m + bw, m + bw, W - m - bw, H - m - bw), r - bw, fill=0)
    img.paste(hgrad(W, H, BLUE, VIOLET), (0, 0), mask.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(img)
    X0, X1 = 330, W - 330
    # U51 mark: "U5" white, "1" brand blue, with the show line under it
    mf = font(470, 800, "Montserrat/Montserrat-VariableFont_wght.ttf")
    try: mf.set_variation_by_axes([900])
    except Exception: pass
    y = 280
    wu = d.textlength("U5", font=mf); bb = d.textbbox((X0, y), "U51", font=mf)
    d.text((X0, y), "U5", font=mf, fill=WHITE); d.text((X0 + wu, y), "1", font=mf, fill=BLUE)
    sf = font(96, 800, "Montserrat/Montserrat-VariableFont_wght.ttf")
    sy = bb[3] + 40; x = X0
    for part, col in (("CYBER ", WHITE), ("AND AI", BLUE), (" SECURITY POD", WHITE)):
        d.text((x, sy), part, font=sf, fill=col); x += d.textlength(part, font=sf)
    # SUNDAY SPECIAL pill
    pf = font(150, 800); label = "SUNDAY SPECIAL"
    pw = d.textlength(label, font=pf); py = 1020; ph = 240
    d.rounded_rectangle((X0, py, X0 + pw + 180, py + ph), ph // 2, fill=INDIGO)
    lb = d.textbbox((0, 0), label, font=pf)
    d.text((X0 + 90, py + (ph - (lb[3] - lb[1])) / 2 - lb[1]), label, font=pf, fill=WHITE)
    # date, muted, right-aligned on the pill row
    df = font(120, 600); ds = datetime.date.fromisoformat(date).strftime("%-d %b %Y").upper()
    dbb = d.textbbox((0, 0), ds, font=df)
    d.text((X1 - (dbb[2] - dbb[0]) - dbb[0], py + (ph - (dbb[3] - dbb[1])) / 2 - dbb[1]), ds, font=df, fill=MUTED)
    # topic title: largest size that fits in at most 3 lines inside the title box
    maxw = X1 - X0; ty = py + ph + 130; box_bottom = 2260
    for size in range(330, 150, -10):
        tf = font(size, 800); lines = wrap(d, title, tf, maxw)
        if len(lines) <= 3 and all(d.textlength(l, font=tf) <= maxw for l in lines) and ty + len(lines) * int(size * 1.12) <= box_bottom: break
    else:
        raise SystemExit("title too long for 3 lines; shorten it")
    lh = int(size * 1.12)
    for i, l in enumerate(lines): d.text((X0, ty + i * lh), l, font=tf, fill=WHITE)
    # waveform motif (blue -> violet bars), then the episode number and date
    import math
    by = 2400; n = 46; step = (X1 - X0) / n
    for i in range(n):
        hgt = 40 + 150 * abs(math.sin(i * 0.55) * math.cos(i * 0.21))
        c = lerp(BLUE, VIOLET, i / (n - 1)); cx = X0 + i * step + step / 2
        d.rounded_rectangle((cx - 9, by - hgt / 2, cx + 9, by + hgt / 2), 9, fill=c)
    ef = font(230, 800)
    d.text((X0, 2540), f"EPISODE {num}", font=ef, fill=BLUE)
    return img, len(lines), size

def save_under(img, path, limit=512_000):
    for q in (90, 86, 82, 78, 74, 70, 65):
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=q, optimize=True, progressive=False, subsampling=0 if q >= 86 else 2)
        if buf.tell() < limit: open(path, "wb").write(buf.getvalue()); return q, buf.tell()
    raise SystemExit("could not get under 512 KB")

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 3: sys.exit(__doc__)
    date, title, num = a[0], a[1], int(a[2])
    datetime.date.fromisoformat(date)
    out = f"/workspace/podcast/specials/{date}"; os.makedirs(out, exist_ok=True)
    img, nl, size = render(date, title, num)
    q, sz = save_under(img, f"{out}/thumb.jpg")
    print(f"{out}/thumb.jpg 3000x3000 RGB q{q} {sz/1024:.0f} KB, title {nl} line(s) at {size}px")
    if "--preview" in sys.argv:
        img.resize((300, 300), Image.LANCZOS).save(f"{out}/thumb-300.jpg", quality=90); print(f"{out}/thumb-300.jpg")
