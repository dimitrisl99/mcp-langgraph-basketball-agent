import json
import ollama
from datetime import datetime
from pathlib import Path
from uuid import uuid4


def get_project_root() -> Path:
    return Path(__file__).parents[2]


def get_conversations_path() -> Path:
    return get_project_root() / "data" / "conversations.json"


def load_conversations() -> list[dict]:
    path = get_conversations_path()

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_conversations(conversations: list[dict]) -> None:
    path = get_conversations_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(conversations, file, ensure_ascii=False, indent=2)


def create_conversation() -> dict:
    now = datetime.now().isoformat(timespec="seconds")

    return {
        "id": str(uuid4()),
        "title": "New Chat",
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "chat_history": [],
        "last_agent_info": {
            "route": "-",
            "standalone_question": "-",
            "sources_count": 0,
            "model": "qwen3:8b",
        },
    }


def generate_title_from_question(question: str) -> str:
    title = question.strip()

    if len(title) > 35:
        title = title[:35].rstrip() + "..."

    return title or "New Chat"

OLLAMA_MODEL = "qwen3:8b"

def generate_llm_title(question: str) -> str:
    prompt = f"""
Create a short, clear chat title for this basketball assistant conversation.

Rules:
- Maximum 5 words.
- No quotes.
- No punctuation unless needed.
- Use title case.
- Return only the title.

User question:
{question}

Title:
"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    title = response["message"]["content"].strip()

    if len(title) > 40:
        title = title[:40].rstrip() + "..."

    return title or generate_title_from_question(question)

def update_conversation(
    conversation_id: str,
    messages: list[dict],
    chat_history: list[dict],
    last_agent_info: dict,
) -> None:
    conversations = load_conversations()

    for conversation in conversations:
        if conversation["id"] == conversation_id:
            conversation["messages"] = messages
            conversation["chat_history"] = chat_history
            conversation["last_agent_info"] = last_agent_info
            conversation["updated_at"] = datetime.now().isoformat(timespec="seconds")

            if conversation["title"] == "New Chat":
                first_user_message = next(
                    (
                        message["content"]
                        for message in messages
                        if message["role"] == "user"
                    ),
                    None,
                )

                if first_user_message:
                    conversation["title"] = generate_llm_title(first_user_message)

            break

    save_conversations(conversations)


def add_new_conversation() -> dict:
    conversations = load_conversations()
    conversation = create_conversation()

    conversations.insert(0, conversation)
    save_conversations(conversations)

    return conversation


def get_conversation_by_id(conversation_id: str) -> dict | None:
    conversations = load_conversations()

    for conversation in conversations:
        if conversation["id"] == conversation_id:
            return conversation

    return None

def delete_conversation(conversation_id: str) -> list[dict]:
    conversations = load_conversations()

    conversations = [
        conversation
        for conversation in conversations
        if conversation["id"] != conversation_id
    ]

    save_conversations(conversations)

    return conversations

def rename_conversation(conversation_id: str, new_title: str) -> None:
    conversations = load_conversations()

    for conversation in conversations:
        if conversation["id"] == conversation_id:
            conversation["title"] = new_title.strip() or "New Chat"
            conversation["updated_at"] = datetime.now().isoformat(timespec="seconds")
            break

    save_conversations(conversations)