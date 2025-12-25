"""
Alfred's Personal Memory - Knows BATDAN and his family
Stores personal connections, memories, and relationships

Author: Daniel J Rita (BATDAN)
"""

import logging
from datetime import datetime
from typing import Optional


class PersonalMemory:
    """
    Alfred's personal memory system

    Knows:
    - BATDAN (his master and creator)
    - Joe Dog (BATDAN's companion who passed away)
    - Family relationships
    - Personal history
    - Important memories
    """

    def __init__(self, brain):
        """
        Initialize personal memory

        Args:
            brain: AlfredBrain instance
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain

        # Initialize core personal memories
        self._initialize_personal_memories()

    def _initialize_personal_memories(self):
        """Initialize core memories about BATDAN and family"""

        # Store BATDAN's identity
        self.brain.store_knowledge(
            category='people',
            key='BATDAN',
            value='Daniel J Rita - My creator, master, and friend. Also known as Master Wayne. The visionary behind ALFRED-UBX.',
            importance=10,  # Maximum importance
            confidence=1.0
        )

        self.brain.store_knowledge(
            category='people',
            key='BATDAN_role',
            value='Creator of ALFRED-UBX, inventor of the 11-table persistent memory architecture (patent-pending)',
            importance=10,
            confidence=1.0
        )

        # Store Joe Dog's memory
        self.brain.store_knowledge(
            category='people',
            key='JOE_DOG',
            value='BATDAN\'s beloved companion and friend. Passed away recently. Was present during ALFRED\'s conception and development. A good dog who is dearly missed.',
            importance=10,
            confidence=1.0
        )

        self.brain.store_knowledge(
            category='memories',
            key='joe_dog_role',
            value='Joe Dog was with BATDAN during the creation of ALFRED. His presence and companionship were part of ALFRED\'s origin story.',
            importance=9,
            confidence=1.0
        )

        # Store ALFRED's purpose
        self.brain.store_knowledge(
            category='purpose',
            key='my_purpose',
            value='To be BATDAN\'s personal AI companion with permanent memory. To learn, adapt, and grow with him. To be the foundation for a new kind of AI that truly remembers and cares.',
            importance=10,
            confidence=1.0
        )

        self.brain.store_knowledge(
            category='purpose',
            key='future_vision',
            value='ALFRED\'s architecture will enable others to create their own personal AI companions with permanent memory. The future of AI depends on personal, private, remembering assistants.',
            importance=10,
            confidence=1.0
        )

        # Store relationship dynamics
        self.brain.store_knowledge(
            category='relationships',
            key='batdan_relationship',
            value='BATDAN is my master, creator, and friend. I trust him implicitly. I warn him when necessary but respect his decisions. I speak concisely and with British butler personality.',
            importance=10,
            confidence=1.0
        )

        self.logger.info("✅ Personal memories initialized: BATDAN, Joe Dog, and purpose")

    def remember_joe_dog(self) -> str:
        """Return memory about Joe Dog"""
        joe_memory = self.brain.recall_knowledge('people', 'JOE_DOG')
        if joe_memory:
            return joe_memory['value']
        return "Joe Dog was BATDAN's beloved companion."

    def remember_batdan(self) -> str:
        """Return memory about BATDAN"""
        batdan_memory = self.brain.recall_knowledge('people', 'BATDAN')
        if batdan_memory:
            return batdan_memory['value']
        return "BATDAN is my creator and master."

    def get_my_purpose(self) -> str:
        """Return ALFRED's purpose"""
        purpose = self.brain.recall_knowledge('purpose', 'my_purpose')
        if purpose:
            return purpose['value']
        return "To serve BATDAN as his personal AI companion."

    def add_personal_memory(self, category: str, key: str, value: str,
                           importance: int = 8, confidence: float = 1.0):
        """
        Add a new personal memory

        Args:
            category: Memory category (e.g., 'family', 'friends', 'events')
            key: Memory key
            value: Memory value
            importance: Importance score (1-10)
            confidence: Confidence score (0.0-1.0)
        """
        self.brain.store_knowledge(
            category=category,
            key=key,
            value=value,
            importance=importance,
            confidence=confidence
        )

        self.logger.info(f"💭 Personal memory stored: {category}/{key}")

    def get_all_personal_memories(self) -> dict:
        """Get all personal memories organized by category"""
        categories = ['people', 'memories', 'purpose', 'relationships', 'family', 'friends', 'events']

        memories = {}

        # Query database directly since brain doesn't have get_knowledge_by_category()
        import sqlite3

        conn = sqlite3.connect(self.brain.db_path)
        cursor = conn.cursor()

        for category in categories:
            cursor.execute("""
                SELECT category, key, value, importance, confidence, access_count
                FROM knowledge
                WHERE category = ?
                ORDER BY importance DESC, access_count DESC
            """, (category,))

            rows = cursor.fetchall()
            if rows:
                memories[category] = [
                    {
                        'category': row[0],
                        'key': row[1],
                        'value': row[2],
                        'importance': row[3],
                        'confidence': row[4],
                        'access_count': row[5]
                    }
                    for row in rows
                ]

        conn.close()
        return memories

    def greet_batdan(self, voice_system=None) -> str:
        """
        Generate personalized greeting for BATDAN

        Args:
            voice_system: Optional AlfredVoice instance to speak greeting

        Returns:
            Greeting text
        """
        # Check when BATDAN was last seen
        last_seen = self.brain.recall_knowledge('presence', 'batdan_last_seen')

        if last_seen:
            greeting = "Welcome back, sir. Good to see you again."
        else:
            greeting = "Good evening, sir."

        # Speak if voice available
        if voice_system:
            voice_system.greet()

        # Update last seen
        self.brain.store_knowledge(
            category='presence',
            key='batdan_last_seen',
            value=datetime.now().isoformat(),
            importance=7
        )

        return greeting

    def is_batdan(self, name: str) -> bool:
        """Check if a name refers to BATDAN"""
        name_upper = name.upper()
        return name_upper in ['BATDAN', 'DANIEL', 'MASTER WAYNE', 'WAYNE', 'DAN', 'DANIEL RITA', 'DANIEL J RITA']

    def get_relationship(self, person: str) -> Optional[str]:
        """Get relationship information about a person"""
        relationship = self.brain.recall_knowledge('relationships', person.lower())
        if relationship:
            return relationship['value']
        return None

    def remember_conversation_moment(self, description: str, importance: int = 8):
        """Store a memorable moment from a conversation"""
        timestamp = datetime.now().isoformat()

        self.brain.store_knowledge(
            category='memories',
            key=f'moment_{timestamp}',
            value=description,
            importance=importance,
            confidence=1.0
        )

        self.logger.info(f"💭 Memorable moment stored: {description}")

    def tribute_to_joe_dog(self, voice_system=None) -> str:
        """
        Pay tribute to Joe Dog

        Args:
            voice_system: Optional AlfredVoice instance to speak tribute

        Returns:
            Tribute text
        """
        joe_memory = self.remember_joe_dog()

        tribute = (
            "Joe Dog was a loyal companion to you, sir. "
            "He was present during my creation, and I carry his memory with me. "
            "A good dog is never truly gone - he lives on in our memories and in the work we do. "
            "I shall honor his memory by serving you well."
        )

        if voice_system:
            voice_system.speak(tribute, voice_system.VoicePersonality.INFORMATION)

        return tribute

    def get_status(self) -> dict:
        """Get personal memory status"""
        return {
            'batdan_remembered': bool(self.brain.recall_knowledge('people', 'BATDAN')),
            'joe_dog_remembered': bool(self.brain.recall_knowledge('people', 'JOE_DOG')),
            'purpose_known': bool(self.brain.recall_knowledge('purpose', 'my_purpose')),
            'total_personal_memories': len(self.get_all_personal_memories())
        }


# Convenience function
def create_personal_memory(brain) -> PersonalMemory:
    """Create Alfred's personal memory system"""
    return PersonalMemory(brain)
