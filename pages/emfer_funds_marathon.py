import streamlit as st

from src.emfer.charts.charts import build_bar_chart_race


st.image("assets/brand_logos/emfer_funds_marathon_badge_transparent.png", width=620)

if "selected_funds" not in st.session_state or not st.session_state.selected_funds:
    st.error("No funds selected. Please go back and select funds first.")
    if st.button("← Go Back"):
        st.switch_page(st.session_state.home_page_link)
else:
    st.caption(
        "Watch how the selected funds move through time based on rolling CAGR. "
        "Use this to spot leaders, laggards, comebacks, and performance decay across market cycles."
    )

    df_rolling_all = st.session_state.df_rolling_all
    n_years = st.session_state.n_years
    col_cagr = f"cagr_{n_years}_years"

    if col_cagr not in df_rolling_all.columns:
        st.error(f"Rolling return column not found: {col_cagr}")
        st.stop()

    fund_count = df_rolling_all["fund"].nunique()

    sample_frequency = st.selectbox(
        "Animation frequency",
        ["Monthly", "Quarterly", "Yearly"],
        index=1,
    )

    st.plotly_chart(
        build_bar_chart_race(
            df_rolling_all,
            n_years,
            sample_frequency,
            fund_count,
        ),
        use_container_width=True,
    )

    back_col, scout_col = st.columns(2)

    with back_col:
        if st.button("← Go Back", use_container_width=True):
            st.switch_page("pages/compare_funds.py")

    with scout_col:
        if st.button("Ask Scout →", use_container_width=True):
            st.switch_page("pages/ask_scout.py")
