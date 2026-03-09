import pandas as pd
import numpy as np


def load_stock_data(file_path: str, stock_name: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    date_col = next(
        (c for c in df.columns if c.lower() in ["tarih", "date"]), None
    )
    if date_col is None:
        raise ValueError(f"{file_path}: Tarih sütunu bulunamadı. Sütunlar: {list(df.columns)}")

    close_col = next(
        (c for c in df.columns if c.lower() in ["şimdi", "close", "son", "last", "kapanış"]), None
    )
    if close_col is None:
        raise ValueError(f"{file_path}: Kapanış sütunu bulunamadı. Sütunlar: {list(df.columns)}")

    df = df[[date_col, close_col]].copy()
    df.rename(columns={date_col: "Date", close_col: "Close"}, inplace=True)

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["Close"] = (
        df["Close"]
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df.dropna(subset=["Date", "Close"], inplace=True)
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    df["Daily_Return"] = df["Close"].pct_change()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()

    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["MA20"] + 2 * rolling_std
    df["BB_Lower"] = df["MA20"] - 2 * rolling_std
    df["RSI"] = _compute_rsi(df["Close"])

    df.rename(columns={
        "Close":        f"{stock_name}_Close",
        "Daily_Return": f"{stock_name}_Return",
        "MA20":         f"{stock_name}_MA20",
        "MA50":         f"{stock_name}_MA50",
        "BB_Upper":     f"{stock_name}_BB_Upper",
        "BB_Lower":     f"{stock_name}_BB_Lower",
        "RSI":          f"{stock_name}_RSI",
    }, inplace=True)

    return df


def _compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta    = series.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()
    rs       = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def merge_stocks(stock_dfs: list[pd.DataFrame]) -> pd.DataFrame:
    merged = stock_dfs[0]
    for df in stock_dfs[1:]:
        merged = merged.merge(df, on="Date", how="inner")
    merged.reset_index(drop=True, inplace=True)
    return merged
