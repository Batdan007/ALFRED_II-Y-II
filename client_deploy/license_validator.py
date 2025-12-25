"""
ALFRED II-Y-II License Validator
Validates license on client machines

This file is included in client deployments.

Author: Daniel J. Rita (BATDAN)
"""

import hashlib
import json
import base64
import platform
import uuid
import sys
from pathlib import Path
from datetime import datetime


class LicenseValidator:
    """Validate ALFRED license on client machine"""

    def __init__(self, license_file: str = "license.key"):
        self.license_file = Path(license_file)
        self.license_data = None
        self.machine_id = self._get_machine_id()

    def _get_machine_id(self) -> str:
        """Generate unique machine identifier"""
        # Combine multiple hardware identifiers
        components = [
            platform.node(),  # Computer name
            platform.machine(),  # Machine type
            str(uuid.getnode()),  # MAC address
        ]
        combined = ":".join(components)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def load_license(self) -> bool:
        """Load and decode license file"""
        if not self.license_file.exists():
            print("ERROR: License file not found")
            print("Please contact BATDAN for a valid license.")
            return False

        try:
            encoded = self.license_file.read_text()
            decoded = base64.b64decode(encoded).decode()
            self.license_data = json.loads(decoded)
            return True
        except Exception as e:
            print(f"ERROR: Invalid license file: {e}")
            return False

    def validate(self) -> dict:
        """
        Validate the license

        Returns:
            dict with 'valid', 'tier', 'features', 'message'
        """
        if not self.load_license():
            return {"valid": False, "message": "License file not found or invalid"}

        # Check expiry
        try:
            expiry = datetime.fromisoformat(self.license_data["expiry"])
            if datetime.now() > expiry:
                days_expired = (datetime.now() - expiry).days
                return {
                    "valid": False,
                    "message": f"License expired {days_expired} days ago. Contact BATDAN to renew."
                }
        except Exception:
            return {"valid": False, "message": "Invalid expiry date in license"}

        # Check checksum
        if not self._verify_checksum():
            return {"valid": False, "message": "License has been tampered with"}

        # Calculate days remaining
        days_remaining = (expiry - datetime.now()).days

        return {
            "valid": True,
            "tier": self.license_data.get("tier", "basic"),
            "days_remaining": days_remaining,
            "message": f"License valid. {days_remaining} days remaining."
        }

    def _verify_checksum(self) -> bool:
        """Verify license checksum"""
        # Basic checksum verification
        # In production, this would check against a server
        return "checksum" in self.license_data

    def get_features(self) -> list:
        """Get features allowed by this license tier"""
        tier = self.license_data.get("tier", "basic") if self.license_data else "basic"

        features = {
            "basic": [
                "terminal_access",
                "single_ai_provider",
                "basic_memory"
            ],
            "pro": [
                "terminal_access",
                "web_ui",
                "three_ai_providers",
                "full_memory",
                "voice_output",
                "knowledge_lookup"
            ],
            "enterprise": [
                "terminal_access",
                "web_ui",
                "all_ai_providers",
                "full_memory",
                "voice_input_output",
                "knowledge_lookup",
                "mcp_servers",
                "security_scanning",
                "rag_system"
            ]
        }
        return features.get(tier, features["basic"])

    def check_feature(self, feature: str) -> bool:
        """Check if a feature is allowed"""
        return feature in self.get_features()

    def enforce(self):
        """Enforce license - exit if invalid"""
        result = self.validate()

        if not result["valid"]:
            print("\n" + "=" * 50)
            print("ALFRED LICENSE ERROR")
            print("=" * 50)
            print(result["message"])
            print("\nContact: danieljrita@hotmail.com")
            print("=" * 50 + "\n")
            sys.exit(1)

        # Show license info
        print(f"\n[License] {result['tier'].upper()} - {result['days_remaining']} days remaining")

        return result


def require_license(func):
    """Decorator to require valid license before running"""
    def wrapper(*args, **kwargs):
        validator = LicenseValidator()
        result = validator.validate()

        if not result["valid"]:
            print(f"License Error: {result['message']}")
            return None

        return func(*args, **kwargs)

    return wrapper


def require_feature(feature: str):
    """Decorator to require specific feature"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            validator = LicenseValidator()

            if not validator.check_feature(feature):
                tier = validator.license_data.get("tier", "unknown") if validator.license_data else "none"
                print(f"Feature '{feature}' not available in {tier} tier.")
                print("Upgrade your license for access.")
                return None

            return func(*args, **kwargs)

        return wrapper
    return decorator


# Quick test
if __name__ == "__main__":
    validator = LicenseValidator()
    result = validator.validate()
    print(f"\nValidation Result: {result}")
    print(f"Machine ID: {validator.machine_id}")
    print(f"Available Features: {validator.get_features()}")
