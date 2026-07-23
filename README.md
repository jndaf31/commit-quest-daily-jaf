# Commit Quest Daily Check-in

A small mobile-first daily checklist inspired by Commit Quest. Completing daily tasks awards XP and stores progress in SQLite.

This application is being built as Phase 7 of João's VPS and networking mentorship. The first version uses Python, Flask, server-rendered HTML, minimal JavaScript, SQLite, and the Europe/Lisbon time zone.

## Current state

The home page renders four fixed daily quests defined in Python. Each quest has a stable identifier, a title, and an XP reward. The current four quests total 100 XP.

Quest completions are stored in SQLite. Each record contains a quest ID, a Europe/Lisbon completion date, and a UTC timestamp. A database uniqueness constraint ensures that each quest awards XP only once per Lisbon calendar day. Completion survives application restarts, while a new Lisbon day begins with an incomplete daily checklist.

The server calculates lifetime XP, current level, and progress toward the next level from all recognized stored completion records. State-changing forms require a same-origin request.

A read-only `/history` page groups recognized completions by Lisbon date, shows newest days first, lists the completed quests, and calculates the XP earned on each day. Unknown historical quest IDs are ignored safely.

A read-only `/health` endpoint checks that the application can query SQLite. It returns `{"status": "ok"}` with HTTP 200 when healthy and a non-sensitive `{"status": "unavailable"}` with HTTP 503 when the database check fails.

Deployment configuration and VPS deployment have not been added yet.

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

The verified primary development environment is an Apple silicon Mac using
uv-managed Python 3.12. Create and activate the project-specific virtual
environment:

```bash
uv python install 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
```

Install the development dependencies and run the tests:

```bash
uv pip install -r requirements-dev.txt
python -m pytest
```

The virtual environment remains the standard Python `.venv` layout, so editors
and ordinary Python commands can use it without depending on uv at runtime.
On another supported environment, the equivalent standard-library creation
command is `python3 -m venv .venv`.

The project also configures pytest so the shorter `pytest` command can import the local `app` package correctly.

Run the development server:

```bash
flask --app app:create_app run
```

Then open `http://127.0.0.1:5000`. The health endpoint is available at `http://127.0.0.1:5000/health`.

The development database is created automatically as `instance/commit-quest.db`. Flask's instance directory is ignored by Git and is intended for local runtime data rather than source code.

## Development workflow

- Work from a focused GitHub issue.
- Use a feature branch for application changes.
- Open a pull request before merging to `main`.
- Keep commits small and beginner-readable.
- Do not deploy unfinished work to the VPS.
