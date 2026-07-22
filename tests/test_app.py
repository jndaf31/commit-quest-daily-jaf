import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app import create_app
from app.quests import QUESTS

SAME_ORIGIN_HEADERS = {"Origin": "http://localhost"}
DEFAULT_NOW = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)


def create_test_app(
    database_path: Path, now: datetime = DEFAULT_NOW
):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": database_path,
            "NOW_PROVIDER": lambda: now,
        }
    )


def test_index_returns_application_title(tmp_path: Path) -> None:
    app = create_test_app(tmp_path / "test.db")
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Commit Quest Daily Check-in" in response.data


def test_index_renders_all_daily_quests(tmp_path: Path) -> None:
    app = create_test_app(tmp_path / "test.db")
    client = app.test_client()

    page = client.get("/").get_data(as_text=True)

    assert len(QUESTS) == 4

    for quest in QUESTS:
        assert quest["title"] in page
        assert f'{quest["xp"]} XP' in page


def test_completing_quest_redirects_and_updates_xp(tmp_path: Path) -> None:
    app = create_test_app(tmp_path / "test.db")
    client = app.test_client()
    quest = QUESTS[0]

    response = client.post(
        f'/quests/{quest["id"]}/complete', headers=SAME_ORIGIN_HEADERS
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    page = client.get("/").get_data(as_text=True)

    assert "Completed" in page
    assert f'<dd>{quest["xp"]}</dd>' in page
    assert f'<dd>{quest["xp"]} / 100 XP</dd>' in page


def test_completing_same_quest_twice_does_not_duplicate_xp(tmp_path: Path) -> None:
    database_path = tmp_path / "test.db"
    app = create_test_app(database_path)
    client = app.test_client()
    quest = QUESTS[0]
    completion_url = f'/quests/{quest["id"]}/complete'

    client.post(completion_url, headers=SAME_ORIGIN_HEADERS)
    client.post(completion_url, headers=SAME_ORIGIN_HEADERS)
    page = client.get("/").get_data(as_text=True)

    with sqlite3.connect(database_path) as database:
        row_count = database.execute(
            "SELECT COUNT(*) FROM quest_completions"
        ).fetchone()[0]

    assert row_count == 1
    assert f'<dd>{quest["xp"]}</dd>' in page
    assert f'<dd>{quest["xp"] * 2}</dd>' not in page


def test_unknown_quest_returns_404(tmp_path: Path) -> None:
    app = create_test_app(tmp_path / "test.db")
    client = app.test_client()

    response = client.post(
        "/quests/not-a-real-quest/complete", headers=SAME_ORIGIN_HEADERS
    )

    assert response.status_code == 404


def test_missing_origin_is_rejected_without_changing_xp(tmp_path: Path) -> None:
    app = create_test_app(tmp_path / "test.db")
    client = app.test_client()
    quest = QUESTS[0]

    response = client.post(f'/quests/{quest["id"]}/complete')
    page = client.get("/").get_data(as_text=True)

    assert response.status_code == 403
    assert f'<dd>{quest["xp"]}</dd>' not in page
    assert "Completed" not in page


def test_cross_origin_request_is_rejected_without_changing_xp(
    tmp_path: Path,
) -> None:
    app = create_test_app(tmp_path / "test.db")
    client = app.test_client()
    quest = QUESTS[0]

    response = client.post(
        f'/quests/{quest["id"]}/complete',
        headers={"Origin": "https://unrelated.example"},
    )
    page = client.get("/").get_data(as_text=True)

    assert response.status_code == 403
    assert f'<dd>{quest["xp"]}</dd>' not in page
    assert "Completed" not in page


def test_completing_all_quests_reaches_level_two(tmp_path: Path) -> None:
    app = create_test_app(tmp_path / "test.db")
    client = app.test_client()

    for quest in QUESTS:
        client.post(
            f'/quests/{quest["id"]}/complete', headers=SAME_ORIGIN_HEADERS
        )

    page = client.get("/").get_data(as_text=True)

    assert "<dd>2</dd>" in page
    assert "<dd>100</dd>" in page
    assert "<dd>0 / 100 XP</dd>" in page


def test_completion_survives_application_recreation(tmp_path: Path) -> None:
    database_path = tmp_path / "persistent.db"
    quest = QUESTS[0]

    first_app = create_test_app(database_path)
    first_app.test_client().post(
        f'/quests/{quest["id"]}/complete', headers=SAME_ORIGIN_HEADERS
    )

    second_app = create_test_app(database_path)
    second_page = second_app.test_client().get("/").get_data(as_text=True)

    assert "Completed" in second_page
    assert f'<dd>{quest["xp"]}</dd>' in second_page


def test_same_quest_can_be_completed_on_another_lisbon_date(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "daily.db"
    quest = QUESTS[0]
    first_day = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    second_day = datetime(2026, 7, 23, 10, 0, tzinfo=UTC)

    first_app = create_test_app(database_path, first_day)
    first_app.test_client().post(
        f'/quests/{quest["id"]}/complete', headers=SAME_ORIGIN_HEADERS
    )

    second_app = create_test_app(database_path, second_day)
    second_client = second_app.test_client()
    page_before_completion = second_client.get("/").get_data(as_text=True)
    second_client.post(
        f'/quests/{quest["id"]}/complete', headers=SAME_ORIGIN_HEADERS
    )

    with sqlite3.connect(database_path) as database:
        completion_dates = database.execute(
            """
            SELECT completion_date
            FROM quest_completions
            WHERE quest_id = ?
            ORDER BY completion_date
            """,
            (quest["id"],),
        ).fetchall()

    assert "Completed" not in page_before_completion
    assert completion_dates == [("2026-07-22",), ("2026-07-23",)]
