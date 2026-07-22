from pathlib import Path

from app import configured_database_path, create_app


def test_database_uses_local_default_when_environment_variable_is_absent(
    monkeypatch,
) -> None:
    monkeypatch.delenv("COMMIT_QUEST_DATABASE", raising=False)
    default_path = Path("instance/commit-quest.db")

    assert configured_database_path(default_path) == default_path


def test_database_uses_environment_variable_when_present(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_path = tmp_path / "production" / "commit-quest.db"
    monkeypatch.setenv("COMMIT_QUEST_DATABASE", str(database_path))

    app = create_app({"TESTING": True})

    assert app.config["DATABASE"] == database_path
    assert database_path.is_file()
