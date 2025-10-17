from etl.fetch_news import fetch_financial_news
from utils.sentiment_pipeline import run_sentiment_pipeline
from utils.market_correlation import correlate_with_stock

if __name__ == "__main__":
    print("🚀 Starting Intelligent Market Sentiment System...\n")
    fetch_financial_news("stock market", days=2)
    run_sentiment_pipeline()
    correlate_with_stock("AAPL")
