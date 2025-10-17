import requests, feedparser

# 1) Primary: Google News RSS (broad query)
GOOGLE_RSS = (
    "https://news.google.com/rss/search?"
    "q=semiconductor%20OR%20chip%20OR%20TSMC%20OR%20Intel"
    "&hl=en-US&gl=US&ceid=US:en"
)

# 2) Fallback: EU Commission press corner RSS (always returns items)
FALLBACK_RSS = "https://ec.europa.eu/commission/presscorner/home/en/rss.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/123.0.0.0 Safari/537.36"
}

def fetch_rss(url: str):
    # Try downloading with a real browser header
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
    except Exception as e:
        print(f"[warn] Could not fetch {url}: {e}")
        feed = feedparser.parse(url)  # last resort: let feedparser fetch
    return feed

# Try Google first
feed = fetch_rss(GOOGLE_RSS)

if not feed.entries:
    print("[info] Google RSS returned 0 items, trying fallback feed…")
    feed = fetch_rss(FALLBACK_RSS)

print(f"Found {len(feed.entries)} items.")
print("-" * 40)

for i, entry in enumerate(feed.entries[:5], start=1):
    title = entry.get("title", "(no title)")
    link = entry.get("link", "")
    print(f"{i}. {title}\n   {link}\n")
