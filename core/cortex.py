"""
CORTEX: Consolidated Organic Retrieval Through Exponential eXpiration

The Forgetting Brain - A 5-layer memory architecture with active forgetting.
"What you forget is as important as what you remember."

Patent Status: TO BE FILED Q1 2025
Author: Daniel J Rita (BATDAN)
Copyright: GxEum Technologies / CAMDAN Enterprizes

PATENT PENDING - DO NOT DISTRIBUTE
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import math

# Graceful degradation for optional dependencies
try:
    from core.path_manager import PathManager
    PATHMANAGER_AVAILABLE = True
except ImportError:
    PATHMANAGER_AVAILABLE = False


class MemoryLayer(Enum):
    """The 5 layers of CORTEX memory."""
    FLASH = "flash"           # < 30 seconds, 90% decay/min
    WORKING = "working"       # 30s - 30min, 50% decay/hour
    SHORT_TERM = "short_term" # 30min - 24h, 25% decay/day
    LONG_TERM = "long_term"   # 24h+, 5% decay/month
    ARCHIVE = "archive"       # Compressed, 1% decay/year


@dataclass
class MemoryItem:
    """A single unit of memory in CORTEX."""
    id: str
    content: str
    layer: MemoryLayer
    importance: float = 5.0        # 1-10 scale
    confidence: float = 0.5        # 0.0-1.0
    access_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    promoted_at: Optional[datetime] = None
    keywords: List[str] = field(default_factory=list)
    topic: Optional[str] = None
    source: str = "input"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'content': self.content,
            'layer': self.layer.value,
            'importance': self.importance,
            'confidence': self.confidence,
            'access_count': self.access_count,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'promoted_at': self.promoted_at.isoformat() if self.promoted_at else None,
            'keywords': self.keywords,
            'topic': self.topic,
            'source': self.source,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        return cls(
            id=data['id'],
            content=data['content'],
            layer=MemoryLayer(data['layer']),
            importance=data.get('importance', 5.0),
            confidence=data.get('confidence', 0.5),
            access_count=data.get('access_count', 0),
            created_at=datetime.fromisoformat(data['created_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            promoted_at=datetime.fromisoformat(data['promoted_at']) if data.get('promoted_at') else None,
            keywords=data.get('keywords', []),
            topic=data.get('topic'),
            source=data.get('source', 'input'),
            metadata=data.get('metadata', {})
        )


@dataclass
class LayerConfig:
    """Configuration for a memory layer."""
    max_capacity: int
    decay_rate: float      # Percentage decay per time unit
    decay_unit: str        # 'minute', 'hour', 'day', 'month', 'year'
    promotion_threshold: float


# Layer configurations - The heart of CORTEX
LAYER_CONFIGS = {
    MemoryLayer.FLASH: LayerConfig(
        max_capacity=100,
        decay_rate=0.90,      # 90% decay per minute
        decay_unit='minute',
        promotion_threshold=3.0
    ),
    MemoryLayer.WORKING: LayerConfig(
        max_capacity=500,
        decay_rate=0.50,      # 50% decay per hour
        decay_unit='hour',
        promotion_threshold=5.0
    ),
    MemoryLayer.SHORT_TERM: LayerConfig(
        max_capacity=2000,
        decay_rate=0.25,      # 25% decay per day
        decay_unit='day',
        promotion_threshold=7.0
    ),
    MemoryLayer.LONG_TERM: LayerConfig(
        max_capacity=50000,
        decay_rate=0.05,      # 5% decay per month
        decay_unit='month',
        promotion_threshold=8.0
    ),
    MemoryLayer.ARCHIVE: LayerConfig(
        max_capacity=100000,
        decay_rate=0.01,      # 1% decay per year
        decay_unit='year',
        promotion_threshold=10.0  # Never promotes from archive
    )
}


class ImportanceEvaluator:
    """Evaluates importance of incoming information."""

    # Keywords that boost importance
    HIGH_IMPORTANCE_MARKERS = [
        'important', 'critical', 'urgent', 'remember', 'never forget',
        'always', 'password', 'key', 'secret', 'deadline', 'meeting',
        'birthday', 'anniversary', 'error', 'bug', 'fix', 'todo'
    ]

    LOW_IMPORTANCE_MARKERS = [
        'weather', 'hello', 'hi', 'thanks', 'okay', 'ok', 'sure',
        'maybe', 'perhaps', 'test', 'testing'
    ]

    def quick_evaluate(self, content: str) -> float:
        """Quick importance evaluation for flash memory."""
        content_lower = content.lower()
        score = 5.0  # Default middle importance

        # Boost for high importance markers
        for marker in self.HIGH_IMPORTANCE_MARKERS:
            if marker in content_lower:
                score += 1.0

        # Reduce for low importance markers
        for marker in self.LOW_IMPORTANCE_MARKERS:
            if marker in content_lower:
                score -= 0.5

        # Length bonus (longer = potentially more important)
        if len(content) > 200:
            score += 0.5
        if len(content) > 500:
            score += 0.5

        # Question bonus (questions often important)
        if '?' in content:
            score += 0.5

        return max(1.0, min(10.0, score))

    def deep_evaluate(self, item: MemoryItem, context: List[MemoryItem]) -> float:
        """Deep importance evaluation with context awareness."""
        base_score = self.quick_evaluate(item.content)

        # Context relevance boost
        if context:
            relevance = self._calculate_context_relevance(item, context)
            base_score += relevance * 2.0

        # Access frequency boost
        if item.access_count > 0:
            base_score += min(2.0, item.access_count * 0.2)

        return max(1.0, min(10.0, base_score))

    def _calculate_context_relevance(self, item: MemoryItem, context: List[MemoryItem]) -> float:
        """Calculate how relevant item is to current context."""
        if not context:
            return 0.0

        item_words = set(item.content.lower().split())
        context_words = set()
        for ctx in context[-5:]:  # Last 5 context items
            context_words.update(ctx.content.lower().split())

        if not item_words or not context_words:
            return 0.0

        overlap = len(item_words & context_words)
        return min(1.0, overlap / 10.0)


class PatternDetector:
    """Detects patterns in memory clusters for ULTRATHUNK compression."""

    def detect(self, items: List[MemoryItem]) -> Optional[MemoryItem]:
        """Detect a pattern from a cluster of similar items."""
        if len(items) < 3:
            return None

        # Extract common elements
        all_words = []
        for item in items:
            all_words.extend(item.content.lower().split())

        # Find frequently occurring words
        word_freq = {}
        for word in all_words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1

        # Words appearing in >50% of items are pattern candidates
        threshold = len(items) * 0.5
        pattern_words = [w for w, c in word_freq.items() if c >= threshold]

        if len(pattern_words) < 2:
            return None

        # Create pattern memory
        pattern_content = f"[PATTERN] {' '.join(sorted(pattern_words)[:10])}"
        pattern_id = hashlib.md5(pattern_content.encode()).hexdigest()[:12]

        return MemoryItem(
            id=f"PTN-{pattern_id}",
            content=pattern_content,
            layer=MemoryLayer.SHORT_TERM,
            importance=8.0,  # Patterns are high importance
            confidence=len(items) / 10.0,  # More items = higher confidence
            keywords=pattern_words[:10],
            topic=items[0].topic if items else None,
            source='pattern_detection',
            metadata={'source_count': len(items), 'source_ids': [i.id for i in items]}
        )


class CORTEX:
    """
    CORTEX: The Forgetting Brain

    A 5-layer memory architecture that implements active forgetting
    to bound storage growth while improving memory quality.

    Layers:
    1. Flash (seconds) - Captures everything, 90% decay/min
    2. Working (minutes) - Active context, 50% decay/hour
    3. Short-Term (hours) - Today's memories, 25% decay/day
    4. Long-Term (days+) - Permanent store, 5% decay/month
    5. Archive (compressed) - Summaries only, 1% decay/year

    Patent Pending - GxEum Technologies / CAMDAN Enterprizes
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize CORTEX memory system."""
        if db_path:
            self.db_path = db_path
        elif PATHMANAGER_AVAILABLE:
            self.db_path = str(PathManager.DATA_DIR / "cortex_memory.db")
        else:
            self.db_path = "cortex_memory.db"

        self.importance_evaluator = ImportanceEvaluator()
        self.pattern_detector = PatternDetector()

        # In-memory caches for fast layers
        self._flash: List[MemoryItem] = []
        self._working: Dict[str, MemoryItem] = {}

        self._init_database()
        self._last_consolidation = datetime.now()

    def _init_database(self):
        """Initialize SQLite database for persistent layers."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cortex_memory (
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
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cortex_layer
            ON cortex_memory(layer)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cortex_importance
            ON cortex_memory(importance DESC)
        ''')

        conn.commit()
        conn.close()

    def capture(self, content: str, importance: Optional[float] = None,
                topic: Optional[str] = None, metadata: Optional[Dict] = None) -> MemoryItem:
        """
        Capture new information into Flash memory.

        All input enters through Flash layer and is evaluated for promotion.
        """
        item_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

        if importance is None:
            importance = self.importance_evaluator.quick_evaluate(content)

        item = MemoryItem(
            id=f"MEM-{item_id}",
            content=content,
            layer=MemoryLayer.FLASH,
            importance=importance,
            topic=topic,
            metadata=metadata or {}
        )

        self._flash.append(item)

        # Enforce flash capacity
        config = LAYER_CONFIGS[MemoryLayer.FLASH]
        if len(self._flash) > config.max_capacity:
            self._flash = self._flash[-config.max_capacity:]

        return item

    def tick(self) -> Dict[str, int]:
        """
        Process memory decay and promotions.

        Call this periodically (e.g., every few seconds) to:
        1. Decay items in all layers
        2. Promote high-value items to next layer
        3. Archive/forget low-value items

        Returns stats on operations performed.
        """
        stats = {
            'promoted': 0,
            'forgotten': 0,
            'archived': 0
        }

        # Process Flash -> Working
        promoted = self._process_flash()
        stats['promoted'] += len(promoted)
        for item in promoted:
            self._add_to_working(item)

        # Process Working -> Short-Term
        promoted, forgotten = self._process_working()
        stats['promoted'] += len(promoted)
        stats['forgotten'] += len(forgotten)
        for item in promoted:
            self._persist_item(item, MemoryLayer.SHORT_TERM)

        # Periodic consolidation (every hour)
        if datetime.now() - self._last_consolidation > timedelta(hours=1):
            consolidation_stats = self._consolidate()
            stats['promoted'] += consolidation_stats.get('promoted', 0)
            stats['archived'] += consolidation_stats.get('archived', 0)
            self._last_consolidation = datetime.now()

        return stats

    def _process_flash(self) -> List[MemoryItem]:
        """Process flash memory - promote important items, forget the rest."""
        now = datetime.now()
        promoted = []
        remaining = []

        config = LAYER_CONFIGS[MemoryLayer.FLASH]
        max_age = timedelta(seconds=30)

        for item in self._flash:
            age = now - item.created_at

            # Too old - evaluate for promotion or forget
            if age > max_age:
                if item.importance >= config.promotion_threshold or item.access_count > 0:
                    item.layer = MemoryLayer.WORKING
                    item.promoted_at = now
                    promoted.append(item)
                # Else: forgotten (not added to remaining)
            else:
                remaining.append(item)

        self._flash = remaining
        return promoted

    def _add_to_working(self, item: MemoryItem):
        """Add item to working memory."""
        item.layer = MemoryLayer.WORKING
        self._working[item.id] = item

        # Enforce capacity
        config = LAYER_CONFIGS[MemoryLayer.WORKING]
        if len(self._working) > config.max_capacity:
            # Remove lowest importance items
            sorted_items = sorted(self._working.values(),
                                  key=lambda x: x.importance)
            for low_item in sorted_items[:len(self._working) - config.max_capacity]:
                del self._working[low_item.id]

    def _process_working(self) -> Tuple[List[MemoryItem], List[str]]:
        """Process working memory - promote or forget based on decay."""
        now = datetime.now()
        promoted = []
        forgotten = []
        remaining = {}

        config = LAYER_CONFIGS[MemoryLayer.WORKING]
        max_age = timedelta(minutes=30)

        for item_id, item in self._working.items():
            age = now - (item.promoted_at or item.created_at)
            age_hours = age.total_seconds() / 3600

            # Calculate strength with decay
            decay_factor = config.decay_rate ** age_hours
            strength = item.importance * decay_factor

            # Promotion criteria
            if item.importance >= config.promotion_threshold or item.access_count > 2:
                item.layer = MemoryLayer.SHORT_TERM
                item.promoted_at = now
                promoted.append(item)
            # Forgotten (too weak or too old)
            elif strength < 1.0 or age > max_age:
                forgotten.append(item_id)
            else:
                remaining[item_id] = item

        self._working = remaining
        return promoted, forgotten

    def _persist_item(self, item: MemoryItem, layer: MemoryLayer):
        """Persist item to database in specified layer."""
        item.layer = layer
        item.promoted_at = datetime.now()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO cortex_memory
            (id, content, layer, importance, confidence, access_count,
             created_at, last_accessed, promoted_at, keywords, topic, source, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.id,
            item.content,
            item.layer.value,
            item.importance,
            item.confidence,
            item.access_count,
            item.created_at.isoformat(),
            item.last_accessed.isoformat(),
            item.promoted_at.isoformat() if item.promoted_at else None,
            json.dumps(item.keywords),
            item.topic,
            item.source,
            json.dumps(item.metadata)
        ))

        conn.commit()
        conn.close()

    def _consolidate(self) -> Dict[str, int]:
        """
        Consolidation process - like sleep for AI memory.

        1. Promote high-access short-term items to long-term
        2. Archive rarely-accessed long-term items
        3. Detect patterns and create ULTRATHUNK candidates
        """
        stats = {'promoted': 0, 'archived': 0, 'patterns': 0}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Promote from short-term to long-term
        cursor.execute('''
            SELECT * FROM cortex_memory
            WHERE layer = ? AND (importance >= 7 OR access_count > 5)
        ''', (MemoryLayer.SHORT_TERM.value,))

        for row in cursor.fetchall():
            item = self._row_to_item(row)
            item.layer = MemoryLayer.LONG_TERM
            item.promoted_at = datetime.now()
            self._persist_item(item, MemoryLayer.LONG_TERM)
            stats['promoted'] += 1

        # Archive old, low-access long-term items
        cutoff = (datetime.now() - timedelta(days=365)).isoformat()
        cursor.execute('''
            SELECT * FROM cortex_memory
            WHERE layer = ? AND last_accessed < ? AND importance < 5
        ''', (MemoryLayer.LONG_TERM.value, cutoff))

        for row in cursor.fetchall():
            item = self._row_to_item(row)
            self._archive_item(item)
            stats['archived'] += 1

        conn.close()
        return stats

    def _archive_item(self, item: MemoryItem):
        """Compress and archive an item."""
        # Create compressed summary
        summary = item.content[:200] + "..." if len(item.content) > 200 else item.content

        archived = MemoryItem(
            id=f"ARC-{item.id}",
            content=f"[ARCHIVED] {summary}",
            layer=MemoryLayer.ARCHIVE,
            importance=item.importance,
            confidence=item.confidence * 0.5,  # Reduced confidence for archived
            keywords=item.keywords[:5],
            topic=item.topic,
            source='archive',
            metadata={'original_id': item.id, 'archived_at': datetime.now().isoformat()}
        )

        self._persist_item(archived, MemoryLayer.ARCHIVE)

        # Remove original
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cortex_memory WHERE id = ?', (item.id,))
        conn.commit()
        conn.close()

    def recall(self, query: str, limit: int = 10,
               min_importance: float = 0.0) -> List[MemoryItem]:
        """
        Recall memories matching a query.

        Searches all layers, boosting access count for retrieved items.
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Search in-memory layers first (fastest)
        for item in self._flash + list(self._working.values()):
            if self._matches_query(item, query_words) and item.importance >= min_importance:
                item.access_count += 1
                item.last_accessed = datetime.now()
                results.append(item)

        # Search persistent layers
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM cortex_memory
            WHERE importance >= ?
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        ''', (min_importance, limit * 3))  # Fetch extra for filtering

        for row in cursor.fetchall():
            item = self._row_to_item(row)
            if self._matches_query(item, query_words):
                item.access_count += 1
                item.last_accessed = datetime.now()

                # Update access in database
                cursor.execute('''
                    UPDATE cortex_memory
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), item.id))

                results.append(item)

        conn.commit()
        conn.close()

        # Sort by relevance (importance * recency)
        now = datetime.now()
        results.sort(key=lambda x: x.importance * (1.0 / max(1, (now - x.last_accessed).days + 1)),
                     reverse=True)

        return results[:limit]

    def _matches_query(self, item: MemoryItem, query_words: set) -> bool:
        """Check if item matches query words."""
        content_words = set(item.content.lower().split())
        keyword_set = set(item.keywords) if item.keywords else set()

        # Match if any query word appears in content or keywords
        return bool(query_words & (content_words | keyword_set))

    def _row_to_item(self, row) -> MemoryItem:
        """Convert database row to MemoryItem."""
        return MemoryItem(
            id=row[0],
            content=row[1],
            layer=MemoryLayer(row[2]),
            importance=row[3],
            confidence=row[4],
            access_count=row[5],
            created_at=datetime.fromisoformat(row[6]),
            last_accessed=datetime.fromisoformat(row[7]),
            promoted_at=datetime.fromisoformat(row[8]) if row[8] else None,
            keywords=json.loads(row[9]) if row[9] else [],
            topic=row[10],
            source=row[11] or 'input',
            metadata=json.loads(row[12]) if row[12] else {}
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get CORTEX memory statistics."""
        stats = {
            'flash_count': len(self._flash),
            'working_count': len(self._working),
            'layers': {}
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for layer in [MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM, MemoryLayer.ARCHIVE]:
            cursor.execute('''
                SELECT COUNT(*), AVG(importance), AVG(confidence)
                FROM cortex_memory WHERE layer = ?
            ''', (layer.value,))
            row = cursor.fetchone()
            stats['layers'][layer.value] = {
                'count': row[0] or 0,
                'avg_importance': round(row[1] or 0, 2),
                'avg_confidence': round(row[2] or 0, 2)
            }

        # Total storage bound calculation
        total = stats['flash_count'] + stats['working_count']
        for layer_stats in stats['layers'].values():
            total += layer_stats['count']

        stats['total_memories'] = total
        stats['storage_bound'] = sum(LAYER_CONFIGS[l].max_capacity for l in MemoryLayer)
        stats['utilization'] = round(total / stats['storage_bound'] * 100, 1)

        conn.close()
        return stats

    def forget(self, item_id: str) -> bool:
        """Explicitly forget a memory item."""
        # Check in-memory layers
        self._flash = [i for i in self._flash if i.id != item_id]
        if item_id in self._working:
            del self._working[item_id]
            return True

        # Check persistent layers
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cortex_memory WHERE id = ?', (item_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted


# CLI interface
if __name__ == "__main__":
    import sys

    cortex = CORTEX()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "stats":
            stats = cortex.get_stats()
            print("\n=== CORTEX Memory Statistics ===")
            print(f"Flash Layer: {stats['flash_count']} items")
            print(f"Working Memory: {stats['working_count']} items")
            for layer, layer_stats in stats['layers'].items():
                print(f"{layer}: {layer_stats['count']} items (avg importance: {layer_stats['avg_importance']})")
            print(f"\nTotal: {stats['total_memories']} / {stats['storage_bound']} ({stats['utilization']}% utilized)")

        elif command == "capture":
            if len(sys.argv) > 2:
                content = " ".join(sys.argv[2:])
                item = cortex.capture(content)
                print(f"Captured: {item.id} (importance: {item.importance})")
            else:
                print("Usage: python cortex.py capture <content>")

        elif command == "recall":
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                results = cortex.recall(query)
                print(f"\n=== Recall Results for '{query}' ===")
                for item in results:
                    print(f"[{item.layer.value}] {item.importance:.1f}: {item.content[:80]}...")
            else:
                print("Usage: python cortex.py recall <query>")

        elif command == "tick":
            stats = cortex.tick()
            print(f"Tick: {stats['promoted']} promoted, {stats['forgotten']} forgotten, {stats['archived']} archived")

        else:
            print("Commands: stats, capture, recall, tick")
    else:
        print("CORTEX - The Forgetting Brain")
        print("Commands: stats, capture <content>, recall <query>, tick")
