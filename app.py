"""
Stock Price Analysis Dashboard
ACC102 Mini Assignment - Track 4: Interactive Data Analysis Tool

Target User: Individual investors and finance students
Data Source: Yahoo Finance (via yfinance library)

This Streamlit app allows users to:
1. Look up any stock by ticker symbol
2. Compare multiple stocks side by side
3. View price trends, moving averages, volume, and return distributions
4. Assess risk via Sharpe Ratio and Maximum Drawdown
5. Download analysis results as CSV
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Price Analysis Dashboard")
st.markdown(
    "A simple tool for individual investors and finance students "
    "to quickly understand stock price trends, volatility, and risk. "
    "Data is retrieved in real time from **Yahoo Finance**."
)

# ============================================================
# Sidebar: User Inputs
# ============================================================
st.sidebar.header("Settings")

tickers_input = st.sidebar.text_input(
    "Enter stock ticker(s), separated by commas",
    value="AAPL, MSFT",
    help="Examples: AAPL, TSLA, GOOGL, MSFT, AMZN"
)

# Parse ticker input
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

start_date = st.sidebar.date_input("Start date", value=pd.Timestamp("2023-01-01"))
end_date = st.sidebar.date_input("End date", value=pd.Timestamp("2024-12-31"))

analyse_button = st.sidebar.button("🔍 Analyse", type="primary")

# ============================================================
# Helper Functions
# ============================================================

@st.cache_data(show_spinner=False)
def fetch_stock_data(ticker, start, end):
    """Fetch and clean stock data from Yahoo Finance."""
    stock = yf.Ticker(ticker)
    df = stock.history(start=start, end=end)
    if df.empty:
        return None
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.dropna(inplace=True)
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)
    return df


def compute_indicators(df):
    """Calculate technical indicators and statistics."""
    df = df.copy()
    # Moving averages
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    # Daily returns
    df["Daily_Return"] = df["Close"].pct_change() * 100
    # Cumulative return
    df["Cumulative_Return"] = (1 + df["Close"].pct_change()).cumprod() - 1
    return df


def compute_risk_metrics(df):
    """Calculate Sharpe Ratio and Maximum Drawdown."""
    daily_ret = df["Close"].pct_change().dropna()

    # Annualised Sharpe Ratio (assuming 252 trading days, risk-free rate = 0)
    if daily_ret.std() == 0:
        sharpe = 0
    else:
        sharpe = (daily_ret.mean() / daily_ret.std()) * (252 ** 0.5)

    # Maximum Drawdown
    cumulative = (1 + daily_ret).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min() * 100  # as percentage

    return round(sharpe, 2), round(max_drawdown, 2)


def build_summary(ticker, df, sharpe, max_dd):
    """Build a summary dictionary for one stock."""
    return {
        "Ticker": ticker,
        "Start": df.index.min().strftime("%Y-%m-%d"),
        "End": df.index.max().strftime("%Y-%m-%d"),
        "Records": len(df),
        "Highest Price ($)": round(df["High"].max(), 2),
        "Lowest Price ($)": round(df["Low"].min(), 2),
        "Mean Close ($)": round(df["Close"].mean(), 2),
        "Total Return (%)": round(df["Cumulative_Return"].iloc[-1] * 100, 2),
        "Avg Daily Change (%)": round(df["Daily_Return"].mean(), 2),
        "Volatility (Std %)": round(df["Daily_Return"].std(), 2),
        "Sharpe Ratio": sharpe,
        "Max Drawdown (%)": max_dd,
    }


# ============================================================
# Main Analysis
# ============================================================

if analyse_button:
    if not tickers:
        st.error("Please enter at least one ticker symbol.")
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    # Fetch data for all tickers
    all_data = {}
    summaries = []

    with st.spinner("Fetching data from Yahoo Finance..."):
        for ticker in tickers:
            df = fetch_stock_data(ticker, str(start_date), str(end_date))
            if df is None or df.empty:
                st.warning(f"⚠️ No data found for **{ticker}**. Please check the ticker symbol.")
                continue
            df = compute_indicators(df)
            sharpe, max_dd = compute_risk_metrics(df)
            all_data[ticker] = df
            summaries.append(build_summary(ticker, df, sharpe, max_dd))

    if not all_data:
        st.error("No valid data retrieved. Please check your ticker symbols and date range.")
        st.stop()

    # ----------------------------------------------------------
    # Section 1: Summary Table
    # ----------------------------------------------------------
    st.header("1. Summary Statistics")

    summary_df = pd.DataFrame(summaries)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown(
        "**How to read this table:** "
        "Total Return shows how much the stock gained or lost over the period. "
        "Volatility (standard deviation of daily returns) measures price fluctuation. "
        "The Sharpe Ratio relates return to risk — higher is better. "
        "Max Drawdown shows the worst peak-to-trough decline."
    )

    # ----------------------------------------------------------
    # Section 2: Price Trend with Moving Averages
    # ----------------------------------------------------------
    st.header("2. Price Trend & Moving Averages")

    fig1, ax1 = plt.subplots(figsize=(12, 5))
    for ticker, df in all_data.items():
        ax1.plot(df.index, df["Close"], label=f"{ticker} Close", linewidth=1.5)
        if len(all_data) == 1:
            ax1.plot(df.index, df["MA20"], label="MA20", linestyle="--", alpha=0.7)
            ax1.plot(df.index, df["MA50"], label="MA50", linestyle="--", alpha=0.7)
    ax1.set_title("Closing Price & Moving Averages", fontsize=14)
    ax1.set_ylabel("Price (USD)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    fig1.tight_layout()
    st.pyplot(fig1)

    if len(all_data) == 1:
        st.markdown(
            "**Insight:** When the short-term MA20 crosses above the long-term MA50, "
            "it is often called a *golden cross* and may signal upward momentum. "
            "The reverse (*death cross*) may signal a downward trend."
        )

    # ----------------------------------------------------------
    # Section 3: Volume
    # ----------------------------------------------------------
    st.header("3. Trading Volume")

    for ticker, df in all_data.items():
        fig_v, ax_v = plt.subplots(figsize=(12, 3))
        colors = ["#4CAF50" if r >= 0 else "#F44336"
                  for r in df["Daily_Return"].fillna(0)]
        ax_v.bar(df.index, df["Volume"], color=colors, alpha=0.7, width=1)
        ax_v.set_title(f"{ticker} — Daily Volume (green = up day, red = down day)", fontsize=12)
        ax_v.set_ylabel("Volume")
        ax_v.grid(True, alpha=0.3)
        fig_v.tight_layout()
        st.pyplot(fig_v)

    st.markdown(
        "**Insight:** Spikes in volume during price drops often indicate "
        "panic selling or strong market reactions to news events."
    )

    # ----------------------------------------------------------
    # Section 4: Daily Return Distribution
    # ----------------------------------------------------------
    st.header("4. Daily Return Distribution")

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    for ticker, df in all_data.items():
        ax3.hist(df["Daily_Return"].dropna(), bins=50, alpha=0.5,
                 label=ticker, edgecolor="white")
    ax3.axvline(x=0, color="black", linestyle="--", linewidth=1)
    ax3.set_title("Distribution of Daily Returns", fontsize=14)
    ax3.set_xlabel("Daily Return (%)")
    ax3.set_ylabel("Frequency")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    fig3.tight_layout()
    st.pyplot(fig3)

    st.markdown(
        "**Insight:** A wider distribution means higher volatility. "
        "If the histogram is skewed to the left, the stock experienced "
        "more large negative days than large positive days."
    )

    # ----------------------------------------------------------
    # Section 5: Cumulative Return Comparison
    # ----------------------------------------------------------
    st.header("5. Cumulative Return Comparison")

    fig4, ax4 = plt.subplots(figsize=(12, 5))
    for ticker, df in all_data.items():
        ax4.plot(df.index, df["Cumulative_Return"] * 100,
                 label=ticker, linewidth=1.5)
    ax4.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax4.set_title("Cumulative Return Over Time", fontsize=14)
    ax4.set_ylabel("Cumulative Return (%)")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    fig4.tight_layout()
    st.pyplot(fig4)

    st.markdown(
        "**Insight:** This chart shows the total return of holding the stock "
        "from the start date. Comparing multiple stocks here reveals which "
        "one performed better over the same period."
    )

    # ----------------------------------------------------------
    # Section 6: Risk Assessment
    # ----------------------------------------------------------
    st.header("6. Risk Assessment")

    risk_data = []
    for s in summaries:
        risk_data.append({
            "Ticker": s["Ticker"],
            "Sharpe Ratio": s["Sharpe Ratio"],
            "Max Drawdown (%)": s["Max Drawdown (%)"],
            "Volatility (Std %)": s["Volatility (Std %)"],
        })
    risk_df = pd.DataFrame(risk_data)
    st.dataframe(risk_df, use_container_width=True, hide_index=True)

    st.markdown(
        "**How to interpret:**\n"
        "- **Sharpe Ratio > 1** is generally considered good; > 2 is very good.\n"
        "- **Max Drawdown** shows the worst loss from a peak — "
        "a drawdown of -30% means the stock lost 30% from its highest point.\n"
        "- **Volatility** measures day-to-day price swings."
    )

    # ----------------------------------------------------------
    # Section 7: Download Results
    # ----------------------------------------------------------
    st.header("7. Download Results")

    csv_data = summary_df.to_csv(index=False)
    st.download_button(
        label="📥 Download summary as CSV",
        data=csv_data,
        file_name="stock_analysis_summary.csv",
        mime="text/csv",
    )

    # ----------------------------------------------------------
    # Footer
    # ----------------------------------------------------------
    st.divider()
    st.caption(
        "Data source: Yahoo Finance (via yfinance). "
        "This tool is for educational purposes only and does not constitute investment advice. "
        "ACC102 Mini Assignment — Track 4."
    )

else:
    # Landing page before user clicks Analyse
    st.info(
        "👈 Enter one or more stock tickers in the sidebar, "
        "choose a date range, and click **Analyse** to begin."
    )
    st.markdown(
        "### What this tool does\n\n"
        "This dashboard helps you quickly assess a stock's historical performance. "
        "You can compare multiple stocks, view moving averages, "
        "check volatility, and evaluate risk metrics like the Sharpe Ratio "
        "and Maximum Drawdown — all in one place."
    )
