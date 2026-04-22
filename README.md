# 📈 S&P 500 Stock Analysis Dashboard

An interactive Streamlit tool for individual investors and finance students to explore historical stock performance, compare companies, and assess investment risk.

**ACC102 Mini Assignment — Track 4: Interactive Data Analysis Tool**

---

## 1. Problem & User

Individual investors often find it difficult to quickly compare stocks, understand price trends, or assess risk without using complex financial software. This tool provides a simple, interactive dashboard that lets users explore historical stock data for any of the 505 S&P 500 companies — no coding required.

**Target users:** Individual investors and finance students with basic stock market knowledge.

## 2. Data

- **Source:** S&P 500 Companies, Historical Prices (Cam Nugent)
- **Platform:** Kaggle — https://www.kaggle.com/datasets/camnugent/sandp500
- **Access date:** April 2026
- **Period covered:** February 2013 to February 2018
- **Coverage:** 505 S&P 500 component stocks
- **Key fields:** Date, Open, High, Low, Close, Volume, Ticker
- **File:** `sp500_data.csv.gz` (compressed CSV, ~9 MB, included in this repository)

No internet connection or API key is required to run this tool. All data is bundled locally.

## 3. Methods

| Step | Python Method |
|------|--------------|
| Data loading | `pandas.read_csv()` with gzip decompression |
| Data filtering | Boolean indexing by ticker and date range |
| Moving averages | `pandas.rolling().mean()` — MA20 and MA50 |
| Daily returns | `pandas.pct_change()` |
| Cumulative returns | Compounding daily returns with `cumprod()` |
| Risk: Sharpe Ratio | Annualised mean/std of daily returns × √252 |
| Risk: Max Drawdown | Peak-to-trough decline using `cummax()` |
| Visualisation | `matplotlib` — price charts, bar charts, histograms |
| Interactive interface | `streamlit` — multiselect, date pickers, tables, download button |

## 4. Key Findings

*(Based on AAPL vs MSFT, January 2016 – February 2018)*

- Both stocks showed strong upward trends, with AAPL delivering a higher total return
- AAPL exhibited slightly higher volatility than MSFT, consistent with its growth profile
- Volume spikes aligned closely with major price movements, reflecting market sentiment
- Both stocks achieved Sharpe Ratios above 1.0, indicating favourable risk-adjusted returns
- Maximum Drawdown for both stocks remained within typical large-cap ranges

## 5. How to Run

**Prerequisites:** Python 3.8+ and pip

```bash
# 1. Clone the repository
git clone https://github.com/ejane2333/ACC102-Individual-Task.git
cd ACC102-Individual-Task

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

## 6. Project Structure

```
├── app.py                  # Streamlit interactive dashboard (main product)
├── notebook.ipynb          # Jupyter Notebook — full analytical workflow
├── sp500_data.csv.gz       # Local dataset (505 S&P 500 stocks, 2013-2018)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 7. Features

- **505 stocks available** — select any S&P 500 component from the dropdown
- **Multi-stock comparison** — select up to 5 stocks and compare side by side
- **Moving averages** — MA20 and MA50 overlaid on price charts
- **Risk metrics** — Sharpe Ratio and Maximum Drawdown per stock
- **Volume analysis** — colour-coded daily volume (green = up day, red = down day)
- **CSV export** — download the summary statistics table
- **No API required** — all data is local, works fully offline

## 8. Limitations & Next Steps

**Limitations:**
- Data covers 2013–2018 only; does not reflect recent market conditions
- Historical analysis only — cannot predict future prices
- Moving averages are lagging indicators
- Sharpe Ratio assumes a risk-free rate of 0%
- Does not include dividends or transaction costs

**Possible improvements:**
- Connect to a live data API for more recent prices
- Add sector-level analysis and S&P 500 index benchmarking
- Include dividend-adjusted returns
- Add portfolio optimisation features

## 9. Disclaimer

This tool is for **educational purposes only** and does not constitute investment advice.
