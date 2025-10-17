import sys
from pathlib import Path

# Ensure project root is on sys.path so imports like `from etl.fetch_news` work
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etl.fetch_news import fetch_financial_news
import os

def main():
    print("Running smoke test: fetching news (1 day) ...")
    df = fetch_financial_news(days=1)
    if os.path.exists("data/news.csv"):
        print(f"OK: data/news.csv created with {len(df)} rows")
    else:
        raise SystemExit("Smoke test failed: data/news.csv not found")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback, sys
        traceback.print_exc()
        print(f"Smoke test failed: {e}", file=sys.stderr)
        raise
