"""Semantic similarity evaluator using LLM-based comparison.

This evaluator assesses how semantically similar two texts are,
even if they use different wording. It's particularly useful for
evaluating whether an LLM output conveys the same meaning as a
reference text.

## When to Use:

- Evaluating paraphrase quality
- Checking if outputs capture reference meaning
- Comparing different phrasings of the same concept
- Translation or summarization quality

## Example:

    >>> evaluator = SemanticEvaluator(llm_client)
    >>> score = await evaluator.evaluate(
    ...     output="Paris is the capital of France",
    ...     reference="The capital of France is Paris"
    ... )
    >>> print(f"Semantic similarity: {score.value:.2f}")
    Semantic similarity: 0.98
"""

from typing import Optional, Type

from pydantic import BaseModel, Field

from ..core.llm_client import LLMClient
from ..core.models import Score
from .base import BasePydanticEvaluator

__all__ = ["SemanticEvaluator", "SemanticResponse"]


class SemanticResponse(BaseModel):
    """Structured response for semantic similarity evaluation."""

    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Semantic similarity score (0=completely different, 1=identical meaning)",
    )
    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence in this similarity assessment",
    )
    explanation: str = Field(
        ..., description="Explanation of why this similarity score was assigned"
    )
    key_differences: list[str] = Field(
        default_factory=list,
        description="Key semantic differences between the texts",
    )
    key_similarities: list[str] = Field(
        default_factory=list,
        description="Key semantic similarities between the texts",
    )


class SemanticEvaluator(BasePydanticEvaluator):
    """Evaluates semantic similarity between output and reference.

    Uses LLM reasoning to assess how similar two texts are in meaning,
    regardless of exact wording. This goes beyond simple string matching
    to understand conceptual similarity.

    The evaluator:
    - Identifies core meaning in both texts
    - Compares semantic content, not just words
    - Provides detailed explanation of similarities/differences
    - Returns confidence in the assessment

    Example:
        >>> # Create evaluator
        >>> from arbiter import LLMManager
        >>> client = await LLMManager.get_client(model="gpt-4o")
        >>> evaluator = SemanticEvaluator(client)
        >>>
        >>> # Evaluate semantic similarity
        >>> score = await evaluator.evaluate(
        ...     output="The quick brown fox jumps over the lazy dog",
        ...     reference="A fast brown fox leaps above a sleepy canine"
        ... )
        >>>
        >>> print(f"Similarity: {score.value:.2f}")
        >>> print(f"Explanation: {score.explanation}")
        >>>
        >>> # Check LLM interactions
        >>> interactions = evaluator.get_interactions()
        >>> print(f"Made {len(interactions)} LLM calls")
        >>> print(f"Total latency: {sum(i.latency for i in interactions):.2f}s")
    """

    @property
    def name(self) -> str:
        """Return evaluator identifier."""
        return "semantic_similarity"

    def _get_system_prompt(self) -> str:
        """Get system prompt defining semantic evaluation approach."""
        return """You are an expert at evaluating semantic similarity between texts.

Your task is to assess how similar two texts are in MEANING, not just in wording.

Consider:
- Core concepts and ideas conveyed
- Factual accuracy and information content
- Intent and purpose of the text
- Logical relationships between ideas

Ignore:
- Exact wording or phrasing
- Grammatical structure
- Writing style or tone (unless it changes meaning)

Provide:
- A similarity score from 0.0 (completely different meaning) to 1.0 (identical meaning)
- Your confidence in this assessment
- Clear explanation of your reasoning
- Key similarities and differences you identified

Be precise and analytical in your evaluation."""

    def _get_user_prompt(
        self, output: str, reference: Optional[str], criteria: Optional[str]
    ) -> str:
        """Get user prompt for specific evaluation."""
        if not reference:
            # If no reference, we can't do semantic comparison
            # Fall back to reference-free evaluation with criteria
            if criteria:
                return f"""Evaluate the semantic quality of this text based on the criteria: {criteria}

Text to evaluate:
{output}

Provide your semantic quality assessment."""
            else:
                # No reference and no criteria - evaluate general semantic coherence
                return f"""Evaluate the semantic coherence and clarity of this text:

{output}

Assess how well the text conveys clear meaning and logical ideas."""

        # Standard semantic similarity evaluation
        return f"""Compare the semantic similarity of these two texts:

OUTPUT (to evaluate):
{output}

REFERENCE (ground truth):
{reference}

Assess how similar they are in MEANING. Consider whether they convey the same information,
even if expressed differently. Provide a detailed analysis."""

    def _get_response_type(self) -> Type[BaseModel]:
        """Use custom semantic response model."""
        return SemanticResponse

    async def _compute_score(self, response: BaseModel) -> Score:
        """Extract Score from semantic response."""
        semantic_response = response  # Type hint: it's a SemanticResponse

        # Build detailed explanation
        explanation_parts = [semantic_response.explanation]

        if hasattr(semantic_response, "key_similarities") and semantic_response.key_similarities:
            explanation_parts.append(
                "\n\nKey Similarities:\n- "
                + "\n- ".join(semantic_response.key_similarities)
            )

        if hasattr(semantic_response, "key_differences") and semantic_response.key_differences:
            explanation_parts.append(
                "\n\nKey Differences:\n- "
                + "\n- ".join(semantic_response.key_differences)
            )

        full_explanation = "".join(explanation_parts)

        return Score(
            name="semantic_similarity",
            value=semantic_response.score,
            confidence=semantic_response.confidence,
            explanation=full_explanation,
            metadata={
                "similarities_count": len(
                    getattr(semantic_response, "key_similarities", [])
                ),
                "differences_count": len(
                    getattr(semantic_response, "key_differences", [])
                ),
            },
        )
