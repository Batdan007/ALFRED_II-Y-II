# ALFRED Brain Learning - Quick Reference Card

**For BATDAN: Fast lookup of new learning systems**

---

## Three Core Systems

| System | File | Purpose | Key Method |
|--------|------|---------|-----------|
| **TaskClassifier** | `core/task_classifier.py` | Detect task type | `.classify(task_input)` |
| **AgentSelector** | `core/agent_selector.py` | Choose agents | `.select_agents(task_input)` |
| **ResponseQualityChecker** | `core/response_quality_checker.py` | Verify responses | `.check_response(response_text, task_input)` |

---

## Task Types Recognized

```
CODE_MODIFICATION    | CODE_REVIEW        | SYSTEM_LEARNING      | CYBERSECURITY
ARCHITECTURE         | RESEARCH           | OPTIMIZATION         | DEBUGGING
DATA_ANALYSIS        | DOCUMENTATION      | UNKNOWN              |
```

---

## Agents Available

```
alfred-engineer      | alfred-researcher  | engineer             | researcher
architect            | pentester          | designer             |
```

---

## Model Tiers

```
HAIKU (fast)    →  Simple tasks (10-20x faster)
SONNET (balanced) → Standard implementation (RECOMMENDED)
OPUS (complex)   → Security, architecture, complex reasoning
```

---

## Response Quality Levels

```
VERIFIED             | LIKELY_ACCURATE  | HONEST_LIMITATION  | UNVERIFIED
SUSPICIOUS           | REPEAT           | CONTRADICTS        |
```

---

## Quick Usage

### 1. Classify Task
```python
from core.task_classifier import TaskClassifier
from core.brain import AlfredBrain

brain = AlfredBrain()
classifier = TaskClassifier(brain=brain)

task_type, confidence, metadata = classifier.classify(
    "Create Python API endpoint"
)
# Returns: (TaskType.CODE_MODIFICATION, 0.87, {...})
```

### 2. Select Agent
```python
from core.agent_selector import AgentSelector

selector = AgentSelector(brain=brain)
selections = selector.select_agents(
    "Create Python API endpoint",
    max_agents=1
)
# Returns: [{agent: "alfred-engineer", model_tier: "sonnet", ...}]
```

### 3. Check Response Quality
```python
from core.response_quality_checker import ResponseQualityChecker

checker = ResponseQualityChecker(brain=brain)
assessment = checker.check_response(
    response_text="The endpoint uses OAuth 2.0...",
    task_input="Explain authentication"
)
# Returns: {quality_level: "VERIFIED", is_clean: True, ...}
```

### 4. Record Outcome (Learning)
```python
selector.record_agent_outcome(
    agent_name="alfred-engineer",
    task_type=TaskType.CODE_MODIFICATION,
    success=True,
    feedback="Excellent implementation"
)
# Brain updates agent success rates
```

---

## MCP Tools in Claude Code

### Classify Task
```
Tool: alfred_classify_task
Inputs: task_input, context (optional)
Output: task_type, confidence, suggested_agents
```

### Select Agents
```
Tool: alfred_select_agents
Inputs: task_input, max_agents, allow_parallel
Output: [agent_name, model_tier, rationale]
```

### Check Response
```
Tool: alfred_check_response_quality
Inputs: response_text, task_input
Output: quality_level, is_clean, flags, improvements
```

### Record Outcome
```
Tool: alfred_record_agent_outcome
Inputs: agent_name, task_type, success, feedback
Output: confirmation
```

### Get Brain Insights
```
Tool: alfred_get_brain_insights
Inputs: insight_type (learning_velocity, confidence_levels, capability_growth, reliability)
Output: metrics showing ALFRED > stateless AI
```

---

## Brain Storage Location

| OS | Path |
|---|---|
| **Windows** | `C:/Drive/data/alfred_brain.db` |
| **macOS** | `~/Library/Application Support/Alfred/data/alfred_brain.db` |
| **Linux** | `~/.alfred/data/alfred_brain.db` |

---

## Key Facts About Learning

| Aspect | Details |
|--------|---------|
| **Repeat Prevention** | Similarity threshold = 75% |
| **Confidence Growth** | Improves with verification count |
| **Importance Scoring** | 1-10 scale (7+ = significant) |
| **Success Rate Calculation** | successes / total_attempts |
| **Agent Ranking** | 60% classifier + 40% historical success |

---

## Proving ALFRED is Learning

### Test 1: Repeat Prevention
```
Ask same question 5 times
→ ALFRED gives different angles each time (NOT repeat)
```

### Test 2: Agent Performance Growth
```python
skills = brain.get_all_skills()
agent_skills = [s for s in skills if 'agent' in s['skill']]
# Should see increasing proficiency over time
```

### Test 3: Task Classification Accuracy
```python
history = brain.search_knowledge("agentic_tasks", limit=20)
# Check if classifications match actual task types
```

### Test 4: Honest Limitations
```
Ask question about private/internal/secret info
→ Alfred says "I cannot verify this" instead of making up answer
```

---

## Common Patterns

### Pattern 1: Task → Agent → Quality Check → Record
```python
# Full workflow
task_type, conf, _ = classifier.classify(input)
agents = selector.select_agents(input, max_agents=1)
agent_name = agents[0]['agent']

response = generate_response(input)  # By agent

assessment = checker.check_response(response, input)
if assessment['is_clean']:
    selector.record_agent_outcome(agent_name, task_type, True)
    return response
else:
    # Improve and retry
    improved = improve_response(response, assessment['improvements'])
    return improved
```

### Pattern 2: Parallel Task Handling
```python
selections = selector.select_agents(
    task_input,
    max_agents=3,
    parallel=True
)
# Run all agents in parallel, merge results
```

### Pattern 3: Learning from Mistakes
```python
brain.record_mistake(
    error_type="agent_selection",
    description="Wrong agent chosen for security task",
    solution="Mark pentester success rate higher"
)
brain.mark_mistake_learned(mistake_id)
```

---

## Importance Scoring Guide

### Use These Values

| Value | Use For |
|-------|---------|
| **9-10** | Critical security findings, human-verified facts, system decisions |
| **7-8** | Important patterns, major task classifications, learned behaviors |
| **5-6** | Standard tasks, routine decisions, regular conversations |
| **3-4** | Minor observations, secondary information |
| **1-2** | Trivial data, testing, throwaway info |

### Confidence Scoring Guide

| Value | Meaning |
|-------|---------|
| **0.9-1.0** | Human-verified, 100% confident |
| **0.7-0.9** | High confidence, multiple sources agree |
| **0.5-0.7** | Moderate confidence, reasonable |
| **0.3-0.5** | Low confidence, uncertain |
| **0.0-0.3** | Very uncertain, needs research |

---

## Error Messages & Fixes

| Error | Fix |
|-------|-----|
| `ImportError: cannot import AlfredBrain` | Brain not initialized, check path |
| `No task history found` | First run? Add min_confidence=0.0 |
| `Low classification confidence (<50%)` | Task description too vague |
| `Agent performance not found` | Not enough outcomes recorded (need 3+) |
| `Response quality is SUSPICIOUS` | Check against brain knowledge |

---

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|---|
| **Task Classification Accuracy** | >80% | Check predicted vs actual |
| **Agent Success Rate** | >75% | `record_agent_outcome()` data |
| **Repeat Prevention Rate** | >90% | Query brain conversation history |
| **Honest Limitation Rate** | 100% | Manual review for fabrications |

---

## Files to Know

```
Core Learning System:
  core/task_classifier.py (520 lines)
  core/agent_selector.py (380 lines)
  core/response_quality_checker.py (400 lines)

MCP Integration:
  mcp/alfred_brain_learning_server.py (480 lines)

Brain:
  core/brain.py (3,044 lines) - THE SOURCE OF TRUTH

Documentation:
  ALFRED_BRAIN_LEARNING_GUIDE.md (comprehensive)
  .github/copilot-instructions.md (agent guidance)
```

---

## Next Commands

### Start Learning Today
```bash
# Run MCP server for Claude Code
python mcp/alfred_brain_learning_server.py

# Check brain health
python -c "
from core.brain import AlfredBrain
brain = AlfredBrain()
print(brain.get_memory_stats())
"

# View learned patterns
python -c "
from core.brain import AlfredBrain
brain = AlfredBrain()
patterns = brain.get_patterns(min_frequency=2)
for p in patterns[:5]:
    print(f'{p[\"type\"]}: {p[\"success_rate\"]:.1%} success')
"
```

---

## Remember

1. **ALFRED learns from outcomes** - Always record success/failure
2. **Brain > models** - Persistent memory beats stateless AI
3. **Honest > confident** - Better to say "I don't know" than fabricate
4. **Task type matters** - Different agents for different tasks
5. **Patterns emerge** - Learning takes repetition (5-10 examples)

---

**All systems operational. Brain learning in real-time.**

Last updated: December 10, 2025
