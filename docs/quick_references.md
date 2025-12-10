# Quick Reference Cheat Sheet

## Essential Commands

```bash
# Development workflow
ruff format . && ruff check --fix . && pytest --cov=src --cov-fail-under=100

# Individual commands
ruff format .                          # Format code
ruff check --fix .                     # Lint with auto-fix
pytest --cov=src --cov-fail-under=100  # Test with coverage
mkdocs serve                           # Serve docs locally
```

---

## Clean Architecture Layers (Quick)

```
Infrastructure (CLI, DI, Config)
    ↓ depends on
Interface Adapters (Repos, External Services)
    ↓ depends on
Application (Use Cases, Interfaces)
    ↓ depends on
Domain (Entities, Value Objects)
```

**Rule:** Inner layers never know about outer layers.

---

## Testing Quick Reference

```python
# Domain tests - No mocks
def test_entity() -> None:
    entity = Download(...)
    assert entity.status == DownloadStatus.DOWNLOADING

# Application tests - Mock interfaces with ABC
def test_use_case() -> None:
    mock_repo = Mock(spec=IDownloadRepository)
    use_case = AddDownloadUseCase(repository=mock_repo)
    # ...

# Adapter tests - Mock protocols
def test_adapter() -> None:
    mock_client = Mock(spec=QBittorrentClientProtocol)
    adapter = QBittorrentClient(client=mock_client)
    # ...
```

---

## Dependency Injection Pattern

```python
# 1. Define interface in domain
class ITorrentClient(ABC):
    @abstractmethod
    def add_torrent(self, magnet: MagnetLink) -> str: ...

# 2. Define protocol in interface_adapters
class QBittorrentClientProtocol(Protocol):
    def torrents_add(self, urls: str) -> str: ...

# 3. Implement adapter
class QBittorrentClient(ITorrentClient):
    def __init__(self, client: QBittorrentClientProtocol):
        self.client = client

# 4. Wire in infrastructure
def create_client() -> ITorrentClient:
    qbt = qbittorrentapi.Client(...)  # Concrete
    return QBittorrentClient(client=qbt)
```

---

## DTO Pattern

```python
# Use case with inner DTOs
class AddDownloadUseCase:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class InputData:
        magnet_link: str
        title: str
    
    @dataclass(frozen=True, kw_only=True, slots=True)
    class OutputData:
        download: DownloadDTO
    
    def execute(self, input_data: InputData) -> OutputData:
        # Business logic
        pass
```

---

## Common Patterns

### Value Object
```python
@dataclass(frozen=True)
class MagnetLink:
    uri: str
    
    @classmethod
    def from_string(cls, uri: str) -> "MagnetLink":
        # Validation
        return cls(uri=uri)
```

### Entity
```python
@dataclass
class Download:
    id: UUID
    magnet_link: MagnetLink
    status: DownloadStatus
    # ...
```

### Repository Interface
```python
class IDownloadRepository(ABC):
    @abstractmethod
    def save(self, download: Download) -> Download: ...
```

### Use Case
```python
class AddDownloadUseCase:
    def __init__(self, repository: IDownloadRepository):
        self.repository = repository
    
    def execute(self, input_data: InputData) -> OutputData:
        # Business logic
        pass
```

---

## File Locations

- **Domain interfaces:** `src/domain/repositories/`, `src/domain/services/`
- **Adapter protocols:** `src/interface_adapters/protocols/`
- **Use cases:** `src/application/use_cases/`
- **Repositories:** `src/interface_adapters/repositories/`
- **Controllers:** `src/infrastructure/controllers/`
- **CLI commands:** `src/infrastructure/cli/commands/`
- **DI container:** `src/infrastructure/di/container.py`
- **Tests:** `tests/unit/<layer>/test_<module>.py`

---

## Checklist Before Commit

- [ ] Code formatted (`ruff format .`)
- [ ] No lint errors (`ruff check .`)
- [ ] Tests pass (`pytest`)
- [ ] 100% coverage (`--cov-fail-under=100`)
- [ ] Type hints everywhere
- [ ] Docstrings (Google style)
- [ ] Tests written (plain functions)
- [ ] CHANGELOG.md updated
- [ ] Documentation updated if needed

---

## Common Mistakes to Avoid

❌ Domain importing from application
❌ Application importing concrete implementations
❌ Use cases instantiating dependencies
❌ Test classes instead of functions
❌ Forgetting to format with ruff
❌ Code without tests
❌ Missing type hints

---

## Quick Navigation

- **Architecture overview:** `docs/architecture/LAYERS.md`
- **Domain model:** `docs/architecture/DOMAIN.md`
- **All use cases:** `docs/architecture/USE_CASES.md`
- **DI patterns:** `docs/architecture/DEPENDENCY_INJECTION.md`
- **Testing guide:** `docs/development/TESTING.md`
- **Code quality:** `docs/development/CODE_QUALITY.md`

---

## Key Principles (Remember These)

1. **Dependency Rule** - Dependencies point inward only
2. **100% Coverage** - Every line tested, no exceptions
3. **Inject Everything** - Never instantiate dependencies
4. **Three Abstractions** - ABC → Protocol → Concrete
5. **Plain Functions** - Test with functions, not classes
6. **Format Always** - Ruff format before every commit

---

## Getting Unstuck

**Can't test something?**
→ You're probably violating dependency injection. Refactor to inject dependencies.

**Import error between layers?**
→ Check dependency rule. Outer depends on inner, not reverse.

**Confused about where code goes?**
→ Ask: "Is this business logic (domain), workflow (application), translation (adapter), or framework (infrastructure)?"

**Test failing mysteriously?**
→ Check if you're using `Mock(spec=Interface)` correctly. Verify the spec matches the actual interface.

**Ruff errors won't go away?**
→ Read the error message carefully. Most can be auto-fixed with `ruff check --fix .`
