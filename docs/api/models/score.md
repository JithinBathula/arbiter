# Score

Individual evaluation score for a specific metric.

## Fields

- `name` (str): Name of the metric (e.g., "semantic_similarity")
- `value` (float): Score value between 0.0 and 1.0
- `confidence` (Optional[float]): Confidence in this score (0.0-1.0)
- `explanation` (Optional[str]): Human-readable explanation
- `metadata` (Dict[str, Any]): Additional metadata about the score

## Example

```python
score = Score(
    name="semantic_similarity",
    value=0.92,
    confidence=0.95,
    explanation="High semantic overlap between output and reference",
    metadata={"key_similarities": ["Both mention Paris", "Both mention capital"]}
)

print(f"{score.name}: {score.value:.2f}")
print(f"Confidence: {score.confidence:.2f}")
print(f"Explanation: {score.explanation}")
```

## Validation

- `value` must be between 0.0 and 1.0
- `confidence` must be between 0.0 and 1.0 (if provided)

