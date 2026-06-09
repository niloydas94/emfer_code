from dotenv import load_dotenv
import os

import streamlit as st
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from src.emfer.charts.charts import plot_boxplot, plot_risk_return_matrix

#%%
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# The chart tools update this when Scout creates a chart.
latest_fig = None

#%%
# Defining Scout as a tool-calling agent
def ask_scout(sys_instruction):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=api_key
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_instruction),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

#%%
#Scout generates answers
def scout_answer(model, question, chat_history=None):
    global latest_fig
    latest_fig = None

    if chat_history is None:
        chat_history = []

    response = model.invoke({
        "input": question,
        "chat_history": chat_history
    })
    return response["output"]



#%%
#@title Defining tools for the AI agent
@tool
def show_boxplot() -> str:
    """
    Use this when the user asks for distribution, range, outliers,
    consistency, box plot, percentile spread, or rolling CAGR distribution.
    """
    n = st.session_state.n_years
    fund_store_all = st.session_state.df_rolling_all

    fig = plot_boxplot(fund_store_all, n)

    global latest_fig
    latest_fig = fig

    return f"The {n}Y rolling CAGR boxplot has been created."


@tool
def show_risk_return_matrix() -> str:
    """
    Use this when the user asks for risk vs return, volatility vs return,
    risk-return matrix, low risk high return funds, or 2x2 quadrant analysis.
    """
    n = st.session_state.n_years
    fund_store_all_summary = st.session_state.summary_all

    fig = plot_risk_return_matrix(fund_store_all_summary, n)

    global latest_fig
    latest_fig = fig

    return f"The {n}Y risk-return matrix has been created."

#%%
tools = [show_boxplot, show_risk_return_matrix]
