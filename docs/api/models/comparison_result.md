# ComparisonResult

Complete result of a pairwise comparison operation.

## Fields

### Input Data
- `output_a` (str): First output compared
- `output_b` (str): Second output compared
- `criteria` (Optional[str]): Evaluation criteria used
- `reference` (Optional[str]): Reference text for context

### Results
- `winner` (Literal["output_a", "output_b", "tie"]): Which output won
- `confidence` (float): Confidence in the comparison (0.0-1.0)
- `reasoning` (str): Detailed reasoning for the decision
- `aspect_scores` (Dict[str, Dict[str, float]]): Scores by aspect

### Metadata
- `total_tokens` (int): Total tokens used
- `processing_time` (float): Total processing time in seconds
- `timestamp` (datetime): When comparison completed
- `interactions` (List[LLMInteraction]): All LLM API calls made
- `metadata` (Dict[str, Any]): Additional metadata

## Methods

### `get_aspect_score(aspect: str, output: Literal["output_a", "output_b"]) -> Optional[float]`

Get score for a specific aspect and output.

```python
accuracy_a = comparison.get_aspect_score("accuracy", "output_a")
if accuracy_a:
    print(f"Output A accuracy: {accuracy_a:.2f}")
```

### `total_llm_cost(cost_per_1k_tokens: float = 0.01) -> float`

Estimate total LLM cost based on token usage.

```python
cost = comparison.total_llm_cost(cost_per_1k_tokens=0.03)
```

## Example

```python
comparison = await compare(
    output_a="GPT-4 response",
    output_b="Claude response",
    criteria="accuracy, clarity"
)

print(f"Winner: {comparison.winner}")
print(f"Confidence: {comparison.confidence:.2f}")
print(f"Reasoning: {comparison.reasoning}")

# Check aspect scores
for aspect, scores in comparison.aspect_scores.items():
    print(f"{aspect}:")
    print(f"  Output A: {scores['output_a']:.2f}")
    print(f"  Output B: {scores['output_b']:.2f}")

# Handle tie
if comparison.winner == "tie":
    print("Both outputs are equally good")
```

