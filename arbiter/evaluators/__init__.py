"""Evaluators for assessing LLM outputs.

This module provides evaluators for different aspects of LLM outputs:
- Semantic similarity between output and reference
- Custom criteria evaluation (domain-specific quality checks)
- Factuality checking and hallucination detection
- Pairwise comparison for A/B testing
- Consistency evaluation (planned)
- Relevance scoring (planned)

All evaluators inherit from BasePydanticEvaluator and automatically
track LLM interactions for full observability.
"""

from .base import BasePydanticEvaluator, EvaluatorResponse
from .custom_criteria import (
    CustomCriteriaEvaluator,
    CustomCriteriaResponse,
    MultiCriteriaResponse,
)
from .factuality import FactualityEvaluator, FactualityResponse
from .pairwise import (
    AspectComparison,
    PairwiseComparisonEvaluator,
    PairwiseResponse,
)
from .semantic import SemanticEvaluator, SemanticResponse

__all__ = [
    "BasePydanticEvaluator",
    "EvaluatorResponse",
    "SemanticEvaluator",
    "SemanticResponse",
    "CustomCriteriaEvaluator",
    "CustomCriteriaResponse",
    "MultiCriteriaResponse",
    "FactualityEvaluator",
    "FactualityResponse",
    "PairwiseComparisonEvaluator",
    "PairwiseResponse",
    "AspectComparison",
]
