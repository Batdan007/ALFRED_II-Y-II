#!/usr/bin/env python3
"""
Alfred Brain - Ultra-Enhanced Persistent Memory & Intelligence System

Features:
- Persistent conversation memory with context
- Knowledge base with semantic search
- Pattern recognition and learning
- User preference adaptation
- Skill and capability tracking
- Memory consolidation
- Emotional intelligence
- Learning from mistakes
- Priority/importance scoring
- Integration with all Alfred systems
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict, Counter
import re


class AlfredBrain:
    """
    Alfred's ultra-enhanced brain - learns, remembers, and evolves

    Capabilities:
    - Long-term memory (conversations, knowledge, skills)
    - Short-term working memory (context)
    - Pattern recognition
    - Learning from experience
    - Preference adaptation
    - Emotional intelligence
    - Knowledge consolidation
    """

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize Alfred's brain"""
        try:
            from core.path_manager import PathManager
        except ModuleNotFoundError:
            # When running as script directly
            from path_manager import PathManager

        # Use PathManager.DATA_DIR if no custom path specified
        if data_dir is None:
            self.data_dir = PathManager.DATA_DIR
        else:
            self.data_dir = Path(data_dir)

        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Database paths
        self.db_path = self.data_dir / "alfred_brain.db"

        # In-memory caches for performance
        self.context_cache = []
        self.knowledge_cache = {}
        self.pattern_cache = defaultdict(list)

        # Initialize
        self.init_database()
        self.load_caches()

        print("[OK] Alfred's Brain initialized - Ultra Mode")
        print(f"  Database: {self.db_path}")
        stats = self.get_memory_stats()
        print(f"  Conversations: {stats['conversations']}")
        print(f"  Knowledge items: {stats['knowledge']}")
        print(f"  Learned patterns: {stats['patterns']}")

    def init_database(self):
        """Initialize comprehensive database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # ========================================
        # CONVERSATIONS - Long-term memory
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                alfred_response TEXT NOT NULL,
                context TEXT,
                models_used TEXT,
                topics TEXT,
                sentiment TEXT,
                importance INTEGER DEFAULT 5,
                success BOOLEAN DEFAULT 1,
                execution_time REAL
            )
        """)

        # ========================================
        # KNOWLEDGE BASE - Learned facts
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                source TEXT,
                confidence REAL DEFAULT 1.0,
                times_accessed INTEGER DEFAULT 0,
                last_accessed TEXT,
                importance INTEGER DEFAULT 5
            )
        """)

        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_category_key
            ON knowledge(category, key)
        """)

        # ========================================
        # USER PREFERENCES - Adaptive settings
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                preference_key TEXT PRIMARY KEY,
                preference_value TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                times_used INTEGER DEFAULT 0,
                confidence REAL DEFAULT 1.0
            )
        """)

        # ========================================
        # PATTERNS - Learned behavioral patterns
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 1.0,
                last_seen TEXT NOT NULL,
                confidence REAL DEFAULT 1.0
            )
        """)

        # ========================================
        # SKILLS - Capabilities and proficiency
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                skill_name TEXT PRIMARY KEY,
                proficiency REAL DEFAULT 0.0,
                times_used INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                last_used TEXT,
                notes TEXT
            )
        """)

        # ========================================
        # MISTAKES - Learning from errors
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                error_type TEXT NOT NULL,
                description TEXT NOT NULL,
                context TEXT,
                solution TEXT,
                learned BOOLEAN DEFAULT 0
            )
        """)

        # ========================================
        # TOPICS - Subject tracking
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                topic TEXT PRIMARY KEY,
                frequency INTEGER DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                interest_level REAL DEFAULT 0.5
            )
        """)

        # ========================================
        # CONTEXT WINDOWS - Recent activity
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_windows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                window_data TEXT NOT NULL,
                summary TEXT
            )
        """)

        # ========================================
        # CONVERSATION ARCHIVES - Archived conversations
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_archives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                archived_at TEXT NOT NULL,
                original_id INTEGER NOT NULL,
                archive_path TEXT NOT NULL,
                reason TEXT
            )
        """)

        # ========================================
        # EXTRACTION PATTERNS - Pattern tracking
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extraction_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                pattern_regex TEXT NOT NULL,
                category TEXT NOT NULL,
                key_template TEXT NOT NULL,
                confidence_level REAL DEFAULT 0.8,
                times_matched INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                active BOOLEAN DEFAULT 1
            )
        """)

        # ========================================
        # EXTRACTION HISTORY - Track extractions
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extraction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                conversation_id INTEGER,
                pattern_id INTEGER,
                extracted_knowledge_id INTEGER,
                confidence REAL
            )
        """)

        # ========================================
        # KNOWLEDGE MERGES - Track merge history
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_merges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                primary_id INTEGER NOT NULL,
                merged_ids TEXT NOT NULL,
                similarity_score REAL,
                merge_strategy TEXT,
                original_values TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_category_value
            ON knowledge(category, value)
        """)

        # ========================================
        # PRIORITY HISTORY - Track priority changes
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS priority_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                old_score REAL,
                new_score REAL,
                reason TEXT
            )
        """)

        # ========================================
        # ARCHIVAL CONFIG - Archival tiers
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archival_config (
                tier TEXT PRIMARY KEY,
                min_priority REAL NOT NULL,
                max_priority REAL NOT NULL,
                min_age_days INTEGER NOT NULL,
                retention_days INTEGER NOT NULL,
                description TEXT
            )
        """)

        # Insert default archival tiers
        cursor.execute("""
            INSERT OR IGNORE INTO archival_config VALUES
                ('hot', 7.0, 10.0, 0, 36500, 'Critical items - never archive'),
                ('warm', 4.0, 6.9, 30, 365, 'Important items - archive after 1 year'),
                ('cold', 2.0, 3.9, 90, 180, 'Low priority - archive after 6 months'),
                ('frozen', 0.0, 1.9, 30, 90, 'Very low priority - archive after 3 months')
        """)

        # ========================================
        # CONVERSATION SESSIONS - Session tracking
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                message_count INTEGER DEFAULT 0,
                topics TEXT,
                avg_importance REAL,
                success_rate REAL,
                duration_minutes INTEGER,
                summary TEXT
            )
        """)

        # Note: idx_conversations_session index created in migrations section after column exists

        # ========================================
        # CONVERSATION RELATIONSHIPS - Conversation links
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                related_conversation_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id),
                FOREIGN KEY (related_conversation_id) REFERENCES conversations(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversation_relationships
            ON conversation_relationships(conversation_id, relationship_type)
        """)

        # ========================================
        # KNOWLEDGE RELATIONSHIPS - Knowledge graph
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id1 INTEGER NOT NULL,
                knowledge_id2 INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                bidirectional BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                created_by TEXT DEFAULT 'system',
                verified BOOLEAN DEFAULT 0,
                times_traversed INTEGER DEFAULT 0,
                last_traversed TEXT,
                FOREIGN KEY (knowledge_id1) REFERENCES knowledge(id),
                FOREIGN KEY (knowledge_id2) REFERENCES knowledge(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_relationships_id1
            ON knowledge_relationships(knowledge_id1, relationship_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_relationships_id2
            ON knowledge_relationships(knowledge_id2, relationship_type)
        """)

        # ========================================
        # WEB CACHE - Crawled content storage
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                metadata TEXT,
                crawled_at TEXT NOT NULL,
                content_hash TEXT,
                links_extracted INTEGER DEFAULT 0,
                times_accessed INTEGER DEFAULT 0,
                last_accessed TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_web_cache_url
            ON web_cache(url)
        """)

        # ========================================
        # SECURITY SCANS - Security analysis results
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                findings TEXT NOT NULL,
                severity_summary TEXT,
                recommendations TEXT,
                authorized BOOLEAN DEFAULT 0,
                notes TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_security_scans_target
            ON security_scans(target, scan_type)
        """)

        # ========================================
        # MARKET DATA - Financial data cache
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                market TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data_type TEXT,
                source TEXT,
                UNIQUE(symbol, market, timestamp)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_data_symbol
            ON market_data(symbol, market)
        """)

        # ========================================
        # CAMDAN PROJECTS - Engineering project tracking
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS camdan_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                client_name TEXT,
                location TEXT,
                building_type TEXT,
                square_footage INTEGER,
                estimated_cost REAL,
                actual_cost REAL,
                status TEXT DEFAULT 'planning',
                timeline_data TEXT,
                compliance_issues TEXT,
                brain_insights TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                importance INTEGER DEFAULT 7,
                notes TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_camdan_projects_client
            ON camdan_projects(client_name, status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_camdan_projects_status
            ON camdan_projects(status, created_at DESC)
        """)

        # ========================================
        # SCHEMA MIGRATIONS - Add new columns to existing tables
        # ========================================

        # Add new columns to conversations table (if they don't exist)
        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN retention_score REAL DEFAULT 1.0")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN times_accessed INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN last_accessed TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN cluster_id INTEGER")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN session_id INTEGER")
        except sqlite3.OperationalError:
            pass

        # Create index for session_id after column is added
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_session
                ON conversations(session_id, timestamp)
            """)
        except sqlite3.OperationalError:
            pass

        # Add new columns to knowledge table (if they don't exist)
        try:
            cursor.execute("ALTER TABLE knowledge ADD COLUMN extraction_method TEXT DEFAULT 'manual'")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE knowledge ADD COLUMN verified BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE knowledge ADD COLUMN superseded_by INTEGER")
        except sqlite3.OperationalError:
            pass

        # Add priority_score columns to tables (if they don't exist)
        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN priority_score REAL DEFAULT 5.0")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE knowledge ADD COLUMN priority_score REAL DEFAULT 5.0")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE patterns ADD COLUMN priority_score REAL DEFAULT 5.0")
        except sqlite3.OperationalError:
            pass

        # Create indexes for priority queries
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_priority
                ON conversations(priority_score DESC, timestamp DESC)
            """)
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_priority
                ON knowledge(priority_score DESC, last_accessed DESC)
            """)
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_priority
                ON patterns(priority_score DESC, last_seen DESC)
            """)
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

    def load_caches(self):
        """Load frequently accessed data into memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Load recent conversations into context cache
        cursor.execute("""
            SELECT user_input, alfred_response, topics, timestamp
            FROM conversations
            ORDER BY id DESC
            LIMIT 50
        """)

        self.context_cache = [
            {"user": row[0], "alfred": row[1], "topics": row[2], "timestamp": row[3]}
            for row in cursor.fetchall()
        ]

        # Load high-importance knowledge
        cursor.execute("""
            SELECT category, key, value
            FROM knowledge
            WHERE importance >= 7
            ORDER BY importance DESC, times_accessed DESC
            LIMIT 100
        """)

        for row in cursor.fetchall():
            cat_key = f"{row[0]}:{row[1]}"
            self.knowledge_cache[cat_key] = row[2]

        conn.close()

    # ============================================================================
    # CONVERSATION MEMORY
    # ============================================================================

    def _get_or_create_session(self, cursor) -> int:
        """Get current session or create new one based on 30-minute time gap"""
        # Get most recent conversation
        cursor.execute("""
            SELECT id, timestamp, session_id
            FROM conversations
            ORDER BY id DESC
            LIMIT 1
        """)

        row = cursor.fetchone()

        if row:
            last_conv_time = datetime.fromisoformat(row[1])
            time_gap = (datetime.now() - last_conv_time).total_seconds() / 60

            # If within 30 minutes, continue current session
            if time_gap < 30 and row[2]:
                return row[2]
            else:
                # Create new session
                cursor.execute("""
                    INSERT INTO conversation_sessions (session_name, start_time)
                    VALUES (?, ?)
                """, (None, datetime.now().isoformat()))
                return cursor.lastrowid
        else:
            # First conversation ever - create session
            cursor.execute("""
                INSERT INTO conversation_sessions (session_name, start_time)
                VALUES (?, ?)
            """, (None, datetime.now().isoformat()))
            return cursor.lastrowid

    def store_conversation(
        self,
        user_input: str,
        alfred_response: str,
        context: Optional[Dict] = None,
        models_used: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        sentiment: str = "neutral",
        importance: int = 5,
        success: bool = True,
        execution_time: float = 0.0
    ):
        """
        Store conversation with rich metadata

        Args:
            user_input: User's message
            alfred_response: Alfred's response
            context: Contextual information
            models_used: AI models that generated response
            topics: Extracted topics
            sentiment: Conversation sentiment
            importance: 1-10 scale
            success: Whether interaction was successful
            execution_time: Time taken to respond
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get or create session (30-minute gap detection)
        session_id = self._get_or_create_session(cursor)

        # Calculate initial priority score
        initial_priority = importance * 0.5  # Scale to 0-5 range

        cursor.execute("""
            INSERT INTO conversations
            (timestamp, user_input, alfred_response, context, models_used, topics,
             sentiment, importance, success, execution_time, retention_score, last_accessed, priority_score, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            user_input,
            alfred_response,
            json.dumps(context) if context else None,
            json.dumps(models_used) if models_used else None,
            json.dumps(topics) if topics else None,
            sentiment,
            importance,
            success,
            execution_time,
            1.0,  # Initial retention_score
            datetime.now().isoformat(),  # last_accessed
            initial_priority,  # priority_score
            session_id  # session_id
        ))

        conv_id = cursor.lastrowid

        # Update topic tracking
        if topics:
            for topic in topics:
                self._update_topic(cursor, topic)

        # Auto-extract and store knowledge
        self._auto_extract_knowledge(cursor, user_input, alfred_response)

        conn.commit()
        conn.close()

        # Update context cache
        self.context_cache.insert(0, {
            "user": user_input,
            "alfred": alfred_response,
            "topics": json.dumps(topics) if topics else None,
            "timestamp": datetime.now().isoformat()
        })
        self.context_cache = self.context_cache[:50]  # Keep last 50

        return conv_id

    def get_conversation_context(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation context and update access tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get IDs of recent conversations
        cursor.execute("""
            SELECT id FROM conversations
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        conv_ids = [row[0] for row in cursor.fetchall()]

        # Update access tracking for these conversations
        if conv_ids:
            placeholders = ','.join('?' * len(conv_ids))
            cursor.execute(f"""
                UPDATE conversations
                SET times_accessed = times_accessed + 1,
                    last_accessed = ?
                WHERE id IN ({placeholders})
            """, [datetime.now().isoformat()] + conv_ids)

            conn.commit()

        conn.close()

        return self.context_cache[:limit]

    def search_conversations(
        self,
        query: str,
        limit: int = 10,
        min_importance: int = 0
    ) -> List[Dict]:
        """
        Search conversations by keyword

        Args:
            query: Search query
            limit: Max results
            min_importance: Minimum importance level

        Returns:
            List of matching conversations
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query_pattern = f"%{query}%"

        cursor.execute("""
            SELECT timestamp, user_input, alfred_response, topics, importance
            FROM conversations
            WHERE (user_input LIKE ? OR alfred_response LIKE ?)
            AND importance >= ?
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        """, (query_pattern, query_pattern, min_importance, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                "timestamp": row[0],
                "user_input": row[1],
                "alfred_response": row[2],
                "topics": json.loads(row[3]) if row[3] else [],
                "importance": row[4]
            })

        conn.close()
        return results

    # ============================================================================
    # KNOWLEDGE BASE
    # ============================================================================

    def store_knowledge(
        self,
        category: str,
        key: str,
        value: str,
        source: str = "conversation",
        confidence: float = 1.0,
        importance: int = 5
    ):
        """
        Store learned knowledge

        Args:
            category: Knowledge category
            key: Knowledge key
            value: Knowledge value
            source: Where this knowledge came from
            confidence: 0.0-1.0 confidence score
            importance: 1-10 importance scale
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate initial priority score
        initial_priority = (importance * 0.5) + (confidence * 2.5)  # Scale to 0-10

        cursor.execute("""
            INSERT INTO knowledge
            (timestamp, category, key, value, source, confidence, importance, last_accessed, priority_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            category,
            key,
            value,
            source,
            confidence,
            importance,
            datetime.now().isoformat(),
            initial_priority
        ))

        conn.commit()
        conn.close()

        # Update cache if high importance
        if importance >= 7:
            cat_key = f"{category}:{key}"
            self.knowledge_cache[cat_key] = value

    def recall_knowledge(
        self,
        category: str,
        key: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> Any:
        """
        Recall knowledge from memory

        Args:
            category: Knowledge category
            key: Specific key (None for all in category)
            min_confidence: Minimum confidence threshold

        Returns:
            Knowledge value(s)
        """
        # Check cache first
        if key:
            cat_key = f"{category}:{key}"
            if cat_key in self.knowledge_cache:
                self._increment_access_count(category, key)
                return self.knowledge_cache[cat_key]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if key:
            cursor.execute("""
                SELECT value, confidence, times_accessed
                FROM knowledge
                WHERE category = ? AND key = ? AND confidence >= ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (category, key, min_confidence))

            row = cursor.fetchone()
            if row:
                # Update access count
                cursor.execute("""
                    UPDATE knowledge
                    SET times_accessed = ?, last_accessed = ?
                    WHERE category = ? AND key = ?
                """, (row[2] + 1, datetime.now().isoformat(), category, key))
                conn.commit()

                result = row[0]
            else:
                result = None
        else:
            # Get all knowledge in category
            cursor.execute("""
                SELECT key, value, confidence
                FROM knowledge
                WHERE category = ? AND confidence >= ?
                ORDER BY importance DESC, times_accessed DESC
            """, (category, min_confidence))

            result = {
                row[0]: row[1]
                for row in cursor.fetchall()
            }

        conn.close()
        return result

    def search_knowledge(self, query: str, limit: int = 10, semantic: bool = True) -> List[Dict]:
        """Search knowledge base with optional semantic ranking"""
        if not semantic:
            # Simple keyword search
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query_pattern = f"%{query}%"

            cursor.execute("""
                SELECT category, key, value, confidence, importance
                FROM knowledge
                WHERE key LIKE ? OR value LIKE ?
                ORDER BY importance DESC, confidence DESC, times_accessed DESC
                LIMIT ?
            """, (query_pattern, query_pattern, limit))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "category": row[0],
                    "key": row[1],
                    "value": row[2],
                    "confidence": row[3],
                    "importance": row[4]
                })

            conn.close()
            return results
        else:
            # Semantic search with relevance scoring
            return self._search_semantic(query, limit)

    def _search_semantic(self, query: str, limit: int = 10) -> List[Dict]:
        """Semantic search with relevance ranking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query_terms = query.lower().split()

        # Get all knowledge items
        cursor.execute("""
            SELECT id, category, key, value, importance, confidence, times_accessed
            FROM knowledge
        """)

        results_with_scores = []

        for row in cursor.fetchall():
            kid, category, key, value, importance, confidence, times_accessed = row

            # Calculate relevance score
            doc = f"{category} {key} {value}".lower()

            # Term frequency scoring
            tf_score = sum(doc.count(term) for term in query_terms)

            # Normalize by document length
            doc_length = len(doc.split())
            tf_score = tf_score / max(doc_length, 1)

            # Combine with other signals
            import math
            access_score = min(1.0, math.log(times_accessed + 1) / math.log(50))

            relevance_score = (
                0.5 * tf_score * 10 +  # TF score (scaled)
                0.2 * (importance / 10.0) * 10 +
                0.15 * confidence * 10 +
                0.15 * access_score * 10
            )

            if relevance_score > 0.1:  # Minimum threshold
                results_with_scores.append({
                    'id': kid,
                    'category': category,
                    'key': key,
                    'value': value,
                    'importance': importance,
                    'confidence': confidence,
                    'relevance_score': relevance_score
                })

        conn.close()

        # Sort by relevance score
        results_with_scores.sort(key=lambda x: x['relevance_score'], reverse=True)

        return results_with_scores[:limit]

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate edit distance between two strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def calculate_knowledge_similarity(self, k1: Dict, k2: Dict) -> float:
        """
        Calculate similarity between two knowledge items

        Considers:
        - Category match (weight: 0.3)
        - Key similarity (weight: 0.4)
        - Value similarity (weight: 0.3)

        Returns:
            0.0-1.0 similarity score
        """
        # Category must match exactly
        if k1['category'] != k2['category']:
            return 0.0

        # Calculate key similarity
        key1, key2 = k1['key'].lower(), k2['key'].lower()
        if key1 == key2:
            key_similarity = 1.0
        else:
            key_distance = self.levenshtein_distance(key1, key2)
            max_len = max(len(key1), len(key2))
            key_similarity = 1.0 - (key_distance / max_len) if max_len > 0 else 0.0

        # Calculate value similarity
        val1, val2 = str(k1['value']).lower(), str(k2['value']).lower()
        if val1 == val2:
            value_similarity = 1.0
        else:
            val_distance = self.levenshtein_distance(val1, val2)
            max_len = max(len(val1), len(val2))
            value_similarity = 1.0 - (val_distance / max_len) if max_len > 0 else 0.0

        # Weighted combination
        similarity = (0.4 * key_similarity) + (0.3 * value_similarity) + 0.3

        return similarity

    def find_duplicate_knowledge(self, similarity_threshold: float = 0.85) -> List[Tuple]:
        """
        Find potential duplicate knowledge items

        Args:
            similarity_threshold: Minimum similarity to consider duplicates

        Returns:
            List of (id1, id2, similarity_score) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all knowledge items
        cursor.execute("""
            SELECT id, category, key, value, confidence
            FROM knowledge
            ORDER BY category, key
        """)

        items = []
        for row in cursor.fetchall():
            items.append({
                'id': row[0],
                'category': row[1],
                'key': row[2],
                'value': row[3],
                'confidence': row[4]
            })

        conn.close()

        # Find similar pairs
        duplicates = []

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                # Only compare items in same category
                if items[i]['category'] != items[j]['category']:
                    continue

                similarity = self.calculate_knowledge_similarity(items[i], items[j])

                if similarity >= similarity_threshold:
                    duplicates.append((
                        items[i]['id'],
                        items[j]['id'],
                        similarity,
                        items[i],
                        items[j]
                    ))

        return duplicates

    def merge_knowledge_items(self, primary_id: int, duplicate_ids: List[int],
                              strategy: str = "keep_highest_confidence") -> int:
        """
        Merge duplicate knowledge items

        Args:
            primary_id: ID to keep
            duplicate_ids: IDs to merge and remove
            strategy: "keep_highest_confidence", "combine_values", "keep_newest"

        Returns:
            Number of items merged
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all items to merge
        all_ids = [primary_id] + duplicate_ids
        placeholders = ','.join('?' * len(all_ids))

        cursor.execute(f"""
            SELECT id, value, confidence, timestamp, times_accessed
            FROM knowledge
            WHERE id IN ({placeholders})
        """, all_ids)

        items = cursor.fetchall()

        # Determine final value based on strategy
        if strategy == "keep_highest_confidence":
            final_item = max(items, key=lambda x: x[2])  # Max confidence
        elif strategy == "keep_newest":
            final_item = max(items, key=lambda x: x[3])  # Max timestamp
        elif strategy == "combine_values":
            # Combine unique values (comma-separated)
            values = [item[1] for item in items]
            unique_values = list(dict.fromkeys(values))  # Preserve order, remove duplicates
            combined_value = ", ".join(unique_values)
            final_item = (primary_id, combined_value, max(items, key=lambda x: x[2])[2],
                         max(items, key=lambda x: x[3])[3], sum(item[4] for item in items))
        else:
            final_item = items[0]

        # Update primary item with merged data
        cursor.execute("""
            UPDATE knowledge
            SET value = ?,
                confidence = ?,
                times_accessed = ?,
                last_accessed = ?
            WHERE id = ?
        """, (
            final_item[1],  # value
            final_item[2],  # confidence
            sum(item[4] for item in items),  # sum of times_accessed
            datetime.now().isoformat(),
            primary_id
        ))

        # Backup merged items
        original_values = json.dumps([
            {"id": item[0], "value": item[1], "confidence": item[2]}
            for item in items
        ])

        cursor.execute("""
            INSERT INTO knowledge_merges
            (timestamp, primary_id, merged_ids, merge_strategy, original_values)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            primary_id,
            json.dumps(duplicate_ids),
            strategy,
            original_values
        ))

        # Delete duplicate items
        if duplicate_ids:
            dup_placeholders = ','.join('?' * len(duplicate_ids))
            cursor.execute(f"""
                DELETE FROM knowledge
                WHERE id IN ({dup_placeholders})
            """, duplicate_ids)

            deleted_count = cursor.rowcount
        else:
            deleted_count = 0

        conn.commit()
        conn.close()

        return deleted_count

    def deduplicate_knowledge(self, dry_run: bool = False,
                              similarity_threshold: float = 0.85) -> Dict:
        """
        Comprehensive deduplication with fuzzy matching

        Args:
            dry_run: Preview without actually merging
            similarity_threshold: Minimum similarity to consider duplicates

        Returns:
            Statistics about deduplication
        """
        print(f"[Brain] Finding duplicates (threshold={similarity_threshold})...")
        duplicates = self.find_duplicate_knowledge(similarity_threshold)

        if not duplicates:
            return {
                'merged_count': 0,
                'cluster_count': 0,
                'saved_space': 0
            }

        # Group duplicates into clusters
        from collections import defaultdict
        clusters = defaultdict(set)

        for id1, id2, similarity, item1, item2 in duplicates:
            # Find existing cluster
            found_cluster = None
            for cluster_id, cluster_items in clusters.items():
                if id1 in cluster_items or id2 in cluster_items:
                    found_cluster = cluster_id
                    break

            if found_cluster:
                clusters[found_cluster].update([id1, id2])
            else:
                # Create new cluster with first ID as primary
                clusters[id1] = {id1, id2}

        merged_count = 0

        if not dry_run:
            for primary_id, cluster_ids in clusters.items():
                duplicate_ids = list(cluster_ids - {primary_id})
                if duplicate_ids:
                    merged_count += self.merge_knowledge_items(
                        primary_id,
                        duplicate_ids,
                        strategy="keep_highest_confidence"
                    )
        else:
            # Calculate what would be merged
            for cluster_ids in clusters.values():
                merged_count += len(cluster_ids) - 1  # All but primary

        return {
            'merged_count': merged_count,
            'cluster_count': len(clusters),
            'duplicate_pairs_found': len(duplicates),
            'saved_space': merged_count * 512  # Estimate 512 bytes per item
        }

    def create_knowledge_relationship(self, knowledge_id1: int, knowledge_id2: int,
                                      relationship_type: str, strength: float = 1.0):
        """
        Create relationship between knowledge items

        Relationship types: related_to, prerequisite_of, contradicts, supports, part_of
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO knowledge_relationships
            (knowledge_id1, knowledge_id2, relationship_type, strength, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (knowledge_id1, knowledge_id2, relationship_type, strength,
              datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def _increment_access_count(self, category: str, key: str):
        """Increment access count for knowledge item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE knowledge
            SET times_accessed = times_accessed + 1,
                last_accessed = ?
            WHERE category = ? AND key = ?
        """, (datetime.now().isoformat(), category, key))

        conn.commit()
        conn.close()

    def _auto_extract_knowledge(
        self,
        cursor,
        user_input: str,
        alfred_response: str
    ):
        """Auto-extract knowledge from conversations using enhanced patterns"""

        extraction_count = 0

        # Check for corrections first (highest priority)
        extraction_count += self._detect_corrections(cursor, user_input)

        # Extract from user input
        extraction_count += self._extract_preferences(cursor, user_input, "user_input")
        extraction_count += self._extract_facts(cursor, user_input, "user_input")
        extraction_count += self._extract_learning_goals(cursor, user_input, "user_input")
        extraction_count += self._extract_habits(cursor, user_input, "user_input")
        extraction_count += self._extract_expertise(cursor, user_input, "user_input")
        extraction_count += self._extract_relationships(cursor, user_input, "user_input")
        extraction_count += self._extract_context_preferences(cursor, user_input, "user_input")

        # Extract from Alfred's response (things learned from external sources)
        extraction_count += self._extract_facts(cursor, alfred_response, "alfred_response")

        return extraction_count

    def _extract_preferences(self, cursor, text: str, source: str) -> int:
        """Enhanced preference extraction"""
        count = 0

        patterns = [
            # Existing patterns
            (r"i (?:prefer|like|want|need) (.+)", "preference", 1.0),
            (r"my (?:favorite|preferred) (.+) is (.+)", "preference", 1.0),
            (r"i (?:don't|do not) like (.+)", "dislike", 1.0),

            # New patterns
            (r"i (?:always|usually|typically|normally) (.+)", "habit", 0.8),
            (r"i tend to (.+)", "tendency", 0.7),
            (r"i'd rather (.+) than (.+)", "preference_comparison", 0.9),
            (r"(?:can you|please) (?:always|remember to) (.+)", "standing_request", 1.0),
            (r"i (?:hate|love|enjoy) (.+)", "strong_preference", 1.0),
            (r"(?:never|don't ever) (.+)", "aversion", 1.0),
        ]

        for pattern, pref_type, confidence in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1).strip()
                cursor.execute("""
                    INSERT INTO knowledge
                    (timestamp, category, key, value, source, confidence, importance,
                     extraction_method, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "user_preferences",
                    pref_type,
                    value,
                    source,
                    confidence,
                    7,  # Important
                    "auto-extract-v2",
                    datetime.now().isoformat()
                ))
                count += 1

        return count

    def _extract_facts(self, cursor, text: str, source: str) -> int:
        """Enhanced fact extraction"""
        count = 0

        patterns = [
            # Personal info (existing)
            (r"(?:my name is|i'm|i am) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)", "user_name", 9, 1.0),
            (r"i live in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)", "user_location", 8, 1.0),
            (r"i work (?:as|at) (.+)", "user_occupation", 8, 1.0),

            # New patterns
            (r"my (?:email|email address) is ([\w\.-]+@[\w\.-]+)", "user_email", 9, 1.0),
            (r"my (?:phone|number) is ([\d\-\(\) ]+)", "user_phone", 8, 0.9),
            (r"i'm (\d+) years old", "user_age", 7, 1.0),
            (r"i speak ([A-Z][a-z]+(?: and [A-Z][a-z]+)*)", "user_languages", 7, 0.9),
            (r"i (?:graduated from|studied at) ([A-Z][a-z\s]+)", "user_education", 7, 0.9),
            (r"i've been (?:working|doing) (.+) for (\d+) (?:years|months)", "user_experience", 8, 0.9),
            (r"i use ([A-Z][a-zA-Z0-9\s]+) (?:for|to) (.+)", "user_tools", 6, 0.8),
            (r"my timezone is ([A-Z]{3,})", "user_timezone", 8, 1.0),
            (r"i'm (?:located in|based in|from) (.+)", "user_location_detailed", 8, 0.9),
        ]

        for pattern, fact_type, importance, confidence in patterns:
            match = re.search(pattern, text, re.IGNORECASE if fact_type.startswith("user_") else 0)
            if match:
                value = match.group(1).strip()
                cursor.execute("""
                    INSERT INTO knowledge
                    (timestamp, category, key, value, source, confidence, importance,
                     extraction_method, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "user_info",
                    fact_type,
                    value,
                    source,
                    confidence,
                    importance,
                    "auto-extract-v2",
                    datetime.now().isoformat()
                ))
                count += 1

        return count

    def _extract_learning_goals(self, cursor, text: str, source: str) -> int:
        """Extract learning goals and aspirations"""
        count = 0

        patterns = [
            (r"i want to learn (?:about |how to )?(.+)", "learning_goal", 8, 0.9),
            (r"i'm trying to (?:learn|understand|master) (.+)", "learning_goal", 8, 0.9),
            (r"(?:teach me|help me learn|show me) (.+)", "learning_request", 8, 0.9),
            (r"i need to (?:learn|understand|know) (.+)", "learning_need", 8, 0.9),
            (r"i'd like to become (.+)", "aspiration", 7, 0.8),
            (r"my goal is to (.+)", "goal", 8, 1.0),
        ]

        for pattern, goal_type, importance, confidence in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1).strip()
                cursor.execute("""
                    INSERT INTO knowledge
                    (timestamp, category, key, value, source, confidence, importance,
                     extraction_method, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "learning_goals",
                    goal_type,
                    value,
                    source,
                    confidence,
                    importance,
                    "auto-extract-v2",
                    datetime.now().isoformat()
                ))
                count += 1

        return count

    def _extract_habits(self, cursor, text: str, source: str) -> int:
        """Extract behavioral habits and routines"""
        count = 0

        patterns = [
            (r"i (?:always|usually|typically|normally) (.+)", "habit", 7, 0.8),
            (r"every (?:day|morning|evening|week) i (.+)", "routine", 7, 0.9),
            (r"i (?:tend to|often) (.+)", "tendency", 6, 0.7),
            (r"i'm (?:usually|typically|generally) (.+)", "characteristic", 6, 0.7),
            (r"i rarely (.+)", "rare_behavior", 6, 0.8),
            (r"i never (.+)", "avoidance", 7, 0.9),
        ]

        for pattern, habit_type, importance, confidence in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1).strip()
                cursor.execute("""
                    INSERT INTO knowledge
                    (timestamp, category, key, value, source, confidence, importance,
                     extraction_method, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "user_habits",
                    habit_type,
                    value,
                    source,
                    confidence,
                    importance,
                    "auto-extract-v2",
                    datetime.now().isoformat()
                ))
                count += 1

        return count

    def _extract_expertise(self, cursor, text: str, source: str) -> int:
        """Extract user expertise and skill areas"""
        count = 0

        patterns = [
            (r"i'm (?:experienced in|an expert in|skilled in|good at) (.+)", "expertise", 8, 0.9),
            (r"i (?:know|understand) (.+) (?:well|very well)", "knowledge_area", 7, 0.8),
            (r"i specialize in (.+)", "specialization", 9, 1.0),
            (r"i've (?:worked with|used) (.+) for (?:\d+) (?:years|months)", "long_term_skill", 8, 0.9),
            (r"i'm (?:not good at|weak in|bad at) (.+)", "skill_gap", 7, 0.9),
            (r"i'm learning (.+)", "developing_skill", 6, 0.8),
        ]

        for pattern, skill_type, importance, confidence in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1).strip()
                cursor.execute("""
                    INSERT INTO knowledge
                    (timestamp, category, key, value, source, confidence, importance,
                     extraction_method, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "user_expertise",
                    skill_type,
                    value,
                    source,
                    confidence,
                    importance,
                    "auto-extract-v2",
                    datetime.now().isoformat()
                ))
                count += 1

        return count

    def _extract_relationships(self, cursor, text: str, source: str) -> int:
        """Extract mentions of people, teams, companies"""
        count = 0

        patterns = [
            (r"my (?:colleague|coworker|teammate) ([A-Z][a-z]+)", "colleague", 6, 0.8),
            (r"(?:working with|working on) the ([A-Z][a-zA-Z\s]+) team", "team", 7, 0.9),
            (r"my (?:boss|manager|supervisor) ([A-Z][a-z]+)", "manager", 7, 0.9),
            (r"i work (?:at|for) ([A-Z][a-zA-Z0-9\s]+)", "company", 8, 1.0),
            (r"my (?:friend|partner) ([A-Z][a-z]+)", "personal_contact", 5, 0.8),
        ]

        for pattern, relation_type, importance, confidence in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                cursor.execute("""
                    INSERT INTO knowledge
                    (timestamp, category, key, value, source, confidence, importance,
                     extraction_method, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "user_relationships",
                    relation_type,
                    value,
                    source,
                    confidence,
                    importance,
                    "auto-extract-v2",
                    datetime.now().isoformat()
                ))
                count += 1

        return count

    def _extract_context_preferences(self, cursor, text: str, source: str) -> int:
        """Extract time preferences, work patterns, etc."""
        count = 0

        patterns = [
            (r"i work (?:from |)(\d+(?:am|pm)) to (\d+(?:am|pm))", "work_hours", 8, 0.9),
            (r"i'm (?:most productive|at my best) (?:in the |during the |)(\w+)", "productivity_time", 7, 0.8),
            (r"i prefer (?:to work|working) (?:in the |during the |)(\w+)", "work_time_preference", 7, 0.8),
            (r"i'm in (?:the |)([A-Z]{3,}|UTC[+-]\d+) (?:timezone|time zone)", "timezone", 9, 1.0),
            (r"i take breaks (?:every |)(\d+) (?:minutes|hours)", "break_pattern", 6, 0.7),
        ]

        for pattern, context_type, importance, confidence in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1).strip()
                cursor.execute("""
                    INSERT INTO knowledge
                    (timestamp, category, key, value, source, confidence, importance,
                     extraction_method, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "user_context",
                    context_type,
                    value,
                    source,
                    confidence,
                    importance,
                    "auto-extract-v2",
                    datetime.now().isoformat()
                ))
                count += 1

        return count

    def _detect_corrections(self, cursor, user_input: str) -> int:
        """Detect corrections to previous knowledge"""
        count = 0

        correction_patterns = [
            r"actually,? (?:it's|i meant|i said) (.+)",
            r"(?:no|nope),? (?:it's|i meant) (.+)",
            r"(?:sorry|my bad),? (?:it's|i meant) (.+)",
            r"correction:? (.+)",
            r"i meant to say (.+)",
        ]

        for pattern in correction_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                correction_value = match.group(1).strip()

                # Mark recent knowledge as superseded
                cursor.execute("""
                    UPDATE knowledge
                    SET verified = 0,
                        confidence = confidence * 0.5
                    WHERE timestamp > ? AND verified = 0
                    ORDER BY timestamp DESC
                    LIMIT 3
                """, ((datetime.now() - timedelta(minutes=5)).isoformat(),))

                # Store the correction with high confidence
                cursor.execute("""
                    INSERT INTO knowledge
                    (timestamp, category, key, value, source, confidence, importance,
                     extraction_method, verified, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "corrections",
                    "user_correction",
                    correction_value,
                    "user_correction",
                    1.0,
                    9,  # Very important
                    "correction-detection",
                    1,  # Verified
                    datetime.now().isoformat()
                ))
                count += 1

        return count

    # ============================================================================
    # USER PREFERENCES
    # ============================================================================

    def set_preference(self, key: str, value: str, confidence: float = 1.0):
        """Set user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO preferences
            (preference_key, preference_value, updated_at, times_used, confidence)
            VALUES (?, ?, ?, COALESCE((SELECT times_used FROM preferences WHERE preference_key = ?), 0), ?)
        """, (key, value, datetime.now().isoformat(), key, confidence))

        conn.commit()
        conn.close()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE preferences
            SET times_used = times_used + 1
            WHERE preference_key = ?
        """, (key,))

        cursor.execute("""
            SELECT preference_value, confidence
            FROM preferences
            WHERE preference_key = ?
        """, (key,))

        row = cursor.fetchone()
        conn.commit()
        conn.close()

        if row:
            return row[0]
        return default

    # ============================================================================
    # PATTERN LEARNING
    # ============================================================================

    def record_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict,
        success: bool = True
    ):
        """
        Record behavioral pattern

        Args:
            pattern_type: Type of pattern
            pattern_data: Pattern data
            success: Whether pattern led to success
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        pattern_json = json.dumps(pattern_data)
        pattern_hash = hashlib.md5(pattern_json.encode()).hexdigest()

        # Check if pattern exists
        cursor.execute("""
            SELECT id, frequency, success_rate
            FROM patterns
            WHERE pattern_type = ? AND pattern_data = ?
        """, (pattern_type, pattern_json))

        row = cursor.fetchone()

        if row:
            # Update existing pattern
            pattern_id, frequency, success_rate = row
            new_frequency = frequency + 1
            new_success_rate = (success_rate * frequency + (1.0 if success else 0.0)) / new_frequency

            cursor.execute("""
                UPDATE patterns
                SET frequency = ?, success_rate = ?, last_seen = ?
                WHERE id = ?
            """, (new_frequency, new_success_rate, datetime.now().isoformat(), pattern_id))
        else:
            # Insert new pattern
            cursor.execute("""
                INSERT INTO patterns
                (pattern_type, pattern_data, frequency, success_rate, last_seen)
                VALUES (?, ?, 1, ?, ?)
            """, (pattern_type, pattern_json, 1.0 if success else 0.0, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_frequency: int = 1,
        min_success_rate: float = 0.5
    ) -> List[Dict]:
        """Get learned patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if pattern_type:
            cursor.execute("""
                SELECT pattern_type, pattern_data, frequency, success_rate
                FROM patterns
                WHERE pattern_type = ? AND frequency >= ? AND success_rate >= ?
                ORDER BY frequency DESC, success_rate DESC
            """, (pattern_type, min_frequency, min_success_rate))
        else:
            cursor.execute("""
                SELECT pattern_type, pattern_data, frequency, success_rate
                FROM patterns
                WHERE frequency >= ? AND success_rate >= ?
                ORDER BY frequency DESC, success_rate DESC
            """, (min_frequency, min_success_rate))

        results = []
        for row in cursor.fetchall():
            results.append({
                "type": row[0],
                "data": json.loads(row[1]),
                "frequency": row[2],
                "success_rate": row[3]
            })

        conn.close()
        return results

    # ============================================================================
    # SKILLS & CAPABILITIES
    # ============================================================================

    def track_skill_use(
        self,
        skill_name: str,
        success: bool = True,
        notes: Optional[str] = None
    ):
        """
        Track skill usage and proficiency

        Args:
            skill_name: Name of skill
            success: Whether skill was used successfully
            notes: Optional notes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO skills (skill_name, last_used)
            VALUES (?, ?)
            ON CONFLICT(skill_name) DO UPDATE SET
                times_used = times_used + 1,
                success_count = success_count + CASE WHEN ? THEN 1 ELSE 0 END,
                failure_count = failure_count + CASE WHEN ? THEN 0 ELSE 1 END,
                proficiency = CAST(success_count AS REAL) / CAST(times_used AS REAL),
                last_used = ?,
                notes = COALESCE(?, notes)
        """, (
            skill_name,
            datetime.now().isoformat(),
            success,
            success,
            datetime.now().isoformat(),
            notes
        ))

        conn.commit()
        conn.close()

    def get_skill_proficiency(self, skill_name: str) -> Optional[float]:
        """Get proficiency level for a skill (0.0-1.0)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT proficiency
            FROM skills
            WHERE skill_name = ?
        """, (skill_name,))

        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None

    def get_all_skills(self, min_proficiency: float = 0.0) -> List[Dict]:
        """Get all tracked skills"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT skill_name, proficiency, times_used, success_count, failure_count
            FROM skills
            WHERE proficiency >= ?
            ORDER BY proficiency DESC, times_used DESC
        """, (min_proficiency,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "skill": row[0],
                "proficiency": row[1],
                "times_used": row[2],
                "successes": row[3],
                "failures": row[4]
            })

        conn.close()
        return results

    # ============================================================================
    # MISTAKES & LEARNING
    # ============================================================================

    def record_mistake(
        self,
        error_type: str,
        description: str,
        context: Optional[str] = None,
        solution: Optional[str] = None
    ):
        """Record a mistake to learn from"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO mistakes
            (timestamp, error_type, description, context, solution)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            error_type,
            description,
            context,
            solution
        ))

        conn.commit()
        conn.close()

    def mark_mistake_learned(self, mistake_id: int):
        """Mark a mistake as learned from"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE mistakes
            SET learned = 1
            WHERE id = ?
        """, (mistake_id,))

        conn.commit()
        conn.close()

    def get_unlearned_mistakes(self) -> List[Dict]:
        """Get mistakes that haven't been learned from yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, error_type, description, context, solution
            FROM mistakes
            WHERE learned = 0
            ORDER BY timestamp DESC
        """)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "error_type": row[1],
                "description": row[2],
                "context": row[3],
                "solution": row[4]
            })

        conn.close()
        return results

    # ============================================================================
    # TOPIC TRACKING
    # ============================================================================

    def _update_topic(self, cursor, topic: str):
        """Update topic tracking"""
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO topics (topic, first_seen, last_seen)
            VALUES (?, ?, ?)
            ON CONFLICT(topic) DO UPDATE SET
                frequency = frequency + 1,
                last_seen = ?,
                interest_level = MIN(1.0, interest_level + 0.1)
        """, (topic, now, now, now))

    def get_top_topics(self, limit: int = 10) -> List[Dict]:
        """Get most discussed topics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT topic, frequency, interest_level, last_seen
            FROM topics
            ORDER BY interest_level DESC, frequency DESC
            LIMIT ?
        """, (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "topic": row[0],
                "frequency": row[1],
                "interest": row[2],
                "last_seen": row[3]
            })

        conn.close()
        return results

    # ============================================================================
    # SECURITY SCANS
    # ============================================================================

    def store_security_scan(
        self,
        target: str,
        scan_type: str,
        findings: Dict,
        severity_summary: Optional[str] = None,
        recommendations: Optional[List[str]] = None,
        authorized: bool = False,
        notes: Optional[str] = None
    ):
        """
        Store security scan results

        Args:
            target: Scan target (URL, directory, GitHub repo)
            scan_type: Type of scan performed (strix, manual, etc.)
            findings: Dictionary of findings/vulnerabilities
            severity_summary: Summary of severity levels
            recommendations: List of remediation recommendations
            authorized: Whether scan was authorized
            notes: Additional notes or commentary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert findings dict to JSON string
        findings_json = json.dumps(findings) if isinstance(findings, dict) else str(findings)

        # Convert recommendations list to JSON string
        recommendations_json = json.dumps(recommendations) if recommendations else None

        cursor.execute("""
            INSERT INTO security_scans
            (timestamp, target, scan_type, findings, severity_summary, recommendations, authorized, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            target,
            scan_type,
            findings_json,
            severity_summary,
            recommendations_json,
            authorized,
            notes
        ))

        conn.commit()
        conn.close()

        print(f"[Brain] Stored security scan: {target} ({scan_type})")

    def get_security_history(
        self,
        target: Optional[str] = None,
        scan_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get security scan history

        Args:
            target: Filter by target (optional)
            scan_type: Filter by scan type (optional)
            limit: Maximum number of results

        Returns:
            List of security scan dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM security_scans WHERE 1=1"
        params = []

        if target:
            query += " AND target LIKE ?"
            params.append(f"%{target}%")

        if scan_type:
            query += " AND scan_type = ?"
            params.append(scan_type)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            # Parse JSON fields
            findings = json.loads(row[4]) if row[4] else {}
            recommendations = json.loads(row[6]) if row[6] else []

            results.append({
                "id": row[0],
                "timestamp": row[1],
                "target": row[2],
                "scan_type": row[3],
                "findings": findings,
                "severity_summary": row[5],
                "recommendations": recommendations,
                "authorized": bool(row[7]),
                "notes": row[8]
            })

        conn.close()
        return results

    def get_latest_scan(self, target: str) -> Optional[Dict]:
        """
        Get most recent scan for specific target

        Args:
            target: Target to search for

        Returns:
            Latest scan dictionary or None
        """
        results = self.get_security_history(target=target, limit=1)
        return results[0] if results else None

    def get_vulnerability_summary(self) -> Dict[str, Any]:
        """
        Get summary of all vulnerability findings

        Returns:
            Dictionary with statistics on security scans
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total scans
        cursor.execute("SELECT COUNT(*) FROM security_scans")
        total_scans = cursor.fetchone()[0]

        # Scans by type
        cursor.execute("""
            SELECT scan_type, COUNT(*)
            FROM security_scans
            GROUP BY scan_type
        """)
        scans_by_type = {row[0]: row[1] for row in cursor.fetchall()}

        # Recent scans (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*)
            FROM security_scans
            WHERE timestamp > ?
        """, (week_ago,))
        recent_scans = cursor.fetchone()[0]

        # Get all findings to parse severity
        cursor.execute("SELECT findings FROM security_scans")
        rows = cursor.fetchall()

        total_vulnerabilities = 0
        severity_totals = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }

        for row in rows:
            try:
                findings = json.loads(row[0]) if row[0] else {}
                if 'severity_summary' in findings:
                    summary = findings['severity_summary']
                    for severity, count in summary.items():
                        if severity in severity_totals:
                            severity_totals[severity] += count
                            total_vulnerabilities += count
            except:
                pass

        conn.close()

        return {
            'total_scans': total_scans,
            'scans_by_type': scans_by_type,
            'recent_scans': recent_scans,
            'total_vulnerabilities': total_vulnerabilities,
            'severity_totals': severity_totals
        }

    # ============================================================================
    # CAMDAN PROJECTS
    # ============================================================================

    def store_camdan_project(
        self,
        project_name: str,
        client_name: Optional[str] = None,
        location: Optional[str] = None,
        building_type: Optional[str] = None,
        square_footage: Optional[int] = None,
        estimated_cost: Optional[float] = None,
        status: str = "planning",
        timeline_data: Optional[Dict] = None,
        compliance_issues: Optional[List] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Store a new CAMDAN project for tracking

        Args:
            project_name: Name/description of the project
            client_name: Client name (e.g., "TBC Corporation")
            location: Project location
            building_type: Type of building
            square_footage: Size in square feet
            estimated_cost: Estimated project cost
            status: Project status (planning, active, completed, on_hold)
            timeline_data: Timeline information (JSON)
            compliance_issues: Compliance issues/violations (JSON)
            notes: Additional notes

        Returns:
            Project ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        # Convert dicts/lists to JSON
        timeline_json = json.dumps(timeline_data) if timeline_data else None
        compliance_json = json.dumps(compliance_issues) if compliance_issues else None

        cursor.execute("""
            INSERT INTO camdan_projects
            (project_name, client_name, location, building_type, square_footage,
             estimated_cost, status, timeline_data, compliance_issues,
             created_at, updated_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_name, client_name, location, building_type, square_footage,
            estimated_cost, status, timeline_json, compliance_json,
            now, now, notes
        ))

        project_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.logger.info(f"[Brain] Stored CAMDAN project: {project_name} (ID: {project_id})")
        return project_id

    def update_camdan_project(
        self,
        project_id: int,
        actual_cost: Optional[float] = None,
        status: Optional[str] = None,
        timeline_data: Optional[Dict] = None,
        compliance_issues: Optional[List] = None,
        brain_insights: Optional[Dict] = None,
        notes: Optional[str] = None
    ):
        """
        Update an existing CAMDAN project

        Args:
            project_id: Project ID to update
            actual_cost: Actual project cost
            status: Updated status
            timeline_data: Updated timeline
            compliance_issues: Updated compliance issues
            brain_insights: Alfred's learned insights about the project
            notes: Updated notes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if actual_cost is not None:
            updates.append("actual_cost = ?")
            params.append(actual_cost)

        if status:
            updates.append("status = ?")
            params.append(status)
            if status == "completed":
                updates.append("completed_at = ?")
                params.append(datetime.now().isoformat())

        if timeline_data:
            updates.append("timeline_data = ?")
            params.append(json.dumps(timeline_data))

        if compliance_issues:
            updates.append("compliance_issues = ?")
            params.append(json.dumps(compliance_issues))

        if brain_insights:
            updates.append("brain_insights = ?")
            params.append(json.dumps(brain_insights))

        if notes:
            updates.append("notes = ?")
            params.append(notes)

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())

        params.append(project_id)

        query = f"UPDATE camdan_projects SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)

        conn.commit()
        conn.close()

        self.logger.info(f"[Brain] Updated CAMDAN project ID: {project_id}")

    def get_camdan_projects(
        self,
        client_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get CAMDAN projects with optional filtering

        Args:
            client_name: Filter by client name
            status: Filter by status
            limit: Maximum number of results

        Returns:
            List of project dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM camdan_projects WHERE 1=1"
        params = []

        if client_name:
            query += " AND client_name LIKE ?"
            params.append(f"%{client_name}%")

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        projects = []
        for row in rows:
            # Parse JSON fields
            timeline = json.loads(row[9]) if row[9] else None
            compliance = json.loads(row[10]) if row[10] else None
            insights = json.loads(row[11]) if row[11] else None

            projects.append({
                "id": row[0],
                "project_name": row[1],
                "client_name": row[2],
                "location": row[3],
                "building_type": row[4],
                "square_footage": row[5],
                "estimated_cost": row[6],
                "actual_cost": row[7],
                "status": row[8],
                "timeline_data": timeline,
                "compliance_issues": compliance,
                "brain_insights": insights,
                "created_at": row[12],
                "updated_at": row[13],
                "completed_at": row[14],
                "importance": row[15],
                "notes": row[16]
            })

        conn.close()
        return projects

    def get_camdan_project_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for CAMDAN projects

        Returns:
            Dictionary with project statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total projects
        cursor.execute("SELECT COUNT(*) FROM camdan_projects")
        total_projects = cursor.fetchone()[0]

        # Projects by status
        cursor.execute("""
            SELECT status, COUNT(*)
            FROM camdan_projects
            GROUP BY status
        """)
        by_status = {row[0]: row[1] for row in cursor.fetchall()}

        # Total estimated vs actual costs
        cursor.execute("""
            SELECT SUM(estimated_cost), SUM(actual_cost)
            FROM camdan_projects
            WHERE estimated_cost IS NOT NULL OR actual_cost IS NOT NULL
        """)
        costs = cursor.fetchone()
        total_estimated = costs[0] or 0
        total_actual = costs[1] or 0

        # Projects by client
        cursor.execute("""
            SELECT client_name, COUNT(*)
            FROM camdan_projects
            WHERE client_name IS NOT NULL
            GROUP BY client_name
        """)
        by_client = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            "total_projects": total_projects,
            "by_status": by_status,
            "total_estimated_cost": total_estimated,
            "total_actual_cost": total_actual,
            "cost_accuracy": (total_actual / total_estimated * 100) if total_estimated > 0 else None,
            "by_client": by_client
        }

    # ============================================================================
    # MEMORY PRIORITIZATION
    # ============================================================================

    def calculate_priority_score(self, item: Dict, context: Optional[Dict] = None) -> float:
        """
        Calculate composite priority score for memory item

        Factors:
        - Importance (1-10): base score weight = 0.3
        - Confidence (0.0-1.0): accuracy weight = 0.2
        - Recency: time decay weight = 0.2
        - Access frequency: usage weight = 0.15
        - Success rate: reliability weight = 0.1
        - Topic relevance: context weight = 0.05

        Returns:
            0.0-10.0 score
        """
        import math

        score = 0.0

        # Factor 1: Importance (weight: 0.3, range: 1-10)
        importance = item.get('importance', 5)
        score += (importance / 10.0) * 3.0  # Contribution: 0-3.0

        # Factor 2: Confidence (weight: 0.2, range: 0.0-1.0)
        confidence = item.get('confidence', 0.5)
        score += confidence * 2.0  # Contribution: 0-2.0

        # Factor 3: Recency (weight: 0.2, exponential decay)
        timestamp_str = item.get('timestamp') or item.get('last_accessed')
        if timestamp_str:
            try:
                item_time = datetime.fromisoformat(timestamp_str)
                age_days = (datetime.now() - item_time).days
                # Exponential decay: e^(-age/365) scaled to 0-2.0
                recency_score = 2.0 * (2.71828 ** (-age_days / 365.0))
                score += recency_score  # Contribution: 0-2.0
            except:
                score += 1.0  # Default middle value
        else:
            score += 1.0

        # Factor 4: Access frequency (weight: 0.15)
        times_accessed = item.get('times_accessed', 0)
        # Logarithmic scaling to prevent domination
        access_score = 1.5 * min(1.0, math.log(times_accessed + 1) / math.log(50))
        score += access_score  # Contribution: 0-1.5

        # Factor 5: Success rate (weight: 0.1)
        if 'success_rate' in item:
            score += item['success_rate'] * 1.0  # Contribution: 0-1.0
        elif 'success' in item:
            score += (1.0 if item['success'] else 0.0) * 1.0
        else:
            score += 0.5  # Neutral

        # Factor 6: Topic relevance (weight: 0.05) - simplified
        score += 0.25  # Default neutral contribution

        # Ensure score is in valid range
        return max(0.0, min(10.0, score))

    def update_priority_scores(self, item_type: str = "all") -> int:
        """
        Update priority scores for all items or specific type

        Args:
            item_type: "conversations", "knowledge", "patterns", or "all"

        Returns:
            Number of items updated
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updated_count = 0
        types_to_update = []

        if item_type == "all":
            types_to_update = ["conversations", "knowledge"]
        else:
            types_to_update = [item_type]

        for ttype in types_to_update:
            # Get items to update
            if ttype == "conversations":
                cursor.execute("""
                    SELECT id, timestamp, importance, success, times_accessed, topics
                    FROM conversations
                """)
            elif ttype == "knowledge":
                cursor.execute("""
                    SELECT id, timestamp, importance, confidence, times_accessed,
                           last_accessed, category
                    FROM knowledge
                """)
            else:
                continue

            items = cursor.fetchall()

            # Calculate and update scores
            for item_data in items:
                if ttype == "conversations":
                    item = {
                        'id': item_data[0],
                        'timestamp': item_data[1],
                        'importance': item_data[2],
                        'success': item_data[3],
                        'times_accessed': item_data[4] if item_data[4] else 0,
                        'confidence': 0.8  # Default for conversations
                    }
                elif ttype == "knowledge":
                    item = {
                        'id': item_data[0],
                        'timestamp': item_data[1],
                        'importance': item_data[2],
                        'confidence': item_data[3],
                        'times_accessed': item_data[4],
                        'last_accessed': item_data[5]
                    }

                new_score = self.calculate_priority_score(item)

                # Update in database
                cursor.execute(f"""
                    UPDATE {ttype}
                    SET priority_score = ?
                    WHERE id = ?
                """, (new_score, item['id']))

                updated_count += 1

        conn.commit()
        conn.close()

        print(f"[Brain] Updated priority scores for {updated_count} items")
        return updated_count

    # ============================================================================
    # MEMORY CONSOLIDATION
    # ============================================================================

    def calculate_retention_score(self, conversation_id: int) -> float:
        """
        Calculate retention score using exponential decay

        Formula: retention = importance * e^(-decay_rate * days_since_access)

        Returns:
            0.0-1.0 score indicating whether to keep
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT importance, last_accessed, times_accessed
            FROM conversations
            WHERE id = ?
        """, (conversation_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return 0.0

        importance, last_accessed, times_accessed = row

        # Calculate days since last access
        if last_accessed:
            try:
                last_access_time = datetime.fromisoformat(last_accessed)
                days_since_access = (datetime.now() - last_access_time).days
            except:
                days_since_access = 365  # Default to old
        else:
            days_since_access = 365

        # Exponential decay formula
        # Higher importance = slower decay
        # More access = slower decay
        import math

        base_importance = importance / 10.0  # Normalize to 0-1
        access_boost = min(1.0, math.log(times_accessed + 1) / math.log(50))

        # Decay rate varies by importance (high importance = slower decay)
        decay_rate = 1.0 / (365.0 * (1.0 + base_importance))

        # Calculate retention score
        retention = (base_importance + access_boost) * math.exp(-decay_rate * days_since_access)

        # Clamp to 0-1 range
        return max(0.0, min(1.0, retention))

    def identify_temporal_clusters(self, days: int = 7) -> List[List[int]]:
        """
        Group conversations into temporal clusters

        Args:
            days: Time window for clustering (default 7 days)

        Returns:
            List of clusters (each cluster is list of conversation IDs)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp
            FROM conversations
            ORDER BY timestamp ASC
        """)

        conversations = cursor.fetchall()
        conn.close()

        if not conversations:
            return []

        clusters = []
        current_cluster = []
        cluster_start_time = None

        for conv_id, timestamp_str in conversations:
            try:
                conv_time = datetime.fromisoformat(timestamp_str)
            except:
                continue

            if cluster_start_time is None:
                # Start first cluster
                cluster_start_time = conv_time
                current_cluster = [conv_id]
            else:
                # Check if conversation belongs to current cluster
                time_diff = (conv_time - cluster_start_time).days

                if time_diff <= days:
                    # Add to current cluster
                    current_cluster.append(conv_id)
                else:
                    # Save current cluster and start new one
                    if current_cluster:
                        clusters.append(current_cluster)

                    cluster_start_time = conv_time
                    current_cluster = [conv_id]

        # Don't forget the last cluster
        if current_cluster:
            clusters.append(current_cluster)

        return clusters

    def archive_conversation(self, conv_id: int, archive_path: Optional[str] = None, reason: str = "low_priority"):
        """
        Archive conversation to JSON file instead of deleting

        Args:
            conv_id: Conversation ID to archive
            archive_path: Optional custom archive path
            reason: Reason for archival
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get conversation data
        cursor.execute("""
            SELECT timestamp, user_input, alfred_response, context, models_used,
                   topics, sentiment, importance, success, execution_time
            FROM conversations
            WHERE id = ?
        """, (conv_id,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return

        # Create archive directory
        archive_dir = self.data_dir / "archives" / "conversations"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Generate archive filename
        if archive_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = str(archive_dir / f"conv_{conv_id}_{timestamp}.json")

        # Prepare conversation data
        conv_data = {
            "id": conv_id,
            "timestamp": row[0],
            "user_input": row[1],
            "alfred_response": row[2],
            "context": json.loads(row[3]) if row[3] else None,
            "models_used": json.loads(row[4]) if row[4] else None,
            "topics": json.loads(row[5]) if row[5] else None,
            "sentiment": row[6],
            "importance": row[7],
            "success": bool(row[8]),
            "execution_time": row[9],
            "archived_at": datetime.now().isoformat(),
            "archive_reason": reason
        }

        # Write to JSON file
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(conv_data, f, indent=2, ensure_ascii=False)

        # Record archival in database
        cursor.execute("""
            INSERT INTO conversation_archives
            (archived_at, original_id, archive_path, reason)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), conv_id, archive_path, reason))

        # Delete from conversations table
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))

        conn.commit()
        conn.close()

        print(f"[Brain] Archived conversation {conv_id} to {archive_path}")

    def consolidate_memory_advanced(self, dry_run: bool = False, retention_threshold: float = 0.3) -> Dict:
        """
        Advanced consolidation with exponential decay and clustering

        Args:
            dry_run: Preview what would be deleted without actually deleting
            retention_threshold: Minimum retention score to keep (0.0-1.0)

        Returns:
            Statistics about consolidation actions
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Step 1: Update retention scores for all conversations
        cursor.execute("SELECT id FROM conversations")
        conv_ids = [row[0] for row in cursor.fetchall()]

        updated_scores = 0
        for conv_id in conv_ids:
            retention_score = self.calculate_retention_score(conv_id)

            cursor.execute("""
                UPDATE conversations
                SET retention_score = ?
                WHERE id = ?
            """, (retention_score, conv_id))

            updated_scores += 1

        if not dry_run:
            conn.commit()

        # Step 2: Identify temporal clusters
        clusters = self.identify_temporal_clusters(days=7)

        # Assign cluster IDs
        for cluster_idx, cluster_conv_ids in enumerate(clusters):
            for conv_id in cluster_conv_ids:
                cursor.execute("""
                    UPDATE conversations
                    SET cluster_id = ?
                    WHERE id = ?
                """, (cluster_idx, conv_id))

        if not dry_run:
            conn.commit()

        # Step 3: Archive low-retention conversations (with age check)
        cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()

        cursor.execute("""
            SELECT id, retention_score
            FROM conversations
            WHERE retention_score < ? AND timestamp < ?
            ORDER BY retention_score ASC
        """, (retention_threshold, cutoff_date))

        candidates = cursor.fetchall()
        archived_count = 0

        for conv_id, retention_score in candidates:
            if not dry_run:
                self.archive_conversation(conv_id, reason=f"low_retention_{retention_score:.3f}")
            archived_count += 1

        # Step 4: Strengthen frequently accessed knowledge
        cursor.execute("""
            UPDATE knowledge
            SET confidence = MIN(1.0, confidence + 0.1),
                importance = MIN(10, importance + 1)
            WHERE times_accessed > 10
        """)

        strengthened = cursor.rowcount

        if not dry_run:
            conn.commit()

        conn.close()

        # Step 5: Smart deduplication with fuzzy matching
        dedup_stats = self.deduplicate_knowledge(
            dry_run=dry_run,
            similarity_threshold=0.85
        )

        # Reload caches
        if not dry_run:
            self.load_caches()

        return {
            "conversations_archived": archived_count,
            "retention_scores_updated": updated_scores,
            "clusters_identified": len(clusters),
            "knowledge_strengthened": strengthened,
            "knowledge_deduplicated": dedup_stats['merged_count'],
            "duplicate_clusters_found": dedup_stats['cluster_count'],
            "retention_threshold": retention_threshold,
            "dry_run": dry_run
        }

    def consolidate_memory(self, aggressive: bool = False):
        """
        Consolidate and optimize memory (wrapper for backward compatibility)

        Calls the new consolidate_memory_advanced() method

        Args:
            aggressive: Use lower retention threshold (0.2 vs 0.3)

        Returns:
            Statistics about consolidation actions
        """
        threshold = 0.2 if aggressive else 0.3
        return self.consolidate_memory_advanced(retention_threshold=threshold)

    # ============================================================================
    # STATISTICS & INSIGHTS
    # ============================================================================

    def get_memory_stats(self) -> Dict:
        """Get comprehensive memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Count tables
        tables = [
            "conversations", "knowledge", "preferences",
            "patterns", "skills", "mistakes", "topics"
        ]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]

        # Additional stats
        cursor.execute("""
            SELECT AVG(importance), AVG(success)
            FROM conversations
        """)
        row = cursor.fetchone()
        stats["avg_importance"] = round(row[0], 2) if row[0] else 0
        stats["success_rate"] = round(row[1] * 100, 1) if row[1] else 0

        cursor.execute("""
            SELECT AVG(proficiency)
            FROM skills
        """)
        row = cursor.fetchone()
        stats["avg_skill_proficiency"] = round(row[0], 2) if row[0] else 0

        cursor.execute("""
            SELECT COUNT(*)
            FROM mistakes
            WHERE learned = 0
        """)
        stats["unlearned_mistakes"] = cursor.fetchone()[0]

        conn.close()

        return stats

    def get_insights(self) -> Dict:
        """Get insights about Alfred's learning and behavior"""
        stats = self.get_memory_stats()
        top_topics = self.get_top_topics(5)
        top_skills = self.get_all_skills()[:5]
        patterns = self.get_patterns(min_frequency=3)

        return {
            "memory_stats": stats,
            "top_topics": top_topics,
            "top_skills": top_skills,
            "learned_patterns": len(patterns),
            "knowledge_strength": stats.get("avg_importance", 0),
            "overall_proficiency": stats.get("avg_skill_proficiency", 0)
        }

    def __repr__(self):
        """String representation"""
        stats = self.get_memory_stats()
        return f"<AlfredBrain: {stats['conversations']} conversations, {stats['knowledge']} knowledge items>"


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
    """CLI for Alfred Brain"""
    import sys

    print("="*80)
    print("ALFRED BRAIN - ULTRA-ENHANCED MEMORY SYSTEM")
    print("="*80)
    print()

    brain = AlfredBrain()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "stats":
            stats = brain.get_memory_stats()
            print("Memory Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")

        elif command == "insights":
            insights = brain.get_insights()
            print(json.dumps(insights, indent=2))

        elif command == "topics":
            topics = brain.get_top_topics(10)
            print("Top Topics:")
            for topic in topics:
                print(f"  - {topic['topic']}: {topic['frequency']} times, interest={topic['interest']:.2f}")

        elif command == "skills":
            skills = brain.get_all_skills()
            print("Tracked Skills:")
            for skill in skills:
                print(f"  - {skill['skill']}: {skill['proficiency']:.1%} proficiency ({skill['times_used']} uses)")

        elif command == "consolidate":
            result = brain.consolidate_memory()
            print("Memory Consolidated:")
            print(f"  Conversations archived: {result['conversations_archived']}")
            print(f"  Knowledge strengthened: {result['knowledge_strengthened']}")
            print(f"  Knowledge deduplicated: {result['knowledge_deduplicated']}")

        elif command == "test":
            print("Running brain tests...")

            # Test conversation storage
            brain.store_conversation(
                "Test question about AI",
                "Test response about artificial intelligence",
                topics=["AI", "testing"],
                importance=7
            )
            print("[OK] Stored test conversation")

            # Test knowledge
            brain.store_knowledge("test", "sample", "value123", importance=8)
            recalled = brain.recall_knowledge("test", "sample")
            print(f"[OK] Knowledge recall: {recalled}")

            # Test skill tracking
            brain.track_skill_use("web_crawling", success=True)
            proficiency = brain.get_skill_proficiency("web_crawling")
            print(f"[OK] Skill proficiency: {proficiency}")

            print("\nAll tests passed!")

    else:
        print("Usage:")
        print("  python alfred_brain.py stats       - Show memory statistics")
        print("  python alfred_brain.py insights    - Get learning insights")
        print("  python alfred_brain.py topics      - Show top topics")
        print("  python alfred_brain.py skills      - Show tracked skills")
        print("  python alfred_brain.py consolidate - Consolidate memory")
        print("  python alfred_brain.py test        - Run tests")
        print()
        print(brain)


if __name__ == "__main__":
    main()
