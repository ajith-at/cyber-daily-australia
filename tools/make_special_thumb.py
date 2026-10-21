#!/usr/bin/env python3
"""Sunday Special episode artwork, to Apple Podcasts art specs (3000x3000 RGB JPEG, under 512 KB).
Usage: python3 make_special_thumb.py <YYYY-MM-DD> "<short topic title>" <episode number> [--preview] [--dark] [--contrast]
Writes /workspace/podcast/specials/<date>/thumb.jpg (and thumb-300.jpg with --preview) in the light Soft Indigo Desk style,
the default since 22 Oct 2026. With --dark it writes thumb-dark.jpg / thumb-dark-300.jpg instead, so thumb.jpg is never overwritten.
--contrast prints the WCAG contrast ratio of every text element against the background actually rendered under it. Run with system python3 (needs PIL).
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

# ---------- WCAG contrast ----------
def lum(c):
    f = lambda v: (v / 255) / 12.92 if v / 255 <= 0.03928 else ((v / 255 + 0.055) / 1.055) ** 2.4
    r, g, b = (f(v) for v in c[:3]); return 0.2126 * r + 0.7152 * g + 0.0722 * b
def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + 0.05) / (lb + 0.05)
def darken_to(c, bgs, target):
    """Darken colour c (towards black, keeping its hue) until it reaches `target` contrast against every bg in bgs."""
    k = 1.0
    while k > 0 and min(ratio(tuple(round(v * k) for v in c), b) for b in bgs) < target: k -= 0.01
    return tuple(round(v * k) for v in c)

# ---------- themes ----------
DARK = dict(name="dark", bg_top=NIGHT, bg_bottom=DEEP, glows=(((-700, -900, 1700, 1300), (10, 70, 130)), ((1500, 1700, 3700, 3800), (70, 30, 120))), glow_mix=.55,
            frame=(BLUE, VIOLET), frame_mix=1.0, ink=WHITE, accent=BLUE, show=WHITE, muted=MUTED, pill=INDIGO, pill_text=WHITE, wave=(BLUE, VIOLET), wave_mix=1.0)
# Soft Indigo Desk light tokens: shell #eef1fb -> canvas #c9d7f8, ink #2a2e45, indigo #5c4de0, on-indigo #f7f6ff, muted #5e6582.
# The brand blue is darkened at render time until it reaches 4.5:1 against the background under it (see render()).
LIGHT = dict(name="light", bg_top=(0xee, 0xf1, 0xfb), bg_bottom=(0xc9, 0xd7, 0xf8), glows=(((-700, -900, 1700, 1300), (255, 255, 255)),), glow_mix=.45,
             frame=(BLUE, INDIGO), frame_mix=.55, ink=(0x2a, 0x2e, 0x45), accent=BLUE, show=(0x5e, 0x65, 0x82), muted=(0x5e, 0x65, 0x82),
             pill=(0x5c, 0x4d, 0xe0), pill_text=(0xf7, 0xf6, 0xff), wave=(INDIGO, VIOLET), wave_mix=.55)

def render(date, title, num, T=DARK, report=None):
    img = Image.new("RGB", (W, H), T["bg_top"])
    # background: vertical gradient plus soft glows
    bg = Image.new("RGB", (1, H)); bg.putdata([lerp(T["bg_top"], T["bg_bottom"], (y / H) ** 1.4) for y in range(H)]); img.paste(bg.resize((W, H)))
    glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    for box, col in T["glows"]: gd.ellipse(box, fill=col)
    if T["name"] == "dark":
        img = Image.blend(img, Image.composite(glow, img, Image.new("L", (W, H), 255)).filter(ImageFilter.GaussianBlur(420)), T["glow_mix"])
    else:   # light: only lighten where the glow is drawn
        gm = Image.new("L", (W, H), 0); ImageDraw.Draw(gm).ellipse(T["glows"][0][0], fill=round(255 * T["glow_mix"]))
        img = Image.composite(Image.new("RGB", (W, H), T["glows"][0][1]), img, gm.filter(ImageFilter.GaussianBlur(420)))
    d = ImageDraw.Draw(img)
    # gradient frame, like the ring on the cover art (subtle on the light theme)
    m, r, bw = 110, 190, 26
    mask = Image.new("L", (W, H), 0); md = ImageDraw.Draw(mask)
    md.rounded_rectangle((m, m, W - m, H - m), r, fill=255); md.rounded_rectangle((m + bw, m + bw, W - m - bw, H - m - bw), r - bw, fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(2)).point(lambda v: round(v * T["frame_mix"]))
    img.paste(hgrad(W, H, *T["frame"]), (0, 0), mask)
    clean = img.copy()   # background only, for contrast checks
    d = ImageDraw.Draw(img)
    def bgs_under(box):
        """Lightest and darkest background colours under a box (sampled from the clean background)."""
        crop = clean.crop(tuple(int(v) for v in box)).resize((32, 8))
        px = list(crop.get_flattened_data() if hasattr(crop, 'get_flattened_data') else crop.getdata()); px.sort(key=lum); return [px[0], px[-1]]
    WHITE_, BLUE_ = T["ink"], T["accent"]
    if T["name"] == "light":   # darken the brand blue to at least 4.5:1 over the whole area it is used in
        BLUE_ = darken_to(BLUE, bgs_under((330, 250, 2670, 2900)), 4.5)
    T = dict(T, accent=BLUE_)
    def check(name, box, fg, bg_cols, large):
        if report is not None:
            worst = min(ratio(fg, b) for b in bg_cols); need = 3.0 if large else 4.5
            report.append((name, "#%02x%02x%02x" % fg[:3], round(worst, 2), need, "PASS" if worst >= need else "FAIL"))
    X0, X1 = 330, W - 330
    # U51 mark: "U5" white, "1" brand blue, with the show line under it
    mf = font(470, 800, "Montserrat/Montserrat-VariableFont_wght.ttf")
    try: mf.set_variation_by_axes([900])
    except Exception: pass
    y = 280
    wu = d.textlength("U5", font=mf); bb = d.textbbox((X0, y), "U51", font=mf)
    d.text((X0, y), "U5", font=mf, fill=WHITE_); d.text((X0 + wu, y), "1", font=mf, fill=BLUE_)
    check("U51 mark: U5", bb, WHITE_, bgs_under(bb), True); check("U51 mark: 1", bb, BLUE_, bgs_under(bb), True)
    sf = font(96, 800, "Montserrat/Montserrat-VariableFont_wght.ttf")
    sy = bb[3] + 40; x = X0
    sbb = d.textbbox((X0, sy), "CYBER AND AI SECURITY POD", font=sf)
    for part, col in (("CYBER ", T["show"]), ("AND AI", BLUE_), (" SECURITY POD", T["show"])):
        d.text((x, sy), part, font=sf, fill=col); x += d.textlength(part, font=sf)
    check("show line", sbb, T["show"], bgs_under(sbb), False); check("show line: AND AI", sbb, BLUE_, bgs_under(sbb), False)
    # SUNDAY SPECIAL pill
    pf = font(150, 800); label = "SUNDAY SPECIAL"
    pw = d.textlength(label, font=pf); py = 1020; ph = 240
    d.rounded_rectangle((X0, py, X0 + pw + 180, py + ph), ph // 2, fill=T["pill"])
    lb = d.textbbox((0, 0), label, font=pf)
    d.text((X0 + 90, py + (ph - (lb[3] - lb[1])) / 2 - lb[1]), label, font=pf, fill=T["pill_text"])
    check("SUNDAY SPECIAL pill", (0, 0, 1, 1), T["pill_text"], [T["pill"]], False)
    # date, muted, right-aligned on the pill row
    df = font(120, 600); ds = datetime.date.fromisoformat(date).strftime("%-d %b %Y").upper()
    dbb = d.textbbox((0, 0), ds, font=df)
    dpos = (X1 - (dbb[2] - dbb[0]) - dbb[0], py + (ph - (dbb[3] - dbb[1])) / 2 - dbb[1])
    d.text(dpos, ds, font=df, fill=T["muted"])
    dbox = d.textbbox(dpos, ds, font=df); check("date", dbox, T["muted"], bgs_under(dbox), False)
    # topic title: largest size that fits in at most 3 lines inside the title box
    maxw = X1 - X0; ty = py + ph + 130; box_bottom = 2260
    for size in range(330, 150, -10):
        tf = font(size, 800); lines = wrap(d, title, tf, maxw)
        if len(lines) <= 3 and all(d.textlength(l, font=tf) <= maxw for l in lines) and ty + len(lines) * int(size * 1.12) <= box_bottom: break
    else:
        raise SystemExit("title too long for 3 lines; shorten it")
    lh = int(size * 1.12)
    for i, l in enumerate(lines):
        d.text((X0, ty + i * lh), l, font=tf, fill=WHITE_); lbox = d.textbbox((X0, ty + i * lh), l, font=tf)
        check(f"title line {i + 1}", lbox, WHITE_, bgs_under(lbox), True)
    # waveform motif (blue -> violet bars), then the episode number and date
    import math
    by = 2400; n = 46; step = (X1 - X0) / n
    for i in range(n):
        hgt = 40 + 150 * abs(math.sin(i * 0.55) * math.cos(i * 0.21))
        c = lerp(*T["wave"], i / (n - 1)); cx = X0 + i * step + step / 2
        if T["wave_mix"] < 1: c = lerp(clean.getpixel((int(cx), by)), c, T["wave_mix"])
        d.rounded_rectangle((cx - 9, by - hgt / 2, cx + 9, by + hgt / 2), 9, fill=c)
    ef = font(230, 800)
    d.text((X0, 2540), f"EPISODE {num}", font=ef, fill=BLUE_)
    ebox = d.textbbox((X0, 2540), f"EPISODE {num}", font=ef); check("EPISODE N", ebox, BLUE_, bgs_under(ebox), True)
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
    dark = "--dark" in sys.argv; stem = "thumb-dark" if dark else "thumb"; rep = []
    img, nl, size = render(date, title, num, DARK if dark else LIGHT, rep)
    q, sz = save_under(img, f"{out}/{stem}.jpg")
    print(f"{out}/{stem}.jpg 3000x3000 RGB q{q} {sz/1024:.0f} KB, title {nl} line(s) at {size}px")
    if "--preview" in sys.argv:
        img.resize((300, 300), Image.LANCZOS).save(f"{out}/{stem}-300.jpg", quality=90); print(f"{out}/{stem}-300.jpg")
    if "--contrast" in sys.argv:
        for r_ in rep: print("  %-22s %s  %5.2f:1  (needs %.1f)  %s" % r_)
