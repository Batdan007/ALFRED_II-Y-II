"""
ALFRED Brain Sync Client - PC-to-PC Synchronization
Connects to the Batcave sync server from any Batcomputer

Usage:
    python brain_sync_client.py --server 192.168.1.100:5000  # Sync with server
    python brain_sync_client.py --pull                        # Pull from server
    python brain_sync_client.py --push                        # Push to server
    python brain_sync_client.py --status                      # Check sync status

For out-of-state: Use Tailscale VPN to connect to your home network

Author: Daniel J Rita (BATDAN)
"""

import os
import sys
import json
import socket
import sqlite3
import hashlib
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from core.brain import AlfredBrain


class BrainSyncClient:
    """Sync ALFRED's brain between PCs"""

    def __init__(self, server_url: str = None):
        self.brain = AlfredBrain()
        self.db_path = self.brain.db_path
        self.device_id = self._get_device_id()
        self.server_url = server_url or os.getenv("ALFRED_SYNC_SERVER", "http://localhost:5050")
        self.sync_state_file = Path(self.db_path).parent / "sync_state.json"

    def _get_device_id(self) -> str:
        """Generate unique device ID from hostname + MAC"""
        hostname = socket.gethostname()
        # Simple hash to avoid exposing MAC
        device_hash = hashlib.md5(hostname.encode()).hexdigest()[:8]
        return f"pc-{hostname}-{device_hash}"

    def _load_sync_state(self) -> Dict:
        """Load last sync state"""
        if self.sync_state_file.exists():
            with open(self.sync_state_file, 'r') as f:
                return json.load(f)
        return {"last_sync": None, "last_hash": None}

    def _save_sync_state(self, state: Dict):
        """Save sync state"""
        with open(self.sync_state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _get_db_hash(self) -> str:
        """Get hash of current database for change detection"""
        if not os.path.exists(self.db_path):
            return ""
        with open(self.db_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def register(self) -> bool:
        """Register this PC with the sync server"""
        try:
            response = requests.post(
                f"{self.server_url}/sync/register",
                json={
                    "device_id": self.device_id,
                    "device_type": "pc",
                    "hostname": socket.gethostname(),
                    "platform": sys.platform,
                    "brain_path": str(self.db_path)
                },
                timeout=10
            )
            if response.status_code == 200:
                print(f"[OK] Registered as: {self.device_id}")
                return True
            else:
                print(f"[ERROR] Registration failed: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Cannot connect to sync server at {self.server_url}")
            return False

    def get_local_changes(self, since: str = None) -> Dict[str, List]:
        """Get all local changes since last sync"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        changes = {
            "conversations": [],
            "knowledge": [],
            "patterns": [],
            "skills": [],
            "topics": [],
            "mistakes": []
        }

        # Build WHERE clause for timestamp filtering
        time_filter = ""
        if since:
            time_filter = f"WHERE timestamp > '{since}'"

        # Get conversations
        c.execute(f"""
            SELECT id, user_input, alfred_response, timestamp, importance,
                   sentiment, topics, context, success
            FROM conversations
            {time_filter}
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        for row in c.fetchall():
            changes["conversations"].append(dict(row))

        # Get knowledge
        c.execute(f"""
            SELECT id, category, key, value, confidence, importance,
                   timestamp, source, last_accessed
            FROM knowledge
            {time_filter}
            ORDER BY timestamp DESC
            LIMIT 200
        """)
        for row in c.fetchall():
            changes["knowledge"].append(dict(row))

        # Get patterns
        c.execute("""
            SELECT id, pattern_type, pattern_data, frequency,
                   success_rate, last_seen, confidence
            FROM patterns
            ORDER BY last_seen DESC
            LIMIT 50
        """)
        for row in c.fetchall():
            changes["patterns"].append(dict(row))

        # Get skills
        c.execute("""
            SELECT skill_name, proficiency, times_used, success_count,
                   failure_count, last_used, notes
            FROM skills
            ORDER BY last_used DESC
        """)
        for row in c.fetchall():
            changes["skills"].append(dict(row))

        # Get topics
        c.execute("""
            SELECT topic, frequency, first_seen, last_seen, interest_level
            FROM topics
            ORDER BY last_seen DESC
            LIMIT 50
        """)
        for row in c.fetchall():
            changes["topics"].append(dict(row))

        # Get mistakes
        c.execute("""
            SELECT id, timestamp, error_type, description, context,
                   solution, learned
            FROM mistakes
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        for row in c.fetchall():
            changes["mistakes"].append(dict(row))

        conn.close()
        return changes

    def push(self) -> bool:
        """Push local brain changes to server"""
        print(f"[SYNC] Pushing brain to {self.server_url}...")

        sync_state = self._load_sync_state()
        changes = self.get_local_changes(sync_state.get("last_sync"))

        total_items = sum(len(v) for v in changes.values())
        print(f"[INFO] Sending {total_items} items to server")

        try:
            response = requests.post(
                f"{self.server_url}/sync/push",
                json={
                    "device_id": self.device_id,
                    "timestamp": datetime.now().isoformat(),
                    "changes": changes
                },
                timeout=60,
                headers={"Content-Encoding": "gzip"}
            )

            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Push complete!")
                print(f"     Conversations: {result.get('conversations_merged', 0)}")
                print(f"     Knowledge: {result.get('knowledge_merged', 0)}")
                print(f"     Conflicts resolved: {result.get('conflicts_resolved', 0)}")

                # Update sync state
                self._save_sync_state({
                    "last_sync": datetime.now().isoformat(),
                    "last_hash": self._get_db_hash(),
                    "last_push": datetime.now().isoformat()
                })
                return True
            else:
                print(f"[ERROR] Push failed: {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Cannot connect to {self.server_url}")
            return False

    def pull(self) -> bool:
        """Pull brain changes from server"""
        print(f"[SYNC] Pulling brain from {self.server_url}...")

        sync_state = self._load_sync_state()

        try:
            response = requests.get(
                f"{self.server_url}/sync/pull",
                params={
                    "device_id": self.device_id,
                    "since": sync_state.get("last_sync")
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                changes = data.get("changes", {})

                total_items = sum(len(v) for v in changes.values())
                print(f"[INFO] Received {total_items} items from server")

                # Merge into local brain
                merged = self._merge_changes(changes)

                print(f"[OK] Pull complete!")
                print(f"     Conversations: {merged.get('conversations', 0)}")
                print(f"     Knowledge: {merged.get('knowledge', 0)}")

                # Update sync state
                self._save_sync_state({
                    "last_sync": datetime.now().isoformat(),
                    "last_hash": self._get_db_hash(),
                    "last_pull": datetime.now().isoformat()
                })
                return True
            else:
                print(f"[ERROR] Pull failed: {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Cannot connect to {self.server_url}")
            return False

    def _merge_changes(self, changes: Dict) -> Dict[str, int]:
        """Merge remote changes into local brain"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        merged = {}

        # Merge conversations (skip duplicates by checking timestamp+user_input hash)
        merged["conversations"] = 0
        for conv in changes.get("conversations", []):
            # Check if exists
            c.execute("""
                SELECT id FROM conversations
                WHERE timestamp = ? AND user_input = ?
            """, (conv["timestamp"], conv["user_input"]))
            if not c.fetchone():
                c.execute("""
                    INSERT INTO conversations
                    (user_input, alfred_response, timestamp, importance,
                     sentiment, topics, context, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conv["user_input"], conv["alfred_response"],
                    conv["timestamp"], conv.get("importance", 5),
                    conv.get("sentiment"), conv.get("topics"),
                    conv.get("context"), conv.get("success", 1)
                ))
                merged["conversations"] += 1

        # Merge knowledge (update if newer, insert if new)
        merged["knowledge"] = 0
        for k in changes.get("knowledge", []):
            c.execute("""
                SELECT id, timestamp FROM knowledge
                WHERE category = ? AND key = ?
            """, (k["category"], k["key"]))
            existing = c.fetchone()

            if existing:
                # Update if newer
                k_timestamp = k.get("timestamp") or k.get("learned_at", "")
                if k_timestamp > (existing[1] or ""):
                    c.execute("""
                        UPDATE knowledge
                        SET value = ?, confidence = ?, importance = ?,
                            timestamp = ?, source = ?
                        WHERE id = ?
                    """, (
                        k["value"], k.get("confidence", 0.5),
                        k.get("importance", 5), k_timestamp,
                        k.get("source", "sync"), existing[0]
                    ))
                    merged["knowledge"] += 1
            else:
                # Insert new
                c.execute("""
                    INSERT INTO knowledge
                    (category, key, value, confidence, importance, timestamp, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    k["category"], k["key"], k["value"],
                    k.get("confidence", 0.5), k.get("importance", 5),
                    k.get("timestamp") or k.get("learned_at"), k.get("source", "sync")
                ))
                merged["knowledge"] += 1

        conn.commit()
        conn.close()
        return merged

    def sync(self) -> bool:
        """Full bidirectional sync"""
        print("=" * 50)
        print("ALFRED Brain Sync")
        print("=" * 50)
        print(f"Device: {self.device_id}")
        print(f"Server: {self.server_url}")
        print(f"Brain:  {self.db_path}")
        print("=" * 50)

        # Register first
        self.register()

        # Push local changes
        print("\n[1/2] Pushing local changes...")
        push_ok = self.push()

        # Pull remote changes
        print("\n[2/2] Pulling remote changes...")
        pull_ok = self.pull()

        print("\n" + "=" * 50)
        if push_ok and pull_ok:
            print("[OK] Sync complete!")
        else:
            print("[WARN] Sync completed with errors")
        print("=" * 50)

        return push_ok and pull_ok

    def status(self) -> Dict:
        """Get sync status"""
        sync_state = self._load_sync_state()
        current_hash = self._get_db_hash()

        has_local_changes = current_hash != sync_state.get("last_hash")

        status = {
            "device_id": self.device_id,
            "server_url": self.server_url,
            "brain_path": str(self.db_path),
            "last_sync": sync_state.get("last_sync", "Never"),
            "has_local_changes": has_local_changes,
            "brain_stats": self.brain.get_stats() if hasattr(self.brain, 'get_stats') else {}
        }

        # Try to get server status
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                status["server_status"] = "online"
                status["server_info"] = response.json()
            else:
                status["server_status"] = "error"
        except:
            status["server_status"] = "offline"

        return status


def main():
    parser = argparse.ArgumentParser(description="ALFRED Brain Sync Client")
    parser.add_argument("--server", "-s", help="Sync server URL (e.g., http://192.168.1.100:5000)")
    parser.add_argument("--push", action="store_true", help="Push local changes to server")
    parser.add_argument("--pull", action="store_true", help="Pull changes from server")
    parser.add_argument("--sync", action="store_true", help="Full bidirectional sync (default)")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    parser.add_argument("--register", action="store_true", help="Register with sync server")

    args = parser.parse_args()

    # Get server URL
    server_url = args.server or os.getenv("ALFRED_SYNC_SERVER")
    if not server_url and not args.status:
        print("Usage: python brain_sync_client.py --server <URL>")
        print("")
        print("Set ALFRED_SYNC_SERVER environment variable or use --server flag")
        print("")
        print("Examples:")
        print("  python brain_sync_client.py --server http://192.168.1.100:5000 --sync")
        print("  python brain_sync_client.py --server http://batcave.local:5000 --push")
        print("")
        print("For out-of-state access, install Tailscale:")
        print("  https://tailscale.com/download")
        print("  Then use your Tailscale IP: --server http://100.x.x.x:5000")
        return

    client = BrainSyncClient(server_url)

    if args.status:
        status = client.status()
        print("\nALFRED Brain Sync Status")
        print("=" * 40)
        print(f"Device ID:     {status['device_id']}")
        print(f"Server:        {status['server_url']}")
        print(f"Server Status: {status['server_status']}")
        print(f"Brain Path:    {status['brain_path']}")
        print(f"Last Sync:     {status['last_sync']}")
        print(f"Local Changes: {'Yes' if status['has_local_changes'] else 'No'}")
        print("=" * 40)
    elif args.register:
        client.register()
    elif args.push:
        client.push()
    elif args.pull:
        client.pull()
    else:
        # Default: full sync
        client.sync()


if __name__ == "__main__":
    main()
