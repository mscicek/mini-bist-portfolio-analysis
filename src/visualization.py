import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams.update({
    "figure.facecolor":  "#0d1117",
    "axes.facecolor":    "#161b22",
    "axes.edgecolor":    "#30363d",
    "axes.labelcolor":   "#c9d1d9",
    "axes.titlecolor":   "#f0f6fc",
    "axes.grid":         True,
    "grid.color":        "#21262d",
    "grid.linestyle":    "--",
    "grid.alpha":        0.6,
    "text.color":        "#c9d1d9",
    "xtick.color":       "#8b949e",
    "ytick.color":       "#8b949e",
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
    "legend.facecolor":  "#161b22",
    "legend.edgecolor":  "#30363d",
    "legend.labelcolor": "#c9d1d9",
    "legend.fontsize":   9,
    "figure.titlesize":  14,
    "figure.titleweight":"bold",
})

COLORS = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657"]


def _fmt_xaxis(ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))


def plot_price_with_ma(data: pd.DataFrame, stock: str) -> None:
    fig, ax = plt.subplots(figsize=(13, 5))
    fig.suptitle(f"{stock} — Fiyat, Hareketli Ortalama & Bollinger Bantları")

    dates    = data["Date"]
    close    = data[f"{stock}_Close"]
    ma20     = data[f"{stock}_MA20"]
    ma50     = data[f"{stock}_MA50"]
    bb_upper = data[f"{stock}_BB_Upper"]
    bb_lower = data[f"{stock}_BB_Lower"]

    ax.plot(dates, close, color=COLORS[0], linewidth=1.2, label="Kapanış Fiyatı")
    ax.plot(dates, ma20, color=COLORS[2], linewidth=1.0, linestyle="--", label="MA20")
    ax.plot(dates, ma50, color=COLORS[4], linewidth=1.0, linestyle="--", label="MA50")
    ax.fill_between(dates, bb_lower, bb_upper, alpha=0.12, color=COLORS[1], label="Bollinger Bantları")
    ax.plot(dates, bb_upper, color=COLORS[1], linewidth=0.6, linestyle=":")
    ax.plot(dates, bb_lower, color=COLORS[1], linewidth=0.6, linestyle=":")

    ax.set_xlabel("Tarih")
    ax.set_ylabel("Fiyat (TL)")
    ax.legend(loc="upper left")
    _fmt_xaxis(ax)
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()
    plt.show()


def plot_rsi(data: pd.DataFrame, stock: str) -> None:
    fig, ax = plt.subplots(figsize=(13, 3.5))
    fig.suptitle(f"{stock} — RSI (14 Günlük)")

    ax.plot(data["Date"], data[f"{stock}_RSI"], color=COLORS[3], linewidth=1.0, label="RSI")
    ax.axhline(70, color=COLORS[2], linestyle="--", linewidth=0.9, label="Aşırı Alım (70)")
    ax.axhline(30, color=COLORS[1], linestyle="--", linewidth=0.9, label="Aşırı Satım (30)")
    ax.fill_between(data["Date"], 70, 100, alpha=0.08, color=COLORS[2])
    ax.fill_between(data["Date"], 0, 30, alpha=0.08, color=COLORS[1])

    ax.set_ylim(0, 100)
    ax.set_xlabel("Tarih")
    ax.set_ylabel("RSI")
    ax.legend(loc="upper left")
    _fmt_xaxis(ax)
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()
    plt.show()


def plot_daily_returns(data: pd.DataFrame, stock_names: list[str]) -> None:
    from scipy.stats import gaussian_kde

    n    = len(stock_names)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    fig.suptitle("Günlük Getiri Dağılımı")

    if n == 1:
        axes = [axes]

    for ax, stock, color in zip(axes, stock_names, COLORS):
        returns = data[f"{stock}_Return"].dropna() * 100
        ax.hist(returns, bins=50, color=color, alpha=0.75, edgecolor="none", density=True)

        kde = gaussian_kde(returns)
        x   = np.linspace(returns.min(), returns.max(), 300)
        ax.plot(x, kde(x), color="white", linewidth=1.5, label="KDE")
        ax.axvline(returns.mean(), color=COLORS[4], linestyle="--", linewidth=1.0,
                   label=f"Ort: {returns.mean():.2f}%")

        ax.set_title(stock)
        ax.set_xlabel("Günlük Getiri (%)")
        ax.set_ylabel("Yoğunluk")
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.show()


def plot_cumulative_returns(cum_df: pd.DataFrame, stock_names: list[str]) -> None:
    fig, ax = plt.subplots(figsize=(13, 5))
    fig.suptitle("Kümülatif Getiri Karşılaştırması (Başlangıç = 100 TL)")

    for stock, color in zip(stock_names, COLORS):
        ax.plot(cum_df["Date"], cum_df[f"{stock}_Cumulative"], color=color, linewidth=1.4, label=stock)

    ax.axhline(100, color="#8b949e", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.set_xlabel("Tarih")
    ax.set_ylabel("Değer (TL)")
    ax.legend(loc="upper left")
    _fmt_xaxis(ax)
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()
    plt.show()


def plot_correlation_heatmap(corr_matrix: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.suptitle("Hisse Korelasyon Matrisi")

    n      = len(corr_matrix)
    im     = ax.imshow(corr_matrix.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    labels = corr_matrix.columns.tolist()

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    for i in range(n):
        for j in range(n):
            val        = corr_matrix.values[i, j]
            text_color = "black" if abs(val) > 0.5 else "white"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=11, color=text_color, fontweight="bold")

    plt.tight_layout()
    plt.show()


def plot_strategy(strategy_df: pd.DataFrame, buy_dates: list, sell_dates: list, stock: str) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True,
                                    gridspec_kw={"height_ratios": [2, 1]})
    fig.suptitle(f"{stock} — Golden Cross Stratejisi vs Buy & Hold")

    ax1.plot(strategy_df["Date"], strategy_df["Strategy_Value"],
             color=COLORS[1], linewidth=1.3, label="Golden Cross Stratejisi")
    ax1.plot(strategy_df["Date"], strategy_df["BuyHold_Value"],
             color=COLORS[0], linewidth=1.3, linestyle="--", label="Buy & Hold")

    for bd in buy_dates:
        ax1.axvline(bd, color=COLORS[1], linewidth=0.7, alpha=0.5)
    for sd in sell_dates:
        ax1.axvline(sd, color=COLORS[2], linewidth=0.7, alpha=0.5)

    ax1.scatter([], [], color=COLORS[1], marker="^", s=40, label="AL Sinyali")
    ax1.scatter([], [], color=COLORS[2], marker="v", s=40, label="SAT Sinyali")
    ax1.set_ylabel("Portföy Değeri (TL)")
    ax1.legend(loc="upper left")

    ax2.plot(strategy_df["Date"], strategy_df["Close"], color="#c9d1d9", linewidth=0.9, label="Fiyat")
    ax2.plot(strategy_df["Date"], strategy_df["MA20"], color=COLORS[2], linewidth=1.0, linestyle="--", label="MA20")
    ax2.plot(strategy_df["Date"], strategy_df["MA50"], color=COLORS[4], linewidth=1.0, linestyle="--", label="MA50")
    ax2.set_xlabel("Tarih")
    ax2.set_ylabel("Fiyat (TL)")
    ax2.legend(loc="upper left")

    _fmt_xaxis(ax2)
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()
    plt.show()


def plot_volatility_comparison(data: pd.DataFrame, stock_names: list[str], window: int = 30) -> None:
    fig, ax = plt.subplots(figsize=(13, 4.5))
    fig.suptitle("30 Günlük Rolling Volatilite Karşılaştırması")

    for stock, color in zip(stock_names, COLORS):
        rolling_vol = data[f"{stock}_Return"].rolling(window=window).std() * np.sqrt(252) * 100
        ax.plot(data["Date"], rolling_vol, color=color, linewidth=1.1, label=stock)

    ax.set_xlabel("Tarih")
    ax.set_ylabel("Yıllık Volatilite (%)")
    ax.legend(loc="upper left")
    _fmt_xaxis(ax)
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()
    plt.show()
