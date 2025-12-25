"""
ALFRED II-Y-II License Generator
Generates machine-locked licenses for client deployments

Author: Daniel J. Rita (BATDAN)
"""

import hashlib
import json
import base64
import secrets
import argparse
from datetime import datetime, timedelta
from pathlib import Path


class LicenseGenerator:
    """Generate and validate ALFRED client licenses"""

    # Your secret key - KEEP THIS SAFE
    MASTER_SECRET = "BATDAN_ALFRED_2024_MASTER_KEY"

    def __init__(self):
        self.licenses_db = Path("licenses.json")
        self.licenses = self._load_licenses()

    def _load_licenses(self) -> dict:
        """Load existing licenses"""
        if self.licenses_db.exists():
            return json.loads(self.licenses_db.read_text())
        return {}

    def _save_licenses(self):
        """Save licenses to disk"""
        self.licenses_db.write_text(json.dumps(self.licenses, indent=2))

    def _generate_key(self, client_id: str, machine_id: str, expiry: str) -> str:
        """Generate a unique license key"""
        data = f"{client_id}:{machine_id}:{expiry}:{self.MASTER_SECRET}"
        hash_bytes = hashlib.sha256(data.encode()).digest()
        key = base64.urlsafe_b64encode(hash_bytes[:24]).decode()
        return f"ALFRED-{key}"

    def generate_license(
        self,
        client_name: str,
        client_email: str,
        tier: str = "basic",
        days: int = 30,
        machine_id: str = None
    ) -> dict:
        """
        Generate a new client license

        Args:
            client_name: Client's name
            client_email: Client's email
            tier: basic, pro, or enterprise
            days: License duration
            machine_id: Optional machine lock (generated on client machine)

        Returns:
            License data dictionary
        """
        client_id = secrets.token_hex(8)
        expiry = (datetime.now() + timedelta(days=days)).isoformat()

        # If no machine ID, generate placeholder (will be locked on first run)
        if not machine_id:
            machine_id = "PENDING_ACTIVATION"

        license_key = self._generate_key(client_id, machine_id, expiry)

        license_data = {
            "license_key": license_key,
            "client_id": client_id,
            "client_name": client_name,
            "client_email": client_email,
            "tier": tier,
            "features": self._get_tier_features(tier),
            "machine_id": machine_id,
            "created": datetime.now().isoformat(),
            "expiry": expiry,
            "status": "active"
        }

        # Save to database
        self.licenses[license_key] = license_data
        self._save_licenses()

        # Create license file for client
        license_file = Path(f"licenses/{client_id}.license")
        license_file.parent.mkdir(exist_ok=True)

        # Encode license data for client
        client_license = {
            "key": license_key,
            "tier": tier,
            "expiry": expiry,
            "checksum": self._generate_checksum(license_data)
        }
        encoded = base64.b64encode(json.dumps(client_license).encode()).decode()
        license_file.write_text(encoded)

        print(f"\n{'='*50}")
        print("LICENSE GENERATED")
        print(f"{'='*50}")
        print(f"Client: {client_name}")
        print(f"Email: {client_email}")
        print(f"Tier: {tier.upper()}")
        print(f"Expires: {expiry[:10]}")
        print(f"License Key: {license_key}")
        print(f"License File: {license_file}")
        print(f"{'='*50}\n")

        return license_data

    def _get_tier_features(self, tier: str) -> list:
        """Get features for each tier"""
        features = {
            "basic": [
                "terminal_access",
                "single_ai_provider",
                "basic_memory",
                "text_only"
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
                "rag_system",
                "priority_support"
            ]
        }
        return features.get(tier, features["basic"])

    def _generate_checksum(self, data: dict) -> str:
        """Generate checksum for license validation"""
        check_data = f"{data['license_key']}:{data['expiry']}:{self.MASTER_SECRET}"
        return hashlib.md5(check_data.encode()).hexdigest()[:16]

    def validate_license(self, license_key: str, machine_id: str = None) -> dict:
        """Validate a license key"""
        if license_key not in self.licenses:
            return {"valid": False, "error": "License not found"}

        license_data = self.licenses[license_key]

        # Check expiry
        expiry = datetime.fromisoformat(license_data["expiry"])
        if datetime.now() > expiry:
            return {"valid": False, "error": "License expired"}

        # Check machine lock
        if license_data["machine_id"] != "PENDING_ACTIVATION":
            if machine_id and machine_id != license_data["machine_id"]:
                return {"valid": False, "error": "License locked to different machine"}

        # Check status
        if license_data["status"] != "active":
            return {"valid": False, "error": f"License {license_data['status']}"}

        return {
            "valid": True,
            "tier": license_data["tier"],
            "features": license_data["features"],
            "days_remaining": (expiry - datetime.now()).days
        }

    def revoke_license(self, license_key: str):
        """Revoke a license"""
        if license_key in self.licenses:
            self.licenses[license_key]["status"] = "revoked"
            self._save_licenses()
            print(f"License {license_key} revoked")

    def list_licenses(self):
        """List all licenses"""
        print(f"\n{'='*80}")
        print("ALFRED LICENSES")
        print(f"{'='*80}")

        for key, data in self.licenses.items():
            status = "ACTIVE" if data["status"] == "active" else data["status"].upper()
            expiry = data["expiry"][:10]
            print(f"{data['client_name']:20} | {data['tier']:10} | {expiry} | {status}")

        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description="ALFRED License Generator")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--email", required=True, help="Client email")
    parser.add_argument("--tier", default="basic", choices=["basic", "pro", "enterprise"])
    parser.add_argument("--days", type=int, default=30, help="License duration in days")
    parser.add_argument("--list", action="store_true", help="List all licenses")
    parser.add_argument("--revoke", help="Revoke a license key")

    args = parser.parse_args()

    generator = LicenseGenerator()

    if args.list:
        generator.list_licenses()
    elif args.revoke:
        generator.revoke_license(args.revoke)
    else:
        generator.generate_license(
            client_name=args.client,
            client_email=args.email,
            tier=args.tier,
            days=args.days
        )


if __name__ == "__main__":
    main()
