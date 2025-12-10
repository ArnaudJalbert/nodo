# CLI Torrent Download Manager - Development Guide

## Overview

A CLI-based torrent download manager built with **Clean Architecture** principles, following Robert C. Martin's architecture patterns.

## Quick Reference

- **[Clean Architecture Layers](./docs/architecture/layers.md)** - Layer definitions, dependencies, and rules
- **[Domain Model](./docs/architecture/domain.md)** - Entities, value objects, and business rules
- **[Use Cases](./docs/architecture/use_cases.md)** - 10 implemented use cases (4 more planned)
- **[Testing Guide](./docs/development/testing.md)** - Testing requirements, patterns, and coverage mandate
- **[Code Quality](./docs/development/code_quality.md)** - Ruff formatting, linting, and type hints
- **[Dependency Injection](./docs/architecture/dependency_injection.md)** - Protocol-based DI patterns
- **[Technology Stack](./docs/development/tech_stack.md)** - Dependencies, tools, and setup
- **[Project Structure](./docs/architecture/project_structure.md)** - File organization

## Core Principles

1. **Clean Architecture** - Strict layer separation with dependency inversion
2. **100% Test Coverage** - Non-negotiable testing requirement
3. **Type Safety** - Full type hints everywhere
4. **Code Quality** - Ruff-formatted and lint-free code only
5. **Documentation** - MkDocs maintained alongside code

## Quick Start Checklist

Before writing any code:

```bash
# 1. Read architecture layers
cat docs/architecture/layers.md

# 2. Understand domain model
cat docs/architecture/domain.md

# 3. Review testing requirements
cat docs/development/testing.md

# 4. Set up environment
uv sync --dev

# 5. Format & test before commit
ruff format . && ruff check --fix . && pytest --cov=src --cov-fail-under=100
```

## Development Workflow

1. **Read relevant architecture docs** - Understand the layer you're working in
2. **Write tests first** (TDD) or immediately after
3. **Format & lint** - `ruff format . && ruff check --fix .`
4. **Run tests** - `pytest --cov=src --cov-fail-under=100`
5. **Update docs** - Keep MkDocs current
6. **Update CHANGELOG.md** - Document your changes

## Key Commands

```bash
# Development
ruff format .                          # Format code
ruff check --fix .                     # Lint with auto-fix
pytest --cov=src --cov-fail-under=100  # Test with coverage

# Documentation
mkdocs serve                           # Serve docs locally
mkdocs build                           # Build static site

# Running the app
# CLI to be implemented
# uv run python -m nodo.infrastructure.cli.main

# Documentation server
uv run nodo-docs
```

## Critical Rules

❌ **Never violate these:**
- No code without tests (100% coverage)
- No unformatted code (must run `ruff format`)
- No lint errors (must pass `ruff check`)
- No circular dependencies between layers
- No concrete implementations in domain/application layers

✅ **Always do:**
- Follow Clean Architecture layers strictly
- Use Protocol-based dependency injection
- Write tests using plain pytest functions (not classes)
- Document as you code (not after)
- Update CHANGELOG.md for every feature

## Getting Help

- **Architecture questions?** → Read `docs/architecture/layers.md`
- **Use case patterns?** → Read `docs/architecture/use_cases.md`
- **Testing confused?** → Read `docs/development/testing.md`
- **DI not clear?** → Read `docs/architecture/dependency_injection.md`

## Project Status

Current implementation status: **Domain & Application Layers Complete**

Core components:
- ✅ Domain entities and value objects (complete)
- ✅ 10 use cases implemented (4 more planned: RemoveDownload, PauseDownload, ResumeDownload, RefreshDownloads)
- ✅ Repository interfaces defined
- ✅ External service interfaces defined
- ✅ DTOs implemented
- ⏳ Interface adapters (to be implemented)
- ⏳ Infrastructure layer (minimal - only documentation server)
- ⏳ CLI commands (to be implemented)