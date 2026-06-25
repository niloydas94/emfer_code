import streamlit as st
import pandas as pd

from src.emfer.data.mf_api import get_all_schemes, fetch_nav_history, calculate_days_to_new_high, calculate_peak_nav_stats
from src.emfer.data.rolling_returns import calculate_rolling_returns, get_nearest_past_index, clean_fund_name
from src.emfer.charts.charts import plot_nav, plot_drawdown, plot_rolling_cagr_mul_mf, rolling_returns_summary
from src.emfer.analytics import format_funds_for_analytics, track_event

st.title("Individual Fund Performance")

if "individual_page_viewed_tracked" not in st.session_state:
    track_event("individual_page_viewed", {"page_name": "Individual Fund Performance"})
    st.session_state.individual_page_viewed_tracked = True

# Get schemes from session state
if "selected_funds" not in st.session_state or not st.session_state.selected_funds:
    st.error("No funds selected. Please go back and select funds first.")
    if st.button("← Go Back"):
        st.switch_page(st.session_state.home_page_link)
else:
    selected_funds = st.session_state.selected_funds
    n_years = st.session_state.get("n_years", 1)
    selected_funds_df = st.session_state.selected_funds_df
    nav_history_all = st.session_state.nav_history_all
    df_rolling_all = st.session_state.df_rolling_all
    summary_all_display = st.session_state.summary_all_display

    funds_to_display = st.pills(
        "Pick fund(s) to review performance",
        options=selected_funds,
        selection_mode="multi",
        default=[],
    )

    if funds_to_display and funds_to_display != st.session_state.get("last_tracked_individual_funds"):
        track_event(
            "individual_funds_selected",
            {
                "funds_selected": format_funds_for_analytics(funds_to_display),
                "number_of_funds": len(funds_to_display),
                "rolling_window_years": n_years,
            }
        )
        st.session_state.last_tracked_individual_funds = funds_to_display

    st.divider()

    if not funds_to_display:
        st.info("Please choose at least one fund to view historical performance.")
    else:
        selected_indicators = st.pills(
            "Add technical indicators",
            options=[
                "50D Moving Average",
                "200D Moving Average",
                "Drawdown",
                "Peak NAV Marker",
                "Distance from Peak",
                "Days to New High",
            ],
            selection_mode="multi",
            default=[],
        )

        st.divider()

        display_funds_df = selected_funds_df[
            selected_funds_df["schemeName"].isin(funds_to_display)
        ].reset_index(drop=True)

        for idx, row in display_funds_df.iterrows():
            st.subheader(f"{row['schemeName']} ({row['schemeCode']})")

            nav_history_fund = nav_history_all[nav_history_all['fund_name'] == row['schemeName']]
            df_rolling_fund = df_rolling_all[df_rolling_all['fund_name'] == row['schemeName']]
            summary_fund_display = summary_all_display[summary_all_display['Fund Name'] == row['schemeName']]

            if "Distance from Peak" in selected_indicators:
                peak_nav_stats = calculate_peak_nav_stats(nav_history_fund)
                peak_date = peak_nav_stats["peak_date"]

                distance_label = "Not available"
                if peak_nav_stats["distance_from_peak_pct"] is not None:
                    distance_label = f"{peak_nav_stats['distance_from_peak_pct']}%"

                st.metric(
                    "Distance from Peak",
                    distance_label,
                    help=(
                        "Shows how far the latest NAV is from the fund's highest historical NAV."
                    )
                )

                if peak_date is not None:
                    st.caption(f"Peak NAV date: {peak_date.date()}")

            if "Days to New High" in selected_indicators:
                days_to_new_high = calculate_days_to_new_high(nav_history_fund)
                metric_cols = st.columns(4)

                metric_values = [
                    (
                        "Average Days to New High",
                        days_to_new_high["average_days_to_new_high"],
                        "Average time the fund historically took to recover from a fall and make a fresh NAV high."
                    ),
                    (
                        "Median Days to New High",
                        days_to_new_high["median_days_to_new_high"],
                        "Typical recovery time to a fresh NAV high, less affected by unusually long recovery periods."
                    ),
                    (
                        "Longest Days to New High",
                        days_to_new_high["longest_days_to_new_high"],
                        "Longest historical wait before the fund recovered and made a fresh NAV high."
                    ),
                    (
                        "Current Days Since High",
                        days_to_new_high["current_days_since_high"],
                        "Number of days since the fund last made its highest NAV."
                    ),
                ]

                for metric_col, (metric_label, metric_value, metric_help) in zip(metric_cols, metric_values):
                    metric_col.metric(
                        metric_label,
                        "Not available" if metric_value is None else f"{metric_value} days",
                        help=metric_help
                    )

            st.plotly_chart(plot_nav(nav_history_fund, selected_indicators), use_container_width=True)

            if "Drawdown" in selected_indicators:
                st.plotly_chart(plot_drawdown(nav_history_fund), use_container_width=True)

            st.plotly_chart(plot_rolling_cagr_mul_mf(df_rolling_fund, n_years), use_container_width=True)

            st.write("**Returns Summary**")
            st.dataframe(
                summary_fund_display,
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

    back_col, sip_lumpsum_col = st.columns(2)

    with back_col:
        if st.button("← Go Back", use_container_width=True):
            st.switch_page(st.session_state.home_page_link)

    with sip_lumpsum_col:
        if st.button("SIP / Lumpsum Returns →", use_container_width=True):
            st.switch_page("pages/sip_lumpsum_returns.py")
