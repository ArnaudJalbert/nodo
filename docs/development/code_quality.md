# Code Quality Standards

## Ruff: Formatting & Linting

**All code must be formatted with Ruff and pass all lint checks.**

### Installation

```bash
uv add --dev ruff
```

### Commands

```bash
# Format code (automatic)
ruff format .

# Check linting
ruff check .

# Auto-fix linting issues
ruff check --fix .
```

### Pre-Commit Workflow

**Before every commit:**

```bash
ruff format .
ruff check --fix .
pytest --cov=src --cov-fail-under=100
```

### Configuration

**Location:** `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Rules

❌ **No code committed without `ruff format`**
❌ **No code with `ruff check` errors**
✅ **All code must pass both checks**
✅ **Configure ruff in `pyproject.toml`**

---

## Type Hints

**Type hints are required everywhere.**

### Rules

✅ **All function signatures must have type hints:**
```python
def search_torrents(
    query: str,
    max_results: int = 10
) -> list[TorrentSearchResult]:
    ...
```

✅ **All class attributes must have type hints:**
```python
@dataclass
class Download:
    id: UUID
    title: str
    status: DownloadStatus
```

✅ **Use modern type syntax (Python 3.11+):**
```python
# ✅ Good - Modern syntax
def get_download(id: str) -> Download | None:
    ...

list[str]
dict[str, int]

# ❌ Old - Don't use
from typing import Optional, List, Dict

def get_download(id: str) -> Optional[Download]:
    ...

List[str]
Dict[str, int]
```

✅ **Use Protocol for structural typing:**
```python
from typing import Protocol

class QBittorrentClientProtocol(Protocol):
    def torrents_add(self, urls: str, save_path: str) -> str: ...
```

✅ **Use ABC for interface definitions:**
```python
from abc import ABC, abstractmethod

class IDownloadRepository(ABC):
    @abstractmethod
    def save(self, download: Download) -> Download:
        pass
```

### Type Checking (Optional but Recommended)

```bash
# Install mypy
uv add --dev mypy

# Run type checking
mypy src/

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
```

---

## Docstrings

**Google style docstrings required for all public functions.**

### Function Docstring

```python
def search_torrents(query: str, max_results: int = 10) -> list[TorrentSearchResult]:
    """
    Search for torrents across multiple aggregators.
    
    Args:
        query: Search terms to find torrents
        max_results: Maximum number of results per aggregator
        
    Returns:
        List of search results sorted by seeders
        
    Raises:
        ValidationError: If query is empty or invalid
        AggregatorError: If all aggregators fail
        
    Example:
        >>> results = search_torrents("ubuntu", max_results=20)
        >>> print(len(results))
        20
    """
    ...
```

### Class Docstring

```python
class Download:
    """
    Represents a torrent download.
    
    A download tracks the state of a torrent from addition through
    completion, including file location and metadata.
    
    Attributes:
        id: Unique identifier
        magnet_link: Torrent magnet link
        title: Download name
        status: Current download status
    """
    ...
```

### Module Docstring

```python
"""
Download repository implementation using SQLite.

This module provides the SQLAlchemy-based repository for persisting
Download entities to a SQLite database.
"""
```

---

## Code Organization

### Import Order

Ruff automatically sorts imports (isort). Standard order:

```python
# 1. Standard library
import os
from pathlib import Path
from typing import Protocol

# 2. Third-party
import sqlalchemy
from pydantic import BaseModel

# 3. Local application
from src.domain.entities.download import Download
from src.application.use_cases.add_download import AddDownloadUseCase
```

### Line Length

**Maximum 100 characters per line.**

Ruff will automatically format long lines.

### Naming Conventions

```python
# Classes: PascalCase
class DownloadRepository:
    ...

# Functions/Variables: snake_case
def get_download_status():
    ...

download_id = "abc123"

# Constants: UPPER_SNAKE_CASE
MAX_CONCURRENT_DOWNLOADS = 10

# Private: _leading_underscore
def _internal_helper():
    ...

# Protocols/Interfaces: Descriptive names
class QBittorrentClientProtocol(Protocol):
    ...

class IDownloadRepository(ABC):
    ...
```

---

## Code Smells to Avoid

❌ **Long functions** - Break into smaller functions
❌ **Deep nesting** - Extract to helper functions
❌ **Magic numbers** - Use named constants
❌ **Commented-out code** - Delete it (use git history)
❌ **God classes** - Follow Single Responsibility Principle
❌ **Circular dependencies** - Restructure with interfaces

---

## Best Practices

### Use Dataclasses

```python
from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True, slots=True)
class DownloadDTO:
    id: str
    title: str
    status: str
```

### Use Enums

```python
from enum import Enum

class DownloadStatus(Enum):
    DOWNLOADING = "DOWNLOADING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"
```

### Use Context Managers

```python
# ✅ Good
with open(file_path, "r") as f:
    content = f.read()

# ❌ Bad
f = open(file_path, "r")
content = f.read()
f.close()
```

### Use Comprehensions

```python
# ✅ Good
titles = [download.title for download in downloads]

# ❌ Bad
titles = []
for download in downloads:
    titles.append(download.title)
```

### Early Returns

```python
# ✅ Good
def validate_download(download: Download) -> bool:
    if not download.magnet_link:
        return False
    
    if not download.title:
        return False
    
    return True

# ❌ Bad - deep nesting
def validate_download(download: Download) -> bool:
    if download.magnet_link:
        if download.title:
            return True
    return False
```

---

## Pre-Commit Hooks (Optional)

Install pre-commit to automatically run checks:

```bash
uv add --dev pre-commit

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

---

## Summary

**Every commit must:**

1. ✅ Be formatted with `ruff format .`
2. ✅ Pass `ruff check .` with no errors
3. ✅ Have type hints everywhere
4. ✅ Have Google-style docstrings
5. ✅ Have 100% test coverage
6. ✅ Follow naming conventions

**Quick check before commit:**

```bash
ruff format . && ruff check --fix . && pytest --cov=src --cov-fail-under=100
```

**No exceptions. High quality code is not optional.**
