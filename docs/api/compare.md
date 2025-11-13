# compare()

Pairwise comparison function for A/B testing and model comparison.

```python
from arbiter import compare

comparison = await compare(
    output_a="First LLM output",
    output_b="Second LLM output",
    criteria="accuracy, clarity, completeness"
)
```

## Parameters

- `output_a` (str): First output to compare
- `output_b` (str): Second output to compare
- `criteria` (Optional[str]): Evaluation criteria for comparison
- `reference` (Optional[str]): Reference text for context
- `llm_client` (Optional[LLMClient]): Pre-configured LLM client
- `model` (str): Model name (default: "gpt-4o")
- `provider` (Provider): Provider to use (default: Provider.OPENAI)
- `middleware` (Optional[MiddlewarePipeline]): Middleware pipeline

## Returns

[`ComparisonResult`](models/comparison_result.md) with winner, confidence, reasoning, and aspect scores.

## Example

```python
comparison = await compare(
    output_a="GPT-4 response: Paris is the capital of France",
    output_b="Claude response: The capital of France is Paris",
    criteria="accuracy, clarity",
    reference="What is the capital of France?"
)

print(f"Winner: {comparison.winner}")
print(f"Confidence: {comparison.confidence:.2f}")
print(f"Reasoning: {comparison.reasoning}")

# Check aspect scores
for aspect, scores in comparison.aspect_scores.items():
    print(f"{aspect}: A={scores['output_a']:.2f}, B={scores['output_b']:.2f}")
```

## Use Cases

- **A/B Testing**: Compare two different prompts or models
- **Model Comparison**: Evaluate which model performs better
- **Output Selection**: Choose the best output from multiple candidates

