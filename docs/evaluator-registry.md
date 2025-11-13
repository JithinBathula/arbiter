# Evaluator Registry System

The evaluator registry provides a centralized, type-safe system for managing evaluators in Arbiter. This makes it easy to discover available evaluators, register custom ones, and get helpful error messages.

## Overview

The registry system consists of:
- **`AVAILABLE_EVALUATORS`**: Dictionary mapping evaluator names to their classes
- **`EvaluatorName`**: Literal type for IDE autocomplete support
- **Registration functions**: `register_evaluator()`, `get_evaluator_class()`, `validate_evaluator_name()`

## Basic Usage

### Getting Available Evaluators

```python
from arbiter import get_available_evaluators

# Get list of all available evaluator names
evaluators = get_available_evaluators()
print(evaluators)  # ['semantic', 'custom_criteria', 'pairwise']
```

### Using Evaluators with Type Safety

The `EvaluatorName` type provides autocomplete in IDEs:

```python
from arbiter import evaluate, EvaluatorName
from typing import List

# IDE will autocomplete available evaluator names
evaluators: List[EvaluatorName] = ["semantic", "custom_criteria"]

result = await evaluate(
    output="Test output",
    reference="Test reference",
    evaluators=evaluators,  # Type-safe
)
```

### Validation with Helpful Errors

The registry provides clear error messages when you use an invalid evaluator name:

```python
from arbiter import evaluate

# This will raise ValidationError with helpful message
result = await evaluate(
    output="Test",
    evaluators=["unknown_evaluator"],  # Invalid name
)
# ValidationError: Unknown evaluator: 'unknown_evaluator'.
# Available evaluators: ['semantic', 'custom_criteria', 'pairwise']
```

## Registering Custom Evaluators

You can register your own custom evaluators to extend Arbiter's functionality:

```python
from arbiter import register_evaluator, BasePydanticEvaluator
from arbiter.core.models import Score
from pydantic import BaseModel
from typing import Type

# 1. Define your response model
class CustomResponse(BaseModel):
    score: float
    explanation: str

# 2. Create your evaluator class
class MyCustomEvaluator(BasePydanticEvaluator):
    @property
    def name(self) -> str:
        return "my_custom"

    def _get_system_prompt(self) -> str:
        return "You are a custom evaluator..."

    def _get_user_prompt(
        self, output: str, reference: str | None, criteria: str | None
    ) -> str:
        return f"Evaluate this: {output}"

    def _get_response_type(self) -> Type[BaseModel]:
        return CustomResponse

    async def _compute_score(self, response: BaseModel) -> Score:
        resp = response  # Type: CustomResponse
        return Score(
            name=self.name,
            value=resp.score,
            explanation=resp.explanation,
        )

# 3. Register your evaluator
register_evaluator("my_custom", MyCustomEvaluator)

# 4. Use it with the main API
result = await evaluate(
    output="Test output",
    evaluators=["my_custom"],  # Now available!
)
```

## Advanced Usage

### Programmatic Evaluator Access

Get evaluator classes programmatically:

```python
from arbiter import get_evaluator_class, LLMManager

# Get evaluator class by name
evaluator_class = get_evaluator_class("semantic")

# Create instance directly
client = await LLMManager.get_client(model="gpt-4o-mini")
evaluator = evaluator_class(llm_client=client)

# Use evaluator directly
score = await evaluator.evaluate(
    output="Paris is the capital of France",
    reference="The capital of France is Paris"
)
```

### Validation in Libraries

If you're building on top of Arbiter, use validation to provide good UX:

```python
from arbiter import validate_evaluator_name, ValidationError

def my_evaluation_function(evaluator_names: List[str]):
    """Validate evaluators before expensive operations."""
    try:
        for name in evaluator_names:
            validate_evaluator_name(name)
    except ValidationError as e:
        print(f"Invalid configuration: {e}")
        return None

    # Proceed with evaluation...
```

## Built-in Evaluators

### semantic
**Purpose**: Measures semantic similarity between output and reference text

**Best for**:
- Paraphrase detection
- Translation quality
- Content summarization evaluation

**Usage**:
```python
result = await evaluate(
    output="Paris is France's capital city",
    reference="The capital of France is Paris",
    evaluators=["semantic"]
)
```

### custom_criteria
**Purpose**: Evaluates output against domain-specific criteria

**Best for**:
- Domain-specific quality assessment (medical, legal, technical)
- Brand voice compliance
- Multi-aspect evaluation (clarity, accuracy, tone)

**Usage**:
```python
# Single criteria
result = await evaluate(
    output="Medical advice about diabetes",
    criteria="Medical accuracy, HIPAA compliance, patient-appropriate tone",
    evaluators=["custom_criteria"]
)

# Multi-criteria (returns separate scores)
result = await evaluate(
    output="Product description",
    criteria={
        "accuracy": "Factually correct information",
        "persuasiveness": "Compelling call-to-action",
        "brand_voice": "Matches company style"
    },
    evaluators=["custom_criteria"]
)
```

### pairwise
**Purpose**: Compares two outputs to determine which is better

**Best for**:
- A/B testing
- Model comparison
- Output selection
- Quality benchmarking

**Usage**:
```python
from arbiter import compare

comparison = await compare(
    output_a="GPT-4 response about Paris",
    output_b="Claude response about Paris",
    criteria="accuracy, clarity, completeness",
    reference="What is the capital of France?"
)
print(f"Winner: {comparison.winner}")  # "output_a", "output_b", or "tie"
```

## Registry Implementation Details

### AVAILABLE_EVALUATORS Dictionary

The registry is a simple dictionary mapping names to classes:

```python
from arbiter.core.registry import AVAILABLE_EVALUATORS

print(AVAILABLE_EVALUATORS)
# {
#     'semantic': <class 'arbiter.evaluators.semantic.SemanticEvaluator'>,
#     'custom_criteria': <class 'arbiter.evaluators.custom_criteria.CustomCriteriaEvaluator'>,
#     'pairwise': <class 'arbiter.evaluators.pairwise.PairwiseComparisonEvaluator'>
# }
```

### Type Safety with Literal

The `EvaluatorName` type is automatically generated from available evaluators:

```python
from typing import Literal
from arbiter.core.registry import AVAILABLE_EVALUATORS

# Generated at runtime
EvaluatorName = Literal["semantic", "custom_criteria", "pairwise"]
```

This provides IDE autocomplete and static type checking while remaining flexible for custom evaluators.

## Best Practices

### 1. Use Type Hints
```python
from arbiter import EvaluatorName
from typing import List

evaluators: List[EvaluatorName] = ["semantic"]  # Type-safe
```

### 2. Validate Early
```python
# Validate before expensive operations
validate_evaluator_name("unknown")  # Raises ValidationError immediately
```

### 3. Register During Initialization
```python
# Register custom evaluators at app startup
def initialize_app():
    register_evaluator("domain_specific", DomainEvaluator)
    register_evaluator("brand_voice", BrandVoiceEvaluator)
```

### 4. Check Availability Programmatically
```python
available = get_available_evaluators()
if "my_custom" in available:
    # Evaluator is registered
    pass
```

## Migration from Hardcoded Names

**Before (hardcoded):**
```python
# Old approach with hardcoded if/else
if evaluator_name == "semantic":
    evaluator = SemanticEvaluator(client)
elif evaluator_name == "custom_criteria":
    evaluator = CustomCriteriaEvaluator(client)
else:
    raise ValueError(f"Unknown evaluator: {evaluator_name}")
```

**After (registry):**
```python
# New approach with registry
evaluator_class = get_evaluator_class(evaluator_name)
evaluator = evaluator_class(llm_client=client)
```

## Error Messages

The registry provides helpful error messages:

```python
# Unknown evaluator
validate_evaluator_name("typo")
# ValidationError: Unknown evaluator: 'typo'.
# Available evaluators: ['semantic', 'custom_criteria', 'pairwise']
# Did you mean: 'semantic'?

# Empty string
validate_evaluator_name("")
# ValidationError: Evaluator name cannot be empty

# Name collision (registering duplicate)
register_evaluator("semantic", MyEvaluator)
# ValueError: Evaluator 'semantic' is already registered
```

## See Also

- [Custom Criteria Evaluator](./custom-criteria.md)
- [Pairwise Comparison Evaluator](./pairwise-comparison.md)
- [Creating Custom Evaluators](./custom-evaluators.md)
- [API Reference](./api-reference.md)
