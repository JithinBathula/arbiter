# LLMClient

Provider-agnostic LLM client with automatic provider detection and PydanticAI integration.

## Overview

The `LLMClient` provides a unified interface for interacting with various LLM providers (OpenAI, Anthropic, Google Gemini, Groq) while handling provider-specific details internally.

## Usage

### Automatic Provider Detection

```python
from arbiter.core import LLMManager

# Automatically detects provider from model name
client = await LLMManager.get_client(model="gpt-4o")
```

### Explicit Provider

```python
from arbiter.core import LLMManager, Provider

client = await LLMManager.get_client(
    provider=Provider.OPENAI,
    model="gpt-4o-mini"
)
```

### Custom Configuration

```python
from arbiter.core.llm_client import LLMClient, Provider

client = LLMClient(
    provider=Provider.OPENAI,
    model="gpt-4o-mini",
    temperature=0.1,  # Low temperature for consistency
    api_key="your-key"  # Optional, uses env var if not provided
)
```

## Supported Providers

- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo models
- **Anthropic**: Claude 3 family
- **Google Gemini**: Gemini Pro models
- **Groq**: Fast inference for open models
- **Mistral**: Mistral models
- **Cohere**: Cohere models

## Methods

### `create_agent(system_prompt: str, result_type: Type[BaseModel]) -> Agent`

Create a PydanticAI agent for structured outputs.

```python
from pydantic import BaseModel

class Response(BaseModel):
    score: float
    explanation: str

agent = client.create_agent(
    system_prompt="You are an evaluator",
    result_type=Response
)

result = await agent.run("Evaluate this output")
```

## Environment Variables

Set API keys for each provider:
- `OPENAI_API_KEY` for OpenAI
- `ANTHROPIC_API_KEY` for Anthropic
- `GOOGLE_API_KEY` for Google Gemini
- `GROQ_API_KEY` for Groq
- `MISTRAL_API_KEY` for Mistral
- `COHERE_API_KEY` for Cohere

The client automatically uses the appropriate key based on the model.

