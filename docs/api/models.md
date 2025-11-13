# Core Models

Arbiter uses Pydantic models for type-safe data structures. All models are serializable and include validation.

## Main Models

- **[EvaluationResult](models/evaluation_result.md)** - Complete evaluation results
- **[ComparisonResult](models/comparison_result.md)** - Pairwise comparison results
- **[Score](models/score.md)** - Individual metric score
- **[LLMInteraction](models/llm_interaction.md)** - LLM call tracking
- **[Metric](models/metric.md)** - Metadata about computed metrics

## Common Patterns

### Accessing Scores

```python
result = await evaluate(...)

# Get overall score
print(result.overall_score)

# Get specific score
semantic_score = result.get_score("semantic_similarity")
if semantic_score:
    print(f"Semantic: {semantic_score.value}")

# Iterate all scores
for score in result.scores:
    print(f"{score.name}: {score.value:.2f}")
```

### Accessing Interactions

```python
# All interactions
for interaction in result.interactions:
    print(f"{interaction.purpose}: {interaction.tokens_used} tokens")

# Filter by purpose
evaluation_interactions = result.get_interactions_by_purpose("semantic_evaluation")

# Calculate cost
total_cost = result.total_llm_cost(cost_per_1k_tokens=0.03)
```

### Handling Partial Results

```python
if result.partial:
    print("⚠️ Some evaluators failed")
    for evaluator, error in result.errors.items():
        print(f"  {evaluator}: {error}")
else:
    print("✅ All evaluators succeeded")
```

