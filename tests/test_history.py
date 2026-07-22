import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app import create_app
from app.quests import QUESTS


def create_test_app(database_path: Path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": database_path,
            "NOW_PROVIDER": lambda: datetime(2026, 7, 23, 10, 0, tzinfo=UTC),
        }
    )


def insert_completion(
    database_path: Path,
    quest_id: str,
    completion_date: str,
    completed_at_utc: str,
) -> None:
    with sqlite3.connect(database_path) as database:
        database.execute(
            "INSERT INTO quest_completions (quest_id, completion_date, completed_at_utc) VALUES (?, ?, ?)",
            (quest_id, completion_date, completed_at_utc),
        )
        database.commit()


def test_history_shows_empty_state(tmp_path: Path) -> None:
    app = create_test_app(tmp_path / "history.db")

    response = app.test_client().get("/history")

    assert response.status_code == 200
    assert b"No completions have been recorded yet." in response.data


def test_history_orders_days_and_calculates_daily_xp(tmp_path: Path) -> None:
    database_path = tmp_path / "history.db"
    app = create_test_app(database_path)

    insert_completion(
        database_path,
        QUESTS[0]["id"],
        "2026-07-22",
        "2026-07-22T08:00:00+00:00",
    )
    insert_completion(
        database_path,
        QUESTS[1]["id"],
        "2026-07-23",
        "2026-07-23T09:00:00+00:00",
    )
    insert_completion(
        database_path,
        QUESTS[2]["id"],
        "2026-07-23",
        "2026-07-23T10:00:00+00:00",
    )

    page = app.test_client().get("/history").get_data(as_text=True)

    assert page.index("2026-07-23") < page.index("2026-07-22")
    assert page.index(QUESTS[1]["title"]) < page.index(QUESTS[2]["title"])
    assert f'{QUESTS[1]["xp"] + QUESTS[2]["xp"]} XP' in page
    assert f'{QUESTS[0]["xp"]} XP' in page


def test_history_ignores_unknown_quest_ids(tmp_path: Path) -> None:
    database_path = tmp_path / "history.db"
    app = create_test_app(database_path)

    insert_completion(
        database_path,
        "retired-quest",
        "2026-07-23",
        "2026-07-23T08:00:00+00:00",
    )
    insert_completion(
        database_path,
        QUESTS[0]["id"],
        "2026-07-23",
        "2026-07-23T09:00:00+00:00",
    )

    page = app.test_client().get("/history").get_data(as_text=True)

    assert "retired-quest" not in page
    assert QUESTS[0]["title"] in page
    assert f'{QUESTS[0]["xp"]} XP' in page
