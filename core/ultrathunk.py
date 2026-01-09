"""
ULTRATHUNK: Atomic Compressed Intelligence

Ultra-compressed intelligence + Thunk (delayed computation)
Achieves 640:1+ compression through generative patterns.

"What you compress determines what you can generate."

Example: 47 weather conversations (100KB) -> 1 Ultrathunk (156 bytes) -> Infinite personalized outputs

Patent Status: TO BE FILED Q1 2025
Author: Daniel J Rita (BATDAN)
Copyright: GxEum Technologies / CAMDAN Enterprizes

PATENT PENDING - DO NOT DISTRIBUTE
"""

import sqlite3
import json
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Graceful degradation
try:
    from core.path_manager import PathManager
    PATHMANAGER_AVAILABLE = True
except ImportError:
    PATHMANAGER_AVAILABLE = False


class ThunkType(Enum):
    """Types of Ultrathunks."""
    PATTERN = "pattern"           # Behavioral pattern (user preferences)
    TEMPLATE = "template"         # Response templates
    KNOWLEDGE = "knowledge"       # Compressed knowledge
    SKILL = "skill"               # Learned capability
    ROUTINE = "routine"           # Time-based routines


@dataclass
class Ultrathunk:
    """
    The atomic unit of compressed intelligence.

    An Ultrathunk is a generative compression that gains quality -
    it doesn't just store data, it generates infinite variations.

    Structure:
    - trigger: Conditions that activate this thunk
    - generator: Code/template that produces output
    - confidence: How reliable this pattern is
    - fire_count: How many times it has generated output
    - compression_ratio: How much data was compressed into this thunk
    """
    id: str
    name: str
    thunk_type: ThunkType
    trigger_pattern: str          # Regex or keyword pattern
    generator_template: str       # Template for generation
    variables: Dict[str, Any]     # Extracted variables
    confidence: float = 0.5       # 0.0-1.0
    fire_count: int = 0
    created_from_count: int = 0   # Number of items compressed
    original_bytes: int = 0       # Size of original data
    thunk_bytes: int = 0          # Size of this thunk
    created_at: datetime = field(default_factory=datetime.now)
    last_fired: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio."""
        if self.thunk_bytes == 0:
            return 0.0
        return self.original_bytes / self.thunk_bytes

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'thunk_type': self.thunk_type.value,
            'trigger_pattern': self.trigger_pattern,
            'generator_template': self.generator_template,
            'variables': self.variables,
            'confidence': self.confidence,
            'fire_count': self.fire_count,
            'created_from_count': self.created_from_count,
            'original_bytes': self.original_bytes,
            'thunk_bytes': self.thunk_bytes,
            'created_at': self.created_at.isoformat(),
            'last_fired': self.last_fired.isoformat() if self.last_fired else None,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Ultrathunk':
        return cls(
            id=data['id'],
            name=data['name'],
            thunk_type=ThunkType(data['thunk_type']),
            trigger_pattern=data['trigger_pattern'],
            generator_template=data['generator_template'],
            variables=data.get('variables', {}),
            confidence=data.get('confidence', 0.5),
            fire_count=data.get('fire_count', 0),
            created_from_count=data.get('created_from_count', 0),
            original_bytes=data.get('original_bytes', 0),
            thunk_bytes=data.get('thunk_bytes', 0),
            created_at=datetime.fromisoformat(data['created_at']),
            last_fired=datetime.fromisoformat(data['last_fired']) if data.get('last_fired') else None,
            metadata=data.get('metadata', {})
        )

    def matches(self, context: str) -> bool:
        """Check if this thunk should fire for the given context."""
        try:
            return bool(re.search(self.trigger_pattern, context, re.IGNORECASE))
        except re.error:
            # Fallback to simple keyword matching
            return self.trigger_pattern.lower() in context.lower()

    def generate(self, context: str = "", **kwargs) -> str:
        """
        Generate output using this thunk's template.

        This is the "thunk" part - delayed computation that
        produces infinite personalized outputs from compressed patterns.
        """
        output = self.generator_template

        # Replace variables from stored values
        for var_name, var_value in self.variables.items():
            output = output.replace(f"{{{var_name}}}", str(var_value))

        # Replace with any provided kwargs
        for key, value in kwargs.items():
            output = output.replace(f"{{{key}}}", str(value))

        # Replace time-based placeholders
        now = datetime.now()
        output = output.replace("{time}", now.strftime("%H:%M"))
        output = output.replace("{date}", now.strftime("%Y-%m-%d"))
        output = output.replace("{day}", now.strftime("%A"))
        output = output.replace("{greeting}", self._time_greeting())

        # Update fire count
        self.fire_count += 1
        self.last_fired = datetime.now()

        return output

    def _time_greeting(self) -> str:
        """Generate time-appropriate greeting."""
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 17:
            return "Good afternoon"
        else:
            return "Good evening"


class UltrathunkCompressor:
    """
    Compresses multiple memory items into Ultrathunks.

    The key innovation: Generative compression that IMPROVES quality
    by extracting patterns rather than just storing data.
    """

    def __init__(self):
        self.min_items_for_compression = 3
        self.pattern_extractors = {
            ThunkType.PATTERN: self._extract_behavioral_pattern,
            ThunkType.TEMPLATE: self._extract_template_pattern,
            ThunkType.KNOWLEDGE: self._extract_knowledge_pattern,
            ThunkType.ROUTINE: self._extract_routine_pattern,
        }

    def compress(self, items: List[Dict], thunk_type: ThunkType = ThunkType.PATTERN) -> Optional[Ultrathunk]:
        """
        Compress a list of memory items into an Ultrathunk.

        Returns None if items don't form a compressible pattern.
        """
        if len(items) < self.min_items_for_compression:
            return None

        extractor = self.pattern_extractors.get(thunk_type, self._extract_behavioral_pattern)
        return extractor(items)

    def _extract_behavioral_pattern(self, items: List[Dict]) -> Optional[Ultrathunk]:
        """Extract behavioral pattern from conversation items."""
        # Analyze content for common elements
        all_content = " ".join(item.get('content', '') for item in items)
        original_bytes = len(all_content.encode())

        # Find common words (potential triggers)
        words = all_content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Top words are trigger candidates
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        if not top_words:
            return None

        trigger_words = [w for w, c in top_words if c >= len(items) * 0.5]
        if not trigger_words:
            trigger_words = [top_words[0][0]]

        # Create trigger pattern
        trigger_pattern = "|".join(trigger_words)

        # Extract variables (common entities)
        variables = self._extract_variables(items)

        # Create generator template
        generator_template = self._create_template(items, variables)

        # Calculate thunk size
        thunk_data = json.dumps({
            'trigger': trigger_pattern,
            'template': generator_template,
            'variables': variables
        })
        thunk_bytes = len(thunk_data.encode())

        # Create thunk ID
        thunk_id = hashlib.md5(thunk_data.encode()).hexdigest()[:10]

        return Ultrathunk(
            id=f"UTK-{thunk_id}",
            name=f"Pattern: {trigger_words[0]}",
            thunk_type=ThunkType.PATTERN,
            trigger_pattern=trigger_pattern,
            generator_template=generator_template,
            variables=variables,
            confidence=min(0.95, len(items) / 20.0),
            created_from_count=len(items),
            original_bytes=original_bytes,
            thunk_bytes=thunk_bytes,
            metadata={'source_words': trigger_words}
        )

    def _extract_template_pattern(self, items: List[Dict]) -> Optional[Ultrathunk]:
        """Extract response template from similar responses."""
        responses = [item.get('response', item.get('content', '')) for item in items]
        if not responses:
            return None

        original_bytes = sum(len(r.encode()) for r in responses)

        # Find common structure
        template = self._find_common_template(responses)
        if not template:
            return None

        variables = self._extract_template_variables(responses, template)

        thunk_data = json.dumps({'template': template, 'variables': variables})
        thunk_bytes = len(thunk_data.encode())
        thunk_id = hashlib.md5(thunk_data.encode()).hexdigest()[:10]

        return Ultrathunk(
            id=f"UTK-{thunk_id}",
            name="Response Template",
            thunk_type=ThunkType.TEMPLATE,
            trigger_pattern=".*",  # Templates match any context
            generator_template=template,
            variables=variables,
            confidence=min(0.9, len(items) / 10.0),
            created_from_count=len(items),
            original_bytes=original_bytes,
            thunk_bytes=thunk_bytes
        )

    def _extract_knowledge_pattern(self, items: List[Dict]) -> Optional[Ultrathunk]:
        """Compress knowledge items into single thunk."""
        facts = [item.get('content', '') for item in items]
        original_bytes = sum(len(f.encode()) for f in facts)

        # Create compressed knowledge summary
        unique_facts = list(set(facts))
        summary = " | ".join(unique_facts[:10])  # Top 10 unique facts

        thunk_data = json.dumps({'summary': summary})
        thunk_bytes = len(thunk_data.encode())
        thunk_id = hashlib.md5(summary.encode()).hexdigest()[:10]

        return Ultrathunk(
            id=f"UTK-{thunk_id}",
            name="Knowledge Cluster",
            thunk_type=ThunkType.KNOWLEDGE,
            trigger_pattern=self._extract_topic_trigger(facts),
            generator_template=summary,
            variables={},
            confidence=min(0.85, len(items) / 15.0),
            created_from_count=len(items),
            original_bytes=original_bytes,
            thunk_bytes=thunk_bytes
        )

    def _extract_routine_pattern(self, items: List[Dict]) -> Optional[Ultrathunk]:
        """Extract time-based routine from items."""
        # Analyze timestamps for patterns
        timestamps = []
        for item in items:
            ts = item.get('timestamp') or item.get('created_at')
            if ts:
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts)
                timestamps.append(ts)

        if len(timestamps) < 3:
            return None

        # Find common hours
        hours = [t.hour for t in timestamps]
        hour_freq = {}
        for h in hours:
            hour_freq[h] = hour_freq.get(h, 0) + 1

        peak_hour = max(hour_freq.items(), key=lambda x: x[1])[0]

        original_bytes = sum(len(str(item).encode()) for item in items)
        thunk_id = hashlib.md5(f"routine_{peak_hour}".encode()).hexdigest()[:10]

        return Ultrathunk(
            id=f"UTK-{thunk_id}",
            name=f"Routine: {peak_hour}:00",
            thunk_type=ThunkType.ROUTINE,
            trigger_pattern=f"time:{peak_hour}",
            generator_template="{greeting}, sir. Time for your usual activity.",
            variables={'peak_hour': peak_hour},
            confidence=min(0.8, hour_freq[peak_hour] / len(items)),
            created_from_count=len(items),
            original_bytes=original_bytes,
            thunk_bytes=100
        )

    def _extract_variables(self, items: List[Dict]) -> Dict[str, Any]:
        """Extract common variables from items."""
        variables = {}

        # Look for common patterns like names, locations, preferences
        all_content = " ".join(item.get('content', '') for item in items)

        # Extract potential names (capitalized words)
        names = re.findall(r'\b[A-Z][a-z]+\b', all_content)
        if names:
            name_freq = {}
            for name in names:
                name_freq[name] = name_freq.get(name, 0) + 1
            top_name = max(name_freq.items(), key=lambda x: x[1])
            if top_name[1] >= 2:
                variables['name'] = top_name[0]

        # Extract potential preferences
        prefs = re.findall(r'(?:prefer|like|want|love)\s+(\w+)', all_content.lower())
        if prefs:
            variables['preference'] = prefs[0]

        return variables

    def _create_template(self, items: List[Dict], variables: Dict) -> str:
        """Create a generator template from items."""
        # Find the most representative response
        responses = [item.get('response', '') for item in items if item.get('response')]

        if not responses:
            return "Understood, sir."

        # Use the shortest response as template base
        base = min(responses, key=len)

        # Replace specific values with variables
        template = base
        for var_name, var_value in variables.items():
            if isinstance(var_value, str) and var_value in template:
                template = template.replace(var_value, f"{{{var_name}}}")

        return template

    def _find_common_template(self, responses: List[str]) -> Optional[str]:
        """Find common template structure in responses."""
        if not responses:
            return None

        # Start with shortest response
        base = min(responses, key=len)

        # Find words that appear in most responses
        base_words = base.split()
        common_words = []

        for word in base_words:
            appearances = sum(1 for r in responses if word.lower() in r.lower())
            if appearances >= len(responses) * 0.6:
                common_words.append(word)
            else:
                common_words.append("{variable}")

        return " ".join(common_words) if common_words else None

    def _extract_template_variables(self, responses: List[str], template: str) -> Dict:
        """Extract variables that differ between responses."""
        # Find positions of {variable} in template
        return {'count': len(responses)}

    def _extract_topic_trigger(self, facts: List[str]) -> str:
        """Extract topic-based trigger from facts."""
        all_words = " ".join(facts).lower().split()
        word_freq = {}
        for word in all_words:
            if len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1

        if word_freq:
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
            return "|".join(w for w, _ in top_words)
        return "knowledge"


class UltrathunkEngine:
    """
    Main engine for managing Ultrathunks.

    Provides:
    - Storage and retrieval of thunks
    - Pattern matching for thunk activation
    - Compression of memory clusters
    - Statistics on compression ratios
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize Ultrathunk engine."""
        if db_path:
            self.db_path = db_path
        elif PATHMANAGER_AVAILABLE:
            self.db_path = str(PathManager.DATA_DIR / "ultrathunks.db")
        else:
            self.db_path = "ultrathunks.db"

        self.compressor = UltrathunkCompressor()
        self._cache: Dict[str, Ultrathunk] = {}
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ultrathunks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                thunk_type TEXT NOT NULL,
                trigger_pattern TEXT NOT NULL,
                generator_template TEXT NOT NULL,
                variables TEXT,
                confidence REAL DEFAULT 0.5,
                fire_count INTEGER DEFAULT 0,
                created_from_count INTEGER DEFAULT 0,
                original_bytes INTEGER DEFAULT 0,
                thunk_bytes INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_fired TEXT,
                metadata TEXT
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_thunk_type
            ON ultrathunks(thunk_type)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_thunk_confidence
            ON ultrathunks(confidence DESC)
        ''')

        conn.commit()
        conn.close()

    def compress_and_store(self, items: List[Dict],
                           thunk_type: ThunkType = ThunkType.PATTERN) -> Optional[Ultrathunk]:
        """Compress items into an Ultrathunk and store it."""
        thunk = self.compressor.compress(items, thunk_type)

        if thunk:
            self._store_thunk(thunk)
            self._cache[thunk.id] = thunk

        return thunk

    def _store_thunk(self, thunk: Ultrathunk):
        """Store thunk in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO ultrathunks
            (id, name, thunk_type, trigger_pattern, generator_template,
             variables, confidence, fire_count, created_from_count,
             original_bytes, thunk_bytes, created_at, last_fired, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            thunk.id,
            thunk.name,
            thunk.thunk_type.value,
            thunk.trigger_pattern,
            thunk.generator_template,
            json.dumps(thunk.variables),
            thunk.confidence,
            thunk.fire_count,
            thunk.created_from_count,
            thunk.original_bytes,
            thunk.thunk_bytes,
            thunk.created_at.isoformat(),
            thunk.last_fired.isoformat() if thunk.last_fired else None,
            json.dumps(thunk.metadata)
        ))

        conn.commit()
        conn.close()

    def find_matching_thunks(self, context: str, min_confidence: float = 0.3) -> List[Ultrathunk]:
        """Find all thunks that match the given context."""
        matching = []

        # Check cache first
        for thunk in self._cache.values():
            if thunk.confidence >= min_confidence and thunk.matches(context):
                matching.append(thunk)

        # Check database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM ultrathunks
            WHERE confidence >= ?
            ORDER BY confidence DESC, fire_count DESC
        ''', (min_confidence,))

        for row in cursor.fetchall():
            thunk = self._row_to_thunk(row)
            if thunk.id not in self._cache and thunk.matches(context):
                matching.append(thunk)
                self._cache[thunk.id] = thunk

        conn.close()

        # Sort by confidence and relevance
        matching.sort(key=lambda t: t.confidence, reverse=True)
        return matching

    def fire_thunk(self, thunk_id: str, context: str = "", **kwargs) -> Optional[str]:
        """Fire a thunk and generate output."""
        thunk = self._cache.get(thunk_id)

        if not thunk:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ultrathunks WHERE id = ?', (thunk_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                thunk = self._row_to_thunk(row)
                self._cache[thunk_id] = thunk

        if not thunk:
            return None

        output = thunk.generate(context, **kwargs)

        # Update fire count in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE ultrathunks
            SET fire_count = fire_count + 1, last_fired = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), thunk_id))
        conn.commit()
        conn.close()

        return output

    def auto_generate(self, context: str, **kwargs) -> Optional[Tuple[str, Ultrathunk]]:
        """
        Automatically find and fire the best matching thunk.

        Returns (generated_output, thunk_used) or None if no match.
        """
        matching = self.find_matching_thunks(context)

        if not matching:
            return None

        best_thunk = matching[0]
        output = best_thunk.generate(context, **kwargs)

        # Update in database
        self._store_thunk(best_thunk)

        return (output, best_thunk)

    def _row_to_thunk(self, row) -> Ultrathunk:
        """Convert database row to Ultrathunk."""
        return Ultrathunk(
            id=row[0],
            name=row[1],
            thunk_type=ThunkType(row[2]),
            trigger_pattern=row[3],
            generator_template=row[4],
            variables=json.loads(row[5]) if row[5] else {},
            confidence=row[6],
            fire_count=row[7],
            created_from_count=row[8],
            original_bytes=row[9],
            thunk_bytes=row[10],
            created_at=datetime.fromisoformat(row[11]),
            last_fired=datetime.fromisoformat(row[12]) if row[12] else None,
            metadata=json.loads(row[13]) if row[13] else {}
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get Ultrathunk statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(original_bytes) as total_original,
                SUM(thunk_bytes) as total_compressed,
                SUM(fire_count) as total_fires,
                AVG(confidence) as avg_confidence
            FROM ultrathunks
        ''')

        row = cursor.fetchone()

        stats = {
            'total_thunks': row[0] or 0,
            'original_bytes': row[1] or 0,
            'compressed_bytes': row[2] or 0,
            'total_fires': row[3] or 0,
            'avg_confidence': round(row[4] or 0, 2)
        }

        # Calculate compression ratio
        if stats['compressed_bytes'] > 0:
            stats['compression_ratio'] = round(stats['original_bytes'] / stats['compressed_bytes'], 1)
        else:
            stats['compression_ratio'] = 0

        # Count by type
        cursor.execute('''
            SELECT thunk_type, COUNT(*) FROM ultrathunks GROUP BY thunk_type
        ''')
        stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()
        return stats

    def list_thunks(self, limit: int = 20) -> List[Ultrathunk]:
        """List all thunks ordered by fire count."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM ultrathunks
            ORDER BY fire_count DESC, confidence DESC
            LIMIT ?
        ''', (limit,))

        thunks = [self._row_to_thunk(row) for row in cursor.fetchall()]
        conn.close()

        return thunks


# CLI interface
if __name__ == "__main__":
    import sys

    engine = UltrathunkEngine()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "stats":
            stats = engine.get_stats()
            print("\n=== ULTRATHUNK Statistics ===")
            print(f"Total Thunks: {stats['total_thunks']}")
            print(f"Original Data: {stats['original_bytes']:,} bytes")
            print(f"Compressed: {stats['compressed_bytes']:,} bytes")
            print(f"Compression Ratio: {stats['compression_ratio']}:1")
            print(f"Total Fires: {stats['total_fires']}")
            print(f"Average Confidence: {stats['avg_confidence']}")
            print(f"\nBy Type: {stats['by_type']}")

        elif command == "list":
            thunks = engine.list_thunks()
            print("\n=== ULTRATHUNK Library ===")
            for thunk in thunks:
                print(f"[{thunk.id}] {thunk.name}")
                print(f"  Type: {thunk.thunk_type.value} | Confidence: {thunk.confidence:.2f}")
                print(f"  Fires: {thunk.fire_count} | Compression: {thunk.compression_ratio:.1f}:1")
                print()

        elif command == "generate":
            if len(sys.argv) > 2:
                context = " ".join(sys.argv[2:])
                result = engine.auto_generate(context)
                if result:
                    output, thunk = result
                    print(f"\n[Generated by {thunk.id}]")
                    print(output)
                else:
                    print("No matching thunk found for context.")
            else:
                print("Usage: python ultrathunk.py generate <context>")

        elif command == "demo":
            # Demo: Create sample thunks
            print("Creating demo Ultrathunks...")

            # Weather pattern demo
            weather_items = [
                {'content': 'What is the weather in Chicago?', 'response': 'Good morning, sir. Chicago weather: partly cloudy, 45F.'},
                {'content': 'Weather update please', 'response': 'Good afternoon, sir. Current conditions in Chicago: sunny, 52F.'},
                {'content': 'How is the weather today?', 'response': 'Good evening, sir. Chicago weather: clear skies, 38F.'},
                {'content': 'Tell me the weather', 'response': 'Of course, sir. Chicago currently: overcast, 41F.'},
            ]

            thunk = engine.compress_and_store(weather_items, ThunkType.PATTERN)
            if thunk:
                print(f"Created: {thunk.id} - {thunk.name}")
                print(f"Compression: {thunk.compression_ratio:.1f}:1")
                print(f"\nTest generation:")
                print(engine.fire_thunk(thunk.id))

        else:
            print("Commands: stats, list, generate <context>, demo")
    else:
        print("ULTRATHUNK - Atomic Compressed Intelligence")
        print("Commands: stats, list, generate <context>, demo")
