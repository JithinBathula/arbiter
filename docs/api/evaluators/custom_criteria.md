# CustomCriteriaEvaluator

Evaluates LLM outputs against custom, domain-specific criteria without requiring reference text.

## Overview

The `CustomCriteriaEvaluator` allows you to evaluate outputs against custom criteria, making it suitable for domain-specific quality assessments like medical accuracy, legal compliance, brand voice, etc.

## Usage

### Single Criteria

```python
from arbiter import evaluate

result = await evaluate(
    output="Medical advice about diabetes management",
    criteria="Medical accuracy, HIPAA compliance, appropriate tone for patients",
    evaluators=["custom_criteria"]
)

print(f"Score: {result.overall_score:.2f}")
print(f"Criteria met: {result.scores[0].metadata['criteria_met']}")
```

### Multi-Criteria

```python
result = await evaluate(
    output="Product description",
    criteria={
        "accuracy": "Factually correct product information",
        "persuasiveness": "Compelling call-to-action",
        "brand_voice": "Matches company brand guidelines"
    },
    evaluators=["custom_criteria"]
)

# Returns separate scores for each criterion
for score in result.scores:
    print(f"{score.name}: {score.value:.2f}")
```

## When to Use

- Domain-specific quality checks (medical accuracy, legal compliance)
- Brand voice and tone evaluation
- Style guide adherence
- Multi-aspect evaluation (accuracy, tone, completeness)
- Reference-free evaluation (no ground truth needed)

## Response Model

### Single Criteria

Returns `CustomCriteriaResponse` with:
- `score` (float): Overall score (0.0-1.0)
- `confidence` (float): Confidence in evaluation
- `explanation` (str): Detailed explanation
- `criteria_met` (List[str]): Criteria successfully met
- `criteria_not_met` (List[str]): Criteria not met

### Multi-Criteria

Returns `MultiCriteriaResponse` with:
- `scores` (Dict[str, float]): Score for each criterion
- `explanations` (Dict[str, str]): Explanation for each criterion
- `overall_score` (float): Average of all criterion scores

## Example

```python
# Medical domain evaluation
result = await evaluate(
    output="Patient should take medication with food",
    criteria="Medical accuracy, appropriate tone, HIPAA compliance",
    evaluators=["custom_criteria"]
)

if result.overall_score >= 0.8:
    print("✅ Meets medical standards")
else:
    print("⚠️ Needs review")
```

