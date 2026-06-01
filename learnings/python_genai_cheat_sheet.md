# Python GenAI Cheat Sheet

This file stores reusable Python snippets for common GenAI use cases.

The goal is not to be a full tutorial. The goal is to keep simple, copy-friendly building blocks for chatbots, RAG pipelines, LangChain, LlamaIndex, evaluation, and Streamlit apps.

---

## Environment Setup

```bash
pip install python-dotenv
pip install google-generativeai
pip install llama-index
pip install langchain
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

## Basic Gemini Call

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Explain RAG in simple terms.")
print(response.text)
```

## Gemini Chatbot

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="You are a helpful assistant. Keep answers clear and beginner-friendly."
)

chat = model.start_chat(history=[])

response = chat.send_message("What is a vector database?")
print(response.text)
```

## Basic System Prompt Pattern

```python
system_prompt = """
You are an AI assistant for answering questions about the provided context.

Rules:
- Use the context as the primary source.
- If the answer is not available, say so clearly.
- Do not make up facts.
- Keep the answer concise and beginner-friendly.
"""
```

## PDF Text Extraction

```python
from pypdf import PdfReader

pdf_path = "document.pdf"
reader = PdfReader(pdf_path)

text = ""
for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

print(text[:1000])
```

## LlamaIndex Setup

```python
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

Settings.llm = Gemini(
    model="models/gemini-2.5-flash",
    api_key=GOOGLE_API_KEY,
    temperature=0
)

Settings.embed_model = GoogleGenAIEmbedding(
    model_name="gemini-embedding-001",
    api_key=GOOGLE_API_KEY
)
```

## LlamaIndex Load Documents

```python
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("data").load_data()

print("Number of documents:", len(documents))
print(documents[0].text[:500])
```

## LlamaIndex Create Index

```python
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)
```

## LlamaIndex Query Engine

```python
query_engine = index.as_query_engine(similarity_top_k=4)

response = query_engine.query("What is this document about?")

print(response)
```

## LlamaIndex Chat Engine

```python
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    similarity_top_k=5,
    system_prompt=system_prompt
)

response = chat_engine.chat("Summarize the document.")
print(response.response)
```

## LlamaIndex Inspect Sources

```python
for i, node in enumerate(response.source_nodes, start=1):
    print(f"Source {i}")
    print("Score:", node.score)
    print("Metadata:", node.metadata)
    print(node.text[:500])
    print("-" * 80)
```

## LlamaIndex Sentence Splitter

```python
from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(
    chunk_size=1024,
    chunk_overlap=100
)

nodes = splitter.get_nodes_from_documents(documents)

print("Number of chunks:", len(nodes))
print(nodes[0].text[:500])
```

## LlamaIndex Semantic Splitter

```python
from llama_index.core.node_parser import SemanticSplitterNodeParser

splitter = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=Settings.embed_model
)

nodes = splitter.get_nodes_from_documents(documents)
```

## LangChain Basic Chat Model

```python
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

load_dotenv()

model = init_chat_model(
    "gemini-2.5-flash",
    model_provider="google_genai",
    temperature=0
)

response = model.invoke("Explain embeddings in simple terms.")
print(response.content)
```

## LangChain Prompt Template

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer using simple language."),
    ("human", "{question}")
])

chain = prompt | model

response = chain.invoke({
    "question": "What is RAG?"
})

print(response.content)
```

## LangChain Simple Agent

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=[],
    system_prompt="You are a helpful assistant."
)

response = agent.invoke({
    "messages": [
        {"role": "user", "content": "Explain what an AI agent is."}
    ]
})

print(response)
```

## LangChain Tool-Calling Agent

Use this pattern when the model should decide whether to call Python tools.

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

@tool
def example_tool() -> str:
    """Use this when the user asks for the example tool."""
    return "The tool ran successfully."

tools = [example_tool]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    api_key=api_key
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

response = agent_executor.invoke({
    "input": "Please use the example tool."
})

print(response["output"])
```

Notes:

- `tools` is the list of Python functions the agent is allowed to call.
- `agent_scratchpad` is where LangChain stores the agent's intermediate tool call steps.
- `AgentExecutor` runs the full loop: model thinks, tool runs, model responds.
- In the current eMFer environment, `create_tool_calling_agent` is available; `create_agent` may not be available depending on the installed LangChain version.

## Basic RAG Prompt Pattern

```python
rag_prompt = """
Use the context below to answer the question.

Context:
{context}

Question:
{question}

Rules:
- Use only the context if possible.
- If the context does not contain the answer, say so clearly.
- Keep the answer concise.
"""
```

## Manual RAG Flow

```python
question = "What is the investment objective?"

retrieved_nodes = query_engine.retrieve(question)

context = "\n\n".join([
    node.text for node in retrieved_nodes
])

prompt = rag_prompt.format(
    context=context,
    question=question
)

response = model.generate_content(prompt)
print(response.text)
```

## Streamlit Basic Chat UI

```python
import streamlit as st

st.title("Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask a question...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    answer = "Replace this with your LLM response."

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.write(answer)
```

## Streamlit Chatbot With Gemini

```python
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.title("Gemini Chatbot")

if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel("gemini-2.5-flash")

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    response = st.session_state.chat.send_message(user_input)
    answer = response.text

    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.write(answer)
```

## Source Citation Pattern

```python
def print_answer_with_sources(response):
    print("Answer:")
    print(response.response)

    print("\nSources:")
    for i, node in enumerate(response.source_nodes, start=1):
        page = node.metadata.get("page_number", "Unknown")
        score = node.score

        print(f"\nSource {i}")
        print("Page:", page)
        print("Score:", score)
        print(node.text[:500])
```

## Basic Evaluation Ideas

```python
test_questions = [
    "What is the investment objective?",
    "What are the main risk factors?",
    "Who is this fund suitable for?"
]

for question in test_questions:
    response = query_engine.query(question)
    print("Question:", question)
    print("Answer:", response)
    print("-" * 80)
```

## DeepEval Install

```bash
pip install deepeval
```

## Useful Debugging Checks

```python
print("Number of documents:", len(documents))
print("Number of chunks:", len(nodes))
print("First chunk:")
print(nodes[0].text[:1000])
```

```python
for node in response.source_nodes:
    print("Score:", node.score)
    print("Metadata:", node.metadata)
    print(node.text[:500])
    print("-" * 80)
```
