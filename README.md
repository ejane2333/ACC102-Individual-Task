# 📈 Stock Price Analysis Dashboard

An interactive Streamlit tool that helps individual investors and finance students quickly understand stock price trends, volatility, and risk.

**ACC102 Mini Assignment — Track 4: Interactive Data Analysis Tool**

---

## 1. Problem & User

Individual investors often struggle to quickly assess whether a stock is trending up or down, how volatile it is, and how it compares to alternatives. This tool addresses that problem by providing a one-click dashboard that retrieves real-time data from Yahoo Finance and presents key metrics, charts, and risk indicators in an accessible format.

**Target users:** Individual investors and finance students with basic stock market knowledge.

## 2. Data

- **Source:** Yahoo Finance, accessed via the `yfinance` Python library
- **Access date:** April 2026
- **Key fields:** Open, High, Low, Close, Volume (OHLCV)
- **Note:** Data is fetched in real time when the user clicks "Analyse". No local dataset file is required.

## 3. Methods

| Step | Python Method |
|------|--------------|
| Data retrieval | `yfinance` — download historical OHLCV data by ticker and date range |
| Data cleaning | `pandas` — drop null values, convert datetime index, remove timezone info |
| Feature engineering | `pandas` — 20-day and 50-day moving averages, daily returns, cumulative returns |
| Risk metrics | Custom functions — Sharpe Ratio (annualised), Maximum Drawdown |
| Visualisation | `matplotlib` — price trend, volume bars, return histogram, cumulative return chart |
| Interactive interface | `streamlit` — sidebar inputs, dynamic charts, data tables, CSV download |

## 4. Key Findings

*(Based on AAPL analysis, Jan 2023 – Dec 2024)*

- AAPL showed a strong upward trend over the two-year period, with the MA20 frequently crossing above the MA50 (golden cross signals)
- Daily return volatility was moderate, with most daily changes within ±2%
- Volume spikes coincided with major price drops, suggesting sentiment-driven selling
- The Sharpe Ratio indicated a favourable risk-adjusted return
- Maximum Drawdown remained within a manageable range for a large-cap stock

## 5. How to Run

**Prerequisites:** Python 3.8+ and pip

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <your-repo-folder>

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## 6. Project Structure

```
├── app.py               # Streamlit interactive dashboard (main product)
├── notebook.ipynb        # Jupyter Notebook showing the analytical workflow
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── figures/              # (Optional) saved chart images
```

## 7. Features

- **Multi-stock comparison:** Enter multiple tickers (e.g., AAPL, MSFT, TSLA) to compare side by side
- **Moving averages:** 20-day and 50-day moving average overlay on price charts
- **Risk metrics:** Sharpe Ratio and Maximum Drawdown for each stock
- **Volume analysis:** Colour-coded volume bars (green for up days, red for down days)
- **CSV export:** Download the summary statistics table as a CSV file

## 8. Limitations & Next Steps

**Limitations:**
- Historical data only — the tool does not predict future prices
- Moving averages are lagging indicators and may not capture sudden reversals
- Sharpe Ratio assumes a risk-free rate of 0%, which is a simplification
- yfinance data may have occasional gaps or delays

**Possible improvements:**
- Add sector or index benchmarking (e.g., compare against S&P 500)
- Include additional risk metrics such as Beta and Value at Risk (VaR)
- Add news sentiment integration for context
- Support for non-US markets

## 9. Disclaimer

This tool is for **educational purposes only** and does not constitute investment advice.
