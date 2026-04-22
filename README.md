# 📈 S&P 500 Stock Analysis & Decision Dashboard

An interactive decision-support tool for individual investors and finance students to compare S&P 500 stocks, explore risk-return trade-offs, and receive data-driven investment recommendations tailored to their risk profile.

**ACC102 Mini Assignment — Track 4: Interactive Data Analysis Tool**

> **To run the app:** `streamlit run app.py`

---

## 1. Problem & User

**Analytical problem:** Given a set of S&P 500 stocks, which offers the best risk-adjusted return — and which is most suitable for different investor risk profiles (Conservative, Balanced, or Aggressive)?

Most individual investors struggle to objectively compare stocks beyond simple price charts. This tool addresses that gap by computing risk metrics, visualising trade-offs, and generating a personalised recommendation — turning raw data into actionable investment guidance.

**Target users:** Individual investors and finance students who want to compare stocks and understand which best fits their risk appetite, without needing to write code or use expensive financial software.

---

## 2. Data

| Field | Details |
|-------|---------|
| Source | S&P 500 Companies, Historical Prices (Cam Nugent) |
| Platform | Kaggle — https://www.kaggle.com/datasets/camnugent/sandp500 |
| Access date | April 2026 |
| Period | February 2013 to February 2018 |
| Coverage | 505 S&P 500 component stocks |
| Key fields | Date, Open, High, Low, Close, Volume, Ticker |
| File | `sp500_data.csv.gz` (compressed CSV, ~9 MB, included in repository) |

No internet connection or API key is required. All data is bundled locally in the repository.

---

## 3. Methods

| Step | Python Implementation |
|------|----------------------|
| Data loading | `pandas.read_csv()` with gzip decompression — no API needed |
| Data filtering | Boolean indexing by ticker and date range |
| Moving averages | `pandas.rolling().mean()` — MA20 and MA50 |
| Daily returns | `pandas.pct_change()` |
| Cumulative returns | Compounding daily returns with `cumprod()` |
| Sharpe Ratio | Annualised: `(mean / std) × √252` — measures risk-adjusted return |
| Maximum Drawdown | `cummax()` to find peak, then worst trough relative to peak |
| Correlation matrix | `pandas.DataFrame.corr()` on daily returns across selected stocks |
| Risk-Return scatter | `matplotlib.scatter` plotting volatility vs total return per stock |
| Auto-conclusion | Rule-based logic using Sharpe, volatility, and drawdown metrics |
| Investor profiling | Classifies each stock as Conservative / Balanced / Aggressive |
| Visualisation | `matplotlib` — line charts, bar charts, histograms, scatter, heatmap |
| Interactive interface | `streamlit` — multiselect, date pickers, radio buttons, tables, download |

---

## 4. Key Findings

*(Based on AAPL vs MSFT, January 2016 – February 2018)*

- **AAPL delivered higher total return** (~103%) but with higher daily volatility (~1.35%), making it more suitable for aggressive investors seeking growth
- **MSFT offered a better Sharpe Ratio**, meaning stronger risk-adjusted performance — the preferred choice for balanced investors who weigh return against risk
- **Correlation analysis** revealed moderate positive correlation between AAPL and MSFT, suggesting they move together to a degree and offer limited diversification benefit when held together
- **Volume spikes aligned with major price moves**, confirming that high-volume down days represent sentiment-driven selling rather than fundamental deterioration
- **Max Drawdown** for both stocks remained within typical large-cap ranges, indicating resilience during the 2016–2018 period

---

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

---

## 6. Project Structure

```
├── app.py                  # Streamlit interactive dashboard (main product)
├── notebook.ipynb          # Jupyter Notebook — full analytical workflow
├── sp500_data.csv.gz       # Local dataset (505 S&P 500 stocks, 2013–2018)
├── requirements.txt        # Python dependencies (streamlit, pandas, matplotlib, numpy)
└── README.md               # This file
```

---

## 7. Dashboard Features

| Feature | Description |
|---------|-------------|
| 505 stocks available | Select any S&P 500 component from the dropdown |
| Investor profile | Choose Conservative / Balanced / Aggressive to personalise the analysis |
| Auto recommendation | Tool generates a written investment conclusion based on the data |
| Risk vs Return scatter | Visual comparison of all selected stocks on a risk-reward chart |
| Correlation heatmap | Shows how selected stocks move together — identifies diversification value |
| Moving averages | MA20 and MA50 overlaid on price charts with golden/death cross explanation |
| Volume analysis | Colour-coded daily volume with behavioural interpretation |
| Return distribution | Histogram showing volatility profile of each stock |
| CSV export | Download the full summary statistics table |
| Offline operation | All data is local — no API, no internet required |

---

## 8. Limitations & Next Steps

**Current limitations:**
- Data covers 2013–2018 only; does not reflect post-2018 market conditions
- Historical analysis cannot predict future prices
- Moving averages are lagging indicators — signals may arrive late
- Sharpe Ratio assumes a risk-free rate of 0%, slightly overstating risk-adjusted return
- Does not account for dividends or transaction costs
- Correlation analysis uses daily returns only; does not capture longer-term structural relationships

**Possible improvements:**
- Connect to a live data API for real-time analysis
- Add rolling Sharpe Ratio and rolling volatility charts
- Include S&P 500 index as a benchmark for comparison
- Add portfolio-level optimisation (e.g. minimum variance portfolio)

---

## 9. Disclaimer

This tool is for **educational purposes only** and does not constitute financial or investment advice.
