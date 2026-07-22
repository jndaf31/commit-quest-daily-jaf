import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app import create_app


def create_test_app(database_path: Path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": database_path,
            "NOW_PROVIDER": lambda: datetime(2026, 7, 23, 10, 0, tzinfo=UTC),
        }
    )


def test_health_returns_ok_when_database_is_available(tmp_path: Path) -> None:
    app = create_test_app(tmp_path / "health.db")

    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_health_returns_unavailable_when_application_table_is_missing(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "health.db"
    app = create_test_app(database_path)

    with sqlite3.connect(database_path) as database:
        database.execute("DROP TABLE quest_completions")
        database.commit()

    response = app.test_client().get("/health")

    assert response.status_code == 503
    assert response.get_json() == {"status": "unavailable"}
    assert b"health.db" not in response.data
    assert b"quest_completions" not in response.data


def test_health_returns_non_sensitive_503_when_database_check_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    app = create_test_app(tmp_path / "health.db")
    monkeypatch.setattr("app.database_is_available", lambda: False)

    response = app.test_client().get("/health")

    assert response.status_code == 503
    assert response.get_json() == {"status": "unavailable"}
    assert b"health.db" not in response.data
    assert b"sqlite" not in response.data.lower()
