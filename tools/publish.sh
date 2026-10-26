#!/usr/bin/env bash
# U51 Cyber and AI Security Botcast
# Usage: publish.sh <script.txt> "<episode title>" <shownotes.md|.html>   (NO_PUSH=1 to build locally only)
set -euo pipefail
D=/workspace/podcast; SITE=${SITE_DIR:-$D/site}
BASE=${BASE_URL:-https://u51.org}   # custom domain (site/CNAME). Old github.io feed URL 301-redirects here; keep the repo name and CNAME. Show name/handle/cover live in brand.py
VOICE=${VOICE:-en-AU-WilliamMultilingualNeural}
SCRIPT=$1; TITLE=$2; NOTES=${3:?show notes file required}; DATE=$(date +%Y-%m-%d); SLUG="$DATE-$(date +%H%M)"
mkdir -p "$SITE/episodes" "$D/build"
RAW=$D/build/$SLUG-raw.mp3; OUT=$SITE/episodes/$SLUG.mp3
"$D/venv/bin/edge-tts" --voice "$VOICE" --rate=-5% -f "$SCRIPT" --write-media "$RAW"
ffmpeg -v error -y -i "$RAW" -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 44100 -ac 1 -b:a 96k "$OUT"
cp "$SCRIPT" "$SITE/episodes/$SLUG.txt"
# Sunday Special artwork (make_special_thumb.py): becomes the episode image on the site and in the feed
IMG=""; if [ -f "$D/specials/$DATE/thumb.jpg" ]; then cp "$D/specials/$DATE/thumb.jpg" "$SITE/episodes/$SLUG.jpg"; IMG="$SLUG.jpg"; fi
case "$NOTES" in *.md|*.markdown) "$D/venv/bin/python" -c "import sys,markdown;print(markdown.markdown(open(sys.argv[1]).read()))" "$NOTES" > "$D/build/$SLUG-notes.html";; *) cp "$NOTES" "$D/build/$SLUG-notes.html";; esac
# no retention step: every episode is kept forever (feed and archive list them all)
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
SUMMARY=$(head -c 400 "$SCRIPT" | tr '\n' ' ')
python3 - "$SITE" "$SLUG" "$TITLE" "$DUR" "$SUMMARY" "$BASE" "$D/build/$SLUG-notes.html" "$IMG" <<'PY'
import sys,json,os,email.utils,html,time,re
sys.path.insert(0,"/workspace/podcast"); import brand as B
site,slug,title,dur,summ,base,notesf,img=sys.argv[1:]
notes=open(notesf).read(); e=html.escape
# the notes page (episodes/<slug>.html) is rendered in full from this JSON by build_site.py (Soft Indigo Desk layout)
plain=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",notes)).strip()
mp3=f"{site}/episodes/{slug}.mp3"
json.dump({"title":title,"slug":slug,"dur":int(float(dur)),"size":os.path.getsize(mp3),
 "notes":notes,"plain":plain,"date":email.utils.formatdate(time.time(),localtime=True),"summary":summ,**({"image":img} if img else {})},open(f"{site}/episodes/{slug}.json","w"))
PY
# feed.xml, index.html, every notes page and site/assets/ (branding in brand.py, styles in assets_src/)
python3 "$D/build_site.py" "$SITE"
touch "$SITE/.nojekyll"
echo "Built $OUT ($DUR s)"
"$D/venv/bin/python" "$D/x/make_post.py" "$SLUG" || echo "WARN: X post not generated"
if [ "${NO_PUSH:-0}" != 1 ]; then
  cd "$SITE" && git add -A && git commit -qm "Episode $SLUG: $TITLE" && git pull --rebase -q && git push -q
  echo "Published $BASE/episodes/$SLUG.mp3"
  P=/workspace/podcast; [ -f "$SITE/episodes/$SLUG.html" ] && "$P/notion/prep_notion_page.sh" "$SLUG" && echo "NOTION: create child page under 3fb48c8e1a2f81449abfdc1ac14526ce with content $P/notion/$SLUG.md (see STYLE.md)" || true
fi
