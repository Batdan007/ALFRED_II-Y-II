"""
ALFRED Security Agent - Autonomous Security Scanning & Vulnerability Management

An autonomous agent that implements the ReAct (Reasoning + Acting) pattern
for comprehensive security assessment, vulnerability detection, and remediation tracking.

Capabilities:
- Autonomous security scanning with Strix
- Vulnerability analysis with Fabric AI patterns
- GitHub issue creation for findings
- Slack notifications for critical alerts
- Persistent memory of all scans and findings
- Mistake-based learning to improve over time

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
Patent Status: Integration covered under USPTO Provisional (Nov 11, 2025)
"""

import json
import logging
import os
import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


class AgentState(Enum):
    """States for the ReAct loop"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETE = "complete"
    ERROR = "error"


class ActionType(Enum):
    """Types of actions the agent can take"""
    SCAN_DIRECTORY = "scan_directory"
    SCAN_URL = "scan_url"
    SCAN_GITHUB = "scan_github"
    ANALYZE_FINDINGS = "analyze_findings"
    CREATE_GITHUB_ISSUE = "create_github_issue"
    SEND_SLACK_ALERT = "send_slack_alert"
    STORE_IN_MEMORY = "store_in_memory"
    APPLY_FABRIC_PATTERN = "apply_fabric_pattern"
    GENERATE_REPORT = "generate_report"


@dataclass
class AgentThought:
    """Represents a thought in the ReAct loop"""
    reasoning: str
    next_action: ActionType
    action_params: Dict[str, Any]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentObservation:
    """Represents an observation after an action"""
    action: ActionType
    result: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityFinding:
    """Represents a security vulnerability finding"""
    id: str
    title: str
    severity: str  # critical, high, medium, low, info
    description: str
    proof_of_concept: Optional[str] = None
    recommendation: str = ""
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    affected_component: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)


class AlfredSecurityAgent:
    """
    ALFRED Security Agent - Autonomous Security Scanning & Analysis

    Implements the ReAct (Reasoning + Acting) pattern for autonomous
    security operations. The agent can:

    1. THINK: Analyze the task and plan next steps
    2. ACT: Execute security tools (Strix, Fabric patterns)
    3. OBSERVE: Analyze results and determine completion
    4. LOOP: Continue until task is complete

    All actions are stored in Alfred Brain for persistent memory
    and continuous improvement through mistake-based learning.
    """

    def __init__(
        self,
        brain=None,
        strix_scanner=None,
        fabric_patterns=None,
        privacy_controller=None,
        voice=None,
        github_token: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        max_iterations: int = 10
    ):
        """
        Initialize the Security Agent

        Args:
            brain: AlfredBrain instance for persistent memory
            strix_scanner: StrixScanner instance for security scanning
            fabric_patterns: FabricPatterns instance for AI analysis
            privacy_controller: PrivacyController for cloud access
            voice: AlfredVoice instance for spoken output
            github_token: GitHub personal access token for issue creation
            slack_webhook: Slack webhook URL for notifications
            max_iterations: Maximum ReAct iterations before stopping
        """
        self.logger = logging.getLogger(__name__)

        # Core components
        self.brain = brain
        self.strix = strix_scanner
        self.fabric = fabric_patterns
        self.privacy_controller = privacy_controller
        self.voice = voice

        # External integrations
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.slack_webhook = slack_webhook or os.getenv("SLACK_WEBHOOK")

        # Agent state
        self.state = AgentState.IDLE
        self.max_iterations = max_iterations
        self.current_task: Optional[str] = None
        self.thoughts: List[AgentThought] = []
        self.observations: List[AgentObservation] = []
        self.findings: List[SecurityFinding] = []

        # Load components lazily
        self._init_components()

    def _init_components(self):
        """Initialize components if not provided"""
        if not self.brain:
            try:
                from core.brain import AlfredBrain
                self.brain = AlfredBrain()
            except ImportError:
                self.logger.warning("AlfredBrain not available")

        if not self.strix:
            try:
                from capabilities.security.strix_scanner import StrixScanner
                self.strix = StrixScanner(
                    privacy_controller=self.privacy_controller,
                    brain=self.brain
                )
            except ImportError:
                self.logger.warning("StrixScanner not available")

        if not self.fabric:
            try:
                from capabilities.fabric.fabric_patterns import FabricPatterns
                self.fabric = FabricPatterns()
            except ImportError:
                self.logger.warning("FabricPatterns not available")

    async def execute(self, task: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a security task using the ReAct loop

        Args:
            task: Description of the security task
            target: Optional target (URL, path, or GitHub repo)

        Returns:
            Dictionary with execution results
        """
        self.current_task = task
        self.state = AgentState.THINKING
        self.thoughts = []
        self.observations = []
        self.findings = []

        start_time = datetime.now()
        iteration = 0

        # Speak start if voice available
        if self.voice:
            self.voice.speak(
                f"Commencing security assessment, sir. Target: {target or 'as specified'}",
                "INFORMATION"
            )

        try:
            while iteration < self.max_iterations:
                iteration += 1
                self.logger.info(f"ReAct iteration {iteration}/{self.max_iterations}")

                # THINK: Analyze situation and decide next action
                thought = await self._think(task, target)
                self.thoughts.append(thought)

                if thought.next_action is None:
                    # Agent decided task is complete
                    self.state = AgentState.COMPLETE
                    break

                # ACT: Execute the decided action
                self.state = AgentState.ACTING
                observation = await self._act(thought)
                self.observations.append(observation)

                # OBSERVE: Analyze the result
                self.state = AgentState.OBSERVING
                should_continue = await self._observe(observation)

                if not should_continue:
                    self.state = AgentState.COMPLETE
                    break

                self.state = AgentState.THINKING

            # Generate final report
            report = self._generate_report(start_time)

            # Store in brain
            if self.brain:
                self._store_execution_in_brain(report)

            # Speak completion
            if self.voice:
                self._speak_summary(report)

            return report

        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error(f"Security agent error: {e}")
            return {
                "success": False,
                "error": str(e),
                "state": self.state.value,
                "iterations": iteration
            }

    async def _think(self, task: str, target: Optional[str]) -> AgentThought:
        """
        THINK phase: Analyze the situation and decide next action

        Uses the current state, previous observations, and task
        to determine the best next action.
        """
        # Build context from previous observations
        context = {
            "task": task,
            "target": target,
            "iteration": len(self.thoughts) + 1,
            "previous_actions": [t.next_action.value for t in self.thoughts if t.next_action],
            "findings_count": len(self.findings),
            "has_critical": any(f.severity == "critical" for f in self.findings)
        }

        # Determine next action based on state
        if len(self.thoughts) == 0:
            # First iteration: start scanning
            return self._plan_initial_scan(task, target)

        # Check if we have findings to analyze
        last_obs = self.observations[-1] if self.observations else None

        if last_obs and last_obs.success:
            if last_obs.action in [ActionType.SCAN_DIRECTORY, ActionType.SCAN_URL, ActionType.SCAN_GITHUB]:
                # Just completed a scan, analyze findings
                return AgentThought(
                    reasoning="Scan completed. I should analyze the findings using Fabric security patterns.",
                    next_action=ActionType.ANALYZE_FINDINGS,
                    action_params={"findings": self.findings},
                    confidence=0.9
                )

            elif last_obs.action == ActionType.ANALYZE_FINDINGS:
                # Analysis complete, check if we need to alert
                if any(f.severity in ["critical", "high"] for f in self.findings):
                    # Critical/high findings - create issues and alert
                    if self.github_token and not self._has_created_issues():
                        return AgentThought(
                            reasoning=f"Found {len(self.findings)} vulnerabilities including critical/high severity. Creating GitHub issues for tracking.",
                            next_action=ActionType.CREATE_GITHUB_ISSUE,
                            action_params={"findings": self.findings},
                            confidence=0.85
                        )
                    elif self.slack_webhook and not self._has_sent_alerts():
                        return AgentThought(
                            reasoning="Critical findings detected. Alerting team on Slack.",
                            next_action=ActionType.SEND_SLACK_ALERT,
                            action_params={"findings": self.findings},
                            confidence=0.85
                        )

                # Generate final report
                return AgentThought(
                    reasoning="Analysis complete. Generating final security report.",
                    next_action=ActionType.GENERATE_REPORT,
                    action_params={},
                    confidence=0.95
                )

            elif last_obs.action == ActionType.GENERATE_REPORT:
                # Report generated, task complete
                return AgentThought(
                    reasoning="Security assessment complete. All findings documented.",
                    next_action=None,
                    action_params={},
                    confidence=1.0
                )

        # Default: store findings and complete
        return AgentThought(
            reasoning="Completing security assessment.",
            next_action=ActionType.STORE_IN_MEMORY,
            action_params={},
            confidence=0.8
        )

    def _plan_initial_scan(self, task: str, target: Optional[str]) -> AgentThought:
        """Plan the initial scan based on target type"""
        if not target:
            # Try to extract target from task
            target = self._extract_target_from_task(task)

        if not target:
            return AgentThought(
                reasoning="No target specified. Cannot proceed with scan.",
                next_action=None,
                action_params={},
                confidence=0.0
            )

        # Determine scan type based on target
        if target.startswith("http://") or target.startswith("https://"):
            if "github.com" in target:
                return AgentThought(
                    reasoning=f"Target is a GitHub repository: {target}. Initiating repository security scan.",
                    next_action=ActionType.SCAN_GITHUB,
                    action_params={"target": target},
                    confidence=0.95
                )
            else:
                return AgentThought(
                    reasoning=f"Target is a URL: {target}. Initiating web application security scan.",
                    next_action=ActionType.SCAN_URL,
                    action_params={"target": target},
                    confidence=0.95
                )
        else:
            # Assume it's a directory/file path
            return AgentThought(
                reasoning=f"Target is a local path: {target}. Initiating code security scan.",
                next_action=ActionType.SCAN_DIRECTORY,
                action_params={"target": target},
                confidence=0.95
            )

    def _extract_target_from_task(self, task: str) -> Optional[str]:
        """Extract target from task description"""
        import re

        # Look for URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, task)
        if urls:
            return urls[0]

        # Look for file paths (Windows or Unix)
        path_patterns = [
            r'[A-Za-z]:\\[^\s]+',  # Windows
            r'/[^\s]+',  # Unix
            r'\./[^\s]+',  # Relative
        ]
        for pattern in path_patterns:
            paths = re.findall(pattern, task)
            if paths:
                return paths[0]

        return None

    async def _act(self, thought: AgentThought) -> AgentObservation:
        """
        ACT phase: Execute the planned action
        """
        action = thought.next_action
        params = thought.action_params

        try:
            if action == ActionType.SCAN_DIRECTORY:
                result = await self._scan_directory(params["target"])
            elif action == ActionType.SCAN_URL:
                result = await self._scan_url(params["target"])
            elif action == ActionType.SCAN_GITHUB:
                result = await self._scan_github(params["target"])
            elif action == ActionType.ANALYZE_FINDINGS:
                result = await self._analyze_findings()
            elif action == ActionType.CREATE_GITHUB_ISSUE:
                result = await self._create_github_issues()
            elif action == ActionType.SEND_SLACK_ALERT:
                result = await self._send_slack_alert()
            elif action == ActionType.STORE_IN_MEMORY:
                result = await self._store_in_memory()
            elif action == ActionType.GENERATE_REPORT:
                result = await self._generate_detailed_report()
            else:
                result = {"error": f"Unknown action: {action}"}

            success = result.get("success", True) if isinstance(result, dict) else True
            error = result.get("error") if isinstance(result, dict) else None

            return AgentObservation(
                action=action,
                result=result,
                success=success,
                error=error
            )

        except Exception as e:
            self.logger.error(f"Action {action} failed: {e}")
            return AgentObservation(
                action=action,
                result={},
                success=False,
                error=str(e)
            )

    async def _observe(self, observation: AgentObservation) -> bool:
        """
        OBSERVE phase: Analyze the result and decide if we should continue

        Returns:
            True if agent should continue, False if task is complete
        """
        if not observation.success:
            self.logger.warning(f"Action {observation.action} failed: {observation.error}")
            # Continue to try alternative approaches
            return True

        # Check if task seems complete
        if observation.action == ActionType.GENERATE_REPORT:
            return False  # Report generated, we're done

        if observation.action == ActionType.STORE_IN_MEMORY:
            return False  # Final storage, we're done

        return True  # Continue the loop

    # ==================== ACTION IMPLEMENTATIONS ====================

    async def _scan_directory(self, target: str) -> Dict[str, Any]:
        """Scan a local directory for vulnerabilities"""
        if not self.strix or not self.strix.strix_available:
            return self._fallback_code_scan(target)

        result = self.strix.scan(target)

        # Extract findings
        if result.get("success"):
            for vuln in result.get("vulnerabilities", []):
                finding = SecurityFinding(
                    id=f"STRIX-{len(self.findings)+1}",
                    title=vuln.get("title", "Unknown Vulnerability"),
                    severity=vuln.get("severity", "medium"),
                    description=vuln.get("description", ""),
                    proof_of_concept=vuln.get("proof_of_concept"),
                    recommendation=vuln.get("recommendation", "Review and remediate")
                )
                self.findings.append(finding)

        return result

    async def _scan_url(self, target: str) -> Dict[str, Any]:
        """Scan a URL for web vulnerabilities"""
        if not self.strix or not self.strix.strix_available:
            return {"success": False, "error": "Strix not available for URL scanning"}

        result = self.strix.scan(
            target,
            instructions="Perform OWASP Top 10 security assessment"
        )

        # Extract findings
        if result.get("success"):
            for vuln in result.get("vulnerabilities", []):
                finding = SecurityFinding(
                    id=f"WEB-{len(self.findings)+1}",
                    title=vuln.get("title", "Unknown Vulnerability"),
                    severity=vuln.get("severity", "medium"),
                    description=vuln.get("description", ""),
                    proof_of_concept=vuln.get("proof_of_concept"),
                    recommendation=vuln.get("recommendation", "Review and remediate"),
                    affected_component=target
                )
                self.findings.append(finding)

        return result

    async def _scan_github(self, target: str) -> Dict[str, Any]:
        """Scan a GitHub repository for vulnerabilities"""
        if not self.strix or not self.strix.strix_available:
            return {"success": False, "error": "Strix not available for GitHub scanning"}

        result = self.strix.scan(
            target,
            instructions="Analyze repository for security vulnerabilities, secrets exposure, and insecure coding patterns"
        )

        # Extract findings
        if result.get("success"):
            for vuln in result.get("vulnerabilities", []):
                finding = SecurityFinding(
                    id=f"GH-{len(self.findings)+1}",
                    title=vuln.get("title", "Unknown Vulnerability"),
                    severity=vuln.get("severity", "medium"),
                    description=vuln.get("description", ""),
                    proof_of_concept=vuln.get("proof_of_concept"),
                    recommendation=vuln.get("recommendation", "Review and remediate"),
                    affected_component=target
                )
                self.findings.append(finding)

        return result

    def _fallback_code_scan(self, target: str) -> Dict[str, Any]:
        """Fallback code scanning when Strix is not available"""
        import re
        from pathlib import Path

        findings = []

        # Patterns for common vulnerabilities
        vuln_patterns = {
            "SQL Injection": [
                r'execute\s*\(\s*["\'].*%s',
                r'cursor\.execute\s*\(\s*f["\']',
                r'\+\s*["\'].*SELECT.*FROM',
            ],
            "Command Injection": [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(\s*[^,\]]+\s*,\s*shell\s*=\s*True',
                r'eval\s*\(',
                r'exec\s*\(',
            ],
            "Hardcoded Secrets": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
            ],
            "XSS Vulnerability": [
                r'innerHTML\s*=',
                r'document\.write\s*\(',
                r'\.html\s*\([^)]*\+',
            ],
            "Path Traversal": [
                r'open\s*\([^)]*\+[^)]*\)',
                r'Path\s*\([^)]*\+',
            ],
        }

        target_path = Path(target)
        if not target_path.exists():
            return {"success": False, "error": f"Path not found: {target}"}

        files_scanned = 0

        # Scan files
        if target_path.is_file():
            files_to_scan = [target_path]
        else:
            files_to_scan = list(target_path.rglob("*.py")) + \
                           list(target_path.rglob("*.js")) + \
                           list(target_path.rglob("*.ts"))

        for file_path in files_to_scan[:100]:  # Limit to 100 files
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                files_scanned += 1

                for vuln_type, patterns in vuln_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            finding = SecurityFinding(
                                id=f"CODE-{len(self.findings)+len(findings)+1}",
                                title=f"Potential {vuln_type}",
                                severity="high" if "Injection" in vuln_type else "medium",
                                description=f"Found potential {vuln_type} at {file_path}:{line_num}",
                                proof_of_concept=match.group(0)[:100],
                                recommendation=f"Review and sanitize the code at line {line_num}",
                                affected_component=str(file_path)
                            )
                            findings.append(finding)
            except Exception as e:
                self.logger.debug(f"Error scanning {file_path}: {e}")

        self.findings.extend(findings)

        return {
            "success": True,
            "files_scanned": files_scanned,
            "vulnerabilities_found": len(findings),
            "note": "Fallback scan (Strix not available)"
        }

    async def _analyze_findings(self) -> Dict[str, Any]:
        """Analyze findings using Fabric security patterns"""
        if not self.fabric or not self.findings:
            return {"success": True, "message": "No findings to analyze"}

        # Prepare findings summary for analysis
        findings_text = "\n".join([
            f"- [{f.severity.upper()}] {f.title}: {f.description}"
            for f in self.findings
        ])

        try:
            # Apply security_audit pattern
            analysis = self.fabric.apply_pattern("security_audit", findings_text)

            # Store analysis
            if self.brain:
                self.brain.store_knowledge(
                    "security_analysis",
                    f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    analysis,
                    importance=8,
                    confidence=0.85
                )

            return {
                "success": True,
                "analysis": analysis,
                "findings_analyzed": len(self.findings)
            }
        except Exception as e:
            self.logger.error(f"Fabric analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def _create_github_issues(self) -> Dict[str, Any]:
        """Create GitHub issues for critical findings using GitHubIntegration"""
        if not self.github_token:
            return {"success": False, "error": "GitHub token not configured"}

        try:
            from integrations.github_integration import GitHubIntegration
            github = GitHubIntegration(token=self.github_token, brain=self.brain)
        except ImportError:
            return {"success": False, "error": "GitHub integration not available"}

        issues_created = []
        failed = []

        # Only create issues for high/critical findings
        critical_findings = [f for f in self.findings if f.severity in ["critical", "high"]]

        for finding in critical_findings[:5]:  # Limit to 5 issues
            try:
                # Convert SecurityFinding to dict for the integration
                finding_dict = {
                    "id": finding.id,
                    "title": finding.title,
                    "severity": finding.severity,
                    "description": finding.description,
                    "proof_of_concept": finding.proof_of_concept,
                    "recommendation": finding.recommendation,
                    "affected_component": finding.affected_component,
                    "cwe_id": finding.cwe_id,
                    "cvss_score": finding.cvss_score
                }

                result = await github.create_security_issue(finding_dict)

                if result.get("success"):
                    issues_created.append(result)
                    self.logger.info(f"Created GitHub issue #{result.get('number')}: {finding.title}")
                else:
                    failed.append({"finding": finding.title, "error": result.get("error")})

            except Exception as e:
                self.logger.error(f"Failed to create issue for {finding.id}: {e}")
                failed.append({"finding": finding.title, "error": str(e)})

        return {
            "success": True,
            "issues_created": len(issues_created),
            "issues": issues_created
        }

    async def _send_slack_alert(self) -> Dict[str, Any]:
        """Send Slack alert for critical findings using SlackIntegration"""
        if not self.slack_webhook:
            return {"success": False, "error": "Slack webhook not configured"}

        try:
            from integrations.slack_integration import SlackIntegration
            slack = SlackIntegration(webhook_url=self.slack_webhook, brain=self.brain)
        except ImportError:
            return {"success": False, "error": "Slack integration not available"}

        # Calculate severity counts
        severity_summary = {
            "critical": len([f for f in self.findings if f.severity == "critical"]),
            "high": len([f for f in self.findings if f.severity == "high"]),
            "medium": len([f for f in self.findings if f.severity == "medium"]),
            "low": len([f for f in self.findings if f.severity == "low"]),
            "info": len([f for f in self.findings if f.severity == "info"])
        }

        # Determine overall severity
        if severity_summary["critical"] > 0:
            overall_severity = "critical"
        elif severity_summary["high"] > 0:
            overall_severity = "high"
        elif severity_summary["medium"] > 0:
            overall_severity = "medium"
        else:
            overall_severity = "low"

        try:
            # Send the security alert
            result = await slack.send_security_alert(
                title=f"Security Scan: {self.current_task or 'Completed'}",
                severity=overall_severity,
                findings_count=len(self.findings),
                severity_summary=severity_summary,
                target=self.current_task
            )

            # If critical findings, also send individual alerts
            critical_findings = [f for f in self.findings if f.severity == "critical"]
            for finding in critical_findings[:3]:  # Limit to 3 critical alerts
                finding_dict = {
                    "id": finding.id,
                    "title": finding.title,
                    "description": finding.description,
                    "recommendation": finding.recommendation
                }
                await slack.send_critical_alert(finding_dict)

            await slack.close()

            return {
                "success": result.get("ok", False),
                "message_sent": True,
                "critical_count": severity_summary["critical"],
                "high_count": severity_summary["high"]
            }

        except Exception as e:
            self.logger.error(f"Slack alert failed: {e}")
            return {"success": False, "error": str(e)}

    async def _store_in_memory(self) -> Dict[str, Any]:
        """Store all findings in Alfred Brain"""
        if not self.brain:
            return {"success": False, "error": "Brain not available"}

        try:
            # Store each finding
            for finding in self.findings:
                self.brain.store_knowledge(
                    "security_findings",
                    finding.id,
                    json.dumps({
                        "title": finding.title,
                        "severity": finding.severity,
                        "description": finding.description,
                        "recommendation": finding.recommendation,
                        "discovered_at": finding.discovered_at.isoformat()
                    }),
                    importance=10 if finding.severity == "critical" else 8 if finding.severity == "high" else 5,
                    confidence=0.9
                )

            return {
                "success": True,
                "findings_stored": len(self.findings)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _generate_detailed_report(self) -> Dict[str, Any]:
        """Generate a detailed security report"""
        severity_counts = {
            "critical": len([f for f in self.findings if f.severity == "critical"]),
            "high": len([f for f in self.findings if f.severity == "high"]),
            "medium": len([f for f in self.findings if f.severity == "medium"]),
            "low": len([f for f in self.findings if f.severity == "low"]),
            "info": len([f for f in self.findings if f.severity == "info"])
        }

        report = {
            "success": True,
            "report_type": "security_assessment",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_findings": len(self.findings),
                "severity_breakdown": severity_counts,
                "iterations": len(self.thoughts),
                "actions_taken": len(self.observations)
            },
            "findings": [
                {
                    "id": f.id,
                    "title": f.title,
                    "severity": f.severity,
                    "description": f.description,
                    "recommendation": f.recommendation
                }
                for f in self.findings
            ],
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []

        critical_count = len([f for f in self.findings if f.severity == "critical"])
        high_count = len([f for f in self.findings if f.severity == "high"])

        if critical_count > 0:
            recommendations.append(f"URGENT: Address {critical_count} critical vulnerabilities immediately")

        if high_count > 0:
            recommendations.append(f"HIGH PRIORITY: Remediate {high_count} high-severity issues within 7 days")

        if any("injection" in f.title.lower() for f in self.findings):
            recommendations.append("Implement input validation and parameterized queries")

        if any("secret" in f.title.lower() or "password" in f.title.lower() for f in self.findings):
            recommendations.append("Move secrets to environment variables or a secrets manager")

        recommendations.append("Schedule follow-up scan after remediation")

        return recommendations

    def _generate_report(self, start_time: datetime) -> Dict[str, Any]:
        """Generate final execution report"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "success": self.state == AgentState.COMPLETE,
            "state": self.state.value,
            "task": self.current_task,
            "duration_seconds": duration,
            "iterations": len(self.thoughts),
            "actions_taken": len(self.observations),
            "findings_count": len(self.findings),
            "severity_summary": {
                "critical": len([f for f in self.findings if f.severity == "critical"]),
                "high": len([f for f in self.findings if f.severity == "high"]),
                "medium": len([f for f in self.findings if f.severity == "medium"]),
                "low": len([f for f in self.findings if f.severity == "low"]),
            },
            "findings": [
                {"id": f.id, "title": f.title, "severity": f.severity}
                for f in self.findings
            ],
            "thought_chain": [
                {"reasoning": t.reasoning, "action": t.next_action.value if t.next_action else "complete"}
                for t in self.thoughts
            ]
        }

    def _store_execution_in_brain(self, report: Dict[str, Any]):
        """Store execution details in brain for learning"""
        if not self.brain:
            return

        try:
            # Store the execution
            self.brain.store_conversation(
                user_input=f"Security scan: {self.current_task}",
                alfred_response=f"Completed scan with {report['findings_count']} findings",
                success=report['success']
            )

            # Store as a learned pattern
            self.brain.store_knowledge(
                "security_executions",
                f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                json.dumps(report),
                importance=8,
                confidence=0.9
            )
        except Exception as e:
            self.logger.error(f"Failed to store in brain: {e}")

    def _speak_summary(self, report: Dict[str, Any]):
        """Speak a summary of the results"""
        if not self.voice:
            return

        findings = report.get("findings_count", 0)
        critical = report.get("severity_summary", {}).get("critical", 0)
        high = report.get("severity_summary", {}).get("high", 0)

        if critical > 0:
            self.voice.speak(
                f"Most concerning, sir. I've discovered {critical} critical vulnerabilities that require immediate attention.",
                "WARNING"
            )
        elif high > 0:
            self.voice.speak(
                f"Sir, I must inform you of {high} high-severity vulnerabilities. I recommend addressing these promptly.",
                "WARNING"
            )
        elif findings > 0:
            self.voice.speak(
                f"Security assessment complete, sir. Found {findings} potential issues of moderate concern.",
                "INFORMATION"
            )
        else:
            self.voice.speak(
                "Excellent news, sir. No significant vulnerabilities detected. The target appears secure.",
                "CONFIRMATION"
            )

    def _has_created_issues(self) -> bool:
        """Check if GitHub issues have been created"""
        return any(
            obs.action == ActionType.CREATE_GITHUB_ISSUE and obs.success
            for obs in self.observations
        )

    def _has_sent_alerts(self) -> bool:
        """Check if Slack alerts have been sent"""
        return any(
            obs.action == ActionType.SEND_SLACK_ALERT and obs.success
            for obs in self.observations
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "state": self.state.value,
            "current_task": self.current_task,
            "iterations": len(self.thoughts),
            "findings": len(self.findings),
            "strix_available": self.strix.strix_available if self.strix else False,
            "brain_connected": self.brain is not None,
            "fabric_available": self.fabric is not None,
            "github_configured": bool(self.github_token),
            "slack_configured": bool(self.slack_webhook)
        }


# Convenience function for quick scans
async def quick_security_scan(target: str) -> Dict[str, Any]:
    """
    Run a quick security scan on a target

    Args:
        target: URL, path, or GitHub repo to scan

    Returns:
        Scan results dictionary
    """
    agent = AlfredSecurityAgent()
    return await agent.execute(f"Scan {target} for security vulnerabilities", target)


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python security_agent.py <target>")
        print("  target: URL, path, or GitHub repo to scan")
        sys.exit(1)

    target = sys.argv[1]
    print(f"Starting ALFRED Security Agent scan on: {target}")
    print("-" * 50)

    result = asyncio.run(quick_security_scan(target))

    print("\n" + "=" * 50)
    print("SCAN RESULTS")
    print("=" * 50)
    print(json.dumps(result, indent=2, default=str))
