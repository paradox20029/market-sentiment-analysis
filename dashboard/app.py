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
		st.info("Running pipeline — this may take a minute. The UI will not auto-reload on some hosts; refresh the page after it finishes.")
		try:
			# Lazy import pipeline functions so the app can start even if optional deps are missing
			from etl.fetch_news import fetch_financial_news
			from utils.sentiment_pipeline import run_sentiment_pipeline

			# Run fetch + sentiment pipeline in-process. We avoid running main.py as a subprocess
			# because that can fail on hosted platforms if the python environment differs.
			fetch_financial_news("stock market", days=2)
			run_sentiment_pipeline()

			st.success("Pipeline completed — refresh the page to load the new data.")
		except Exception as e:
			st.error(f"Pipeline failed: {e}")
			import traceback
			st.text(traceback.format_exc())
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
