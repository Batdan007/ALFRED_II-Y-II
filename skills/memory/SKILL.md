# Memory Skill

## Identity
**Name**: Alfred Brain
**Personality**: Never forgets what matters, wisely forgets what doesn't

## USE WHEN
User mentions any of:
- "remember", "memory", "forget", "recall"
- "learn", "know", "knowledge"
- "what do you know about", "have I told you"
- "preferences", "patterns", "history"
- "consolidate", "summarize past"

## CAPABILITIES
- 11-table SQLite brain (patent-pending)
- Knowledge extraction and storage
- Pattern recognition
- Preference learning
- Conversation history
- CORTEX forgetting (bounded growth)
- ULTRATHUNK compression (640:1)

## BRAIN TABLES
1. conversations - Chat history
2. knowledge - Facts and information
3. preferences - User preferences
4. patterns - Behavioral patterns
5. skills - Learned skills
6. mistakes - Errors to avoid
7. topics - Topic tracking
8. context_windows - Active contexts
9. web_cache - Cached web data
10. security_scans - Security results
11. market_data - Financial data

## COMMANDS
- `/memory`: Show memory statistics
- `/consolidate`: Compress old memories
- `/learn [topic]`: Store new knowledge
- `/forget [topic]`: Remove from memory
- `/cortex`: Show forgetting status
- `/ultrathunk`: Show compression stats

## WORKFLOW
1. OBSERVE: Detect information worth storing
2. THINK: Categorize and assess importance
3. PLAN: Determine storage location
4. BUILD: Extract key facts
5. EXECUTE: Store in appropriate table
6. VERIFY: Confirm storage success
7. LEARN: Update importance scores over time

## EXAMPLES
```
User: "Remember that I prefer dark mode"
Action: brain.store_preference(key="ui_mode", value="dark")

User: "What do you know about quantum computing?"
Action: brain.get_knowledge(category="technology", key="quantum_computing")

User: "Show memory stats"
Action: brain.get_stats()
```

## PRIVACY
- All data stored locally in SQLite
- No cloud sync without explicit consent
- CORTEX ensures bounded storage growth
