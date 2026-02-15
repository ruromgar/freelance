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

- **invoicing**: Full invoicing system (BusinessProfile, Client, Invoice, InvoiceLineItem, Payment, PDF generation)
- **fiscal**: Fiscal management for autónomos (FiscalYear, Quarter, Expense, QuarterlyResult, modelos 303/130/390)

### Configuration Structure

- `config/settings/base.py`: Main settings
- `config/settings/dev.py` / `prod.py`: Environment-specific overrides
- Environment variables loaded from `.env` (see `.env.example`)

### URL Structure

- `/` - Invoicing app dashboard
- `/fiscal/` - Fiscal management
- `/room/` - Django admin (uses Unfold theme)

### Multi-tenancy

The project uses BusinessProfile as the central entity for multi-tenant isolation:
- Users are connected to BusinessProfiles via BusinessMembership
- All models (Invoice, Client, FiscalYear, Expense) have a business_profile FK
- Views use `@require_business` decorator from `apps.invoicing.services.permissions`

### Fiscal Calculations

The fiscal app calculates Spanish tax forms:
- **Modelo 303** (VAT quarterly): Reads from Invoice + InvoiceLineItem for income, Expense for deductible VAT
- **Modelo 130** (IRPF quarterly): Cumulative calculation including "gastos de difícil justificación" (5% of income, max 2000€/year)
- **Modelo 390** (VAT annual): Aggregates quarterly modelo 303 results

## Code Guidelines

### Import Restrictions

The project enforces import isolation between apps via `config/project_guidelines.py` (runs as pre-commit hook). Apps cannot import from other apps except through allowed namespaces: `api`, `ninja`, `tests`.

**Exception**: The fiscal app imports from invoicing for Invoice model and permissions service.

### Pre-commit Hooks

The project uses pre-commit hooks including:
- ruff (linting + formatting)
- mypy, pydocstyle
- djhtml/djcss/djjs for template formatting
- gitleaks for secret detection
- Migration check (ensures no uncreated migrations)
- Project guidelines check (import isolation)

Run `pre-commit install` after cloning.
