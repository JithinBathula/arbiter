"""Core type definitions and enumerations for Arbiter.

This module defines the fundamental types used throughout the Arbiter
evaluation framework, including provider enumerations, evaluator types,
and storage types.
"""

from enum import Enum

__all__ = ["Provider", "MetricType", "StorageType"]


class Provider(str, Enum):
    """Enumeration of supported LLM providers.

    Each provider represents a different LLM API service. The enum
    values are used for configuration and automatic detection.

    Attributes:
        OPENAI: OpenAI's GPT models (GPT-3.5, GPT-4, etc.)
        ANTHROPIC: Anthropic's Claude models (Claude 3 family)
        GEMINI: Google's Gemini models (Gemini Pro, etc.)
        GROQ: Groq's fast inference service for open models
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"


class MetricType(str, Enum):
    """Types of evaluation metrics.

    Defines the standard metrics that evaluators can compute.
    """

    SEMANTIC_SIMILARITY = "semantic_similarity"
    FACTUALITY = "factuality"
    CONSISTENCY = "consistency"
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    FLUENCY = "fluency"
    CUSTOM = "custom"


class StorageType(str, Enum):
    """Types of storage backends.

    Defines the available storage backend options for persisting
    evaluation results.
    """

    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
    CUSTOM = "custom"
