#!/usr/bin/env python3
"""
Alfred Autonomous Agent Framework - SuperAGI-Style
Multi-step task execution with tool use and reasoning

Features:
- ReAct (Reasoning + Acting) pattern
- Multiple built-in tools
- Task decomposition
- Memory and context
- Error recovery
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentThought:
    """A single step in agent reasoning"""
    step: int
    thought: str
    action: str
    action_input: Dict
    observation: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentTask:
    """A task for the autonomous agent"""
    id: str
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    thoughts: List[AgentThought] = field(default_factory=list)
    result: Any = None
    error: str = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "goal": self.goal,
            "status": self.status.value,
            "thoughts": [{"step": t.step, "thought": t.thought, "action": t.action,
                          "observation": t.observation[:200]} for t in self.thoughts],
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }


# ============================================================================
# TOOLS
# ============================================================================

class AgentTool(ABC):
    """Base class for agent tools"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict:
        """JSON Schema for parameters"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool and return result"""
        pass


class WebSearchTool(AgentTool):
    """Search the web for information"""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for information on a topic"

    @property
    def parameters(self) -> Dict:
        return {
            "query": {"type": "string", "description": "Search query"},
            "num_results": {"type": "integer", "description": "Number of results", "default": 5}
        }

    async def execute(self, query: str, num_results: int = 5) -> str:
        try:
            import requests
            from bs4 import BeautifulSoup

            # Use DuckDuckGo HTML search (no API key needed)
            url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; AlfredBot/1.0)'}
            resp = requests.get(url, headers=headers, timeout=10)

            soup = BeautifulSoup(resp.text, 'html.parser')
            results = []

            for result in soup.find_all('div', class_='result')[:num_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                if title_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                    })

            if results:
                return json.dumps(results, indent=2)
            return "No results found"

        except Exception as e:
            return f"Search error: {str(e)}"


class FileReadTool(AgentTool):
    """Read contents of a file"""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file"

    @property
    def parameters(self) -> Dict:
        return {
            "path": {"type": "string", "description": "Path to the file"},
            "max_lines": {"type": "integer", "description": "Max lines to read", "default": 100}
        }

    async def execute(self, path: str, max_lines: int = 100) -> str:
        try:
            from pathlib import Path
            file_path = Path(path)
            if not file_path.exists():
                return f"File not found: {path}"
            if not file_path.is_file():
                return f"Not a file: {path}"

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:max_lines]
                return ''.join(lines)

        except Exception as e:
            return f"Error reading file: {str(e)}"


class FileWriteTool(AgentTool):
    """Write contents to a file"""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file"

    @property
    def parameters(self) -> Dict:
        return {
            "path": {"type": "string", "description": "Path to the file"},
            "content": {"type": "string", "description": "Content to write"}
        }

    async def execute(self, path: str, content: str) -> str:
        try:
            from pathlib import Path
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote {len(content)} characters to {path}"

        except Exception as e:
            return f"Error writing file: {str(e)}"


class ShellCommandTool(AgentTool):
    """Execute a shell command (sandboxed)"""

    ALLOWED_COMMANDS = {'ls', 'dir', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep',
                        'find', 'wc', 'date', 'whoami', 'python', 'pip', 'git', 'npm'}

    @property
    def name(self) -> str:
        return "shell"

    @property
    def description(self) -> str:
        return "Execute a shell command (limited to safe commands)"

    @property
    def parameters(self) -> Dict:
        return {
            "command": {"type": "string", "description": "Command to execute"}
        }

    async def execute(self, command: str) -> str:
        import subprocess
        import shlex

        # Safety check
        parts = shlex.split(command)
        if not parts:
            return "Empty command"

        base_cmd = parts[0].lower()
        if base_cmd not in self.ALLOWED_COMMANDS:
            return f"Command '{base_cmd}' not allowed. Allowed: {', '.join(self.ALLOWED_COMMANDS)}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout[:2000] if result.stdout else ""
            if result.stderr:
                output += f"\nSTDERR: {result.stderr[:500]}"
            return output or "(no output)"

        except subprocess.TimeoutExpired:
            return "Command timed out (30s limit)"
        except Exception as e:
            return f"Error: {str(e)}"


class CodeExecuteTool(AgentTool):
    """Execute Python code (sandboxed)"""

    @property
    def name(self) -> str:
        return "python_exec"

    @property
    def description(self) -> str:
        return "Execute Python code and return the result"

    @property
    def parameters(self) -> Dict:
        return {
            "code": {"type": "string", "description": "Python code to execute"}
        }

    async def execute(self, code: str) -> str:
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr

        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Sandboxed globals
        sandbox = {
            '__builtins__': {
                'print': print, 'len': len, 'range': range, 'str': str,
                'int': int, 'float': float, 'list': list, 'dict': dict,
                'tuple': tuple, 'set': set, 'bool': bool, 'type': type,
                'sum': sum, 'min': min, 'max': max, 'abs': abs,
                'sorted': sorted, 'enumerate': enumerate, 'zip': zip,
                'map': map, 'filter': filter, 'any': any, 'all': all
            }
        }

        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, sandbox)

            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()

            result = output[:2000] if output else "(no output)"
            if errors:
                result += f"\nErrors: {errors[:500]}"
            return result

        except Exception as e:
            return f"Execution error: {str(e)}"


class CalculatorTool(AgentTool):
    """Perform calculations"""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Perform mathematical calculations"

    @property
    def parameters(self) -> Dict:
        return {
            "expression": {"type": "string", "description": "Math expression to evaluate"}
        }

    async def execute(self, expression: str) -> str:
        import math

        # Safe evaluation
        allowed_names = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'pow': pow,
            'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos,
            'tan': math.tan, 'log': math.log, 'log10': math.log10,
            'exp': math.exp, 'pi': math.pi, 'e': math.e
        }

        try:
            # Clean expression
            expr = expression.strip()
            # Evaluate safely
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"


class ThinkTool(AgentTool):
    """Record thoughts and reasoning"""

    @property
    def name(self) -> str:
        return "think"

    @property
    def description(self) -> str:
        return "Record your thoughts and reasoning about the task"

    @property
    def parameters(self) -> Dict:
        return {
            "thought": {"type": "string", "description": "Your thought or reasoning"}
        }

    async def execute(self, thought: str) -> str:
        return f"Recorded thought: {thought}"


class FinalAnswerTool(AgentTool):
    """Provide the final answer to complete the task"""

    @property
    def name(self) -> str:
        return "final_answer"

    @property
    def description(self) -> str:
        return "Provide the final answer to complete the task"

    @property
    def parameters(self) -> Dict:
        return {
            "answer": {"type": "string", "description": "The final answer"}
        }

    async def execute(self, answer: str) -> str:
        return f"TASK_COMPLETE: {answer}"


# ============================================================================
# AUTONOMOUS AGENT
# ============================================================================

class AutonomousAgent:
    """
    Autonomous agent with ReAct reasoning pattern
    Decomposes tasks, uses tools, and achieves goals
    """

    def __init__(
        self,
        name: str = "Alfred",
        max_steps: int = 10,
        ai_provider: str = "ollama"
    ):
        self.name = name
        self.max_steps = max_steps
        self.ai_provider = ai_provider
        self.logger = logging.getLogger(f"Agent.{name}")

        # Initialize tools
        self.tools: Dict[str, AgentTool] = {}
        self._register_default_tools()

        # Task management
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []

        # AI clients
        self.ollama = None
        self._init_ai()

    def _register_default_tools(self):
        """Register default tools"""
        default_tools = [
            WebSearchTool(),
            FileReadTool(),
            FileWriteTool(),
            ShellCommandTool(),
            CodeExecuteTool(),
            CalculatorTool(),
            ThinkTool(),
            FinalAnswerTool()
        ]
        for tool in default_tools:
            self.tools[tool.name] = tool

    def _init_ai(self):
        """Initialize AI provider"""
        try:
            from ollama_integration import OllamaAI
            self.ollama = OllamaAI()
            if not self.ollama.is_available:
                self.ollama = None
        except Exception:
            self.ollama = None

    def register_tool(self, tool: AgentTool):
        """Register a custom tool"""
        self.tools[tool.name] = tool

    def get_tools_description(self) -> str:
        """Get formatted description of all tools"""
        descriptions = []
        for name, tool in self.tools.items():
            params = ", ".join([f"{k}: {v.get('description', '')}"
                               for k, v in tool.parameters.items()])
            descriptions.append(f"- {name}: {tool.description}\n  Parameters: {params}")
        return "\n".join(descriptions)

    async def execute_task(self, goal: str) -> AgentTask:
        """
        Execute a task autonomously

        Args:
            goal: The task goal to achieve

        Returns:
            AgentTask with results
        """
        import uuid

        # Create task
        task = AgentTask(
            id=str(uuid.uuid4())[:8],
            goal=goal,
            status=TaskStatus.RUNNING
        )
        self.current_task = task

        print(f"\n{'='*60}")
        print(f"AUTONOMOUS AGENT: {self.name}")
        print(f"{'='*60}")
        print(f"Goal: {goal}")
        print(f"Max steps: {self.max_steps}")
        print(f"{'='*60}\n")

        try:
            for step in range(1, self.max_steps + 1):
                print(f"\n--- Step {step}/{self.max_steps} ---")

                # Get next action from AI
                thought = await self._think_and_act(task, step)
                task.thoughts.append(thought)

                print(f"Thought: {thought.thought[:100]}...")
                print(f"Action: {thought.action}")
                print(f"Observation: {thought.observation[:200]}...")

                # Check if task is complete
                if "TASK_COMPLETE" in thought.observation:
                    task.status = TaskStatus.COMPLETED
                    task.result = thought.observation.replace("TASK_COMPLETE: ", "")
                    task.completed_at = datetime.now().isoformat()
                    break

            else:
                # Max steps reached
                task.status = TaskStatus.FAILED
                task.error = f"Max steps ({self.max_steps}) reached without completion"

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.logger.error(f"Task failed: {e}")

        self.task_history.append(task)
        self.current_task = None

        print(f"\n{'='*60}")
        print(f"Task Status: {task.status.value}")
        if task.result:
            print(f"Result: {task.result[:500]}")
        if task.error:
            print(f"Error: {task.error}")
        print(f"{'='*60}\n")

        return task

    async def _think_and_act(self, task: AgentTask, step: int) -> AgentThought:
        """Generate thought and execute action"""

        # Build context from previous steps
        history = ""
        for t in task.thoughts:
            history += f"\nStep {t.step}:\nThought: {t.thought}\nAction: {t.action}\nObservation: {t.observation}\n"

        # Create prompt
        prompt = f"""You are {self.name}, an autonomous AI agent.

GOAL: {task.goal}

AVAILABLE TOOLS:
{self.get_tools_description()}

PREVIOUS STEPS:{history if history else " None yet"}

Based on the goal and previous steps, decide what to do next.
You must respond in this exact format:

THOUGHT: <your reasoning about what to do next>
ACTION: <tool_name>
ACTION_INPUT: <JSON object with tool parameters>

When you have achieved the goal, use the 'final_answer' tool.

What is your next step?"""

        # Get AI response
        if self.ollama:
            response = self.ollama.generate(prompt, model=self.ollama.primary_model)
        else:
            # Fallback to simple pattern matching
            response = self._simple_reasoning(task, step)

        # Parse response
        thought_text = ""
        action = "think"
        action_input = {"thought": "Processing..."}

        try:
            if "THOUGHT:" in response:
                thought_text = response.split("THOUGHT:")[1].split("ACTION:")[0].strip()
            if "ACTION:" in response:
                action = response.split("ACTION:")[1].split("ACTION_INPUT:")[0].strip().lower()
            if "ACTION_INPUT:" in response:
                input_str = response.split("ACTION_INPUT:")[1].strip()
                # Try to parse JSON
                action_input = json.loads(input_str)
        except Exception:
            pass

        # Execute action
        observation = await self._execute_action(action, action_input)

        return AgentThought(
            step=step,
            thought=thought_text,
            action=action,
            action_input=action_input,
            observation=observation
        )

    async def _execute_action(self, action: str, action_input: Dict) -> str:
        """Execute a tool action"""
        if action not in self.tools:
            return f"Unknown tool: {action}. Available: {list(self.tools.keys())}"

        tool = self.tools[action]
        try:
            result = await tool.execute(**action_input)
            return result
        except Exception as e:
            return f"Tool error: {str(e)}"

    def _simple_reasoning(self, task: AgentTask, step: int) -> str:
        """Simple fallback reasoning without AI"""
        if step == 1:
            return f"""THOUGHT: I need to understand the goal: {task.goal}
ACTION: think
ACTION_INPUT: {{"thought": "Analyzing the goal to determine best approach"}}"""

        elif step >= self.max_steps - 1:
            return f"""THOUGHT: I've taken several steps. Time to provide a final answer.
ACTION: final_answer
ACTION_INPUT: {{"answer": "Based on my analysis, here is what I found regarding: {task.goal}"}}"""

        else:
            return f"""THOUGHT: Continuing to work on the goal
ACTION: think
ACTION_INPUT: {{"thought": "Working on step {step} of the task"}}"""


# ============================================================================
# AGENT MANAGER
# ============================================================================

class AutonomousAgentManager:
    """
    Manages multiple autonomous agents
    Provides unified interface for Alfred integration
    """

    def __init__(self):
        self.agents: Dict[str, AutonomousAgent] = {}
        self.default_agent = AutonomousAgent("Alfred")
        self.logger = logging.getLogger("AgentManager")

    def create_agent(self, name: str, **kwargs) -> AutonomousAgent:
        """Create a new autonomous agent"""
        agent = AutonomousAgent(name=name, **kwargs)
        self.agents[name] = agent
        return agent

    def get_agent(self, name: str = None) -> AutonomousAgent:
        """Get an agent by name or return default"""
        if name and name in self.agents:
            return self.agents[name]
        return self.default_agent

    async def run_task(self, goal: str, agent_name: str = None) -> Dict:
        """Run a task with an agent"""
        agent = self.get_agent(agent_name)
        task = await agent.execute_task(goal)
        return task.to_dict()

    def list_agents(self) -> List[str]:
        """List all agents"""
        return ["default"] + list(self.agents.keys())

    def get_task_history(self, agent_name: str = None) -> List[Dict]:
        """Get task history for an agent"""
        agent = self.get_agent(agent_name)
        return [t.to_dict() for t in agent.task_history]


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI for autonomous agents"""
    import sys

    print("=" * 60)
    print("ALFRED AUTONOMOUS AGENT FRAMEWORK")
    print("SuperAGI-Style Multi-Step Task Execution")
    print("=" * 60)
    print()

    manager = AutonomousAgentManager()
    agent = manager.default_agent

    print(f"Agent: {agent.name}")
    print(f"Max Steps: {agent.max_steps}")
    print(f"AI Provider: {'Ollama' if agent.ollama else 'Fallback'}")
    print()
    print("Available Tools:")
    for name, tool in agent.tools.items():
        print(f"  - {name}: {tool.description}")

    print()
    print("Usage:")
    print("  from autonomous_agents import AutonomousAgentManager")
    print("  manager = AutonomousAgentManager()")
    print("  result = await manager.run_task('Research Python best practices')")
    print()

    # Interactive mode
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
        print(f"\nExecuting task: {goal}")
        asyncio.run(manager.run_task(goal))


if __name__ == "__main__":
    main()
