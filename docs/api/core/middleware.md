# Middleware

Composable middleware pipeline for cross-cutting concerns like logging, metrics, caching, and rate limiting.

## Overview

Middleware allows you to add functionality to evaluations without modifying core code. Middleware runs before and after the evaluation, enabling logging, metrics collection, caching, and more.

## Built-in Middleware

### LoggingMiddleware

Logs evaluation requests and results.

```python
from arbiter.core.middleware import LoggingMiddleware, MiddlewarePipeline

pipeline = MiddlewarePipeline([
    LoggingMiddleware(log_level="INFO")
])

result = await evaluate(
    output="test",
    evaluators=["semantic"],
    middleware=pipeline
)
```

### MetricsMiddleware

Collects performance metrics.

```python
from arbiter.core.middleware import MetricsMiddleware

pipeline = MiddlewarePipeline([
    MetricsMiddleware()
])

result = await evaluate(
    output="test",
    evaluators=["semantic"],
    middleware=pipeline
)
```

### CachingMiddleware

Caches evaluation results to avoid redundant LLM calls.

```python
from arbiter.core.middleware import CachingMiddleware

pipeline = MiddlewarePipeline([
    CachingMiddleware(ttl=3600)  # Cache for 1 hour
])

result = await evaluate(
    output="test",
    evaluators=["semantic"],
    middleware=pipeline
)
```

### RateLimitingMiddleware

Limits request rate to prevent API throttling.

```python
from arbiter.core.middleware import RateLimitingMiddleware

pipeline = MiddlewarePipeline([
    RateLimitingMiddleware(max_requests_per_second=10)
])

result = await evaluate(
    output="test",
    evaluators=["semantic"],
    middleware=pipeline
)
```

## Combining Middleware

```python
pipeline = MiddlewarePipeline([
    LoggingMiddleware(log_level="DEBUG"),
    MetricsMiddleware(),
    CachingMiddleware(ttl=3600),
    RateLimitingMiddleware(max_requests_per_second=10)
])

result = await evaluate(
    output="test",
    evaluators=["semantic"],
    middleware=pipeline
)
```

## Custom Middleware

Create custom middleware by implementing the `Middleware` protocol:

```python
from arbiter.core.middleware import Middleware
from arbiter.core.models import EvaluationResult

class CustomMiddleware(Middleware):
    async def process(self, output, reference, next_handler, context):
        # Pre-processing
        start = time.time()

        # Call next in chain
        result = await next_handler(output, reference)

        # Post-processing
        elapsed = time.time() - start
        print(f"Evaluation took {elapsed:.2f}s")

        return result
```

## Example

See [Middleware Usage Example](../../examples/middleware_usage.md) for complete examples.

