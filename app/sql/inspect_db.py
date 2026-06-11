"""
Ελέγχουμε 3 πράγματα:

- Ποιά tables υπάρχουν
- Τι columns_name έχει το players_stats
- Αν δουλεύει ένα κανονικό SQL query
"""

import sqlite3
from pathlib import Path

import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).parents[2]


def connect_to_db(db_path: Path):
    return sqlite3.connect(db_path)


def show_tables(connection) -> pd.DataFrame:
    query = """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table';
    """

    return pd.read_sql_query(query, connection)


def show_table_schema(connection, table_name: str) -> pd.DataFrame:
    query = f"""
    PRAGMA table_info({table_name});
    """

    return pd.read_sql_query(query, connection)


def run_sample_query(connection) -> pd.DataFrame:
    query = """
    SELECT
        PLAYER_NAME,
        TEAM_ABBREVIATION,
        PTS,
        REB,
        AST
    FROM player_stats
    ORDER BY AST DESC
    LIMIT 10;
    """

    return pd.read_sql_query(query, connection)


if __name__ == "__main__":
    project_root = get_project_root()
    db_path = project_root / "data" / "nba_stats.db"

    connection = connect_to_db(db_path)

    print("\nTables:")
    print(show_tables(connection))

    print("\nSchema for player_stats:")
    print(show_table_schema(connection, "player_stats"))

    print("\nTop 10 players by assists:")
    print(run_sample_query(connection))

    connection.close()