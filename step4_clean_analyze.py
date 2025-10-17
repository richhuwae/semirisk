import re
import pandas as pd
from collections import Counter

# 1) Load the CSV from Step 3
df = pd.read_csv("news_sample.csv")

# 2) Clean the summary (remove HTML tags)
def strip_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"<.*?>", "", text)

df["summary_clean"] = df["summary"].apply(strip_html)

# 3) Parse the published date into a proper datetime
df["published_dt"] = pd.to_datetime(df["published"], errors="coerce")

# 4) Keep tidy columns
df_clean = df[["title", "source", "link", "published_dt", "summary_clean"]].copy()

print("Preview (cleaned):")
print(df_clean.head(3), "\n")

# 5) Simple filtering: show rows that mention some keywords
KEYWORDS = ["TSMC", "Intel", "ASML", "Nvidia", "Netherlands", "Germany", "France"]
mask = df_clean["title"].fillna("").str.contains("|".join(KEYWORDS), case=False)
hits = df_clean[mask]
print(f"Found {len(hits)} items mentioning any of: {', '.join(KEYWORDS)}")
print(hits[["title", "published_dt"]].head(5), "\n")

# 6) Quick counts by country/company terms (very simple rule-based search)
terms = {
    "Netherlands": ["Netherlands", "Dutch", "Amsterdam", "Eindhoven", "ASML"],
    "Germany": ["Germany", "German", "Berlin", "Munich", "Infineon"],
    "France": ["France", "French", "Paris", "STMicro", "STMicroelectronics"],
    "Italy": ["Italy", "Italian", "Milan", "Rome"],
    "Ireland": ["Ireland", "Irish", "Dublin", "Intel"],
    "Spain": ["Spain", "Spanish", "Madrid", "Barcelona"],
}

def mentions(row_text: str, bag: list[str]) -> bool:
    t = row_text or ""
    return any(word.lower() in t.lower() for word in bag)

counts = Counter()
for _, row in df_clean.iterrows():
    text = f"{row['title']} {row['summary_clean']}"
    for k, bag in terms.items():
        if mentions(text, bag):
            counts[k] += 1

# Convert counts to a small DataFrame and save
counts_df = pd.DataFrame(sorted(counts.items(), key=lambda x: x[1], reverse=True), columns=["country","mentions"])
print("Mentions by simple term matching:")
print(counts_df, "\n")

# 7) Save cleaned data & counts
df_clean.to_csv("news_clean.csv", index=False)
counts_df.to_csv("mentions_counts.csv", index=False)
print("Saved: news_clean.csv, mentions_counts.csv ✅")
