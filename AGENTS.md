# Commit Quest Daily Check-in — Agent Instructions

## Purpose

Build a small, understandable daily check-in application as Phase 7 of João's VPS and networking mentorship. The application must be meaningfully owned and understood by João before deployment.

The VPS mentorship repository `jndaf31/vps-learning-project-jaf` remains the sole source of truth for server state, deployment constraints, and phase progress. This repository is the source of truth for the application code and its application-specific design.

## Current first-version scope

- Python and Flask backend.
- Server-rendered HTML and mobile-first CSS.
- Minimal JavaScript only where it clearly improves the interface.
- SQLite persistent state.
- Europe/Lisbon calendar dates.
- One user and a fixed daily checklist.
- Each task awards XP at most once per calendar day.
- Completion history and a non-sensitive health endpoint.
- Private Tailscale-only deployment after local application work is complete.

Do not add public authentication, registration, multiple accounts, third-party APIs, containers, automated deployment, or full Commit Quest synchronization unless a later approved issue explicitly introduces them.

## Teaching and implementation rules

- João is a programming and server-administration beginner working primarily from an Apple silicon MacBook. Prefer local repositories, a native editor and terminal, project-specific Python environments, and local tests.
- The independently verified iPhone with Termius remains a secondary VPS access and tested recovery path. GitHub Codespaces is an optional fallback rather than the default programming environment.
- Explain each new programming concept and important syntax before expecting João to use it.
- Use small, focused issues and beginner-readable changes.
- Do not introduce frameworks, abstractions, dependencies, or patterns without a concrete need.
- Prefer standard-library features where practical, but do not recreate security-sensitive framework functionality.
- Separate application code, templates, static assets, tests, and persistent data clearly.
- Never commit databases, virtual environments, secrets, local environment files, or generated caches.
- Use placeholders for any future secret configuration.

## Git workflow

- Do not push application changes directly to `main`.
- Create one focused feature branch per issue.
- Open a pull request for review before merging.
- Keep commits scoped and descriptive.
- Documentation-only corrections may be committed directly to `main` when they do not alter executable behavior.
- Do not deploy unmerged or unreviewed application code to the VPS.

## Security and data rules

- Treat every state-changing request as untrusted input.
- Use POST for state changes and GET for read-only views.
- Enforce the once-per-task-per-day XP rule in the database, not only in the interface.
- Do not expose stack traces, filesystem paths, database contents, or sensitive configuration through the health endpoint.
- Do not request or record passwords, tokens, private keys, or recovery codes.
- Keep persistent application state outside the deployed code directory in production.

## Definition of done for a feature

A feature is complete only when:

1. Its behavior is explained and understood.
2. Relevant tests pass.
3. Failure and edge cases are handled deliberately.
4. Documentation is updated where needed.
5. The pull request is reviewed before merge.
