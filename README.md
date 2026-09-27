# aiogram_template

A modern [aiogram 3](https://docs.aiogram.dev/) bot template with batteries included
and a project workflow inherited from
[python-template](https://github.com/k0te1ch/python-template).

## What's inside

- **aiogram 3** — routers, FSM, custom filters and middlewares
- **pydantic-settings** — typed `.env` configuration (`config.py`)
- **loguru** — colored stdout + rotating file logs in `logs/`
- **FTL i18n** — per-language strings in `locales/*.ftl`, `{placeholder}` formatting
- **Redis / Memory** — FSM storage and APScheduler jobstore (auto-selected)
- **APScheduler** — background jobs (`services/scheduler.py`)
- **SQLAlchemy + Alembic** — optional database with migrations via the CLI
- **poetry** — dependency management
- **ruff** — lint + format
- **pre-commit** — `ruff` + `commitizen` on every commit
- **commitizen** — Conventional Commits validation and version bump
- **git-cliff** — automated `CHANGELOG.md` + GitHub Release notes (CI)
- **Docker / docker-compose** — bot + redis
- **pytest** + **[aiogram-testing](https://github.com/k0te1ch/aiogram_tests)** — handler tests through the real dispatcher (`tests/test_handlers.py`), no Telegram needed

## Project layout

```
.
├── main.py                 # bot + dispatcher wiring (entry via cli.py)
├── cli.py                  # click CLI: run, migrate, makemigrations, showmigrations
├── config.py               # pydantic-settings + loguru setup
├── handlers/               # routers (ROUTERS) + bot commands (COMMANDS)
├── filters/                # reusable aiogram filters (chat type, admin, i18n button)
├── forms/                  # FSM StatesGroups
├── keyboards/              # aiogram keyboard builders
├── middlewares/base/       # error, logging, user-context, chat-action middlewares
├── services/               # redis, scheduler, db, i18n context, init_services
├── locales/                # *.ftl translation files
├── models/                 # SQLAlchemy models
├── utils/                  # helpers
├── tests/                  # pytest suite
├── docs/WORKFLOW.md        # commits, branching and release workflow
└── logs/                   # rotating log files (git-ignored)
```

The example registration flow (`/start`), admin panel (`/admin_panel`) and scheduler
demo (`/deleteit`) are included to show the structure — delete them when you start
your own project.

## Quick start

1. Install dependencies and git hooks:

   ```bash
   poetry install
   poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg
   ```

2. Copy `.env.example` to `.env` and set at least `TELEGRAM_API_TOKEN`:

   ```bash
   cp .env.example .env
   ```

3. (Optional) create the database schema if `DATABASE=true`:

   ```bash
   poetry run python cli.py makemigrations
   poetry run python cli.py migrate
   ```

4. Run the bot:

   ```bash
   poetry run python cli.py run
   ```

5. Run tests:

   ```bash
   poetry run pytest
   ```

   `tests/test_handlers.py` drives the bot's own dispatcher (`main.dp`) with `BotTester`: send messages, press
   inline buttons and check FSM state. Live end-to-end checks against a real bot use tgtest (`pytest -m e2e`).

The `Makefile` wraps the common commands (`make install`, `make run`, `make test`,
`make lint`, `make format`, `make check`, `make bump`).

## Launch with Docker

```bash
docker compose build
docker compose up -d
```

This starts the bot together with a Redis instance (used for FSM storage and the
scheduler jobstore).

## Commits & releases

Full guide with diagrams — [docs/WORKFLOW.md](docs/WORKFLOW.md).

Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `docs:`, `feat(scope)!: …` for breaking, etc.). The commitizen
`commit-msg` hook rejects non-conforming messages.

To cut a release:

```bash
poetry run cz bump          # bumps version in pyproject.toml, commits, creates tag
git push --follow-tags      # pushing the tag triggers .github/workflows/release.yml
```

The release workflow generates Release Notes with `git-cliff --latest`, publishes a
GitHub Release, regenerates the full `CHANGELOG.md` and commits it back to `main`.

## Logging

Logs are written to `logs/` (rotating, git-ignored) and to colored stdout. Control the
verbosity with `LOG_LEVEL` in `.env`.
