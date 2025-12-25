"""
Agent Selector - Intelligent Agent Routing for ALFRED

Selects the optimal agent (engineer, researcher, security, architect) for each task
based on task classification, brain learning patterns, and success history.

Alfred decides which agents to use autonomously based on:
1. Task type classification (code, security, research, architecture, etc.)
2. Historical success patterns in brain (which agents succeeded before)
3. Confidence levels in agent expertise for this specific task type
4. Current context and recent conversation patterns

Author: Daniel J Rita (BATDAN)
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from core.task_classifier import TaskType, TaskClassifier


class ModelTier(Enum):
    """Model selection tiers based on task complexity"""
    HAIKU = "haiku"        # Fast, simple tasks (10-20x faster)
    SONNET = "sonnet"      # Balanced, standard implementation
    OPUS = "opus"          # Complex reasoning, maximum intelligence


class AgentSelector:
    """
    Intelligent agent selector that enables Alfred to autonomously choose
    the best agent(s) for each task based on learned patterns and historical success.

    Key Features:
    - Learns which agents perform best for each task type
    - Routes to specialized agents without user specification
    - Tracks success rates and adjusts selections accordingly
    - Can delegate to multiple agents in parallel
    - Makes model tier decisions (haiku/sonnet/opus) based on complexity
    """

    def __init__(self, brain=None):
        """
        Initialize Agent Selector

        Args:
            brain: AlfredBrain instance for learning and pattern tracking
        """
        self.brain = brain
        self.classifier = TaskClassifier(brain=brain)

        # Agent profiles
        self.agents = {
            "alfred-engineer": {
                "description": "ALFRED's specialized engineering agent",
                "strengths": ["code_modification", "code_review", "debugging", "system_learning"],
                "specialization": "Implementation and code quality",
                "personality": "british-butler-engineer",
            },
            "alfred-researcher": {
                "description": "ALFRED's specialized research agent",
                "strengths": ["research", "data_analysis", "documentation", "architecture"],
                "specialization": "Research and knowledge synthesis",
                "personality": "british-butler-researcher",
            },
            "engineer": {
                "description": "Generic engineering agent",
                "strengths": ["code_modification", "code_review", "debugging"],
                "specialization": "Implementation",
                "personality": "technical",
            },
            "researcher": {
                "description": "Generic research agent",
                "strengths": ["research", "data_analysis", "documentation"],
                "specialization": "Research",
                "personality": "analytical",
            },
            "architect": {
                "description": "System architect agent",
                "strengths": ["architecture", "optimization", "system_learning"],
                "specialization": "System design and optimization",
                "personality": "strategic",
            },
            "pentester": {
                "description": "Security pentesting agent",
                "strengths": ["cybersecurity"],
                "specialization": "Security analysis and testing",
                "personality": "security-focused",
            },
            "designer": {
                "description": "UI/UX designer agent",
                "strengths": ["documentation", "architecture"],
                "specialization": "Design and user experience",
                "personality": "creative",
            },
        }

    def select_agents(
        self,
        task_input: str,
        context: Optional[Dict] = None,
        max_agents: int = 1,
        parallel: bool = False,
    ) -> List[Dict]:
        """
        Select optimal agents for a task.

        Args:
            task_input: Description of the task
            context: Optional context from conversation
            max_agents: Maximum number of agents to select
            parallel: Whether agents can work in parallel

        Returns:
            List of agent selection recommendations with model tiers
        """
        # Classify the task
        task_type, confidence, metadata = self.classifier.classify(task_input, context)

        # Get suggested agents from classifier
        suggested_agents = self.classifier.get_suggested_agents(task_type, confidence)

        # Rank agents using brain patterns
        ranked_agents = self._rank_agents(
            suggested_agents, task_type, task_input
        )

        # Select top N agents
        selections = ranked_agents[:max_agents]

        # Determine model tiers
        results = []
        for agent_name, suitability_score in selections:
            model_tier = self._select_model_tier(task_type, confidence)

            result = {
                "agent": agent_name,
                "agent_info": self.agents.get(agent_name, {}),
                "suitability_score": suitability_score,
                "task_type": task_type.value,
                "task_confidence": confidence,
                "model_tier": model_tier.value,
                "rationale": self._generate_rationale(
                    agent_name, task_type, suitability_score
                ),
                "metadata": metadata,
                "decision_timestamp": datetime.now().isoformat(),
            }

            results.append(result)

        # Store decision in brain
        if self.brain and results:
            try:
                self.brain.store_knowledge(
                    "agent_decisions",
                    f"decision_{datetime.now().isoformat()}",
                    json.dumps({
                        "task_input": task_input[:200],
                        "selected_agents": [r["agent"] for r in results],
                        "task_type": task_type.value,
                        "confidence": confidence,
                    }),
                    importance=7,
                    confidence=confidence,
                )
            except Exception:
                pass

        return results

    def _rank_agents(
        self,
        suggested_agents: List[Tuple[str, float]],
        task_type: TaskType,
        task_input: str,
    ) -> List[Tuple[str, float]]:
        """
        Rank agents using brain patterns and historical success.

        Considers:
        - Success rate for this task type
        - Historical performance
        - Specialization match
        """
        if not self.brain:
            return suggested_agents

        ranked = []

        for agent_name, classifier_score in suggested_agents:
            # Get historical success rate from brain
            success_rate = self._get_agent_success_rate(agent_name, task_type)

            # Combine scores
            # 60% classifier recommendation, 40% historical performance
            combined_score = (classifier_score * 0.6) + (success_rate * 0.4)

            ranked.append((agent_name, combined_score))

        # Sort by combined score
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def _get_agent_success_rate(self, agent_name: str, task_type: TaskType) -> float:
        """
        Get historical success rate for an agent on this task type.

        Queries brain for agent performance patterns.
        """
        if not self.brain:
            return 0.5  # Neutral default

        try:
            # Search brain for agent performance records
            key = f"agent_perf_{agent_name}_{task_type.value}"
            knowledge = self.brain.recall_knowledge("agent_performance", key, min_confidence=0.5)

            if knowledge:
                data = json.loads(knowledge)
                return data.get("success_rate", 0.5)
        except Exception:
            pass

        return 0.5  # Default neutral score

    def _select_model_tier(self, task_type: TaskType, confidence: float) -> ModelTier:
        """
        Select appropriate model tier based on task complexity and confidence.

        - HAIKU: Low-complexity tasks (simple code review, documentation)
        - SONNET: Standard implementation (most code modifications)
        - OPUS: High-complexity tasks (architecture, security analysis)
        """
        complexity_map = {
            TaskType.CODE_MODIFICATION: ModelTier.SONNET,
            TaskType.CODE_REVIEW: ModelTier.HAIKU if confidence > 0.8 else ModelTier.SONNET,
            TaskType.SYSTEM_LEARNING: ModelTier.SONNET,
            TaskType.CYBERSECURITY: ModelTier.OPUS,  # Always high complexity
            TaskType.ARCHITECTURE: ModelTier.OPUS,   # Always high complexity
            TaskType.RESEARCH: ModelTier.SONNET,
            TaskType.OPTIMIZATION: ModelTier.SONNET,
            TaskType.DEBUGGING: ModelTier.SONNET,
            TaskType.DATA_ANALYSIS: ModelTier.HAIKU if confidence > 0.9 else ModelTier.SONNET,
            TaskType.DOCUMENTATION: ModelTier.HAIKU,
            TaskType.UNKNOWN: ModelTier.SONNET,  # Default to balanced
        }

        return complexity_map.get(task_type, ModelTier.SONNET)

    def _generate_rationale(
        self, agent_name: str, task_type: TaskType, score: float
    ) -> str:
        """
        Generate human-readable rationale for agent selection.
        """
        agent_info = self.agents.get(agent_name, {})
        specialization = agent_info.get("specialization", "general")

        rationale_parts = [
            f"{agent_name} specializes in {specialization}",
        ]

        if task_type in [TaskType.CYBERSECURITY]:
            rationale_parts.append("This task involves security analysis")
        elif task_type in [TaskType.ARCHITECTURE, TaskType.OPTIMIZATION]:
            rationale_parts.append("This task requires architectural thinking")
        elif task_type in [TaskType.CODE_MODIFICATION, TaskType.DEBUGGING]:
            rationale_parts.append("This task involves implementation")
        elif task_type in [TaskType.RESEARCH, TaskType.DATA_ANALYSIS]:
            rationale_parts.append("This task requires research capabilities")

        if score >= 0.9:
            rationale_parts.append("High confidence match")
        elif score >= 0.7:
            rationale_parts.append("Strong match")
        elif score >= 0.5:
            rationale_parts.append("Reasonable match")

        return ". ".join(rationale_parts) + "."

    def record_agent_outcome(
        self,
        agent_name: str,
        task_type: TaskType,
        success: bool,
        feedback: Optional[str] = None,
    ):
        """
        Record the outcome of an agent's task execution.

        Updates brain with success/failure data for learning.
        """
        if not self.brain:
            return

        try:
            key = f"agent_perf_{agent_name}_{task_type.value}"

            # Get current record
            current = self.brain.recall_knowledge("agent_performance", key, min_confidence=0.0)

            if current:
                data = json.loads(current)
                total = data.get("total_attempts", 0) + 1
                successes = data.get("successes", 0) + (1 if success else 0)
                success_rate = successes / total
            else:
                total = 1
                successes = 1 if success else 0
                success_rate = 1.0 if success else 0.0

            # Store updated record
            self.brain.store_knowledge(
                "agent_performance",
                key,
                json.dumps({
                    "agent": agent_name,
                    "task_type": task_type.value,
                    "total_attempts": total,
                    "successes": successes,
                    "success_rate": success_rate,
                    "last_used": datetime.now().isoformat(),
                    "feedback": feedback,
                }),
                importance=8,
                confidence=1.0 if total > 3 else (total / 3.0),
            )

            # Record skill tracking
            self.brain.track_skill_use(
                f"agent_use_{agent_name}",
                success=success,
                notes=f"Task type: {task_type.value}"
            )
        except Exception as e:
            pass  # Silently fail if brain storage unavailable

    def get_parallel_plan(
        self,
        task_input: str,
        num_parallel: int = 3,
    ) -> List[Dict]:
        """
        Create a parallel agent plan for tasks that can be parallelized.

        Example: Research task split across multiple researcher agents.
        """
        selections = self.select_agents(task_input, max_agents=num_parallel, parallel=True)

        # Group agents that can work in parallel
        parallel_plan = {
            "parallel_agents": selections,
            "coordination": "Independent execution - merge results after",
            "estimated_time": "Time of slowest agent",
            "suggested_merge_strategy": self._suggest_merge_strategy(selections),
        }

        return [parallel_plan]

    def _suggest_merge_strategy(self, selections: List[Dict]) -> str:
        """
        Suggest how to merge parallel agent results.
        """
        if len(selections) == 1:
            return "N/A - single agent"

        # Different strategies based on task type
        task_type_str = selections[0].get("task_type", "")

        if "research" in task_type_str:
            return "Combine findings by importance/confidence, deduplicate"
        elif "code" in task_type_str:
            return "Merge code changes, identify conflicts for manual review"
        elif "architecture" in task_type_str:
            return "Synthesize designs, identify patterns and best practices"
        elif "security" in task_type_str:
            return "Combine vulnerability findings, prioritize by severity"
        else:
            return "Merge results by relevance and confidence"
