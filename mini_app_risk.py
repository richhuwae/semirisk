import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="EU Semi Risk – Scores", layout="wide")
st.title("🇪🇺 Semiconductor Supply Risk – Scores")

# Load precomputed files (from step8_run_scoring.py)
try:
    risk_items = pd.read_csv("risk_items.csv", parse_dates=["published_dt"])
    risk_daily = pd.read_csv("risk_daily.csv")
except FileNotFoundError:
    st.error("Missing CSVs. Run: python step8_run_scoring.py")
    st.stop()

if risk_items.empty or risk_daily.empty:
    st.warning("No risk data. Run: python step8_run_scoring.py")
    st.stop()

with st.sidebar:
    st.header("Filters")
    days = st.slider("Days window", 3, 30, 14)
    countries = sorted(risk_daily["iso3"].unique().tolist())
    sel = st.multiselect("Countries", countries)

# Filter by window
risk_daily["date"] = pd.to_datetime(risk_daily["date"])
max_day = risk_daily["date"].max()
cutoff = max_day - pd.Timedelta(days=days-1)
df = risk_daily[risk_daily["date"] >= cutoff].copy()
if sel:
    df = df[df["iso3"].isin(sel)]

# Leaderboard (latest day)
st.subheader("Leaderboard – latest day")
latest = df[df["date"] == df["date"].max()].copy()
latest = latest.sort_values("score_ewma", ascending=False)
st.dataframe(
    latest[["iso3","score_ewma"]].rename(columns={"iso3":"Country","score_ewma":"Score"}),
    use_container_width=True
)

# Heatmap (country × date)
st.subheader("Heatmap – EWMA risk (country × date)")
if not df.empty:
    pivot = df.pivot(index="iso3", columns="date", values="score_ewma").fillna(0)
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale="YlOrRd", labels=dict(color="Risk"))
    fig.update_layout(height=500, margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data in the selected window.")

# Top contributing items (last 24h)
st.subheader("Top contributing items (last 24h)")
last24 = risk_items[risk_items["published_dt"] >= (pd.Timestamp.now(tz='UTC') - pd.Timedelta(hours=24))]
if sel:
    last24 = last24[last24["iso3"].isin(sel)]
top = last24.sort_values("item_score", ascending=False).head(30)
st.dataframe(top[["published_dt","iso3","item_score","topics","source_class","title","link"]], use_container_width=True)

st.caption("Scores combine topic weight, sentiment, source credibility, and time decay.")
