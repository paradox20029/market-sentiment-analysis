import streamlit as st
import pandas as pd
import plotly.express as px
import os
import subprocess

st.title("📈 Intelligent Market Sentiment System")

DATA_SENTIMENT = "data/sentiment_results.csv"
DATA_NEWS = "data/news.csv"

def load_data():
	if os.path.exists(DATA_SENTIMENT):
		df = pd.read_csv(DATA_SENTIMENT)
		source = df.get('source', pd.Series(['unknown'] * len(df))).mode()[0]
		return df, source
	elif os.path.exists(DATA_NEWS):
		df = pd.read_csv(DATA_NEWS)
		return df, df.get('source', pd.Series(['news'] * len(df))).mode()[0]
	else:
		return None, None


df, source = load_data()

if df is None:
	st.warning("No data found. Run the pipeline (click 'Run pipeline') or place a CSV in data/ named sentiment_results.csv or news.csv")
	if st.button("Run pipeline"):
		# call main.py to fetch and process data
		subprocess.run(["python", "main.py"])
		st.experimental_rerun()
else:
	st.info(f"Data source: {source}")
	if 'sentiment' in df.columns:
		st.subheader("Sentiment Distribution")
		fig = px.histogram(df, x="sentiment", color="sentiment")
		st.plotly_chart(fig)
		st.subheader("Recent Headlines")
		st.dataframe(df[[col for col in ['title', 'sentiment', 'publishedAt'] if col in df.columns]])
	else:
		st.subheader("Recent Headlines")
		st.dataframe(df[[col for col in ['title', 'publishedAt', 'description'] if col in df.columns]])
