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
# Session State Initialization
# ==========================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_agent_info" not in st.session_state:
    st.session_state.last_agent_info = {
        "route": "-",
        "standalone_question": "-",
        "sources_count": 0,
        "model": "qwen3:8b",
    }

# ==========================
# Sidebar
# ==========================

with st.sidebar:

    st.header("Settings")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    st.header("Chat History")

    if st.session_state.messages:
        user_messages = [
            message["content"]
            for message in st.session_state.messages
            if message["role"] == "user"
        ]

        for index, user_message in enumerate(user_messages, start=1):
            st.markdown(f"**{index}.** {user_message}")
    else:
        st.caption("No messages yet.")

    st.divider()

    st.header("Agent Observability")

    agent_info = st.session_state.last_agent_info

    st.markdown(f"**Route:** `{agent_info['route']}`")
    st.markdown(f"**Standalone Question:**")
    st.caption(agent_info["standalone_question"])
    st.markdown(f"**Retrieved Sources:** `{agent_info['sources_count']}`")
    st.markdown(f"**Model:** `{agent_info['model']}`")

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
            sources = result.get("sources", [])

            st.session_state.last_agent_info = {
                "route": route,
                "standalone_question": standalone_question,
                "sources_count": len(sources),
                "model": "qwen3:8b",
            }

            st.caption(f"Route: {route}")
            st.caption(f"Standalone question: {standalone_question}")

            st.markdown(answer)
            if sources:
                with st.expander("📚 Sources"):
                    for index, source in enumerate(sources, start=1):

                        st.markdown(
                            f"### {source['label']}"
                        )

                        st.markdown(
                            f"**File:** {source['file']}"
                        )

                        st.markdown(
                            f"**Page:** {source['page']}"
                        )

                        pdf_path = Path(source["file_path"])

                        if pdf_path.exists():
                            with pdf_path.open("rb") as pdf_file:
                                st.download_button(
                                    label=f"📄 Open / Download {source['file']}",
                                    data=pdf_file,
                                    file_name=source["file"],
                                    mime="application/pdf",
                                    key=f"download_{index}_{source['file']}_{source['page']}",
                                )
                        else:
                            st.warning("PDF file not found locally.")

                        with st.expander("Retrieved text preview"):
                            st.write(source["text"])

                        st.divider()

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