# LLMInteraction

Record of a single LLM API call during evaluation, providing complete observability.

## Overview

Every LLM call made during evaluation is automatically tracked in an `LLMInteraction` object. This provides complete transparency into how evaluations are performed.

## Fields

- `prompt` (str): The prompt sent to the LLM
- `response` (str): The LLM's response
- `model` (str): Model used for this call
- `tokens_used` (int): Tokens consumed in this call
- `latency` (float): Time taken for this call (seconds)
- `timestamp` (datetime): When this call was made
- `purpose` (str): Purpose of this call (e.g., "semantic_evaluation")
- `metadata` (Dict[str, Any]): Additional context about this call

## Use Cases

### Cost Tracking

```python
for interaction in result.interactions:
    cost = (interaction.tokens_used / 1000) * cost_per_1k_tokens
    print(f"{interaction.purpose}: {interaction.tokens_used} tokens = ${cost:.6f}")
```

### Performance Monitoring

```python
total_latency = sum(i.latency for i in result.interactions)
avg_latency = total_latency / len(result.interactions)
print(f"Average latency: {avg_latency:.3f}s")
```

### Debugging

```python
# Inspect exact prompt and response
interaction = result.interactions[0]
print(f"Prompt: {interaction.prompt}")
print(f"Response: {interaction.response}")
```

### Audit Trails

```python
# Complete audit trail
for interaction in result.interactions:
    print(f"{interaction.timestamp}: {interaction.purpose}")
    print(f"  Model: {interaction.model}")
    print(f"  Tokens: {interaction.tokens_used}")
    print(f"  Latency: {interaction.latency:.3f}s")
```

## Example

```python
result = await evaluate(...)

# Access interactions
for i, interaction in enumerate(result.interactions, 1):
    print(f"Interaction {i}:")
    print(f"  Purpose: {interaction.purpose}")
    print(f"  Model: {interaction.model}")
    print(f"  Tokens: {interaction.tokens_used:,}")
    print(f"  Latency: {interaction.latency:.3f}s")
    print(f"  Timestamp: {interaction.timestamp}")
```

## Key Benefits

- **Complete Transparency**: See every LLM call
- **Cost Visibility**: Track token usage and costs
- **Performance Monitoring**: Identify slow operations
- **Debugging**: Inspect prompts and responses
- **Compliance**: Complete audit trail for regulations

