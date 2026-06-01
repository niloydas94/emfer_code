import streamlit as st
import pandas as pd

import src.emfer.genAI.scout as scout

st.title("Ask Scout")

if "selected_funds" not in st.session_state or not st.session_state.selected_funds:
    st.error("No funds selected. Please go back and select funds first.")
    if st.button("← Go Back"):
        st.switch_page("app.py")
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
        answer = scout.scout_answer(st.session_state.model, question)
        if scout.latest_fig is not None:
            st.plotly_chart(scout.latest_fig, use_container_width=True)
        
        st.write("### Scout:")
        st.write(answer)

        
