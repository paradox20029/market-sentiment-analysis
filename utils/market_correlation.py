import pandas as pd, yfinance as yf
import matplotlib.pyplot as plt

def correlate_with_stock(ticker="AAPL"):
    df_sent = pd.read_csv("data/sentiment_results.csv")
    stock = yf.download(ticker, period="5d", interval="1d")[["Close"]].reset_index()

    # If yfinance returned MultiIndex columns (can happen), flatten them.
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = ["_".join([str(c) for c in col]).strip("_") for col in stock.columns]

    # Normalize dates in both dataframes to date-only (no time) so we can merge
    df_sent["publishedAt"] = pd.to_datetime(df_sent["publishedAt"])
    df_sent["Date"] = df_sent["publishedAt"].dt.date

    # Build daily sentiment counts with a Date column
    daily_sent = (
        df_sent.groupby("Date")["sentiment"].value_counts().unstack(fill_value=0).reset_index()
    )

    # If daily_sent has MultiIndex columns (unlikely but safe), flatten them
    if isinstance(daily_sent.columns, pd.MultiIndex):
        daily_sent.columns = ["_".join([str(c) for c in col]).strip("_") for col in daily_sent.columns]

    # Ensure both keys are of the same type (python date)
    daily_sent["Date"] = pd.to_datetime(daily_sent["Date"]).dt.date
    stock["DateOnly"] = pd.to_datetime(stock["Date"]).dt.date

    # Merge on the explicit date columns (single-level on both sides)
    merged = stock.merge(daily_sent, left_on="DateOnly", right_on="Date", how="left").fillna(0)

    # Identify existing sentiment columns
    sentiment_cols = [c for c in ("Positive", "Negative", "Neutral") if c in merged.columns]

    # Determine a date column to plot on. Prefer explicit single-level date columns
    if "DateOnly" in merged.columns:
        merged["PlotDate"] = pd.to_datetime(merged["DateOnly"])
    elif "Date" in merged.columns:
        merged["PlotDate"] = pd.to_datetime(merged["Date"])
    else:
        date_cols = [c for c in merged.columns if "date" in str(c).lower()]
        if date_cols:
            merged["PlotDate"] = pd.to_datetime(merged[date_cols[0]])
        else:
            try:
                merged["PlotDate"] = pd.to_datetime(merged.index)
            except Exception:
                merged["PlotDate"] = pd.NaT

    if not sentiment_cols and "Close" not in merged.columns:
        print("No data columns available to plot.")
        return

    # Compute sentiment percentages (per-day) so they are on a comparable scale
    # with stock price. If counts are all zero for a day, percentages will be zero.
    if sentiment_cols:
        merged_sent = merged[sentiment_cols].fillna(0)
        total = merged_sent.sum(axis=1).replace(0, pd.NA)
        for c in sentiment_cols:
            pct_col = f"{c}_pct"
            # avoid division by zero; fillna with 0 after computing
            merged[pct_col] = (merged[c].fillna(0) / total).fillna(0) * 100
        sentiment_pct_cols = [f"{c}_pct" for c in sentiment_cols]
    else:
        sentiment_pct_cols = []

    # Create the figure: sentiment % on left axis, Close price on right axis
    fig, ax1 = plt.subplots(figsize=(10, 5))

    if sentiment_pct_cols:
        merged.plot(x="PlotDate", y=sentiment_pct_cols, ax=ax1)
        ax1.set_ylabel("Sentiment (%)")

    ax2 = ax1.twinx()
    if "Close" in merged.columns:
        ax2.plot(merged["PlotDate"], merged["Close"], color="black", linewidth=2, label="Close")
        ax2.set_ylabel("Price")

    ax1.set_title(f"{ticker} Stock Price vs News Sentiment")

    # Legends: combine both axes' legends
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    if handles1 or handles2:
        ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper left")

    plt.show()
