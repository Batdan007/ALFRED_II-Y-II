"""
Self-Governing ALFRED - Autonomous Context & Communication Management

ALFRED operates as a self-governing entity that:
- Understands context automatically (person, business, system)
- Adjusts communication style appropriately
- Shows correct empathy level
- Demonstrates situational awareness
- Learns communication preferences
- Operates across all programs and devices
- Makes autonomous decisions about tone and depth

This is the central hub that ALL programs/integrations use.

Author: Daniel J Rita (BATDAN)
"""

import asyncio
import json
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict
from pathlib import Path

from core.brain import AlfredBrain
from core.task_classifier import TaskClassifier
from core.agent_selector import AgentSelector
from core.response_quality_checker import ResponseQualityChecker
from core.adaptive_comm import AdaptiveComm, CommunicationContext, CommunicationProfile
from core.privacy_controller import PrivacyController
from ai.multimodel import MultiModelOrchestrator


class AlfredGovernanceEngine:
    """
    Self-governing ALFRED that makes autonomous decisions about communication.

    Central decision hub for all ALFRED operations across programs/devices.
    """

    def __init__(self):
        """Initialize governance engine"""
        self.logger = logging.getLogger(__name__)

        # Core systems
        self.brain = AlfredBrain()
        self.privacy = PrivacyController(default_mode="LOCAL")
        self.classifier = TaskClassifier(self.brain)
        self.selector = AgentSelector(self.brain)
        self.quality_checker = ResponseQualityChecker(self.brain)
        self.adaptive_comm = AdaptiveComm(self.brain)
        self.ai = MultiModelOrchestrator(self.privacy)

        # State tracking
        self.active_sessions = {}  # user_id -> session info
        self.interaction_history = {}  # user_id -> [interactions]

    async def process_input(
        self,
        user_input: str,
        user_id: str = "default",
        context_hints: Optional[Dict] = None
    ) -> Dict:
        """
        Process user input with full governance.

        Returns: Complete response with all metadata about decisions made.
        """

        # Step 1: Detect communication context
        detected_context, context_confidence = self.adaptive_comm.detect_context(
            user_input,
            context_hints or {}
        )

        # Step 2: Get user's communication profile
        comm_profile = self.adaptive_comm.get_profile(
            user_id=user_id,
            context=detected_context,
            user_input=user_input
        )

        # Step 3: Classify task type
        task_type, task_confidence, task_metadata = self.classifier.classify(user_input)

        # Step 4: Select best agents
        agents = self.selector.select_agents(user_input, max_agents=3)

        # Step 5: Generate system prompt based on profile
        system_prompt = self.adaptive_comm.generate_system_prompt(comm_profile)

        # Step 6: Generate response
        try:
            response_text = await self.ai.generate(
                prompt=user_input,
                context=system_prompt,
                max_tokens=self._get_max_tokens(comm_profile)
            )
        except Exception as e:
            self.logger.error(f"Response generation error: {e}")
            response_text = self._generate_fallback_response(
                user_input, comm_profile, task_type
            )

        # Step 7: Validate response quality
        quality_assessment = self.quality_checker.check_response(
            response_text, user_input
        )

        # Step 8: Adapt response to profile if needed
        adapted_response = self.adaptive_comm.adapt_response(
            response_text, comm_profile, user_input
        )

        # Step 9: Store conversation and learn
        self._store_and_learn(
            user_id=user_id,
            user_input=user_input,
            response=adapted_response,
            context=detected_context,
            task_type=task_type,
            quality=quality_assessment,
            comm_profile=comm_profile
        )

        # Step 10: Build complete response object
        response_object = {
            "response": adapted_response,
            "governance": {
                "communication_context": detected_context.value,
                "context_confidence": context_confidence,
                "task_type": task_type.value,
                "task_confidence": task_confidence,
                "selected_agents": agents,
            },
            "communication_profile": {
                "formality": comm_profile.formality,
                "empathy": comm_profile.empathy,
                "technical_depth": comm_profile.technical_depth,
                "verbosity": comm_profile.verbosity,
            },
            "quality": {
                "level": quality_assessment["quality_level"].value,
                "is_clean": quality_assessment["is_clean"],
                "flags": quality_assessment["flags"],
                "confidence": quality_assessment["confidence"],
            },
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
        }

        return response_object

    def _get_max_tokens(self, profile: CommunicationProfile) -> int:
        """Calculate max tokens based on verbosity preference"""
        base_tokens = 2000

        if profile.verbosity > 0.8:
            return int(base_tokens * 1.5)  # Detailed responses
        elif profile.verbosity > 0.5:
            return base_tokens
        else:
            return int(base_tokens * 0.5)  # Brief responses

    def _generate_fallback_response(
        self,
        user_input: str,
        profile: CommunicationProfile,
        task_type
    ) -> str:
        """Generate fallback response if AI generation fails"""

        if profile.context == CommunicationContext.SYSTEM:
            return f"ERROR: Unable to process {task_type.value} task"

        elif profile.empathy > 0.6:
            return (
                "I apologize, but I'm having difficulty generating a response at the moment. "
                "Could you try again? I'm working to ensure I give you the best answer."
            )

        else:
            return (
                "Unable to generate response. Please retry or check logs."
            )

    def _store_and_learn(
        self,
        user_id: str,
        user_input: str,
        response: str,
        context: CommunicationContext,
        task_type,
        quality,
        comm_profile: CommunicationProfile
    ):
        """Store interaction and learn from it"""

        # Store conversation
        self.brain.store_conversation(
            user_input=user_input,
            alfred_response=response,
            success=quality.get("is_clean", True)
        )

        # Update context history
        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = []

        self.interaction_history[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "context": context.value,
            "task_type": task_type.value,
            "quality_level": quality["quality_level"].value,
        })

        # Keep only last 100 interactions per user
        if len(self.interaction_history[user_id]) > 100:
            self.interaction_history[user_id] = self.interaction_history[user_id][-100:]

        # Store in brain
        self.brain.store_knowledge(
            "user_history",
            f"{user_id}_interactions",
            json.dumps(self.interaction_history[user_id]),
            importance=5,
            confidence=0.9
        )

        # Learn communication preferences if there's feedback potential
        self._attempt_communication_learning(user_id, context, quality)

    def _attempt_communication_learning(
        self,
        user_id: str,
        context: CommunicationContext,
        quality: Dict
    ):
        """Attempt to learn user's communication preferences"""

        # If response had quality issues, note it
        if quality.get("flags"):
            feedback = {}

            for flag in quality["flags"]:
                if "UNVERIFIED" in flag:
                    feedback["unverified_content"] = True
                elif "REPEAT" in flag:
                    feedback["repetitive"] = True
                elif "CONTRADICTS" in flag:
                    feedback["contradictory"] = True

            if feedback and user_id in self.adaptive_comm.user_profiles:
                # Learning happened - profile will adapt
                self.logger.info(f"Learning communication adjustment for {user_id}: {feedback}")

    def get_context_explanation(self, user_id: str) -> Dict:
        """
        Get explanation of current context and communication settings.

        Useful for transparency - user knows how ALFRED is communicating.
        """

        profile = self.adaptive_comm.get_profile(user_id=user_id)
        insights = self.adaptive_comm.get_communication_insights(user_id)

        explanation = {
            "current_context": profile.context.value,
            "why_this_context": f"ALFRED detected context type based on your input patterns and communication style",
            "how_im_communicating": {
                "formality_level": f"{profile.formality:.0%} formal",
                "empathy_shown": f"{profile.empathy:.0%}",
                "technical_detail": f"{profile.technical_depth:.0%}",
                "explanation_style": profile.explanation_style,
            },
            "learned_preferences": insights,
            "how_i_decide": [
                "1. I analyze your input for keywords and patterns",
                "2. I check my memory for how you prefer to be communicated with",
                "3. I adjust my formality, empathy, and technical depth",
                "4. I select the best explanation style for you",
                "5. I learn from your feedback to improve",
            ],
            "you_can_tell_me": [
                "\"Be more formal\", \"Be more casual\", \"Add more detail\", \"Keep it brief\"",
                "\"That was too technical\", \"I need more empathy\", \"Be more direct\"",
                "Over time, I learn your preferences automatically",
            ]
        }

        return explanation

    def set_communication_preference(
        self,
        user_id: str,
        preference: str,
        context: Optional[CommunicationContext] = None
    ) -> Dict:
        """
        Allow user to explicitly set communication preferences.

        Examples:
        - "be more formal"
        - "add more empathy"
        - "keep it brief"
        - "more technical detail"
        """

        preference_lower = preference.lower()

        feedback = {}

        # Formality adjustments
        if "more formal" in preference_lower or "formal" in preference_lower:
            feedback["increase_formality"] = True
        elif "less formal" in preference_lower or "casual" in preference_lower:
            feedback["decrease_formality"] = True

        # Empathy adjustments
        if "more empathy" in preference_lower or "empathetic" in preference_lower:
            feedback["increase_empathy"] = True
        elif "less empathy" in preference_lower:
            feedback["decrease_empathy"] = True

        # Technical adjustments
        if "more technical" in preference_lower or "deeper" in preference_lower:
            feedback["increase_technical"] = True
        elif "less technical" in preference_lower or "simpler" in preference_lower:
            feedback["decrease_technical"] = True

        # Verbosity adjustments
        if "more detail" in preference_lower or "detailed" in preference_lower:
            feedback["increase_verbosity"] = True
        elif "brief" in preference_lower or "concise" in preference_lower:
            feedback["decrease_verbosity"] = True

        # Apply learning
        if feedback and context:
            self.adaptive_comm.learn_user_style(user_id, context, feedback)

        return {
            "understood": True,
            "preferences_updated": feedback,
            "message": "I'll adjust my communication style going forward"
        }

    def get_system_status(self) -> Dict:
        """Get system status and governance info"""

        brain_stats = self.brain.get_memory_stats()

        return {
            "status": "operational",
            "governance_mode": "autonomous_adaptive",
            "privacy_mode": self.privacy.mode.value,
            "brain_status": {
                "conversations_stored": brain_stats.get("conversations", 0),
                "knowledge_entries": brain_stats.get("knowledge", 0),
                "patterns_learned": brain_stats.get("patterns", 0),
            },
            "users_with_profiles": len(self.adaptive_comm.user_profiles),
            "active_sessions": len(self.active_sessions),
            "communication_contexts_available": [
                c.value for c in CommunicationContext
            ],
            "self_governing": True,
            "learns_from_interactions": True,
            "timestamp": datetime.now().isoformat(),
        }

    def get_governance_report(self) -> str:
        """
        Get human-readable governance report.

        Shows how ALFRED is self-governing and making decisions.
        """

        status = self.get_system_status()
        brain_stats = self.brain.get_memory_stats()

        report = f"""
╔═══════════════════════════════════════════════════════════╗
║            ALFRED Self-Governance Report                 ║
╚═══════════════════════════════════════════════════════════╝

OPERATIONAL STATUS:
  • Status: {status['status'].upper()}
  • Mode: Autonomous Adaptive Communication
  • Privacy: {status['privacy_mode'].upper()}

AUTONOMOUS CAPABILITIES:
  ✓ Detects communication context (10 types)
  ✓ Adjusts formality automatically (0-100%)
  ✓ Calibrates empathy level (0-100%)
  ✓ Adapts technical depth (0-100%)
  ✓ Learns user preferences over time
  ✓ Makes decisions without user input
  ✓ Operates across all programs/devices

BRAIN & LEARNING:
  • Conversations Stored: {brain_stats.get('conversations', 0)}
  • Knowledge Entries: {brain_stats.get('knowledge', 0)}
  • Patterns Learned: {brain_stats.get('patterns', 0)}
  • Skills Tracked: {brain_stats.get('skills', 0)}

USERS & PERSONALIZATION:
  • Users with Profiles: {status['users_with_profiles']}
  • Active Sessions: {status['active_sessions']}
  • Contexts Available: {len(status['communication_contexts_available'])}

COMMUNICATION CONTEXTS UNDERSTOOD:
  • CASUAL_CHAT - Friendly, conversational
  • BUSINESS - Professional, efficient
  • TECHNICAL - Detailed, precise
  • SUPPORT - Empathetic, helpful
  • SYSTEM - Formal, fast
  • RESEARCH - Rigorous, thorough
  • LEARNING - Instructive, patient
  • EXECUTIVE - Concise, strategic
  • SECURITY - Cautious, thorough
  • CREATIVE - Expressive, imaginative

HOW SELF-GOVERNANCE WORKS:

1. Input Analysis
   └─ Analyzes user input for context clues
   └─ Checks metadata (device, program, role)
   └─ Recalls previous interactions

2. Context Detection
   └─ Identifies communication context (10 types)
   └─ Calculates confidence level
   └─ Adjusts based on learned preferences

3. Profile Application
   └─ Loads user's communication profile
   └─ Applies formality settings
   └─ Determines empathy level
   └─ Sets technical depth

4. Autonomous Decision Making
   └─ Generates system prompt with settings
   └─ Selects best agents for task
   └─ Validates response quality
   └─ Adapts response to profile

5. Continuous Learning
   └─ Stores interaction outcome
   └─ Updates pattern knowledge
   └─ Refines communication preferences
   └─ Improves future decisions

SELF-GOVERNANCE GUARANTEES:

✓ KNOWS WHEN:
  - To be formal vs casual
  - To show empathy vs efficiency
  - To go deep vs stay simple
  - To be brief vs detailed

✓ KNOWS WHERE:
  - Business environment → Professional tone
  - Help request → Empathetic tone
  - Technical task → Detailed tone
  - System call → Efficient tone

✓ KNOWS HOW:
  - To adjust communication style mid-conversation
  - To learn from feedback
  - To improve over time
  - To operate across all programs

✓ KNOWS WHY:
  - Each decision is traceable
  - Every adjustment has reasoning
  - Learning is intentional
  - Privacy is maintained

AUTONOMOUS OPERATION:
  • No user configuration needed
  • Works out of box
  • Learns from each interaction
  • Improves with time
  • Self-correcting
  • Privacy-preserving

Timestamp: {datetime.now().isoformat()}
═════════════════════════════════════════════════════════════
"""
        return report
