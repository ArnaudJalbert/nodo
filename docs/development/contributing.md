# Contributing

Thank you for your interest in contributing to Nodo! This guide will help you get started.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment** - See [Development Setup](setup.md)
4. **Create a branch** for your changes

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### 1. Make Your Changes

- Follow the existing code style
- Write tests for new code
- Update documentation as needed
- Keep commits focused and atomic

### 2. Run Quality Checks

Before committing, ensure:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Run tests
uv run pytest --cov=src --cov-fail-under=100
```

### 3. Commit Your Changes

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for new aggregator
fix: resolve download status update issue
docs: update architecture documentation
test: add tests for download repository
refactor: simplify use case implementation
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

### Formatting

We use **ruff** for formatting. Code is automatically formatted to:

- Line length: 88 characters
- Use double quotes for strings
- Trailing commas in multi-line structures

### Linting

We use **ruff** for linting with these rules:

- `E501` - Line too long
- `ANN` - Type annotations
- `N` - Naming conventions (PEP 8)
- `R` - Refactoring suggestions
- `I` - Import sorting

### Type Hints

- Use type hints for all function parameters and return values
- Use `|` for union types (Python 3.10+)
- Use `None` explicitly for optional values

### Docstrings

Use Google-style docstrings:

```python
def add_download(magnet_link: MagnetLink, title: str) -> DownloadDTO:
    """Add a new download.
    
    Args:
        magnet_link: The magnet link of the torrent.
        title: The title of the download.
    
    Returns:
        The created download DTO.
    
    Raises:
        DuplicateDownloadError: If download already exists.
    """
    pass
```

## Architecture Guidelines

### Follow Clean Architecture

- **Domain layer**: No external dependencies
- **Application layer**: Depends only on Domain
- **Interface Adapters**: Implements Application interfaces
- **Infrastructure**: Depends on all layers

### Adding New Features

1. **Start with Domain** - Add entities, value objects, exceptions
2. **Define Interfaces** - Add ABCs in Application layer
3. **Implement Use Cases** - Add business logic in Application layer
4. **Implement Adapters** - Create concrete implementations
5. **Wire in Infrastructure** - Add CLI commands, DI setup

### Adding New Aggregators

1. Create aggregator adapter in `interface_adapters/services/aggregators/`
2. Implement `IAggregatorService` interface
3. Add tests
4. Register in DI container
5. Update documentation

## Testing Requirements

- **100% test coverage** - All new code must be tested
- **Test in isolation** - Use mocks for dependencies
- **Clear test names** - Describe what is being tested
- **Fast tests** - Unit tests should run quickly

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Document complex algorithms
- Include examples in docstrings when helpful

### User Documentation

- Update user guide for new features
- Add examples for new commands
- Update configuration documentation

### Architecture Documentation

- Update architecture docs for significant changes
- Document design decisions
- Keep diagrams up to date

## Pull Request Process

1. **Create a draft PR** if work is in progress
2. **Ensure all checks pass** - Tests, linting, coverage
3. **Request review** - Tag relevant maintainers
4. **Address feedback** - Make requested changes
5. **Mark ready for review** - When all feedback is addressed

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass
- [ ] Coverage is 100%
- [ ] No linting errors
- [ ] Commits follow conventional commits

## Reporting Issues

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python version, etc.)
- Error messages/logs

### Feature Requests

Include:
- Description of the feature
- Use case/justification
- Proposed implementation (if you have ideas)
- Alternatives considered

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues/PRs

Thank you for contributing to Nodo! 🎉

