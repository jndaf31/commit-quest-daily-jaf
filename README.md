# Commit Quest Daily Check-in

A small mobile-first daily checklist inspired by Commit Quest. Completing daily tasks awards XP and stores progress in SQLite.

This application is being built as Phase 7 of João's VPS and networking mentorship. The first version uses Python, Flask, server-rendered HTML, minimal JavaScript, SQLite, and the Europe/Lisbon time zone.

## Current state

The home page renders four fixed daily quests defined in Python. Each quest has a stable identifier, a title, and an XP reward. The current four quests total 100 XP.

Quest completions are stored in SQLite. Each record contains a quest ID, a Europe/Lisbon completion date, and a UTC timestamp. A database uniqueness constraint ensures that each quest awards XP only once per Lisbon calendar day. Completion survives application restarts, while a new Lisbon day begins with an incomplete daily checklist.

The server calculates lifetime XP, current level, and progress toward the next level from all recognized stored completion records. State-changing forms require a same-origin request.

A read-only `/history` page groups recognized completions by Lisbon date, shows newest days first, lists the completed quests, and calculates the XP earned on each day. Unknown historical quest IDs are ignored safely.

A read-only `/health` endpoint checks that the application can query SQLite. It returns `{"status": "ok"}` with HTTP 200 when healthy and a non-sensitive `{"status": "unavailable"}` with HTTP 503 when the database check fails.

The application can read its production SQLite path from the
`COMMIT_QUEST_DATABASE` environment variable. Gunicorn is pinned as the
production web server. VPS provisioning has not been performed yet.

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

Run the tests with the active Python interpreter:

```bash
python -m pytest
```

The project also configures pytest so the shorter `pytest` command can import the local `app` package correctly.

Run the development server:

```bash
flask --app app:create_app run
```

Then open `http://127.0.0.1:5000`. The health endpoint is available at `http://127.0.0.1:5000/health`.

The development database is created automatically as `instance/commit-quest.db`. Flask's instance directory is ignored by Git and is intended for local runtime data rather than source code.

## Production entry point

Install the pinned production dependencies in a dedicated virtual environment:

```bash
python -m pip install -r requirements-prod.txt
```

Set `COMMIT_QUEST_DATABASE` to the persistent SQLite path outside the release
directory, then start one Gunicorn worker on the loopback-only backend listener:

```bash
COMMIT_QUEST_DATABASE=/var/lib/commit-quest-daily/commit-quest.db \
  gunicorn --bind 127.0.0.1:8001 --workers 1 --threads 2 \
  --access-logfile - --error-logfile - --no-control-socket \
  --access-logformat 'pid=%(p)s method=%(m)s path=%(U)s status=%(s)s bytes=%(B)s duration_seconds=%(L)s' \
  'app:create_app()'
```

Gunicorn remains in the foreground so a service manager can supervise it. Both
logs go to standard output or standard error for capture by the service manager.
The access log uses compact `key=value` fields and avoids request bodies, query
strings, database contents, and environment values.
The unused runtime control socket is disabled, so Gunicorn does not need another
writable directory.
The listener is intentionally local: a separate HTTPS reverse proxy provides
the private user-facing connection.

## Development workflow

- Work from a focused GitHub issue.
- Use a feature branch for application changes.
- Open a pull request before merging to `main`.
- Keep commits small and beginner-readable.
- Do not deploy unfinished work to the VPS.
