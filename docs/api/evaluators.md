# Evaluators

Evaluators assess LLM outputs against different criteria. All evaluators inherit from `BasePydanticEvaluator` and automatically track LLM interactions.

## Built-in Evaluators

- **[SemanticEvaluator](evaluators/semantic.md)** - Semantic similarity evaluation
- **[CustomCriteriaEvaluator](evaluators/custom_criteria.md)** - Domain-specific criteria evaluation
- **[PairwiseComparisonEvaluator](evaluators/pairwise.md)** - A/B testing and comparison

## Using Evaluators

### Via High-Level API

```python
from arbiter import evaluate

result = await evaluate(
    output="Your LLM output",
    reference="Expected output",
    evaluators=["semantic", "custom_criteria"]
)
```

### Direct Usage

```python
from arbiter import SemanticEvaluator, LLMManager

client = await LLMManager.get_client(model="gpt-4o-mini")
evaluator = SemanticEvaluator(client)

score = await evaluator.evaluate(
    output="Your output",
    reference="Expected output"
)
```

## Custom Evaluators

Register custom evaluators using the registry system:

```python
from arbiter import register_evaluator, BasePydanticEvaluator

class MyEvaluator(BasePydanticEvaluator):
    # Implement required methods
    ...

register_evaluator("my_evaluator", MyEvaluator)

# Now use in evaluate()
result = await evaluate(
    output="test",
    evaluators=["my_evaluator"]
)
```

See [Evaluator Registry Guide](../guides/evaluator-registry.md) for details.

