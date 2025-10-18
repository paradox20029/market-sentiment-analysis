import os

def run_all():
    from etl.fetch_news import fetch_financial_news
    from utils.sentiment_pipeline import run_sentiment_pipeline
    from utils.market_correlation import correlate_with_stock

    print("🚀 Starting Intelligent Market Sentiment System...\n")
    fetch_financial_news("stock market", days=2)
    run_sentiment_pipeline()
    correlate_with_stock("AAPL")


if __name__ == "__main__":
    # Only run the pipeline when explicitly requested via env var to avoid
    # accidental execution when this file is selected as a Streamlit entrypoint.
    if os.getenv("RUN_PIPELINE", "false").lower() in ("1", "true", "yes"):
        run_all()
    else:
        print("RUN_PIPELINE is not enabled; main pipeline will not run. Set RUN_PIPELINE=true to execute.")
