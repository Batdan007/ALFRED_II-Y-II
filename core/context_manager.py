"""
Context Manager - Manages conversation context for Alfred Brain
Provides intelligent context window management and relevance filtering
Author: Daniel J Rita (BATDAN)
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


class ContextManager:
    """
    Manages conversation context for AI interactions.

    Key Features:
    - Smart context window management
    - Relevance-based filtering
    - Token counting and limits
    - Topic-based context retrieval
    - Automatic context summarization
    """

    def __init__(self, brain, max_tokens: int = 4000, max_messages: int = 10):
        """
        Initialize context manager

        Args:
            brain: AlfredBrain instance
            max_tokens: Maximum tokens for context (default: 4000)
            max_messages: Maximum number of messages to include (default: 10)
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.max_tokens = max_tokens
        self.max_messages = max_messages

    def get_context(self,
                   limit: Optional[int] = None,
                   topic: Optional[str] = None,
                   time_window: Optional[timedelta] = None,
                   include_knowledge: bool = True) -> str:
        """
        Get conversation context for AI

        Args:
            limit: Number of recent conversations (default: max_messages)
            topic: Optional topic filter
            time_window: Optional time window (e.g., timedelta(hours=1))
            include_knowledge: Include relevant knowledge from brain

        Returns:
            Formatted context string for AI
        """
        limit = limit or self.max_messages

        # Get recent conversations from brain
        conversations = self.brain.get_conversation_context(limit=limit)

        # Filter by topic if specified
        if topic:
            conversations = self._filter_by_topic(conversations, topic)

        # Filter by time window if specified
        if time_window:
            conversations = self._filter_by_time(conversations, time_window)

        # Build context string
        context_parts = []

        # Add conversation history
        if conversations:
            context_parts.append("=== Recent Conversation ===")
            for conv in conversations:
                context_parts.append(f"User: {conv.get('user_input', '')}")
                context_parts.append(f"Alfred: {conv.get('ai_response', '')}")

        # Add relevant knowledge if requested
        if include_knowledge and conversations:
            # Extract topics from recent conversations
            topics = self._extract_topics(conversations)
            relevant_knowledge = self._get_relevant_knowledge(topics)

            if relevant_knowledge:
                context_parts.append("\n=== Relevant Knowledge ===")
                for knowledge in relevant_knowledge:
                    context_parts.append(
                        f"{knowledge['category']}/{knowledge['key']}: {knowledge['value']}"
                    )

        # Join and ensure token limit
        full_context = "\n".join(context_parts)
        return self._truncate_to_token_limit(full_context)

    def get_smart_context(self, current_input: str) -> str:
        """
        Get smart context based on current input

        Analyzes current input to determine:
        - Relevant past conversations
        - Related knowledge
        - Appropriate context length

        Args:
            current_input: User's current message

        Returns:
            Optimized context string
        """
        # Detect if this is a new topic or continuation
        is_new_topic = self._is_new_topic(current_input)

        if is_new_topic:
            # New topic: less history, more knowledge
            limit = 3
            include_knowledge = True
        else:
            # Continuing: more history
            limit = self.max_messages
            include_knowledge = False

        # Extract potential topics from input
        topics = self._extract_topics_from_text(current_input)

        # Build context
        context = self.get_context(
            limit=limit,
            topic=topics[0] if topics else None,
            include_knowledge=include_knowledge
        )

        return context

    def _filter_by_topic(self, conversations: List[Dict], topic: str) -> List[Dict]:
        """Filter conversations by topic"""
        # In a full implementation, this would use more sophisticated topic matching
        return [
            conv for conv in conversations
            if topic.lower() in conv.get('user_input', '').lower()
            or topic.lower() in conv.get('ai_response', '').lower()
        ]

    def _filter_by_time(self, conversations: List[Dict], window: timedelta) -> List[Dict]:
        """Filter conversations by time window"""
        cutoff = datetime.now() - window
        return [
            conv for conv in conversations
            if datetime.fromisoformat(conv.get('timestamp', ''))  > cutoff
        ]

    def _extract_topics(self, conversations: List[Dict]) -> List[str]:
        """Extract topics from conversations"""
        # Simple implementation - could be enhanced with NLP
        topics = set()
        for conv in conversations:
            # Extract key words (simplified)
            text = conv.get('user_input', '') + ' ' + conv.get('ai_response', '')
            words = text.lower().split()
            # Filter for potential topic words (longer than 5 chars)
            topics.update([w for w in words if len(w) > 5])

        return list(topics)[:5]  # Top 5 topics

    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simple keyword extraction
        words = text.lower().split()
        return [w for w in words if len(w) > 5][:3]

    def _get_relevant_knowledge(self, topics: List[str]) -> List[Dict]:
        """Get relevant knowledge from brain based on topics"""
        # Query brain for knowledge related to topics
        # Simplified implementation
        all_knowledge = []
        for topic in topics:
            try:
                knowledge = self.brain.get_knowledge("topics", topic)
                if knowledge:
                    all_knowledge.append({
                        'category': 'topics',
                        'key': topic,
                        'value': knowledge
                    })
            except:
                pass

        return all_knowledge[:5]  # Limit to 5 knowledge items

    def _is_new_topic(self, current_input: str) -> bool:
        """Determine if current input is a new topic"""
        # Get most recent conversation
        recent = self.brain.get_conversation_context(limit=1)

        if not recent:
            return True

        # Compare current input with recent conversation
        last_input = recent[0].get('user_input', '')

        # Simple heuristic: if very different, it's a new topic
        # Could be enhanced with embeddings/similarity
        common_words = set(current_input.lower().split()) & set(last_input.lower().split())
        similarity = len(common_words) / max(len(current_input.split()), len(last_input.split()))

        return similarity < 0.3  # Less than 30% word overlap = new topic

    def _truncate_to_token_limit(self, text: str) -> str:
        """Truncate text to fit within token limit"""
        # Simple approximation: 1 token ≈ 4 characters
        max_chars = self.max_tokens * 4

        if len(text) <= max_chars:
            return text

        # Truncate and add indicator
        self.logger.warning(f"Context truncated from {len(text)} to {max_chars} chars")
        return text[:max_chars] + "\n\n[Context truncated to fit token limit]"

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4

    def summarize_old_context(self, age_threshold: timedelta = timedelta(hours=24)) -> str:
        """
        Summarize old conversations for efficient context storage

        Args:
            age_threshold: Age threshold for summarization

        Returns:
            Summary of old conversations
        """
        cutoff = datetime.now() - age_threshold

        # Get old conversations
        all_conversations = self.brain.get_conversation_context(limit=100)
        old_conversations = [
            conv for conv in all_conversations
            if datetime.fromisoformat(conv.get('timestamp', '')) < cutoff
        ]

        if not old_conversations:
            return ""

        # Create summary
        summary_parts = [
            f"=== Summary of {len(old_conversations)} older conversations ===",
            f"Time range: {old_conversations[-1].get('timestamp')} to {old_conversations[0].get('timestamp')}",
            "\nKey topics discussed:"
        ]

        # Extract and list topics
        topics = self._extract_topics(old_conversations)
        for topic in topics[:10]:
            summary_parts.append(f"  - {topic}")

        return "\n".join(summary_parts)

    def get_status(self) -> Dict:
        """Get context manager status"""
        recent_convs = self.brain.get_conversation_context(limit=self.max_messages)

        return {
            'max_tokens': self.max_tokens,
            'max_messages': self.max_messages,
            'recent_conversations': len(recent_convs),
            'topics_tracked': len(self._extract_topics(recent_convs)) if recent_convs else 0
        }


# Convenience function
def create_context_manager(brain, max_tokens: int = 4000) -> ContextManager:
    """Create a context manager with specified settings"""
    return ContextManager(brain=brain, max_tokens=max_tokens)
