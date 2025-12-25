"""
GitHub Integration for ALFRED

Provides GitHub API integration for:
- Creating issues for security findings
- Creating pull requests
- Repository management
- Workflow triggers
- Code scanning alerts

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class GitHubIssue:
    """Represents a GitHub issue"""
    number: int
    title: str
    body: str
    state: str
    url: str
    labels: List[str]
    created_at: str


@dataclass
class GitHubPR:
    """Represents a GitHub pull request"""
    number: int
    title: str
    body: str
    state: str
    url: str
    base_branch: str
    head_branch: str


class GitHubIntegration:
    """
    GitHub API Integration for ALFRED

    Supports:
    - Issue creation and management
    - Pull request operations
    - Repository information
    - Security alerts

    Authentication via:
    - GITHUB_TOKEN environment variable
    - Direct token parameter
    """

    API_BASE = "https://api.github.com"

    def __init__(
        self,
        token: Optional[str] = None,
        default_repo: Optional[str] = None,
        brain=None
    ):
        """
        Initialize GitHub integration

        Args:
            token: GitHub personal access token (or use GITHUB_TOKEN env var)
            default_repo: Default repository in format "owner/repo"
            brain: AlfredBrain instance for storing operations
        """
        self.logger = logging.getLogger(__name__)
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.default_repo = default_repo or os.getenv("GITHUB_DEFAULT_REPO")
        self.brain = brain

        if not self.token:
            self.logger.warning("No GitHub token configured. Set GITHUB_TOKEN environment variable.")

        self._session = None

    @property
    def is_configured(self) -> bool:
        """Check if GitHub integration is properly configured"""
        return bool(self.token)

    @property
    def headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def _get_session(self):
        """Get or create aiohttp session"""
        if not AIOHTTP_AVAILABLE:
            return None
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()

    def _sync_request(self, method: str, url: str, **kwargs) -> Dict:
        """Make synchronous request (fallback when aiohttp not available)"""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests library not available"}

        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GitHub API error: {e}")
            return {"error": str(e)}

    async def _async_request(self, method: str, url: str, **kwargs) -> Dict:
        """Make async request"""
        session = await self._get_session()
        if not session:
            return self._sync_request(method, url, **kwargs)

        try:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json() if response.content_length else {}
        except Exception as e:
            self.logger.error(f"GitHub API error: {e}")
            return {"error": str(e)}

    def _parse_repo(self, repo: Optional[str] = None) -> tuple:
        """Parse repository string into owner and repo"""
        repo = repo or self.default_repo
        if not repo:
            raise ValueError("No repository specified")

        if "/" not in repo:
            raise ValueError(f"Invalid repo format: {repo}. Expected 'owner/repo'")

        parts = repo.split("/")
        return parts[0], parts[1]

    # ==================== ISSUE OPERATIONS ====================

    async def create_issue(
        self,
        title: str,
        body: str,
        repo: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new GitHub issue

        Args:
            title: Issue title
            body: Issue body (markdown supported)
            repo: Repository in format "owner/repo" (uses default if not specified)
            labels: List of label names
            assignees: List of usernames to assign
            milestone: Milestone number

        Returns:
            Created issue data or error
        """
        if not self.is_configured:
            return {"error": "GitHub not configured", "success": False}

        owner, repo_name = self._parse_repo(repo)
        url = f"{self.API_BASE}/repos/{owner}/{repo_name}/issues"

        payload = {
            "title": title,
            "body": body
        }

        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees
        if milestone:
            payload["milestone"] = milestone

        result = await self._async_request("POST", url, json=payload)

        if "error" not in result:
            self.logger.info(f"Created issue #{result.get('number')}: {title}")

            # Store in brain
            if self.brain:
                self.brain.store_knowledge(
                    "github_issues",
                    f"issue_{result.get('number')}",
                    json.dumps({
                        "number": result.get("number"),
                        "title": title,
                        "url": result.get("html_url"),
                        "created_at": datetime.now().isoformat()
                    }),
                    importance=7,
                    confidence=1.0
                )

            return {
                "success": True,
                "number": result.get("number"),
                "url": result.get("html_url"),
                "title": title
            }

        return {"success": False, **result}

    async def create_security_issue(
        self,
        finding: Dict[str, Any],
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a security issue from a finding

        Args:
            finding: Security finding dictionary with title, severity, description, etc.
            repo: Target repository

        Returns:
            Created issue data
        """
        severity = finding.get("severity", "medium").upper()
        severity_emoji = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "INFO": "🔵"
        }.get(severity, "⚪")

        title = f"[Security] {severity_emoji} {finding.get('title', 'Security Finding')}"

        body = f"""## Security Finding

**Severity:** {severity}
**ID:** {finding.get('id', 'N/A')}
**Discovered:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Description

{finding.get('description', 'No description provided')}

### Proof of Concept

```
{finding.get('proof_of_concept', 'N/A')}
```

### Affected Component

{finding.get('affected_component', 'Not specified')}

### Recommendation

{finding.get('recommendation', 'Review and remediate the vulnerability')}

### References

- CWE: {finding.get('cwe_id', 'N/A')}
- CVSS Score: {finding.get('cvss_score', 'N/A')}

---

*This issue was automatically created by ALFRED Security Agent*
*Part of the ALFRED-UBX AI Assistant System*
"""

        labels = ["security", finding.get("severity", "medium").lower()]

        if severity in ["CRITICAL", "HIGH"]:
            labels.append("priority-high")

        return await self.create_issue(
            title=title,
            body=body,
            repo=repo,
            labels=labels
        )

    async def create_security_issues_batch(
        self,
        findings: List[Dict[str, Any]],
        repo: Optional[str] = None,
        max_issues: int = 10
    ) -> Dict[str, Any]:
        """
        Create multiple security issues from findings

        Args:
            findings: List of security findings
            repo: Target repository
            max_issues: Maximum number of issues to create

        Returns:
            Summary of created issues
        """
        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.get(f.get("severity", "info").lower(), 5)
        )

        created = []
        failed = []

        for finding in sorted_findings[:max_issues]:
            try:
                result = await self.create_security_issue(finding, repo)
                if result.get("success"):
                    created.append(result)
                else:
                    failed.append({"finding": finding.get("title"), "error": result.get("error")})

                # Rate limiting - wait between requests
                await asyncio.sleep(1)

            except Exception as e:
                failed.append({"finding": finding.get("title"), "error": str(e)})

        return {
            "success": len(created) > 0,
            "created_count": len(created),
            "failed_count": len(failed),
            "created_issues": created,
            "failed": failed
        }

    async def get_issue(
        self,
        issue_number: int,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get issue details"""
        if not self.is_configured:
            return {"error": "GitHub not configured"}

        owner, repo_name = self._parse_repo(repo)
        url = f"{self.API_BASE}/repos/{owner}/{repo_name}/issues/{issue_number}"

        return await self._async_request("GET", url)

    async def list_issues(
        self,
        repo: Optional[str] = None,
        state: str = "open",
        labels: Optional[List[str]] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """List repository issues"""
        if not self.is_configured:
            return []

        owner, repo_name = self._parse_repo(repo)
        url = f"{self.API_BASE}/repos/{owner}/{repo_name}/issues"

        params = {
            "state": state,
            "per_page": limit
        }

        if labels:
            params["labels"] = ",".join(labels)

        result = await self._async_request("GET", url, params=params)

        if isinstance(result, list):
            return result
        return []

    async def close_issue(
        self,
        issue_number: int,
        repo: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue"""
        if not self.is_configured:
            return {"error": "GitHub not configured"}

        owner, repo_name = self._parse_repo(repo)

        # Add comment if provided
        if comment:
            comment_url = f"{self.API_BASE}/repos/{owner}/{repo_name}/issues/{issue_number}/comments"
            await self._async_request("POST", comment_url, json={"body": comment})

        # Close issue
        url = f"{self.API_BASE}/repos/{owner}/{repo_name}/issues/{issue_number}"
        result = await self._async_request("PATCH", url, json={"state": "closed"})

        return {"success": "error" not in result, **result}

    # ==================== PULL REQUEST OPERATIONS ====================

    async def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        repo: Optional[str] = None,
        draft: bool = False
    ) -> Dict[str, Any]:
        """
        Create a pull request

        Args:
            title: PR title
            body: PR description
            head: Branch with changes
            base: Target branch (default: main)
            repo: Repository
            draft: Create as draft PR

        Returns:
            Created PR data
        """
        if not self.is_configured:
            return {"error": "GitHub not configured"}

        owner, repo_name = self._parse_repo(repo)
        url = f"{self.API_BASE}/repos/{owner}/{repo_name}/pulls"

        payload = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
            "draft": draft
        }

        result = await self._async_request("POST", url, json=payload)

        if "error" not in result:
            return {
                "success": True,
                "number": result.get("number"),
                "url": result.get("html_url"),
                "title": title
            }

        return {"success": False, **result}

    # ==================== REPOSITORY OPERATIONS ====================

    async def get_repo_info(self, repo: Optional[str] = None) -> Dict[str, Any]:
        """Get repository information"""
        if not self.is_configured:
            return {"error": "GitHub not configured"}

        owner, repo_name = self._parse_repo(repo)
        url = f"{self.API_BASE}/repos/{owner}/{repo_name}"

        return await self._async_request("GET", url)

    async def list_branches(self, repo: Optional[str] = None) -> List[Dict[str, Any]]:
        """List repository branches"""
        if not self.is_configured:
            return []

        owner, repo_name = self._parse_repo(repo)
        url = f"{self.API_BASE}/repos/{owner}/{repo_name}/branches"

        result = await self._async_request("GET", url)
        return result if isinstance(result, list) else []

    async def get_security_alerts(self, repo: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get Dependabot security alerts"""
        if not self.is_configured:
            return []

        owner, repo_name = self._parse_repo(repo)
        url = f"{self.API_BASE}/repos/{owner}/{repo_name}/dependabot/alerts"

        result = await self._async_request("GET", url)
        return result if isinstance(result, list) else []

    # ==================== CONVENIENCE METHODS ====================

    async def quick_security_report(
        self,
        findings: List[Dict[str, Any]],
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a single summary issue for multiple findings

        Args:
            findings: List of security findings
            repo: Target repository

        Returns:
            Created issue data
        """
        if not findings:
            return {"success": False, "error": "No findings to report"}

        # Count by severity
        severity_counts = {}
        for f in findings:
            sev = f.get("severity", "medium").lower()
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        title = f"[Security Report] {len(findings)} vulnerabilities found"

        findings_list = "\n".join([
            f"- **[{f.get('severity', 'medium').upper()}]** {f.get('title', 'Unknown')}"
            for f in findings[:20]  # Limit to first 20
        ])

        body = f"""## Security Scan Report

**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Findings:** {len(findings)}

### Severity Summary

| Severity | Count |
|----------|-------|
| Critical | {severity_counts.get('critical', 0)} |
| High | {severity_counts.get('high', 0)} |
| Medium | {severity_counts.get('medium', 0)} |
| Low | {severity_counts.get('low', 0)} |
| Info | {severity_counts.get('info', 0)} |

### Findings

{findings_list}

{'... and more' if len(findings) > 20 else ''}

### Next Steps

1. Review critical and high severity findings immediately
2. Create individual issues for items requiring tracking
3. Schedule remediation based on severity
4. Re-scan after fixes are applied

---

*Generated by ALFRED Security Agent*
"""

        labels = ["security", "security-report"]
        if severity_counts.get("critical", 0) > 0:
            labels.append("priority-critical")
        elif severity_counts.get("high", 0) > 0:
            labels.append("priority-high")

        return await self.create_issue(
            title=title,
            body=body,
            repo=repo,
            labels=labels
        )

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "configured": self.is_configured,
            "default_repo": self.default_repo,
            "token_set": bool(self.token),
            "aiohttp_available": AIOHTTP_AVAILABLE,
            "requests_available": REQUESTS_AVAILABLE
        }


# Convenience function for quick issue creation
async def create_security_issue(
    finding: Dict[str, Any],
    repo: str,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to create a security issue

    Args:
        finding: Security finding dictionary
        repo: Repository in format "owner/repo"
        token: GitHub token (or use GITHUB_TOKEN env var)

    Returns:
        Created issue data
    """
    gh = GitHubIntegration(token=token, default_repo=repo)
    try:
        return await gh.create_security_issue(finding)
    finally:
        await gh.close()


if __name__ == "__main__":
    # Test the integration
    import asyncio

    async def test():
        gh = GitHubIntegration()
        status = gh.get_status()
        print(f"GitHub Integration Status: {json.dumps(status, indent=2)}")

        if status["configured"]:
            print("\nGitHub is configured and ready!")
        else:
            print("\nSet GITHUB_TOKEN environment variable to enable GitHub integration")

    asyncio.run(test())
