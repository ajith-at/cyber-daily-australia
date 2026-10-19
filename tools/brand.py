# Single source of truth for show branding (imported by build_site.py, x/make_post.py, x/make_banner.py, make_brand_assets.py)
SHOW = "U51 Cyber and AI Security Pod"
SHORT = "U51"
SUBTITLE = "The daily cyber and AI threat brief, from Melbourne"
X_HANDLE = "u51cyber"
X_URL = "https://x.com/u51cyber"
BASE = "https://u51.org"   # custom domain since 19 Oct 2026. The old feed https://ajith-at.github.io/cyber-daily-australia/feed.xml 301-redirects here (Spotify is subscribed to it): never rename the repo or remove the CNAME file
COVER = "cover-u51-v2.jpg"   # owner-supplied artwork (brand_src). Bump the filename whenever the art changes so podcast apps refresh
OWNER_EMAIL = "troy4claude@gmail.com"
FORMERLY = "Cyber Daily Australia"
KEYWORDS = "cybersecurity, cyber security, AI security, threat intelligence, ransomware, vulnerabilities, infosec, Australia, Melbourne, daily brief"
# Listen links (verified 19 Oct 2026). None = not confirmed yet, so the button is hidden. Never guess an ID.
APPLE_URL = "https://podcasts.apple.com/au/podcast/u51-cyber-and-ai-security-pod/id6823895836"   # iTunes Search API, feedUrl matched
POCKETCASTS_URL = "https://pca.st/itunes/6823895836"   # official Pocket Casts link via the Apple ID; redirects to pocketcasts.com/podcast/u51-cyber-and-ai-security-pod/088d7c70-ad77-013f-7974-0efff22b0435
SPOTIFY_URL = None   # set to "https://open.spotify.com/show/<id>" once confirmed (Spotify for Creators > show > Share)
