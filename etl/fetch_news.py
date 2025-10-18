import os
import sys
import pandas as pd
import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    requests = None
    _HAS_REQUESTS = False


def safe_print(msg: str):
    """Print without raising UnicodeEncodeError on narrow Windows consoles.

    Tries a normal print, falls back to writing utf-8 bytes to stdout buffer, then to an ascii-replaced string.
    """
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            # write encoded bytes directly
            sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        except Exception:
            # final fallback: strip non-ascii
            print(msg.encode("ascii", errors="replace").decode())

# Read API key from environment first; fall back to placeholder so the user sees clearly if it's unset
API_KEY = os.environ.get("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY")


def fetch_from_newsapi(query="stock market", days=2):
    """Fetch using NewsAPI (requires NEWSAPI_KEY)."""
    if API_KEY == "YOUR_NEWSAPI_KEY":
        raise RuntimeError(
            "NewsAPI key not set. Please set the NEWSAPI_KEY environment variable or edit etl/fetch_news.py to add your key."
        )

    from_date = (datetime.date.today() - datetime.timedelta(days=days))
    url = (
        f"https://newsapi.org/v2/everything?q={quote_plus(query)}&language=en&from={from_date}"
        f"&sortBy=publishedAt&apiKey={API_KEY}"
    )
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    articles = data.get("articles", [])

    # handle cases where some fields might be missing
    rows = []
    for a in articles:
        rows.append(
            {
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "publishedAt": a.get("publishedAt"),
                "source": "newsapi",
            }
        )

    return pd.DataFrame(rows)


def fetch_from_google_rss(query="stock market", days=2):
    """Fallback: use Google News RSS search (no API key required).

    Note: RSS may provide fewer fields and uses public search results. This keeps the app functional
    when you don't have a NewsAPI key.
    """
    # Google News RSS supports search queries; adding a 'when' filter helps limit results
    q = f"{query} when:{days}d"
    url = f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"
    if _HAS_REQUESTS:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        content = r.content
    else:
        # fallback to urllib
        from urllib.request import Request, urlopen
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible)"})
        with urlopen(req, timeout=15) as resp:
            content = resp.read()
    root = ET.fromstring(content)
    items = root.findall('.//item')
    rows = []
    for it in items:
        title = it.findtext('title')
        description = it.findtext('description')
        link = it.findtext('link')
        pub = it.findtext('pubDate')
        rows.append({
            "title": title,
            "description": description,
            "url": link,
            "publishedAt": pub,
            "source": "google_rss",
        })
    return pd.DataFrame(rows)


def fetch_financial_news(query="stock market", days=2):
    """High-level fetcher: prefer NewsAPI (if key present), otherwise fall back to Google News RSS."""
    os.makedirs("data", exist_ok=True)

    # Try NewsAPI first if key is set
    if API_KEY != "YOUR_NEWSAPI_KEY":
        try:
            df = fetch_from_newsapi(query, days)
            if not df.empty:
                df.to_csv("data/news.csv", index=False)
                safe_print(f"[OK] Saved {len(df)} news articles to data/news.csv (NewsAPI)")
                return df
            else:
                print("NewsAPI returned no articles; falling back to Google News RSS...")
        except Exception as e:
            print("NewsAPI fetch failed:", e)
            print("Falling back to Google News RSS...")

    # Fallback path: Google News RSS (no key required)
    try:
        df = fetch_from_google_rss(query, days)
        df.to_csv("data/news.csv", index=False)
        safe_print(f"[OK] Saved {len(df)} news articles to data/news.csv (Google News RSS)")
        return df
    except Exception as e:
        raise RuntimeError("Failed to fetch news from NewsAPI and Google News RSS: " + str(e))
