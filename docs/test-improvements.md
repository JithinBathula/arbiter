# Test Infrastructure Improvements

This document explains the recent improvements to Arbiter's test infrastructure, focusing on code quality, maintainability, and developer experience.

## Overview

Recent refactoring eliminated **~158 lines of duplicate code** across the test suite while improving consistency and maintainability. The improvements follow pytest best practices and make it easier to maintain test utilities.

## Changes Summary

### Before: Duplicate Fixtures in Every Test File

Every test file had its own copy of common fixtures:

```python
# tests/unit/test_semantic.py
class MockAgentResult:
    """Mock PydanticAI agent result."""
    def __init__(self, output: object):
        self.output = output
    def usage(self):
        mock_usage = MagicMock()
        mock_usage.total_tokens = 100
        return mock_usage

@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = MagicMock(spec=LLMClient)
    client.model = "gpt-4o-mini"
    client.temperature = 0.0
    return client

@pytest.fixture
def mock_agent():
    """Create a mock PydanticAI agent."""
    agent = AsyncMock()
    return agent
```

This was duplicated in **6 test files**:
- test_api.py
- test_base.py
- test_custom_criteria.py
- test_error_handling.py
- test_pairwise.py
- test_semantic.py

### After: Centralized Fixtures in conftest.py

Now all shared fixtures live in one place:

```python
# tests/conftest.py
"""Shared test fixtures and utilities for Arbiter tests."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from arbiter.core.llm_client import LLMClient

class MockAgentResult:
    """Mock PydanticAI agent result for testing."""
    def __init__(self, output: object):
        self.output = output

    def usage(self):
        mock_usage = MagicMock()
        mock_usage.total_tokens = 100
        return mock_usage

@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = MagicMock(spec=LLMClient)
    client.model = "gpt-4o-mini"
    client.temperature = 0.0
    return client

@pytest.fixture
def mock_agent():
    """Create a mock PydanticAI agent."""
    agent = AsyncMock()
    return agent
```

Test files now just import and use:

```python
# tests/unit/test_semantic.py
from tests.conftest import MockAgentResult

# Fixtures automatically available (pytest discovers them)
def test_something(mock_llm_client, mock_agent):
    # Use fixtures
    pass
```

## Benefits

### 1. Single Source of Truth

Changes to test utilities now happen in one place:

**Before**: Update `MockAgentResult` in 6 files
**After**: Update `MockAgentResult` in 1 file

### 2. Reduced Code Duplication

- **test_api.py**: -27 lines
- **test_base.py**: -25 lines
- **test_custom_criteria.py**: -25 lines
- **test_error_handling.py**: -27 lines
- **test_pairwise.py**: -27 lines
- **test_semantic.py**: -27 lines
- **Total**: ~158 lines eliminated

### 3. Better Organization

Following pytest conventions makes the codebase more familiar to Python developers:

```
tests/
├── conftest.py          # Shared fixtures (pytest standard)
├── unit/
│   ├── test_api.py
│   ├── test_base.py
│   └── ...
└── integration/
    └── ...
```

### 4. Improved Maintainability

New developers don't need to hunt through test files to find fixture definitions.

### 5. Consistent Test Behavior

All tests use the same mock implementations, ensuring consistent behavior across the test suite.

## Shared Fixtures Reference

### MockAgentResult

Mocks the result object returned by PydanticAI agents.

```python
from tests.conftest import MockAgentResult

# Create mock result
response = CustomResponse(score=0.85, explanation="Good")
mock_result = MockAgentResult(response)

# Configure agent to return it
mock_agent.run = AsyncMock(return_value=mock_result)
```

**Properties**:
- `output`: The response object (e.g., SemanticResponse, CustomCriteriaResponse)
- `usage()`: Returns mock usage with `total_tokens = 100`

### mock_llm_client

Provides a standard mock LLM client for tests.

```python
def test_evaluator(mock_llm_client):
    """Test using the mock LLM client fixture."""
    evaluator = SemanticEvaluator(llm_client=mock_llm_client)

    # Client is already configured
    assert mock_llm_client.model == "gpt-4o-mini"
    assert mock_llm_client.temperature == 0.0
```

**Attributes**:
- `model = "gpt-4o-mini"`
- `temperature = 0.0`
- Spec'd as `LLMClient` for type safety

### mock_agent

Provides a standard mock PydanticAI agent.

```python
def test_evaluation(mock_llm_client, mock_agent):
    """Test using mock agent fixture."""
    # Configure agent response
    mock_response = SemanticResponse(score=0.9, explanation="Great")
    mock_result = MockAgentResult(mock_response)
    mock_agent.run = AsyncMock(return_value=mock_result)

    # Configure client to return agent
    mock_llm_client.create_agent = MagicMock(return_value=mock_agent)

    # Use in evaluator
    evaluator = SemanticEvaluator(llm_client=mock_llm_client)
    score = await evaluator.evaluate(output="test", reference="test")
```

## Writing New Tests

### Using Shared Fixtures

```python
# tests/unit/test_new_feature.py
"""Tests for new feature."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from tests.conftest import MockAgentResult  # Import shared class

# Fixtures are automatically available
def test_my_feature(mock_llm_client, mock_agent):
    """Test using shared fixtures."""
    # Use fixtures directly
    evaluator = MyEvaluator(llm_client=mock_llm_client)

    # Configure mock response
    response = MyResponse(score=0.8)
    mock_result = MockAgentResult(response)
    mock_agent.run = AsyncMock(return_value=mock_result)

    # Test...
```

### Adding File-Specific Fixtures

Keep file-specific fixtures in the test file:

```python
# tests/unit/test_semantic.py
from tests.conftest import MockAgentResult  # Shared

@pytest.fixture
def evaluator(mock_llm_client):  # File-specific fixture
    """Create a SemanticEvaluator instance."""
    return SemanticEvaluator(llm_client=mock_llm_client)

def test_something(evaluator):  # Use file-specific fixture
    """Test using evaluator fixture."""
    assert evaluator.name == "semantic_similarity"
```

### When to Add to conftest.py

Add fixtures to `conftest.py` when they're:
- Used in **3+ test files**
- **Generic** and not feature-specific
- **Stable** (unlikely to change frequently)

Keep in individual test files when they're:
- Used in **1-2 files only**
- **Feature-specific**
- **Likely to change** with feature evolution

## Test Execution

All tests continue to work exactly as before:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_semantic.py

# Run specific test
pytest tests/unit/test_semantic.py::TestSemanticEvaluator::test_name_property

# Run with coverage
pytest --cov=arbiter --cov-report=html
```

## Migration Guide

If you have existing test files to migrate:

### Step 1: Import Shared Classes

```python
# Add to imports
from tests.conftest import MockAgentResult
```

### Step 2: Remove Local Definitions

Delete the `MockAgentResult` class definition from your test file.

### Step 3: Remove Duplicate Fixtures

Delete local `mock_llm_client` and `mock_agent` fixture definitions.

### Step 4: Update Usage

No changes needed! Pytest automatically discovers fixtures from `conftest.py`.

### Example Migration

**Before**:
```python
# tests/unit/test_my_feature.py
from unittest.mock import AsyncMock, MagicMock

class MockAgentResult:  # Delete this
    def __init__(self, output: object):
        self.output = output
    def usage(self):
        mock_usage = MagicMock()
        mock_usage.total_tokens = 100
        return mock_usage

@pytest.fixture
def mock_llm_client():  # Delete this
    client = MagicMock(spec=LLMClient)
    client.model = "gpt-4o-mini"
    client.temperature = 0.0
    return client

@pytest.fixture
def mock_agent():  # Delete this
    agent = AsyncMock()
    return agent

def test_feature(mock_llm_client, mock_agent):
    # Test code...
```

**After**:
```python
# tests/unit/test_my_feature.py
from unittest.mock import AsyncMock, MagicMock
from tests.conftest import MockAgentResult  # Add this import

# All fixture definitions removed!

def test_feature(mock_llm_client, mock_agent):
    # Test code unchanged - fixtures auto-discovered
```

## Best Practices

### 1. Import Only What You Need

```python
# ✅ Good: Import only MockAgentResult (used explicitly)
from tests.conftest import MockAgentResult

# ❌ Avoid: Don't import fixtures (pytest discovers them)
from tests.conftest import mock_llm_client  # Not needed!
```

### 2. Document File-Specific Fixtures

```python
@pytest.fixture
def evaluator(mock_llm_client):
    """Create a SemanticEvaluator instance.

    This fixture is specific to test_semantic.py tests.
    """
    return SemanticEvaluator(llm_client=mock_llm_client)
```

### 3. Keep conftest.py Focused

Only add truly shared utilities to `conftest.py`. Don't let it become a dumping ground for all test code.

### 4. Use Meaningful Fixture Names

```python
# ✅ Good: Clear purpose
@pytest.fixture
def semantic_evaluator(mock_llm_client):
    return SemanticEvaluator(llm_client=mock_llm_client)

# ❌ Less clear: Generic name
@pytest.fixture
def eval(mock_llm_client):
    return SemanticEvaluator(llm_client=mock_llm_client)
```

## Impact on Test Coverage

The refactoring maintains **100% of existing test coverage** while improving code quality:

- **2,703 lines** of test code across 7 test files
- **>80% code coverage** maintained
- **All tests passing** after refactoring
- **Zero behavioral changes** to tests

## Future Improvements

Potential future enhancements to the test infrastructure:

1. **Shared test data**: Add common test inputs/outputs to conftest.py
2. **Test utilities**: Helper functions for common test patterns
3. **Parameterized fixtures**: Configurable fixtures for different test scenarios
4. **Integration test fixtures**: Shared fixtures for integration tests

## See Also

- [pytest conftest.py documentation](https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files)
- [Arbiter Contributing Guide](../CONTRIBUTING.md)
- [Running Tests](../README.md#development)
