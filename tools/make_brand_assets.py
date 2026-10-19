# Builds every image asset from the owner-supplied U51 artwork in /workspace/podcast/brand_src (the brand source of truth).
# Outputs: site/<brand.COVER> + site/cover.jpg (3000x3000 podcast cover), x_banner.png (1500x500), x_avatar.png (400x400),
# site/img/* (web logo, banner strip, og image, favicons). Run: python3 x/make_brand_assets.py   (not run by publish.sh)
import sys, io, os; sys.path.insert(0, "/workspace/podcast"); import brand as B
from PIL import Image
D = "/workspace/podcast"; L = Image.LANCZOS
cov = Image.open(f"{D}/brand_src/u51_cover_src.png").convert("RGB")
ban = Image.open(f"{D}/brand_src/u51_banner_src.png").convert("RGB")
assert cov.width == cov.height, cov.size
def jpeg_under(img, path, limit=512_000):
    for q in (92, 90, 88, 86, 84, 82, 80, 78, 75, 72, 70):
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=q, optimize=True, progressive=False, subsampling=0 if q >= 88 else 2)
        if buf.tell() <= limit: break
    open(path, "wb").write(buf.getvalue()); return q, buf.tell()
big = cov.resize((3000, 3000), L)
q, n = jpeg_under(big, f"{D}/site/{B.COVER}"); open(f"{D}/site/cover.jpg", "wb").write(open(f"{D}/site/{B.COVER}", "rb").read())
print("cover", B.COVER, big.size, "q", q, n, "bytes")
# banner: crop minimum to exactly 3:1 around the centre, then resize
w, h = ban.size
if w * 1 > h * 3: nw = h * 3; ban = ban.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
elif w * 1 < h * 3: nh = w // 3; ban = ban.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
ban.resize((1500, 500), L).save(f"{D}/x_banner.png", optimize=True)
cov.resize((400, 400), L).save(f"{D}/x_avatar.png", optimize=True)
os.makedirs(f"{D}/site/img", exist_ok=True)
cov.resize((600, 600), L).save(f"{D}/site/img/u51-logo-600.jpg", quality=85, optimize=True, progressive=True)
cov.resize((160, 160), L).save(f"{D}/site/img/u51-logo-160.jpg", quality=85, optimize=True, progressive=True)
cov.resize((1200, 1200), L).save(f"{D}/site/img/u51-og-1200.jpg", quality=84, optimize=True, progressive=True)
ban.resize((1500, 500), L).save(f"{D}/site/img/u51-banner-1500.jpg", quality=82, optimize=True, progressive=True)
cov.resize((180, 180), L).save(f"{D}/site/img/apple-touch-icon.png", optimize=True)
cov.resize((32, 32), L).save(f"{D}/site/img/favicon-32.png", optimize=True)
cov.save(f"{D}/site/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
print("ok")
