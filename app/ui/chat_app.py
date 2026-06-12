import sys
from pathlib import Path

project_root = Path(__file__).parents[2]
sys.path.append(str(project_root))

import streamlit as st

from app.graph.agent import run_agent


st.set_page_config(
    page_title="MCP Basketball Assistant",
    page_icon="🏀",
    layout="wide",
)

st.title("🏀 MCP Basketball Assistant")

st.markdown(
    """
Ask questions about:

- Basketball systems and playbooks
- NBA player statistics
- Offensive and defensive concepts
"""
)

# ==========================
# Sidebar
# ==========================

with st.sidebar:

    st.header("Settings")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

#====================================
# Session State Initialization
#====================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#====================================
# Display Previous Messages
#====================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#====================================
# User Input
#====================================

if prompt := st.chat_input("Ask a basketball question..."):

    # show user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # call agent

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            result = run_agent(
                question=prompt,
                chat_history=st.session_state.chat_history,
            )

            answer = result["answer"]
            route = result["route"]
            standalone_question = result["standalone_question"]

            st.caption(f"Route: {route}")
            st.caption(f"Standalone question: {standalone_question}")

            st.markdown(answer)

    # save assistant response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    # update history for rewrite node

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )