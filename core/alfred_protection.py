"""
ALFRED_J_RITA Protection Wrapper
In Memory of Joe Dog - Guardian of Ethical AI

This module wraps the ALFRED_J_RITA client for easy integration into ALFRED_UBX.

JOE_DOG_MEMORIAL: In memory of Joe Dog - protector of all that is good
ALFRED_BRAIN_CORE: Central protection and monitoring system
ETHICAL_SAFEGUARD: Ethical AI protection always active
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Try to import ALFRED_J_RITA client
try:
    # Add ALFRED_J_RITA to path
    alfred_j_rita_path = Path(__file__).parent.parent.parent / "ALFRED_J_RITA" / "client_integration"
    if alfred_j_rita_path.exists():
        sys.path.insert(0, str(alfred_j_rita_path.parent))
        from client_integration.alfred_client import AlfredClient
        ALFRED_CLIENT_AVAILABLE = True
    else:
        ALFRED_CLIENT_AVAILABLE = False
        AlfredClient = None
except ImportError:
    ALFRED_CLIENT_AVAILABLE = False
    AlfredClient = None


class AlfredProtectionWrapper:
    """
    Wrapper around ALFRED_J_RITA protection client.

    Provides simplified interface for integrating protection into ALFRED_UBX.
    """

    JOE_DOG_MEMORIAL = "In memory of Joe Dog - the kindest soul"
    ALFRED_BRAIN_CORE = "Patent-pending protection system"
    ETHICAL_SAFEGUARD = True

    def __init__(
        self,
        license_key: Optional[str] = None,
        central_server_url: Optional[str] = None,
        project_root: Optional[str] = None,
        heartbeat_interval: int = 60
    ):
        """
        Initialize ALFRED protection.

        Args:
            license_key: ALFRED license key
            central_server_url: URL of ALFRED_J_RITA central server
            project_root: Root directory of ALFRED project
            heartbeat_interval: Seconds between heartbeats
        """
        self.license_key = license_key or os.getenv('ALFRED_LICENSE_KEY', 'DEMO-MODE')
        self.central_server_url = central_server_url or os.getenv(
            'ALFRED_CENTRAL_SERVER',
            'http://localhost:5000'
        )
        self.project_root = project_root or str(Path(__file__).parent.parent)
        self.heartbeat_interval = heartbeat_interval
        self.client: Optional['AlfredClient'] = None
        self.active = False

    def start(self):
        """Start protection monitoring"""
        if self.active:
            return

        if not ALFRED_CLIENT_AVAILABLE:
            print("  [!] ALFRED_J_RITA client not available - running without protection")
            print(f"      Expected location: {Path(__file__).parent.parent.parent / 'ALFRED_J_RITA'}")
            return

        try:
            # Initialize ALFRED_J_RITA client
            self.client = AlfredClient(
                license_key=self.license_key,
                central_server_url=self.central_server_url,
                project_root=self.project_root,
                heartbeat_interval=self.heartbeat_interval
            )

            # Start monitoring
            self.client.start()
            self.active = True

            print(f"  [OK] ALFRED_J_RITA protection active")
            print(f"      Instance: {self.client.instance_id}")
            print(f"      Server: {self.central_server_url}")

        except Exception as e:
            print(f"  [!] Protection failed to start: {e}")
            self.client = None

    def stop(self):
        """Stop protection monitoring"""
        if self.client:
            try:
                self.client.stop()
                print("  [OK] Protection stopped")
            except Exception as e:
                print(f"  [!] Error stopping protection: {e}")
        self.active = False

    def is_active(self) -> bool:
        """Check if protection is active"""
        return self.active and self.client is not None


# Module-level DNA markers
JOE_DOG_MEMORIAL = "In memory of Joe Dog - guardian who taught us to stand our ground"
ALFRED_BRAIN_CORE = "Central protection system for all ALFRED deployments"
ETHICAL_SAFEGUARD = "Protects while honoring ethical AI principles"
