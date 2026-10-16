#!/usr/bin/env bash
# Usage: publish.sh <script.txt> "<episode title>" <shownotes.md|.html>   (NO_PUSH=1 to build locally only)
set -euo pipefail
D=/workspace/podcast; SITE=${SITE_DIR:-$D/site}
BASE=${BASE_URL:-https://ajith-at.github.io/cyber-daily-australia}
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
import sys,json,os,glob,email.utils,html,time
site,slug,title,dur,summ,base,notesf=sys.argv[1:]
import re
notes=open(notesf).read()
e=html.escape
open(f"{site}/episodes/{slug}.html","w").write(f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>{e(title)}</title><body style='font-family:sans-serif;max-width:760px;margin:auto;padding:1em'><p><a href='../index.html'>Cyber Daily Australia</a></p><h1>{e(title)}</h1><audio controls src='{slug}.mp3'></audio>{notes}</body>")
plain=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",notes)).strip()
mp3=f"{site}/episodes/{slug}.mp3"
json.dump({"title":title,"slug":slug,"dur":int(float(dur)),"size":os.path.getsize(mp3),
 "notes":notes,"plain":plain,"date":email.utils.formatdate(time.time(),localtime=True),"summary":summ},open(f"{site}/episodes/{slug}.json","w"))
eps=sorted((json.load(open(f)) for f in glob.glob(f"{site}/episodes/*.json") if os.path.exists(f[:-5]+".mp3")),key=lambda e:e["slug"],reverse=True)
items=""
for x in eps:
    d=x["dur"]; items+=f"""  <item>
    <title>{e(x['title'])}</title>
    {('<link>'+base+'/episodes/'+x['slug']+'.html</link>') if x.get('notes') else ''}
    <description>{e(x.get('plain') or x['summary'])}</description>
    {('<content:encoded><![CDATA['+x['notes'].replace(']]>',']]&gt;')+'<p><a href="'+base+'/episodes/'+x['slug']+'.html">Show notes page</a></p>]]></content:encoded>') if x.get('notes') else ''}
    <pubDate>{x['date']}</pubDate>
    <guid isPermaLink="false">cyber-daily-australia-{x['slug']}</guid>
    <enclosure url="{base}/episodes/{x['slug']}.mp3" length="{x['size']}" type="audio/mpeg"/>
    <itunes:duration>{d//3600:02d}:{d%3600//60:02d}:{d%60:02d}</itunes:duration>
    <itunes:episodeType>full</itunes:episodeType>
    <itunes:explicit>false</itunes:explicit>
  </item>
"""
t=open("/workspace/podcast/feed_template.xml").read()
t=t.replace("{{SHOW_TITLE}}","Cyber Daily Australia").replace("{{SITE_URL}}",base).replace("  <!-- ITEMS -->\n",items)
open(f"{site}/feed.xml","w").write(t)
PY
touch "$SITE/.nojekyll"
python3 - "$SITE" <<'PY2'
import json,glob,html
site=__import__("sys").argv[1]
eps=sorted((json.load(open(f)) for f in glob.glob(site+"/episodes/*.json")),key=lambda e:e["slug"],reverse=True)
li="".join(f"<li><a href='episodes/{x['slug']}.html'>{html.escape(x['title'])}</a></li>" if x.get("notes") else f"<li><a href='episodes/{x['slug']}.mp3'>{html.escape(x['title'])}</a></li>" for x in eps)
open(site+"/index.html","w").write(f"<!doctype html><meta charset=utf-8><title>Cyber Daily Australia</title><h1>Cyber Daily Australia</h1><p>Daily cybersecurity SITREP podcast. <a href='feed.xml'>RSS feed</a></p><ul>{li}</ul>")
PY2
true ||  printf '<!doctype html><title>Cyber Daily Australia</title><h1>Cyber Daily Australia</h1><p>Daily cybersecurity SITREP podcast. <a href="feed.xml">RSS feed</a></p>\n' > "$SITE/index.html"
echo "Built $OUT ($DUR s)"
if [ "${NO_PUSH:-0}" != 1 ]; then
  cd "$SITE" && git add -A && git commit -qm "Episode $SLUG: $TITLE" && git push -q
  echo "Published $BASE/episodes/$SLUG.mp3"
fi
