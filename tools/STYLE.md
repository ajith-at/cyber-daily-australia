# U51 Cyber and AI Security Pod: podcast style rules

## Name and brand (rebranded 19 Oct 2026; formerly Cyber Daily Australia)
- Full name: "U51 Cyber and AI Security Pod". Short form in scripts and posts: "U51" (say it as "U fifty-one"; write "U51"). X: @u51cyber, https://x.com/u51cyber.
- Branding values (name, handle, subtitle, cover filename, keywords) live in `/workspace/podcast/brand.py`; publish.sh, build_site.py, x/make_post.py, and x/make_brand_assets.py read from it.
- Site and feed: https://u51.org/ and https://u51.org/feed.xml (custom domain on GitHub Pages since 19 Oct 2026, HTTPS enforced). Spotify is still subscribed to the old https://ajith-at.github.io/cyber-daily-australia/feed.xml, which 301-redirects to u51.org, so never rename the repo, never delete `site/CNAME` (it holds `u51.org`), and never change the item guid prefix `cyber-daily-australia-`. BASE lives in brand.py (`https://u51.org`). Use u51.org links in notes, posts and Notion.
- Artwork: the owner-supplied U51 graphics in `/workspace/podcast/brand_src/` (u51_cover_src.png, u51_banner_src.png) are the brand. Do not generate or redraw brand art. `python3 x/make_brand_assets.py` builds everything from them: site/cover-u51-v2.jpg and site/cover.jpg (3000x3000 podcast cover), x_banner.png (1500x500), x_avatar.png (400x400), and the web copies in site/img (600px logo, banner strip, 1200px og image, favicons). If the art changes, bump `COVER` in brand.py to a new filename so podcast apps refresh. x/make_cover.py and x/make_banner.py are retired (they exit unless forced); publish.sh does not call any image script.
- Note: the artwork reads "U51 Cyber and AI Podcast" while the feed title is "U51 Cyber and AI Security Pod". Keep the feed title as is unless told otherwise.
- Website: build_site.py adds the banner strip and logo to index.html, a small logo header to every notes page, plus favicon and og:image tags. Do not hand-edit these.
- Listen buttons: APPLE_URL, POCKETCASTS_URL and SPOTIFY_URL in brand.py drive the button row on index.html and the compact row in each notes-page header. A platform set to None is hidden. Spotify is not confirmed yet: when the owner supplies the open.spotify.com/show/<id> link, set SPOTIFY_URL, run `python3 build_site.py` and push. Never guess an ID.
- Never mention the owner's name in any script, notes, feed, site or post. Owner email in the feed stays troy4claude@gmail.com.
- Do not mention the old name again after Episode 5 (see the one-off note below).

## Script
- Length: 1,500 to 2,200 words (10 to 15 min), scaled to how significant the day's news is.
- Intro: one or two sentences only: a Melbourne greeting, the show name "U51", the date, and the reporting window (Melbourne time). Then go straight into the first story. No show preamble or running order.
  - Model: "Hello from Melbourne, Australia, this is U51, your cyber and AI security brief for Tuesday the 20th of October, covering the 24 hours to 7 am." Vary the wording every day, for example: "Good morning from Melbourne. You're listening to U51, the cyber and AI security brief for ...", "From Melbourne, this is U51 with your cyber and AI threat brief for ...", "Hello from a [weather] Melbourne, it's U51, your security brief for ...". Never reuse the previous episode's exact opening.
- Australian English, spoken style, neutral executive tone. Expand acronyms on first use; say CVE numbers sparingly and spell them out.
- No URLs and no IoC strings (point listeners to the show notes instead). Invent nothing beyond the day's SITREP.
- Confidence: never say "confidence is high", and don't flag high-confidence items at all. Flag only moderate or low items, in varied natural phrasing, for example: "this rests on a single report", "not yet independently verified", "details are still emerging", "treat this as a lead only", "the figures are self-reported". Don't repeat the same phrasing within an episode.
- Order: headlines → Australian focus (say plainly if there is no significant Australia-specific activity) → global threats → AI security → industry → outlook and patch priorities → a short sign-off.

## Show notes (required, 3rd argument to publish.sh)
- An HTML fragment (or simple markdown) listing every story covered: a bold title, a one-line summary and the source link(s) from the SITREP. Group by section. Items with no link may be listed without one.

## Audio
- Voice en-AU-WilliamMultilingualNeural, rate -5%, loudness normalised to -16 LUFS, mono 96 kbps.

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

## X (Twitter): @u51cyber, https://x.com/u51cyber (added 19 Oct 2026; was @CyberDailyAus until the rebrand)
- The site index, every notes page (top nav "Follow on X (@u51cyber)"), each feed item's show-notes footer and the feed channel description link to the X profile. publish.sh (via build_site.py) adds these automatically.
- Daily X post: publish.sh runs `x/make_post.py <stem>` after each build and writes `/workspace/podcast/x/<stem>.txt` (ready to paste; nothing is posted automatically, as the box has no X access).
  - Default headline is the episode title's topics. For a better post, regenerate with a custom headline: `X_HEADLINE="..." venv/bin/python x/make_post.py <stem>` or pass it as the 2nd argument. Lead with the 2 to 4 biggest stories, specific and punchy; a light touch of character is fine, but never at victims' expense.
  - Format: 🎧 U51 Episode N (D Month): headline. / Show notes and audio: <notes URL> / 1 or 2 light hashtags (default `#cybersecurity #AIsecurity`, override with X_TAGS).
  - Limits: 280 characters or fewer, raw and X-weighted (the script trims the headline if needed). No em or en dashes. Never include personal names or details of the show's owner.
- Banner: `/workspace/podcast/x_banner.png` (1500x500) and avatar `/workspace/podcast/x_avatar.png` (400x400), rebuilt by `python3 x/make_brand_assets.py` from the supplied artwork.

## One-off note for Episode 5 (Tuesday 20 Oct 2026) only
- Episode 5 is the first under the new name. Once, early (right after the intro, or folded into it), mention briefly and naturally, with a light touch of humour, that the show has a new name and was formerly Cyber Daily Australia. Example tone only, do not copy: "Same brief, same voice, new name: until yesterday this was Cyber Daily Australia, and from today it's U51. Nothing else has changed, apart from a name that's quicker to say before your first coffee." Don't refer to any other organisation or explain why the name changed. Keep it to one or two sentences and don't mention who chose the name.
- Mention the new X handle @u51cyber in that same aside if it fits ("you'll find us on X at u51cyber").
- After Episode 5, never mention the rename or the old name in scripts again. Delete this section once Episode 5 is published.
