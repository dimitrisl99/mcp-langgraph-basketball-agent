import sqlite3
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import LeagueDashPlayerStats


SEASON = "2024-25"


def get_project_root() -> Path:
    return Path(__file__).parents[2]


def fetch_player_stats() -> pd.DataFrame:
    """
    Downloads NBA player statistics from nba_api.
    """

    print("Downloading NBA player stats...")

    stats = LeagueDashPlayerStats(
        season=SEASON,
        per_mode_detailed="PerGame",
    )

    #Μετατρέπει το API response σε Pandas DataFrame
    df = stats.get_data_frames()[0]

    print(f"Players downloaded: {len(df)}")

    return df

#keep some columns
def keep_relevant_columns(df: pd.DataFrame) -> pd.DataFrame:

    columns = [
        "PLAYER_NAME",
        "TEAM_ABBREVIATION",
        "GP",
        "MIN",
        "PTS",
        "REB",
        "AST",
        "STL",
        "BLK",
        "TOV",
        "FG_PCT",
        "FG3_PCT",
        "FT_PCT",
    ]

    return df[columns]


def save_to_sqlite(df: pd.DataFrame, db_path: Path) -> None:
    """
    Saves the dataframe to SQLite.
    """

    connection = sqlite3.connect(db_path)

    df.to_sql(
        "player_stats",
        connection,
        if_exists="replace",
        index=False,
    )

    connection.close()


if __name__ == "__main__":

    project_root = get_project_root()

    db_path = project_root / "data" / "nba_stats.db"

    df = fetch_player_stats()

    df = keep_relevant_columns(df)

    save_to_sqlite(df, db_path)

    print(f"\nDatabase created:")
    print(db_path)

    print("\nSample rows:\n")
    print(df.head())