# U51 Cyber and AI Security Botcast: podcast style rules

## Name and brand (rebranded 19 Oct 2026)
- Full name (from 27 Oct 2026): "U51 Cyber and AI Security Botcast". Short form in scripts and posts: "U51" (say it as "U fifty-one"; write "U51"). X: @u51cyber, https://x.com/u51cyber.
- Show description: `DESCRIPTION` in brand.py (feed channel description and itunes:summary, homepage hero, meta and og descriptions). It says the show is researched, written and voiced by AI agents under human editorial direction. Keep it factual, no names, no em dashes.
- Branding values (name, handle, subtitle, description, cover filename, keywords) live in `/workspace/podcast/brand.py`; publish.sh, build_site.py, x/make_post.py, and x/make_brand_assets.py read from it.
- Site and feed: https://u51.org/ and https://u51.org/feed.xml (custom domain on GitHub Pages since 19 Oct 2026, HTTPS enforced). Spotify is still subscribed to the old https://ajith-at.github.io/cyber-daily-australia/feed.xml, which 301-redirects to u51.org, so never rename the repo, never delete `site/CNAME` (it holds `u51.org`), and never change the item guid prefix `cyber-daily-australia-`. BASE lives in brand.py (`https://u51.org`). Use u51.org links in notes and posts.
- Artwork: the owner-supplied U51 graphics in `/workspace/podcast/brand_src/` (u51_cover_src.png, u51_banner_src.png) are the brand. Do not generate or redraw brand art. `python3 x/make_brand_assets.py` builds everything from them: site/cover-u51-v2.jpg and site/cover.jpg (3000x3000 podcast cover), x_banner.png (1500x500), x_avatar.png (400x400), and the web copies in site/img (600px logo, banner strip, 1200px og image, favicons). If the art changes, bump `COVER` in brand.py to a new filename so podcast apps refresh. x/make_cover.py and x/make_banner.py are retired (they exit unless forced); publish.sh does not call any image script.
- Note: the cover and X artwork still read "U51 Cyber and AI Podcast" (not regenerated after the 27 Oct 2026 rename to "U51 Cyber and AI Security Botcast"). The feed title, site and Sunday Special thumbnails use the full name. Leave the artwork until the owner supplies new art.
- Website: build_site.py adds the banner strip and logo to index.html, a small logo header to every notes page, plus favicon and og:image tags. Do not hand-edit these.
- Listen buttons: APPLE_URL, POCKETCASTS_URL and SPOTIFY_URL in brand.py drive the button row on index.html and the compact row in each notes-page header. A platform set to None is hidden. Spotify is not confirmed yet: when the owner supplies the open.spotify.com/show/<id> link, set SPOTIFY_URL, run `python3 build_site.py` and push. Never guess an ID.
- Never mention the owner's name in any script, notes, feed, site or post. Owner email in the feed stays troy4claude@gmail.com.
- Never mention the podcast's pre-rename name or the rename in scripts, notes, posts or anywhere public (internal rule; don't spell the old name out in files either) (Episode 5, 20 Oct 2026, was the first under the new name).

## Script
- Length: 1,500 to 2,200 words (10 to 15 min), scaled to how significant the day's news is.
- Intro: one or two sentences only: a Melbourne greeting, the show name "U51", the date, and the reporting window (Melbourne time). Then go straight into the first story. No show preamble or running order.
  - Name in scripts: "U51" is the default in the intro and sign-off. Whenever the full name is spoken (intro, sign-off or a plug), say "U51 Cyber and AI Security Botcast", never the older "Pod" form.
  - Model: "Hello from Melbourne, Australia, this is U51, your cyber and AI security brief for Tuesday the 20th of October, covering the 24 hours to 7 am." Vary the wording every day, for example: "Good morning from Melbourne. You're listening to U51, the cyber and AI security brief for ...", "From Melbourne, this is U51 with your cyber and AI threat brief for ...", "Hello from a [weather] Melbourne, it's U51, your security brief for ...". Never reuse the previous episode's exact opening.
- Australian English, spoken style, neutral executive tone. Expand acronyms on first use; say CVE numbers sparingly and spell them out.
- No URLs and no IoC strings (point listeners to the show notes instead). Invent nothing beyond the day's SITREP.
- Confidence: never say "confidence is high", and don't flag high-confidence items at all. Flag only moderate or low items, in varied natural phrasing, for example: "this rests on a single report", "not yet independently verified", "details are still emerging", "treat this as a lead only", "the figures are self-reported". Don't repeat the same phrasing within an episode.
- Order: headlines → Australian focus (say plainly if there is no significant Australia-specific activity) → global threats → AI security → industry → outlook and patch priorities → a short sign-off (if it names the show in full, use "U51 Cyber and AI Security Botcast").

## Show notes (required, 3rd argument to publish.sh)
- An HTML fragment (or simple markdown) listing every story covered: a bold title, a one-line summary and the source link(s) from the SITREP. Group by section. Items with no link may be listed without one.

## Audio
- Voice en-AU-WilliamMultilingualNeural, rate -10% (slowed from -5% at Ajith's request, 24 Oct 2026), loudness normalised to -16 LUFS, mono 96 kbps.

## Titles and descriptions (Spotify)
- Episode titles: never use an em dash or en dash. Format: "Episode N: <headline topics>, <D Month YYYY>" (e.g. "Episode 2: Ivanti patch deadline and AI key theft, 17 October 2026").
- The show-notes file drives the Spotify description. Open it with a 2 or 3 sentence plain summary of the day's top stories (no greeting, no "welcome", no methodology), then the story list with links. No em dashes anywhere in the notes.

## Character
- A little dry, understated humour and personality is welcome, e.g. a wry aside about a vendor's patch cadence or a well-placed observation. At most two or three light touches per episode, never at victims' expense, never undermining seriousness on critical items.
- Never repeat the same joke, phrase, sign-off or aside across episodes; vary openings, transitions and closings daily.

## Weekly and continuity rules (added 18 Oct 2026)
- Monday episodes: after the intro, give a brief recap of significant weekend activity and the stories covered in the Saturday and Sunday editions (read previous scripts/notes in /workspace/podcast/site/episodes and ep*.txt), for listeners who skip weekends.
- Localisation: occasionally (not daily) open with a light local touch, such as Melbourne weather, events, public holidays or something significant in Australia, or worldwide if it's very important. Keep it natural, varied and never formulaic; verify any facts (e.g. a weather forecast) from live sources.
- Continuity: rarely, and only when the story warrants it, link to coverage in a previous episode (e.g. "a follow-up on Friday's BeyondTrust story"). Check the earlier scripts first; keep it natural.
- Australian section: do not say there were no new ASD/ACSC alerts. Mention ASD/ACSC only when there is something relevant. If nothing important is relevant to Australia, omit the Australian segment entirely without remarking on its absence.

## X (Twitter): @u51cyber, https://x.com/u51cyber (added 19 Oct 2026, replacing the pre-rename handle)
- The site index, every notes page (site footer "@u51cyber" and the mobile section chips; not the desktop sidebar), each feed item's show-notes footer and the feed channel description link to the X profile. publish.sh (via build_site.py) adds these automatically.
- Daily X post: publish.sh runs `x/make_post.py <stem>` after each build and writes `/workspace/podcast/x/<stem>.txt` (ready to paste; nothing is posted automatically, as the box has no X access).
  - Default headline is the episode title's topics. For a better post, regenerate with a custom headline: `X_HEADLINE="..." venv/bin/python x/make_post.py <stem>` or pass it as the 2nd argument. Lead with the 2 to 4 biggest stories, specific and punchy; a light touch of character is fine, but never at victims' expense.
  - Format: 🎧 U51 Episode N (D Month): headline. / Show notes and audio: <notes URL> / 1 or 2 light hashtags (default `#cybersecurity #AIsecurity`, override with X_TAGS).
  - Limits: 280 characters or fewer, raw and X-weighted (the script trims the headline if needed). No em or en dashes. Never include personal names or details of the show's owner.
- Banner: `/workspace/podcast/x_banner.png` (1500x500) and avatar `/workspace/podcast/x_avatar.png` (400x400), rebuilt by `python3 x/make_brand_assets.py` from the supplied artwork.


## Sunday Special (from 25 Oct 2026)
- Every Sunday episode is a "Sunday Special": a deep dive into one relevant topic instead of the usual news run. No news segment by default. Only if there is a burning high-severity or extraordinary high-profile incident in the past 24 hours, open with a brief (under 2 minutes) verified mention of it, then the deep dive. Target 20 to 25 minutes in total.
- Title format: "Sunday Special: <topic>, D Month YYYY" (still counts as the next episode number in the feed: "Episode N, Sunday Special: <topic>, D Month YYYY").
- Planning cycle: Thursday evening, five candidate topics go to Ajith for selection; Saturday, a draft text outline goes to him for review; Sunday morning, the episode is produced from the approved outline (with his feedback applied). Files live in /workspace/podcast/specials/<Sunday date YYYY-MM-DD>/ (topic.md, outline.md).
- Deep dives explain frameworks and standards accurately from primary sources (standard bodies, NIST, regulators). Never quote or paraphrase clauses of a paywalled standard you haven't read; rely on the publisher's public summaries and say so where relevant.
- The written daily SITREP still runs on Sundays as normal. Monday's weekend recap covers Saturday's episode, the Sunday Special, and any significant news from Sunday that the Special didn't cover.

## Monday episodes: plug the Sunday Special (standing rule, Ajith 25 Oct 2026)
Every Monday episode includes a short plug of the previous day's Sunday Special (about 30 to 45 seconds, after the intro or within the weekend recap): name the episode and topic, give 2 or 3 key takeaways drawn from its published script or show notes in /workspace/podcast/specials/<Sunday date>/ and the episode page, and point listeners to it on u51.org. Link the Special's notes page in the Monday show notes.
