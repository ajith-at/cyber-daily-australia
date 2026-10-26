#!/usr/bin/env python3
"""Rebuild feed.xml, index.html and every episode notes page from site/episodes/*.json, and copy the site stylesheet and scripts.
Usage: python3 build_site.py [SITE_DIR]. Called by publish.sh; safe to run on its own after branding or style changes.
Style: 'Soft Indigo Desk' (brief: /workspace/shared/style/soft-indigo-desk.md), matching the Cyber Toolkit at /toolkit/.
Stylesheet and scripts live in /workspace/podcast/assets_src/ and are copied to site/assets/ (never link to /toolkit/ assets:
the toolkit deploy replaces that folder). Episode pages are rendered in full from their JSON, so the layout survives every publish.
No episode is ever trimmed by age or count: the feed lists every episode; the homepage shows the latest 8 as cards and the rest in an Archive."""
import sys, json, glob, os, re, html, shutil, email.utils, time
sys.path.insert(0, "/workspace/podcast"); import brand as B
site = sys.argv[1] if len(sys.argv) > 1 else "/workspace/podcast/site"
base = os.environ.get("BASE_URL", B.BASE); e = html.escape
ASSETS_SRC = os.environ.get("ASSETS_SRC", "/workspace/podcast/assets_src")
LATEST_N = 8    # full episode cards on the homepage; older episodes go to the Archive (grouped by month)
DESC = f"{B.DESCRIPTION} Follow on X: @{B.X_HANDLE} ({B.X_URL})"   # feed channel description and itunes:summary
FOOT = f'<a href="{B.X_URL}">Follow on X (@{B.X_HANDLE})</a>'
LOGO = "img/u51-logo-600.jpg"; LOGO_SM = "img/u51-logo-160.jpg"; OG = f"{base}/img/u51-og-1200.jpg"
def head(title, desc, url, rel):
    return ("<!--u51head-->"
            f"<link rel=icon href='{rel}favicon.ico' sizes=any><link rel=icon type=image/png href='{rel}img/favicon-32.png'>"
            f"<link rel=apple-touch-icon href='{rel}img/apple-touch-icon.png'>"
            f"<meta property='og:site_name' content='{e(B.SHOW)}'><meta property='og:title' content='{e(title)}'>"
            f"<meta property='og:description' content='{e(desc)}'><meta property='og:type' content='website'><meta property='og:url' content='{url}'>"
            f"<meta property='og:image' content='{OG}'><meta property='og:image:width' content='1200'><meta property='og:image:height' content='1200'>"
            f"<meta name='twitter:card' content='summary'><meta name='twitter:site' content='@{B.X_HANDLE}'><meta name='twitter:image' content='{OG}'>"
            "<!--/u51head-->")

# Outline icons from Lucide (https://lucide.dev, lucide-static 1.60.0), ISC licence. Inner SVG markup only.
ICONS = {
 "archive": '<rect width="20" height="5" x="2" y="3" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/>',
 "arrow-left": '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
 "at-sign": '<circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"/>',
 "audio-lines": '<path d="M2 10v3"/><path d="M6 6v11"/><path d="M10 3v18"/><path d="M14 8v7"/><path d="M18 5v13"/><path d="M22 10v3"/>',
 "calendar": '<path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/>',
 "chevron-left": '<path d="m15 18-6-6 6-6"/>',
 "chevron-right": '<path d="m9 18 6-6-6-6"/>',
 "circle-play": '<path d="M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z"/><circle cx="12" cy="12" r="10"/>',
 "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "external-link": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
 "file-text": '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
 "headphones": '<path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/>',
 "list-music": '<path d="M16 5H3"/><path d="M11 12H3"/><path d="M11 19H3"/><path d="M21 16V5"/><circle cx="18" cy="16" r="3"/>',
 "moon": '<path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401"/>',
 "podcast": '<path d="M12 17v4"/><path d="M18 11a6 6 0 00-3-5.197"/><path d="M2 11a10 10 0 015-8.662"/><path d="M22 11a10 10 0 00-5-8.662"/><path d="M6 11a6 6 0 013-5.197"/><path d="M9 21h6"/><rect x="10" y="9" width="4" height="8" rx="2"/>',
 "rss": '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
 "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.106-3.105c.32-.322.863-.22.983.218a6 6 0 0 1-8.259 7.057l-7.91 7.91a1 1 0 0 1-2.999-3l7.91-7.91a6 6 0 0 1 7.057-8.259c.438.12.54.662.219.984z"/>',
}
def icon(name, size=18, cls=""):
    return (f"<svg class='icon {cls}' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' "
            f"stroke-linecap='round' stroke-linejoin='round' aria-hidden='true' focusable='false'>{ICONS[name]}</svg>")

# Listen links (only platforms with a confirmed URL in brand.py are shown). Spotify is the primary (indigo) button.
LISTEN = [(n, u, i) for n, u, i in (("Spotify", getattr(B, "SPOTIFY_URL", None), "headphones"),
                                    ("Apple Podcasts", getattr(B, "APPLE_URL", None), "podcast"),
                                    ("Pocket Casts", getattr(B, "POCKETCASTS_URL", None), "circle-play")) if u]
def listen_row(rel, extra=True, small=False):
    sm = " btn-sm" if small else ""
    out = "".join(f"<a class='btn {'btn-primary' if k == 0 else 'btn-secondary'}{sm}' href='{u}' target='_blank' rel='noopener' aria-label='Listen on {n}'>{icon(i)}<span>{n}</span></a>"
                  for k, (n, u, i) in enumerate(LISTEN))
    if extra:
        out += (f"<a class='btn btn-secondary{sm}' href='{rel}feed.xml'>{icon('rss')}<span>RSS feed</span></a>"
                f"<a class='btn btn-secondary{sm}' href='{B.X_URL}' target='_blank' rel='noopener'>{icon('at-sign')}<span>Follow on X (@{B.X_HANDLE})</span></a>")
    return f"<div class='btn-row u51-listen'>{out}</div>"

def when(x):
    """(datetime-ish tuple) from the RFC 2822 date in the episode JSON, falling back to the slug."""
    try: return email.utils.parsedate_to_datetime(x["date"])
    except Exception:
        import datetime; return datetime.datetime.strptime(x["slug"][:10], "%Y-%m-%d")
def fmt_date(x, short=False):
    d = when(x); return d.strftime("%a %-d %b %Y") if not short else d.strftime("%a %-d %b")
def fmt_dur(s): s = int(s); return f"{s//3600}:{s%3600//60:02d}:{s%60:02d}" if s >= 3600 else f"{s//60}:{s%60:02d}"
def split_title(t, x=None):
    """'Episode 6: Topic, 21 October 2026' -> ('Episode 6', 'Topic'). The number comes from the JSON 'episode' field if set,
    else from 'Episode N' anywhere in the title. Sunday Specials are numbered like any other episode (25 Oct 2026 = Episode 10)."""
    n = (x or {}).get("episode")
    m = re.search(r"\bEpisode\s+(\d+)", t)
    if n is None and m: n = int(m.group(1))
    rest = re.sub(r"^\s*Episode\s+\d+\s*[:\u2014\u2013-]\s*", "", t)
    rest = re.sub(r"\s*[,\u2014\u2013-]\s*\d{1,2} [A-Z][a-z]+ \d{4}\s*$", "", rest).strip()
    return (f"Episode {n}" if n is not None else "Episode"), rest
def is_special(x): return bool(re.search(r"sunday special", x["title"], re.I)) or x.get("special") is True
def ep_href(x, rel): return f"{rel}episodes/{x['slug']}.html" if x.get("notes") else f"{rel}episodes/{x['slug']}.mp3"

def shell(*, title, rel, active, desc, url, toolbar, body, chips_extra=(), cal_current=""):
    """Full page: rounded shell, indigo rail, sticky toolbar, content column. rel is '' for the root, '../' for /episodes/."""
    nav = [("episodes", "Episodes", f"{rel}index.html", "audio-lines", False)]
    nav += [(k, n, h, i, False) for k, n, h, i in chips_extra]
    nav += [("toolkit", "Toolkit", f"{rel}toolkit/", "wrench", False),
            ("feed", "Feed (RSS)", f"{rel}feed.xml", "rss", False),
            ("x", f"Follow on X", B.X_URL, "at-sign", True)]
    def item(k, n, h, i, ext, cls):
        a = " aria-current='page'" if k == active else ""
        act = " active" if k == active else ""
        tgt = " target='_blank' rel='noopener'" if ext else ""
        return f"<a class='{cls}{act}' href='{h}'{a}{tgt}>{icon(i)}<span>{n}</span></a>"
    rail_nav = "".join(f"<li>{item(*n, 'nav-item')}</li>" for n in nav)
    listen_nav = "".join(f"<li><a class='nav-item' href='{u}' target='_blank' rel='noopener'>{icon(i)}<span>{n}</span></a></li>" for n, u, i in LISTEN)
    cal_href = "#calendar" if rel == "" else f"{rel}index.html#calendar"
    chips = "".join(item(*n, "chip") for n in nav[:1]) + f"<a class='chip js-only' href='{cal_href}'>{icon('calendar', 16)}<span>Calendar</span></a>" + "".join(item(*n, "chip") for n in nav[1:]) + "".join(f"<a class='chip' href='{u}' target='_blank' rel='noopener'>{icon(i, 16)}<span>{n}</span></a>" for n, u, i in LISTEN)
    switch_rail = (f"<button type='button' class='switch switch-rail' role='switch' aria-checked='false' data-theme-toggle>"
                   f"{icon('sun', 18, 'i-sun')}{icon('moon', 18, 'i-moon')}<span class='switch-label'>Dark mode</span><span class='track'><span class='knob'></span></span></button>")
    switch_compact = (f"<button type='button' class='switch switch-compact' role='switch' aria-checked='false' aria-label='Dark mode' data-theme-toggle>"
                      f"{icon('sun', 18, 'i-sun')}{icon('moon', 18, 'i-moon')}<span class='track'><span class='knob'></span></span></button>")
    return (
        "<!doctype html>\n<html lang=en-AU class=no-js><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width, initial-scale=1'>"
        f"<title>{e(title)}</title>" + head(title, desc, url, rel) +
        f"<meta name=description content='{e(desc)}'>"
        f"<link rel=alternate type=application/rss+xml title='{e(B.SHOW)}' href='{base}/feed.xml'>"
        "<link rel=preconnect href='https://fonts.googleapis.com'><link rel=preconnect href='https://fonts.gstatic.com' crossorigin>"
        "<link rel=stylesheet href='https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap'>"
        f"<link rel=stylesheet href='{rel}assets/site.css'><script src='{rel}assets/theme-init.js'></script>"
        f"<script src='{rel}assets/site.js' defer></script>"
        f"<script src='{rel}assets/episodes.js' defer></script><script src='{rel}assets/calendar.js' defer></script></head>\n<body>"
        "<a class=skip href='#content'>Skip to content</a><div class=shell>"
        f"<aside class=rail aria-label='Site'>"
        f"<a class=wordmark href='{rel}index.html'><img src='{rel}{LOGO_SM}' alt='' width=160 height=160><span><strong>{B.SHORT}</strong><small>{e(B.SHOW[len(B.SHORT):].strip())}</small></span></a>"
        f"<nav aria-label='Main'><ul class=nav>{rail_nav}</ul></nav>"
        f"<nav aria-label='Listen'><p class=nav-label>Listen</p><ul class=nav>{listen_nav}</ul></nav>"
        f"<section class='cal cal-rail js-only' data-cal data-root='{rel}' data-current='{cal_current}' aria-label='Episode calendar'></section>"
        f"<div class=rail-foot>{switch_rail}</div></aside>"
        "<main class=main>"
        f"<header class=toolbar><div class=toolbar-row>"
        f"<a class=mobile-mark href='{rel}index.html'><img src='{rel}{LOGO_SM}' alt='' width=160 height=160><span>{B.SHORT}</span></a>"
        f"<div class=toolbar-title>{toolbar}</div>{switch_compact}</div>"
        f"<nav class=chips aria-label='Sections'>{chips}</nav></header>"
        f"<div class=content id=content tabindex=-1>{body}"
        f"<footer class=site-foot>{B.SHOW}. Researched, written and voiced by AI agents under human editorial direction. Not for profit, open sources only. "
        f"<a href='{rel}feed.xml'>RSS</a> · <a href='{B.X_URL}'>@{B.X_HANDLE}</a></footer>"
        "</div></main></div></body></html>\n")

def write_if_changed(path, s):
    if not os.path.exists(path) or open(path).read() != s: open(path, "w").write(s)

# ---------- assets ----------
os.makedirs(f"{site}/assets", exist_ok=True)
for n in ("site.css", "theme-init.js", "site.js", "calendar.js"):
    write_if_changed(f"{site}/assets/{n}", open(f"{ASSETS_SRC}/{n}").read())

# ---------- feed (unchanged format: lists every episode, no cap) ----------
eps = sorted((json.load(open(f)) for f in glob.glob(f"{site}/episodes/*.json") if os.path.exists(f[:-5] + ".mp3")), key=lambda x: x["slug"], reverse=True)
def img_tag(x): return f'    <itunes:image href="{base}/episodes/{x["image"]}"/>\n' if x.get("image") else ""
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
{img_tag(x)}  </item>
"""
# NB: guid prefix "cyber-daily-australia-" is intentionally unchanged so podcast apps don't see old episodes as new.
t = open("/workspace/podcast/feed_template.xml").read()
for k, v in {"SHOW_TITLE": e(B.SHOW), "SITE_URL": base, "DESCRIPTION": e(DESC), "SUBTITLE": e(B.FEED_SUBTITLE),
             "KEYWORDS": e(B.KEYWORDS), "OWNER_EMAIL": B.OWNER_EMAIL, "COVER": B.COVER}.items():
    t = t.replace("{{" + k + "}}", v)
t = t.replace("  <!-- ITEMS -->\n", items)
open(f"{site}/feed.xml", "w").write(t)

# ---------- episode artwork (Sunday Specials): a 600px web copy of episodes/<slug>.jpg for the site ----------
def thumb(x):
    """Relative (to /episodes/) name of a web-sized copy of the episode image, or None. The full image stays for the feed."""
    img = x.get("image")
    if not img or not os.path.exists(f"{site}/episodes/{img}"): return None
    small = re.sub(r"\.(jpe?g|png)$", "", img) + "-600.jpg"
    if not os.path.exists(f"{site}/episodes/{small}"):
        try:
            from PIL import Image
            Image.open(f"{site}/episodes/{img}").convert("RGB").resize((600, 600), Image.LANCZOS).save(f"{site}/episodes/{small}", quality=85, optimize=True, progressive=True)
        except Exception as ex:
            print("WARN: thumbnail resize failed, using full image:", ex); return img
    return small

# ---------- calendar data (assets/episodes.js, read by assets/calendar.js; oldest first, Melbourne dates) ----------
cal = [{"d": when(x).strftime("%Y-%m-%d"), "n": split_title(x["title"], x)[0], "t": x["title"], "u": ep_href(x, "")} for x in reversed(eps)]
write_if_changed(f"{site}/assets/episodes.js", "window.U51_EPISODES = " + json.dumps(cal, ensure_ascii=False, separators=(",", ":")) + ";\n")

# ---------- episode notes pages (rendered in full from JSON; written only when the content changes) ----------
for x in eps:
    if not x.get("notes"): continue
    label, short = split_title(x["title"], x)
    th = thumb(x)
    art = f"<img class=ep-art src='{th}' alt='{e(label)} artwork' width=600 height=600>" if th else ""
    body = (f"<section class='card ep-head{' has-art' if th else ''}'>{art}<a class=back href='../index.html'>{icon('arrow-left', 16)}All episodes</a>"
            f"<div class=ep-meta><span>{label}</span><span>{icon('calendar', 16)}<time datetime='{when(x).isoformat()}'>{fmt_date(x)}</time></span>"
            f"<span>{icon('clock', 16)}<span class=dur>{fmt_dur(x['dur'])}</span></span></div>"
            f"<h1>{e(x['title'])}</h1>"
            f"<div class=player><audio controls preload=metadata src='{x['slug']}.mp3'></audio></div>"
            + listen_row("../", extra=False, small=True) + "</section>"
            f"<article class='card notes'><!--u51notes-->{x['notes']}<!--/u51notes--></article>")
    page = shell(title=x["title"], rel="../", active="episodes", desc=B.DESCRIPTION, url=f"{base}/episodes/{x['slug']}.html",
                 toolbar=f"<p class=h1>Episodes</p><p class=caption>{label}</p>", body=body, cal_current=when(x).strftime("%Y-%m-%d"))
    write_if_changed(f"{site}/episodes/{x['slug']}.html", page)

# ---------- homepage ----------
def ep_card(x):
    label, short = split_title(x["title"], x)
    if is_special(x): short = re.sub(r"^Sunday Special\s*[:\u2014\u2013-]\s*", "", short)   # the tag says it
    th = thumb(x)
    tags = ("<span class=tag>Sunday Special</span>" if is_special(x) else "") + ("" if x.get("notes") else "<span class=tag>Audio only</span>")
    return (f"<article class='card ep-card{' has-thumb' if th else ''}'>"
            + (f"<img class=ep-thumb src='episodes/{th}' alt='' width=600 height=600 loading=lazy>" if th else "")
            + f"<p class=ep-label><span>{label}</span>{tags}</p>"
            f"<h3><a href='{ep_href(x, '')}'>{e(short)}</a></h3>"
            f"<p class=ep-meta><span>{icon('calendar', 16)}<time datetime='{when(x).isoformat()}'>{fmt_date(x)}</time></span>"
            f"<span>{icon('clock', 16)}<span class=dur>{fmt_dur(x['dur'])}</span></span></p></article>")
latest, older = eps[:LATEST_N], eps[LATEST_N:]
feature = ""
if eps:
    x = eps[0]; label, short = split_title(x["title"], x)
    feature = (f"<section class='card feature' aria-labelledby=latest-title><p class=ep-meta><span>Latest · {label}</span>"
               f"<span>{icon('calendar', 16)}<time datetime='{when(x).isoformat()}'>{fmt_date(x)}</time></span>"
               f"<span>{icon('clock', 16)}<span class=dur>{fmt_dur(x['dur'])}</span></span></p>"
               f"<h3 id=latest-title><a href='{ep_href(x, '')}'>{e(short)}</a></h3>"
               f"<div class=player><audio controls preload=none src='episodes/{x['slug']}.mp3'></audio></div>"
               + (f"<div class=btn-row><a class='btn btn-primary' href='{ep_href(x, '')}'>{icon('file-text')}<span>Show notes</span></a></div>" if x.get("notes") else "")
               + "</section>")
archive = ""
if older:
    months = {}
    for x in older: months.setdefault(when(x).strftime("%B %Y"), []).append(x)
    groups = "".join(f"<div><h3>{m}</h3><ul class=arc-list>" + "".join(
        f"<li class=arc-row><time datetime='{when(x).isoformat()}'>{fmt_date(x, short=True)}</time>"
        f"<a href='{ep_href(x, '')}'>{e(x['title'])}</a><span class=dur>{fmt_dur(x['dur'])}</span></li>" for x in xs) + "</ul></div>"
        for m, xs in months.items())
    archive = (f"<div class=section-head id=archive><h2>Archive</h2><span class=caption>{len(older)} older episode{'s' if len(older) != 1 else ''}, by month</span></div>"
               f"<section class='card archive' aria-label='Archive'>{groups}</section>")
BW = getattr(B, "BANNER_WIDE", None) or {"src": "img/u51-banner-1500.jpg", "srcset": "img/u51-banner-1500.jpg 1500w", "w": 1500, "h": 500}
hero = (f"<section class='card hero'><img class=hero-banner src='{BW['src']}' srcset='{BW['srcset']}' sizes='(max-width: 860px) 100vw, min(1150px, 80vw)' alt='{B.SHORT} banner' width={BW['w']} height={BW['h']}>"
        f"<div class=hero-body><img class=hero-logo src='{LOGO}' alt='{e(B.SHOW)} logo' width=200 height=200>"
        f"<div class=hero-text><h2>{B.SHOW}</h2><p>{e(B.DESCRIPTION)}</p>"
        + listen_row("", extra=True) + "</div></div></section>")
body = (hero + feature +
        f"<div class=section-head id=episodes><h2>Episodes</h2><span class=caption>Latest {len(latest)}, newest first</span></div>"
        f"<div class=ep-grid>{''.join(ep_card(x) for x in latest)}</div>"
        "<section class='card cal-card js-only' id=calendar aria-labelledby=cal-title><h2 id=cal-title>Browse by date</h2>"
        "<div class=cal data-cal data-root='' aria-label='Episode calendar'></div></section>" + archive)
extra_nav = [("archive", "Archive", "#archive", "archive")] if older else []
write_if_changed(f"{site}/index.html", shell(title=B.SHOW, rel="", active="episodes", desc=B.DESCRIPTION, url=f"{base}/",
     toolbar="<h1>Episodes</h1><p class=caption>Latest episodes</p>", body=body, chips_extra=extra_nav))
print(f"built feed.xml ({len(eps)} episodes), index.html ({len(latest)} cards, {len(older)} archived) and {sum(1 for x in eps if x.get('notes'))} notes pages")
