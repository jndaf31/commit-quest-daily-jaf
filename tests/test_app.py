from app import create_app
from app.quests import QUESTS


def test_index_returns_application_title() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Commit Quest Daily Check-in" in response.data


def test_index_renders_all_daily_quests() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/")
    page = response.get_data(as_text=True)

    assert len(QUESTS) == 4

    for quest in QUESTS:
        assert quest["title"] in page
        assert f'{quest["xp"]} XP' in page
