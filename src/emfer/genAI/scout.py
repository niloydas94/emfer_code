from dotenv import load_dotenv
import os

import streamlit as st
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from src.emfer.charts.charts import plot_boxplot, plot_risk_return_matrix

#%%
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# The chart tools update this when Scout creates a chart.
latest_fig = None
latest_token_usage = {}
MODEL_NAME = "gemini-2.5-flash"
INPUT_COST_PER_TOKEN_USD = 0.30 / 1_000_000
OUTPUT_COST_PER_TOKEN_USD = 2.50 / 1_000_000


class TokenUsageCallback(BaseCallbackHandler):
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0

    def on_llm_end(self, response, **kwargs):
        for generation_group in response.generations:
            for generation in generation_group:
                message = getattr(generation, "message", None)
                usage = getattr(message, "usage_metadata", None)

                if usage:
                    self.input_tokens += usage.get("input_tokens", 0)
                    self.output_tokens += usage.get("output_tokens", 0)
                    self.total_tokens += usage.get("total_tokens", 0)


def build_token_usage_payload(input_tokens, output_tokens, total_tokens):
    estimated_input_cost_usd = input_tokens * INPUT_COST_PER_TOKEN_USD
    estimated_output_cost_usd = output_tokens * OUTPUT_COST_PER_TOKEN_USD

    return {
        "model_name": MODEL_NAME,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "input_cost_per_token_usd": INPUT_COST_PER_TOKEN_USD,
        "output_cost_per_token_usd": OUTPUT_COST_PER_TOKEN_USD,
        "estimated_input_cost_usd": estimated_input_cost_usd,
        "estimated_output_cost_usd": estimated_output_cost_usd,
        "estimated_total_cost_usd": estimated_input_cost_usd + estimated_output_cost_usd,
    }

#%%
# Defining Scout as a tool-calling agent
def ask_scout(sys_instruction):
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
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
    global latest_token_usage
    latest_fig = None
    latest_token_usage = {}

    if chat_history is None:
        chat_history = []

    token_callback = TokenUsageCallback()
    response = model.invoke({
        "input": question,
        "chat_history": chat_history
    }, config={"callbacks": [token_callback]})
    latest_token_usage = build_token_usage_payload(
        token_callback.input_tokens,
        token_callback.output_tokens,
        token_callback.total_tokens
    )
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
