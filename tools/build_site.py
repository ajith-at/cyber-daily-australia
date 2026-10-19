#!/usr/bin/env python3
"""Rebuild feed.xml and index.html from site/episodes/*.json, and refresh the nav bar on every notes page.
Usage: python3 build_site.py [SITE_DIR]. Called by publish.sh; safe to run on its own after branding changes."""
import sys, json, glob, os, re, html
sys.path.insert(0, "/workspace/podcast"); import brand as B
site = sys.argv[1] if len(sys.argv) > 1 else "/workspace/podcast/site"
base = os.environ.get("BASE_URL", B.BASE); e = html.escape
NAV = f"<p><a href='../index.html'>{B.SHOW}</a> | <a href='{B.X_URL}'>Follow on X (@{B.X_HANDLE})</a></p>"
DESC = (f"{B.SHOW}: {B.SUBTITLE[0].lower() + B.SUBTITLE[1:]}. A short daily executive briefing on the cyber threats, "
        f"vulnerabilities and AI security developments that matter, with an Australian lens. Open sources only. "
        f"Formerly {B.FORMERLY}. Follow on X: @{B.X_HANDLE} ({B.X_URL})")
FOOT = f'<a href="{B.X_URL}">Follow on X (@{B.X_HANDLE})</a>'
# refresh the nav bar on existing notes pages (first <p> after <body ...>)
for f in glob.glob(f"{site}/episodes/*.html"):
    s = open(f).read(); n = re.sub(r"(<body[^>]*>)<p>.*?</p>", lambda m: m.group(1) + NAV, s, count=1, flags=re.S)
    if n != s: open(f, "w").write(n)
eps = sorted((json.load(open(f)) for f in glob.glob(f"{site}/episodes/*.json") if os.path.exists(f[:-5] + ".mp3")), key=lambda x: x["slug"], reverse=True)
items = ""
for x in eps:
    d = x["dur"]; notes = x.get("notes")
    link = f"<link>{base}/episodes/{x['slug']}.html</link>" if notes else ""
    enc = ("<content:encoded><![CDATA[" + notes.replace("]]>", "]]&gt;") + f'<p><a href="{base}/episodes/{x["slug"]}.html">Show notes page</a> | {FOOT}</p>]]></content:encoded>') if notes else ""
    items += f"""  <item>
    <title>{e(x['title'])}</title>
    {link}
    <description>{e(x.get('plain') or x['summary'])}</description>
    {enc}
    <pubDate>{x['date']}</pubDate>
    <guid isPermaLink="false">cyber-daily-australia-{x['slug']}</guid>
    <enclosure url="{base}/episodes/{x['slug']}.mp3" length="{x['size']}" type="audio/mpeg"/>
    <itunes:duration>{d//3600:02d}:{d%3600//60:02d}:{d%60:02d}</itunes:duration>
    <itunes:episodeType>full</itunes:episodeType>
    <itunes:explicit>false</itunes:explicit>
  </item>
"""
# NB: guid prefix "cyber-daily-australia-" is intentionally unchanged so podcast apps don't see old episodes as new.
t = open("/workspace/podcast/feed_template.xml").read()
for k, v in {"SHOW_TITLE": e(B.SHOW), "SITE_URL": base, "DESCRIPTION": e(DESC), "SUBTITLE": e(B.SUBTITLE),
             "KEYWORDS": e(B.KEYWORDS), "OWNER_EMAIL": B.OWNER_EMAIL, "COVER": B.COVER}.items():
    t = t.replace("{{" + k + "}}", v)
t = t.replace("  <!-- ITEMS -->\n", items)
open(f"{site}/feed.xml", "w").write(t)
li = "".join(f"<li><a href='episodes/{x['slug']}.html'>{e(x['title'])}</a></li>" if x.get("notes") else f"<li><a href='episodes/{x['slug']}.mp3'>{e(x['title'])}</a></li>" for x in eps)
open(f"{site}/index.html", "w").write(
    f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>{B.SHOW}</title>"
    f"<body style='font-family:sans-serif;max-width:760px;margin:auto;padding:1em'>"
    f"<img src='{B.COVER}' alt='{B.SHOW} cover art' width=160 height=160 style='float:right;margin:0 0 1em 1em'>"
    f"<h1>{B.SHOW}</h1><p>{B.SUBTITLE}. <a href='feed.xml'>RSS feed</a> | <a href='{B.X_URL}'>Follow on X (@{B.X_HANDLE})</a></p>"
    f"<p><small>Formerly {B.FORMERLY}.</small></p><ul>{li}</ul></body>")
print(f"built feed.xml ({len(eps)} episodes) and index.html")
