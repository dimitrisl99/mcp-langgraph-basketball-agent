import sys
import time
from pathlib import Path


project_root = Path(__file__).parents[2]
sys.path.append(str(project_root))

from app.ui.warmup import warmup_system

import streamlit as st


from app.ui.conversation_manager import (
    load_conversations,
    add_new_conversation,
    get_conversation_by_id,
    update_conversation,
    delete_conversation,
    rename_conversation,
)

from app.graph.agent import run_agent

st.set_page_config(
    page_title="MCP Basketball Assistant",
    page_icon="🏀",
    layout="wide",
)

def render_sources(sources: list[dict], key_prefix: str) -> None:
    if not sources:
        return

    with st.expander("📚 Sources"):
        for index, source in enumerate(sources, start=1):
            st.markdown(f"### {source['label']}")
            st.markdown(f"**File:** {source['file']}")
            st.markdown(f"**Page:** {source['page']}")

            pdf_path = Path(source["file_path"])

            if pdf_path.exists():
                with pdf_path.open("rb") as pdf_file:
                    st.download_button(
                        label=f"📄 Open / Download {source['file']}",
                        data=pdf_file,
                        file_name=source["file"],
                        mime="application/pdf",
                        key=f"{key_prefix}_download_{index}_{source['file']}_{source['page']}",
                    )
            else:
                st.warning("PDF file not found locally.")

            with st.expander("Retrieved text preview"):
                st.write(source["text"])

            st.divider()

@st.cache_resource(show_spinner=False)
def cached_warmup():
    return warmup_system()


with st.spinner("Loading AI models and retrieval index..."):
    warmup_timings = cached_warmup()

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
        "timings": {},
    }

if "conversations" not in st.session_state:
    st.session_state.conversations = load_conversations()

if not st.session_state.conversations:
    first_conversation = add_new_conversation()
    st.session_state.conversations = load_conversations()
    st.session_state.current_conversation_id = first_conversation["id"]

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = st.session_state.conversations[0]["id"]

current_conversation = get_conversation_by_id(
    st.session_state.current_conversation_id
)

if current_conversation:
    st.session_state.messages = current_conversation["messages"]
    st.session_state.chat_history = current_conversation["chat_history"]
    st.session_state.last_agent_info = current_conversation["last_agent_info"]

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ==========================
# Sidebar
# ==========================

with st.sidebar:

    st.header("Conversations")

    if st.button("➕ New Chat"):
        new_conversation = add_new_conversation()
        st.session_state.current_conversation_id = new_conversation["id"]
        st.rerun()

    st.divider()

    conversations = load_conversations()

    for conversation in conversations:
        is_current = conversation["id"] == st.session_state.current_conversation_id
        label = f"✅ {conversation['title']}" if is_current else conversation["title"]

        col1, col2 = st.columns([0.82, 0.18])

        with col1:
            if st.button(label, key=f"conversation_{conversation['id']}"):
                st.session_state.current_conversation_id = conversation["id"]
                st.rerun()

        with col2:
            if st.button("🗑", key=f"delete_{conversation['id']}"):
                remaining_conversations = delete_conversation(conversation["id"])

                if remaining_conversations:
                    st.session_state.current_conversation_id = remaining_conversations[0]["id"]
                else:
                    new_conversation = add_new_conversation()
                    st.session_state.current_conversation_id = new_conversation["id"]

                st.rerun()

    st.divider()

    st.header("Settings")

    if st.button("🗑️ Clear Current Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.last_agent_info = {
            "route": "-",
            "standalone_question": "-",
            "sources_count": 0,
            "model": "qwen3:8b",
            "timings": {},
        }

        update_conversation(
            conversation_id=st.session_state.current_conversation_id,
            messages=st.session_state.messages,
            chat_history=st.session_state.chat_history,
            last_agent_info=st.session_state.last_agent_info,
        )

        st.rerun()

    current_conversation = get_conversation_by_id(
        st.session_state.current_conversation_id
    )

    current_title = current_conversation["title"] if current_conversation else "New Chat"

    new_title = st.text_input(
        "Rename current chat",
        value=current_title,
        key=f"rename_{st.session_state.current_conversation_id}",
    )

    if st.button("💾 Save Title"):
        rename_conversation(
            conversation_id=st.session_state.current_conversation_id,
            new_title=new_title,
        )
        st.rerun()

    st.divider()

    show_debug = st.toggle(
        "🔧 Developer Mode",
        value=st.session_state.get(
            "developer_mode",
            False
        )
    )

    st.session_state.developer_mode = show_debug

    if show_debug:

        with st.expander(
                "🔧 Agent Observability",
                expanded=False,
        ):

            agent_info = st.session_state.last_agent_info

            st.markdown(
                f"**Route:** `{agent_info['route']}`"
            )

            st.markdown(
                "**Standalone Question:**"
            )

            st.caption(
                agent_info["standalone_question"]
            )

            st.markdown(
                f"**Retrieved Sources:** `{agent_info['sources_count']}`"
            )

            st.markdown(
                f"**Model:** `{agent_info['model']}`"
            )

            timings = agent_info.get("timings", {})

            if timings:

                st.markdown("### Timings")

                for step, value in timings.items():

                    if isinstance(value, (int, float)):
                        st.markdown(
                            f"**{step}:** `{value}s`"
                        )
                    else:
                        st.markdown(
                            f"**{step}:** `{value}`"
                        )

#====================================
# Display Previous Messages
#====================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        sources = message.get("sources", [])

        render_sources(sources, key_prefix="history")

#====================================
# Suggested Questions
#====================================

suggested_prompt = None

if not st.session_state.messages:
    st.markdown("### Try asking:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏀 How does Spain Pick and Roll work?"):
            suggested_prompt = "How does Spain Pick and Roll work?"

    with col2:
        if st.button("📊 Who has the most assists?"):
            suggested_prompt = "Who has the most assists?"

    with col3:
        if st.button("🎯 Who has the best 3-point percentage?"):
            suggested_prompt = "Who has the best 3-point percentage?"

#====================================
# User Input
#====================================

typed_prompt = st.chat_input(
    "Ask a basketball question...",
    disabled=st.session_state.is_generating,
)

prompt = suggested_prompt or typed_prompt

if prompt:

    st.session_state.is_generating = True

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
            timings = result.get("timings", {})

            message_placeholder = st.empty()
            message_placeholder.markdown(answer)

            st.session_state.last_agent_info = {
                "route": route,
                "standalone_question": standalone_question,
                "sources_count": len(sources),
                "model": "qwen3:8b",
                "timings": timings,
            }

            render_sources(sources, key_prefix="new")

    # save assistant response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
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

    update_conversation(
        conversation_id=st.session_state.current_conversation_id,
        messages=st.session_state.messages,
        chat_history=st.session_state.chat_history,
        last_agent_info=st.session_state.last_agent_info,
    )

    st.session_state.is_generating = False
    st.rerun()