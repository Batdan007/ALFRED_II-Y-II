"""
Task Classifier - Intelligent Agentic Task Detection & Classification

Automatically detects and classifies the type of task Alfred is being asked to perform,
enabling intelligent agent selection without user prompting.

Task Types:
- CODE_MODIFICATION: Modifying existing code, creating new code
- CODE_REVIEW: Analyzing, reviewing, or explaining code
- SYSTEM_LEARNING: Learning from mistakes, updating processes
- CYBERSECURITY: Security analysis, penetration testing, threat modeling
- ARCHITECTURE: System design, architecture decisions
- RESEARCH: Information gathering, research, analysis
- OPTIMIZATION: Performance tuning, improvements
- DEBUGGING: Problem-solving, troubleshooting
- DATA_ANALYSIS: Data processing, analytics
- DOCUMENTATION: Writing docs, explanations

Author: Daniel J Rita (BATDAN)
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from pathlib import Path


class TaskType(Enum):
    """Enumeration of task types"""
    CODE_MODIFICATION = "code_modification"
    CODE_REVIEW = "code_review"
    SYSTEM_LEARNING = "system_learning"
    CYBERSECURITY = "cybersecurity"
    ARCHITECTURE = "architecture"
    RESEARCH = "research"
    OPTIMIZATION = "optimization"
    DEBUGGING = "debugging"
    DATA_ANALYSIS = "data_analysis"
    DOCUMENTATION = "documentation"
    UNKNOWN = "unknown"


class TaskClassifier:
    """
    Classifies user requests into specific task types for intelligent agent routing.

    Enables Alfred to determine which specialized agent (engineer, security, researcher, etc.)
    should handle each request without explicit user specification.
    """

    def __init__(self, brain=None):
        """
        Initialize Task Classifier

        Args:
            brain: AlfredBrain instance for learning from patterns
        """
        self.brain = brain
        
        # Pattern definitions for task classification
        self.patterns = {
            TaskType.CODE_MODIFICATION: {
                "keywords": [
                    "create", "write", "build", "implement", "modify", "update", "add",
                    "refactor", "fix bug", "patch", "rewrite", "convert", "migrate",
                    "generate code", "write function", "write class", "script",
                    "implement feature", "add method", "change function"
                ],
                "patterns": [
                    r"(?:create|write|build|implement|modify|update).*(?:code|script|function|class|module)",
                    r"(?:refactor|rewrite|convert).*(?:from|to) (\w+)",
                    r"fix.*(?:bug|issue|error|problem)",
                    r"(?:add|implement) (?:feature|functionality)",
                    r"(?:patch|update).*code",
                    r"write (?:a )?(?:python|javascript|java|cpp|c\#|go|rust) (?:script|function|class)",
                ]
            },
            TaskType.CODE_REVIEW: {
                "keywords": [
                    "review", "analyze", "explain", "understand", "read", "check",
                    "look at", "examine", "audit", "inspect", "evaluate",
                    "what does", "how does", "meaning of", "purpose of",
                    "document", "annotate"
                ],
                "patterns": [
                    r"(?:review|analyze|examine).*(?:code|script|function|class|module)",
                    r"explain.*(?:code|this|that|what)",
                    r"(?:what|how) (?:does|can|will).*(?:code|script|function|class)",
                    r"(?:audit|inspect|evaluate).*(?:code|implementation)",
                    r"(?:document|comment) (?:this|the).*code",
                ]
            },
            TaskType.SYSTEM_LEARNING: {
                "keywords": [
                    "learn", "mistake", "error", "i was wrong", "correction", "i realized",
                    "update process", "improve", "better", "lesson", "learned",
                    "adjust", "refine", "tune", "optimize parameters", "fix process",
                    "remember this", "don't forget"
                ],
                "patterns": [
                    r"i (?:made a |was |realized |made the )(?:mistake|error|wrong|error)",
                    r"(?:lesson|learned|mistake).*(?:for )?(?:next time|future)",
                    r"(?:update|improve|adjust|refine).*(?:process|approach|method)",
                    r"don't (?:repeat|make) (?:this|that) (?:mistake|error)",
                    r"remember.*(?:for next time|in future)",
                ]
            },
            TaskType.CYBERSECURITY: {
                "keywords": [
                    "security", "vulnerability", "penetration", "pentest", "hack", "breach",
                    "exploit", "attack", "threat", "risk", "compliance", "encrypt",
                    "authentication", "authorization", "access control", "malware",
                    "patch", "sanitize", "injection", "xss", "csrf", "dos"
                ],
                "patterns": [
                    r"(?:security|penetration|pentest|vulnerability) (?:audit|assessment|testing|scan)",
                    r"(?:find|identify|discover) (?:vulnerabilities|exploits|security issues)",
                    r"(?:hack|breach|attack) (?:vector|scenario|simulation)",
                    r"(?:encrypt|secure|harden).*(?:code|system|application)",
                    r"(?:sanitize|validate|escape).*(?:input|data|user input)",
                    r"(?:compliance|regulatory).*(?:requirement|standard)",
                ]
            },
            TaskType.ARCHITECTURE: {
                "keywords": [
                    "architecture", "design", "system design", "pattern", "structure",
                    "scalability", "reliability", "microservices", "database", "schema",
                    "deployment", "infrastructure", "devops", "cloud", "distributed",
                    "framework", "technology choice", "tradeoff", "decision"
                ],
                "patterns": [
                    r"(?:design|architect).*(?:system|application|solution|infrastructure)",
                    r"(?:system design|architecture).*(?:for|to handle)",
                    r"(?:technology|framework) (?:choice|decision|selection)",
                    r"(?:database|schema) (?:design|planning)",
                    r"(?:scalability|reliability|performance).*(?:consideration|tradeoff)",
                    r"(?:microservices|distributed).*(?:architecture|pattern)",
                ]
            },
            TaskType.RESEARCH: {
                "keywords": [
                    "research", "find", "look up", "investigate", "information",
                    "data", "statistics", "trend", "analysis", "study",
                    "compare", "benchmark", "survey", "report"
                ],
                "patterns": [
                    r"(?:research|find|look up|investigate).*(?:about|on|regarding)",
                    r"(?:compare|benchmark).*(?:vs|versus|against)",
                    r"(?:find|get).*(?:information|data|statistics).*(?:about|on)",
                    r"(?:survey|study).*(?:trend|market|competition)",
                ]
            },
            TaskType.OPTIMIZATION: {
                "keywords": [
                    "optimize", "improve", "faster", "performance", "efficiency",
                    "reduce", "simplify", "streamline", "enhance", "tuning",
                    "bottleneck", "profiling", "benchmark", "caching", "compression"
                ],
                "patterns": [
                    r"(?:optimize|improve|enhance).*(?:performance|speed|efficiency)",
                    r"(?:make|be) (?:faster|more efficient|optimized)",
                    r"(?:reduce|minimize).*(?:latency|overhead|memory|cpu)",
                    r"(?:bottleneck|slow).*(?:part|area|section)",
                    r"(?:caching|compression|optimization).*(?:strategy|technique)",
                ]
            },
            TaskType.DEBUGGING: {
                "keywords": [
                    "debug", "problem", "error", "bug", "crash", "fail",
                    "issue", "not working", "broken", "doesn't work",
                    "why", "what's wrong", "trace", "log"
                ],
                "patterns": [
                    r"(?:debug|trace|find).*(?:bug|error|problem|issue)",
                    r"(?:why|why is).*(?:failing|crashing|not working|broken)",
                    r"(?:what's|what is).*(?:wrong|error|problem)",
                    r"(?:fix|resolve|troubleshoot).*(?:bug|error|issue)",
                    r"(?:error|exception|crash).*(?:message|trace|stack)",
                ]
            },
            TaskType.DATA_ANALYSIS: {
                "keywords": [
                    "data", "analysis", "analytics", "statistics", "process",
                    "sql", "query", "database", "dataframe", "dataset",
                    "visualization", "chart", "graph", "report", "metrics"
                ],
                "patterns": [
                    r"(?:analyze|process|query).*(?:data|dataset|database)",
                    r"(?:create|generate).*(?:report|visualization|chart|graph).*(?:from|of)",
                    r"(?:data|dataset|table).*(?:analysis|processing|transformation)",
                    r"(?:sql|query).*(?:data|table|database)",
                ]
            },
            TaskType.DOCUMENTATION: {
                "keywords": [
                    "document", "readme", "guide", "tutorial", "instruction",
                    "explanation", "comment", "docstring", "manual",
                    "describe", "explain", "write about", "how to"
                ],
                "patterns": [
                    r"(?:document|write).*(?:code|function|class|api|module)",
                    r"(?:create|write).*(?:readme|guide|tutorial|documentation)",
                    r"(?:add|write).*(?:docstring|comment|explanation)",
                    r"(?:explain|describe).*(?:how to|way to) .*(?:use|do)",
                ]
            },
        }

    def classify(self, task_input: str, context: Optional[Dict] = None) -> Tuple[TaskType, float, Dict]:
        """
        Classify a task input into a specific task type.

        Args:
            task_input: User input describing the task
            context: Optional context from conversation history

        Returns:
            Tuple of (TaskType, confidence_score, metadata)
        """
        if not task_input or not task_input.strip():
            return (TaskType.UNKNOWN, 0.0, {})

        # Normalize input
        normalized = task_input.lower().strip()

        # Score each task type
        scores = {}
        for task_type, pattern_data in self.patterns.items():
            score = self._score_task_type(normalized, task_type, pattern_data)
            scores[task_type] = score

        # Find best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # Build metadata
        metadata = {
            "all_scores": {t.value: s for t, s in scores.items()},
            "top_3": sorted(
                [(t.value, s) for t, s in scores.items()],
                key=lambda x: x[1],
                reverse=True
            )[:3],
            "input_length": len(task_input),
            "classified_at": datetime.now().isoformat(),
        }

        # If low confidence, check context from brain
        if best_score < 0.4 and self.brain:
            contextual_type, contextual_score = self._classify_from_context(
                normalized, context
            )
            if contextual_score > best_score:
                best_type = contextual_type
                best_score = contextual_score
                metadata["source"] = "contextual"
            else:
                metadata["source"] = "pattern_match"
        else:
            metadata["source"] = "pattern_match"

        # Store classification in brain if available
        if self.brain and best_score > 0.3:
            try:
                self.brain.store_knowledge(
                    "agentic_tasks",
                    f"task_classification_{datetime.now().isoformat()}",
                    json.dumps({
                        "task_type": best_type.value,
                        "confidence": best_score,
                        "input": task_input[:200],  # Truncate for storage
                    }),
                    importance=7 if best_score > 0.7 else 5,
                    confidence=best_score
                )
            except Exception as e:
                pass  # Silently fail if brain storage unavailable

        return (best_type if best_score > 0.0 else TaskType.UNKNOWN, best_score, metadata)

    def _score_task_type(self, normalized: str, task_type: TaskType, pattern_data: Dict) -> float:
        """
        Score how well a task input matches a specific task type.

        Uses both keyword matching and regex pattern matching.
        """
        score = 0.0

        # Keyword matching (lower weight)
        keywords = pattern_data.get("keywords", [])
        keyword_matches = sum(
            1 for kw in keywords
            if kw in normalized
        )
        keyword_score = min(1.0, keyword_matches / max(len(keywords), 1) * 0.5)
        score += keyword_score * 0.3

        # Pattern matching (higher weight)
        patterns = pattern_data.get("patterns", [])
        pattern_matches = sum(
            1 for pattern in patterns
            if re.search(pattern, normalized)
        )
        pattern_score = min(1.0, pattern_matches / max(len(patterns), 1))
        score += pattern_score * 0.7

        return min(1.0, score)

    def _classify_from_context(
        self, normalized: str, context: Optional[Dict]
    ) -> Tuple[TaskType, float]:
        """
        Classify using context from previous conversations.

        If current task is related to previous high-confidence tasks,
        inherit that classification.
        """
        if not self.brain or not context:
            return (TaskType.UNKNOWN, 0.0)

        try:
            # Get recent task classifications
            recent_tasks = self.brain.search_knowledge(
                "agentic_tasks",
                limit=5,
                semantic=False
            )

            if not recent_tasks:
                return (TaskType.UNKNOWN, 0.0)

            # Score relevance to recent tasks
            best_match = None
            best_relevance = 0.0

            for task in recent_tasks:
                task_data = json.loads(task.get("value", "{}"))
                task_type_str = task_data.get("task_type")

                if not task_type_str:
                    continue

                # Simple relevance check
                task_input = task_data.get("input", "")
                common_words = set(normalized.split()) & set(task_input.lower().split())
                relevance = len(common_words) / max(len(normalized.split()), 1)

                if relevance > best_relevance:
                    best_relevance = relevance
                    best_match = TaskType(task_type_str)

            if best_relevance > 0.3 and best_match:
                return (best_match, best_relevance * 0.8)

        except Exception:
            pass

        return (TaskType.UNKNOWN, 0.0)

    def get_suggested_agents(self, task_type: TaskType, confidence: float) -> List[Tuple[str, float]]:
        """
        Get suggested agents for a task type with confidence scores.

        Returns:
            List of (agent_name, suitability_score) tuples
        """
        agent_mapping = {
            TaskType.CODE_MODIFICATION: [
                ("alfred-engineer", 1.0),
                ("engineer", 0.95),
                ("architect", 0.5),
            ],
            TaskType.CODE_REVIEW: [
                ("alfred-engineer", 0.95),
                ("engineer", 0.9),
                ("architect", 0.6),
            ],
            TaskType.SYSTEM_LEARNING: [
                ("alfred-engineer", 0.9),
                ("architect", 0.8),
                ("engineer", 0.7),
            ],
            TaskType.CYBERSECURITY: [
                ("pentester", 1.0),
                ("architect", 0.7),
                ("alfred-engineer", 0.5),
            ],
            TaskType.ARCHITECTURE: [
                ("architect", 1.0),
                ("alfred-engineer", 0.8),
                ("engineer", 0.7),
            ],
            TaskType.RESEARCH: [
                ("alfred-researcher", 1.0),
                ("researcher", 0.95),
                ("architect", 0.4),
            ],
            TaskType.OPTIMIZATION: [
                ("architect", 0.95),
                ("alfred-engineer", 0.85),
                ("engineer", 0.8),
            ],
            TaskType.DEBUGGING: [
                ("alfred-engineer", 1.0),
                ("engineer", 0.95),
                ("architect", 0.5),
            ],
            TaskType.DATA_ANALYSIS: [
                ("alfred-researcher", 0.95),
                ("researcher", 0.9),
                ("architect", 0.5),
            ],
            TaskType.DOCUMENTATION: [
                ("alfred-researcher", 0.9),
                ("researcher", 0.85),
                ("alfred-engineer", 0.7),
            ],
            TaskType.UNKNOWN: [
                ("alfred-engineer", 0.5),
                ("engineer", 0.5),
            ],
        }

        agents = agent_mapping.get(task_type, [("alfred-engineer", 0.5)])

        # Adjust scores by task classification confidence
        adjusted = [
            (agent, min(1.0, score * confidence))
            for agent, score in agents
        ]

        return adjusted
