import streamlit as st
import pandas as pd
import requests
import base64
from pathlib import Path

from src.emfer.data.mf_api import get_all_schemes, fetch_nav_history
from src.emfer.data.rolling_returns import calculate_rolling_returns, get_nearest_past_index, clean_fund_name
from src.emfer.charts.charts import plot_nav, plot_rolling_cagr_mul_mf, rolling_returns_summary, plot_boxplot
from src.emfer.genAI.fund_store import create_fund_store, build_rag_context
from src.emfer.genAI.prompts import system_instruction, ques_bank
from src.emfer.genAI.scout import ask_scout, scout_answer

st.set_page_config(
    page_title="eMFer",
    layout="wide"
)

footer_bg = base64.b64encode(
    Path("assets/backgrounds/emfer_data_wave_footer.png").read_bytes()
).decode()

st.markdown(
    """
    <style>
        :root {
            --emfer-bg: #05060A;
            --emfer-panel: #0B0F1A;
            --emfer-border: rgba(138, 43, 255, 0.35);
            --emfer-blue: #0B7CFF;
            --emfer-purple: #8A2BFF;
            --emfer-magenta: #D32DFF;
            --emfer-text: #F5F7FB;
            --emfer-muted: #A8B0C3;
        }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(138, 43, 255, 0.16), transparent 30%),
                radial-gradient(circle at bottom left, rgba(11, 124, 255, 0.14), transparent 28%),
                var(--emfer-bg);
            color: var(--emfer-text);
        }

        .stApp::after {
            content: "";
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            height: 180px;
            pointer-events: none;
            z-index: 0;
            opacity: 0.55;
            background-image: url("data:image/png;base64,__FOOTER_BG__");
            background-repeat: no-repeat;
            background-position: bottom center;
            background-size: cover;
            mask-image: linear-gradient(to top, black 0%, black 55%, transparent 100%);
            -webkit-mask-image: linear-gradient(to top, black 0%, black 55%, transparent 100%);
        }

        header[data-testid="stHeader"] {
            background: rgba(5, 6, 10, 0.88);
            border-bottom: 1px solid rgba(42, 49, 66, 0.7);
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            position: relative;
            z-index: 1;
        }

        h1, h2, h3 {
            color: var(--emfer-text);
            letter-spacing: 0;
        }

        p, label, span, div {
            color: var(--emfer-text);
        }

        small,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stWidgetLabel"] label {
            color: var(--emfer-muted);
        }

        div[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(11, 124, 255, 0.18), transparent 35%),
                radial-gradient(circle at bottom right, rgba(138, 43, 255, 0.18), transparent 32%),
                #080B14;
            border-right: 1px solid var(--emfer-border);
            z-index: 2;
        }

        div[data-testid="stSidebar"] * {
            color: #E8ECF5;
        }

        div[data-testid="stSidebarNav"] {
            padding-top: 1rem;
        }

        div[data-testid="stSidebarNav"] a {
            border-radius: 10px;
            color: var(--emfer-muted);
            font-weight: 600;
            margin: 0.15rem 0.35rem;
            transition: all 160ms ease;
        }

        div[data-testid="stSidebarNav"] a:hover {
            background: rgba(11, 124, 255, 0.14);
            color: white;
        }

        div[data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(11, 124, 255, 0.85), rgba(138, 43, 255, 0.85));
            color: white;
            box-shadow: 0 0 18px rgba(138, 43, 255, 0.26);
        }

        div[data-testid="stButton"] > button {
            border: 1px solid rgba(138, 43, 255, 0.55);
            background: linear-gradient(90deg, var(--emfer-blue), var(--emfer-purple));
            color: white;
            font-weight: 600;
        }

        div[data-testid="stButton"] > button:hover {
            border-color: var(--emfer-magenta);
            box-shadow: 0 0 18px rgba(138, 43, 255, 0.35);
            color: white;
        }

        div[data-testid="stSelectbox"],
        div[data-testid="stMultiSelect"],
        div[data-testid="stSlider"] {
            background: rgba(11, 15, 26, 0.72);
            border: 1px solid rgba(42, 49, 66, 0.9);
            border-radius: 12px;
            padding: 0.8rem 1rem;
        }

        hr {
            border-color: rgba(138, 43, 255, 0.28);
        }
    </style>
    """.replace("__FOOTER_BG__", footer_bg),
    unsafe_allow_html=True
)

from dotenv import load_dotenv
import os
load_dotenv()

@st.cache_data
def load_schemes():
    return get_all_schemes()

def home_page():
    st.image("assets/brand_logos/emfer_full_lockup_transparent.png", width=560)

    try:
        st.session_state.schemes = load_schemes()
    except requests.exceptions.JSONDecodeError:
        st.error("The mutual fund data API is temporarily unavailable. Please try again later.")
        st.stop()
    except requests.exceptions.RequestException:
        st.error("Could not connect to the mutual fund data API. Please check your internet connection and try again.")
        st.stop()

    if "selected_funds" not in st.session_state:
        st.session_state.selected_funds = []

    if "n_years" not in st.session_state:
        st.session_state.n_years = 1

    st.session_state.selected_funds = st.multiselect(
        "Select Mutual Fund(s)",
        options=st.session_state.schemes["schemeName"].sort_values().tolist(),
        default=st.session_state.selected_funds,
        placeholder="Start typing fund name...",
        key="selected_funds_input"
    )

    st.divider()

    st.session_state.n_years = st.slider(
        "Please select desired rolling returns window (in years):",
        min_value=1,
        max_value=10,
        value=st.session_state.n_years,
        step=1,
        key="n_years_input"
    )

    st.divider()

    if st.session_state.selected_funds:
        selected_funds_display = pd.DataFrame({"Selected funds": st.session_state.selected_funds})
        selected_funds_display.index = selected_funds_display.index + 1
        st.dataframe(selected_funds_display)
        st.divider()

        st.session_state.selected_funds_df = st.session_state.schemes[
            st.session_state.schemes["schemeName"].isin(
                st.session_state.selected_funds)].reset_index(drop=True)
        
        st.session_state.nav_history_all = pd.DataFrame()
        st.session_state.df_rolling_all = pd.DataFrame()
        st.session_state.summary_all = pd.DataFrame()

        for idx, row in st.session_state.selected_funds_df.iterrows():
            #Creating historical NAV history and rolling returns data for each selected fund and appending to session state variables
            st.session_state.nav_history, tmp = fetch_nav_history(row["schemeCode"])

            fund_start_date = st.session_state.nav_history["date"].min()
            fund_end_date = st.session_state.nav_history["date"].max()
            fund_age_years = (fund_end_date - fund_start_date).days / 365.25

            if fund_age_years < st.session_state.n_years:
                st.error(
                    f"{row['schemeName']} has only {fund_age_years:.1f} years of NAV history. "
                    f"Please choose a rolling return window below {fund_age_years:.1f} years or pick a different fund."
                )
                st.stop()

            st.session_state.df_rolling = calculate_rolling_returns(st.session_state.nav_history, st.session_state.n_years)
            st.session_state.summary = rolling_returns_summary(st.session_state.df_rolling, st.session_state.n_years)
            
            #Appending all nav history data
            st.session_state.nav_history['fund_name'] = row['schemeName']
            st.session_state.nav_history_all = pd.concat([st.session_state.nav_history_all, st.session_state.nav_history])

            #Appending all rolling returns data
            st.session_state.df_rolling_all = pd.concat([st.session_state.df_rolling_all, st.session_state.df_rolling])
            
            # Appending rolling returns summary data
            st.session_state.summary_all = pd.concat([st.session_state.summary_all, st.session_state.summary]).reset_index(drop=True)
            st.session_state.summary_all_display = st.session_state.summary_all.rename(columns={
                "fund_name": "Fund Name",
                "start_date": "Start Date",
                "end_date": "End Date",
                "metric": "Metric",
                f"latest_{st.session_state.n_years}_year_cagr": f"Latest {st.session_state.n_years}Y CAGR (%)",
                "mean": "Average CAGR (%)",
                "std_dev": "Volatility / Std Dev (%)",
                "min": "Worst Observed CAGR (%)",
                "p5": "5th Percentile CAGR (%)",
                "p10": "10th Percentile CAGR (%)",
                "p25": "25th Percentile CAGR (%)",
                "median": "Median CAGR (%)",
                "p75": "75th Percentile CAGR (%)",
                "p90": "90th Percentile CAGR (%)",
                "p95": "95th Percentile CAGR (%)",
                "max": "Best Observed CAGR (%)",
            })

            # Creating fund store for RAG context
            st.session_state.fund_store = create_fund_store(st.session_state.df_rolling_all, st.session_state.summary_all)

            # Building RAG context
            st.session_state.rag_context = build_rag_context(st.session_state.fund_store)

            # Creating system instruction for Scout
            st.session_state.sys_instruction = system_instruction(st.session_state.rag_context)

            # Initializing Scout model with system instruction
            st.session_state.model = ask_scout(st.session_state.sys_instruction)

            # Importing question bank
            st.session_state.ques_bank = ques_bank()
        
        if st.button("Proceed", key="proceed_button"):
            st.switch_page("pages/individual_fund_performance.py")


page = st.navigation([
    st.Page(home_page, title="eMFer Home Page", default=True),
    st.Page("pages/individual_fund_performance.py", title="Individual Fund Performance"),
    st.Page("pages/compare_funds.py", title="Compare Funds"),
    st.Page("pages/emfer_funds_marathon.py", title="eMFer Funds Marathon"),
    st.Page("pages/ask_scout.py", title="Ask Scout"),
])

page.run()

        
