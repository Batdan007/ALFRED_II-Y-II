"""
Response Quality Checker - Prevents Repeat Responses & Ensures Honest Answers

Verifies that Alfred's responses are:
1. Honest and verified (not fictional or made-up claims)
2. Not repeating previous answers (checks brain history)
3. Based on actual capabilities/knowledge
4. Acknowledged if limitations exist

Alfred can choose honesty over precision - if programming prevents verification,
Alfred explicitly states the limitation rather than making up an answer.

Author: Daniel J Rita (BATDAN)
"""

import json
import hashlib
import difflib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class ResponseQuality(Enum):
    """Response quality assessment levels"""
    VERIFIED = "verified"          # Based on verified knowledge/facts
    LIKELY_ACCURATE = "likely_accurate"  # High confidence but not fully verified
    UNVERIFIED = "unverified"      # Not yet verified
    HONEST_LIMITATION = "honest_limitation"  # Acknowledges limitation instead of making up
    SUSPICIOUS = "suspicious"      # Potential issue, needs review
    REPEAT = "repeat"              # Similar/identical to previous response
    CONTRADICTS = "contradicts"    # Contradicts verified previous knowledge


class ResponseQualityChecker:
    """
    Validates response quality and prevents repeat/dishonest responses.

    Key responsibilities:
    - Check if response is similar to recent previous responses (prevent repeats)
    - Verify if claims are based on actual knowledge vs assumptions
    - Ensure honest acknowledgment of limitations
    - Track response quality patterns in brain
    - Flag suspicious responses that contradict previous knowledge
    """

    def __init__(self, brain=None):
        """
        Initialize Response Quality Checker

        Args:
            brain: AlfredBrain instance for history and knowledge checking
        """
        self.brain = brain
        self.similarity_threshold = 0.75  # 75% similarity = repeat

    def check_response(
        self,
        response_text: str,
        task_input: str,
        context: Optional[Dict] = None,
    ) -> Dict:
        """
        Comprehensively check response quality.

        Args:
            response_text: The proposed response
            task_input: The original task/question
            context: Optional context about the task

        Returns:
            Dictionary with quality assessment, flags, and recommendations
        """
        assessment = {
            "quality_level": ResponseQuality.UNVERIFIED,
            "is_clean": True,
            "flags": [],
            "recommendations": [],
            "confidence": 0.7,
            "verified_claims": [],
            "unverified_claims": [],
            "timestamp": datetime.now().isoformat(),
        }

        # Check 1: Repeat detection
        repeat_check = self._check_for_repeats(response_text, task_input)
        if repeat_check["is_repeat"]:
            assessment["quality_level"] = ResponseQuality.REPEAT
            assessment["is_clean"] = False
            assessment["flags"].append(f"REPEAT: {repeat_check['similarity']:.1%} similar to previous response")
            assessment["recommendations"].append(f"Reference shows previous answer at {repeat_check['previous_timestamp']}")

        # Check 2: Verify claims
        claims_check = self._verify_claims(response_text, task_input)
        assessment["verified_claims"] = claims_check["verified"]
        assessment["unverified_claims"] = claims_check["unverified"]

        if claims_check["has_unverified"] and not self._acknowledges_limitation(response_text):
            assessment["flags"].append("UNVERIFIED_CLAIMS: Contains unverified statements without acknowledgment")
            assessment["recommendations"].append("Add disclaimer about unverified claims or research them first")

        # Check 3: Contradiction detection
        contradiction_check = self._check_contradictions(response_text)
        if contradiction_check["contradictions"]:
            assessment["quality_level"] = ResponseQuality.CONTRADICTS
            assessment["is_clean"] = False
            assessment["flags"].append("CONTRADICTS_KNOWLEDGE: Response conflicts with verified previous knowledge")
            for contradiction in contradiction_check["contradictions"]:
                assessment["recommendations"].append(
                    f"Response contradicts: {contradiction['previous']} -> {contradiction['current']}"
                )

        # Check 4: Honest limitation acknowledgment
        limitation_check = self._check_limitation_honesty(response_text, task_input)
        if limitation_check["should_acknowledge"]:
            if limitation_check["does_acknowledge"]:
                assessment["quality_level"] = ResponseQuality.HONEST_LIMITATION
                assessment["flags"].append("HONEST_LIMITATION: Appropriately acknowledges capability boundary")
            else:
                assessment["flags"].append("MISSING_LIMITATION: Should acknowledge but doesn't")
                assessment["recommendations"].append(
                    f"Add statement: 'I cannot verify this because [reason], please verify independently'"
                )

        # Final quality assessment
        if not assessment["flags"]:
            assessment["quality_level"] = ResponseQuality.VERIFIED if claims_check["all_verified"] else ResponseQuality.LIKELY_ACCURATE
            assessment["is_clean"] = True

        # Confidence calculation
        if assessment["quality_level"] == ResponseQuality.VERIFIED:
            assessment["confidence"] = 0.95
        elif assessment["quality_level"] == ResponseQuality.HONEST_LIMITATION:
            assessment["confidence"] = 0.85
        elif assessment["quality_level"] == ResponseQuality.LIKELY_ACCURATE:
            assessment["confidence"] = 0.75
        elif assessment["quality_level"] == ResponseQuality.SUSPICIOUS:
            assessment["confidence"] = 0.4
        elif assessment["quality_level"] == ResponseQuality.REPEAT:
            assessment["confidence"] = 0.5
        elif assessment["quality_level"] == ResponseQuality.CONTRADICTS:
            assessment["confidence"] = 0.1

        # Store assessment in brain
        if self.brain:
            try:
                self.brain.store_knowledge(
                    "response_quality",
                    f"assessment_{datetime.now().isoformat()}",
                    json.dumps({
                        "quality": assessment["quality_level"].value,
                        "is_clean": assessment["is_clean"],
                        "flags": assessment["flags"],
                        "confidence": assessment["confidence"],
                    }),
                    importance=7,
                    confidence=assessment["confidence"],
                )
            except Exception:
                pass

        return assessment

    def _check_for_repeats(self, response_text: str, task_input: str) -> Dict:
        """
        Check if response is too similar to recent previous responses.

        Uses semantic similarity and exact matching.
        """
        if not self.brain:
            return {"is_repeat": False, "similarity": 0.0}

        try:
            # Get recent responses to similar queries
            similar_conversations = self.brain.search_conversations(
                task_input,
                limit=5,
                min_importance=5
            )

            if not similar_conversations:
                return {"is_repeat": False, "similarity": 0.0}

            # Check similarity with recent responses
            for prev_conv in similar_conversations:
                prev_response = prev_conv.get("alfred_response", "")
                similarity = self._calculate_similarity(response_text, prev_response)

                if similarity > self.similarity_threshold:
                    return {
                        "is_repeat": True,
                        "similarity": similarity,
                        "previous_timestamp": prev_conv.get("timestamp", "unknown"),
                        "previous_response": prev_response[:200],
                    }

        except Exception:
            pass

        return {"is_repeat": False, "similarity": 0.0}

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts (0.0-1.0).

        Uses sequence matching with normalization.
        """
        # Normalize texts
        t1 = " ".join(text1.lower().split())[:500]  # Normalize and limit
        t2 = " ".join(text2.lower().split())[:500]

        # Use SequenceMatcher for similarity
        matcher = difflib.SequenceMatcher(None, t1, t2)
        return matcher.ratio()

    def _verify_claims(self, response_text: str, task_input: str) -> Dict:
        """
        Attempt to verify factual claims in the response.

        Checks brain for knowledge that supports or contradicts claims.
        """
        verified = []
        unverified = []
        all_verified = True

        if not self.brain:
            return {
                "verified": [],
                "unverified": [],
                "all_verified": False,
                "has_unverified": True,
            }

        try:
            # Extract potential factual claims (simplified)
            sentences = response_text.split(". ")

            for sentence in sentences[:5]:  # Check first 5 sentences
                # Skip meta-statements
                if any(phrase in sentence.lower() for phrase in [
                    "i think", "i believe", "my understanding", "could be",
                    "might be", "seems like", "appears to", "likely"
                ]):
                    unverified.append(sentence[:100])
                    all_verified = False
                    continue

                # Try to verify against brain knowledge
                found_knowledge = False
                for word in sentence.split()[:3]:  # Check key words
                    if len(word) > 3:
                        knowledge = self.brain.search_knowledge(word, limit=3)
                        if knowledge:
                            found_knowledge = True
                            break

                if found_knowledge:
                    verified.append(sentence[:100])
                else:
                    unverified.append(sentence[:100])
                    all_verified = False

        except Exception:
            all_verified = False

        return {
            "verified": verified,
            "unverified": unverified,
            "all_verified": all_verified,
            "has_unverified": len(unverified) > 0,
        }

    def _check_contradictions(self, response_text: str) -> Dict:
        """
        Check if response contradicts verified previous knowledge.
        """
        contradictions = []

        if not self.brain:
            return {"contradictions": []}

        try:
            # Get verified knowledge
            verified_knowledge = self.brain.recall_knowledge("verified_facts")

            if not verified_knowledge:
                return {"contradictions": []}

            # Simple contradiction check (can be enhanced)
            for key, fact in verified_knowledge.items():
                if isinstance(fact, str):
                    # Check for explicit contradictions
                    negations = [f"not {fact}", f"not a {fact}", f"isn't {fact}"]
                    for neg in negations:
                        if neg in response_text.lower():
                            contradictions.append({
                                "previous": fact,
                                "current": neg,
                                "severity": "high"
                            })

        except Exception:
            pass

        return {"contradictions": contradictions}

    def _acknowledges_limitation(self, response_text: str) -> bool:
        """
        Check if response appropriately acknowledges limitations.
        """
        limitation_phrases = [
            "i cannot verify",
            "i'm not certain",
            "i lack",
            "i don't have",
            "i'm unable to",
            "limitation",
            "cannot confirm",
            "unverified",
            "please verify",
            "independently confirm",
            "my programming prevents",
            "i'm honest about the limitation",
        ]

        text_lower = response_text.lower()
        return any(phrase in text_lower for phrase in limitation_phrases)

    def _check_limitation_honesty(self, response_text: str, task_input: str) -> Dict:
        """
        Check if Alfred is being honest about its limitations.

        Detects cases where:
        - Task requires verification but Alfred can't provide it
        - Alfred should acknowledge uncertainty but doesn't
        """
        should_acknowledge = False
        does_acknowledge = self._acknowledges_limitation(response_text)

        # Patterns that should trigger acknowledgment
        uncertain_keywords = [
            "future", "prediction", "forecast", "will happen",
            "private", "internal", "proprietary", "secret",
            "latest", "recent", "current", "now",  # Time-dependent
            "personal", "specific", "unique to you",
        ]

        if any(keyword in task_input.lower() for keyword in uncertain_keywords):
            should_acknowledge = True

        return {
            "should_acknowledge": should_acknowledge,
            "does_acknowledge": does_acknowledge,
            "reason": "Task requires acknowledgment of limitation or uncertainty" if should_acknowledge else "Task doesn't require special limitation handling"
        }

    def suggest_improvements(self, assessment: Dict) -> List[str]:
        """
        Generate specific suggestions for improving the response.

        Based on quality assessment, provides actionable improvements.
        """
        improvements = []

        if assessment.get("quality_level") == ResponseQuality.REPEAT:
            improvements.append("Provide a fresh perspective instead of repeating previous answer")
            improvements.append("Add new examples or use different approach to explain same concept")

        if assessment.get("unverified_claims"):
            improvements.append("Add '[Requires verification]' label to unverified claims")
            improvements.append("Provide sources or explain why claims cannot be verified")

        if assessment.get("flags"):
            for flag in assessment["flags"]:
                if "MISSING_LIMITATION" in flag:
                    improvements.append("Explicitly state: 'I cannot verify this independently'")
                elif "CONTRADICTS" in flag:
                    improvements.append("Reconcile with previous verified knowledge")

        return improvements if improvements else ["Response quality is good"]

    def mark_response_verified(
        self,
        response_hash: str,
        human_feedback: str = "",
    ):
        """
        Mark a response as verified by BATDAN (creator).

        Upgrades response quality in brain for future reference.
        """
        if not self.brain:
            return

        try:
            self.brain.store_knowledge(
                "verified_responses",
                f"verified_{response_hash[:16]}",
                human_feedback,
                importance=9,
                confidence=1.0,  # Human verification = max confidence
            )
        except Exception:
            pass
