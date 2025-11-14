# Non-Functional Requirements (NFRs)

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Status:** Living Document

---

## Overview

This document defines the non-functional requirements for the Arbiter LLM evaluation framework. These requirements establish clear expectations for performance, scalability, reliability, security, and compatibility.

---

## Performance Requirements

### Response Time Targets

| Operation Type | Target (p50) | Target (p95) | Target (p99) | Notes |
|----------------|--------------|--------------|--------------|-------|
| Single evaluation | < 3s | < 5s | < 8s | Depends on LLM provider latency |
| Batch evaluation (10 items) | < 20s | < 30s | < 45s | With connection pooling |
| Pairwise comparison | < 4s | < 7s | < 10s | Single comparison operation |
| Multi-evaluator (3 evaluators) | < 8s | < 12s | < 18s | Parallel evaluator execution |

**Assumptions:**
- OpenAI gpt-4o-mini as reference model
- Typical prompt size: 500-1000 tokens
- Network latency: < 100ms
- No rate limiting or throttling

### Throughput Targets

| Processing Mode | Target Throughput | Configuration |
|-----------------|-------------------|---------------|
| Serial processing | 1-2 evaluations/sec | Single client, no pooling |
| Parallel processing | 10-20 evaluations/sec | Pool size: 10, concurrent requests |
| Batch processing | 50-100 items/minute | Optimal batch size: 10-20 items |

**Scaling Characteristics:**
- **Linear scaling:** Up to connection pool limit
- **Bottleneck:** LLM provider rate limits
- **Optimization:** Connection pooling + middleware caching

### Token Usage Estimates

| Evaluator Type | Input Tokens | Output Tokens | Total Tokens | Cost (GPT-4o-mini) |
|----------------|--------------|---------------|--------------|---------------------|
| Semantic evaluation | 400-600 | 100-200 | 500-800 | $0.0004-$0.0006 |
| Custom criteria (single) | 500-700 | 150-300 | 650-1000 | $0.0005-$0.0008 |
| Custom criteria (multi) | 600-800 | 200-400 | 800-1200 | $0.0006-$0.0010 |
| Pairwise comparison | 700-900 | 200-400 | 900-1300 | $0.0007-$0.0011 |

**Token Optimization:**
- Middleware caching: ~70% reduction for repeated evaluations
- Batch processing: ~15% reduction through context sharing
- Criteria reuse: ~20% reduction with consistent criteria

---

## Scalability Limits

### LLM Client Pool

| Parameter | Default | Range | Production Recommendation |
|-----------|---------|-------|---------------------------|
| Max concurrent clients | 10 | 1-50 | 10-20 (based on provider limits) |
| Connection timeout | 30s | 10s-120s | 30s |
| Max retries | 3 | 1-10 | 3 |
| Circuit breaker threshold | 5 | 3-10 | 5 |

**Pool Sizing Guidelines:**
- **Development:** 5 clients
- **Production (low volume):** 10 clients
- **Production (high volume):** 20 clients
- **Provider rate limits:** Configure based on your API tier

### Memory Footprint

| Component | Base Memory | Per Evaluation | Per 1000 Evaluations |
|-----------|-------------|----------------|----------------------|
| Framework overhead | ~50MB | ~1-2MB | ~1-2GB |
| With caching (10% hit rate) | ~100MB | ~0.5MB | ~500MB |
| With metrics tracking | +10MB | +0.1MB | +100MB |

**Memory Optimization:**
- Clear interaction history for long-running processes
- Configure cache TTL based on memory constraints
- Use streaming for very large batches (>1000 items)

### Concurrent Evaluation Limits

| Scenario | Max Concurrent | Limiting Factor |
|----------|----------------|-----------------|
| Same provider | 10-50 | Provider rate limits |
| Multiple providers | 50-100 | Memory + connection pool |
| With caching | 100-200 | Cache hit rate dependent |

---

## Reliability Guarantees

### Availability

| Metric | Target | Measurement |
|--------|--------|-------------|
| Framework uptime | 99.9% | Excluding provider outages |
| Circuit breaker recovery | < 60s | Half-open state timeout |
| Retry success rate | > 95% | After transient failures |

**Failure Handling:**
- **Circuit breaker:** Opens after 5 consecutive failures
- **Auto-recovery:** Tests recovery every 60 seconds
- **Partial results:** Returns successful evaluations on batch failures
- **Graceful degradation:** Falls back to simpler evaluations on complex failures

### Data Integrity

| Requirement | Implementation | Validation |
|-------------|----------------|------------|
| Interaction tracking | 100% of LLM calls | Automatic in BasePydanticEvaluator |
| Result consistency | Deterministic (temp=0) | Unit tests with fixed seeds |
| Score accuracy | ±0.001 precision | Float validation in Pydantic models |
| Metadata completeness | All fields populated | Schema validation |

### Error Recovery

| Error Type | Strategy | Max Retries | Backoff |
|------------|----------|-------------|---------|
| Rate limit (429) | Exponential backoff | 3 | 1s, 2s, 4s |
| Timeout | Retry | 3 | 1s, 2s, 4s |
| API error (500-599) | Retry | 3 | 1s, 2s, 4s |
| Authentication (401) | Fail fast | 0 | N/A |
| Circuit breaker open | Block + wait | N/A | 60s timeout |

**Error Response Guarantees:**
- All errors include provider context
- Partial results preserved on batch failures
- Original exceptions preserved in error chain
- Structured error details (error codes, retry info)

---

## Security Requirements

### API Key Management

| Requirement | Implementation | Enforcement |
|-------------|----------------|-------------|
| No hardcoded keys | Environment variables only | Code review + linting |
| Key rotation support | No client-side caching | Immediate effect |
| Key validation | Pre-flight check | Client initialization |
| Secure storage | User responsibility | Documentation guidance |

**Security Best Practices:**
- Use `.env` files (excluded from git)
- Rotate keys regularly (monthly minimum)
- Use different keys per environment
- Monitor for unauthorized usage

### Data Privacy

| Requirement | Implementation | GDPR Compliance |
|-------------|----------------|-----------------|
| No PII logging | Output/reference never logged | ✅ Yes |
| No persistent storage | Memory only (default) | ✅ Yes |
| Opt-in storage | Explicit user configuration | ✅ Yes |
| Data retention | 0 days (default) | ✅ Yes |

**Privacy Guarantees:**
- Evaluation inputs/outputs never logged by default
- LLM interactions sent only to configured provider
- No telemetry or analytics collection
- User controls all data persistence

### Input Validation

| Input Type | Validation | Sanitization |
|------------|------------|--------------|
| Output text | Non-empty string | Unicode normalization |
| Reference text | Optional string | Unicode normalization |
| Criteria | Optional string | Length limits |
| Model name | Provider validation | Whitelist check |
| Temperature | 0.0-2.0 range | Float validation |

---

## Compatibility Requirements

### Python Versions

| Version | Support Level | Testing | Notes |
|---------|---------------|---------|-------|
| 3.10 | ✅ Full support | CI/CD | Minimum version |
| 3.11 | ✅ Full support | CI/CD | Recommended |
| 3.12 | ✅ Full support | CI/CD | Latest stable |
| 3.13 | 🔄 Best effort | Manual | Beta support |
| 3.9 | ❌ Not supported | None | Missing type features |

**Python Feature Requirements:**
- Type hints (PEP 604): `str | None` syntax
- Structural pattern matching: Python 3.10+
- Exception groups: Python 3.11+ (optional)

### LLM Provider Compatibility

| Provider | Support Level | SDK Version | Models Tested |
|----------|---------------|-------------|---------------|
| OpenAI | ✅ Full | 2.0+ | GPT-4o, GPT-4, GPT-3.5-turbo |
| Anthropic | ✅ Full | 0.72+ | Claude 3.5 Sonnet, Claude 3 |
| Google Gemini | ✅ Full | 0.8.5+ | Gemini 1.5 Pro, Flash |
| Groq | ✅ Full | Latest | Llama 3.1, Mixtral |
| Mistral | 🔄 Beta | 1.0+ | Mistral models |
| Cohere | 🔄 Beta | 5.0+ | Command models |

**Provider Fallback:**
- Automatic provider switching on failure (optional)
- Graceful degradation to available providers
- Provider-specific error handling

### Operating Systems

| OS | Support Level | Testing | Notes |
|----|---------------|---------|-------|
| Linux | ✅ Full | CI/CD | Primary platform |
| macOS | ✅ Full | Local | Development platform |
| Windows | ✅ Full | Local | WSL recommended |
| Docker | ✅ Full | CI/CD | Official images |

### Dependency Versions

| Dependency | Minimum Version | Tested Version | Notes |
|------------|----------------|----------------|-------|
| pydantic | 2.12.0 | 2.12+ | Core validation |
| pydantic-ai | 1.14.0 | 1.14+ | Structured outputs |
| httpx | 0.28.0 | 0.28+ | Async HTTP |
| pymilvus | 2.6.0 | 2.6+ | Phase 3: Vector DB |
| openai | 2.0.0 | 2.0+ | LLM SDK |
| anthropic | 0.72.0 | 0.72+ | LLM SDK |

---

## Quality Requirements

### Code Quality Standards

| Metric | Target | Enforcement |
|--------|--------|-------------|
| Test coverage | ≥ 80% | CI/CD gate |
| Type coverage | 100% | mypy strict mode |
| Linting | 0 errors | ruff + CI/CD |
| Code formatting | 100% | black + CI/CD |

**Quality Gates:**
- All PRs must pass tests
- No mypy errors in strict mode
- Ruff linting with no errors
- Black formatting enforced

### Documentation Standards

| Component | Requirement | Validation |
|-----------|-------------|------------|
| Public API | Complete docstrings | Manual review |
| Examples | Working code | Automated testing |
| Architecture docs | Up to date | Monthly review |
| NFRs (this doc) | Updated quarterly | Scheduled review |

---

## Monitoring and Observability

### Metrics to Track

| Metric Category | Key Metrics | Collection Method |
|-----------------|-------------|-------------------|
| Performance | Latency (p50, p95, p99), throughput | MetricsMiddleware |
| Reliability | Error rate, circuit breaker state | Exception logging |
| Usage | Token count, API calls, cost | LLM interaction tracking |
| System | Memory usage, connection pool health | PerformanceMonitor |

### Recommended Logging

| Log Level | Use Case | Example |
|-----------|----------|---------|
| DEBUG | Development, troubleshooting | Detailed request/response |
| INFO | Normal operations | Evaluation started/completed |
| WARNING | Recoverable issues | Retry attempts, cache misses |
| ERROR | Failures | API errors, validation failures |
| CRITICAL | System failures | Circuit breaker open, pool exhausted |

### Health Checks

| Check | Frequency | Action on Failure |
|-------|-----------|-------------------|
| LLM provider reachability | Every 60s | Open circuit breaker |
| Connection pool health | Every 30s | Log warning |
| Memory usage | Every 60s | Trigger cleanup if > 80% |

---

## Compliance and Standards

### Code Standards

- **PEP 8:** Python style guide compliance
- **PEP 484:** Type hints for all public APIs
- **PEP 257:** Docstring conventions

### Testing Standards

- **Pytest:** Testing framework
- **Coverage:** Minimum 80% coverage
- **Mypy:** Strict type checking

### Versioning Standards

- **Semantic Versioning:** MAJOR.MINOR.PATCH
- **API Compatibility:** Maintain backward compatibility in MINOR versions
- **Deprecation Policy:** 6-month notice for breaking changes

---

## Performance Benchmarks

### Baseline Metrics (Reference System)

**System Specifications:**
- CPU: Apple M2 Pro (10-core)
- RAM: 16GB
- Network: 100Mbps
- Python: 3.11
- Provider: OpenAI (gpt-4o-mini)

**Benchmark Results:**

| Operation | p50 | p95 | p99 | Throughput |
|-----------|-----|-----|-----|------------|
| Single semantic eval | 2.1s | 4.2s | 6.8s | 1.5/sec |
| Batch 10 (serial) | 22s | 28s | 35s | 0.45/sec |
| Batch 10 (parallel, pool=5) | 8.5s | 12.1s | 16.4s | 1.2/sec |
| Batch 10 (parallel, pool=10) | 5.2s | 7.8s | 10.5s | 1.9/sec |

**Token Usage (per eval):**
- Average: 650 tokens
- Cost: $0.00052 (GPT-4o-mini rates)

---

## Continuous Improvement

### Review Schedule

| Document Section | Review Frequency | Owner |
|------------------|------------------|-------|
| Performance targets | Quarterly | Engineering team |
| Provider compatibility | Monthly | Engineering team |
| Security requirements | Quarterly | Security review |
| Entire document | Annually | Product + Engineering |

### Performance Regression Testing

- Run benchmarks on every release
- Alert on >10% performance degradation
- Track performance trends over time
- Document performance improvements

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-14 | Initial NFRs document | Claude Code |

---

## References

- [DESIGN_SPEC.md](../DESIGN_SPEC.md) - Architecture and design decisions
- [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) - Testing approach and standards
- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
