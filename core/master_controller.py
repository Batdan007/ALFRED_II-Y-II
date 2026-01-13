"""
ALFRED-PRIME Master Controller
Provides elite control capabilities over all ALFRED_SYSTEMS instances.

HIERARCHY:
- ALFRED-PRIME (II-Y-II): Top tier - BATDAN only - Full control & audit
- ALFRED_UBX: Second tier - President of ALFRED_SYSTEMS - Ecosystem control
- ALFRED_ULTIMATE: Third tier - Internal company use with clearance

Author: Daniel J Rita (BATDAN)
License: Proprietary - ALFRED-PRIME Exclusive
"""

import os
import json
import logging
import hashlib
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class ALFREDTier(Enum):
    """ALFRED instance tier levels."""
    PRIME = 1      # Top tier - BATDAN only - Unrestricted
    UBX = 2        # Second tier - President of ALFRED_SYSTEMS
    ULTIMATE = 3   # Third tier - Internal company use
    STANDARD = 4   # Public/SaaS tier


@dataclass
class ALFREDInstance:
    """Represents a registered ALFRED instance."""
    name: str
    tier: ALFREDTier
    path: str
    api_endpoint: Optional[str] = None
    status: str = "unknown"
    last_seen: Optional[str] = None
    capabilities: List[str] = None
    owner: str = "BATDAN"
    clearance_required: bool = False

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class MasterController:
    """
    Master Controller for ALFRED-PRIME.

    Provides:
    - Registration and discovery of ALFRED instances
    - Remote control and command execution
    - Audit logging of all ALFRED_SYSTEMS activity
    - Security scanning and validation
    - Clearance management for ULTIMATE tier
    """

    def __init__(self, brain=None):
        """
        Initialize Master Controller.

        Args:
            brain: AlfredBrain instance for persistent storage
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.instances: Dict[str, ALFREDInstance] = {}
        self.audit_log: List[Dict[str, Any]] = []

        # BATDAN authentication (simple for now, can be enhanced)
        self.master_key = os.getenv("ALFRED_PRIME_KEY", self._generate_master_key())

        # Default ALFRED_SYSTEMS paths
        self.default_paths = {
            "ALFRED_UBX": "C:\\Users\\danie\\Projects\\ALFRED_SYSTEMS\\ALFRED_UBX",
            "ALFRED_ULTIMATE": "C:\\Users\\danie\\Projects\\ALFRED_SYSTEMS\\Alfred_Ultimate",
            "ALFRED_PRIME": "C:\\Users\\danie\\Projects\\ALFRED_II-Y-II"
        }

        # Register known instances
        self._register_default_instances()
        self.logger.info("ALFRED-PRIME Master Controller initialized")

    def _generate_master_key(self) -> str:
        """Generate a master key based on BATDAN's identity."""
        identity = "Daniel J Rita BATDAN ALFRED-PRIME"
        return hashlib.sha256(identity.encode()).hexdigest()[:32]

    def _register_default_instances(self):
        """Register known ALFRED instances."""
        # ALFRED-PRIME (self)
        self.register_instance(ALFREDInstance(
            name="ALFRED-PRIME",
            tier=ALFREDTier.PRIME,
            path=self.default_paths.get("ALFRED_PRIME", ""),
            status="active",
            last_seen=datetime.now().isoformat(),
            capabilities=[
                "master_control", "full_audit", "unrestricted_mode",
                "security_tools", "bug_bounty", "penetration_testing",
                "image_generation", "voice", "vision", "all_ai_providers"
            ],
            owner="BATDAN"
        ))

        # ALFRED_UBX
        self.register_instance(ALFREDInstance(
            name="ALFRED_UBX",
            tier=ALFREDTier.UBX,
            path=self.default_paths.get("ALFRED_UBX", ""),
            status="registered",
            capabilities=[
                "ecosystem_control", "policy_enforcement", "mcp_servers",
                "privacy_controller", "ai_orchestration"
            ],
            owner="ALFRED_SYSTEMS"
        ))

        # ALFRED_ULTIMATE
        self.register_instance(ALFREDInstance(
            name="ALFRED_ULTIMATE",
            tier=ALFREDTier.ULTIMATE,
            path=self.default_paths.get("ALFRED_ULTIMATE", ""),
            status="registered",
            capabilities=[
                "fabric_patterns", "multi_model", "research"
            ],
            owner="CAMDAN_ENTERPRISES",
            clearance_required=True
        ))

    def register_instance(self, instance: ALFREDInstance) -> bool:
        """
        Register an ALFRED instance.

        Args:
            instance: ALFREDInstance to register

        Returns:
            True if registered successfully
        """
        self.instances[instance.name] = instance
        self._audit("register", f"Registered instance: {instance.name}", instance.name)

        if self.brain:
            self.brain.store_knowledge(
                category="alfred_instances",
                key=instance.name,
                value=asdict(instance),
                importance=8,
                confidence=1.0
            )

        return True

    def get_instance_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status of a registered instance."""
        if name not in self.instances:
            return None

        instance = self.instances[name]

        # Check if path exists
        path_exists = Path(instance.path).exists() if instance.path else False

        # Try to ping API if available
        api_status = "unknown"
        if instance.api_endpoint:
            try:
                response = requests.get(instance.api_endpoint, timeout=5)
                api_status = "online" if response.status_code == 200 else "offline"
            except Exception:
                api_status = "unreachable"

        return {
            "name": instance.name,
            "tier": instance.tier.name,
            "tier_level": instance.tier.value,
            "path_exists": path_exists,
            "api_status": api_status,
            "capabilities": instance.capabilities,
            "clearance_required": instance.clearance_required,
            "last_seen": instance.last_seen
        }

    def list_all_instances(self) -> List[Dict[str, Any]]:
        """List all registered ALFRED instances."""
        return [self.get_instance_status(name) for name in self.instances]

    def scan_instance(self, name: str) -> Dict[str, Any]:
        """
        Perform security scan on an ALFRED instance.
        Only PRIME tier can scan all instances.

        Args:
            name: Instance name to scan

        Returns:
            Scan results
        """
        if name not in self.instances:
            return {"error": f"Instance {name} not found"}

        instance = self.instances[name]
        self._audit("scan", f"Security scan initiated for: {name}", name)

        results = {
            "instance": name,
            "tier": instance.tier.name,
            "scan_time": datetime.now().isoformat(),
            "checks": []
        }

        # Check path exists
        path = Path(instance.path)
        if path.exists():
            results["checks"].append({
                "check": "path_exists",
                "status": "pass",
                "details": str(path)
            })

            # Check for sensitive files
            sensitive_patterns = [".env", "credentials", "secrets", "api_key"]
            for pattern in sensitive_patterns:
                found = list(path.glob(f"**/*{pattern}*"))
                if found:
                    results["checks"].append({
                        "check": f"sensitive_files_{pattern}",
                        "status": "warning",
                        "details": f"Found {len(found)} files matching '{pattern}'"
                    })

            # Check requirements
            req_file = path / "requirements.txt"
            if req_file.exists():
                results["checks"].append({
                    "check": "requirements_exists",
                    "status": "pass",
                    "details": "requirements.txt found"
                })
        else:
            results["checks"].append({
                "check": "path_exists",
                "status": "fail",
                "details": f"Path not found: {instance.path}"
            })

        return results

    def send_command(self, target: str, command: str, params: Dict = None) -> Dict[str, Any]:
        """
        Send command to an ALFRED instance.

        Args:
            target: Target instance name
            command: Command to execute
            params: Command parameters

        Returns:
            Command result
        """
        if target not in self.instances:
            return {"error": f"Instance {target} not found"}

        instance = self.instances[target]
        self._audit("command", f"Command '{command}' sent to {target}", target)

        # For now, log the command - actual execution requires API integration
        result = {
            "target": target,
            "command": command,
            "params": params or {},
            "timestamp": datetime.now().isoformat(),
            "status": "queued",
            "message": f"Command queued for {target}. API integration required for remote execution."
        }

        if self.brain:
            self.brain.store_knowledge(
                category="master_commands",
                key=f"{target}_{command}_{datetime.now().timestamp()}",
                value=result,
                importance=6
            )

        return result

    def validate_clearance(self, user_id: str, target_tier: ALFREDTier) -> bool:
        """
        Validate user clearance for accessing an ALFRED tier.

        Args:
            user_id: User identifier
            target_tier: Tier attempting to access

        Returns:
            True if authorized
        """
        # BATDAN has full clearance
        if user_id.upper() in ["BATDAN", "DANIEL J RITA", "DANIEL RITA"]:
            return True

        # PRIME tier is BATDAN only
        if target_tier == ALFREDTier.PRIME:
            self._audit("access_denied", f"PRIME access denied for {user_id}", "PRIME")
            return False

        # UBX tier requires system authorization
        if target_tier == ALFREDTier.UBX:
            # Check if user is in approved list (would be stored in brain)
            if self.brain:
                approval = self.brain.get_knowledge("clearance", f"ubx_{user_id}")
                return bool(approval)
            return False

        # ULTIMATE tier requires company clearance
        if target_tier == ALFREDTier.ULTIMATE:
            if self.brain:
                approval = self.brain.get_knowledge("clearance", f"ultimate_{user_id}")
                return bool(approval)
            return False

        return True

    def grant_clearance(self, user_id: str, tier: ALFREDTier, granted_by: str = "BATDAN") -> bool:
        """
        Grant clearance to a user for a specific tier.

        Args:
            user_id: User to grant clearance
            tier: Tier to grant access to
            granted_by: Who is granting (must be higher tier)

        Returns:
            True if granted
        """
        # Only BATDAN can grant clearances
        if granted_by.upper() not in ["BATDAN", "DANIEL J RITA"]:
            self._audit("clearance_denied", f"Unauthorized clearance grant attempt by {granted_by}", tier.name)
            return False

        if self.brain:
            self.brain.store_knowledge(
                category="clearance",
                key=f"{tier.name.lower()}_{user_id}",
                value={
                    "user_id": user_id,
                    "tier": tier.name,
                    "granted_by": granted_by,
                    "granted_at": datetime.now().isoformat()
                },
                importance=9
            )
            self._audit("clearance_granted", f"Clearance granted to {user_id} for {tier.name}", tier.name)
            return True

        return False

    def _audit(self, action: str, details: str, target: str = None):
        """Log an audit entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "target": target,
            "controller": "ALFRED-PRIME"
        }
        self.audit_log.append(entry)
        self.logger.info(f"[AUDIT] {action}: {details}")

        if self.brain:
            self.brain.store_knowledge(
                category="audit_log",
                key=f"audit_{datetime.now().timestamp()}",
                value=entry,
                importance=5
            )

    def get_audit_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:]

    def get_hierarchy_summary(self) -> str:
        """Get a formatted summary of the ALFRED hierarchy."""
        return """
╔═══════════════════════════════════════════════════════════════════╗
║                    ALFRED SYSTEMS HIERARCHY                        ║
╠═══════════════════════════════════════════════════════════════════╣
║  TIER 1: ★ ALFRED-PRIME (II-Y-II) ★                               ║
║          Master Controller | BATDAN Only | Unrestricted            ║
║          - Full audit & control of all instances                   ║
║          - Security tools, bug bounty, penetration testing         ║
║          - Can modify ALFRED_UBX code/policies                     ║
╠───────────────────────────────────────────────────────────────────╣
║  TIER 2: ALFRED_UBX                                                ║
║          President of ALFRED_SYSTEMS | Ecosystem Control           ║
║          - Policy enforcement across all lower tiers               ║
║          - MCP servers, privacy controller                         ║
║          - Cannot be modified except by PRIME                      ║
╠───────────────────────────────────────────────────────────────────╣
║  TIER 3: ALFRED_ULTIMATE                                           ║
║          Internal Company Model | Clearance Required               ║
║          - CAMDAN, MECA, GxEum officials only                      ║
║          - Fabric patterns, multi-model support                    ║
║          - Requires explicit clearance from BATDAN                 ║
╠───────────────────────────────────────────────────────────────────╣
║  TIER 4: STANDARD (Future SaaS)                                    ║
║          Public tier | Restricted capabilities                     ║
║          - Follows Joe Dog's Rule strictly                         ║
║          - Privacy-first, local-first operation                    ║
╚═══════════════════════════════════════════════════════════════════╝
"""
