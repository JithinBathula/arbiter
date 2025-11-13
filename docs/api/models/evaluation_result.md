# EvaluationResult

Complete result of an evaluation operation, containing all scores, metadata, and audit trail information.

## Fields

### Input Data
- `output` (str): The LLM output that was evaluated
- `reference` (Optional[str]): Reference text used for comparison
- `criteria` (Optional[str]): Evaluation criteria used

### Results
- `scores` (List[Score]): Individual metric scores from successful evaluators
- `overall_score` (float): Aggregate score (average of successful evaluators)
- `passed` (bool): Whether evaluation passed quality threshold

### Error Handling
- `errors` (Dict[str, str]): Errors encountered, keyed by evaluator name
- `partial` (bool): Whether this is a partial result (some evaluators failed)

### Metadata
- `metrics` (List[Metric]): Metadata about computed metrics
- `evaluator_names` (List[str]): Names of evaluators used
- `total_tokens` (int): Total tokens used
- `processing_time` (float): Total processing time in seconds
- `timestamp` (datetime): When evaluation completed
- `interactions` (List[LLMInteraction]): All LLM API calls made
- `metadata` (Dict[str, Any]): Additional metadata

## Methods

### `get_score(name: str) -> Optional[Score]`

Get a specific score by name.

```python
semantic_score = result.get_score("semantic_similarity")
if semantic_score:
    print(f"Score: {semantic_score.value}")
```

### `get_metric(name: str) -> Optional[Metric]`

Get a specific metric by name.

```python
metric = result.get_metric("latency")
if metric:
    print(f"Latency: {metric.value}")
```

### `get_interactions_by_purpose(purpose: str) -> List[LLMInteraction]`

Filter interactions by purpose.

```python
evaluation_interactions = result.get_interactions_by_purpose("semantic_evaluation")
```

### `total_llm_cost(cost_per_1k_tokens: float = 0.01) -> float`

Estimate total LLM cost based on token usage.

```python
cost = result.total_llm_cost(cost_per_1k_tokens=0.03)
print(f"Total cost: ${cost:.4f}")
```

## Example

```python
result = await evaluate(
    output="Paris is the capital",
    reference="The capital of France is Paris",
    evaluators=["semantic"]
)

print(f"Overall Score: {result.overall_score:.2f}")
print(f"Passed: {result.passed}")
print(f"Processing Time: {result.processing_time:.2f}s")
print(f"Total Tokens: {result.total_tokens:,}")

# Check for partial results
if result.partial:
    print("⚠️ Some evaluators failed:")
    for evaluator, error in result.errors.items():
        print(f"  {evaluator}: {error}")

# Access interactions
for interaction in result.interactions:
    print(f"{interaction.purpose}: {interaction.tokens_used} tokens")
```

