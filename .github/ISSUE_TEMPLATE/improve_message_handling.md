---
name: Improve Multi-Turn Message Handling
about: Enhance message handling in LLMClient to properly support multi-turn conversations
title: "[Enhancement]: Improve multi-turn message handling in LLMClient"
labels: ["enhancement", "good first issue"]
---

## Problem Statement

Currently, `LLMClient._execute_pydanticai_completion()` flattens multi-turn conversation messages into a single prompt string (lines 304-326 in `arbiter_ai/core/llm_client.py`). This approach:

1. **Loses conversation structure** - Assistant messages are converted to `"[assistant]\n{content}"` strings instead of preserving proper message roles
2. **Inefficient for multi-turn conversations** - All messages are concatenated rather than using proper conversation state
3. **Limits functionality** - Cannot leverage PydanticAI's conversation management features

## Current Implementation

```python
# Current approach flattens messages:
system_prompt = ""
user_messages: List[str] = []
for msg in typed_messages:
    role = msg.get("role")
    content = msg.get("content") or ""
    if role == "system" and not system_prompt:
        system_prompt = str(content)
    elif role == "user":
        user_messages.append(str(content))
    elif role == "assistant":
        user_messages.append(f"[assistant]\n{content}")  # Loses structure
    else:
        user_messages.append(str(content))

user_prompt = "\n\n".join(user_messages)  # Single flattened string
```

## Proposed Solution

Investigate and implement proper multi-turn conversation support using PydanticAI's conversation state management. Options to explore:

1. **Use PydanticAI's conversation state** - If PydanticAI supports conversation history, use it properly
2. **Preserve message structure** - Pass messages as structured data rather than flattening
3. **Agent.run() with conversation context** - Check if Agent.run() supports conversation history parameters

## Expected Behavior

Multi-turn conversations should preserve message roles and structure:

```python
messages = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "What's 2+2?"}
]

# Should preserve structure, not flatten to single string
response = await client.complete(messages)
```

## Research Needed

- [ ] Check PydanticAI documentation for conversation/message handling
- [ ] Investigate if `Agent.run()` supports conversation history
- [ ] Look for PydanticAI examples with multi-turn conversations
- [ ] Test current behavior with complex multi-turn scenarios

## Related Code

- `arbiter_ai/core/llm_client.py` - `_execute_pydanticai_completion()` method (lines 296-370)
- All providers now route through PydanticAI (after refactoring in #XXX)

## Priority

Medium - Current implementation works but is suboptimal for multi-turn conversations. This is a quality-of-life improvement rather than a critical bug.

## Additional Context

This issue was identified during refactoring to route all providers through PydanticAI. The message flattening was already present but becomes more important now that all providers use this path.

