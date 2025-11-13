# Examples

Complete code examples demonstrating Arbiter's features.

## Getting Started

- [Basic Evaluation](basic_evaluation.md) - Simple semantic evaluation
- [Multiple Evaluators](multiple_evaluators.md) - Combining evaluators
- [Custom Criteria](custom_criteria.md) - Domain-specific evaluation

## Advanced Usage

- [Pairwise Comparison](pairwise_comparison.md) - A/B testing and model comparison
- [Batch Processing](batch_manual.md) - Manual batching with asyncio.gather
- [Advanced Configuration](advanced_config.md) - Temperature, retries, custom clients
- [Interaction Tracking](interaction_tracking.md) - Complete observability

## Production Patterns

- [Error Handling](../examples/error_handling_example.py) - Handling failures gracefully
- [Middleware Usage](../examples/middleware_usage.py) - Logging, metrics, caching
- [Provider Switching](../examples/provider_switching.py) - Using different providers
- [Evaluator Registry](../examples/evaluator_registry_example.py) - Custom evaluators

## Running Examples

All examples can be run directly:

```bash
python examples/basic_evaluation.py
python examples/multiple_evaluators.py
# etc.
```

Make sure you have your API keys set:

```bash
export OPENAI_API_KEY="your-key-here"
```

