import streamlit as st
import pandas as pd

from src.emfer.charts.charts import plot_investment_value_growth
from src.emfer.data.investment_returns import calculate_lumpsum_returns, calculate_sip_returns
from src.emfer.analytics import format_funds_for_analytics, track_event


def format_indian_currency(value):
    value = round(value)
    sign = "-" if value < 0 else ""
    value_text = str(abs(value))

    if len(value_text) <= 3:
        return f"{sign}₹{value_text}"

    last_three_digits = value_text[-3:]
    remaining_digits = value_text[:-3]
    indian_groups = []

    while len(remaining_digits) > 2:
        indian_groups.insert(0, remaining_digits[-2:])
        remaining_digits = remaining_digits[:-2]

    if remaining_digits:
        indian_groups.insert(0, remaining_digits)

    return f"{sign}₹{','.join(indian_groups)},{last_three_digits}"


st.title("SIP / Lumpsum Returns")

if "sip_lumpsum_page_viewed_tracked" not in st.session_state:
    track_event("sip_lumpsum_page_viewed", {"page_name": "SIP / Lumpsum Returns"})
    st.session_state.sip_lumpsum_page_viewed_tracked = True

if "selected_funds" not in st.session_state or not st.session_state.selected_funds:
    st.error("No funds selected. Please go back and select funds first.")
    if st.button("← Go Back"):
        st.switch_page(st.session_state.home_page_link)
else:
    st.caption(
        "Estimate how a monthly SIP or one-time lumpsum investment would have grown "
        "across your selected funds using historical NAV data."
    )

    investment_mode = st.segmented_control(
        "Investment mode",
        ["Monthly SIP", "Lumpsum"],
        default="Monthly SIP"
    )

    amount_label = "Monthly SIP amount" if investment_mode == "Monthly SIP" else "Lumpsum amount"
    investment_amount = st.number_input(
        amount_label,
        min_value=1,
        value=10000,
        step=1000
    )

    default_years = st.session_state.get("n_years", 1)
    analysis_years = st.slider(
        "Select investment period (in years):",
        min_value=1,
        max_value=10,
        value=default_years,
        step=1
    )
    st.caption(
        "For SIP, eMFer uses 12 monthly installments per year within the selected "
        "period and values the final corpus on the latest NAV date. The final "
        "valuation month is not counted as an extra SIP installment."
    )

    st.divider()

    if investment_mode == "Monthly SIP":
        results_df, value_history_df, excluded_funds = calculate_sip_returns(
            st.session_state.nav_history_all,
            investment_amount,
            analysis_years
        )
    else:
        results_df, value_history_df, excluded_funds = calculate_lumpsum_returns(
            st.session_state.nav_history_all,
            investment_amount,
            analysis_years
        )

    if excluded_funds:
        excluded_text = "\n".join(
            f"- {fund['fund_name']} has only {fund['available_years']:.1f} years of NAV history."
            for fund in excluded_funds
        )
        st.warning(
            "Some funds were excluded because they do not have enough NAV history "
            f"for a {analysis_years}-year analysis.\n\n{excluded_text}"
        )

    if value_history_df.empty:
        st.info("No funds have enough NAV history for this investment period.")
    else:
        current_tracking_state = {
            "investment_mode": investment_mode,
            "investment_amount": investment_amount,
            "investment_years": analysis_years,
            "funds_selected": format_funds_for_analytics(st.session_state.selected_funds),
            "number_of_funds": len(st.session_state.selected_funds),
        }

        if current_tracking_state != st.session_state.get("last_tracked_sip_lumpsum_inputs"):
            track_event("sip_lumpsum_analysis", current_tracking_state)
            st.session_state.last_tracked_sip_lumpsum_inputs = current_tracking_state

        st.write("### Investment Value Over Time")
        st.plotly_chart(
            plot_investment_value_growth(value_history_df, investment_mode),
            use_container_width=True
        )

        metric_name = "XIRR (%)" if investment_mode == "Monthly SIP" else "CAGR (%)"

        st.write("### Return Dashboard")
        dashboard_cols = st.columns(min(len(results_df), 3))

        for idx, row in results_df.iterrows():
            metric_col = dashboard_cols[idx % len(dashboard_cols)]

            with metric_col:
                return_value = row[metric_name]
                return_label = "Not available" if pd.isna(return_value) else f"{return_value:.2f}%"

                st.metric(
                    label=row["Fund Name"],
                    value=return_label,
                    delta=f"Gain/Loss: {format_indian_currency(row['Gain / Loss'])}"
                )

        st.write("### Investment Summary")
        display_results_df = results_df.copy()
        money_columns = ["Total Invested", "Current Value", "Gain / Loss"]

        for column in money_columns:
            display_results_df[column] = display_results_df[column].apply(format_indian_currency)

        column_config = {
            "Fund Name": st.column_config.TextColumn(
                "Fund Name",
                pinned=True,
                width="large"
            ),
            "Total Invested": st.column_config.TextColumn(
                "Total Invested"
            ),
            "Current Value": st.column_config.TextColumn(
                "Current Value"
            ),
            "Gain / Loss": st.column_config.TextColumn(
                "Gain / Loss"
            ),
            "Absolute Return (%)": st.column_config.NumberColumn(
                "Absolute Return (%)",
                format="%.2f%%"
            ),
        }

        if investment_mode == "Monthly SIP":
            column_config["XIRR (%)"] = st.column_config.NumberColumn(
                "XIRR (%)",
                format="%.2f%%"
            )
        else:
            column_config["CAGR (%)"] = st.column_config.NumberColumn(
                "CAGR (%)",
                format="%.2f%%"
            )

        st.dataframe(
            display_results_df,
            hide_index=True,
            column_config=column_config
        )

    back_col, compare_col = st.columns(2)

    with back_col:
        if st.button("← Go Back", use_container_width=True):
            st.switch_page("pages/individual_fund_performance.py")

    with compare_col:
        if st.button("Compare Funds →", use_container_width=True):
            st.switch_page("pages/compare_funds.py")
