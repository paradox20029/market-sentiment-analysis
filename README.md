# Intelligent Market Sentiment Analysis System

## 🎯 Overview
A Deep Learning–based NLP system using **FinBERT** to extract real-time **financial news**, determine **market sentiment**, and visualize correlation with **stock performance**.

## ⚙️ Tech Stack
- **Deep Learning Model:** FinBERT (Transformer)
- **Language:** Python 3.10+
- **Libraries:** Transformers, Torch, Pandas, Streamlit, Plotly, YFinance, NewsAPI
- **Visualization:** Streamlit dashboard

## 🚀 How to Run
1. Clone or unzip this project.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Automation (optional)
   - A PowerShell helper is provided: `scripts\setup.ps1` — run it to create the venv and get instructions for installing requirements.
   - A small smoke test is provided: `python scripts\smoke_test.py` (run from inside the activated venv) which verifies `data/news.csv` is created.

4. News sources
   - Preferred: provide a NewsAPI key (set `NEWSAPI_KEY` environment variable or add it to `etl/fetch_news.py`).
   - If you don't have a NewsAPI key, the project will automatically fall back to Google News RSS search so the app remains functional (no API key required).
4. Run the system:
   ```bash
   python main.py
   ```
5. Launch the dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```

## 📊 Output
- Sentiment results (`data/sentiment_results.csv`)
- Real-time dashboard with sentiment visualization
- Correlation of sentiment vs stock trend

## Quick steps (Windows PowerShell)

Create venv and install:
```powershell
.\scripts\setup.ps1
# after following the printed instructions, activate venv and run:
pip install -r requirements.txt
```

Smoke test (inside venv):
```powershell
python .\scripts\smoke_test.py
```

Run pipeline and dashboard:
```powershell
python .\main.py
streamlit run .\dashboard\app.py
```
