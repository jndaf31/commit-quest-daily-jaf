from app import create_app


def test_index_returns_application_title() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Commit Quest Daily Check-in" in response.data
