import sqlite3
from pathlib import Path

from flask import Flask, current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS quest_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_id TEXT NOT NULL,
    completion_date TEXT NOT NULL,
    completed_at_utc TEXT NOT NULL,
    UNIQUE (quest_id, completion_date)
)
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(error: BaseException | None = None) -> None:
    database = g.pop("db", None)

    if database is not None:
        database.close()


def init_db() -> None:
    database = get_db()
    database.execute(SCHEMA)
    database.commit()


def get_completed_quest_ids(completion_date: str) -> set[str]:
    rows = get_db().execute(
        "SELECT quest_id FROM quest_completions WHERE completion_date = ?",
        (completion_date,),
    ).fetchall()

    return {row["quest_id"] for row in rows}


def get_completion_counts() -> dict[str, int]:
    rows = get_db().execute(
        """
        SELECT quest_id, COUNT(*) AS completion_count
        FROM quest_completions
        GROUP BY quest_id
        """
    ).fetchall()

    return {row["quest_id"]: row["completion_count"] for row in rows}


def get_completion_history() -> list[sqlite3.Row]:
    return get_db().execute(
        """
        SELECT quest_id, completion_date, completed_at_utc
        FROM quest_completions
        ORDER BY completion_date DESC, completed_at_utc ASC, id ASC
        """
    ).fetchall()


def record_completion(
    quest_id: str,
    completion_date: str,
    completed_at_utc: str,
) -> None:
    database = get_db()
    database.execute(
        """
        INSERT OR IGNORE INTO quest_completions (
            quest_id,
            completion_date,
            completed_at_utc
        ) VALUES (?, ?, ?)
        """,
        (quest_id, completion_date, completed_at_utc),
    )
    database.commit()


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
