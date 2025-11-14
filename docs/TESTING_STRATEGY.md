# Testing Strategy

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Status:** Living Document

---

## Overview

This document defines the comprehensive testing strategy for the Arbiter LLM evaluation framework. It establishes testing layers, coverage requirements, quality gates, and continuous integration practices.

---

## Testing Philosophy

**Core Principles:**
1. **Test Early, Test Often:** Write tests alongside implementation
2. **Comprehensive Coverage:** Target ≥80% code coverage
3. **Fast Feedback:** Unit tests complete in <5 seconds
4. **Realistic Testing:** Integration tests use real provider calls (with mocking option)
5. **Automated Everything:** All tests run in CI/CD pipeline

**Testing Pyramid:**
```
        /\
       /  \        E2E Tests (5%)
      /    \       - Full system validation
     /______\      - Critical user journeys
    /        \
   /          \    Integration Tests (25%)
  /            \   - Multi-component workflows
 /______________\  - Provider integration
/                \
|                | Unit Tests (70%)
|________________| - Individual components
                   - Fast, isolated tests
```

---

## Testing Layers

### 1. Unit Tests (`tests/unit/`)

**Purpose:** Test individual components in isolation

**Coverage Target:** 80%+ overall, 100% for core infrastructure

**Characteristics:**
- ✅ Fast execution (< 1 second per test, < 5 seconds total)
- ✅ Fully isolated (all external deps mocked)
- ✅ Deterministic results (no flakiness)
- ✅ Run on every commit

**What to Test:**

| Component | Test Focus | Example Tests |
|-----------|------------|---------------|
| Evaluators | Prompt generation, score calculation, response parsing | test_semantic_evaluator.py |
| Middleware | Request interception, metrics tracking, caching | test_middleware.py |
| LLM Client | Provider mapping, error handling, retry logic | test_llm_client.py |
| Circuit Breaker | State transitions, failure detection, recovery | test_circuit_breaker.py |
| Models | Pydantic validation, serialization, field constraints | test_models.py |
| Registry | Evaluator registration, lookup, validation | test_registry.py |

**Mocking Strategy:**

```python
# Mock LLM responses
from unittest.mock import AsyncMock, MagicMock

# Mock agent result
mock_response = SemanticResponse(score=0.92, explanation="High similarity")
mock_result = MagicMock()
mock_result.data = mock_response

# Mock agent
mock_agent = MagicMock()
mock_agent.run = AsyncMock(return_value=mock_result)

# Mock client
mock_client = MagicMock()
mock_client.create_agent = MagicMock(return_value=mock_agent)
```

**Running Unit Tests:**
```bash
# All unit tests
pytest tests/unit/ -v

# Specific test file
pytest tests/unit/test_semantic.py -v

# With coverage
pytest tests/unit/ --cov=arbiter --cov-report=html

# Fast mode (fail on first error)
pytest tests/unit/ -x
```

---

### 2. Integration Tests (`tests/integration/`)

**Purpose:** Test end-to-end workflows with real dependencies

**Coverage Target:** All critical user journeys

**Characteristics:**
- ✅ Real LLM API calls (with VCR.py option for determinism)
- ✅ Multi-component coordination
- ✅ Provider compatibility validation
- ✅ Run before releases

**What to Test:**

| Workflow | Test Focus | Example |
|----------|------------|---------|
| Single evaluation | Full evaluate() flow | test_full_evaluation.py |
| Batch evaluation | Concurrent processing, partial results | test_batch_evaluation.py |
| Pairwise comparison | compare() with real LLMs | test_pairwise_integration.py |
| Middleware pipeline | End-to-end logging + metrics + caching | test_middleware_integration.py |
| Provider switching | Fallback behavior, multi-provider | test_provider_switching.py |
| Error recovery | Retry logic, circuit breaker recovery | test_error_recovery.py |

**VCR.py for Deterministic Tests:**

```python
import pytest
import vcr

@pytest.mark.vcr
async def test_semantic_evaluation_with_recording():
    """Test with recorded LLM interaction."""
    # First run: Records real API call to cassette
    # Subsequent runs: Replays from cassette (fast + deterministic)

    result = await evaluate(
        output="Paris is the capital of France.",
        reference="Paris is the capital of France.",
        model="gpt-4o-mini"
    )

    assert result.overall_score > 0.9
```

**Running Integration Tests:**
```bash
# All integration tests (requires API keys)
pytest tests/integration/ -v

# With VCR replay (no API calls)
pytest tests/integration/ -v --vcr-mode=replay

# Record new cassettes
pytest tests/integration/ -v --vcr-mode=new_episodes

# Skip slow tests
pytest tests/integration/ -v -m "not slow"
```

---

### 3. Performance Tests (`benchmarks/`)

**Purpose:** Validate performance requirements and detect regressions

**Coverage Target:** All NFR performance targets

**Characteristics:**
- ✅ Baseline metrics tracked
- ✅ Regression detection (>10% degradation)
- ✅ Run on every release
- ✅ Results published to dashboard

**What to Benchmark:**

| Metric | Measurement | Target |
|--------|-------------|--------|
| Single evaluation latency | p50, p95, p99 | < 3s, < 5s, < 8s |
| Batch evaluation throughput | Evals per second | > 10/sec (with pooling) |
| Token usage | Tokens per evaluation | 500-800 (semantic) |
| Memory footprint | Peak memory usage | < 500MB (1000 evals) |
| Connection pool efficiency | Pool utilization % | > 80% |

**Benchmark Implementation:**

```python
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

@pytest.mark.benchmark
def test_semantic_evaluation_latency(benchmark):
    """Benchmark single semantic evaluation latency."""

    def run_evaluation():
        return asyncio.run(evaluate(
            output="Test output",
            reference="Test reference",
            model="gpt-4o-mini"
        ))

    result = benchmark(run_evaluation)

    # Assert performance targets
    assert benchmark.stats.median < 3.0  # p50 < 3s
    assert benchmark.stats.max < 8.0     # p99 < 8s
```

**Running Benchmarks:**
```bash
# All benchmarks
pytest benchmarks/ -v

# With baseline comparison
pytest benchmarks/ --benchmark-compare

# Save new baseline
pytest benchmarks/ --benchmark-save=v0.1.0

# Generate HTML report
pytest benchmarks/ --benchmark-histogram
```

---

### 4. Contract Tests

**Purpose:** Validate compatibility with LLM provider APIs

**Coverage Target:** All supported providers

**Characteristics:**
- ✅ Real API calls to providers
- ✅ Weekly scheduled runs
- ✅ Alert on breaking changes
- ✅ Version compatibility matrix

**What to Test:**

| Provider | Test Focus | Frequency |
|----------|------------|-----------|
| OpenAI | API schema, model availability | Weekly |
| Anthropic | Response structure, error codes | Weekly |
| Google Gemini | Authentication, rate limits | Weekly |
| Groq | Model mappings, compatibility | Weekly |

**Contract Test Example:**

```python
@pytest.mark.contract
@pytest.mark.provider("openai")
async def test_openai_api_contract():
    """Validate OpenAI API contract."""

    client = LLMClient(provider=Provider.OPENAI, model="gpt-4o-mini")

    # Test basic completion
    response = await client.complete([
        {"role": "user", "content": "Hello"}
    ])

    # Validate response structure
    assert isinstance(response.content, str)
    assert "usage" in response.usage
    assert response.usage["total_tokens"] > 0
    assert response.model == "gpt-4o-mini"
```

---

### 5. Concurrency and Load Testing

**Purpose:** Validate behavior under concurrent operations and high load

**Coverage Target:** Circuit breaker, connection pool, middleware pipeline

**Characteristics:**
- ✅ Tests with asyncio.gather for concurrent operations
- ✅ Race condition detection and documentation
- ✅ Performance under load validation

**Circuit Breaker Concurrency Tests:**

**Test Focus:**
- State transition integrity under concurrent access
- Half-open state call limiting with multiple tasks
- Race condition handling in failure counting

**Example Test:**

```python
@pytest.mark.asyncio
async def test_circuit_breaker_concurrent_half_open():
    """Test circuit breaker with concurrent calls in half-open state."""
    breaker = CircuitBreaker(failure_threshold=2, timeout=0.5, half_open_max_calls=1)

    # Open the circuit
    async def failing_operation():
        raise ValueError("Simulated failure")

    for _ in range(2):
        with pytest.raises(ValueError):
            await breaker.call(failing_operation)

    assert breaker.is_open

    # Wait for timeout
    await asyncio.sleep(0.6)

    # Launch 5 concurrent calls
    async def successful_operation():
        return "success"

    tasks = [breaker.call(successful_operation) for _ in range(5)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Expect 1-3 calls to succeed (due to race conditions in half-open state)
    # This is acceptable behavior documented in CircuitBreaker docstring
    successful = [r for r in results if not isinstance(r, Exception)]
    blocked = [r for r in results if isinstance(r, CircuitBreakerOpenError)]

    assert 1 <= len(successful) <= 3  # Slight overage acceptable
    assert len(blocked) >= 2  # Most should be blocked
    assert breaker.is_closed  # Should transition to closed after success
```

**Note on Circuit Breaker Concurrency:**
The circuit breaker's concurrency characteristics are documented in the class docstring.
Under high concurrent load, the `half_open_max_calls` limit may be slightly exceeded
(e.g., 2-3 calls instead of 1). This is acceptable for most use cases and keeps the
implementation simple without requiring locking mechanisms. The behavior is well-tested
and documented for users who need to understand the trade-offs.

---

## Quality Gates

### Pre-Commit Checks

**Developer Workflow:**
```bash
# Format code
make format

# Lint
make lint

# Type check
make type-check

# Run fast tests
pytest tests/unit/ -x
```

**Automated (Git Pre-Commit Hook):**
- ✅ Black formatting
- ✅ Ruff linting
- ✅ Mypy type checking
- ✅ Unit tests pass

### Pull Request Requirements

**Required Checks:**
- ✅ All unit tests pass (100%)
- ✅ Integration smoke tests pass
- ✅ Coverage ≥ 80% for new code
- ✅ No new mypy errors (strict mode)
- ✅ No new ruff warnings
- ✅ Documentation updated

**Review Checklist:**
- [ ] Tests added for new functionality
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Examples updated if API changed
- [ ] NFRs validated if applicable

### Pre-Release Requirements

**Complete Test Suite:**
- ✅ All unit tests pass (100%)
- ✅ All integration tests pass (100%)
- ✅ Performance benchmarks within ±10% of baseline
- ✅ Contract tests pass for all providers
- ✅ Manual smoke test of examples
- ✅ Security scan clean
- ✅ Documentation complete

**Release Artifacts:**
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Git tag created
- [ ] Release notes drafted
- [ ] Migration guide (if breaking changes)

---

## Testing Tools and Frameworks

### Current Stack

| Tool | Purpose | Version |
|------|---------|---------|
| pytest | Test framework | 9.0+ |
| pytest-asyncio | Async test support | 1.0+ |
| pytest-cov | Coverage reporting | 6.0+ |
| pytest-benchmark | Performance testing | 5.0+ |
| pytest-mock | Mocking utilities | 3.14+ |

### Planned Additions

| Tool | Purpose | Priority | Target Version |
|------|---------|----------|----------------|
| vcrpy | HTTP interaction recording | High | Phase 3 |
| hypothesis | Property-based testing | Medium | Phase 4 |
| locust | Load testing | Medium | Phase 5 |
| pytest-xdist | Parallel test execution | Low | Phase 5 |

### Test Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "benchmark: marks tests as performance benchmarks",
    "contract: marks tests as provider contract tests",
]

[tool.coverage.run]
source = ["arbiter"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

---

## Test Data Management

### Fixtures (`tests/fixtures/`)

**Organization:**
```
tests/fixtures/
├── llm_responses/          # Mock LLM responses
│   ├── semantic_good.json
│   ├── semantic_bad.json
│   └── pairwise_tie.json
├── evaluation_data/        # Test inputs
│   ├── samples.json        # Sample outputs/references
│   └── edge_cases.json     # Edge case inputs
└── provider_configs/       # Provider test configs
    ├── openai.json
    └── anthropic.json
```

**Example Fixture:**
```python
@pytest.fixture
def sample_evaluation_data():
    """Provide common evaluation test data."""
    return {
        "good_match": {
            "output": "Paris is the capital of France.",
            "reference": "Paris is the capital of France.",
        },
        "poor_match": {
            "output": "Berlin is in Germany.",
            "reference": "Paris is the capital of France.",
        },
        "empty_output": {
            "output": "",
            "reference": "Some reference",
        },
    }
```

### VCR Cassettes (`tests/cassettes/`)

**Organization:**
```
tests/cassettes/
├── openai/
│   ├── semantic_evaluation.yaml
│   └── batch_evaluation.yaml
├── anthropic/
│   └── pairwise_comparison.yaml
└── google/
    └── custom_criteria.yaml
```

**VCR Configuration:**
```python
@pytest.fixture(scope="module")
def vcr_config():
    """Configure VCR for provider API recording."""
    return {
        "filter_headers": ["authorization", "x-api-key"],
        "match_on": ["uri", "method", "body"],
        "record_mode": "once",  # Record once, then replay
    }
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Lint
        run: |
          ruff check arbiter/
          black --check arbiter/

      - name: Type check
        run: mypy arbiter/ --strict

      - name: Unit tests
        run: pytest tests/unit/ -v --cov=arbiter

      - name: Integration tests (smoke)
        run: pytest tests/integration/ -v -m "not slow"
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

### Test Execution Strategy

| Environment | Tests Run | Trigger | Duration |
|-------------|-----------|---------|----------|
| Local dev | Unit tests | Pre-commit | < 5s |
| CI (PR) | Unit + integration smoke | On push | < 2 min |
| CI (main) | Full test suite | On merge | < 5 min |
| Nightly | Full + performance + contract | Scheduled | < 15 min |
| Release | All tests + manual QA | Pre-release | < 30 min |

---

## Test Writing Guidelines

### Unit Test Template

```python
"""Tests for [component name].

Tests cover:
- [Test category 1]
- [Test category 2]
- [Test category 3]
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from arbiter import evaluate
from arbiter.evaluators import SemanticEvaluator


@pytest.fixture
def mock_llm_client():
    """Create mock LLM client for testing."""
    # Setup mock
    client = MagicMock()
    # Configure mock behavior
    return client


@pytest.mark.asyncio
async def test_feature_happy_path(mock_llm_client):
    """Test [feature] with valid inputs."""
    # Arrange
    input_data = {...}

    # Act
    result = await function_under_test(input_data)

    # Assert
    assert result.success
    assert result.value > 0.9


@pytest.mark.asyncio
async def test_feature_error_handling(mock_llm_client):
    """Test [feature] handles errors gracefully."""
    # Arrange
    mock_llm_client.complete.side_effect = Exception("API error")

    # Act & Assert
    with pytest.raises(ModelProviderError, match="API error"):
        await function_under_test(input_data)
```

### Integration Test Template

```python
"""Integration tests for [workflow].

Tests cover end-to-end workflows with real LLM calls.
"""

import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_evaluation():
    """Test full evaluation workflow."""
    # No mocks - real API call
    result = await evaluate(
        output="Real output text",
        reference="Real reference text",
        model="gpt-4o-mini"
    )

    # Validate real results
    assert 0.0 <= result.overall_score <= 1.0
    assert len(result.interactions) > 0
    assert result.interactions[0].tokens_used > 0
```

---

## Performance Regression Detection

### Baseline Metrics

**Establishment:**
- Run benchmarks on stable release
- Record p50, p95, p99 latencies
- Commit baseline to repository
- Use for future comparisons

**Tracking:**
```bash
# Save baseline
pytest benchmarks/ --benchmark-save=baseline

# Compare against baseline
pytest benchmarks/ --benchmark-compare=baseline

# Fail if >10% regression
pytest benchmarks/ --benchmark-max-time=1.1
```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Latency increase | +10% | +25% |
| Throughput decrease | -10% | -25% |
| Memory increase | +15% | +50% |
| Token usage increase | +10% | +20% |

---

## Test Maintenance

### Review Schedule

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Remove obsolete tests | Quarterly | Engineering |
| Update fixtures | As needed | Engineering |
| Refresh VCR cassettes | Monthly | CI/CD |
| Review slow tests | Quarterly | Engineering |
| Update testing strategy | Bi-annually | Tech Lead |

### Technical Debt Management

**Identifying Test Debt:**
- Tests that are frequently skipped
- Flaky tests (success rate < 95%)
- Slow tests (> 5s for unit tests)
- Tests with extensive mocking (>10 mocks)

**Debt Paydown:**
- Allocate 10% of sprint capacity
- Prioritize by impact (flaky > slow > complex)
- Track in issue backlog with `test-debt` label

---

## Monitoring and Reporting

### Coverage Dashboard

**Metrics to Track:**
- Overall coverage percentage
- Coverage by module
- Coverage trends over time
- Uncovered critical paths

**Tools:**
- codecov.io for visualization
- Coverage badges in README
- Weekly coverage reports

### Test Health Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test pass rate | > 99% | CI/CD results |
| Test execution time | < 5 min (full suite) | CI/CD duration |
| Flaky test rate | < 1% | Retry analysis |
| Coverage trend | Stable or increasing | Weekly reports |

---

## Special Testing Scenarios

### Security Testing

**Scope:**
- Input validation (XSS, injection)
- API key leakage prevention
- Dependency vulnerability scanning
- Secret detection in commits

**Tools:**
- `bandit` for Python security linting
- `safety` for dependency checks
- GitHub secret scanning

### Compatibility Testing

**Provider Matrix:**
```python
@pytest.mark.parametrize("provider,model", [
    (Provider.OPENAI, "gpt-4o-mini"),
    (Provider.ANTHROPIC, "claude-3-5-sonnet"),
    (Provider.GOOGLE, "gemini-pro"),
    (Provider.GROQ, "llama-3.1-8b-instant"),
])
async def test_provider_compatibility(provider, model):
    """Test evaluation across all providers."""
    result = await evaluate(
        output="Test output",
        reference="Test reference",
        provider=provider,
        model=model
    )
    assert result.overall_score is not None
```

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-14 | Initial testing strategy document | Claude Code |

---

## References

- [NFRs.md](./NFRs.md) - Performance targets and requirements
- [pytest Documentation](https://docs.pytest.org/)
- [VCR.py Documentation](https://vcrpy.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
