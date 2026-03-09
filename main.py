import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import load_stock_data, merge_stocks
from src.returns import compute_summary, compute_cumulative_returns
from src.portfolio import compute_correlation, golden_cross_strategy, strategy_performance
from src.visualization import (
    plot_price_with_ma,
    plot_rsi,
    plot_daily_returns,
    plot_cumulative_returns,
    plot_correlation_heatmap,
    plot_strategy,
    plot_volatility_comparison,
)

STOCK_NAMES     = ["THYAO", "ASELS", "TUPRS"]
DATA_DIR        = "data"
INITIAL_CAPITAL = 10_000
STRATEGY_STOCK  = "THYAO"

print("=" * 60)
print("  BIST Hisse Senedi Analizi")
print("=" * 60)

print("\n[1/6] Veriler yükleniyor...")
stock_dfs = []
for name in STOCK_NAMES:
    df = load_stock_data(os.path.join(DATA_DIR, f"{name}.csv"), name)
    stock_dfs.append(df)
    print(f"  ✓ {name}: {len(df)} satır")

data = merge_stocks(stock_dfs)
print(f"\n  {data['Date'].min().date()} — {data['Date'].max().date()} | {len(data)} işlem günü")

print("\n[2/6] Performans metrikleri...")
summary = compute_summary(data, STOCK_NAMES)
print(summary.to_string())

print("\n[3/6] Korelasyon matrisi...")
corr = compute_correlation(data, STOCK_NAMES)
print(corr.to_string())

print(f"\n[4/6] Golden Cross stratejisi ({STRATEGY_STOCK})...")
strategy_df, buy_dates, sell_dates = golden_cross_strategy(
    data, stock=STRATEGY_STOCK, initial_capital=INITIAL_CAPITAL
)
for k, v in strategy_performance(strategy_df, INITIAL_CAPITAL).items():
    print(f"  {k:<35}: {v}")

print("\n[5/6] Grafikler oluşturuluyor...")
cum_df = compute_cumulative_returns(data, STOCK_NAMES)
plot_cumulative_returns(cum_df, STOCK_NAMES)
for stock in STOCK_NAMES:
    plot_price_with_ma(data, stock)
    plot_rsi(data, stock)
plot_daily_returns(data, STOCK_NAMES)
plot_volatility_comparison(data, STOCK_NAMES)
plot_correlation_heatmap(corr)
plot_strategy(strategy_df, buy_dates, sell_dates, STRATEGY_STOCK)

print("\n[6/6] Tamamlandı.")
print("=" * 60)
