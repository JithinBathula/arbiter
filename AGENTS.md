# CLAUDE.md - AI Agent Guide

**Purpose**: Quick reference for working on Arbiter
**Last Updated**: 2025-11-16

---

## Quick Orientation

**Arbiter**: Production-grade LLM evaluation framework (v0.1.0-alpha)
**Stack**: Python 3.10+, PydanticAI, provider-agnostic (OpenAI/Anthropic/Google/Groq)
**Coverage**: 95% test coverage, strict mypy, comprehensive examples

### Directory Structure

```
arbiter/
├── arbiter/
│   ├── api.py              # Public API (evaluate, compare)
│   ├── core/               # Infrastructure (llm_client, middleware, monitoring, registry)
│   ├── evaluators/         # Semantic, CustomCriteria, Pairwise, Factuality, Groundedness, Relevance
│   ├── storage/            # Storage backends (Phase 4)
│   └── tools/              # Utilities
├── examples/               # 15+ comprehensive examples
├── tests/                  # Unit + integration tests
└── pyproject.toml          # Dependencies and config
```

---

## Critical Rules

### 1. Template Method Pattern
All evaluators extend `BasePydanticEvaluator` and implement 4 methods:

```python
class MyEvaluator(BasePydanticEvaluator):
    @property
    def name(self) -> str:
        return "my_evaluator"

    def _get_system_prompt(self) -> str:
        return "You are an expert evaluator..."

    def _get_user_prompt(self, output: str, reference: Optional[str], criteria: Optional[str]) -> str:
        return f"Evaluate '{output}' against: {criteria}"

    def _get_response_type(self) -> Type[BaseModel]:
        return MyEvaluatorResponse  # Pydantic model

    async def _compute_score(self, response: BaseModel) -> Score:
        resp = cast(MyEvaluatorResponse, response)
        return Score(name=self.name, value=resp.score, confidence=resp.confidence, explanation=resp.explanation)
```

### 2. Provider-Agnostic Design
Must work with ANY LLM provider (OpenAI, Anthropic, Google, Groq, Mistral, Cohere).

```python
# ✅ GOOD
client = await LLMManager.get_client(provider="anthropic", model="claude-3-5-sonnet")

# ❌ BAD
from openai import OpenAI
client = OpenAI()  # Hardcoded to OpenAI
```

### 3. Type Safety (Strict Mypy)
All functions require type hints, no `Any` without justification.

### 4. No Placeholders/TODOs
Production-grade code only. Complete implementations or nothing.

### 5. Complete Features Only
If you start, you finish:
- ✅ Implementation complete
- ✅ Tests (>80% coverage)
- ✅ Docstrings
- ✅ Example code
- ✅ Exported in `__init__.py`

### 6. PydanticAI for Structured Outputs
All evaluators use PydanticAI for type-safe LLM responses.

---

## Development Workflow

### Before Starting
1. Check `git status` and `git branch`
2. Create feature branch: `git checkout -b feature/my-feature`

### During Development
1. Follow template method pattern
2. Write tests as you code (not after)
3. Run `make test` frequently

### Before Committing
```bash
make test        # Tests pass
make type-check  # Mypy clean
make lint        # Ruff clean
make format      # Black formatted
```

### After Completing
1. Add example to `examples/` if user-facing
2. Update README.md if API changed

---

## Common Tasks

### Add New Evaluator
```bash
# 1. Create evaluator file
touch arbiter/evaluators/my_evaluator.py

# 2. Implement template methods (see Critical Rules #1)

# 3. Export in arbiter/evaluators/__init__.py
from .my_evaluator import MyEvaluator
__all__ = [..., "MyEvaluator"]

# 4. Export in arbiter/__init__.py
from .evaluators import MyEvaluator
__all__ = [..., "MyEvaluator"]

# 5. Write tests
touch tests/unit/test_my_evaluator.py

# 6. Add example
touch examples/my_evaluator_example.py
```

### Run Tests
```bash
make test              # All tests with coverage
pytest tests/unit/     # Unit tests only
pytest -v              # Verbose output
make test-cov          # Coverage report
```

---

## Code Quality Standards

### Docstrings
```python
async def evaluate(output: str, reference: Optional[str] = None) -> EvaluationResult:
    """Evaluate LLM output against reference or criteria.

    Args:
        output: The LLM output to evaluate
        reference: Optional reference text for comparison

    Returns:
        EvaluationResult with scores, metrics, and interactions

    Raises:
        ValidationError: If output is empty
        EvaluatorError: If evaluation fails

    Example:
        >>> result = await evaluate(output="Paris", reference="Paris is the capital of France")
        >>> print(result.overall_score)
        0.92
    """
```

### Formatting
- **black**: Line length 88
- **ruff**: Follow pyproject.toml config
- **mypy**: Strict mode (all functions typed)

---

## Quick Reference

### Key Files
- **evaluators/semantic.py** - Reference evaluator implementation
- **pyproject.toml** - Dependencies and config
- **README.md** - User documentation with examples
- **examples/** - 15+ comprehensive examples

### Key Patterns
- **Evaluators**: Template method pattern (4 required methods)
- **Middleware**: Pre/post processing pipeline
- **LLM Client**: Provider-agnostic abstraction
- **Interaction Tracking**: Automatic LLM call logging

### Make Targets
```bash
make test          # Run tests with coverage
make type-check    # Run mypy
make lint          # Run ruff
make format        # Run black
make all           # Format + lint + type-check + test
```

---

## Working with AI Agents: Lessons Learned

### Audience Context Recognition
**Pattern**: When creating materials for specific audiences (engineers, researchers, business users), immediately adapt tone and content.

**Examples**:
- **Engineering audiences** (AI Tinkerers, tech meetups) → Technical tone, no marketing language
- **Business audiences** (executive presentations) → Focus on value, ROI, business impact
- **Academic audiences** (research papers) → Methodology, rigor, citations

**Common mistakes**:
- Using marketing language for technical audiences
- Mixing presentation materials (narratives, talking points) with code examples
- Defaulting to generic tone instead of contextualizing

**Fix**: Before creating content, ask: "Who is this for?" and adjust accordingly.

### Code vs. Presentation Materials
**Pattern**: Keep code examples and presentation materials strictly separated.

**Code examples** (`examples/`):
- Clean technical demonstrations
- Self-contained, runnable
- Show real data structures
- No narratives or talking points
- Full output, not truncated summaries

**Presentation materials** (`assets/`, docs):
- Openers, narratives, talking points
- Speaker notes and demo flows
- Audience-appropriate language
- References to code, not embedded in it

**Common mistake**: Adding presentation narratives to code files (openers in example docstrings, marketing language in comments).

### Testing Output Quality
**Pattern**: Test not just functionality, but output quality and usefulness.

When creating examples:
1. Run the code to verify it works (functionality)
2. Review the actual output to verify it's useful (quality)
3. Check that output serves the example's purpose (effectiveness)

**Example**: Debugging example showing "first 200 chars" of prompts is functionally correct but useless for understanding what happened. Show full prompts/responses instead.

### Iterative Refinement Over Perfection
**Pattern**: Ship working version, get feedback, refine based on actual output.

**Effective workflow**:
1. Create initial implementation
2. Test it (run the code, verify output)
3. Get feedback on real results
4. Fix specific issues identified
5. Commit, repeat

**Ineffective**: Try to anticipate all requirements upfront and build perfect solution before testing.

### Direct Feedback Enables Fast Iteration
**Pattern**: Clear, immediate feedback on what's wrong enables rapid course correction.

**Effective feedback characteristics**:
- **Direct**: "This reads like marketing" (clear what's wrong)
- **Specific**: "Move this section after that one" (concrete action)
- **Immediate**: Don't accumulate issues, address as they appear
- **Contextual**: Reference prior conversation ("the first one, the one I liked")

**Why this works**: No ambiguity about what needs to change, minimal back-and-forth, fast feedback loops.

### Use TodoWrite for Multi-Step Tasks
**Pattern**: For tasks with 3+ steps, use TodoWrite to track progress.

**When to use**:
- Multiple discrete tasks in sequence
- Complex workflows requiring phase tracking
- Ensures nothing gets forgotten
- Provides progress visibility

**Example**: "Test example → Update opener → Update presentation docs" breaks into clear trackable tasks.

### Commit Hygiene for Collaboration
**Pattern**: Every meaningful change gets its own commit with clear message.

**Benefits**:
- Easy to track what changed when
- Allows selective rollback if needed
- Communicates progress through git log
- Makes PR review easier

**Good commit messages**:
- What changed (files/features)
- Why it changed (context)
- Related issues or PRs

---

**Questions?** Check evaluators/semantic.py (reference implementation) or README.md (user docs)

**Last Updated**: 2025-01-18
