# PATENT SPECIFICATION
## CORTEX: Consolidated Organic Retrieval Through Exponential eXpiration
### 5-Layer Forgetting Memory Architecture for Artificial Intelligence Systems

---

## TITLE OF INVENTION

**Method and System for Bounded Memory Growth in Artificial Intelligence Through Active Forgetting Architecture**

---

## ABSTRACT

A method and system for managing memory in artificial intelligence systems through a multi-layer forgetting architecture. The invention implements a 5-layer memory system (Flash, Working, Short-Term, Long-Term, Archive) with configurable decay rates that actively forget low-value information while preserving and promoting high-value information. Unlike traditional memory systems that grow unbounded until failure, CORTEX ensures memory remains within defined capacity limits while improving overall memory quality through selective retention. The system includes importance evaluation, automatic promotion between layers, pattern detection, and consolidation processes that mirror human memory consolidation during sleep.

---

## FIELD OF INVENTION

The present invention relates to artificial intelligence memory systems, and more particularly to methods and systems for bounded memory growth through active forgetting mechanisms.

---

## BACKGROUND

### Problem Statement

Current AI memory systems suffer from critical limitations:

1. **Unbounded Growth**: Vector databases and embedding stores grow indefinitely until storage is exhausted or performance degrades
2. **No Intelligent Forgetting**: All information is retained equally regardless of value
3. **No Promotion Mechanism**: No pathway for important information to become more persistent
4. **Storage Exhaustion**: Systems eventually fail when storage limits are reached
5. **Performance Degradation**: Search performance decreases as corpus size increases

### Prior Art Limitations

| System | Limitation |
|--------|------------|
| Vector Databases (Pinecone, Weaviate) | Unbounded growth, no forgetting |
| Traditional Caches (LRU, LFU) | Single layer, no importance weighting |
| Sliding Window Memory | Loses old information regardless of value |
| Summarization Approaches | Lossy compression, no retrieval of originals |

### Need for Innovation

There exists a need for a memory architecture that:
- Bounds storage growth to defined limits
- Actively forgets low-value information
- Promotes high-value information to more persistent storage
- Improves memory quality over time through selective retention
- Mirrors human memory consolidation patterns

---

## SUMMARY OF INVENTION

CORTEX (Consolidated Organic Retrieval Through Exponential eXpiration) provides a 5-layer memory architecture with active forgetting:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CORTEX ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: FLASH MEMORY (< 30 seconds)                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Capacity: 100 items  │  Decay: 90%/minute                  │   │
│  │  All input enters here first                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼ Promotion (importance >= 3.0)        │
│  Layer 2: WORKING MEMORY (30 seconds - 30 minutes)                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Capacity: 500 items  │  Decay: 50%/hour                    │   │
│  │  Active context and recent important items                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼ Promotion (importance >= 5.0)        │
│  Layer 3: SHORT-TERM MEMORY (30 minutes - 24 hours)                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Capacity: 2,000 items  │  Decay: 25%/day                   │   │
│  │  Today's significant memories                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼ Promotion (importance >= 7.0)        │
│  Layer 4: LONG-TERM MEMORY (24+ hours)                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Capacity: 50,000 items  │  Decay: 5%/month                 │   │
│  │  Persistent knowledge store                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼ Archival (rarely accessed)           │
│  Layer 5: ARCHIVE (Compressed)                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Capacity: 100,000 items  │  Decay: 1%/year                 │   │
│  │  Compressed summaries of archived content                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  TOTAL BOUNDED CAPACITY: 152,600 items (NEVER EXCEEDED)            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## DETAILED DESCRIPTION

### 1. Memory Layer Structure

Each layer is defined by:

```python
@dataclass
class LayerConfig:
    max_capacity: int      # Maximum items in layer
    decay_rate: float      # Percentage decay per time unit
    decay_unit: str        # 'minute', 'hour', 'day', 'month', 'year'
    promotion_threshold: float  # Importance score needed for promotion
```

**Layer Configurations:**

| Layer | Capacity | Decay Rate | Decay Unit | Promotion Threshold |
|-------|----------|------------|------------|---------------------|
| Flash | 100 | 90% | minute | 3.0 |
| Working | 500 | 50% | hour | 5.0 |
| Short-Term | 2,000 | 25% | day | 7.0 |
| Long-Term | 50,000 | 5% | month | 8.0 |
| Archive | 100,000 | 1% | year | N/A |

### 2. Memory Item Structure

Each memory item contains:

```python
@dataclass
class MemoryItem:
    id: str                           # Unique identifier
    content: str                      # Memory content
    layer: MemoryLayer                # Current layer
    importance: float                 # 1-10 importance score
    confidence: float                 # 0.0-1.0 confidence score
    access_count: int                 # Retrieval count
    created_at: datetime              # Creation timestamp
    last_accessed: datetime           # Last access timestamp
    promoted_at: Optional[datetime]   # Promotion timestamp
    keywords: List[str]               # Extracted keywords
    topic: Optional[str]              # Topic category
    source: str                       # Origin of memory
    metadata: Dict[str, Any]          # Additional data
```

### 3. Importance Evaluation System

**Quick Evaluation (for Flash layer):**
- Base score: 5.0 (middle importance)
- High importance markers boost score (+1.0 each): important, critical, urgent, remember, password, deadline, meeting, error, bug
- Low importance markers reduce score (-0.5 each): weather, hello, thanks, okay, test
- Length bonus: +0.5 for >200 chars, +0.5 for >500 chars
- Question bonus: +0.5 if contains "?"

**Deep Evaluation (for promotion decisions):**
- Context relevance: +2.0 max based on word overlap with recent context
- Access frequency boost: +0.2 per access, max +2.0
- Final score clamped to 1.0-10.0 range

### 4. Promotion Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROMOTION ALGORITHM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FOR each item in current_layer:                               │
│                                                                 │
│    1. Calculate age = now - promoted_at (or created_at)        │
│                                                                 │
│    2. IF age > layer.max_age:                                  │
│         IF item.importance >= layer.promotion_threshold         │
│            OR item.access_count > access_threshold:            │
│              → PROMOTE to next layer                           │
│         ELSE:                                                   │
│              → FORGET (remove from memory)                     │
│                                                                 │
│    3. IF layer.count > layer.max_capacity:                     │
│         → Remove lowest importance items                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Decay Calculation

Memory strength decays over time:

```python
def calculate_strength(item, config):
    age_in_units = get_age_in_units(item, config.decay_unit)
    decay_factor = config.decay_rate ** age_in_units
    strength = item.importance * decay_factor
    return strength
```

Items with strength < 1.0 are candidates for forgetting.

### 6. Consolidation Process (Sleep-like)

Periodic consolidation (every hour) performs:

1. **Promote high-access items**: Short-term items with importance >= 7 or access_count > 5 → Long-term
2. **Archive stale items**: Long-term items not accessed in 365 days with importance < 5 → Archive
3. **Pattern detection**: Cluster similar items for ULTRATHUNK compression
4. **Index optimization**: Rebuild database indexes for performance

### 7. Archival Compression

When items move to Archive layer:
- Content truncated to 200 characters with "..." suffix
- Confidence reduced by 50%
- Keywords reduced to top 5
- Original ID preserved in metadata
- Original item deleted from source layer

---

## CLAIMS

### Independent Claims

**Claim 1.** A computer-implemented method for managing memory in an artificial intelligence system with bounded growth, comprising:

(a) receiving information into a **first memory layer** (Flash) with a first capacity limit and a first decay rate;

(b) evaluating an **importance score** for the received information based on content analysis;

(c) **promoting** information that exceeds an importance threshold from the first layer to a **second memory layer** (Working) with a second capacity limit and a second decay rate lower than the first;

(d) **forgetting** information that does not meet the importance threshold and exceeds a maximum age;

(e) repeating steps (c) and (d) through subsequent memory layers (Short-Term, Long-Term, Archive), wherein each subsequent layer has:
   - a higher capacity limit than the previous layer;
   - a lower decay rate than the previous layer;
   - a higher importance threshold for promotion;

(f) **bounding total memory** by enforcing capacity limits at each layer and removing lowest-importance items when capacity is exceeded.

---

**Claim 2.** A 5-layer memory architecture for artificial intelligence systems, comprising:

(a) a **Flash memory layer** configured to:
   - capture all incoming information;
   - store up to 100 items;
   - apply 90% decay per minute;
   - promote items with importance >= 3.0 to working memory;

(b) a **Working memory layer** configured to:
   - maintain active context;
   - store up to 500 items;
   - apply 50% decay per hour;
   - promote items with importance >= 5.0 to short-term memory;

(c) a **Short-term memory layer** configured to:
   - store significant daily memories;
   - store up to 2,000 items;
   - apply 25% decay per day;
   - promote items with importance >= 7.0 to long-term memory;

(d) a **Long-term memory layer** configured to:
   - persist important knowledge;
   - store up to 50,000 items;
   - apply 5% decay per month;
   - archive rarely-accessed items;

(e) an **Archive layer** configured to:
   - store compressed summaries;
   - store up to 100,000 items;
   - apply 1% decay per year;

wherein the total capacity across all layers is bounded and never exceeded.

---

**Claim 3.** A method for importance-based memory evaluation comprising:

(a) analyzing incoming content for **high-importance markers** including urgency indicators, personal significance markers, and error-related terms;

(b) analyzing incoming content for **low-importance markers** including greetings, acknowledgments, and routine queries;

(c) calculating a **base importance score** adjusted by marker presence;

(d) applying **context relevance scoring** based on overlap with recent memories;

(e) applying **access frequency boosting** for frequently retrieved items;

(f) clamping the final score to a defined range (1.0-10.0);

wherein the importance score determines promotion eligibility and forgetting priority.

---

**Claim 4.** A consolidation method for AI memory systems comprising:

(a) periodically executing consolidation during low-activity periods;

(b) **promoting** high-access short-term items to long-term storage based on access count thresholds;

(c) **archiving** long-term items that have not been accessed within a defined period and fall below an importance threshold;

(d) **detecting patterns** across similar memory items for compression;

(e) **optimizing indexes** for improved retrieval performance;

wherein the consolidation process mirrors human memory consolidation during sleep.

---

### Dependent Claims

**Claim 5.** The method of claim 1, wherein the importance score is calculated using a weighted combination of:
- content marker analysis;
- content length normalization;
- question presence detection;
- context relevance scoring.

**Claim 6.** The method of claim 1, wherein promotion decisions additionally consider access frequency, promoting items with high access counts regardless of importance score.

**Claim 7.** The architecture of claim 2, wherein the Flash and Working layers are maintained in RAM for sub-millisecond access, while Short-Term, Long-Term, and Archive layers are persisted to SQLite database.

**Claim 8.** The architecture of claim 2, wherein each memory item includes:
- unique identifier;
- content string;
- current layer designation;
- importance score (1-10);
- confidence score (0.0-1.0);
- access count;
- creation timestamp;
- last access timestamp;
- promotion timestamp;
- extracted keywords;
- topic category.

**Claim 9.** The method of claim 3, wherein high-importance markers include: "important", "critical", "urgent", "remember", "never forget", "password", "deadline", "meeting", "birthday", "anniversary", "error", "bug", "fix", "todo".

**Claim 10.** The method of claim 3, wherein low-importance markers include: "weather", "hello", "hi", "thanks", "okay", "sure", "maybe", "test".

**Claim 11.** The method of claim 4, wherein consolidation includes pattern detection that:
- clusters items with >50% word overlap;
- extracts common keywords;
- creates pattern summaries for ULTRATHUNK compression.

**Claim 12.** The architecture of claim 2, wherein archive compression includes:
- truncating content to 200 characters;
- reducing confidence by 50%;
- limiting keywords to top 5;
- preserving original ID in metadata.

**Claim 13.** The method of claim 1, wherein decay is calculated as:
`strength = importance * (decay_rate ^ age_in_time_units)`
and items with strength below 1.0 are candidates for forgetting.

**Claim 14.** The architecture of claim 2, wherein the total bounded capacity is 152,600 items across all layers, and this limit is never exceeded regardless of input volume.

---

## CLAIM DEPENDENCY CHART

```
Claim 1 (Bounded Memory Method - Independent)
  ├── Claim 5 (Importance calculation details)
  ├── Claim 6 (Access frequency consideration)
  └── Claim 13 (Decay calculation formula)

Claim 2 (5-Layer Architecture - Independent)
  ├── Claim 7 (RAM vs SQLite storage)
  ├── Claim 8 (Memory item structure)
  ├── Claim 12 (Archive compression)
  └── Claim 14 (Total bounded capacity)

Claim 3 (Importance Evaluation - Independent)
  ├── Claim 9 (High-importance markers)
  └── Claim 10 (Low-importance markers)

Claim 4 (Consolidation Method - Independent)
  └── Claim 11 (Pattern detection details)
```

---

## CLAIM SUMMARY

| Type | Count | Description |
|------|-------|-------------|
| Independent | 4 | Core innovations |
| Dependent | 10 | Specific implementations |
| **Total** | **14** | Full claim set |

---

## IMPLEMENTATION

**Primary Implementation File:** `core/cortex.py`

**Key Classes:**
- `MemoryLayer` - Enum defining 5 layers
- `MemoryItem` - Memory unit structure
- `LayerConfig` - Layer configuration
- `ImportanceEvaluator` - Importance scoring
- `PatternDetector` - Pattern detection for compression
- `CORTEX` - Main memory management class

**Database Schema:**
```sql
CREATE TABLE cortex_memory (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    layer TEXT NOT NULL,
    importance REAL DEFAULT 5.0,
    confidence REAL DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    last_accessed TEXT NOT NULL,
    promoted_at TEXT,
    keywords TEXT,
    topic TEXT,
    source TEXT DEFAULT 'input',
    metadata TEXT
);
```

---

## NOVELTY STATEMENT

No prior art combines:
1. Multi-layer memory with distinct decay rates per layer
2. Importance-based promotion between layers
3. Active forgetting of low-value information
4. Bounded total capacity that is never exceeded
5. Consolidation process mirroring human sleep memory consolidation
6. Access frequency boosting for retrieval-based importance

CORTEX is the first AI memory system to implement human-like forgetting as a feature rather than a bug.

---

**Document Version**: 1.0
**Draft Date**: January 8, 2026
**Author**: Daniel J Rita (BATDAN)
**Entity**: GxEum Technologies / CAMDAN Enterprizes
**Status**: READY FOR FILING
