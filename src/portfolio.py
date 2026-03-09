"""
portfolio.py
------------
Portföy analizi ve al-sat stratejisi simülasyon modülü.
Golden Cross stratejisi, Buy & Hold karşılaştırması.
"""

import pandas as pd
import numpy as np


def compute_correlation(data: pd.DataFrame, stock_names: list[str]) -> pd.DataFrame:
    """
    Hisse getirileri arasındaki korelasyon matrisini hesaplar.

    Args:
        data: Birleştirilmiş hisse DataFrame'i
        stock_names: Hisse adları listesi

    Returns:
        Korelasyon matrisi DataFrame'i
    """
    return_cols = [f"{s}_Return" for s in stock_names]
    return data[return_cols].corr().rename(
        columns={f"{s}_Return": s for s in stock_names},
        index={f"{s}_Return": s for s in stock_names},
    )


def golden_cross_strategy(
    data: pd.DataFrame,
    stock: str,
    initial_capital: float = 10_000.0,
) -> pd.DataFrame:
    """
    Golden Cross al-sat stratejisini simüle eder.
    Kural: MA20 > MA50 → AL, MA20 < MA50 → SAT (nakit tutma).

    Args:
        data: Birleştirilmiş hisse DataFrame'i (MA20 ve MA50 gerekli)
        stock: Hisse adı (örn. 'THYAO')
        initial_capital: Başlangıç sermayesi (TL)

    Returns:
        Sinyal ve portföy değerini içeren DataFrame
    """
    required = [f"{stock}_Close", f"{stock}_MA20", f"{stock}_MA50"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Eksik sütunlar: {missing}")

    df = data[["Date"] + required].copy()
    df.columns = ["Date", "Close", "MA20", "MA50"]
    df = df.dropna(subset=["MA20", "MA50"]).reset_index(drop=True)

    # Sinyal: 1 = AL pozisyonunda, 0 = Nakit
    df["Signal"] = (df["MA20"] > df["MA50"]).astype(int)
    # Pozisyon değişimi: +1 → AL, -1 → SAT, 0 → değişim yok
    df["Position"] = df["Signal"].diff().fillna(0)

    # --- Portföy simülasyonu ---
    portfolio_value = initial_capital
    cash = initial_capital
    shares = 0.0
    portfolio_values = []
    buy_dates, sell_dates = [], []

    for i, row in df.iterrows():
        price = row["Close"]
        if row["Position"] == 1:  # AL sinyali
            if cash > 0 and price > 0:
                shares = cash / price
                cash = 0.0
                buy_dates.append(row["Date"])
        elif row["Position"] == -1:  # SAT sinyali
            if shares > 0:
                cash = shares * price
                shares = 0.0
                sell_dates.append(row["Date"])

        current_value = cash + shares * price
        portfolio_values.append(current_value)

    df["Strategy_Value"] = portfolio_values

    # Buy & Hold karşılaştırması (başlangıçta al, sonuna kadar tut)
    first_price = df["Close"].iloc[0]
    df["BuyHold_Value"] = (df["Close"] / first_price) * initial_capital

    return df, buy_dates, sell_dates


def strategy_performance(strategy_df: pd.DataFrame, initial_capital: float = 10_000.0) -> dict:
    """
    Strateji performans özetini hesaplar.

    Args:
        strategy_df: golden_cross_strategy çıktısı
        initial_capital: Başlangıç sermayesi

    Returns:
        Performans metrikleri sözlüğü
    """
    final_strategy = strategy_df["Strategy_Value"].iloc[-1]
    final_buyhold = strategy_df["BuyHold_Value"].iloc[-1]

    strategy_return = (final_strategy / initial_capital - 1) * 100
    buyhold_return = (final_buyhold / initial_capital - 1) * 100

    # Strateji işlem sayısı
    buys = (strategy_df["Position"] == 1).sum()
    sells = (strategy_df["Position"] == -1).sum()

    return {
        "Başlangıç Sermayesi (TL)": f"{initial_capital:,.0f}",
        "Strateji Final Değeri (TL)": f"{final_strategy:,.2f}",
        "Buy & Hold Final Değeri (TL)": f"{final_buyhold:,.2f}",
        "Strateji Toplam Getiri (%)": f"{strategy_return:.2f}",
        "Buy & Hold Getiri (%)": f"{buyhold_return:.2f}",
        "Fark (%)": f"{strategy_return - buyhold_return:.2f}",
        "Toplam AL İşlemi": buys,
        "Toplam SAT İşlemi": sells,
        "Kazanan Strateji": "Golden Cross" if strategy_return > buyhold_return else "Buy & Hold",
    }
