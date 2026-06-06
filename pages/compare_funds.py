import streamlit as st
import pandas as pd

from src.emfer.data.mf_api import get_all_schemes, fetch_nav_history
from src.emfer.data.rolling_returns import calculate_rolling_returns, get_nearest_past_index
from src.emfer.charts.charts import plot_nav, plot_rolling_cagr_mul_mf, rolling_returns_summary, plot_boxplot, plot_risk_return_matrix

st.title("Compare Funds")

if "selected_funds" not in st.session_state or not st.session_state.selected_funds:
    st.error("No funds selected. Please go back and select funds first.")
    if st.button("← Go Back"):
        st.switch_page(st.session_state.home_page_link)
else:
    st.write("### Rolling Returns Comparison")
    st.caption(
        "Use this chart to see how each fund's rolling CAGR changed over time. "
        "Look for funds that stayed strong across many periods, not just at the end."
    )
    st.plotly_chart(plot_rolling_cagr_mul_mf(st.session_state.df_rolling_all, st.session_state.n_years), use_container_width=True)

    st.divider()

    st.write("### Rolling Returns Summary")
    st.caption(
        "This table summarizes typical return, volatility, downside, and upside. "
        "Median and percentiles are often more useful than only the latest return."
    )
    st.dataframe(
        st.session_state.summary_all_display,
        hide_index=True,
        column_config={
            "Fund Name": st.column_config.TextColumn(
                "Fund Name",
                pinned=True,
                width="large"
            )
        }
    )

    st.divider()

    st.write("### Distribution of Rolling Returns")
    st.caption(
        "Use the boxplot to compare consistency and spread. A tighter box usually means "
        "the fund delivered more predictable rolling returns."
    )
    sort_by_label = st.radio(
        "Sort boxplots by",
        ["Returns (high to low)", "Spread (low to high)"],
        horizontal=True,
        index=0,
    )
    sort_by = "returns" if sort_by_label.startswith("Returns") else "spread"
    st.plotly_chart(
        plot_boxplot(st.session_state.df_rolling_all, st.session_state.n_years, sort_by),
        use_container_width=True
    )

    st.divider()

    st.write("### Risk-Return Matrix")
    st.caption(
        "This chart compares median rolling return against volatility. The ideal area is "
        "higher return with lower risk, but always check whether the comparison is fair."
    )
    st.plotly_chart(
        plot_risk_return_matrix(st.session_state.summary_all, st.session_state.n_years),
        use_container_width=True)

    back_col, marathon_col = st.columns(2)

    with back_col:
        if st.button("← Go Back", use_container_width=True):
            st.switch_page("pages/individual_fund_performance.py")

    with marathon_col:
        if st.button("eMFer Funds Marathon →", use_container_width=True):
            st.switch_page("pages/emfer_funds_marathon.py")
