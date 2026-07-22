# Commit Quest Daily Check-in

A small mobile-first daily checklist inspired by Commit Quest. Completing daily tasks awards XP and stores progress in SQLite.

This application is being built as Phase 7 of João's VPS and networking mentorship. The first version uses Python, Flask, server-rendered HTML, minimal JavaScript, SQLite, and the Europe/Lisbon time zone.

## Current state

The home page renders four fixed daily quests defined in Python. Each quest has a stable identifier, a title, and an XP reward. The current four quests total 100 XP.

Quest completions are stored in SQLite. Each record contains a quest ID, a Europe/Lisbon completion date, and a UTC timestamp. A database uniqueness constraint ensures that each quest awards XP only once per Lisbon calendar day. Completion survives application restarts, while a new Lisbon day begins with an incomplete daily checklist.

The server calculates total XP, current level, and progress toward the next level from today's stored records. State-changing forms require a same-origin request.

History views, health monitoring, deployment configuration, and VPS deployment have not been added yet.

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

Then open `http://127.0.0.1:5000`.

The development database is created automatically as `instance/commit-quest.db`. Flask's instance directory is ignored by Git and is intended for local runtime data rather than source code.

## Development workflow

- Work from a focused GitHub issue.
- Use a feature branch for application changes.
- Open a pull request before merging to `main`.
- Keep commits small and beginner-readable.
- Do not deploy unfinished work to the VPS.
