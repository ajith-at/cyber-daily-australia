# RETIRED 19 Oct 2026: superseded by x/make_brand_assets.py (owner-supplied artwork).
import os, sys
if os.environ.get("FORCE_OLD_GENERATED_ART") != "1":
    sys.exit("RETIRED: the brand now uses the owner-supplied U51 artwork in /workspace/podcast/brand_src. Run x/make_brand_assets.py instead. (Set FORCE_OLD_GENERATED_ART=1 only to reproduce the old placeholder art.)")
# Generates the 3000x3000 podcast cover in the navy/cyan style. Writes site/cover.jpg and site/<brand.COVER> (cache-busting name used by the feed).
import sys; sys.path.insert(0, "/workspace/podcast"); import brand as B
from PIL import Image, ImageDraw, ImageFont
W = H = 3000
NAVY=(12,28,51); CYAN=(0,180,215); GREY=(200,212,226); WHITE=(255,255,255)
img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
BF="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; RF="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
big = ImageFont.truetype(BF, 1050); mid = ImageFont.truetype(BF, 170); small = ImageFont.truetype(RF, 118)
cx = W // 2
# "U" white + "51" cyan, centred optically using the glyph bounding boxes
a, b = "U", "51"
ba, bb = d.textbbox((0, 0), a, font=big), d.textbbox((0, 0), b, font=big)
wa, wb = d.textlength(a, font=big), d.textlength(b, font=big)
x0 = cx - (wa + wb) / 2; top = 620 - ba[1]
d.text((x0, top), a, font=big, fill=WHITE); d.text((x0 + wa, top), b, font=big, fill=CYAN)
y_line = 1660
d.line([(cx - 1150, y_line), (cx + 1150, y_line)], fill=CYAN, width=16)
def ctext(y, t, f, fill):
    w = d.textlength(t, font=f); d.text((cx - w / 2, y), t, font=f, fill=fill)
ctext(1780, "Cyber and AI Security Pod", mid, WHITE)
ctext(2060, "The daily cyber and AI threat brief", small, GREY)
ctext(2220, "from Melbourne", small, GREY)
for name in ("cover.jpg", B.COVER):
    img.save(f"/workspace/podcast/site/{name}", quality=92, optimize=True, progressive=False)
print("ok", img.size)
