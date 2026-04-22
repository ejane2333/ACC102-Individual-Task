"""
S&P 500 Stock Analysis Dashboard
ACC102 Mini Assignment - Track 4: Interactive Data Analysis Tool

Target User: Individual investors and finance students
Data Source: S&P 500 historical stock data (Kaggle, 2013-2018)
             Dataset: https://www.kaggle.com/datasets/camnugent/sandp500
             Accessed: April 2026

To run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="S&P 500 Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# ============================================================
# Load Data (cached so it only loads once)
# ============================================================
@st.cache_data
def load_data():
    """Load the S&P 500 dataset from local CSV."""
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp500_data.csv.gz")
    df = pd.read_csv(data_path, parse_dates=["Date"])
    df = df.sort_values(["Ticker", "Date"])
    return df

# ============================================================
# App Header
# ============================================================
st.title("📈 S&P 500 Stock Analysis Dashboard")
st.markdown(
    "An interactive tool for individual investors and finance students to explore "
    "historical stock performance, compare companies, and assess risk. "
    "Data covers **505 S&P 500 companies** from **2013 to 2018**."
)

# Load data
with st.spinner("Loading dataset..."):
    try:
        full_df = load_data()
        all_tickers = sorted(full_df["Ticker"].unique())
    except FileNotFoundError:
        st.error(
            "Data file `sp500_data.csv.gz` not found. "
            "Please ensure it is in the same folder as app.py."
        )
        st.stop()

# ============================================================
# Sidebar: User Inputs
# ============================================================
st.sidebar.header("⚙️ Settings")

st.sidebar.markdown(f"**{len(all_tickers)} stocks available**")

selected_tickers = st.sidebar.multiselect(
    "Select stock(s) to analyse",
    options=all_tickers,
    default=["AAPL", "MSFT"],
    help="You can select up to 5 stocks for comparison."
)

date_min = full_df["Date"].min().date()
date_max = full_df["Date"].max().date()

start_date = st.sidebar.date_input(
    "Start date",
    value=pd.Timestamp("2016-01-01"),
    min_value=date_min,
    max_value=date_max
)
end_date = st.sidebar.date_input(
    "End date",
    value=pd.Timestamp("2018-02-07"),
    min_value=date_min,
    max_value=date_max
)

analyse_button = st.sidebar.button("🔍 Analyse", type="primary")

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: S&P 500 Companies, Historical Prices. "
    "Source: Kaggle (Cam Nugent). Accessed April 2026."
)

# ============================================================
# Helper Functions
# ============================================================

def get_stock_data(ticker, df, start, end):
    """Filter dataset for one ticker and date range."""
    mask = (
        (df["Ticker"] == ticker) &
        (df["Date"] >= pd.Timestamp(start)) &
        (df["Date"] <= pd.Timestamp(end))
    )
    result = df[mask].copy()
    result = result.set_index("Date")
    return result if not result.empty else None


def compute_indicators(df):
    """Calculate technical indicators."""
    df = df.copy()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["Daily_Return"] = df["Close"].pct_change() * 100
    df["Cumulative_Return"] = (1 + df["Close"].pct_change()).cumprod() - 1
    return df


def compute_risk_metrics(df):
    """Calculate Sharpe Ratio and Maximum Drawdown."""
    daily_ret = df["Close"].pct_change().dropna()
    sharpe = (daily_ret.mean() / daily_ret.std()) * (252 ** 0.5) if daily_ret.std() != 0 else 0
    cumulative = (1 + daily_ret).cumprod()
    running_max = cumulative.cummax()
    max_drawdown = ((cumulative - running_max) / running_max).min() * 100
    return round(sharpe, 2), round(max_drawdown, 2)


def build_summary(ticker, df, sharpe, max_dd):
    """Build a one-row summary for one stock."""
    return {
        "Ticker": ticker,
        "Start": df.index.min().strftime("%Y-%m-%d"),
        "End": df.index.max().strftime("%Y-%m-%d"),
        "Trading Days": len(df),
        "Highest Price ($)": round(df["High"].max(), 2),
        "Lowest Price ($)": round(df["Low"].min(), 2),
        "Mean Close ($)": round(df["Close"].mean(), 2),
        "Total Return (%)": round(df["Cumulative_Return"].iloc[-1] * 100, 2),
        "Avg Daily Return (%)": round(df["Daily_Return"].mean(), 3),
        "Volatility (%)": round(df["Daily_Return"].std(), 3),
        "Sharpe Ratio": sharpe,
        "Max Drawdown (%)": max_dd,
    }


# ============================================================
# Main Analysis
# ============================================================

if analyse_button:

    # --- Validation ---
    if not selected_tickers:
        st.error("Please select at least one stock from the sidebar.")
        st.stop()
    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()
    if len(selected_tickers) > 5:
        st.warning("For clarity, please select no more than 5 stocks.")

    # --- Fetch & Process ---
    all_data = {}
    summaries = []

    for ticker in selected_tickers:
        df = get_stock_data(ticker, full_df, start_date, end_date)
        if df is None:
            st.warning(f"⚠️ No data found for **{ticker}** in the selected date range.")
            continue
        df = compute_indicators(df)
        sharpe, max_dd = compute_risk_metrics(df)
        all_data[ticker] = df
        summaries.append(build_summary(ticker, df, sharpe, max_dd))

    if not all_data:
        st.error("No valid data found. Please adjust your stock selection or date range.")
        st.stop()

    # -------------------------------------------------------
    # Section 1: Summary Statistics
    # -------------------------------------------------------
    st.header("1. Summary Statistics")
    summary_df = pd.DataFrame(summaries)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    st.markdown(
        "**How to read:** Total Return shows the overall gain/loss over the period. "
        "Volatility is the standard deviation of daily returns — higher means more risk. "
        "Sharpe Ratio measures return per unit of risk (higher is better). "
        "Max Drawdown is the worst peak-to-trough loss."
    )

    # -------------------------------------------------------
    # Section 2: Price Trend & Moving Averages
    # -------------------------------------------------------
    st.header("2. Price Trend & Moving Averages")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    for ticker, df in all_data.items():
        ax1.plot(df.index, df["Close"], label=f"{ticker}", linewidth=1.5)
        if len(all_data) == 1:
            ax1.plot(df.index, df["MA20"], label="MA20", linestyle="--",
                     color="orange", alpha=0.8)
            ax1.plot(df.index, df["MA50"], label="MA50", linestyle="--",
                     color="red", alpha=0.8)
    ax1.set_title("Closing Price" + (" & Moving Averages" if len(all_data) == 1 else " Comparison"),
                  fontsize=14)
    ax1.set_ylabel("Price (USD)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    fig1.tight_layout()
    st.pyplot(fig1)

    if len(all_data) == 1:
        st.markdown(
            "**Insight:** The MA20 (20-day moving average) tracks short-term trend. "
            "The MA50 (50-day) tracks medium-term trend. "
            "When MA20 crosses above MA50, this is called a *golden cross* — "
            "a potential signal of upward momentum."
        )

    # -------------------------------------------------------
    # Section 3: Trading Volume
    # -------------------------------------------------------
    st.header("3. Trading Volume")
    for ticker, df in all_data.items():
        fig_v, ax_v = plt.subplots(figsize=(12, 3))
        colors = ["#4CAF50" if r >= 0 else "#F44336"
                  for r in df["Daily_Return"].fillna(0)]
        ax_v.bar(df.index, df["Volume"], color=colors, alpha=0.7, width=1)
        ax_v.set_title(
            f"{ticker} — Daily Volume  (green = price up, red = price down)",
            fontsize=12
        )
        ax_v.set_ylabel("Volume")
        ax_v.grid(True, alpha=0.3)
        fig_v.tight_layout()
        st.pyplot(fig_v)
    st.markdown(
        "**Insight:** High-volume days on down days often signal panic selling. "
        "High volume on up days suggests strong buying interest."
    )

    # -------------------------------------------------------
    # Section 4: Daily Return Distribution
    # -------------------------------------------------------
    st.header("4. Daily Return Distribution")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    for ticker, df in all_data.items():
        ax3.hist(df["Daily_Return"].dropna(), bins=60,
                 alpha=0.55, label=ticker, edgecolor="white")
    ax3.axvline(x=0, color="black", linestyle="--", linewidth=1)
    ax3.set_title("Distribution of Daily Returns", fontsize=14)
    ax3.set_xlabel("Daily Return (%)")
    ax3.set_ylabel("Frequency")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    fig3.tight_layout()
    st.pyplot(fig3)
    st.markdown(
        "**Insight:** A bell-shaped distribution centred near zero is typical for stocks. "
        "A wider bell means higher volatility. "
        "Fat tails (extreme values) indicate the stock has experienced large unexpected moves."
    )

    # -------------------------------------------------------
    # Section 5: Cumulative Return Comparison
    # -------------------------------------------------------
    st.header("5. Cumulative Return Comparison")
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    for ticker, df in all_data.items():
        ax4.plot(df.index, df["Cumulative_Return"] * 100,
                 label=ticker, linewidth=1.8)
    ax4.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax4.set_title("Cumulative Return Over Time (%)", fontsize=14)
    ax4.set_ylabel("Cumulative Return (%)")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    fig4.tight_layout()
    st.pyplot(fig4)
    st.markdown(
        "**Insight:** This chart shows what would have happened if you had invested "
        "$1 in each stock at the start date. "
        "The stock finishing highest delivered the best total return over this period."
    )

    # -------------------------------------------------------
    # Section 6: Risk Assessment
    # -------------------------------------------------------
    st.header("6. Risk Assessment")
    risk_rows = [{
        "Ticker": s["Ticker"],
        "Total Return (%)": s["Total Return (%)"],
        "Volatility (%)": s["Volatility (%)"],
        "Sharpe Ratio": s["Sharpe Ratio"],
        "Max Drawdown (%)": s["Max Drawdown (%)"],
    } for s in summaries]
    st.dataframe(pd.DataFrame(risk_rows), use_container_width=True, hide_index=True)

    st.markdown(
        "**How to interpret:**\n"
        "- **Sharpe Ratio > 1:** Return is good relative to risk taken.\n"
        "- **Max Drawdown:** The worst loss from a peak — e.g. -30% means the stock "
        "fell 30% from its highest point before recovering.\n"
        "- **Volatility:** Higher means the stock price swings more day to day."
    )

    # -------------------------------------------------------
    # Section 7: Download Results
    # -------------------------------------------------------
    st.header("7. Download Results")
    st.download_button(
        label="📥 Download summary as CSV",
        data=summary_df.to_csv(index=False),
        file_name="stock_analysis_summary.csv",
        mime="text/csv",
    )

    st.divider()
    st.caption(
        "Data: S&P 500 Companies, Historical Prices (Kaggle, Cam Nugent). "
        "Period: 2013–2018. Accessed April 2026. "
        "For educational purposes only. Not investment advice."
    )

else:
    # -------------------------------------------------------
    # Landing page (before clicking Analyse)
    # -------------------------------------------------------
    st.info("👈 Select one or more stocks in the sidebar, choose a date range, then click **Analyse**.")

    st.markdown("### What this tool does")
    st.markdown(
        "This dashboard lets you explore the historical performance of any S&P 500 company. "
        "Select one stock for a detailed single-stock analysis, "
        "or select multiple stocks to compare them side by side.\n\n"
        "**Available analysis:**\n"
        "- Price trend with 20-day and 50-day moving averages\n"
        "- Trading volume patterns\n"
        "- Daily return distribution\n"
        "- Cumulative return comparison\n"
        "- Risk metrics: Sharpe Ratio and Maximum Drawdown\n"
        "- Downloadable summary CSV"
    )

    st.markdown("### Available stocks (sample)")
    sample = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JPM", "GS", "WMT", "KO", "NFLX"]
    st.code(", ".join(sample) + f"  ... and {len(all_tickers) - len(sample)} more")
