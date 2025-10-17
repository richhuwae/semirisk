import requests, feedparser
import pandas as pd

# Re-use the same feed from before
RSS = "https://news.google.com/rss/search?q=semiconductor+OR+chip+OR+TSMC+OR+Intel&hl=en-GB&gl=GB&ceid=GB:en"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Download the feed
resp = requests.get(RSS, headers=HEADERS, timeout=10)
feed = feedparser.parse(resp.text)

print(f"Found {len(feed.entries)} items")

# Turn into a list of dictionaries
rows = []
for e in feed.entries:
    rows.append({
        "title": e.get("title"),
        "link": e.get("link"),
        "source": e.get("source", {}).get("title") if isinstance(e.get("source"), dict) else e.get("source"),
        "published": e.get("published"),
        "summary": e.get("summary"),
    })

# Convert to DataFrame
df = pd.DataFrame(rows)
print(df.head())          # show first few rows

# Save to CSV
df.to_csv("news_sample.csv", index=False)
print("\\nSaved to news_sample.csv ✅")
