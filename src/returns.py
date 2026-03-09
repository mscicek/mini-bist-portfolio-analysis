import pandas as pd
import numpy as np


def compute_summary(data: pd.DataFrame, stock_names: list[str]) -> pd.DataFrame:
    return_cols = [f"{s}_Return" for s in stock_names]
    returns_df  = data[return_cols].dropna()

    summary = pd.DataFrame(index=stock_names)
    summary["Ort. Günlük Getiri (%)"]  = returns_df.mean().values * 100
    summary["Volatilite (Günlük %)"]   = returns_df.std().values * 100
    summary["Yıllık Getiri (%)"]        = returns_df.mean().values * 252 * 100
    summary["Yıllık Volatilite (%)"]    = returns_df.std().values * np.sqrt(252) * 100
    summary["Sharpe Ratio"]             = sharpe_ratio(returns_df, return_cols)
    summary["Max Drawdown (%)"]         = [max_drawdown(data[f"{s}_Close"]) * 100 for s in stock_names]
    summary["Toplam Getiri (%)"]        = [cumulative_return(data[f"{s}_Close"]) * 100 for s in stock_names]
    return summary.round(2)


def sharpe_ratio(
    returns_df: pd.DataFrame,
    return_cols: list[str],
    risk_free_rate: float = 0.0,
    trading_days: int = 252,
) -> list[float]:
    daily_rf = risk_free_rate / trading_days
    results  = []
    for col in return_cols:
        col_returns = returns_df[col].dropna()
        excess      = col_returns - daily_rf
        sr          = (excess.mean() / excess.std()) * np.sqrt(trading_days)
        results.append(round(sr, 3))
    return results


def max_drawdown(price_series: pd.Series) -> float:
    prices      = price_series.dropna()
    rolling_max = prices.cummax()
    drawdown    = (prices - rolling_max) / rolling_max
    return drawdown.min()


def cumulative_return(price_series: pd.Series) -> float:
    prices = price_series.dropna()
    if prices.empty or prices.iloc[0] == 0:
        return 0.0
    return (prices.iloc[-1] / prices.iloc[0]) - 1


def compute_cumulative_returns(data: pd.DataFrame, stock_names: list[str]) -> pd.DataFrame:
    cum_df = pd.DataFrame({"Date": data["Date"]})
    for stock in stock_names:
        close       = data[f"{stock}_Close"]
        first_valid = close.dropna().iloc[0]
        cum_df[f"{stock}_Cumulative"] = (close / first_valid) * 100
    return cum_df
