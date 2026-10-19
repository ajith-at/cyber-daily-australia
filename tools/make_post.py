#!/usr/bin/env python3
"""Write a ready-to-paste X post for an episode of U51 Cyber and AI Security Pod (@u51cyber).
Usage: x/make_post.py <episode-stem> ["optional custom headline sentence"]   (or set X_HEADLINE; SITE_DIR, X_TAGS optional)
Reads site/episodes/<stem>.json, writes x/<stem>.txt and prints it.
Rules: <=280 chars both raw and X-weighted (URLs count 23), no em/en dashes, 1-2 hashtags."""
import json, re, sys, os
sys.path.insert(0, "/workspace/podcast"); import brand as B
D = "/workspace/podcast"; SITE = os.environ.get("SITE_DIR", D + "/site"); BASE = os.environ.get("BASE_URL", B.BASE)
TAGS = os.environ.get("X_TAGS", "#cybersecurity #AIsecurity")
stem = sys.argv[1]; custom = sys.argv[2] if len(sys.argv) > 2 else (os.environ.get("X_HEADLINE") or None)
ep = json.load(open(f"{SITE}/episodes/{stem}.json"))
title = re.sub(r"\s*[\u2014\u2013]\s*", ", ", ep["title"])
m = re.match(r"Episode (\d+):\s*(.*?),\s*(\d{1,2} \w+) \d{4}$", title)
num, topics, day = (m.group(1), m.group(2), m.group(3)) if m else ("", title, "")
url = f"{BASE}/episodes/{stem}.html" if os.path.exists(f"{SITE}/episodes/{stem}.html") else f"{BASE}/episodes/{stem}.mp3"

def xlen(s):  # X weighting: URLs = 23, most non-Latin/emoji = 2
    s2 = re.sub(r"https?://\S+", "x" * 23, s)
    return sum(2 if ord(c) > 0x10FF else 1 for c in s2)

def build(head):
    lead = f"{B.SHORT} Episode {num}" + (f" ({day})" if day else "") if num else B.SHORT
    return f"\U0001F3A7 {lead}: {head}\n\nShow notes and audio: {url}\n\n{TAGS}"

head = (custom or (topics[:1].upper() + topics[1:])).strip()
if not head.endswith((".", "!", "?")): head += "."
post = build(head)
while max(xlen(post), len(post)) > 280:  # keep both X-weighted and raw length <= 280; trim the headline on a word boundary
    head = head.rstrip(".").rsplit(" ", 1)[0].rstrip(",;:") + "..."
    post = build(head)
assert "\u2014" not in post and "\u2013" not in post
os.makedirs(f"{D}/x", exist_ok=True)
open(f"{D}/x/{stem}.txt", "w").write(post + "\n")
print(post); print(f"[{len(post)} raw, {xlen(post)} X-weighted /280] -> {D}/x/{stem}.txt", file=sys.stderr)
