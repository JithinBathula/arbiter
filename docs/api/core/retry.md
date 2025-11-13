# Retry Configuration

Configurable retry system for handling transient failures in LLM API calls.

## Overview

The retry system implements exponential backoff and selective retry based on error types. It only retries errors that are likely to be transient (API errors, timeouts, connection issues).

## Preset Configurations

### RETRY_QUICK

Fast retries for quick operations.

```python
from arbiter.core.retry import RETRY_QUICK, with_retry

@with_retry(RETRY_QUICK)
async def quick_operation():
    return await llm_client.generate(prompt)
```

### RETRY_STANDARD

Standard retry configuration (default).

```python
from arbiter.core.retry import RETRY_STANDARD, with_retry

@with_retry(RETRY_STANDARD)
async def standard_operation():
    return await llm_client.generate(prompt)
```

### RETRY_PERSISTENT

Patient retries for important operations.

```python
from arbiter.core.retry import RETRY_PERSISTENT, with_retry

@with_retry(RETRY_PERSISTENT)
async def important_operation():
    return await llm_client.generate(prompt)
```

## Custom Configuration

```python
from arbiter.core.retry import RetryConfig, with_retry

config = RetryConfig(
    max_attempts=5,
    delay=2.0,
    backoff=2.0
)

@with_retry(config)
async def custom_operation():
    return await llm_client.generate(prompt)
```

## RetryConfig Parameters

- `max_attempts` (int): Maximum number of retry attempts
- `delay` (float): Initial delay between retries (seconds)
- `backoff` (float): Multiplier for exponential backoff

## Error Handling

The retry system only retries:
- `ModelProviderError`: API errors from LLM providers
- `TimeoutError`: Request timeouts
- `ConnectionError`: Network connectivity issues

Other errors are raised immediately without retry.

