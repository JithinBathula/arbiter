# Using Multiple Evaluators

Arbiter supports running multiple evaluators simultaneously to get comprehensive evaluation from different perspectives. This guide explains how to combine evaluators effectively and handle partial results.

## Quick Start

```python
from arbiter import evaluate

result = await evaluate(
    output="Paris is the capital of France",
    reference="The capital of France is Paris",
    criteria="Accuracy and clarity",
    evaluators=["semantic", "custom_criteria"],  # Multiple evaluators
    model="gpt-4o-mini"
)

print(f"Overall Score: {result.overall_score}")  # Average of successful evaluators
print(f"Individual Scores: {len(result.scores)}")  # 2 scores (one per evaluator)
print(f"Partial Result: {result.partial}")  # True if any evaluator failed
```

## Understanding Combined Scores

### Overall Score Calculation

The `overall_score` is the **average of successful evaluator scores only**:

```python
result = await evaluate(
    output="Medical advice about diabetes management",
    reference="Standard diabetes treatment guidelines",
    criteria="Medical accuracy, patient safety, appropriate tone",
    evaluators=["semantic", "custom_criteria"]
)

# If both succeed:
# - semantic_score = 0.85
# - custom_criteria_score = 0.75
# - overall_score = (0.85 + 0.75) / 2 = 0.80

# If custom_criteria fails:
# - semantic_score = 0.85
# - overall_score = 0.85 (NOT 0.425 = (0.85 + 0) / 2)
# - result.partial = True
# - result.errors = {"custom_criteria": "error message"}
```

### Accessing Individual Scores

```python
result = await evaluate(
    output="Product description",
    reference="Product specs",
    criteria="Accuracy, persuasiveness, brand voice",
    evaluators=["semantic", "custom_criteria"]
)

# Access scores by evaluator name
for score in result.scores:
    print(f"{score.name}: {score.value:.2f}")
    if score.confidence:
        print(f"  Confidence: {score.confidence:.2f}")
    print(f"  Explanation: {score.explanation}")

# Or get specific score
semantic_score = result.get_score("semantic_similarity")
if semantic_score:
    print(f"Semantic: {semantic_score.value:.2f}")
```

## Graceful Degradation

Arbiter handles evaluator failures gracefully, allowing you to use successful results even when some evaluators fail.

### Detecting Partial Results

```python
result = await evaluate(
    output="Test output",
    evaluators=["semantic", "custom_criteria", "factuality"]
)

if result.partial:
    print(f"⚠️ Partial result: {len(result.errors)} evaluators failed")
    print(f"✅ Successful: {len(result.scores)} evaluators")

    # Log errors for monitoring
    for evaluator, error_msg in result.errors.items():
        logger.warning(f"Evaluator '{evaluator}' failed: {error_msg}")

    # Still use the result if we have scores
    if result.scores:
        # Use overall_score from successful evaluators
        use_score = result.overall_score
else:
    print("✅ All evaluators succeeded")
```

### Error Information

The `errors` dictionary contains detailed information about failures:

```python
result = await evaluate(
    output="Test",
    evaluators=["semantic", "custom_criteria"]
)

if result.errors:
    for evaluator_name, error_message in result.errors.items():
        print(f"Failed: {evaluator_name}")
        print(f"Reason: {error_message}")

        # Check if it's an API timeout
        if "timeout" in error_message.lower():
            # Handle timeout specifically
            pass
        # Check if it's a rate limit
        elif "rate limit" in error_message.lower():
            # Implement backoff
            pass
```

### Metadata

The result metadata provides counts:

```python
print(f"Total evaluators requested: {result.metadata['evaluator_count']}")
print(f"Successful evaluators: {result.metadata['successful_evaluators']}")
print(f"Failed evaluators: {result.metadata['failed_evaluators']}")
```

## Best Practices

### 1. Choose Complementary Evaluators

Combine evaluators that measure different aspects:

```python
# ✅ Good: Different perspectives
evaluators = [
    "semantic",  # Measures similarity
    "custom_criteria"  # Measures domain-specific quality
]

# ❌ Less useful: Redundant evaluation
evaluators = [
    "semantic",
    "semantic"  # Same evaluator twice
]
```

### 2. Handle Partial Results

Always check for partial results in production:

```python
async def evaluate_with_fallback(output, reference):
    """Evaluate with fallback logic for partial failures."""
    result = await evaluate(
        output=output,
        reference=reference,
        evaluators=["semantic", "custom_criteria", "factuality"]
    )

    if result.partial:
        # Log for monitoring
        logger.warning(
            f"Partial evaluation: {len(result.errors)}/{len(result.evaluator_names)} failed",
            extra={"errors": result.errors}
        )

        # Check if we have minimum required evaluators
        if len(result.scores) < 2:
            raise ValueError("Insufficient successful evaluators")

    return result
```

### 3. Set Appropriate Thresholds

Consider partial results when setting pass/fail thresholds:

```python
result = await evaluate(
    output="Content for review",
    evaluators=["semantic", "custom_criteria"],
    threshold=0.7  # 70% threshold
)

if result.partial:
    # Maybe require higher score if some evaluators failed
    required_score = 0.8
else:
    required_score = 0.7

passed = result.overall_score >= required_score
```

### 4. Monitor Failure Patterns

Track which evaluators fail most often:

```python
from collections import Counter

failure_counts = Counter()

for evaluation in evaluations:
    result = await evaluate(
        output=evaluation.output,
        evaluators=["semantic", "custom_criteria", "factuality"]
    )

    if result.partial:
        for failed_evaluator in result.errors.keys():
            failure_counts[failed_evaluator] += 1

# Alert if one evaluator fails frequently
for evaluator, count in failure_counts.most_common():
    if count > 10:
        alert(f"Evaluator '{evaluator}' has failed {count} times")
```

## Decision Logic with Multiple Scores

Use multiple scores to make nuanced decisions:

```python
result = await evaluate(
    output="Medical advice response",
    reference="Medical guidelines",
    criteria="Medical accuracy, patient safety, clarity",
    evaluators=["semantic", "custom_criteria"]
)

# Get individual scores
semantic = result.get_score("semantic_similarity")
custom = result.get_score("custom_criteria")

# Decision matrix
if semantic and semantic.value >= 0.9 and custom and custom.value >= 0.8:
    decision = "EXCELLENT - Use as-is"
elif semantic and semantic.value >= 0.7 and custom and custom.value >= 0.7:
    decision = "GOOD - Minor review recommended"
elif semantic and semantic.value >= 0.5 or custom and custom.value >= 0.5:
    decision = "MODERATE - Requires review"
else:
    decision = "POOR - Needs rewrite"

print(f"Decision: {decision}")
```

## Error Handling Patterns

### Pattern 1: Fail Fast

Require all evaluators to succeed:

```python
from arbiter.core.exceptions import EvaluatorError

try:
    result = await evaluate(
        output="Critical content",
        evaluators=["semantic", "custom_criteria"]
    )

    if result.partial:
        raise ValueError(f"Partial result not acceptable: {result.errors}")

except EvaluatorError as e:
    # All evaluators failed
    logger.error(f"Complete evaluation failure: {e}")
    raise
```

### Pattern 2: Best Effort

Use whatever scores are available:

```python
result = await evaluate(
    output="Content",
    evaluators=["semantic", "custom_criteria", "factuality"]
)

# Use whatever succeeded
if result.scores:
    # At least one evaluator succeeded
    score = result.overall_score
    confidence_level = "partial" if result.partial else "full"

    return {
        "score": score,
        "confidence": confidence_level,
        "evaluators_used": result.evaluator_names
    }
else:
    # This shouldn't happen (would raise EvaluatorError)
    # but handle defensively
    return None
```

### Pattern 3: Required Minimum

Require a minimum number of successful evaluators:

```python
MIN_REQUIRED_EVALUATORS = 2

result = await evaluate(
    output="Content",
    evaluators=["semantic", "custom_criteria", "factuality"]
)

if len(result.scores) < MIN_REQUIRED_EVALUATORS:
    raise ValueError(
        f"Only {len(result.scores)} evaluators succeeded, "
        f"need at least {MIN_REQUIRED_EVALUATORS}"
    )

# Proceed with evaluation
score = result.overall_score
```

## Combining with Middleware

Use middleware to add cross-cutting concerns when using multiple evaluators:

```python
from arbiter import MiddlewarePipeline
from arbiter.core.middleware import LoggingMiddleware, MetricsMiddleware

pipeline = MiddlewarePipeline([
    LoggingMiddleware(log_level="INFO"),
    MetricsMiddleware()
])

result = await evaluate(
    output="Test output",
    reference="Test reference",
    evaluators=["semantic", "custom_criteria"],
    middleware=pipeline
)

# Check metrics for per-evaluator performance
metrics_mw = pipeline.get_middleware(MetricsMiddleware)
if metrics_mw:
    metrics = metrics_mw.get_metrics()
    print(f"Total time: {metrics['total_time']:.2f}s")
    print(f"Avg per evaluator: {metrics['avg_processing_time']:.2f}s")
```

## Cost and Performance Considerations

Multiple evaluators = multiple LLM calls:

```python
result = await evaluate(
    output="Test",
    evaluators=["semantic", "custom_criteria"]  # 2 LLM calls
)

# Track costs
total_tokens = result.total_tokens
total_cost = result.total_llm_cost(cost_per_1k_tokens=0.03)

print(f"Tokens: {total_tokens}")
print(f"Cost: ${total_cost:.4f}")

# Check per-evaluator metrics
for metric in result.metrics:
    print(f"{metric.evaluator}: {metric.tokens_used} tokens, {metric.processing_time:.2f}s")
```

### Optimization Tips

1. **Use caching** for repeated evaluations:
```python
from arbiter.core.middleware import CachingMiddleware

pipeline = MiddlewarePipeline([CachingMiddleware(max_size=100)])

# First call: hits all evaluators
result1 = await evaluate(output="test", evaluators=["semantic", "custom_criteria"], middleware=pipeline)

# Second call: instant from cache
result2 = await evaluate(output="test", evaluators=["semantic", "custom_criteria"], middleware=pipeline)
```

2. **Choose evaluators strategically**: Don't run more evaluators than needed
3. **Use cheaper models** when appropriate: `model="gpt-4o-mini"` vs `model="gpt-4o"`

## See Also

- [Error Handling Example](../examples/error_handling_example.py)
- [Multiple Evaluators Example](../examples/multiple_evaluators.py)
- [Evaluator Registry](./evaluator-registry.md)
- [Middleware Guide](./middleware.md)
