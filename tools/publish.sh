#!/usr/bin/env bash
# U51 Cyber and AI Security Pod (formerly Cyber Daily Australia)
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
case "$NOTES" in *.md|*.markdown) "$D/venv/bin/python" -c "import sys,markdown;print(markdown.markdown(open(sys.argv[1]).read()))" "$NOTES" > "$D/build/$SLUG-notes.html";; *) cp "$NOTES" "$D/build/$SLUG-notes.html";; esac
# retention: delete episodes older than 90 days
find "$SITE/episodes" -type f \( -name '*.mp3' -o -name '*.txt' -o -name '*.json' -o -name '*.html' \) -mtime +90 -delete
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
SUMMARY=$(head -c 400 "$SCRIPT" | tr '\n' ' ')
python3 - "$SITE" "$SLUG" "$TITLE" "$DUR" "$SUMMARY" "$BASE" "$D/build/$SLUG-notes.html" <<'PY'
import sys,json,os,email.utils,html,time,re
sys.path.insert(0,"/workspace/podcast"); import brand as B
site,slug,title,dur,summ,base,notesf=sys.argv[1:]
notes=open(notesf).read(); e=html.escape
open(f"{site}/episodes/{slug}.html","w").write(f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>{e(title)}</title><body style='font-family:sans-serif;max-width:760px;margin:auto;padding:1em'><p><a href='../index.html'>{B.SHOW}</a> | <a href='{B.X_URL}'>Follow on X (@{B.X_HANDLE})</a></p><h1>{e(title)}</h1><audio controls src='{slug}.mp3'></audio>{notes}</body>")
plain=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",notes)).strip()
mp3=f"{site}/episodes/{slug}.mp3"
json.dump({"title":title,"slug":slug,"dur":int(float(dur)),"size":os.path.getsize(mp3),
 "notes":notes,"plain":plain,"date":email.utils.formatdate(time.time(),localtime=True),"summary":summ},open(f"{site}/episodes/{slug}.json","w"))
PY
# feed.xml, index.html and notes-page nav bars (branding lives in brand.py)
python3 "$D/build_site.py" "$SITE"
touch "$SITE/.nojekyll"
echo "Built $OUT ($DUR s)"
"$D/venv/bin/python" "$D/x/make_post.py" "$SLUG" || echo "WARN: X post not generated"
if [ "${NO_PUSH:-0}" != 1 ]; then
  cd "$SITE" && git add -A && git commit -qm "Episode $SLUG: $TITLE" && git push -q
  echo "Published $BASE/episodes/$SLUG.mp3"
  P=/workspace/podcast; [ -f "$SITE/episodes/$SLUG.html" ] && "$P/notion/prep_notion_page.sh" "$SLUG" && echo "NOTION: create child page under 3fb48c8e1a2f81449abfdc1ac14526ce with content $P/notion/$SLUG.md (see STYLE.md)" || true
fi
