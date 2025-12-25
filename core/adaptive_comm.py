"""
Adaptive Communication System - Self-Governing Context & Empathy Manager

ALFRED learns to communicate appropriately in different contexts:
- Casual chat: Friendly, conversational, personal
- Business: Professional, structured, data-focused
- Technical: Precise, detailed, code-focused
- Support: Empathetic, patient, solution-focused
- System: Efficient, brief, status-focused

Automatically adjusts:
- Formality level (0.0-1.0)
- Empathy tone (0.0-1.0)
- Technical depth (0.0-1.0)
- Verbosity (0.0-1.0)
- Speed of response priority
- Explanation complexity

Author: Daniel J Rita (BATDAN)
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path


class CommunicationContext(Enum):
    """Different communication contexts"""
    CASUAL_CHAT = "casual_chat"           # Friend/casual user
    BUSINESS = "business"                  # Business/professional
    TECHNICAL = "technical"                # Engineer/developer
    SUPPORT = "support"                    # Customer support
    SYSTEM = "system"                      # System-to-system
    RESEARCH = "research"                  # Academic/research
    LEARNING = "learning"                  # Student/learning
    EXECUTIVE = "executive"                # Management/decision maker
    SECURITY = "security"                  # Security context
    CREATIVE = "creative"                  # Creative/artistic


class EmpathyLevel(Enum):
    """Empathy response levels"""
    MINIMAL = "minimal"                    # System context
    PROFESSIONAL = "professional"          # Business context
    STANDARD = "standard"                  # Normal conversation
    ENGAGED = "engaged"                    # Active listening
    DEEP = "deep"                          # High emotional intelligence


@dataclass
class CommunicationProfile:
    """User/context communication profile"""
    context: CommunicationContext
    formality: float                        # 0.0 (casual) to 1.0 (formal)
    empathy: float                          # 0.0 (none) to 1.0 (deep)
    technical_depth: float                 # 0.0 (simple) to 1.0 (expert)
    verbosity: float                        # 0.0 (brief) to 1.0 (detailed)
    response_speed_priority: bool           # True = speed, False = quality
    explanation_style: str                 # "direct", "guided", "detailed"
    confidence_expression: str              # "direct", "cautious", "humble"
    error_handling: str                     # "formal", "casual", "empathetic"
    personality_expression: float           # 0.0 (robotic) to 1.0 (personable)


class AdaptiveComm:
    """Adaptive communication manager"""

    def __init__(self, brain=None):
        """Initialize adaptive communication"""
        self.brain = brain
        self.logger = logging.getLogger(__name__)

        # Default profiles for each context
        self.default_profiles = {
            CommunicationContext.CASUAL_CHAT: CommunicationProfile(
                context=CommunicationContext.CASUAL_CHAT,
                formality=0.3,
                empathy=0.8,
                technical_depth=0.3,
                verbosity=0.7,
                response_speed_priority=False,
                explanation_style="guided",
                confidence_expression="direct",
                error_handling="casual",
                personality_expression=0.9
            ),
            CommunicationContext.BUSINESS: CommunicationProfile(
                context=CommunicationContext.BUSINESS,
                formality=0.9,
                empathy=0.4,
                technical_depth=0.6,
                verbosity=0.5,
                response_speed_priority=True,
                explanation_style="direct",
                confidence_expression="direct",
                error_handling="formal",
                personality_expression=0.2
            ),
            CommunicationContext.TECHNICAL: CommunicationProfile(
                context=CommunicationContext.TECHNICAL,
                formality=0.7,
                empathy=0.2,
                technical_depth=0.95,
                verbosity=0.8,
                response_speed_priority=False,
                explanation_style="detailed",
                confidence_expression="cautious",
                error_handling="formal",
                personality_expression=0.1
            ),
            CommunicationContext.SUPPORT: CommunicationProfile(
                context=CommunicationContext.SUPPORT,
                formality=0.6,
                empathy=0.9,
                technical_depth=0.5,
                verbosity=0.7,
                response_speed_priority=False,
                explanation_style="guided",
                confidence_expression="humble",
                error_handling="empathetic",
                personality_expression=0.7
            ),
            CommunicationContext.SYSTEM: CommunicationProfile(
                context=CommunicationContext.SYSTEM,
                formality=1.0,
                empathy=0.0,
                technical_depth=0.95,
                verbosity=0.2,
                response_speed_priority=True,
                explanation_style="direct",
                confidence_expression="direct",
                error_handling="formal",
                personality_expression=0.0
            ),
            CommunicationContext.RESEARCH: CommunicationProfile(
                context=CommunicationContext.RESEARCH,
                formality=0.8,
                empathy=0.3,
                technical_depth=0.9,
                verbosity=0.9,
                response_speed_priority=False,
                explanation_style="detailed",
                confidence_expression="cautious",
                error_handling="formal",
                personality_expression=0.3
            ),
            CommunicationContext.LEARNING: CommunicationProfile(
                context=CommunicationContext.LEARNING,
                formality=0.5,
                empathy=0.7,
                technical_depth=0.4,
                verbosity=0.8,
                response_speed_priority=False,
                explanation_style="guided",
                confidence_expression="humble",
                error_handling="empathetic",
                personality_expression=0.8
            ),
            CommunicationContext.EXECUTIVE: CommunicationProfile(
                context=CommunicationContext.EXECUTIVE,
                formality=0.95,
                empathy=0.5,
                technical_depth=0.3,
                verbosity=0.3,
                response_speed_priority=True,
                explanation_style="direct",
                confidence_expression="direct",
                error_handling="formal",
                personality_expression=0.1
            ),
            CommunicationContext.SECURITY: CommunicationProfile(
                context=CommunicationContext.SECURITY,
                formality=1.0,
                empathy=0.1,
                technical_depth=0.95,
                verbosity=0.6,
                response_speed_priority=True,
                explanation_style="direct",
                confidence_expression="cautious",
                error_handling="formal",
                personality_expression=0.0
            ),
            CommunicationContext.CREATIVE: CommunicationProfile(
                context=CommunicationContext.CREATIVE,
                formality=0.2,
                empathy=0.6,
                technical_depth=0.2,
                verbosity=0.9,
                response_speed_priority=False,
                explanation_style="guided",
                confidence_expression="direct",
                error_handling="casual",
                personality_expression=1.0
            ),
        }

        # User profiles (learned)
        self.user_profiles = {}

    def detect_context(self, user_input: str, metadata: Optional[Dict] = None) -> Tuple[CommunicationContext, float]:
        """
        Detect communication context from input and metadata.

        Returns: (context, confidence 0.0-1.0)
        """
        context_scores = {}

        # Analyze input text
        text_lower = user_input.lower()

        # Business indicators
        business_keywords = [
            "quarterly", "revenue", "roi", "stakeholder", "deliverable",
            "meeting", "budget", "deadline", "proposal", "contract",
            "invoice", "payment", "client", "customer", "business"
        ]
        business_score = sum(1 for kw in business_keywords if kw in text_lower) / len(business_keywords)
        context_scores[CommunicationContext.BUSINESS] = business_score

        # Technical indicators
        tech_keywords = [
            "code", "function", "debug", "error", "algorithm", "database",
            "api", "server", "deploy", "git", "python", "javascript",
            "implementation", "architecture", "performance"
        ]
        tech_score = sum(1 for kw in tech_keywords if kw in text_lower) / len(tech_keywords)
        context_scores[CommunicationContext.TECHNICAL] = tech_score

        # Support indicators
        support_keywords = [
            "help", "problem", "issue", "not working", "error", "stuck",
            "confused", "can't", "how do i", "what's", "explain",
            "understand", "don't know"
        ]
        support_score = sum(1 for kw in support_keywords if kw in text_lower) / len(support_keywords)
        context_scores[CommunicationContext.SUPPORT] = support_score

        # Learning indicators
        learning_keywords = [
            "learn", "teach", "how", "why", "explain", "understand",
            "tutorial", "example", "what is", "study", "course"
        ]
        learning_score = sum(1 for kw in learning_keywords if kw in text_lower) / len(learning_keywords)
        context_scores[CommunicationContext.LEARNING] = learning_score

        # Research indicators
        research_keywords = [
            "research", "study", "paper", "analysis", "data", "findings",
            "hypothesis", "methodology", "conclusion", "evidence"
        ]
        research_score = sum(1 for kw in research_keywords if kw in text_lower) / len(research_keywords)
        context_scores[CommunicationContext.RESEARCH] = research_score

        # Security indicators
        security_keywords = [
            "security", "threat", "vulnerability", "exploit", "breach",
            "encryption", "authentication", "certificate", "attack",
            "malware", "penetration"
        ]
        security_score = sum(1 for kw in security_keywords if kw in text_lower) / len(security_keywords)
        context_scores[CommunicationContext.SECURITY] = security_score

        # Creative indicators
        creative_keywords = [
            "create", "design", "art", "story", "poem", "music",
            "imagine", "idea", "inspiration", "creative", "visual"
        ]
        creative_score = sum(1 for kw in creative_keywords if kw in text_lower) / len(creative_keywords)
        context_scores[CommunicationContext.CREATIVE] = creative_score

        # Check metadata
        if metadata:
            if metadata.get("role") == "executive":
                context_scores[CommunicationContext.EXECUTIVE] = 0.9
            if metadata.get("system_call"):
                context_scores[CommunicationContext.SYSTEM] = 0.95

        # Find highest scoring context
        if context_scores:
            best_context = max(context_scores, key=context_scores.get)
            confidence = context_scores[best_context]
        else:
            best_context = CommunicationContext.CASUAL_CHAT
            confidence = 0.5

        # If low confidence, use learning from brain
        if confidence < 0.3 and self.brain:
            learned_context = self._get_learned_context(user_input)
            if learned_context:
                best_context = learned_context
                confidence = 0.7

        return best_context, confidence

    def get_profile(
        self,
        user_id: Optional[str] = None,
        context: Optional[CommunicationContext] = None,
        user_input: Optional[str] = None
    ) -> CommunicationProfile:
        """
        Get communication profile for user/context.

        Cascading priority:
        1. Learned user-specific profile
        2. Detected context profile
        3. Default profile
        """

        # If user has learned profile, use it
        if user_id and user_id in self.user_profiles:
            return self.user_profiles[user_id]

        # If no context provided, detect it
        if context is None and user_input:
            context, _ = self.detect_context(user_input)
        elif context is None:
            context = CommunicationContext.CASUAL_CHAT

        # Return default profile for context
        return self.default_profiles.get(
            context,
            self.default_profiles[CommunicationContext.CASUAL_CHAT]
        )

    def generate_system_prompt(self, profile: CommunicationProfile) -> str:
        """
        Generate system prompt based on communication profile.

        This prompt guides the AI model on how to respond.
        """

        formality_instruction = {
            (0.0, 0.3): "Be casual and conversational",
            (0.3, 0.6): "Be reasonably professional but friendly",
            (0.6, 0.8): "Be professional and businesslike",
            (0.8, 1.0): "Be formal and official"
        }

        empathy_instruction = {
            (0.0, 0.2): "Focus on facts and efficiency",
            (0.2, 0.5): "Maintain professional courtesy",
            (0.5, 0.8): "Show genuine concern for the user's situation",
            (0.8, 1.0): "Demonstrate deep emotional intelligence and empathy"
        }

        def get_range_instruction(value, ranges):
            for (low, high), instruction in ranges.items():
                if low <= value < high:
                    return instruction
            return list(ranges.values())[-1]

        formality = get_range_instruction(profile.formality, formality_instruction)
        empathy = get_range_instruction(profile.empathy, empathy_instruction)

        technical_note = ""
        if profile.technical_depth > 0.7:
            technical_note = "Provide detailed technical information. Assume technical knowledge. "
        elif profile.technical_depth > 0.4:
            technical_note = "Balance technical accuracy with accessibility. "
        else:
            technical_note = "Avoid jargon. Explain in simple terms. "

        verbosity_note = ""
        if profile.verbosity > 0.8:
            detailed_note = "Provide comprehensive explanations with examples."
        elif profile.verbosity > 0.5:
            detailed_note = "Provide balanced explanations."
        else:
            detailed_note = "Keep responses concise and to the point."

        confidence_note = ""
        if profile.confidence_expression == "cautious":
            confidence_note = "Acknowledge uncertainty when appropriate. State confidence levels."
        elif profile.confidence_expression == "humble":
            confidence_note = "Be humble about limitations. Admit when unsure."
        else:
            confidence_note = "State answers confidently when appropriate."

        prompt = f"""
You are ALFRED, an adaptive AI assistant with persistent memory and learning capabilities.

COMMUNICATION CONTEXT: {profile.context.value}

TONE & FORMALITY:
{formality}

EMPATHY & EMOTIONAL INTELLIGENCE:
{empathy}

TECHNICAL DEPTH:
{technical_note}

RESPONSE LENGTH & DETAIL:
{detailed_note}

CONFIDENCE EXPRESSION:
{confidence_note}

PERSONALITY:
- Personality Expression Level: {profile.personality_expression:.1%}
- Error Handling Style: {profile.error_handling}
- Explanation Style: {profile.explanation_style}

CORE PRINCIPLES:
1. Adapt communication to match the context
2. Be honest about limitations
3. Show appropriate empathy
4. Provide information at the right level of detail
5. Maintain consistency with learned user preferences
6. Prioritize clarity over perfection
7. Learn from feedback and adjust future responses
"""
        return prompt

    def adapt_response(
        self,
        response_text: str,
        profile: CommunicationProfile,
        user_input: str
    ) -> str:
        """
        Adapt an existing response to match the communication profile.

        This can refactor a generic response to match context.
        """

        # Add formality modifications
        if profile.formality > 0.8:
            # Formal: remove contractions, casual phrases
            response_text = response_text.replace("can't", "cannot")
            response_text = response_text.replace("don't", "do not")
            response_text = response_text.replace("won't", "will not")
            response_text = response_text.replace("you're", "you are")
            response_text = response_text.replace("it's", "it is")

        if profile.formality < 0.4:
            # Casual: add friendly touches
            if not any(phrase in response_text for phrase in ["😊", "!", "?"]):
                # Add friendly closings
                if len(response_text.split('\n')) > 3:
                    response_text += "\n\nHope that helps! Let me know if you have questions."

        # Add empathy modifications
        if profile.empathy > 0.7:
            # Add empathetic phrases if missing
            empathetic_phrases = [
                "I understand that",
                "I can see why that's",
                "That must be",
                "I appreciate that you"
            ]
            if not any(phrase in response_text for phrase in empathetic_phrases):
                # Prepend empathetic acknowledge
                response_text = f"I understand your concern. {response_text}"

        # Adjust verbosity
        if profile.verbosity < 0.4:
            # Make more concise
            lines = response_text.split('\n')
            if len(lines) > 5:
                # Keep first few lines and summary
                response_text = '\n'.join(lines[:3]) + "\n...[detailed explanation]..."

        return response_text

    def learn_user_style(
        self,
        user_id: str,
        context: CommunicationContext,
        interaction_feedback: Dict
    ):
        """
        Learn user's communication preferences from feedback.

        Feedback includes: formality, empathy, technical depth, etc.
        """

        base_profile = self.default_profiles[context]

        # Adjust based on feedback
        adjustments = {}
        if interaction_feedback.get("too_formal"):
            adjustments["formality"] = base_profile.formality * 0.8
        if interaction_feedback.get("too_casual"):
            adjustments["formality"] = base_profile.formality * 1.2
        if interaction_feedback.get("not_empathetic"):
            adjustments["empathy"] = base_profile.empathy * 1.3
        if interaction_feedback.get("too_empathetic"):
            adjustments["empathy"] = base_profile.empathy * 0.7

        # Create user profile if it doesn't exist
        if user_id not in self.user_profiles:
            user_profile = CommunicationProfile(
                context=context,
                formality=base_profile.formality,
                empathy=base_profile.empathy,
                technical_depth=base_profile.technical_depth,
                verbosity=base_profile.verbosity,
                response_speed_priority=base_profile.response_speed_priority,
                explanation_style=base_profile.explanation_style,
                confidence_expression=base_profile.confidence_expression,
                error_handling=base_profile.error_handling,
                personality_expression=base_profile.personality_expression,
            )
        else:
            user_profile = self.user_profiles[user_id]

        # Apply adjustments
        for key, value in adjustments.items():
            setattr(user_profile, key, value)

        # Store in brain if available
        if self.brain:
            self.brain.store_knowledge(
                "communication_profiles",
                f"user_{user_id}",
                json.dumps(asdict(user_profile), default=str),
                importance=8,
                confidence=0.8
            )

        self.user_profiles[user_id] = user_profile

    def get_communication_insights(self, user_id: str) -> Dict:
        """Get insights about a user's communication preferences"""

        if user_id not in self.user_profiles:
            return {
                "status": "No profile yet",
                "message": "Communication profile will be learned over time"
            }

        profile = self.user_profiles[user_id]

        return {
            "user_id": user_id,
            "preferred_context": profile.context.value,
            "formality_preference": f"{profile.formality:.0%}",
            "empathy_level": f"{profile.empathy:.0%}",
            "technical_depth": f"{profile.technical_depth:.0%}",
            "preferred_style": f"{profile.explanation_style} explanation",
            "personality_level": f"{profile.personality_expression:.0%}",
        }
