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
# Shared <head> extras (favicon, social preview) and a logo header, injected idempotently between marker comments.
LOGO = "img/u51-logo-600.jpg"; OG = f"{base}/img/u51-og-1200.jpg"
def head(title, desc, url, rel):
    return ("<!--u51head-->"
            f"<link rel=icon href='{rel}favicon.ico' sizes=any><link rel=icon type=image/png href='{rel}img/favicon-32.png'>"
            f"<link rel=apple-touch-icon href='{rel}img/apple-touch-icon.png'>"
            f"<meta property='og:site_name' content='{e(B.SHOW)}'><meta property='og:title' content='{e(title)}'>"
            f"<meta property='og:description' content='{e(desc)}'><meta property='og:type' content='website'><meta property='og:url' content='{url}'>"
            f"<meta property='og:image' content='{OG}'><meta property='og:image:width' content='1200'><meta property='og:image:height' content='1200'>"
            f"<meta name='twitter:card' content='summary'><meta name='twitter:site' content='@{B.X_HANDLE}'><meta name='twitter:image' content='{OG}'>"
            "<!--/u51head-->")
# Listen buttons (only platforms with a confirmed URL in brand.py are shown)
ICON = {
 "Spotify": "<svg viewBox='0 0 24 24' width='{s}' height='{s}' aria-hidden='true'><circle cx='12' cy='12' r='12' fill='#1DB954'/><path d='M6.5 9.3c3.8-1.1 8-.8 11.2 1.1M7.2 12.4c3.1-.9 6.6-.6 9.3.9M7.9 15.3c2.5-.7 5.2-.5 7.3.7' stroke='#000' stroke-width='1.7' stroke-linecap='round' fill='none'/></svg>",
 "Apple Podcasts": "<svg viewBox='0 0 24 24' width='{s}' height='{s}' aria-hidden='true'><rect width='24' height='24' rx='5.5' fill='#9933CC'/><circle cx='12' cy='10.2' r='2.1' fill='#fff'/><path d='M10.6 13.6h2.8l-.5 5.6h-1.8z' fill='#fff'/><path d='M8 15.6a5.8 5.8 0 1 1 8 0' stroke='#fff' stroke-width='1.5' fill='none' stroke-linecap='round'/></svg>",
 "Pocket Casts": "<svg viewBox='0 0 24 24' width='{s}' height='{s}' aria-hidden='true'><circle cx='12' cy='12' r='12' fill='#F43E37'/><path d='M12 5.2a6.8 6.8 0 1 0 6.8 6.8h-2.2A4.6 4.6 0 1 1 12 7.4z' fill='#fff'/><path d='M12 9.2a2.8 2.8 0 1 0 2.8 2.8h-1.3A1.5 1.5 0 1 1 12 10.5z' fill='#fff'/></svg>",
}
LISTEN = [(n, u) for n, u in (("Spotify", getattr(B, "SPOTIFY_URL", None)), ("Apple Podcasts", getattr(B, "APPLE_URL", None)), ("Pocket Casts", getattr(B, "POCKETCASTS_URL", None))) if u]
def listen_row(big=True):
    sz = 22 if big else 16
    st = ("display:inline-flex;align-items:center;gap:8px;padding:8px 14px;border:1px solid #ccd;border-radius:22px;text-decoration:none;color:#111;font-weight:600;background:#f7f8fb"
          if big else "display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border:1px solid #ccd;border-radius:14px;text-decoration:none;color:#111;font-size:.85em;background:#f7f8fb")
    btn = "".join(f"<a href='{u}' target='_blank' rel='noopener' style='{st}' aria-label='Listen on {n}'>{ICON[n].replace('{s}', str(sz))}<span>{n}</span></a>" for n, u in LISTEN)
    return f"<div class='u51-listen' style='display:flex;flex-wrap:wrap;gap:{10 if big else 6}px;margin:{'.8em 0' if big else '.4em 0 0'}'>{btn}</div>" if LISTEN else ""
STRIP = re.compile(r"<!--u51(head|hdr)-->.*?<!--/u51\1-->", re.S)
HDR = (f"<!--u51hdr--><header style='display:flex;align-items:center;gap:14px;margin:0 0 .5em'>"
       f"<a href='../index.html'><img src='../{LOGO}' alt='{B.SHOW} logo' width=96 height=96 style='border-radius:50%;display:block'></a>"
       f"<div><a href='../index.html' style='font-weight:bold;font-size:1.15em;color:inherit;text-decoration:none'>{B.SHOW}</a><br>"
       f"<small>{B.SUBTITLE}</small> | <a href='{B.X_URL}'>Follow on X (@{B.X_HANDLE})</a>" + listen_row(False) + "</div></header><!--/u51hdr-->")
for f in glob.glob(f"{site}/episodes/*.html"):
    s0 = open(f).read(); s1 = STRIP.sub("", s0)
    # drop the old one-line nav bar (first <p> after <body>) if it is the show/X nav
    s1 = re.sub(r"(<body[^>]*>)<p><a href='../index.html'>.*?</p>", r"\1", s1, count=1, flags=re.S)
    t = re.search(r"<title>(.*?)</title>", s1, re.S); t = html.unescape(t.group(1)) if t else B.SHOW
    stem = os.path.basename(f)
    s1 = s1.replace("</title>", "</title>" + head(t, f"{B.SHOW}: {B.SUBTITLE}.", f"{base}/episodes/{stem}", "../"), 1)
    s1 = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + HDR, s1, count=1)
    if s1 != s0: open(f, "w").write(s1)
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
    + head(B.SHOW, f"{B.SHOW}: {B.SUBTITLE}.", f"{base}/", "")
    + f"<meta name=description content='{e(B.SHOW)}: {e(B.SUBTITLE)}.'>"
    f"<body style='font-family:sans-serif;max-width:900px;margin:auto;padding:1em;background:#fff'>"
    f"<a href='./'><img src='img/u51-banner-1500.jpg' alt='{B.SHORT} banner' width=1500 height=500 style='width:100%;height:auto;display:block;border-radius:8px'></a>"
    f"<div style='display:flex;align-items:center;gap:20px;margin:1em 0;flex-wrap:wrap'>"
    f"<img src='{LOGO}' alt='{B.SHOW} logo' width=200 height=200 style='border-radius:50%'>"
    f"<div><h1 style='margin:0 0 .3em'>{B.SHOW}</h1><p style='margin:0'>{B.SUBTITLE}. <a href='feed.xml'>RSS feed</a> | <a href='{B.X_URL}'>Follow on X (@{B.X_HANDLE})</a></p>"
    + listen_row(True) + f"<p style='margin:.4em 0 0'><small>Formerly {B.FORMERLY}.</small></p></div></div>"
    f"<h2>Episodes</h2><ul>{li}</ul></body>")
print(f"built feed.xml ({len(eps)} episodes) and index.html")
