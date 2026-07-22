from app import create_app
from app.quests import QUESTS

SAME_ORIGIN_HEADERS = {"Origin": "http://localhost"}


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


def test_completing_quest_redirects_and_updates_xp() -> None:
    app = create_app()
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


def test_completing_same_quest_twice_does_not_duplicate_xp() -> None:
    app = create_app()
    client = app.test_client()
    quest = QUESTS[0]
    completion_url = f'/quests/{quest["id"]}/complete'

    client.post(completion_url, headers=SAME_ORIGIN_HEADERS)
    client.post(completion_url, headers=SAME_ORIGIN_HEADERS)
    page = client.get("/").get_data(as_text=True)

    assert f'<dd>{quest["xp"]}</dd>' in page
    assert f'<dd>{quest["xp"] * 2}</dd>' not in page


def test_unknown_quest_returns_404() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/quests/not-a-real-quest/complete", headers=SAME_ORIGIN_HEADERS
    )

    assert response.status_code == 404


def test_missing_origin_is_rejected_without_changing_xp() -> None:
    app = create_app()
    client = app.test_client()
    quest = QUESTS[0]

    response = client.post(f'/quests/{quest["id"]}/complete')
    page = client.get("/").get_data(as_text=True)

    assert response.status_code == 403
    assert f'<dd>{quest["xp"]}</dd>' not in page
    assert "Completed" not in page


def test_cross_origin_request_is_rejected_without_changing_xp() -> None:
    app = create_app()
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


def test_completing_all_quests_reaches_level_two() -> None:
    app = create_app()
    client = app.test_client()

    for quest in QUESTS:
        client.post(
            f'/quests/{quest["id"]}/complete', headers=SAME_ORIGIN_HEADERS
        )

    page = client.get("/").get_data(as_text=True)

    assert "<dd>2</dd>" in page
    assert "<dd>100</dd>" in page
    assert "<dd>0 / 100 XP</dd>" in page


def test_new_application_starts_with_no_completed_quests() -> None:
    first_app = create_app()
    first_client = first_app.test_client()
    first_client.post(
        f'/quests/{QUESTS[0]["id"]}/complete', headers=SAME_ORIGIN_HEADERS
    )

    second_app = create_app()
    second_page = second_app.test_client().get("/").get_data(as_text=True)

    assert "<dd>0</dd>" in second_page
    assert "Completed" not in second_page
