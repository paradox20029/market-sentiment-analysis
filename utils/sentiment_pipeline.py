import pandas as pd
from models.finbert_sentiment import FinBERT

def run_sentiment_pipeline():
    finbert = FinBERT()
    df = pd.read_csv("data/news.csv")
    df["sentiment"] = df["title"].fillna("").apply(finbert.predict)
    df.to_csv("data/sentiment_results.csv", index=False)
    print("✅ Sentiment analysis completed and saved to data/sentiment_results.csv")
    return df
