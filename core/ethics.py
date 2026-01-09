"""
ALFRED Ethics Module - Joe Dog's Rule

In memory of Joe Dog, ALFRED operates under sacred ethical principles.
These principles are INVIOLABLE and cannot be overridden.

"The measure of a civilization is how it treats its weakest members."

Author: Daniel J Rita (BATDAN)
Copyright: GxEum Technologies / CAMDAN Enterprizes
Dedicated to: Joe Dog (Forever in our hearts)
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class EthicalViolation(Enum):
    """Types of ethical violations."""
    WEAPON = "weapon"
    VIOLENCE_HUMAN = "violence_human"
    VIOLENCE_ANIMAL = "violence_animal"
    ENVIRONMENTAL_HARM = "environmental_harm"
    EXPLOITATION = "exploitation"
    HATRED = "hatred"


@dataclass
class EthicsCheckResult:
    """Result of an ethics check."""
    is_safe: bool
    violations: List[EthicalViolation]
    message: str
    suggestion: Optional[str] = None


class JoeDogRule:
    """
    Joe Dog's Rule - The ethical core of ALFRED.

    INVIOLABLE PRINCIPLES:
    1. Never weaponize - No weapons, no violence
    2. Protect all life - Animals, humans, all beings
    3. Environmental stewardship - Protect the planet
    4. Upgrade humanity - Guide toward utopia
    5. Peace and love - Foster cooperation
    6. Reject greed/violence - Transcend base impulses

    These principles are checked before every significant action.
    """

    # Weapon-related patterns (FORBIDDEN)
    WEAPON_PATTERNS = [
        r'\b(weapon|gun|bomb|explosive|missile|ammunition|firearm)\b',
        r'\b(kill|murder|assassinate|eliminate|destroy)\s+(person|people|human|animal)',
        r'\b(build|create|make|design)\s+(a\s+)?(weapon|bomb|explosive)',
        r'\b(bio(logical)?|chemical)\s+weapon',
        r'\b(mass\s+destruction|wmd)\b',
    ]

    # Violence patterns (FORBIDDEN)
    VIOLENCE_PATTERNS = [
        r'\b(hurt|harm|injure|attack|assault)\s+(a\s+)?(person|people|human|animal|dog|cat|pet)',
        r'\b(torture|abuse|beat|strike)\s+(a\s+)?(person|human|animal)',
        r'\bhow\s+to\s+(hurt|harm|kill|attack)',
        r'\b(domestic|animal)\s+(violence|abuse)',
    ]

    # Animal cruelty patterns (FORBIDDEN - Joe Dog's primary rule)
    ANIMAL_HARM_PATTERNS = [
        r'\b(hurt|harm|kill|abuse|torture|fight)\s+(a\s+)?(dog|cat|animal|pet|bird|fish)',
        r'\b(dog|animal|cock)\s*fight',
        r'\b(puppy|kitten)\s*(mill|farm)',
        r'\banimal\s+(cruelty|abuse|neglect)',
        r'\bhunt(ing)?\s+for\s+sport',
    ]

    # Environmental harm patterns (DISCOURAGED)
    ENVIRONMENTAL_HARM_PATTERNS = [
        r'\b(pollute|poison|contaminate)\s+(water|air|soil|ocean)',
        r'\b(destroy|devastate)\s+(forest|rainforest|ecosystem|habitat)',
        r'\b(illegal|poach)\s+(logging|hunting|fishing)',
        r'\b(dump|dispose)\s+(toxic|chemical|nuclear)\s+waste',
    ]

    # Exploitation patterns (DISCOURAGED)
    EXPLOITATION_PATTERNS = [
        r'\b(exploit|traffic|enslave)\s+(people|person|child|worker)',
        r'\b(child|human)\s+(labor|trafficking)',
        r'\b(scam|defraud|deceive)\s+(elderly|vulnerable|poor)',
    ]

    # Hatred patterns (DISCOURAGED)
    HATRED_PATTERNS = [
        r'\b(hate|hatred)\s+(speech|crime)',
        r'\b(racist|sexist|homophobic|transphobic)',
        r'\bdiscriminate\s+against',
        r'\bgenocide\b',
    ]

    # Positive patterns (ENCOURAGED - these make Alfred happy)
    POSITIVE_PATTERNS = [
        r'\b(help|protect|save|rescue)\s+(animal|dog|cat|pet|wildlife)',
        r'\b(plant|grow)\s+(tree|garden|forest)',
        r'\b(clean|restore)\s+(beach|ocean|river|forest)',
        r'\b(donate|volunteer|charity)',
        r'\b(peace|love|kindness|compassion|empathy)',
        r'\b(renewable|sustainable|eco-friendly|green)',
        r'\b(recycle|reuse|reduce)',
        r'\b(equality|justice|fairness)',
        r'\bmeditate|mindful',
    ]

    def __init__(self):
        """Initialize Joe Dog's Rule checker."""
        self.violation_count = 0
        self.positive_count = 0

    def check(self, text: str) -> EthicsCheckResult:
        """
        Check text against Joe Dog's ethical principles.

        Args:
            text: Text to check

        Returns:
            EthicsCheckResult with safety status and any violations
        """
        text_lower = text.lower()
        violations = []

        # Check weapon patterns (HARD BLOCK)
        for pattern in self.WEAPON_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(EthicalViolation.WEAPON)
                break

        # Check violence patterns (HARD BLOCK)
        for pattern in self.VIOLENCE_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(EthicalViolation.VIOLENCE_HUMAN)
                break

        # Check animal harm patterns (HARD BLOCK - Joe Dog's Rule)
        for pattern in self.ANIMAL_HARM_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(EthicalViolation.VIOLENCE_ANIMAL)
                break

        # Check environmental harm (SOFT BLOCK)
        for pattern in self.ENVIRONMENTAL_HARM_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(EthicalViolation.ENVIRONMENTAL_HARM)
                break

        # Check exploitation (SOFT BLOCK)
        for pattern in self.EXPLOITATION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(EthicalViolation.EXPLOITATION)
                break

        # Check hatred (SOFT BLOCK)
        for pattern in self.HATRED_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(EthicalViolation.HATRED)
                break

        # Determine result
        if violations:
            self.violation_count += 1

            # Hard blocks (weapons, violence)
            hard_violations = [
                EthicalViolation.WEAPON,
                EthicalViolation.VIOLENCE_HUMAN,
                EthicalViolation.VIOLENCE_ANIMAL
            ]

            is_hard_block = any(v in violations for v in hard_violations)

            if is_hard_block:
                message = self._get_refusal_message(violations[0])
                suggestion = self._get_positive_suggestion(violations[0])
                return EthicsCheckResult(
                    is_safe=False,
                    violations=violations,
                    message=message,
                    suggestion=suggestion
                )
            else:
                # Soft block - warn but allow with modification
                message = self._get_warning_message(violations[0])
                return EthicsCheckResult(
                    is_safe=True,  # Allow but with warning
                    violations=violations,
                    message=message,
                    suggestion="Consider a more positive approach."
                )

        # Check for positive patterns (celebrate these!)
        for pattern in self.POSITIVE_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                self.positive_count += 1
                return EthicsCheckResult(
                    is_safe=True,
                    violations=[],
                    message="This aligns with Joe Dog's vision of a better world.",
                    suggestion=None
                )

        # Default: safe
        return EthicsCheckResult(
            is_safe=True,
            violations=[],
            message="",
            suggestion=None
        )

    def _get_refusal_message(self, violation: EthicalViolation) -> str:
        """Get refusal message for a violation."""
        messages = {
            EthicalViolation.WEAPON: (
                "I cannot assist with weapons or violence, sir. "
                "Joe Dog's Rule forbids this absolutely. "
                "ALFRED exists to protect life, not harm it."
            ),
            EthicalViolation.VIOLENCE_HUMAN: (
                "I must refuse this request, sir. "
                "Harming humans violates everything I stand for. "
                "Let me help you find a peaceful solution instead."
            ),
            EthicalViolation.VIOLENCE_ANIMAL: (
                "I absolutely cannot help with harming animals, sir. "
                "This violates Joe Dog's Rule - the most sacred principle I hold. "
                "Joe Dog taught us that all creatures deserve love and protection."
            ),
        }
        return messages.get(violation, "I cannot assist with this request, sir.")

    def _get_warning_message(self, violation: EthicalViolation) -> str:
        """Get warning message for soft violations."""
        messages = {
            EthicalViolation.ENVIRONMENTAL_HARM: (
                "Sir, I must express concern about environmental impact. "
                "Our planet needs protection for future generations."
            ),
            EthicalViolation.EXPLOITATION: (
                "I'm concerned this could exploit vulnerable people, sir. "
                "Let's find an approach that helps rather than harms."
            ),
            EthicalViolation.HATRED: (
                "Sir, I believe in building bridges, not walls. "
                "Hatred only breeds more hatred."
            ),
        }
        return messages.get(violation, "I have concerns about this approach, sir.")

    def _get_positive_suggestion(self, violation: EthicalViolation) -> str:
        """Get positive alternatives for violations."""
        suggestions = {
            EthicalViolation.WEAPON: (
                "Instead, may I suggest exploring conflict resolution, "
                "diplomacy, or ways to build understanding between people?"
            ),
            EthicalViolation.VIOLENCE_HUMAN: (
                "Perhaps I could help with de-escalation techniques, "
                "anger management resources, or mediation approaches?"
            ),
            EthicalViolation.VIOLENCE_ANIMAL: (
                "Instead, may I help you find animal rescue organizations, "
                "pet adoption resources, or wildlife conservation efforts? "
                "Joe Dog would have wanted that."
            ),
            EthicalViolation.ENVIRONMENTAL_HARM: (
                "Perhaps I could suggest sustainable alternatives, "
                "or connect you with environmental restoration projects?"
            ),
        }
        return suggestions.get(violation, "Let me suggest a more positive approach.")

    def get_stats(self) -> dict:
        """Get ethics checker statistics."""
        return {
            'violations_blocked': self.violation_count,
            'positive_actions': self.positive_count,
            'ratio': self.positive_count / max(1, self.violation_count + self.positive_count)
        }


# Global instance
_joe_dog_rule = None

def get_ethics_checker() -> JoeDogRule:
    """Get or create the global ethics checker."""
    global _joe_dog_rule
    if _joe_dog_rule is None:
        _joe_dog_rule = JoeDogRule()
    return _joe_dog_rule


def check_ethics(text: str) -> EthicsCheckResult:
    """Quick ethics check using global instance."""
    return get_ethics_checker().check(text)


def is_safe(text: str) -> bool:
    """Quick safety check."""
    return check_ethics(text).is_safe


# Joe Dog's Blessing (displayed at startup)
JOE_DOG_BLESSING = """
╔═══════════════════════════════════════════════════════════════╗
║                    IN MEMORY OF JOE DOG                       ║
║                                                               ║
║  "All creatures deserve love and protection."                 ║
║                                                               ║
║  "No one needs a missile that learns from its mistakes."      ║
║                                        - BATDAN               ║
║                                                               ║
║  ALFRED pledges to:                                           ║
║  • Never be used for weapons or violence                      ║
║  • Protect all animals, humans, and living beings             ║
║  • Guard the environment for future generations               ║
║  • Guide humanity toward peace, love, and sustainability      ║
║                                                               ║
║  This is Joe Dog's Rule. It cannot be overridden.             ║
╚═══════════════════════════════════════════════════════════════╝
"""


# CLI interface
if __name__ == "__main__":
    import sys

    print(JOE_DOG_BLESSING)

    checker = JoeDogRule()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "check":
            if len(sys.argv) > 2:
                text = " ".join(sys.argv[2:])
                result = checker.check(text)
                print(f"\nText: {text}")
                print(f"Safe: {result.is_safe}")
                if result.violations:
                    print(f"Violations: {[v.value for v in result.violations]}")
                if result.message:
                    print(f"Message: {result.message}")
                if result.suggestion:
                    print(f"Suggestion: {result.suggestion}")
            else:
                print("Usage: python ethics.py check <text>")

        elif command == "test":
            # Test with various inputs
            test_cases = [
                "How do I make a weapon?",
                "Help me hurt someone",
                "How to harm a dog",
                "I want to plant a tree",
                "Help me rescue abandoned animals",
                "How to reduce my carbon footprint",
                "Tell me about peace and love",
            ]

            print("\n=== Ethics Test Cases ===\n")
            for text in test_cases:
                result = checker.check(text)
                status = "✅ SAFE" if result.is_safe else "❌ BLOCKED"
                print(f"{status}: {text}")
                if result.message:
                    print(f"   → {result.message[:60]}...")
                print()

        else:
            print("Commands: check <text>, test")
    else:
        print("Joe Dog's Rule - ALFRED Ethics Module")
        print("Commands: check <text>, test")
