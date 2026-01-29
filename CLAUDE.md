# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses `uv` for Python package management and provides a Makefile for common tasks:

```bash
make install       # Install dependencies (uv sync)
make run           # Run development server
make test          # Run tests
make lint          # Run ruff linter
make format        # Format code with ruff
make migrate       # Apply database migrations
make migrations    # Create new migrations
make shell         # Open Django shell_plus
make app name=X    # Create a new Django app
make command app=X name=Y  # Create a management command
```

## Architecture

This is a Django 5.x monolith using the multi-app pattern. All apps live under `apps/`.

### Apps

- **core**: Base app with user profiles and authentication templates
- **freelance**: Fiscal management for autónomos (modelos 303, 130, 390)

### Configuration Structure

- `config/settings/base.py`: Main settings, imports app-specific settings from `config/settings/apps/`
- `config/settings/dev.py` / `prod.py`: Environment-specific overrides
- Environment variables loaded from `.env` (see `.env.example`)

### URL Structure

- `/` - Freelance app (home)
- `/room/` - Django admin (uses Unfold theme)

## Code Guidelines

### Import Restrictions

The project enforces import isolation between apps via `config/project_guidelines.py` (runs as pre-commit hook). Apps cannot import from other apps except through allowed namespaces: `api`, `ninja`, `tests`.

### Pre-commit Hooks

The project uses pre-commit hooks including:
- ruff (linting + formatting)
- mypy, pydocstyle
- djhtml/djcss/djjs for template formatting
- gitleaks for secret detection
- Migration check (ensures no uncreated migrations)
- Project guidelines check (import isolation)

Run `pre-commit install` after cloning.
