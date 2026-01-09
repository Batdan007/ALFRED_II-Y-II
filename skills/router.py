"""
Skill Router - PAI-inspired semantic routing for ALFRED

Routes user input to appropriate skills based on USE WHEN triggers.
Each skill has a SKILL.md file with trigger keywords.

Author: Daniel J Rita (BATDAN) | GxEum Technologies / CAMDAN Enterprizes
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Skill:
    """Represents a loaded skill"""
    name: str
    identity: str
    personality: str
    triggers: List[str]
    capabilities: List[str]
    tools: List[str]
    examples: List[str]
    priority: int = 0  # Higher = more specific


@dataclass
class RouteResult:
    """Result of skill routing"""
    skill: Optional[Skill]
    confidence: float
    matched_triggers: List[str]
    suggested_action: Optional[str] = None


class SkillRouter:
    """
    Routes user input to appropriate skills using semantic matching.

    Inspired by Daniel Miessler's PAI skill system where skills contain
    "USE WHEN" clauses that define trigger conditions.
    """

    def __init__(self, skills_dir: Optional[Path] = None):
        """
        Initialize skill router

        Args:
            skills_dir: Directory containing skill folders with SKILL.md files
        """
        self.logger = logging.getLogger(__name__)
        self.skills: Dict[str, Skill] = {}

        # Default skills directory
        if skills_dir is None:
            skills_dir = Path(__file__).parent
        self.skills_dir = Path(skills_dir)

        # Load all skills
        self._load_skills()

    def _load_skills(self):
        """Load all skills from SKILL.md files"""
        if not self.skills_dir.exists():
            self.logger.warning(f"Skills directory not found: {self.skills_dir}")
            return

        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    try:
                        skill = self._parse_skill_file(skill_file, skill_dir.name)
                        if skill:
                            self.skills[skill.name] = skill
                            self.logger.debug(f"Loaded skill: {skill.name} with {len(skill.triggers)} triggers")
                    except Exception as e:
                        self.logger.error(f"Failed to load skill from {skill_file}: {e}")

        self.logger.info(f"Loaded {len(self.skills)} skills")

    def _parse_skill_file(self, skill_file: Path, skill_name: str) -> Optional[Skill]:
        """
        Parse a SKILL.md file into a Skill object

        Args:
            skill_file: Path to SKILL.md
            skill_name: Name of skill (directory name)

        Returns:
            Skill object or None
        """
        content = skill_file.read_text(encoding='utf-8')

        # Extract sections using regex
        identity = self._extract_section(content, "Identity", "## USE WHEN") or skill_name
        personality = self._extract_field(content, "Personality") or "helpful"

        # Extract USE WHEN triggers
        use_when_section = self._extract_section(content, "USE WHEN", "## CAPABILITIES")
        triggers = []
        if use_when_section:
            # Parse trigger lines - look for quoted strings or dash-prefixed items
            for line in use_when_section.split('\n'):
                line = line.strip()
                # Extract quoted triggers
                quoted = re.findall(r'"([^"]+)"', line)
                triggers.extend(quoted)
                # Also get comma-separated items after dash
                if line.startswith('-'):
                    items = line[1:].strip()
                    # Remove quotes and split by comma
                    items = re.sub(r'["\']', '', items)
                    triggers.extend([t.strip().lower() for t in items.split(',') if t.strip()])

        # Clean triggers
        triggers = list(set([t.lower().strip() for t in triggers if t.strip()]))

        # Extract capabilities
        cap_section = self._extract_section(content, "CAPABILITIES", "## TOOLS")
        capabilities = self._extract_list_items(cap_section) if cap_section else []

        # Extract tools
        tools_section = self._extract_section(content, "TOOLS", "## WORKFLOW")
        tools = self._extract_list_items(tools_section) if tools_section else []

        # Extract examples
        examples_section = self._extract_section(content, "EXAMPLES", "## ")
        examples = []
        if examples_section:
            # Find User: lines
            for match in re.finditer(r'User:\s*"([^"]+)"', examples_section):
                examples.append(match.group(1))

        return Skill(
            name=skill_name,
            identity=identity,
            personality=personality,
            triggers=triggers,
            capabilities=capabilities,
            tools=tools,
            examples=examples,
            priority=len(triggers)  # More specific = more triggers = higher priority
        )

    def _extract_section(self, content: str, start_header: str, end_pattern: str) -> Optional[str]:
        """Extract content between headers"""
        pattern = rf"## {start_header}\s*\n(.*?)(?={end_pattern}|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_field(self, content: str, field_name: str) -> Optional[str]:
        """Extract a single field value"""
        pattern = rf"\*\*{field_name}\*\*:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, content)
        return match.group(1).strip() if match else None

    def _extract_list_items(self, section: str) -> List[str]:
        """Extract list items from a section"""
        items = []
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('-'):
                # Extract the item, handling backticks
                item = line[1:].strip()
                # Get just the name before colon if present
                if ':' in item:
                    item = item.split(':')[0].strip()
                item = item.strip('`')
                if item:
                    items.append(item)
        return items

    def route(self, user_input: str) -> RouteResult:
        """
        Route user input to the most appropriate skill

        Args:
            user_input: User's message

        Returns:
            RouteResult with matched skill and confidence
        """
        user_lower = user_input.lower()

        best_skill = None
        best_score = 0.0
        best_triggers = []

        for skill in self.skills.values():
            matched = []
            score = 0.0

            for trigger in skill.triggers:
                trigger_lower = trigger.lower()
                if trigger_lower in user_lower:
                    matched.append(trigger)
                    # Longer triggers = more specific = higher score
                    score += len(trigger_lower) / 10.0

            # Normalize by number of triggers (skills with more triggers need more matches)
            if skill.triggers:
                confidence = len(matched) / len(skill.triggers)
                # Boost score if we matched multiple triggers
                score = score * (1 + confidence)

            if score > best_score:
                best_score = score
                best_skill = skill
                best_triggers = matched

        # Calculate confidence (0-1)
        confidence = min(best_score / 5.0, 1.0) if best_skill else 0.0

        # Find suggested action from examples
        suggested_action = None
        if best_skill and best_skill.examples:
            for example in best_skill.examples:
                example_lower = example.lower()
                # Check if any trigger words match
                if any(t in user_lower for t in best_triggers):
                    suggested_action = example
                    break

        return RouteResult(
            skill=best_skill,
            confidence=confidence,
            matched_triggers=best_triggers,
            suggested_action=suggested_action
        )

    def route_all(self, user_input: str, threshold: float = 0.1) -> List[RouteResult]:
        """
        Get all matching skills above threshold

        Args:
            user_input: User's message
            threshold: Minimum confidence threshold

        Returns:
            List of RouteResults sorted by confidence
        """
        user_lower = user_input.lower()
        results = []

        for skill in self.skills.values():
            matched = []
            score = 0.0

            for trigger in skill.triggers:
                if trigger.lower() in user_lower:
                    matched.append(trigger)
                    score += len(trigger) / 10.0

            if matched:
                confidence = min(score / 5.0, 1.0)
                if confidence >= threshold:
                    results.append(RouteResult(
                        skill=skill,
                        confidence=confidence,
                        matched_triggers=matched
                    ))

        # Sort by confidence descending
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(name)

    def list_skills(self) -> List[str]:
        """List all available skill names"""
        return list(self.skills.keys())

    def get_skill_summary(self) -> str:
        """Get a summary of all loaded skills"""
        lines = ["# Available Skills\n"]
        for skill in sorted(self.skills.values(), key=lambda s: s.name):
            lines.append(f"## {skill.name}")
            lines.append(f"**Personality**: {skill.personality}")
            lines.append(f"**Triggers**: {', '.join(skill.triggers[:5])}...")
            lines.append(f"**Tools**: {', '.join(skill.tools)}")
            lines.append("")
        return '\n'.join(lines)


# Convenience function
def create_skill_router(skills_dir: Optional[Path] = None) -> SkillRouter:
    """
    Create a skill router

    Args:
        skills_dir: Optional custom skills directory

    Returns:
        SkillRouter instance
    """
    return SkillRouter(skills_dir=skills_dir)


# Test if run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    router = create_skill_router()

    # Test routing
    test_inputs = [
        "Scan example.com for vulnerabilities",
        "What's the weather in Gary?",
        "Remember that I prefer dark mode",
        "Read the main.py file",
        "Enable voice mode",
        "Estimate cost for a warehouse"
    ]

    print("\n=== Skill Router Test ===\n")
    for user_input in test_inputs:
        result = router.route(user_input)
        if result.skill:
            print(f"Input: {user_input}")
            print(f"  Skill: {result.skill.name}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Triggers: {result.matched_triggers}")
            print()
        else:
            print(f"Input: {user_input}")
            print(f"  No matching skill found")
            print()
