import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")

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

BG_DARK   = "#0d1117"
BG_PANEL  = "#161b22"
BG_CARD   = "#21262d"
BORDER    = "#30363d"
TEXT_PRI  = "#f0f6fc"
TEXT_SEC  = "#8b949e"
ACCENT    = "#58a6ff"
GREEN     = "#3fb950"
RED       = "#f78166"
PURPLE    = "#d2a8ff"
ORANGE    = "#ffa657"

FONT_TITLE = ("Segoe UI", 15, "bold")
FONT_HEAD  = ("Segoe UI", 10, "bold")
FONT_BODY  = ("Segoe UI", 9)
FONT_SMALL = ("Segoe UI", 8)
FONT_MONO  = ("Consolas", 9)

STOCK_NAMES = ["THYAO", "ASELS", "TUPRS"]
DATA_DIR    = "data"


class BistApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BIST Hisse Senedi Analizi Dashboard")
        self.geometry("1080x720")
        self.minsize(900, 600)
        self.configure(bg=BG_DARK)
        self._apply_style()

        self.data        = None
        self.summary_df  = None
        self.cum_df      = None
        self.corr_matrix = None
        self.strategy_df = None
        self.buy_dates   = []
        self.sell_dates  = []

        self._build_ui()
        self._load_data_async()

    def _apply_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".",
            background=BG_DARK, foreground=TEXT_PRI,
            fieldbackground=BG_PANEL, font=FONT_BODY)
        style.configure("TFrame", background=BG_DARK)
        style.configure("TLabel", background=BG_DARK, foreground=TEXT_PRI)
        style.configure("TCombobox",
            background=BG_CARD, foreground=TEXT_PRI,
            arrowcolor=TEXT_SEC)
        style.map("TCombobox",
            fieldbackground=[("readonly", BG_CARD)],
            foreground=[("readonly", TEXT_PRI)])
        style.configure("Treeview",
            background=BG_PANEL, foreground=TEXT_PRI,
            fieldbackground=BG_PANEL, rowheight=24, font=FONT_MONO)
        style.configure("Treeview.Heading",
            background=BG_CARD, foreground=ACCENT,
            font=FONT_HEAD, relief="flat")
        style.map("Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", BG_DARK)])
        style.configure("TScrollbar",
            background=BG_CARD, troughcolor=BG_DARK,
            arrowcolor=TEXT_SEC, borderwidth=0)

    def _build_ui(self):
        header = tk.Frame(self, bg=BG_PANEL, height=54)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📈  BIST Hisse Senedi Analizi Dashboard",
                 font=FONT_TITLE, bg=BG_PANEL, fg=TEXT_PRI).pack(side="left", padx=20, pady=12)
        self.status_var = tk.StringVar(value="⏳  Veriler yükleniyor...")
        tk.Label(header, textvariable=self.status_var,
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_SEC).pack(side="right", padx=20)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=12, pady=12)

        left = tk.Frame(content, bg=BG_DARK)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._build_summary_table(left)
        self._build_strategy_card(left)

        right = tk.Frame(content, bg=BG_DARK, width=310)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_chart_panel(right)

    def _build_summary_table(self, parent):
        card = tk.Frame(parent, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, pady=(0, 8))
        tk.Label(card, text="📊  Performans Özeti", font=FONT_HEAD,
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w", padx=12, pady=(10, 4))
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=8)

        cols     = ("Metrik", "THYAO", "ASELS", "TUPRS")
        tv_frame = tk.Frame(card, bg=BG_PANEL)
        tv_frame.pack(fill="both", expand=True, padx=8, pady=8)

        vsb = ttk.Scrollbar(tv_frame, orient="vertical")
        self.summary_tree = ttk.Treeview(tv_frame, columns=cols, show="headings",
                                          height=8, yscrollcommand=vsb.set)
        vsb.config(command=self.summary_tree.yview)
        vsb.pack(side="right", fill="y")
        self.summary_tree.pack(fill="both", expand=True)

        self.summary_tree.column("Metrik", width=190, anchor="w")
        for c in ("THYAO", "ASELS", "TUPRS"):
            self.summary_tree.column(c, width=90, anchor="center")
        for c in cols:
            self.summary_tree.heading(c, text=c)

        self.summary_tree.tag_configure("pos", foreground=GREEN)
        self.summary_tree.tag_configure("neg", foreground=RED)
        self.summary_tree.tag_configure("neu", foreground=TEXT_PRI)

        for _ in range(7):
            self.summary_tree.insert("", "end", values=("—", "—", "—", "—"))

    def _build_strategy_card(self, parent):
        card = tk.Frame(parent, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")
        tk.Label(card, text="⚡  Golden Cross Stratejisi — THYAO", font=FONT_HEAD,
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w", padx=12, pady=(10, 4))
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=8)

        self.strat_frame = tk.Frame(card, bg=BG_PANEL)
        self.strat_frame.pack(fill="x", padx=12, pady=8)

        for text in ["Yükleniyor...", "", "", "", "", ""]:
            tk.Label(self.strat_frame, text=text, font=FONT_MONO,
                     bg=BG_PANEL, fg=TEXT_SEC).pack(anchor="w")

    def _build_chart_panel(self, parent):
        tk.Label(parent, text="🎨  Grafik Seç", font=FONT_HEAD,
                 bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0, 6))

        sel_frame = tk.Frame(parent, bg=BG_DARK)
        sel_frame.pack(fill="x", pady=(0, 8))
        tk.Label(sel_frame, text="Hisse:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_SEC).pack(side="left")
        self.stock_var = tk.StringVar(value="THYAO")
        cb = ttk.Combobox(sel_frame, textvariable=self.stock_var,
                          values=STOCK_NAMES, state="readonly", width=10)
        cb.pack(side="left", padx=6)

        categories = [
            ("Tüm Hisseler", GREEN, [
                ("Kümülatif Getiri Karşılaştırması",  self._chart_cumulative),
                ("Günlük Getiri Dağılımı",            self._chart_returns_dist),
                ("Rolling Volatilite",                 self._chart_volatility),
                ("Korelasyon Isı Haritası",            self._chart_correlation),
            ]),
            ("Seçili Hisse", ORANGE, [
                ("Fiyat + MA + Bollinger Bantları",   self._chart_price_ma),
                ("RSI (14 Günlük)",                   self._chart_rsi),
            ]),
            ("Al-Sat Stratejisi", PURPLE, [
                ("Golden Cross — THYAO",              self._chart_strategy),
            ]),
        ]

        for cat_name, cat_color, buttons in categories:
            cat_frame = tk.Frame(parent, bg=BG_PANEL, highlightbackground=BORDER, highlightthickness=1)
            cat_frame.pack(fill="x", pady=4)
            tk.Label(cat_frame, text=cat_name, font=FONT_SMALL,
                     bg=BG_PANEL, fg=cat_color).pack(anchor="w", padx=10, pady=(6, 2))

            for btn_text, cmd in buttons:
                b = tk.Button(cat_frame, text=f"  {btn_text}",
                              font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRI,
                              activebackground=ACCENT, activeforeground=BG_DARK,
                              relief="flat", anchor="w", cursor="hand2",
                              bd=0, padx=8, pady=5, command=cmd)
                b.pack(fill="x", padx=6, pady=2)
                b.bind("<Enter>", lambda e, w=b: w.config(bg=BG_DARK, fg=ACCENT))
                b.bind("<Leave>", lambda e, w=b: w.config(bg=BG_CARD, fg=TEXT_PRI))

            tk.Frame(cat_frame, bg=BG_PANEL, height=4).pack()

    def _load_data_async(self):
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            stock_dfs = []
            for name in STOCK_NAMES:
                df = load_stock_data(os.path.join(DATA_DIR, f"{name}.csv"), name)
                stock_dfs.append(df)

            self.data        = merge_stocks(stock_dfs)
            self.summary_df  = compute_summary(self.data, STOCK_NAMES)
            self.cum_df      = compute_cumulative_returns(self.data, STOCK_NAMES)
            self.corr_matrix = compute_correlation(self.data, STOCK_NAMES)
            self.strategy_df, self.buy_dates, self.sell_dates = golden_cross_strategy(
                self.data, "THYAO", 10_000
            )
            self.after(0, self._on_data_loaded)
        except Exception as e:
            self.after(0, lambda: self._on_data_error(str(e)))

    def _on_data_loaded(self):
        d = self.data
        self.status_var.set(
            f"✅  {len(d)} işlem günü  |  {d['Date'].min().date()} — {d['Date'].max().date()}"
        )
        self._populate_summary_table()
        self._populate_strategy_card()

    def _on_data_error(self, msg):
        self.status_var.set(f"❌  Hata: {msg}")
        messagebox.showerror("Veri Yükleme Hatası", msg)

    def _populate_summary_table(self):
        tree = self.summary_tree
        for row in tree.get_children():
            tree.delete(row)

        df   = self.summary_df
        rows = [
            ("Ort. Günlük Getiri (%)",  "Ort. Günlük Getiri (%)"),
            ("Yıllık Getiri (%)",        "Yıllık Getiri (%)"),
            ("Volatilite (Günlük %)",    "Volatilite (Günlük %)"),
            ("Yıllık Volatilite (%)",    "Yıllık Volatilite (%)"),
            ("Sharpe Ratio",             "Sharpe Ratio"),
            ("Max Drawdown (%)",         "Max Drawdown (%)"),
            ("Toplam Getiri (%)",        "Toplam Getiri (%)"),
        ]

        for label, col in rows:
            vals = [str(df.loc[s, col]) for s in STOCK_NAMES]
            try:
                first = float(vals[0])
                tag   = "neu" if "Drawdown" in col or "Volatilite" in col else ("pos" if first >= 0 else "neg")
            except ValueError:
                tag = "neu"
            tree.insert("", "end", values=(label, *vals), tags=(tag,))

    def _populate_strategy_card(self):
        for w in self.strat_frame.winfo_children():
            w.destroy()

        perf   = strategy_performance(self.strategy_df, initial_capital=10_000)
        colors = {
            "Başlangıç Sermayesi (TL)":    TEXT_SEC,
            "Strateji Final Değeri (TL)":  GREEN,
            "Buy & Hold Final Değeri (TL)": ORANGE,
            "Strateji Toplam Getiri (%)":  GREEN,
            "Buy & Hold Getiri (%)":       ORANGE,
            "Fark (%)":                    ACCENT,
            "Toplam AL İşlemi":            GREEN,
            "Toplam SAT İşlemi":           RED,
            "Kazanan Strateji":            PURPLE,
        }

        for key, val in perf.items():
            row = tk.Frame(self.strat_frame, bg=BG_PANEL)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{key}:", font=FONT_SMALL,
                     bg=BG_PANEL, fg=TEXT_SEC, width=30, anchor="w").pack(side="left")
            tk.Label(row, text=str(val), font=FONT_MONO,
                     bg=BG_PANEL, fg=colors.get(key, TEXT_PRI)).pack(side="left")

    def _require_data(self) -> bool:
        if self.data is None:
            messagebox.showwarning("Uyarı", "Veriler henüz yüklenmedi. Lütfen bekleyin.")
            return False
        return True

    def _open_chart(self, fn, *args):
        if not self._require_data():
            return
        self.after(0, lambda: fn(*args))

    def _chart_cumulative(self):
        self._open_chart(plot_cumulative_returns, self.cum_df, STOCK_NAMES)

    def _chart_returns_dist(self):
        self._open_chart(plot_daily_returns, self.data, STOCK_NAMES)

    def _chart_volatility(self):
        self._open_chart(plot_volatility_comparison, self.data, STOCK_NAMES)

    def _chart_correlation(self):
        self._open_chart(plot_correlation_heatmap, self.corr_matrix)

    def _chart_price_ma(self):
        self._open_chart(plot_price_with_ma, self.data, self.stock_var.get())

    def _chart_rsi(self):
        self._open_chart(plot_rsi, self.data, self.stock_var.get())

    def _chart_strategy(self):
        self._open_chart(plot_strategy, self.strategy_df, self.buy_dates, self.sell_dates, "THYAO")


if __name__ == "__main__":
    BistApp().mainloop()
