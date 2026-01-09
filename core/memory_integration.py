"""
Memory Integration - Deep integration between Brain, CORTEX, and ULTRATHUNK

Combines all three patent-pending memory systems into a unified architecture:
- AlfredBrain: Permanent 11-table SQLite store (Patent #1)
- CORTEX: 5-layer forgetting brain with decay (Patent #3)
- ULTRATHUNK: 640:1 generative compression (Patent #4)

Flow:
1. Input -> CORTEX Flash layer (immediate capture)
2. CORTEX promotes important items -> Brain knowledge table
3. CORTEX patterns -> ULTRATHUNK compression -> Brain patterns table
4. Brain queries can use CORTEX for fast recent recall

Author: Daniel J Rita (BATDAN)
Copyright: GxEum Technologies / CAMDAN Enterprizes

PATENT PENDING - DO NOT DISTRIBUTE
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

# Graceful imports
try:
    from core.brain import AlfredBrain
    BRAIN_AVAILABLE = True
except ImportError:
    AlfredBrain = None
    BRAIN_AVAILABLE = False

try:
    from core.cortex import CORTEX, MemoryLayer, MemoryItem
    CORTEX_AVAILABLE = True
except ImportError:
    CORTEX = None
    CORTEX_AVAILABLE = False

try:
    from core.ultrathunk import UltrathunkEngine, ThunkType
    ULTRATHUNK_AVAILABLE = True
except ImportError:
    UltrathunkEngine = None
    ULTRATHUNK_AVAILABLE = False


class UnifiedMemory:
    """
    Unified Memory System - Integrates Brain + CORTEX + ULTRATHUNK

    This is the recommended way to use all three memory systems together.

    Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                     UNIFIED MEMORY                          │
    ├─────────────────────────────────────────────────────────────┤
    │  INPUT ──► CORTEX (5 layers) ──► BRAIN (11 tables)         │
    │              │                        ▲                     │
    │              │   patterns             │ knowledge           │
    │              ▼                        │                     │
    │         ULTRATHUNK ──────────────────►│                     │
    │         (compression)                                       │
    └─────────────────────────────────────────────────────────────┘
    """

    def __init__(self, brain: Optional['AlfredBrain'] = None):
        """Initialize unified memory with optional existing brain."""
        # Initialize or use existing brain
        if brain:
            self.brain = brain
        elif BRAIN_AVAILABLE:
            self.brain = AlfredBrain()
        else:
            self.brain = None

        # Initialize CORTEX
        if CORTEX_AVAILABLE:
            self.cortex = CORTEX()
        else:
            self.cortex = None

        # Initialize ULTRATHUNK
        if ULTRATHUNK_AVAILABLE:
            self.ultrathunk = UltrathunkEngine()
        else:
            self.ultrathunk = None

        # Track pending consolidations
        self._pending_patterns: List[Dict] = []
        self._last_sync = datetime.now()
        self._sync_interval = timedelta(minutes=5)

        # Consolidation stats
        self.stats = {
            'syncs': 0,
            'knowledge_synced': 0,
            'patterns_compressed': 0,
            'thunks_created': 0
        }

    def capture(self, content: str, importance: Optional[float] = None,
                topic: Optional[str] = None, response: Optional[str] = None) -> Dict:
        """
        Capture new information into the unified memory system.

        Flow:
        1. Capture in CORTEX (fast, 5-layer processing)
        2. Store conversation in Brain (permanent record)
        3. Check for pattern emergence

        Args:
            content: User input or information to capture
            importance: Override importance (1-10)
            topic: Topic classification
            response: Alfred's response (for conversation storage)

        Returns:
            Capture result with IDs from all systems
        """
        result = {
            'cortex_id': None,
            'brain_id': None,
            'pattern_detected': False
        }

        # 1. Capture in CORTEX (immediate, with decay)
        if self.cortex:
            item = self.cortex.capture(content, importance=importance, topic=topic)
            result['cortex_id'] = item.id

            # Process decay/promotions
            tick_stats = self.cortex.tick()

            # Check if items were promoted to long-term
            if tick_stats['promoted'] > 0:
                self._sync_promoted_to_brain()

        # 2. Store in Brain (permanent)
        if self.brain and response:
            self.brain.store_conversation(
                user_input=content,
                alfred_response=response,
                success=True,
                topics=topic
            )

        # 3. Check for patterns and compress
        if self.cortex and self.ultrathunk:
            patterns = self._detect_and_compress_patterns(topic)
            if patterns:
                result['pattern_detected'] = True

        # 4. Periodic full sync
        if datetime.now() - self._last_sync > self._sync_interval:
            self.sync()

        return result

    def recall(self, query: str, limit: int = 10,
               use_cortex_first: bool = True) -> List[Dict]:
        """
        Recall information using both CORTEX (fast/recent) and Brain (permanent).

        Args:
            query: Search query
            limit: Maximum results
            use_cortex_first: Check CORTEX first for recent items

        Returns:
            Combined results from both systems
        """
        results = []
        seen_content = set()

        # 1. Check CORTEX first (fast, recent items)
        if use_cortex_first and self.cortex:
            cortex_results = self.cortex.recall(query, limit=limit)
            for item in cortex_results:
                if item.content not in seen_content:
                    results.append({
                        'source': 'cortex',
                        'layer': item.layer.value,
                        'content': item.content,
                        'importance': item.importance,
                        'confidence': item.confidence,
                        'recency': 'recent'
                    })
                    seen_content.add(item.content)

        # 2. Check Brain (permanent knowledge)
        if self.brain and len(results) < limit:
            # Search knowledge base
            brain_results = self.brain.search_knowledge(query, limit=limit - len(results))
            for item in brain_results:
                content = item.get('value', '')
                if content not in seen_content:
                    results.append({
                        'source': 'brain',
                        'layer': 'knowledge',
                        'content': content,
                        'importance': item.get('importance', 5),
                        'confidence': item.get('confidence', 0.5),
                        'recency': 'permanent'
                    })
                    seen_content.add(content)

        # 3. Check ULTRATHUNK for compressed patterns
        if self.ultrathunk and len(results) < limit:
            thunk_results = self.ultrathunk.find_matching_thunks(query)
            for thunk in thunk_results[:limit - len(results)]:
                generated = thunk.generate(query)
                if generated not in seen_content:
                    results.append({
                        'source': 'ultrathunk',
                        'layer': 'compressed',
                        'content': generated,
                        'importance': 8,  # Patterns are high importance
                        'confidence': thunk.confidence,
                        'recency': 'generated',
                        'compression_ratio': thunk.compression_ratio
                    })
                    seen_content.add(generated)

        return results[:limit]

    def sync(self) -> Dict[str, int]:
        """
        Synchronize all memory systems.

        Operations:
        1. Promote CORTEX long-term items to Brain knowledge
        2. Compress CORTEX patterns with ULTRATHUNK
        3. Store compressed thunks in Brain patterns table

        Returns:
            Sync statistics
        """
        sync_stats = {
            'knowledge_synced': 0,
            'patterns_compressed': 0,
            'thunks_created': 0
        }

        # 1. Sync CORTEX long-term to Brain knowledge
        if self.cortex and self.brain:
            sync_stats['knowledge_synced'] = self._sync_promoted_to_brain()

        # 2. Compress patterns and store
        if self.cortex and self.ultrathunk and self.brain:
            sync_stats['patterns_compressed'], sync_stats['thunks_created'] = \
                self._compress_and_store_patterns()

        self._last_sync = datetime.now()
        self.stats['syncs'] += 1
        self.stats['knowledge_synced'] += sync_stats['knowledge_synced']
        self.stats['patterns_compressed'] += sync_stats['patterns_compressed']
        self.stats['thunks_created'] += sync_stats['thunks_created']

        return sync_stats

    def _sync_promoted_to_brain(self) -> int:
        """Sync CORTEX long-term items to Brain knowledge table."""
        if not self.cortex or not self.brain:
            return 0

        synced = 0
        cortex_stats = self.cortex.get_stats()

        # Get long-term items from CORTEX
        long_term_items = self.cortex.recall("", limit=100, min_importance=7.0)

        for item in long_term_items:
            if item.layer in [MemoryLayer.LONG_TERM, MemoryLayer.ARCHIVE]:
                # Store in Brain's knowledge table
                self.brain.store_knowledge(
                    category="cortex_promoted",
                    key=item.id,
                    value=item.content,
                    source="cortex_sync",
                    confidence=item.confidence,
                    importance=int(item.importance)
                )
                synced += 1

        return synced

    def _detect_and_compress_patterns(self, topic: Optional[str] = None) -> List:
        """Detect patterns in CORTEX and compress with ULTRATHUNK."""
        if not self.cortex or not self.ultrathunk:
            return []

        patterns_found = []

        # Get recent items from short-term memory
        recent_items = self.cortex.recall("", limit=50)

        # Group by topic
        topic_groups: Dict[str, List] = {}
        for item in recent_items:
            item_topic = item.topic or "general"
            if item_topic not in topic_groups:
                topic_groups[item_topic] = []
            topic_groups[item_topic].append({
                'content': item.content,
                'importance': item.importance,
                'timestamp': item.created_at.isoformat()
            })

        # Compress each group with 3+ items
        for topic_name, items in topic_groups.items():
            if len(items) >= 3:
                thunk = self.ultrathunk.compress_and_store(items, ThunkType.PATTERN)
                if thunk:
                    patterns_found.append({
                        'topic': topic_name,
                        'thunk_id': thunk.id,
                        'items_compressed': len(items),
                        'compression_ratio': thunk.compression_ratio
                    })
                    self._pending_patterns.append({
                        'thunk': thunk,
                        'topic': topic_name
                    })

        return patterns_found

    def _compress_and_store_patterns(self) -> tuple:
        """Compress pending patterns and store in Brain."""
        if not self._pending_patterns or not self.brain:
            return 0, 0

        patterns_processed = 0
        thunks_stored = 0

        for pending in self._pending_patterns:
            thunk = pending['thunk']
            topic = pending['topic']

            # Store thunk metadata in Brain's patterns table
            # (Brain uses patterns table for behavioral learning)
            try:
                # Store as knowledge with special category
                self.brain.store_knowledge(
                    category="ultrathunk",
                    key=thunk.id,
                    value=json.dumps({
                        'name': thunk.name,
                        'type': thunk.thunk_type.value,
                        'trigger': thunk.trigger_pattern,
                        'template': thunk.generator_template,
                        'compression_ratio': thunk.compression_ratio,
                        'fire_count': thunk.fire_count,
                        'topic': topic
                    }),
                    source="ultrathunk_compression",
                    confidence=thunk.confidence,
                    importance=8  # Patterns are important
                )
                thunks_stored += 1
            except Exception as e:
                print(f"Error storing thunk: {e}")

            patterns_processed += 1

        # Clear pending
        self._pending_patterns = []

        return patterns_processed, thunks_stored

    def consolidate(self) -> Dict[str, Any]:
        """
        Full memory consolidation - like sleep for the AI.

        Operations:
        1. CORTEX consolidation (decay, promotion, archival)
        2. ULTRATHUNK pattern detection across all topics
        3. Brain knowledge optimization
        4. Full sync between systems

        Returns:
            Consolidation report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'cortex': {},
            'ultrathunk': {},
            'brain': {},
            'sync': {}
        }

        # 1. CORTEX consolidation
        if self.cortex:
            # Force consolidation cycle
            cortex_before = self.cortex.get_stats()
            self.cortex._consolidate()
            cortex_after = self.cortex.get_stats()

            report['cortex'] = {
                'before': cortex_before['total_memories'],
                'after': cortex_after['total_memories'],
                'archived': cortex_before['total_memories'] - cortex_after['total_memories']
            }

        # 2. ULTRATHUNK compression pass
        if self.ultrathunk:
            thunk_before = self.ultrathunk.get_stats()

            # Compress any pending patterns
            self._detect_and_compress_patterns()

            thunk_after = self.ultrathunk.get_stats()
            report['ultrathunk'] = {
                'thunks_before': thunk_before['total_thunks'],
                'thunks_after': thunk_after['total_thunks'],
                'compression_ratio': thunk_after['compression_ratio']
            }

        # 3. Brain consolidation
        if self.brain:
            brain_before = self.brain.get_memory_stats()
            self.brain.consolidate_memory()
            brain_after = self.brain.get_memory_stats()

            report['brain'] = {
                'conversations': brain_after['conversations'],
                'knowledge': brain_after['knowledge'],
                'patterns': brain_after['patterns']
            }

        # 4. Full sync
        report['sync'] = self.sync()

        return report

    def get_stats(self) -> Dict[str, Any]:
        """Get unified memory statistics."""
        stats = {
            'integration': self.stats.copy(),
            'systems': {
                'brain': None,
                'cortex': None,
                'ultrathunk': None
            }
        }

        if self.brain:
            stats['systems']['brain'] = self.brain.get_memory_stats()

        if self.cortex:
            stats['systems']['cortex'] = self.cortex.get_stats()

        if self.ultrathunk:
            stats['systems']['ultrathunk'] = self.ultrathunk.get_stats()

        # Calculate total storage
        total_items = 0
        if stats['systems']['brain']:
            total_items += stats['systems']['brain'].get('conversations', 0)
            total_items += stats['systems']['brain'].get('knowledge', 0)
        if stats['systems']['cortex']:
            total_items += stats['systems']['cortex'].get('total_memories', 0)
        if stats['systems']['ultrathunk']:
            total_items += stats['systems']['ultrathunk'].get('total_thunks', 0)

        stats['total_items'] = total_items

        return stats


# Convenience function for quick unified memory access
_unified_memory = None

def get_unified_memory(brain: Optional['AlfredBrain'] = None) -> UnifiedMemory:
    """Get or create the global unified memory instance."""
    global _unified_memory
    if _unified_memory is None:
        _unified_memory = UnifiedMemory(brain=brain)
    return _unified_memory


# CLI interface
if __name__ == "__main__":
    import sys

    unified = UnifiedMemory()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "stats":
            stats = unified.get_stats()
            print("\n=== Unified Memory Statistics ===")
            print(f"\nIntegration Stats:")
            print(f"  Syncs: {stats['integration']['syncs']}")
            print(f"  Knowledge synced: {stats['integration']['knowledge_synced']}")
            print(f"  Patterns compressed: {stats['integration']['patterns_compressed']}")
            print(f"  Thunks created: {stats['integration']['thunks_created']}")

            if stats['systems']['brain']:
                print(f"\nBrain (11-table):")
                print(f"  Conversations: {stats['systems']['brain'].get('conversations', 0)}")
                print(f"  Knowledge: {stats['systems']['brain'].get('knowledge', 0)}")

            if stats['systems']['cortex']:
                print(f"\nCORTEX (5-layer):")
                print(f"  Total memories: {stats['systems']['cortex'].get('total_memories', 0)}")
                print(f"  Utilization: {stats['systems']['cortex'].get('utilization', 0)}%")

            if stats['systems']['ultrathunk']:
                print(f"\nULTRATHUNK:")
                print(f"  Total thunks: {stats['systems']['ultrathunk'].get('total_thunks', 0)}")
                print(f"  Compression: {stats['systems']['ultrathunk'].get('compression_ratio', 0)}:1")

            print(f"\nTotal items across all systems: {stats['total_items']}")

        elif command == "sync":
            print("Synchronizing memory systems...")
            result = unified.sync()
            print(f"Sync complete:")
            print(f"  Knowledge synced: {result['knowledge_synced']}")
            print(f"  Patterns compressed: {result['patterns_compressed']}")
            print(f"  Thunks created: {result['thunks_created']}")

        elif command == "consolidate":
            print("Running full consolidation (this may take a moment)...")
            report = unified.consolidate()
            print(f"\nConsolidation Report:")
            print(json.dumps(report, indent=2))

        elif command == "capture":
            if len(sys.argv) > 2:
                content = " ".join(sys.argv[2:])
                result = unified.capture(content)
                print(f"Captured: {result}")
            else:
                print("Usage: python memory_integration.py capture <content>")

        elif command == "recall":
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                results = unified.recall(query)
                print(f"\n=== Recall Results for '{query}' ===")
                for r in results:
                    print(f"[{r['source']}/{r['layer']}] {r['content'][:80]}...")
            else:
                print("Usage: python memory_integration.py recall <query>")

        else:
            print("Commands: stats, sync, consolidate, capture, recall")
    else:
        print("Unified Memory - Brain + CORTEX + ULTRATHUNK Integration")
        print("Commands: stats, sync, consolidate, capture <content>, recall <query>")
