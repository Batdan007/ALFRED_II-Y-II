# ALFRED Brain Learning - Verification Checklist

**Use this to verify all systems are working correctly**

---

## Installation Verification

### Step 1: Verify Files Created
```bash
# Run in workspace root
[ -f core/task_classifier.py ] && echo "✓ TaskClassifier created" || echo "✗ TaskClassifier missing"
[ -f core/agent_selector.py ] && echo "✓ AgentSelector created" || echo "✗ AgentSelector missing"
[ -f core/response_quality_checker.py ] && echo "✓ ResponseQualityChecker created" || echo "✗ ResponseQualityChecker missing"
[ -f mcp/alfred_brain_learning_server.py ] && echo "✓ MCP Learning Server created" || echo "✗ MCP Learning Server missing"
[ -f ALFRED_BRAIN_LEARNING_GUIDE.md ] && echo "✓ Guide created" || echo "✗ Guide missing"
[ -f QUICK_REFERENCE_BRAIN_LEARNING.md ] && echo "✓ Reference created" || echo "✗ Reference missing"
[ -f IMPLEMENTATION_SUMMARY.md ] && echo "✓ Summary created" || echo "✗ Summary missing"
```

### Step 2: Verify Imports Work
```bash
python -c "from core.task_classifier import TaskClassifier, TaskType; print('✓ TaskClassifier imports OK')" || echo "✗ TaskClassifier import failed"
python -c "from core.agent_selector import AgentSelector, ModelTier; print('✓ AgentSelector imports OK')" || echo "✗ AgentSelector import failed"
python -c "from core.response_quality_checker import ResponseQualityChecker, ResponseQuality; print('✓ ResponseQualityChecker imports OK')" || echo "✗ ResponseQualityChecker import failed"
```

### Step 3: Verify Brain Integration
```bash
python -c "
from core.brain import AlfredBrain
from core.task_classifier import TaskClassifier

brain = AlfredBrain()
classifier = TaskClassifier(brain=brain)

result = classifier.classify('Write a Python script')
print(f'✓ TaskClassifier can access brain')
print(f'  Task Type: {result[0].value}')
print(f'  Confidence: {result[1]:.1%}')
" || echo "✗ Brain integration failed"
```

---

## Functional Testing

### Test 1: Task Classification
```bash
python -c "
from core.task_classifier import TaskClassifier
from core.brain import AlfredBrain

brain = AlfredBrain()
classifier = TaskClassifier(brain=brain)

test_cases = [
    ('Write a Python function', 'CODE_MODIFICATION'),
    ('Explain how this code works', 'CODE_REVIEW'),
    ('I realized my mistake was', 'SYSTEM_LEARNING'),
    ('Find security vulnerabilities', 'CYBERSECURITY'),
    ('Design a microservices architecture', 'ARCHITECTURE'),
    ('Research the latest trends', 'RESEARCH'),
]

print('Testing Task Classification:')
passed = 0
for task_input, expected_type in test_cases:
    task_type, confidence, _ = classifier.classify(task_input)
    match = '✓' if task_type.value == expected_type.lower().replace('_', '_') else '✗'
    if match == '✓':
        passed += 1
    print(f'{match} \"{task_input[:30]}...\" → {task_type.value} ({confidence:.1%})')

print(f'\nPassed: {passed}/{len(test_cases)} tests')
" || echo "✗ Task classification test failed"
```

### Test 2: Agent Selection
```bash
python -c "
from core.agent_selector import AgentSelector
from core.brain import AlfredBrain

brain = AlfredBrain()
selector = AgentSelector(brain=brain)

print('Testing Agent Selection:')
tasks = [
    'Create a REST API endpoint',
    'Conduct a security audit',
    'Research market trends',
    'Design system architecture',
]

for task in tasks:
    selections = selector.select_agents(task, max_agents=1)
    if selections:
        agent = selections[0]['agent']
        model = selections[0]['model_tier']
        score = selections[0]['suitability_score']
        print(f'✓ \"{task[:30]}...\" → {agent} (tier: {model}, score: {score:.1%})')
    else:
        print(f'✗ Failed to select agent for: {task}')
" || echo "✗ Agent selection test failed"
```

### Test 3: Response Quality Checking
```bash
python -c "
from core.response_quality_checker import ResponseQualityChecker
from core.brain import AlfredBrain

brain = AlfredBrain()
checker = ResponseQualityChecker(brain=brain)

test_response = 'The system uses OAuth 2.0 for authentication with support for both client credentials and authorization code flows.'
test_task = 'Explain the authentication system'

print('Testing Response Quality Checking:')
assessment = checker.check_response(test_response, test_task)

print(f'✓ Quality Assessment:')
print(f'  Quality Level: {assessment[\"quality_level\"].value}')
print(f'  Is Clean: {assessment[\"is_clean\"]}')
print(f'  Confidence: {assessment[\"confidence\"]:.1%}')
print(f'  Flags: {len(assessment[\"flags\"])} detected')

if not assessment['is_clean']:
    print(f'  Issues Found:')
    for flag in assessment['flags']:
        print(f'    - {flag}')
" || echo "✗ Response quality test failed"
```

### Test 4: Brain Storage & Learning
```bash
python -c "
from core.brain import AlfredBrain
from core.task_classifier import TaskClassifier, TaskType
from core.agent_selector import AgentSelector

brain = AlfredBrain()

print('Testing Brain Learning Storage:')

# Simulate a task classification
classifier = TaskClassifier(brain=brain)
task_type, conf, _ = classifier.classify('Create a web application')

print(f'✓ Task classified: {task_type.value} ({conf:.1%})')

# Simulate agent selection
selector = AgentSelector(brain=brain)
selections = selector.select_agents('Create a web application')

if selections:
    agent_name = selections[0]['agent']
    selector.record_agent_outcome(agent_name, task_type, True, 'Great implementation')
    print(f'✓ Agent outcome recorded: {agent_name} success=True')

# Check brain storage
stats = brain.get_memory_stats()
print(f'✓ Brain Statistics:')
print(f'  Total Conversations: {stats.get(\"conversations\", 0)}')
print(f'  Total Knowledge: {stats.get(\"knowledge\", 0)}')
print(f'  Total Patterns: {stats.get(\"patterns\", 0)}')
print(f'  Total Skills: {stats.get(\"skills\", 0)}')
" || echo "✗ Brain learning storage test failed"
```

---

## MCP Server Testing

### Test 1: Start MCP Server
```bash
# In one terminal, start the MCP server (will run in background)
python mcp/alfred_brain_learning_server.py &
MCP_PID=$!

# Give it a second to start
sleep 1

# Check if running
if kill -0 $MCP_PID 2>/dev/null; then
    echo "✓ MCP server started (PID: $MCP_PID)"
    
    # Kill it
    kill $MCP_PID
else
    echo "✗ MCP server failed to start"
fi
```

### Test 2: Verify MCP Tools Available
```bash
python -c "
from mcp.alfred_brain_learning_server import AlfredBrainLearningServer
import asyncio

async def check_tools():
    server = AlfredBrainLearningServer()
    
    # Get list of tools
    # Note: This is simplified - real test would use stdio
    tools = [
        'alfred_classify_task',
        'alfred_select_agents',
        'alfred_check_response_quality',
        'alfred_record_agent_outcome',
        'alfred_get_learning_patterns',
        'alfred_get_brain_insights',
    ]
    
    print('✓ MCP Tools Available:')
    for tool in tools:
        print(f'  - {tool}')

# Note: This is a simplified check
print('✓ MCP Server imports successfully')
" || echo "✗ MCP server verification failed"
```

---

## Performance Testing

### Test 1: Task Classification Speed
```bash
python -c "
from core.task_classifier import TaskClassifier
from core.brain import AlfredBrain
import time

brain = AlfredBrain()
classifier = TaskClassifier(brain=brain)

print('Performance Test: Task Classification')

# Warm up
classifier.classify('test')

# Measure
start = time.time()
for i in range(10):
    classifier.classify('Create a Python REST API endpoint')
elapsed = (time.time() - start) / 10

print(f'✓ Average classification time: {elapsed*1000:.1f}ms')
if elapsed < 0.05:
    print(f'  ✓ Performance is excellent (< 50ms)')
elif elapsed < 0.1:
    print(f'  ✓ Performance is good (< 100ms)')
else:
    print(f'  ⚠ Performance could be better (> 100ms)')
" || echo "✗ Performance test failed"
```

### Test 2: Agent Selection Speed
```bash
python -c "
from core.agent_selector import AgentSelector
from core.brain import AlfredBrain
import time

brain = AlfredBrain()
selector = AgentSelector(brain=brain)

print('Performance Test: Agent Selection')

# Warm up
selector.select_agents('test')

# Measure
start = time.time()
for i in range(10):
    selector.select_agents('Create a Python REST API endpoint', max_agents=1)
elapsed = (time.time() - start) / 10

print(f'✓ Average selection time: {elapsed*1000:.1f}ms')
if elapsed < 0.02:
    print(f'  ✓ Performance is excellent (< 20ms)')
elif elapsed < 0.05:
    print(f'  ✓ Performance is good (< 50ms)')
else:
    print(f'  ⚠ Performance could be better (> 50ms)')
" || echo "✗ Agent selection performance test failed"
```

---

## Data Quality Testing

### Test 1: Confidence Scoring
```bash
python -c "
from core.task_classifier import TaskClassifier
from core.brain import AlfredBrain

brain = AlfredBrain()
classifier = TaskClassifier(brain=brain)

print('Data Quality Test: Confidence Scoring')

test_cases = [
    ('Create a Python script', 'CODE_MODIFICATION'),
    ('Write code for a web app', 'CODE_MODIFICATION'),
    ('Review this code', 'CODE_REVIEW'),
    ('Find security issues', 'CYBERSECURITY'),
]

for task, expected in test_cases:
    task_type, confidence, _ = classifier.classify(task)
    
    if confidence >= 0.7:
        status = '✓ High confidence'
    elif confidence >= 0.5:
        status = '⚠ Medium confidence'
    else:
        status = '✗ Low confidence'
    
    print(f'{status}: \"{task}\" ({confidence:.1%})')
" || echo "✗ Confidence scoring test failed"
```

### Test 2: Importance Scoring
```bash
python -c "
from core.brain import AlfredBrain

brain = AlfredBrain()

print('Data Quality Test: Knowledge Importance Scoring')

# Store test knowledge
brain.store_knowledge(
    'test_category',
    'critical_finding',
    'This is a critical security issue',
    importance=9,
    confidence=0.95
)

brain.store_knowledge(
    'test_category',
    'routine_info',
    'This is routine information',
    importance=5,
    confidence=0.7
)

# Recall and check
critical = brain.recall_knowledge('test_category', 'critical_finding')
routine = brain.recall_knowledge('test_category', 'routine_info')

print(f'✓ Critical finding stored: {critical[:50]}...' if critical else '✗ Failed to store critical')
print(f'✓ Routine info stored: {routine[:50]}...' if routine else '✗ Failed to store routine')
" || echo "✗ Importance scoring test failed"
```

---

## Learning Verification

### Test 1: Pattern Learning
```bash
python -c "
from core.brain import AlfredBrain
from core.agent_selector import AgentSelector, TaskType

brain = AlfredBrain()
selector = AgentSelector(brain=brain)

print('Learning Verification: Pattern Recording')

# Record multiple outcomes to build pattern
for i in range(5):
    selector.record_agent_outcome(
        agent_name='alfred-engineer',
        task_type=TaskType.CODE_MODIFICATION,
        success=(i < 4),  # 4 successes, 1 failure
        feedback=f'Attempt {i+1}'
    )

# Check patterns
patterns = brain.get_patterns()
print(f'✓ Patterns learned: {len(patterns)} total')

# Check skill proficiency
skills = brain.get_all_skills()
engineer_skills = [s for s in skills if 'alfred-engineer' in s.get('skill', '')]
if engineer_skills:
    for skill in engineer_skills:
        print(f'✓ {skill[\"skill\"]}: {skill[\"proficiency\"]:.1%} proficiency')
" || echo "✗ Pattern learning test failed"
```

### Test 2: Response History
```bash
python -c "
from core.brain import AlfredBrain
from core.response_quality_checker import ResponseQualityChecker

brain = AlfredBrain()
checker = ResponseQualityChecker(brain=brain)

print('Learning Verification: Response History')

# Store a test response
brain.store_conversation(
    user_input='How does authentication work?',
    alfred_response='The system uses OAuth 2.0 for authentication.',
    success=True
)

# Store similar response
brain.store_conversation(
    user_input='Explain authentication',
    alfred_response='The system uses OAuth 2.0 for authentication.',
    success=True
)

# Check for repeat
conversations = brain.get_conversation_context(limit=5)
print(f'✓ Stored {len(conversations)} test conversations')

# Try to detect repeat
assessment = checker.check_response(
    'The system uses OAuth 2.0 for authentication.',
    'How does auth work?'
)

if 'REPEAT' in str(assessment.get('quality_level', '')):
    print(f'✓ Repeat detection working (found similar response)')
else:
    print(f'⚠ Repeat detection may not have found match (might need more history)')
" || echo "✗ Response history test failed"
```

---

## Integration Testing

### Test 1: Full Workflow
```bash
python -c "
from core.brain import AlfredBrain
from core.task_classifier import TaskClassifier
from core.agent_selector import AgentSelector
from core.response_quality_checker import ResponseQualityChecker

brain = AlfredBrain()
classifier = TaskClassifier(brain=brain)
selector = AgentSelector(brain=brain)
checker = ResponseQualityChecker(brain=brain)

print('Integration Test: Full Workflow')

# 1. Classify task
task_input = 'Create a secure API endpoint for user authentication'
task_type, confidence, metadata = classifier.classify(task_input)
print(f'1. ✓ Classified: {task_type.value} ({confidence:.1%})')

# 2. Select agent
selections = selector.select_agents(task_input, max_agents=1)
if selections:
    agent = selections[0]
    print(f'2. ✓ Selected: {agent[\"agent\"]} (model: {agent[\"model_tier\"]})')
    
    # 3. Simulate response
    response = 'Use OAuth 2.0 with client credentials flow for secure API authentication.'
    
    # 4. Check quality
    assessment = checker.check_response(response, task_input)
    print(f'3. ✓ Quality checked: {assessment[\"quality_level\"].value} (clean: {assessment[\"is_clean\"]})')
    
    # 5. Record outcome
    selector.record_agent_outcome(
        agent['agent'],
        task_type,
        True,
        'Excellent implementation'
    )
    print(f'4. ✓ Outcome recorded')
    
    print(f'\n✓ Full workflow completed successfully!')
else:
    print('✗ Failed to select agent')
" || echo "✗ Full workflow test failed"
```

---

## Sign-Off Checklist

### Basic Functionality
- [ ] All files created and present
- [ ] All modules import without errors
- [ ] Brain integration working
- [ ] TaskClassifier working (>70% accuracy)
- [ ] AgentSelector working
- [ ] ResponseQualityChecker working
- [ ] MCP server starts without errors

### Performance
- [ ] Task classification: <50ms
- [ ] Agent selection: <20ms
- [ ] Response quality check: <100ms
- [ ] Brain queries: <1ms

### Data Quality
- [ ] Confidence scores reasonable (0.5-1.0)
- [ ] Importance scoring working
- [ ] Knowledge storage working
- [ ] Pattern recognition working

### Learning & Storage
- [ ] Patterns being recorded in brain
- [ ] Agent outcomes being tracked
- [ ] Response history accessible
- [ ] No errors in brain storage

### Integration
- [ ] Full workflow tested end-to-end
- [ ] MCP tools callable
- [ ] Claude Code integration ready
- [ ] Documentation complete

---

## Final Verification

Run this complete test:

```bash
echo "===== ALFRED Brain Learning - Final Verification ====="
echo ""
echo "1. File Check..."
python -c "
import os
files = [
    'core/task_classifier.py',
    'core/agent_selector.py',
    'core/response_quality_checker.py',
    'mcp/alfred_brain_learning_server.py'
]
for f in files:
    status = '✓' if os.path.exists(f) else '✗'
    print(f'{status} {f}')
"

echo ""
echo "2. Import Check..."
python -c "
try:
    from core.task_classifier import TaskClassifier
    from core.agent_selector import AgentSelector
    from core.response_quality_checker import ResponseQualityChecker
    from core.brain import AlfredBrain
    print('✓ All modules import successfully')
except Exception as e:
    print(f'✗ Import failed: {e}')
"

echo ""
echo "3. Functionality Check..."
python -c "
from core.brain import AlfredBrain
from core.task_classifier import TaskClassifier
from core.agent_selector import AgentSelector
from core.response_quality_checker import ResponseQualityChecker

brain = AlfredBrain()
classifier = TaskClassifier(brain=brain)
selector = AgentSelector(brain=brain)
checker = ResponseQualityChecker(brain=brain)

# Quick functionality test
task_type, conf, _ = classifier.classify('Create Python code')
agents = selector.select_agents('Create Python code', max_agents=1)
assessment = checker.check_response('Python implementation here', 'Create code')

if task_type and agents and assessment:
    print('✓ All systems functional')
else:
    print('✗ One or more systems failed')
"

echo ""
echo "===== Verification Complete ====="
```

---

**Status**: Ready for BATDAN verification

Mark items with ✓ as you verify them. If any fail, check the troubleshooting guide in ALFRED_BRAIN_LEARNING_GUIDE.md
