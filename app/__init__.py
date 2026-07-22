from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from flask import Flask, abort, current_app, jsonify, redirect, render_template, request, url_for

from app.db import (
    database_is_available,
    get_completed_quest_ids,
    get_completion_counts,
    get_completion_history,
    init_app as init_database,
    record_completion,
)
from app.quests import QUESTS

LISBON_TIME_ZONE = ZoneInfo("Europe/Lisbon")
QUESTS_BY_ID = {quest["id"]: quest for quest in QUESTS}


def request_has_same_origin() -> bool:
    origin = request.headers.get("Origin")

    if origin is None:
        return False

    try:
        parsed_origin = urlsplit(origin)
    except ValueError:
        return False

    return (
        parsed_origin.scheme in {"http", "https"}
        and parsed_origin.netloc.casefold() == request.host.casefold()
    )


def current_time() -> datetime:
    provider: Callable[[], datetime] = current_app.config["NOW_PROVIDER"]
    return provider()


def current_lisbon_date() -> str:
    return current_time().astimezone(LISBON_TIME_ZONE).date().isoformat()


def build_history_days() -> list[dict]:
    history_days: list[dict] = []
    days_by_date: dict[str, dict] = {}

    for row in get_completion_history():
        quest = QUESTS_BY_ID.get(row["quest_id"])
        if quest is None:
            continue

        completion_date = row["completion_date"]
        if completion_date not in days_by_date:
            day = {"date": completion_date, "quests": [], "total_xp": 0}
            days_by_date[completion_date] = day
            history_days.append(day)

        day = days_by_date[completion_date]
        day["quests"].append(quest)
        day["total_xp"] += quest["xp"]

    return history_days


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
        completion_counts = get_completion_counts()
        total_xp = sum(
            quest["xp"] * completion_counts.get(quest["id"], 0)
            for quest in QUESTS
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

    @app.get("/history")
    def history() -> str:
        return render_template("history.html", history_days=build_history_days())

    @app.get("/health")
    def health():
        if database_is_available():
            return jsonify(status="ok"), 200

        return jsonify(status="unavailable"), 503

    @app.post("/quests/<quest_id>/complete")
    def complete_quest(quest_id: str):
        if quest_id not in QUESTS_BY_ID:
            abort(404)

        if not request_has_same_origin():
            abort(403)

        now = current_time()
        completion_date = now.astimezone(LISBON_TIME_ZONE).date().isoformat()
        completed_at_utc = now.astimezone(UTC).isoformat()
        record_completion(quest_id, completion_date, completed_at_utc)

        return redirect(url_for("index"))

    return app
