"""Pairwise comparison with middleware example.

This example demonstrates how to use middleware (logging, metrics, caching)
with pairwise comparison operations. Middleware provides consistent observability
across both evaluate() and compare() functions.

Run with:
    python examples/pairwise_with_middleware.py
"""

import asyncio
import os
from dotenv import load_dotenv

from arbiter import compare
from arbiter.core.middleware import (
    LoggingMiddleware,
    MetricsMiddleware,
    MiddlewarePipeline,
)


async def main():
    """Run pairwise comparison examples with middleware."""

    # Load environment variables from .env file
    load_dotenv()

    # Ensure API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set OPENAI_API_KEY environment variable")
        return

    print("🔍 Arbiter - Pairwise Comparison with Middleware")
    print("=" * 70)

    # Example 1: Basic logging middleware
    print("\n📝 Example 1: Pairwise Comparison with Logging")
    print("-" * 70)

    # Create pipeline with logging
    pipeline = MiddlewarePipeline([
        LoggingMiddleware(log_level="INFO")
    ])

    comparison1 = await compare(
        output_a="GPT-4: Paris is the capital of France.",
        output_b="Claude: The capital of France is Paris.",
        criteria="accuracy",
        model="gpt-4o-mini",
        middleware=pipeline,  # Enable logging
    )

    print(f"✅ Winner: {comparison1.winner}")
    print(f"   Confidence: {comparison1.confidence:.3f}")
    print("   (Check logs above for detailed middleware output)")

    # Example 2: Metrics middleware for performance tracking
    print("\n\n📝 Example 2: Pairwise Comparison with Metrics Tracking")
    print("-" * 70)

    # Create pipeline with metrics
    metrics_middleware = MetricsMiddleware()
    pipeline_with_metrics = MiddlewarePipeline([metrics_middleware])

    # Run multiple comparisons
    test_cases = [
        {
            "output_a": "Short answer A",
            "output_b": "Short answer B",
            "criteria": "brevity",
        },
        {
            "output_a": "Detailed response with comprehensive information.",
            "output_b": "Brief response.",
            "criteria": "completeness",
        },
        {
            "output_a": "Technical explanation with jargon.",
            "output_b": "Simple explanation in plain language.",
            "criteria": "clarity",
        },
    ]

    print("Running 3 comparisons...")
    for i, case in enumerate(test_cases, 1):
        result = await compare(
            output_a=case["output_a"],
            output_b=case["output_b"],
            criteria=case["criteria"],
            model="gpt-4o-mini",
            middleware=pipeline_with_metrics,
        )
        print(f"  {i}. Winner: {result.winner} (confidence: {result.confidence:.3f})")

    # Get aggregated metrics
    metrics = metrics_middleware.get_metrics()
    print("\n📊 Aggregated Metrics:")
    print(f"  Total Comparisons: {metrics['total_requests']}")
    print(f"  Total Processing Time: {metrics['total_time']:.2f}s")
    print(f"  Avg Time per Comparison: {metrics['avg_time_per_request']:.2f}s")
    print(f"  Total Tokens Used: {metrics['tokens_used']}")

    # Example 3: Combined middleware (logging + metrics)
    print("\n\n📝 Example 3: Multiple Middleware Together")
    print("-" * 70)

    # Create pipeline with multiple middleware
    combined_pipeline = MiddlewarePipeline([
        LoggingMiddleware(log_level="INFO"),
        MetricsMiddleware(),
    ])

    comparison3 = await compare(
        output_a="""Our AI model achieves 95% accuracy on the benchmark dataset,
outperforming previous state-of-the-art models by 5 percentage points.""",
        output_b="""The model performs well with good accuracy numbers compared to others.""",
        criteria="specificity, technical detail, credibility",
        reference="Describe the model's performance",
        model="gpt-4o-mini",
        middleware=combined_pipeline,
    )

    print(f"\n✅ Comparison Result:")
    print(f"   Winner: {comparison3.winner}")
    print(f"   Confidence: {comparison3.confidence:.3f}")
    print(f"   Reasoning: {comparison3.reasoning[:150]}...")

    if comparison3.aspect_scores:
        print(f"\n   Aspect Scores:")
        for aspect, scores in comparison3.aspect_scores.items():
            a_score = scores["output_a"]
            b_score = scores["output_b"]
            print(f"     {aspect}: A={a_score:.3f}, B={b_score:.3f}")

    # Example 4: Understanding middleware context
    print("\n\n📝 Example 4: Custom Middleware for Pairwise Detection")
    print("-" * 70)

    from arbiter.core.middleware import Middleware
    from arbiter.core.type_defs import MiddlewareContext
    from typing import Any, Callable, Optional

    class PairwiseDetectorMiddleware(Middleware):
        """Custom middleware that detects pairwise operations."""

        async def process(
            self,
            output: str,
            reference: Optional[str],
            next_handler: Callable[[str, Optional[str]], Any],
            context: MiddlewareContext,
        ) -> Any:
            # Check if this is a pairwise comparison
            is_pairwise = context.get("is_pairwise_comparison", False)

            if is_pairwise:
                pairwise_data = context.get("pairwise_data", {})
                output_a = pairwise_data.get("output_a", "")
                output_b = pairwise_data.get("output_b", "")
                criteria = pairwise_data.get("criteria", "N/A")

                print(f"   🎯 Detected pairwise comparison:")
                print(f"      Output A length: {len(output_a)} chars")
                print(f"      Output B length: {len(output_b)} chars")
                print(f"      Criteria: {criteria}")
            else:
                print(f"   📝 Regular evaluation detected")

            # Continue the chain
            return await next_handler(output, reference)

    # Create pipeline with custom detector
    detector_pipeline = MiddlewarePipeline([
        PairwiseDetectorMiddleware()
    ])

    comparison4 = await compare(
        output_a="First output with some content",
        output_b="Second output with different content",
        criteria="quality",
        model="gpt-4o-mini",
        middleware=detector_pipeline,
    )

    print(f"\n   Result: {comparison4.winner} wins")

    # Example 5: Performance monitoring for A/B testing
    print("\n\n📝 Example 5: A/B Testing with Performance Monitoring")
    print("-" * 70)

    # Simulate A/B testing scenario
    metrics_mw = MetricsMiddleware()
    ab_test_pipeline = MiddlewarePipeline([
        LoggingMiddleware(log_level="WARNING"),  # Minimal logging
        metrics_mw,
    ])

    print("Simulating A/B test with 5 comparisons...")

    ab_test_cases = [
        ("Prompt variant A output 1", "Prompt variant B output 1"),
        ("Prompt variant A output 2", "Prompt variant B output 2"),
        ("Prompt variant A output 3", "Prompt variant B output 3"),
        ("Prompt variant A output 4", "Prompt variant B output 4"),
        ("Prompt variant A output 5", "Prompt variant B output 5"),
    ]

    variant_a_wins = 0
    variant_b_wins = 0
    ties = 0

    for output_a, output_b in ab_test_cases:
        result = await compare(
            output_a=output_a,
            output_b=output_b,
            criteria="overall quality",
            model="gpt-4o-mini",
            middleware=ab_test_pipeline,
        )

        if result.winner == "output_a":
            variant_a_wins += 1
        elif result.winner == "output_b":
            variant_b_wins += 1
        else:
            ties += 1

    # A/B test results
    print(f"\n📊 A/B Test Results:")
    print(f"   Variant A wins: {variant_a_wins}")
    print(f"   Variant B wins: {variant_b_wins}")
    print(f"   Ties: {ties}")

    # Performance metrics
    ab_metrics = metrics_mw.get_metrics()
    print(f"\n⚡ Performance Metrics:")
    print(f"   Total comparisons: {ab_metrics['total_requests']}")
    print(f"   Avg latency: {ab_metrics['avg_time_per_request']:.3f}s")
    print(f"   Total cost estimate: ${ab_metrics['tokens_used'] * 0.00001:.4f}")

    print("\n" + "=" * 70)
    print("✨ Middleware provides consistent observability for both")
    print("   evaluate() and compare() operations!")


if __name__ == "__main__":
    asyncio.run(main())
