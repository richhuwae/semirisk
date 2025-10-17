import os, requests, feedparser, re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

RSS = "https://news.google.com/rss/search?q=semiconductor+OR+chip+OR+TSMC+OR+Intel&hl=en-GB&gl=GB&ceid=GB:en"
HEADERS = {"User-Agent": "Mozilla/5.0"}

TERMS = {
    "Netherlands": ["Netherlands","Dutch","Amsterdam","Eindhoven","ASML"],
    "Germany": ["Germany","German","Berlin","Munich","Infineon"],
    "France": ["France","French","Paris","STMicro","STMicroelectronics"],
    "Italy": ["Italy","Italian","Milan","Rome"],
    "Ireland": ["Ireland","Irish","Dublin","Intel"],
    "Spain": ["Spain","Spanish","Madrid","Barcelona"],
}

def strip_html(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r"<.*?>", "", text)

def fetch_to_dataframe():
    resp = requests.get(RSS, headers=HEADERS, timeout=10)
    feed = feedparser.parse(resp.text)
    rows = []
    for e in feed.entries:
        rows.append({
            "title": e.get("title"),
            "link": e.get("link"),
            "source": e.get("source", {}).get("title") if isinstance(e.get("source"), dict) else e.get("source"),
            "published": e.get("published"),
            "summary": e.get("summary"),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["summary_clean"] = df["summary"].apply(strip_html)
    df["published_dt"] = pd.to_datetime(df["published"], errors="coerce")
    return df[["title","source","link","published_dt","summary_clean"]].copy()

def mentions_counts(df):
    from collections import Counter
    C = Counter()
    for _, r in df.iterrows():
        text = f"{r['title']} {r['summary_clean']}"
        for k, bag in TERMS.items():
            if any(word.lower() in (text or "").lower() for word in bag):
                C[k] += 1
    return pd.DataFrame(sorted(C.items(), key=lambda x: x[1], reverse=True), columns=["country","mentions"])

@st.cache_data(ttl=600)
def load_data():
    if os.path.exists("news_clean.csv"):
        news = pd.read_csv("news_clean.csv", parse_dates=["published_dt"])
    else:
        news = fetch_to_dataframe()
        if not news.empty:
            news.to_csv("news_clean.csv", index=False)
    counts = mentions_counts(news) if not news.empty else pd.DataFrame(columns=["country","mentions"])
    return news, counts

st.set_page_config(page_title="Mini Semi Dashboard", layout="wide")
st.title("🖥️ Mini EU Semiconductor News Dashboard")

news, counts = load_data()

if news.empty:
    st.warning("No data yet. Try running again in a minute.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    kw = st.text_input("Keyword contains", value="")
    days = st.slider("Days window (lookback)", 3, 30, 14)

latest_date = news["published_dt"].max()
cutoff = latest_date - pd.Timedelta(days=days-1)
filtered = news[news["published_dt"] >= cutoff]
if kw.strip():
    filtered = filtered[filtered["title"].str.contains(kw, case=False, na=False)]

col1, col2, col3 = st.columns(3)
col1.metric("Articles", len(filtered))
col2.metric("Unique sources", filtered["source"].nunique())
col3.metric("Date range", f"{filtered['published_dt'].min().date()} → {filtered['published_dt'].max().date()}")

st.subheader("Latest headlines")
st.dataframe(filtered[["published_dt","source","title","link"]].sort_values("published_dt", ascending=False), use_container_width=True)

st.subheader("Mentions by country (simple matching)")
top = counts.sort_values("mentions", ascending=False).head(8)
fig1 = plt.figure()
plt.bar(top["country"], top["mentions"])
plt.title("Mentions by country")
plt.xlabel("Country"); plt.ylabel("Mentions")
plt.xticks(rotation=30, ha="right")
st.pyplot(fig1)

st.subheader("Articles per day")
by_day = filtered.assign(date=filtered["published_dt"].dt.date).groupby("date").size().reset_index(name="count")
fig2 = plt.figure()
plt.plot(by_day["date"], by_day["count"], marker="o")
plt.title("Articles per day")
plt.xlabel("Date"); plt.ylabel("Count")
plt.xticks(rotation=30, ha="right")
st.pyplot(fig2)

st.caption("Data source: Google News RSS • Refresh every 10 minutes")
