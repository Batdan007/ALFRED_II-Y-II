# Accumulated Learnings

## Technical Lessons

### 2026-01-08: NumPy/Numba Compatibility
**Problem**: Voice learning failed with "Numba needs NumPy 2.3 or less. Got NumPy 2.4"
**Solution**: Install numpy>=2.0,<2.3 to satisfy both numba and opencv-python
**Key Insight**: Python dependency conflicts require checking all package constraints

### 2025-xx-xx: Privacy-First Architecture Works
Local Ollama as default, cloud as fallback with consent. Users appreciate control over their data.

### 2025-xx-xx: Skills Need Semantic Routing
Tools alone aren't enough - need "USE WHEN" triggers to automatically route requests to appropriate capabilities (inspired by PAI).

## Patterns Discovered

### The 7-Phase Algorithm
Applies at every scale:
1. OBSERVE - Gather information
2. THINK - Generate hypotheses
3. PLAN - Sequence approach
4. BUILD - Define success criteria
5. EXECUTE - Do the work
6. VERIFY - Test against criteria (CRITICAL)
7. LEARN - Extract insights

### Graceful Degradation Pattern
```python
try:
    from advanced_feature import Feature
    FEATURE_AVAILABLE = True
except ImportError:
    FEATURE_AVAILABLE = False
    Feature = None
```

### PathManager Pattern
Never hardcode paths. Always use PathManager for cross-platform compatibility.

## Mistakes to Avoid

### Don't Skip VERIFY Phase
"It works on my machine" isn't verification. Always test.

### Don't Over-Engineer
Solve the problem at hand. Don't build frameworks for hypothetical futures.

### Don't Ignore Security
OWASP Top 10 applies everywhere. Sanitize inputs. Validate outputs.

---
*This file is updated as ALFRED learns from experience*

**Entity**: GxEum Technologies / CAMDAN Enterprizes
