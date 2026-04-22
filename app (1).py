"""
S&P 500 Stock Analysis & Decision Dashboard
ACC102 Mini Assignment - Track 4: Interactive Data Analysis Tool

Analytical Problem:
    Given a set of S&P 500 stocks, which offers the best risk-adjusted return,
    and which is most suitable for different investor risk profiles?

Target User: Individual investors and finance students who need
    data-driven guidance to compare stocks and support investment decisions.

Data Source: S&P 500 Companies Historical Prices (Kaggle, Cam Nugent)
    URL: https://www.kaggle.com/datasets/camnugent/sandp500
    Accessed: April 2026
    Period: February 2013 to February 2018

To run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="S&P 500 Stock Decision Dashboard",
    page_icon="📈",
    layout="wide"
)

# ============================================================
# Load Data
# ============================================================
@st.cache_data
def load_data():
    """Load the S&P 500 dataset from local compressed CSV."""
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp500_data.csv.gz")
    df = pd.read_csv(data_path, parse_dates=["Date"])
    df = df.sort_values(["Ticker", "Date"])
    return df

# ============================================================
# Header
# ============================================================
st.title("📈 S&P 500 Stock Analysis & Decision Dashboard")
st.markdown(
    "An interactive decision-support tool for individual investors and finance students. "
    "Compare up to 5 S&P 500 stocks, explore risk-return trade-offs, "
    "and receive **data-driven investment guidance** tailored to your risk appetite. "
    "Data covers **505 companies** from **2013 to 2018**."
)

with st.spinner("Loading dataset..."):
    try:
        full_df = load_data()
        all_tickers = sorted(full_df["Ticker"].unique())
    except FileNotFoundError:
        st.error("Data file `sp500_data.csv.gz` not found. Please place it in the same folder as app.py.")
        st.stop()

# ============================================================
# Sidebar
# ============================================================
st.sidebar.header("⚙️ Settings")
st.sidebar.markdown(f"**{len(all_tickers)} stocks available**")

selected_tickers = st.sidebar.multiselect(
    "Select stock(s) to analyse",
    options=all_tickers,
    default=["AAPL", "MSFT"],
    help="Select 2–5 stocks to unlock comparison and correlation analysis."
)

date_min = full_df["Date"].min().date()
date_max = full_df["Date"].max().date()

start_date = st.sidebar.date_input("Start date", value=pd.Timestamp("2016-01-01"),
                                    min_value=date_min, max_value=date_max)
end_date = st.sidebar.date_input("End date", value=pd.Timestamp("2018-02-07"),
                                  min_value=date_min, max_value=date_max)

investor_profile = st.sidebar.radio(
    "Your investor profile",
    options=["Conservative", "Balanced", "Aggressive"],
    index=1,
    help="Conservative: prioritises stability. Aggressive: accepts higher risk for higher return."
)

analyse_button = st.sidebar.button("🔍 Analyse", type="primary")

st.sidebar.markdown("---")
st.sidebar.caption("Data: S&P 500 Historical Prices. Source: Kaggle (Cam Nugent). Accessed April 2026.")

# ============================================================
# Helper Functions
# ============================================================

def get_stock_data(ticker, df, start, end):
    mask = (
        (df["Ticker"] == ticker) &
        (df["Date"] >= pd.Timestamp(start)) &
        (df["Date"] <= pd.Timestamp(end))
    )
    result = df[mask].copy().set_index("Date")
    return result if not result.empty else None


def compute_indicators(df):
    df = df.copy()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["Daily_Return"] = df["Close"].pct_change() * 100
    df["Cumulative_Return"] = (1 + df["Close"].pct_change()).cumprod() - 1
    return df


def compute_risk_metrics(df):
    daily_ret = df["Close"].pct_change().dropna()
    sharpe = (daily_ret.mean() / daily_ret.std()) * (252 ** 0.5) if daily_ret.std() != 0 else 0
    cumulative = (1 + daily_ret).cumprod()
    running_max = cumulative.cummax()
    max_drawdown = ((cumulative - running_max) / running_max).min() * 100
    return round(sharpe, 2), round(max_drawdown, 2)


def build_summary(ticker, df, sharpe, max_dd):
    vol = round(df["Daily_Return"].std(), 3)
    total_ret = round(df["Cumulative_Return"].iloc[-1] * 100, 2)

    # Investor profile classification
    if sharpe >= 1.2 and vol <= 1.2:
        profile = "Conservative ✅"
    elif sharpe >= 0.8 and vol <= 1.8:
        profile = "Balanced ✅"
    else:
        profile = "Aggressive ✅"

    return {
        "Ticker": ticker,
        "Total Return (%)": total_ret,
        "Avg Daily Return (%)": round(df["Daily_Return"].mean(), 3),
        "Volatility (%)": vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown (%)": max_dd,
        "Suitable For": profile,
    }


def generate_auto_conclusion(summaries, investor_profile):
    """Generate a data-driven investment conclusion paragraph."""
    if not summaries:
        return ""

    df_s = pd.DataFrame(summaries)

    best_return = df_s.loc[df_s["Total Return (%)"].idxmax()]
    best_sharpe = df_s.loc[df_s["Sharpe Ratio"].idxmax()]
    lowest_vol = df_s.loc[df_s["Volatility (%)"].idxmin()]
    lowest_dd = df_s.loc[df_s["Max Drawdown (%)"].idxmax()]  # least negative

    lines = []
    lines.append(f"**📊 Analysis Summary ({investor_profile} Investor Profile)**\n")

    # Return leader
    lines.append(
        f"- **Highest total return:** {best_return['Ticker']} achieved "
        f"{best_return['Total Return (%)']:.1f}% over the period, "
        f"making it the strongest performer by raw return."
    )

    # Risk-adjusted leader
    if best_sharpe["Ticker"] == best_return["Ticker"]:
        lines.append(
            f"- **Best risk-adjusted return:** {best_sharpe['Ticker']} also leads on Sharpe Ratio "
            f"({best_sharpe['Sharpe Ratio']:.2f}), meaning it delivered strong returns "
            f"without taking on excessive risk."
        )
    else:
        lines.append(
            f"- **Best risk-adjusted return:** {best_sharpe['Ticker']} leads on Sharpe Ratio "
            f"({best_sharpe['Sharpe Ratio']:.2f}), offering better return per unit of risk "
            f"than {best_return['Ticker']} despite a lower total return."
        )

    # Stability
    lines.append(
        f"- **Most stable stock:** {lowest_vol['Ticker']} showed the lowest daily volatility "
        f"({lowest_vol['Volatility (%)']:.2f}%), making it the least risky day-to-day option."
    )

    # Drawdown
    lines.append(
        f"- **Best downside protection:** {lowest_dd['Ticker']} had the smallest maximum drawdown "
        f"({lowest_dd['Max Drawdown (%)']:.1f}%), meaning it held its value better during market downturns."
    )

    # Profile-specific recommendation
    lines.append("")
    if investor_profile == "Conservative":
        rec = lowest_vol["Ticker"]
        lines.append(
            f"**💡 Recommendation for Conservative investors:** "
            f"Based on your risk profile, **{rec}** is the most suitable choice. "
            f"It offers the lowest volatility ({lowest_vol['Volatility (%)']:.2f}%) and "
            f"greatest price stability, prioritising capital preservation over maximum growth."
        )
    elif investor_profile == "Aggressive":
        rec = best_return["Ticker"]
        lines.append(
            f"**💡 Recommendation for Aggressive investors:** "
            f"Based on your risk profile, **{rec}** is the most suitable choice. "
            f"It delivered the highest total return ({best_return['Total Return (%)']:.1f}%), "
            f"and aggressive investors can accept its higher volatility in exchange for stronger growth."
        )
    else:  # Balanced
        rec = best_sharpe["Ticker"]
        lines.append(
            f"**💡 Recommendation for Balanced investors:** "
            f"Based on your risk profile, **{rec}** offers the best trade-off between return and risk. "
            f"Its Sharpe Ratio of {best_sharpe['Sharpe Ratio']:.2f} means it generates "
            f"strong returns without disproportionate risk — ideal for balanced investors."
        )

    # Trade-off note if multiple stocks
    if len(summaries) > 1:
        lines.append("")
        lines.append(
            f"**⚖️ Key trade-off:** "
            f"{best_return['Ticker']} maximises return but carries "
            f"higher volatility ({df_s.loc[df_s['Ticker']==best_return['Ticker'], 'Volatility (%)'].values[0]:.2f}%). "
            f"{lowest_vol['Ticker']} minimises risk but may sacrifice upside potential. "
            f"The right choice depends on your investment horizon and risk tolerance."
        )

    return "\n".join(lines)


# ============================================================
# Main Analysis
# ============================================================

if analyse_button:

    if not selected_tickers:
        st.error("Please select at least one stock from the sidebar.")
        st.stop()
    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

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
        st.error("No valid data found. Please adjust your selection or date range.")
        st.stop()

    summary_df = pd.DataFrame(summaries)

    # -------------------------------------------------------
    # Section 1: Summary Statistics
    # -------------------------------------------------------
    st.header("1. Summary Statistics")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    st.markdown(
        "**How to read:** Total Return = overall gain/loss. "
        "Volatility = standard deviation of daily returns (higher = more risk). "
        "Sharpe Ratio = return per unit of risk (higher is better, >1 is good). "
        "Max Drawdown = worst peak-to-trough loss. "
        "Suitable For = investor profile this stock best matches."
    )

    # -------------------------------------------------------
    # Section 2: AUTO CONCLUSION (Decision Support)
    # -------------------------------------------------------
    st.header("2. Investment Insight & Recommendation")
    conclusion = generate_auto_conclusion(summaries, investor_profile)
    st.markdown(conclusion)

    # -------------------------------------------------------
    # Section 3: Price Trend & Moving Averages
    # -------------------------------------------------------
    st.header("3. Price Trend & Moving Averages")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    for ticker, df in all_data.items():
        ax1.plot(df.index, df["Close"], label=f"{ticker}", linewidth=1.5)
        if len(all_data) == 1:
            ax1.plot(df.index, df["MA20"], label="MA20", linestyle="--", color="orange", alpha=0.8)
            ax1.plot(df.index, df["MA50"], label="MA50", linestyle="--", color="red", alpha=0.8)
    ax1.set_title(
        "Closing Price" + (" & Moving Averages" if len(all_data) == 1 else " Comparison"),
        fontsize=14
    )
    ax1.set_ylabel("Price (USD)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    fig1.tight_layout()
    st.pyplot(fig1)

    if len(all_data) == 1:
        st.markdown(
            "**Insight:** MA20 tracks short-term momentum; MA50 tracks medium-term trend. "
            "When MA20 crosses above MA50 (*golden cross*), it signals potential upward momentum. "
            "The reverse (*death cross*) may signal a downtrend."
        )

    # -------------------------------------------------------
    # Section 4: Cumulative Return Comparison
    # -------------------------------------------------------
    st.header("4. Cumulative Return Comparison")
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    for ticker, df in all_data.items():
        ax4.plot(df.index, df["Cumulative_Return"] * 100, label=ticker, linewidth=1.8)
    ax4.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax4.set_title("Cumulative Return Over Time (%)", fontsize=14)
    ax4.set_ylabel("Cumulative Return (%)")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    fig4.tight_layout()
    st.pyplot(fig4)
    st.markdown(
        "**Insight:** This shows the total return of a $1 investment from the start date. "
        "Diverging lines indicate different growth paths. "
        "A stock that recovers quickly after dips shows resilience."
    )

    # -------------------------------------------------------
    # Section 5: Risk-Return Scatter (NEW)
    # -------------------------------------------------------
    st.header("5. Risk vs Return Trade-off")
    fig5, ax5 = plt.subplots(figsize=(8, 6))
    for s in summaries:
        ax5.scatter(s["Volatility (%)"], s["Total Return (%)"], s=200, zorder=5)
        ax5.annotate(
            s["Ticker"],
            (s["Volatility (%)"], s["Total Return (%)"]),
            textcoords="offset points", xytext=(8, 5), fontsize=11, fontweight="bold"
        )
    ax5.set_xlabel("Volatility — Daily Return Std Dev (%)", fontsize=12)
    ax5.set_ylabel("Total Return (%)", fontsize=12)
    ax5.set_title("Risk vs Return: Where Do These Stocks Stand?", fontsize=13)
    ax5.axhline(y=0, color="gray", linestyle="--", linewidth=0.8)
    ax5.grid(True, alpha=0.3)
    fig5.tight_layout()
    st.pyplot(fig5)
    st.markdown(
        "**Insight:** Stocks in the **top-left** quadrant deliver high returns with low risk — "
        "the ideal position. Stocks in the **bottom-right** are high-risk but low-return — "
        "generally the least attractive. This chart helps investors quickly see the trade-off "
        "between each stock's risk and reward."
    )

    # -------------------------------------------------------
    # Section 6: Correlation Heatmap (multi-stock only)
    # -------------------------------------------------------
    if len(all_data) >= 2:
        st.header("6. Return Correlation Analysis")

        # Build a returns matrix
        returns_dict = {t: df["Daily_Return"].dropna() for t, df in all_data.items()}
        returns_df = pd.DataFrame(returns_dict).dropna()
        corr_matrix = returns_df.corr()

        fig6, ax6 = plt.subplots(figsize=(max(5, len(all_data) * 1.5),
                                          max(4, len(all_data) * 1.3)))
        im = ax6.imshow(corr_matrix.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
        plt.colorbar(im, ax=ax6, label="Correlation coefficient")
        ax6.set_xticks(range(len(corr_matrix.columns)))
        ax6.set_yticks(range(len(corr_matrix.index)))
        ax6.set_xticklabels(corr_matrix.columns, fontsize=11)
        ax6.set_yticklabels(corr_matrix.index, fontsize=11)
        ax6.set_title("Daily Return Correlation Between Selected Stocks", fontsize=13)

        # Annotate each cell
        for i in range(len(corr_matrix)):
            for j in range(len(corr_matrix.columns)):
                val = corr_matrix.values[i, j]
                ax6.text(j, i, f"{val:.2f}", ha="center", va="center",
                         fontsize=12, fontweight="bold",
                         color="black" if 0.3 < val < 0.8 else "white")
        fig6.tight_layout()
        st.pyplot(fig6)

        # Auto-interpret correlation
        pairs = []
        tickers_list = list(corr_matrix.columns)
        for i in range(len(tickers_list)):
            for j in range(i + 1, len(tickers_list)):
                pairs.append((tickers_list[i], tickers_list[j],
                               round(corr_matrix.iloc[i, j], 2)))

        low_corr = [p for p in pairs if p[2] < 0.5]
        high_corr = [p for p in pairs if p[2] >= 0.8]

        corr_insight = (
            "**Insight:** Correlation measures how similarly two stocks move. "
            "A value near **+1** means they move together; near **0** means they move independently. "
            "**Lower correlation = better diversification** — combining low-correlation stocks "
            "reduces overall portfolio risk because they do not all fall at the same time.\n\n"
        )
        if low_corr:
            pair_strs = [f"{p[0]} & {p[1]} (r = {p[2]})" for p in low_corr]
            corr_insight += (
                f"**✅ Good diversification pairs:** {', '.join(pair_strs)}. "
                f"These stocks move relatively independently, so holding both "
                f"reduces portfolio volatility compared to holding either alone.\n\n"
            )
        if high_corr:
            pair_strs = [f"{p[0]} & {p[1]} (r = {p[2]})" for p in high_corr]
            corr_insight += (
                f"**⚠️ High correlation pairs:** {', '.join(pair_strs)}. "
                f"These stocks tend to move together, offering limited diversification benefit."
            )
        st.markdown(corr_insight)

    # -------------------------------------------------------
    # Section 7: Volume Analysis
    # -------------------------------------------------------
    st.header("7. Trading Volume")
    for ticker, df in all_data.items():
        fig_v, ax_v = plt.subplots(figsize=(12, 3))
        colors = ["#4CAF50" if r >= 0 else "#F44336" for r in df["Daily_Return"].fillna(0)]
        ax_v.bar(df.index, df["Volume"], color=colors, alpha=0.7, width=1)
        ax_v.set_title(f"{ticker} — Daily Volume (green = price up, red = price down)", fontsize=12)
        ax_v.set_ylabel("Volume")
        ax_v.grid(True, alpha=0.3)
        fig_v.tight_layout()
        st.pyplot(fig_v)
    st.markdown(
        "**Insight:** Volume spikes on red (down) days often indicate panic selling — "
        "many investors exiting simultaneously. Volume spikes on green days suggest "
        "strong conviction buying. Sustained price rises on increasing volume are "
        "generally more reliable signals than price moves on low volume."
    )

    # -------------------------------------------------------
    # Section 8: Daily Return Distribution
    # -------------------------------------------------------
    st.header("8. Daily Return Distribution")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    for ticker, df in all_data.items():
        ax3.hist(df["Daily_Return"].dropna(), bins=60, alpha=0.55, label=ticker, edgecolor="white")
    ax3.axvline(x=0, color="black", linestyle="--", linewidth=1)
    ax3.set_title("Distribution of Daily Returns", fontsize=14)
    ax3.set_xlabel("Daily Return (%)")
    ax3.set_ylabel("Frequency")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    fig3.tight_layout()
    st.pyplot(fig3)
    st.markdown(
        "**Insight:** A narrow bell curve indicates low volatility and more predictable returns. "
        "Fat tails (bars far from centre) indicate the stock has experienced "
        "large unexpected moves — important for risk management."
    )

    # -------------------------------------------------------
    # Section 9: Download
    # -------------------------------------------------------
    st.header("9. Download Results")
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
    st.info("👈 Select stocks in the sidebar, choose your investor profile, then click **Analyse**.")

    st.markdown("### What this tool does")
    st.markdown(
        "This dashboard helps you answer a core investment question: "
        "**which stock offers the best risk-adjusted return for your investor profile?**\n\n"
        "Select your investor profile (Conservative / Balanced / Aggressive), "
        "choose stocks to compare, and the tool will:\n"
        "- Compute returns, volatility, Sharpe Ratio, and Max Drawdown\n"
        "- Generate a personalised investment recommendation\n"
        "- Show a Risk vs Return scatter chart for quick comparison\n"
        "- Analyse return correlations to identify diversification opportunities\n"
        "- Provide actionable insights at every step"
    )
    st.markdown("### Sample stocks")
    sample = ["AAPL", "MSFT", "GOOGL", "AMZN", "JPM", "GS", "KO", "JNJ", "WMT", "NFLX"]
    st.code(", ".join(sample) + f"  ... and {len(all_tickers) - len(sample)} more")
