# PairwiseComparisonEvaluator

Compares two LLM outputs to determine which is better, useful for A/B testing and model comparison.

## Overview

The `PairwiseComparisonEvaluator` performs head-to-head comparison of two outputs, determining a winner and providing detailed reasoning and aspect-level scores.

## Usage

### Via High-Level API

```python
from arbiter import compare

comparison = await compare(
    output_a="GPT-4 response",
    output_b="Claude response",
    criteria="accuracy, clarity, completeness"
)

print(f"Winner: {comparison.winner}")
print(f"Confidence: {comparison.confidence:.2f}")
```

### Direct Usage

```python
from arbiter import PairwiseComparisonEvaluator, LLMManager

client = await LLMManager.get_client(model="gpt-4o")
evaluator = PairwiseComparisonEvaluator(client)

comparison = await evaluator.compare(
    output_a="First output",
    output_b="Second output",
    criteria="accuracy, clarity"
)
```

## When to Use

- **A/B Testing**: Compare different prompts or models
- **Model Comparison**: Evaluate which model performs better
- **Output Selection**: Choose best output from multiple candidates
- **Quality Assessment**: Compare outputs against criteria

## Response Model

Returns `ComparisonResult` with:
- `winner` (Literal["output_a", "output_b", "tie"]): Which output won
- `confidence` (float): Confidence in the comparison
- `reasoning` (str): Detailed reasoning for the decision
- `aspect_scores` (Dict[str, Dict[str, float]]): Scores by aspect
- `interactions` (List[LLMInteraction]): All LLM calls made

## Example

```python
comparison = await compare(
    output_a="Paris is the capital of France, founded in 3rd century BC.",
    output_b="The capital of France is Paris, established around 250 BC.",
    criteria="accuracy, clarity, completeness",
    reference="What is the capital of France?"
)

if comparison.winner == "output_a":
    print("GPT-4 output is better")
elif comparison.winner == "output_b":
    print("Claude output is better")
else:
    print("Both outputs are equally good")

# Check aspect scores
for aspect, scores in comparison.aspect_scores.items():
    print(f"{aspect}:")
    print(f"  Output A: {scores['output_a']:.2f}")
    print(f"  Output B: {scores['output_b']:.2f}")
```

