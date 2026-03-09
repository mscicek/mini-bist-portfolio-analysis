<div align="center">

# 📈 BIST Hisse Senedi Analizi

**Borsa İstanbul hisselerini analiz eden, teknik indikatörler hesaplayan ve al-sat stratejilerini simüle eden Python uygulaması.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat-square&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7+-11557C?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## 📸 Ekran Görüntüleri

### Dashboard

> 📷 *`screenshots/dashboard.png` — Ana pencere: performans tablosu, strateji özeti ve grafik seçim paneli*

![Dashboard](screenshots/dashboard.png)

---

### Kümülatif Getiri Karşılaştırması

> 📷 *`screenshots/cumulative_returns.png` — THYAO, ASELS ve TUPRS normalize kümülatif getiri*

![Kümülatif Getiri](screenshots/cumulative_returns.png)

---

### Fiyat + Hareketli Ortalama + Bollinger Bantları

> 📷 *`screenshots/price_ma_bollinger.png` — Fiyat, MA20, MA50 ve Bollinger Bantları*

![Fiyat & MA](screenshots/price_ma_bollinger.png)

---

### RSI Göstergesi

> 📷 *`screenshots/rsi.png` — 14 günlük RSI, aşırı alım/si

![RSI](screenshots/rsi.png)

---

### Golden Cross Al-Sat Stratejisi

> 📷 *`screenshots/strategy.png` — Golden Cross stratejisi vs Buy & Hold portföy karşılaştırması*

![Strateji](screenshots/strategy.png)

---

### Korelasyon Isı Haritası

> 📷 *`screenshots/correlation.png` — Hisseler arası getiri korelasyonu*

![Korelasyon](screenshots/correlation.png)

---

## 🚀 Özellikler

| Kategori | Özellik |
|---|---|
| **Veri** | Investing.com & Yahoo Finance CSV desteği |
| **Teknik İndikatörler** | MA20, MA50, Bollinger Bantları, RSI (14) |
| **Risk Metrikleri** | Volatilite, Sharpe Ratio, Max Drawdown |
| **Portföy** | Kümülatif getiri, korelasyon matrisi |
| **Al-Sat** | Golden Cross stratejisi & Buy & Hold karşılaştırması |
| **Arayüz** | Dark-themed Tkinter dashboard — istediğin grafiği aç |

---

## 📁 Proje Yapısı

```
mini-bist-portfolio-analysis/
│
├── app.py               
├── main.py             
├── requirements.txt
├── README.md
│
├── data/
│   ├── THYAO.csv
│   ├── ASELS.csv
│   └── TUPRS.csv
│
├── screenshots/         
│
└── src/
    ├── data_loader.py  
    ├── returns.py      
    ├── portfolio.py    
    └── visualization.py
```

---

## ⚙️ Kurulum

```bash
pip install -r requirements.txt
```

---

## ▶️ Kullanım

### İnteraktif Dashboard (Önerilen)

```bash
python app.py
```

Açılan pencerede sağ panelden istediğin grafiği seçip açabilirsin.

### CLI Modu

```bash
python main.py
```

Grafikler sırayla otomatik açılır.

---

## � Teknik İndikatörler

| İndikatör | Parametre | Açıklama |
|---|---|---|
| MA20 | 20 gün | Kısa vadeli hareketli ortalama |
| MA50 | 50 gün | Uzun vadeli hareketli ortalama |
| Bollinger Bantları | 20 gün, 2σ | Fiyat volatilite kanalı |
| RSI | 14 gün (Wilder) | 70 → aşırı alım · 30 → aşırı satım |
| Sharpe Ratio | 252 işlem günü | Risk-düzeltmeli yıllık getiri |
| Max Drawdown | — | En büyük tepe-çukur kaybı |

---

## ⚡ Golden Cross Stratejisi

| Sinyal | Kural | Aksiyon |
|---|---|---|
| **AL** | MA20 > MA50 (yukarı kesiş) | Nakit → Hisse |
| **SAT** | MA20 < MA50 (aşağı kesiş) | Hisse → Nakit |

Sonuçlar **Buy & Hold** ile karşılaştırılır.

---

## 🔧 Yeni Hisse Ekleme

1. `data/HISSE.csv` dosyasını ekle (Investing.com formatı)
2. `app.py` ve `main.py` içindeki `STOCK_NAMES` listesini güncelle:

```python
STOCK_NAMES = ["THYAO", "ASELS", "TUPRS", "HISSE"]
```

---

## 📦 Bağımlılıklar

| Paket | Kullanım |
|---|---|
| `pandas` | Veri işleme |
| `numpy` | Sayısal hesaplama |
| `matplotlib` | Grafik |
| `scipy` | KDE (getiri dağılımı) |

---

> **⚠️ Uyarı:** Bu proje yalnızca eğitim amaçlıdır. Gerçek yatırım kararları için profesyonel danışmanlık alınız.
