# Evaluator Registry

Dynamic evaluator discovery and registration system.

## Overview

The registry system allows you to discover available evaluators, register custom evaluators, and get helpful error messages when using invalid evaluator names.

## Functions

### `get_available_evaluators() -> List[str]`

Get list of all registered evaluator names.

```python
from arbiter import get_available_evaluators

evaluators = get_available_evaluators()
print(evaluators)  # ['semantic', 'custom_criteria', 'pairwise']
```

### `register_evaluator(name: str, evaluator_class: Type[BaseEvaluator]) -> None`

Register a custom evaluator.

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

### `get_evaluator_class(name: str) -> Optional[Type[BaseEvaluator]]`

Get evaluator class by name.

```python
from arbiter import get_evaluator_class

SemanticEvaluator = get_evaluator_class("semantic")
```

### `validate_evaluator_name(name: str) -> None`

Validate that an evaluator name exists. Raises `ValidationError` if not.

```python
from arbiter import validate_evaluator_name

validate_evaluator_name("semantic")  # OK
validate_evaluator_name("unknown")    # Raises ValidationError
```

## Type Safety

Use `EvaluatorName` type for IDE autocomplete:

```python
from arbiter import EvaluatorName
from typing import List

evaluators: List[EvaluatorName] = ["semantic", "custom_criteria"]
# IDE will autocomplete available evaluator names
```

## Example

See [Evaluator Registry Guide](../../guides/evaluator-registry.md) for complete examples.

