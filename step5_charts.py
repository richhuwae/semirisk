import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned data
news = pd.read_csv("news_clean.csv", parse_dates=["published_dt"])
counts = pd.read_csv("mentions_counts.csv")

# ---- Chart 1: Bar chart of mentions by country ----
# Keep top 8 (or fewer if not enough)
counts_sorted = counts.sort_values("mentions", ascending=False).head(8)

plt.figure()
plt.bar(counts_sorted["country"], counts_sorted["mentions"])
plt.title("Mentions by country (simple term matching)")
plt.xlabel("Country")
plt.ylabel("Mentions")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("chart_mentions_by_country.png", dpi=160)
plt.close()

# ---- Chart 2: Time series of article counts per day ----
news["date"] = news["published_dt"].dt.date
by_day = news.groupby("date").size().reset_index(name="count")

plt.figure()
plt.plot(by_day["date"], by_day["count"], marker="o")
plt.title("Articles per day")
plt.xlabel("Date")
plt.ylabel("Count")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("chart_articles_per_day.png", dpi=160)
plt.close()

print("Saved: chart_mentions_by_country.png, chart_articles_per_day.png ✅")
