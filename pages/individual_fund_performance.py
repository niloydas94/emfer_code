import streamlit as st
import pandas as pd

from src.emfer.data.mf_api import get_all_schemes, fetch_nav_history
from src.emfer.data.rolling_returns import calculate_rolling_returns, get_nearest_past_index, clean_fund_name
from src.emfer.charts.charts import plot_nav, plot_rolling_cagr_mul_mf, rolling_returns_summary
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
        display_funds_df = selected_funds_df[
            selected_funds_df["schemeName"].isin(funds_to_display)
        ].reset_index(drop=True)

        for idx, row in display_funds_df.iterrows():
            st.subheader(f"{row['schemeName']} ({row['schemeCode']})")

            nav_history_fund = nav_history_all[nav_history_all['fund_name'] == row['schemeName']]
            df_rolling_fund = df_rolling_all[df_rolling_all['fund_name'] == row['schemeName']]
            summary_fund_display = summary_all_display[summary_all_display['Fund Name'] == row['schemeName']]

            st.plotly_chart(plot_nav(nav_history_fund), use_container_width=True)

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
