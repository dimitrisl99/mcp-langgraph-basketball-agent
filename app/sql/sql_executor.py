import sqlite3
from pathlib import Path

import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).parents[2]


def get_database_path() -> Path:
    project_root = get_project_root()
    return project_root / "data" / "nba_stats.db"


def is_safe_select_query(sql_query: str) -> bool:
    """
    Allows only SELECT queries for safety.
    """
    cleaned_query = sql_query.strip().lower()

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "replace",
        "truncate",
    ]

    if not cleaned_query.startswith("select"):
        return False

    for keyword in forbidden_keywords:
        if keyword in cleaned_query:
            return False

    return True


def execute_sql_query(sql_query: str) -> pd.DataFrame:
    """
    Executes a safe SELECT query against the NBA SQLite database.
    """

    if not is_safe_select_query(sql_query):
        raise ValueError("Only safe SELECT queries are allowed.")

    db_path = get_database_path()

    connection = sqlite3.connect(db_path)

    try:
        df = pd.read_sql_query(sql_query, connection)
    finally:
        connection.close()

    return df


if __name__ == "__main__":
    query = """
    SELECT
        PLAYER_NAME,
        TEAM_ABBREVIATION,
        AST
    FROM player_stats
    ORDER BY AST DESC
    LIMIT 5;
    """

    result = execute_sql_query(query)

    print(result)