from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from flask import Flask, abort, current_app, redirect, render_template, request, url_for

from app.db import get_completed_quest_ids, init_app as init_database, record_completion
from app.quests import QUESTS

LISBON_TIME_ZONE = ZoneInfo("Europe/Lisbon")


def request_has_same_origin() -> bool:
    origin = request.headers.get("Origin")

    if origin is None:
        return False

    parsed_origin = urlsplit(origin)

    return (
        parsed_origin.scheme in {"http", "https"}
        and parsed_origin.netloc.casefold() == request.host.casefold()
    )


def current_time() -> datetime:
    provider: Callable[[], datetime] = current_app.config["NOW_PROVIDER"]
    return provider()


def current_lisbon_date() -> str:
    return current_time().astimezone(LISBON_TIME_ZONE).date().isoformat()


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=Path(app.instance_path) / "commit-quest.db",
        NOW_PROVIDER=lambda: datetime.now(UTC),
    )

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_database(app)

    @app.get("/")
    def index() -> str:
        completion_date = current_lisbon_date()
        completed_quest_ids = get_completed_quest_ids(completion_date)
        total_xp = sum(
            quest["xp"] for quest in QUESTS if quest["id"] in completed_quest_ids
        )
        level = total_xp // 100 + 1
        xp_progress = total_xp % 100

        return render_template(
            "index.html",
            quests=QUESTS,
            completed_quest_ids=completed_quest_ids,
            total_xp=total_xp,
            level=level,
            xp_progress=xp_progress,
        )

    @app.post("/quests/<quest_id>/complete")
    def complete_quest(quest_id: str):
        valid_quest_ids = {quest["id"] for quest in QUESTS}

        if quest_id not in valid_quest_ids:
            abort(404)

        if not request_has_same_origin():
            abort(403)

        now = current_time()
        completion_date = now.astimezone(LISBON_TIME_ZONE).date().isoformat()
        completed_at_utc = now.astimezone(UTC).isoformat()
        record_completion(quest_id, completion_date, completed_at_utc)

        return redirect(url_for("index"))

    return app
