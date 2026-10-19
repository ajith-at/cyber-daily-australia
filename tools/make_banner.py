# RETIRED 19 Oct 2026: superseded by x/make_brand_assets.py (owner-supplied artwork).
import os, sys
if os.environ.get("FORCE_OLD_GENERATED_ART") != "1":
    sys.exit("RETIRED: the brand now uses the owner-supplied U51 artwork in /workspace/podcast/brand_src. Run x/make_brand_assets.py instead. (Set FORCE_OLD_GENERATED_ART=1 only to reproduce the old placeholder art.)")
# Generates the 1500x500 X banner for U51 Cyber and AI Security Pod (@u51cyber) in the cover style (navy, cyan, DejaVu Sans).
from PIL import Image, ImageDraw, ImageFont
import random, math
S=2; W,H=1500*S,500*S
NAVY=(12,28,51); CYAN=(0,180,215); GREY=(200,212,226); WHITE=(255,255,255)
img=Image.new("RGB",(W,H),NAVY)
ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
# subtle grid
for x in range(0,W,60*S): d.line([(x,0),(x,H)],fill=(255,255,255,9),width=S)
for y in range(0,H,60*S): d.line([(0,y),(W,y)],fill=(255,255,255,9),width=S)
# sparse network nodes, kept away from the central text block
random.seed(7); pts=[]
while len(pts)<46:
    x,y=random.uniform(0,W),random.uniform(0,H)
    if 300*S<x<1200*S and 50*S<y<450*S: continue
    pts.append((x,y))
for i,a in enumerate(pts):
    for b in pts[i+1:]:
        dist=math.dist(a,b)
        if dist<170*S: d.line([a,b],fill=CYAN+(int(55*(1-dist/(170*S))),),width=S)
for (x,y) in pts:
    r=random.choice([2,3,3,4])*S
    d.ellipse([x-r,y-r,x+r,y+r],fill=CYAN+(110,))
img=Image.alpha_composite(img.convert("RGBA"),ov)
d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f1=ImageFont.truetype(B,64*S); f3=ImageFont.truetype(R,30*S)
cx=W//2
def ctext(y,txt,font,fill):
    w=d.textlength(txt,font=font); d.text((cx-w/2,y),txt,font=font,fill=fill)
# "U51" (U white, 51 cyan), rule, show name, tagline
fb=ImageFont.truetype(B,150*S); f2=ImageFont.truetype(B,40*S)
a,b="U","51"
wa,wb=d.textlength(a,font=fb),d.textlength(b,font=fb); x0=cx-(wa+wb)/2; y0=78*S-d.textbbox((0,0),a,font=fb)[1]
d.text((x0,y0),a,font=fb,fill=WHITE); d.text((x0+wa,y0),b,font=fb,fill=CYAN)
d.line([(cx-300*S,262*S),(cx+300*S,262*S)],fill=CYAN,width=3*S)
ctext(282*S,"Cyber and AI Security Pod",f2,WHITE)
ctext(342*S,"The daily cyber and AI threat brief, from Melbourne",f3,GREY)
img.convert("RGB").resize((1500,500),Image.LANCZOS).save("/workspace/podcast/x_banner.png",optimize=True)
print("ok")
