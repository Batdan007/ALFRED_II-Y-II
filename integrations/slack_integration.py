"""
Slack Integration for ALFRED

Provides Slack API integration for:
- Sending security alerts
- Team notifications
- Channel messaging
- Rich message formatting with blocks

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

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


class SlackIntegration:
    """
    Slack Integration for ALFRED

    Supports:
    - Webhook-based messaging (simplest setup)
    - Bot token messaging (more features)
    - Rich message formatting with Block Kit
    - Security alert templates

    Authentication via:
    - SLACK_WEBHOOK_URL environment variable (webhook mode)
    - SLACK_BOT_TOKEN environment variable (bot mode)
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        bot_token: Optional[str] = None,
        default_channel: Optional[str] = None,
        brain=None
    ):
        """
        Initialize Slack integration

        Args:
            webhook_url: Slack incoming webhook URL
            bot_token: Slack bot token (for API mode)
            default_channel: Default channel for messages
            brain: AlfredBrain instance for storing operations
        """
        self.logger = logging.getLogger(__name__)
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.default_channel = default_channel or os.getenv("SLACK_DEFAULT_CHANNEL", "#security-alerts")
        self.brain = brain

        self._session = None

        if not self.webhook_url and not self.bot_token:
            self.logger.warning("No Slack configuration found. Set SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN")

    @property
    def is_configured(self) -> bool:
        """Check if Slack integration is properly configured"""
        return bool(self.webhook_url or self.bot_token)

    @property
    def mode(self) -> str:
        """Get integration mode"""
        if self.bot_token:
            return "bot"
        elif self.webhook_url:
            return "webhook"
        return "none"

    async def _get_session(self):
        """Get or create aiohttp session"""
        if not AIOHTTP_AVAILABLE:
            return None
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()

    def _sync_post(self, url: str, payload: Dict) -> Dict:
        """Make synchronous POST request"""
        if not REQUESTS_AVAILABLE:
            return {"ok": False, "error": "requests library not available"}

        try:
            headers = {"Content-Type": "application/json"}
            if self.bot_token:
                headers["Authorization"] = f"Bearer {self.bot_token}"

            response = requests.post(url, json=payload, headers=headers)

            # Webhook returns "ok" as text, API returns JSON
            if response.text == "ok":
                return {"ok": True}

            return response.json()
        except Exception as e:
            self.logger.error(f"Slack API error: {e}")
            return {"ok": False, "error": str(e)}

    async def _async_post(self, url: str, payload: Dict) -> Dict:
        """Make async POST request"""
        session = await self._get_session()
        if not session:
            return self._sync_post(url, payload)

        try:
            headers = {"Content-Type": "application/json"}
            if self.bot_token:
                headers["Authorization"] = f"Bearer {self.bot_token}"

            async with session.post(url, json=payload, headers=headers) as response:
                text = await response.text()

                # Webhook returns "ok" as text
                if text == "ok":
                    return {"ok": True}

                return json.loads(text)
        except Exception as e:
            self.logger.error(f"Slack API error: {e}")
            return {"ok": False, "error": str(e)}

    # ==================== MESSAGING ====================

    async def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        blocks: Optional[List[Dict]] = None,
        attachments: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to Slack

        Args:
            text: Message text (required for notifications)
            channel: Channel to post to (ignored in webhook mode)
            blocks: Block Kit blocks for rich formatting
            attachments: Legacy attachments
            thread_ts: Thread timestamp for replies

        Returns:
            Response from Slack
        """
        if not self.is_configured:
            return {"ok": False, "error": "Slack not configured"}

        payload = {"text": text}

        if blocks:
            payload["blocks"] = blocks
        if attachments:
            payload["attachments"] = attachments

        if self.mode == "webhook":
            # Webhook mode - simple POST
            result = await self._async_post(self.webhook_url, payload)
        else:
            # Bot mode - use chat.postMessage API
            url = "https://slack.com/api/chat.postMessage"
            payload["channel"] = channel or self.default_channel
            if thread_ts:
                payload["thread_ts"] = thread_ts
            result = await self._async_post(url, payload)

        # Store in brain
        if result.get("ok") and self.brain:
            self.brain.store_knowledge(
                "slack_messages",
                f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                json.dumps({
                    "text": text[:100],
                    "channel": channel or self.default_channel,
                    "sent_at": datetime.now().isoformat()
                }),
                importance=3,
                confidence=1.0
            )

        return result

    # ==================== SECURITY ALERTS ====================

    async def send_security_alert(
        self,
        title: str,
        severity: str,
        findings_count: int,
        severity_summary: Dict[str, int],
        target: Optional[str] = None,
        details: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a formatted security alert

        Args:
            title: Alert title
            severity: Overall severity (critical, high, medium, low)
            findings_count: Number of findings
            severity_summary: Dict with counts per severity
            target: Scan target
            details: Additional details
            channel: Target channel

        Returns:
            Response from Slack
        """
        # Severity colors
        colors = {
            "critical": "#FF0000",
            "high": "#FF6600",
            "medium": "#FFCC00",
            "low": "#00CC00",
            "info": "#0066FF"
        }

        # Severity emojis
        emojis = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "🔵"
        }

        color = colors.get(severity.lower(), "#808080")
        emoji = emojis.get(severity.lower(), "⚪")

        # Build severity breakdown
        breakdown_parts = []
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = severity_summary.get(sev, 0)
            if count > 0:
                breakdown_parts.append(f"{emojis[sev]} {sev.capitalize()}: {count}")

        breakdown_text = " | ".join(breakdown_parts) if breakdown_parts else "No findings"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Security Alert: {title}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Findings:*\n{findings_count}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Breakdown:*\n{breakdown_text}"
                }
            }
        ]

        if target:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Target:*\n`{target}`"
                }
            })

        if details:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{details[:500]}"
                }
            })

        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"_Sent by ALFRED Security Agent at {datetime.now().strftime('%Y-%m-%d %H:%M')}_"
                }
            ]
        })

        # Also send as attachment for email notifications
        attachments = [{
            "color": color,
            "title": title,
            "text": f"Found {findings_count} security issues. Severity: {severity.upper()}",
            "footer": "ALFRED Security Agent",
            "ts": int(datetime.now().timestamp())
        }]

        text = f"🚨 Security Alert: {findings_count} findings ({severity.upper()}) - {title}"

        return await self.send_message(
            text=text,
            channel=channel,
            blocks=blocks,
            attachments=attachments
        )

    async def send_security_findings(
        self,
        findings: List[Dict[str, Any]],
        target: Optional[str] = None,
        channel: Optional[str] = None,
        max_findings: int = 5
    ) -> Dict[str, Any]:
        """
        Send detailed security findings

        Args:
            findings: List of security findings
            target: Scan target
            channel: Target channel
            max_findings: Maximum findings to include in message

        Returns:
            Response from Slack
        """
        if not findings:
            return await self.send_message(
                text="✅ Security scan complete - no findings",
                channel=channel
            )

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.get(f.get("severity", "info").lower(), 5)
        )

        # Build blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔍 Security Scan Results ({len(findings)} findings)",
                    "emoji": True
                }
            }
        ]

        if target:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Target:* `{target}`"
                }
            })

        blocks.append({"type": "divider"})

        # Add findings
        emojis = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "🔵"
        }

        for finding in sorted_findings[:max_findings]:
            severity = finding.get("severity", "medium").lower()
            emoji = emojis.get(severity, "⚪")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{finding.get('title', 'Unknown')}*\n{finding.get('description', '')[:200]}"
                }
            })

        if len(findings) > max_findings:
            blocks.append({
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"_...and {len(findings) - max_findings} more findings_"
                }]
            })

        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"_ALFRED Security Agent | {datetime.now().strftime('%Y-%m-%d %H:%M')}_"
            }]
        })

        return await self.send_message(
            text=f"Security scan found {len(findings)} issues",
            channel=channel,
            blocks=blocks
        )

    async def send_critical_alert(
        self,
        finding: Dict[str, Any],
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an urgent alert for a critical finding

        Args:
            finding: Critical security finding
            channel: Target channel

        Returns:
            Response from Slack
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 CRITICAL SECURITY VULNERABILITY",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{finding.get('title', 'Critical Vulnerability Detected')}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": finding.get("description", "A critical vulnerability has been detected that requires immediate attention.")[:500]
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n🔴 CRITICAL"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*ID:*\n{finding.get('id', 'N/A')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommendation:*\n{finding.get('recommendation', 'Immediate review and remediation required')}"
                }
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": "⚠️ *This requires immediate attention* | ALFRED Security Agent"
                }]
            }
        ]

        return await self.send_message(
            text="🚨 CRITICAL SECURITY VULNERABILITY DETECTED - Immediate action required!",
            channel=channel,
            blocks=blocks
        )

    # ==================== UTILITY METHODS ====================

    async def send_scan_started(
        self,
        target: str,
        scan_type: str = "security",
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notify that a scan has started"""
        return await self.send_message(
            text=f"🔍 Starting {scan_type} scan on `{target}`",
            channel=channel,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔍 *Security Scan Started*\n\n*Target:* `{target}`\n*Type:* {scan_type}\n*Started:* {datetime.now().strftime('%H:%M:%S')}"
                    }
                }
            ]
        )

    async def send_scan_complete(
        self,
        target: str,
        duration_seconds: float,
        findings_count: int,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notify that a scan has completed"""
        emoji = "✅" if findings_count == 0 else "⚠️"
        status = "No issues found" if findings_count == 0 else f"{findings_count} issues found"

        return await self.send_message(
            text=f"{emoji} Scan complete: {status}",
            channel=channel,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{emoji} *Security Scan Complete*\n\n*Target:* `{target}`\n*Duration:* {duration_seconds:.1f}s\n*Result:* {status}"
                    }
                }
            ]
        )

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "configured": self.is_configured,
            "mode": self.mode,
            "default_channel": self.default_channel,
            "webhook_set": bool(self.webhook_url),
            "bot_token_set": bool(self.bot_token),
            "aiohttp_available": AIOHTTP_AVAILABLE,
            "requests_available": REQUESTS_AVAILABLE
        }


# Convenience function for quick alerts
async def send_security_alert(
    title: str,
    severity: str,
    findings_count: int,
    webhook_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to send a security alert

    Args:
        title: Alert title
        severity: Severity level
        findings_count: Number of findings
        webhook_url: Slack webhook URL (or use SLACK_WEBHOOK_URL env var)

    Returns:
        Response from Slack
    """
    slack = SlackIntegration(webhook_url=webhook_url)
    try:
        return await slack.send_security_alert(
            title=title,
            severity=severity,
            findings_count=findings_count,
            severity_summary={}
        )
    finally:
        await slack.close()


if __name__ == "__main__":
    import asyncio

    async def test():
        slack = SlackIntegration()
        status = slack.get_status()
        print(f"Slack Integration Status: {json.dumps(status, indent=2)}")

        if status["configured"]:
            print("\nSlack is configured and ready!")
            print(f"Mode: {status['mode']}")
        else:
            print("\nSet SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN to enable Slack integration")
            print("\nTo create a webhook:")
            print("1. Go to https://api.slack.com/apps")
            print("2. Create a new app or select existing")
            print("3. Go to Incoming Webhooks")
            print("4. Activate and create a new webhook")
            print("5. Set SLACK_WEBHOOK_URL environment variable")

    asyncio.run(test())
