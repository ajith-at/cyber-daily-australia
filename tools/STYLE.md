# Cyber Daily Australia: podcast style rules

## Script
- Length: 1,500–2,200 words (10–15 min), scaled to how significant the day's news is.
- Intro: one or two sentences only: "Hello from Melbourne, Australia", the date, and the reporting window (Melbourne time). Then go straight into the first story. No show preamble or running order.
- Australian English, spoken style, neutral executive tone. Expand acronyms on first use; say CVE numbers sparingly and spell them out.
- No URLs and no IoC strings (point listeners to the show notes instead). Invent nothing beyond the day's SITREP.
- Confidence: never say "confidence is high", and don't flag high-confidence items at all. Flag only moderate or low items, in varied natural phrasing, for example: "this rests on a single report", "not yet independently verified", "details are still emerging", "treat this as a lead only", "the figures are self-reported". Don't repeat the same phrasing within an episode.
- Order: headlines → Australian focus (say plainly if there is no significant Australia-specific activity) → global threats → AI security → industry → outlook and patch priorities → a short sign-off.

## Show notes (required, 3rd argument to publish.sh)
- An HTML fragment (or simple markdown) listing every story covered: a bold title, a one-line summary and the source link(s) from the SITREP. Group by section. Items with no link may be listed without one.

## Audio
- Voice en-AU-WilliamMultilingualNeural, rate -5%, loudness normalised to -16 LUFS, mono 96 kbps.
