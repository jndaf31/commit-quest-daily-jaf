# Commit Quest Daily Check-in

A small mobile-first daily checklist inspired by Commit Quest. Completing daily tasks awards XP, builds a completion history, and will persist progress in SQLite.

This application is being built as Phase 7 of João's VPS and networking mentorship. The first version uses Python, Flask, server-rendered HTML, minimal JavaScript, SQLite, and the Europe/Lisbon time zone.

## Current state

The home page renders four fixed daily quests defined in Python. Each quest has a stable identifier, a title, and an XP reward. The current four quests total 100 XP.

Quests can now be completed through HTML forms. The server calculates total XP, current level, and progress toward the next level. Completion is temporarily held in a Python `set` inside the running Flask application, so it resets whenever the application process restarts or a new application instance is created.

SQLite persistence, daily date boundaries, history, health monitoring, and VPS deployment have not been added yet.

## Initial scope

- One user.
- A fixed daily checklist.
- Each task can award XP once per Lisbon calendar day.
- Persistent completion history.
- Mobile-first interface.
- A small health endpoint for service monitoring.
- Private deployment through Tailscale after the application is complete and reviewed.

## Deliberately excluded from the first version

- Public access.
- User registration or passwords.
- Multiple accounts.
- Third-party APIs.
- Full synchronization with the original Commit Quest application.
- Containers or automated deployment.

Full Commit Quest synchronization will be evaluated after the daily check-in application is complete, deployed, backed up, monitored, and understood.

## Local development

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the tests:

```bash
pytest
```

Run the development server:

```bash
flask --app app:create_app run
```

Then open `http://127.0.0.1:5000`.

## Development workflow

- Work from a focused GitHub issue.
- Use a feature branch for application changes.
- Open a pull request before merging to `main`.
- Keep commits small and beginner-readable.
- Do not deploy unfinished work to the VPS.
