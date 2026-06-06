import streamlit as st
import pandas as pd
import random
import time
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

import src.emfer.genAI.scout as scout

st.title("Ask Scout")

scout_loading_nuggets = [
    "📈 Rolling returns help you spot consistency, not just one lucky finish-line selfie.",
    "🎢 The highest return is exciting, but volatility may be hiding in the back seat.",
    "🧭 Median rolling CAGR is like the fund's usual behavior, not its best outfit.",
    "🕵️ Downside periods are where funds stop posing and start revealing character.",
    "😌 A tight return distribution is boring in the best possible way.",
    "🎬 Risk and return are a pair. Reading only one is like watching half a movie.",
    "👣 Past performance does not predict the future, but it does leave fingerprints.",
    "⚖️ Using the same rolling window keeps fund comparisons from turning into apples vs mangoes.",
    "👋 Volatility is not a villain. But it does need an introduction.",
    "🌧️ A fund's worst rolling return deserves attention. It is the part that shows up during market drama.",
    "🔍 Scout is looking at your selected funds, not pretending to know the entire universe.",
    "📦 Boxplots show the full return story, not just the headline number with good lighting.",
    "😴 Long term suitability is a mix of consistency, risk, and your ability to sleep peacefully.",
    "🏁 Recoveries after drawdowns matter. Comebacks are not just for sports movies.",
    "🧩 The risk-return matrix helps separate steady performers from thrill seekers.",
]

if "selected_funds" not in st.session_state or not st.session_state.selected_funds:
    st.error("No funds selected. Please go back and select funds first.")
    if st.button("← Go Back"):
        st.switch_page(st.session_state.home_page_link)
else:
    #Creating a chat interface for asking Scout questions and getting answers
    st.write("### Scout is your very own AI mutual fund analyst! \n" \
    "Ask anything about the funds you've selected, and it will provide insights based on historical data. \n" \
    " Ask about performance, risk, comparisons, or anything else you're curious about.")

    question_selectbox = st.selectbox(
        "Or select a sample question from the dropdown below:",
        st.session_state.ques_bank,
        key="sample_question"
    )

    if st.session_state.sample_question:
        st.session_state.user_question = st.session_state.sample_question

    question = st.text_input(
        "Enter your question for Scout here:",
        key="user_question"
    )

    #Creating a drop down of sample questions from the question bank to inspire users
    # question_selectbox = st.selectbox(
    #     "Or select a sample question from the dropdown below:", 
    #     st.session_state.ques_bank)

    # question = st.text_input("Enter your question for Scout here:")
    if st.button("Ask Scout", key="ask_scout_button"):    
        nugget_box = st.empty()

        with st.spinner("Scout is thinking through your question..."):
            scout_result = {}

            def get_scout_answer():
                try:
                    scout_result["answer"] = scout.scout_answer(st.session_state.model, question)
                except Exception as error:
                    scout_result["error"] = error

            scout_thread = threading.Thread(target=get_scout_answer)
            add_script_run_ctx(scout_thread, get_script_run_ctx())
            scout_thread.start()

            while scout_thread.is_alive():
                nugget = random.choice(scout_loading_nuggets)
                nugget_box.markdown(
                    f"""
                    <div style="
                        background: rgba(11, 124, 255, 0.12);
                        border: 1px solid rgba(138, 43, 255, 0.35);
                        border-radius: 10px;
                        padding: 0.9rem 1rem;
                        margin-bottom: 1rem;
                    ">
                        <div style="font-size: 0.85rem; color: #A8B0C3; margin-bottom: 0.25rem;">
                            While Scout connects the dots, here is something to ponder...
                        </div>
                        <div style="font-size: 1.05rem; font-weight: 650; color: #F5F7FB;">
                            {nugget}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                time.sleep(10)

            scout_thread.join()

            if "error" in scout_result:
                raise scout_result["error"]

            answer = scout_result["answer"]

        nugget_box.empty()

        if scout.latest_fig is not None:
            st.plotly_chart(scout.latest_fig, use_container_width=True)
        
        st.write("### Scout:")
        st.write(answer)

    if st.button("← Go Back", use_container_width=True):
        st.switch_page("pages/compare_funds.py")
