import streamlit as st
import pandas as pd

from src.emfer.data.mf_api import get_all_schemes, fetch_nav_history
from src.emfer.data.rolling_returns import calculate_rolling_returns, get_nearest_past_index
from src.emfer.charts.charts import plot_nav, plot_rolling_cagr_mul_mf, rolling_returns_summary, plot_boxplot, plot_risk_return_matrix
from src.emfer.analytics import format_funds_for_analytics, track_event


def format_metric_values_for_analytics(values):
    return " || ".join(f"{value:.2f}" for value in values)

st.title("Compare Funds")

if "compare_page_viewed_tracked" not in st.session_state:
    track_event("compare_page_viewed", {"page_name": "Compare Funds"})
    st.session_state.compare_page_viewed_tracked = True

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

    summary_for_analytics = st.session_state.summary_all_display.sort_values("Fund Name")
    compare_metrics_state = {
        "funds_selected": format_funds_for_analytics(summary_for_analytics["Fund Name"].tolist()),
        "metric": f"{st.session_state.n_years}Y CAGR",
        "latest_metric_value": format_metric_values_for_analytics(
            summary_for_analytics[f"Latest {st.session_state.n_years}Y CAGR (%)"]
        ),
        "average_metric_value": format_metric_values_for_analytics(
            summary_for_analytics["Average CAGR (%)"]
        ),
        "median_metric_value": format_metric_values_for_analytics(
            summary_for_analytics["Median CAGR (%)"]
        ),
        "std_dev_metric_value": format_metric_values_for_analytics(
            summary_for_analytics["Volatility / Std Dev (%)"]
        ),
    }

    if compare_metrics_state != st.session_state.get("last_tracked_compare_metrics"):
        track_event("compare_metrics", compare_metrics_state)
        st.session_state.last_tracked_compare_metrics = compare_metrics_state

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
    st.markdown(
        """
        This matrix helps you read return and risk together. Look for funds that suit your risk appetite.<br><br>
        ⭐ Best Zone: higher rolling returns with lower volatility.<br>
        🔺 Aggressive Zone: higher rolling returns, but with higher volatility.<br>
        ➖ Stable Zone: lower volatility, but also lower rolling returns.<br>
        ❌ Weak Zone: lower rolling returns with higher volatility.
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(
        plot_risk_return_matrix(st.session_state.summary_all, st.session_state.n_years),
        use_container_width=True)

    back_col, marathon_col = st.columns(2)

    with back_col:
        if st.button("← Go Back", use_container_width=True):
            st.switch_page("pages/sip_lumpsum_returns.py")

    with marathon_col:
        if st.button("eMFer Funds Marathon →", use_container_width=True):
            st.switch_page("pages/emfer_funds_marathon.py")
