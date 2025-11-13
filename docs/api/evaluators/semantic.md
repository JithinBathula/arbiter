# SemanticEvaluator

Evaluates semantic similarity between output and reference text using LLM reasoning.

## Overview

The `SemanticEvaluator` assesses how semantically similar two texts are, even if they use different wording. It's particularly useful for evaluating whether an LLM output conveys the same meaning as a reference text.

## Usage

```python
from arbiter import SemanticEvaluator, LLMManager

client = await LLMManager.get_client(model="gpt-4o-mini")
evaluator = SemanticEvaluator(client)

score = await evaluator.evaluate(
    output="Paris is the capital of France",
    reference="The capital of France is Paris"
)

print(f"Semantic similarity: {score.value:.2f}")
print(f"Confidence: {score.confidence:.2f}")
print(f"Explanation: {score.explanation}")
```

## When to Use

- Evaluating paraphrase quality
- Checking if outputs capture reference meaning
- Comparing different phrasings of the same concept
- Translation or summarization quality

## Response Model

The evaluator returns a `SemanticResponse` with:
- `score` (float): Semantic similarity score (0.0-1.0)
- `confidence` (float): Confidence in the assessment
- `explanation` (str): Human-readable explanation
- `key_similarities` (List[str]): Main similarities found
- `key_differences` (List[str]): Main differences found

## Example

```python
result = await evaluate(
    output="The quick brown fox jumps over the lazy dog",
    reference="A fast brown fox leaps above a sleepy canine",
    evaluators=["semantic"]
)

# Score will be high (0.9+) because meanings are similar
# despite different wording
```

