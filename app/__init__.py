from flask import Flask, render_template

from app.quests import QUESTS


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return render_template("index.html", quests=QUESTS)

    return app
