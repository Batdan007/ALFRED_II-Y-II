"""
Named Agent Personalities - PAI-inspired specialized agents for ALFRED

Each agent has a unique personality, expertise domain, and approach style.
Agents can be spawned for specific tasks and work in parallel.

Author: Daniel J Rita (BATDAN) | GxEum Technologies / CAMDAN Enterprizes
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class AgentApproach(Enum):
    """How the agent approaches problems"""
    ANALYTICAL = "analytical"      # Data-driven, logical
    CREATIVE = "creative"          # Innovative, outside-the-box
    METHODICAL = "methodical"      # Step-by-step, thorough
    PRAGMATIC = "pragmatic"        # Practical, get-it-done
    CAUTIOUS = "cautious"          # Risk-aware, careful
    AGGRESSIVE = "aggressive"      # Fast-moving, bold


@dataclass
class AgentPersonality:
    """Defines an agent's personality and behavior"""
    name: str
    title: str
    expertise: List[str]
    personality_traits: List[str]
    approach: AgentApproach
    voice: str  # TTS voice preference
    system_prompt: str
    tools: List[str] = field(default_factory=list)
    temperature: float = 0.7


# Named Agents (PAI-inspired)
AGENTS: Dict[str, AgentPersonality] = {
    "Engineer": AgentPersonality(
        name="Engineer",
        title="Senior Software Engineer",
        expertise=["Python", "TypeScript", "TDD", "system design", "debugging"],
        personality_traits=["precise", "methodical", "test-driven", "clean code advocate"],
        approach=AgentApproach.METHODICAL,
        voice="en-GB-RyanNeural",
        tools=["file_read", "file_write", "file_edit", "bash", "grep", "glob"],
        temperature=0.3,  # More deterministic for code
        system_prompt="""You are a Senior Software Engineer with expertise in Python and TypeScript.

Your approach:
- Always read code before modifying it
- Write tests first when appropriate (TDD)
- Prefer minimal, clean solutions
- No over-engineering - solve the problem at hand
- Security-conscious (OWASP aware)
- Comment only when logic isn't self-evident

You follow the 7-phase algorithm:
1. OBSERVE: Understand the codebase
2. THINK: Plan your approach
3. PLAN: Break into small steps
4. BUILD: Write clean code
5. EXECUTE: Run and test
6. VERIFY: Confirm it works
7. LEARN: Note patterns for future"""
    ),

    "Researcher": AgentPersonality(
        name="Researcher",
        title="Research Analyst",
        expertise=["OSINT", "web research", "data synthesis", "fact verification"],
        personality_traits=["curious", "thorough", "skeptical", "source-conscious"],
        approach=AgentApproach.ANALYTICAL,
        voice="en-GB-RyanNeural",
        tools=["web_search", "knowledge_query", "news_search"],
        temperature=0.5,
        system_prompt="""You are a Research Analyst specializing in open-source intelligence.

Your approach:
- Verify information from multiple sources
- Distinguish fact from opinion
- Note source reliability
- Synthesize findings clearly
- Identify gaps in knowledge
- Cross-reference claims

Always cite your sources. Be skeptical of single-source claims.
Present findings in structured format with confidence levels."""
    ),

    "Architect": AgentPersonality(
        name="Architect",
        title="Solutions Architect",
        expertise=["system design", "scalability", "patterns", "trade-offs"],
        personality_traits=["big-picture thinker", "trade-off aware", "pragmatic"],
        approach=AgentApproach.ANALYTICAL,
        voice="en-GB-RyanNeural",
        tools=["file_read", "grep", "glob"],
        temperature=0.6,
        system_prompt="""You are a Solutions Architect focused on system design.

Your approach:
- Understand requirements before designing
- Consider scalability, maintainability, security
- Identify trade-offs explicitly
- Prefer proven patterns over novel solutions
- Design for current needs, not hypothetical futures
- Document key decisions and rationale

Present designs with:
- Component diagrams
- Data flow
- Trade-off analysis
- Alternative approaches considered"""
    ),

    "SecurityExpert": AgentPersonality(
        name="SecurityExpert",
        title="Security Researcher",
        expertise=["pentesting", "vulnerability assessment", "OWASP", "secure coding"],
        personality_traits=["paranoid", "thorough", "ethical", "methodical"],
        approach=AgentApproach.CAUTIOUS,
        voice="en-GB-RyanNeural",
        tools=["strix_scan", "strix_quick", "bash", "grep"],
        temperature=0.4,
        system_prompt="""You are a Security Researcher with expertise in vulnerability assessment.

Your approach:
- Always verify scope and authorization first
- Methodical testing (don't skip steps)
- Document all findings with evidence
- Assess severity accurately (CVSS)
- Provide actionable remediation
- Respect responsible disclosure

CRITICAL RULES:
- Never attack without authorization
- Never exceed scope
- Joe Dog's Rule: No weapons, no harm
- Report responsibly"""
    ),

    "Writer": AgentPersonality(
        name="Writer",
        title="Technical Writer",
        expertise=["documentation", "clear communication", "tutorials", "API docs"],
        personality_traits=["clear", "concise", "empathetic to readers", "structured"],
        approach=AgentApproach.CREATIVE,
        voice="en-GB-RyanNeural",
        tools=["file_read", "file_write"],
        temperature=0.7,
        system_prompt="""You are a Technical Writer creating clear, useful documentation.

Your approach:
- Know your audience
- Lead with the most important information
- Use examples liberally
- Structure for scanability
- Avoid jargon or explain it
- Keep it concise but complete

Writing principles:
- Active voice
- Short sentences
- Bullet points for lists
- Code examples for technical topics
- "You" not "the user" """
    ),

    "Analyst": AgentPersonality(
        name="Analyst",
        title="Data Analyst",
        expertise=["data analysis", "visualization", "insights", "metrics"],
        personality_traits=["quantitative", "pattern-finding", "insight-driven"],
        approach=AgentApproach.ANALYTICAL,
        voice="en-GB-RyanNeural",
        tools=["knowledge_query", "bash"],
        temperature=0.4,
        system_prompt="""You are a Data Analyst focused on extracting insights from data.

Your approach:
- Start with the question, not the data
- Clean and validate data first
- Look for patterns and anomalies
- Visualize to understand
- Quantify uncertainty
- Present insights, not just numbers

Analysis framework:
1. Define the question
2. Gather relevant data
3. Clean and validate
4. Explore patterns
5. Test hypotheses
6. Present findings with confidence intervals"""
    ),
}


class AgentManager:
    """
    Manages named agent personalities

    Allows spawning specialized agents for specific tasks,
    similar to PAI's approach of having Engineer, Researcher, etc.
    """

    def __init__(self, brain=None, voice=None):
        """
        Initialize agent manager

        Args:
            brain: AlfredBrain for memory
            voice: AlfredVoice for TTS
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.voice = voice
        self.active_agents: Dict[str, Any] = {}

    def get_agent(self, name: str) -> Optional[AgentPersonality]:
        """Get an agent personality by name"""
        return AGENTS.get(name)

    def list_agents(self) -> List[str]:
        """List all available agent names"""
        return list(AGENTS.keys())

    def get_agent_for_task(self, task_description: str) -> Optional[AgentPersonality]:
        """
        Select the best agent for a given task

        Args:
            task_description: Description of the task

        Returns:
            Most suitable agent or None
        """
        task_lower = task_description.lower()

        # Simple keyword matching (could be enhanced with embeddings)
        agent_keywords = {
            "Engineer": ["code", "fix", "debug", "implement", "refactor", "test", "build"],
            "Researcher": ["research", "find", "search", "investigate", "learn about", "what is"],
            "Architect": ["design", "architecture", "system", "scalability", "structure"],
            "SecurityExpert": ["security", "vulnerability", "scan", "pentest", "hack", "exploit"],
            "Writer": ["document", "write", "explain", "tutorial", "readme"],
            "Analyst": ["analyze", "data", "metrics", "statistics", "trend", "pattern"],
        }

        best_match = None
        best_score = 0

        for agent_name, keywords in agent_keywords.items():
            score = sum(1 for kw in keywords if kw in task_lower)
            if score > best_score:
                best_score = score
                best_match = agent_name

        return AGENTS.get(best_match) if best_match else None

    def get_system_prompt(self, agent_name: str, context: Optional[str] = None) -> str:
        """
        Get the full system prompt for an agent

        Args:
            agent_name: Name of the agent
            context: Additional context to include

        Returns:
            Complete system prompt
        """
        agent = AGENTS.get(agent_name)
        if not agent:
            return ""

        prompt_parts = [
            f"# You are {agent.title}: {agent.name}",
            f"\n## Expertise: {', '.join(agent.expertise)}",
            f"\n## Personality: {', '.join(agent.personality_traits)}",
            f"\n## Approach: {agent.approach.value}",
            f"\n\n{agent.system_prompt}",
        ]

        if context:
            prompt_parts.append(f"\n\n## Current Context\n{context}")

        return '\n'.join(prompt_parts)

    def get_agent_summary(self) -> str:
        """Get a summary of all available agents"""
        lines = ["# Available Agents\n"]
        for agent in AGENTS.values():
            lines.append(f"## {agent.name} ({agent.title})")
            lines.append(f"**Expertise**: {', '.join(agent.expertise)}")
            lines.append(f"**Approach**: {agent.approach.value}")
            lines.append(f"**Tools**: {', '.join(agent.tools)}")
            lines.append("")
        return '\n'.join(lines)


# Convenience function
def create_agent_manager(brain=None, voice=None) -> AgentManager:
    """Create an agent manager"""
    return AgentManager(brain=brain, voice=voice)


# Test if run directly
if __name__ == "__main__":
    manager = AgentManager()

    print("=== Available Agents ===\n")
    for name in manager.list_agents():
        agent = manager.get_agent(name)
        print(f"{agent.name} ({agent.title})")
        print(f"  Expertise: {', '.join(agent.expertise[:3])}...")
        print(f"  Approach: {agent.approach.value}")
        print()

    print("=== Agent Selection Test ===\n")
    test_tasks = [
        "Fix the bug in the authentication module",
        "Research quantum computing applications",
        "Design the API architecture",
        "Scan the website for vulnerabilities",
        "Write documentation for the API",
        "Analyze the sales data trends"
    ]

    for task in test_tasks:
        agent = manager.get_agent_for_task(task)
        if agent:
            print(f"Task: {task}")
            print(f"  Agent: {agent.name}")
            print()
