import re

import ollama

from app.sql.sql_executor import execute_sql_query


OLLAMA_MODEL = "qwen3:8b"


DATABASE_SCHEMA = """
Table: player_stats

Columns:
- PLAYER_NAME: player full name
- TEAM_ABBREVIATION: NBA team abbreviation
- GP: games played
- MIN: minutes per game
- PTS: points per game
- REB: rebounds per game
- AST: assists per game
- STL: steals per game
- BLK: blocks per game
- TOV: turnovers per game
- FG_PCT: field goal percentage
- FG3_PCT: three point percentage
- FT_PCT: free throw percentage
"""


def extract_sql(text: str) -> str:
    """
    Extracts SQL from the model response.
    """

    code_block_match = re.search(
        r"```sql\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if code_block_match:
        return code_block_match.group(1).strip()

    return text.strip()


def generate_sql(question: str) -> str:
    """
    Uses a local Ollama model to generate a SQL SELECT query.
    """

    prompt = f"""
You are a Text-to-SQL assistant.

Your task is to write ONE valid SQLite SELECT query.

Use ONLY this database schema:

{DATABASE_SCHEMA}

Rules:
- Return ONLY the SQL query.
- Do not explain.
- Do not use markdown unless necessary.
- Use only the player_stats table.
- Never write INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, REPLACE, or TRUNCATE.
- If the user asks for best/top players, use ORDER BY and LIMIT.
- For percentages, columns like FG_PCT, FG3_PCT, FT_PCT are stored as decimal values.

User question:
{question}

SQL:
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

    raw_response = response["message"]["content"]

    return extract_sql(raw_response)


def answer_sql_question(question: str) -> str:
    """
    Generates SQL, executes it, and returns a user-friendly answer.
    """

    sql_query = generate_sql(question)

    result_df = execute_sql_query(sql_query)

    if result_df.empty:
        return "I could not find matching NBA statistics for this question."

    result_text = result_df.to_string(index=False)

    prompt = f"""
You are an NBA statistics assistant.

The user asked:
{question}

The SQL query returned this result:
{result_text}

Write a clear, concise natural language answer for the user.

Rules:
- Do NOT mention the SQL query.
- Do NOT say "based on the SQL result".
- Do NOT include table formatting unless needed.
- Answer directly.
- If there are multiple players, list them clearly.
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

    return response["message"]["content"].strip()


if __name__ == "__main__":
    question = "Who are the top 5 players by assists?"

    answer = answer_sql_question(question)

    print(answer)