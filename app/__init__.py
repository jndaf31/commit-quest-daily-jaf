from urllib.parse import urlsplit

from flask import Flask, abort, redirect, render_template, request, url_for

from app.quests import QUESTS


def request_has_same_origin() -> bool:
    origin = request.headers.get("Origin")

    if origin is None:
        return False

    parsed_origin = urlsplit(origin)

    return (
        parsed_origin.scheme in {"http", "https"}
        and parsed_origin.netloc.casefold() == request.host.casefold()
    )


def create_app() -> Flask:
    app = Flask(__name__)
    completed_quest_ids: set[str] = set()

    @app.get("/")
    def index() -> str:
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

        completed_quest_ids.add(quest_id)
        return redirect(url_for("index"))

    return app
