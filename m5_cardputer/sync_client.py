"""
Sync Client - WiFi Sync for ALFRED Edge
========================================
Handles communication with main ALFRED_IV-Y-VI brain server.
Uploads collected data and downloads assigned tasks.

Protocol:
- HTTP REST API over WiFi
- JSON payloads with gzip compression
- Chunked uploads for large voice files
- Automatic retry with backoff

Author: Daniel J. Rita (BATDAN)
"""

import json
import time
import gc

# MicroPython HTTP client
try:
    import urequests as requests
except ImportError:
    import requests

# Optional compression (if available)
try:
    import zlib
    COMPRESSION_AVAILABLE = True
except ImportError:
    COMPRESSION_AVAILABLE = False


class SyncClient:
    """
    Client for syncing ALFRED Edge data to main ALFRED_IV-Y-VI server.

    The server runs alfred_sync_server.py on the main ALFRED installation,
    exposing REST endpoints for edge devices to upload data.
    """

    def __init__(self, server_url="http://192.168.1.100:8765"):
        """
        Initialize sync client.

        Args:
            server_url: Base URL of ALFRED sync server
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 2  # seconds

        # Endpoints
        self.endpoints = {
            "upload": f"{self.server_url}/api/edge/upload",
            "tasks": f"{self.server_url}/api/edge/tasks",
            "register": f"{self.server_url}/api/edge/register",
            "health": f"{self.server_url}/api/health"
        }

        print(f"[INFO] Sync client initialized: {self.server_url}")

    def _make_request(self, method, url, data=None, headers=None):
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT)
            url: Full URL
            data: Request body (dict)
            headers: Optional headers

        Returns:
            dict: Response JSON or error dict
        """
        if headers is None:
            headers = {"Content-Type": "application/json"}

        payload = None
        if data:
            payload = json.dumps(data)

            # Compress if available and payload is large
            if COMPRESSION_AVAILABLE and len(payload) > 1024:
                compressed = zlib.compress(payload.encode())
                if len(compressed) < len(payload):
                    payload = compressed
                    headers["Content-Encoding"] = "gzip"

        last_error = None

        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=self.timeout)
                elif method == "POST":
                    response = requests.post(url, data=payload, headers=headers, timeout=self.timeout)
                elif method == "PUT":
                    response = requests.put(url, data=payload, headers=headers, timeout=self.timeout)
                else:
                    return {"success": False, "error": f"Unknown method: {method}"}

                # Check status
                if response.status_code == 200:
                    result = response.json()
                    response.close()
                    return result
                else:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_body = response.json()
                        error_msg = error_body.get("error", error_msg)
                    except:
                        pass
                    response.close()
                    last_error = error_msg

            except OSError as e:
                last_error = f"Network error: {e}"
            except Exception as e:
                last_error = f"Request failed: {e}"

            # Retry with backoff
            if attempt < self.max_retries - 1:
                print(f"[WARN] Attempt {attempt + 1} failed, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay * (attempt + 1))
                gc.collect()

        return {"success": False, "error": last_error}

    # ========================================
    # Connection & Registration
    # ========================================

    def check_connection(self):
        """
        Check if server is reachable.

        Returns:
            bool: True if server responds
        """
        try:
            result = self._make_request("GET", self.endpoints["health"])
            return result.get("status") == "ok"
        except:
            return False

    def register_device(self, device_info):
        """
        Register this edge device with the server.

        Args:
            device_info: Dict with device_name, device_type, worker_id, etc.

        Returns:
            dict: Registration response
        """
        print(f"[INFO] Registering device: {device_info.get('device_name')}")

        result = self._make_request("POST", self.endpoints["register"], {
            "device_name": device_info.get("device_name"),
            "device_type": device_info.get("device_type", "m5_cardputer"),
            "worker_id": device_info.get("worker_id"),
            "worker_name": device_info.get("worker_name"),
            "firmware_version": "1.0.0",
            "capabilities": ["notes", "voice", "observations", "tasks"],
            "timestamp": time.time()
        })

        if result.get("success"):
            print(f"[OK] Device registered")
        else:
            print(f"[ERROR] Registration failed: {result.get('error')}")

        return result

    # ========================================
    # Upload Operations
    # ========================================

    def upload(self, items):
        """
        Upload items to ALFRED server.

        Args:
            items: List of items to upload (notes, voice, observations, etc.)

        Returns:
            dict: Upload result with success flag and any tasks from server
        """
        if not items:
            return {"success": True, "synced": 0, "tasks": []}

        print(f"[INFO] Uploading {len(items)} items...")

        # Separate voice notes (they're larger)
        voice_items = [i for i in items if i.get("type") == "voice_note"]
        other_items = [i for i in items if i.get("type") != "voice_note"]

        synced_count = 0
        all_tasks = []

        # Upload non-voice items in batch
        if other_items:
            result = self._upload_batch(other_items)
            if result.get("success"):
                synced_count += len(other_items)
                all_tasks.extend(result.get("tasks", []))
            else:
                return result

        # Upload voice items individually (they're large)
        for voice in voice_items:
            result = self._upload_voice(voice)
            if result.get("success"):
                synced_count += 1
            else:
                print(f"[WARN] Voice upload failed: {voice.get('id')}")

        return {
            "success": True,
            "synced": synced_count,
            "tasks": all_tasks
        }

    def _upload_batch(self, items):
        """Upload batch of items (non-voice)."""
        return self._make_request("POST", self.endpoints["upload"], {
            "items": items,
            "timestamp": time.time(),
            "batch_size": len(items)
        })

    def _upload_voice(self, voice_item):
        """
        Upload voice note (potentially large).

        Uses chunked upload if item is very large.
        """
        # Check size - if under 50KB, upload normally
        audio_data = voice_item.get("audio_data", "")
        if len(audio_data) < 50 * 1024:
            return self._make_request("POST", self.endpoints["upload"], {
                "items": [voice_item],
                "timestamp": time.time()
            })

        # Chunked upload for large files
        chunk_size = 32 * 1024  # 32KB chunks
        chunks = []
        for i in range(0, len(audio_data), chunk_size):
            chunks.append(audio_data[i:i + chunk_size])

        # Start chunked upload
        init_result = self._make_request("POST", f"{self.endpoints['upload']}/chunked/start", {
            "item_id": voice_item.get("id"),
            "type": "voice_note",
            "total_chunks": len(chunks),
            "metadata": {k: v for k, v in voice_item.items() if k != "audio_data"}
        })

        if not init_result.get("success"):
            return init_result

        upload_id = init_result.get("upload_id")

        # Upload chunks
        for i, chunk in enumerate(chunks):
            chunk_result = self._make_request("POST", f"{self.endpoints['upload']}/chunked/chunk", {
                "upload_id": upload_id,
                "chunk_index": i,
                "data": chunk
            })

            if not chunk_result.get("success"):
                return chunk_result

            # Free memory between chunks
            gc.collect()

        # Complete upload
        return self._make_request("POST", f"{self.endpoints['upload']}/chunked/complete", {
            "upload_id": upload_id
        })

    # ========================================
    # Download Operations
    # ========================================

    def get_tasks(self, worker_id, device_name):
        """
        Get assigned tasks from server.

        Args:
            worker_id: Worker identifier
            device_name: Device identifier

        Returns:
            dict: Task list response
        """
        print(f"[INFO] Fetching tasks for {worker_id}...")

        result = self._make_request("GET",
            f"{self.endpoints['tasks']}?worker_id={worker_id}&device={device_name}")

        if result.get("success"):
            tasks = result.get("tasks", [])
            print(f"[OK] Retrieved {len(tasks)} tasks")
        else:
            print(f"[ERROR] Task fetch failed: {result.get('error')}")

        return result

    def acknowledge_tasks(self, task_ids):
        """
        Acknowledge receipt of tasks.

        Args:
            task_ids: List of task IDs received

        Returns:
            dict: Acknowledgement result
        """
        return self._make_request("POST", f"{self.endpoints['tasks']}/ack", {
            "task_ids": task_ids,
            "timestamp": time.time()
        })

    # ========================================
    # Full Sync
    # ========================================

    def full_sync(self, local_brain, device_config):
        """
        Perform full sync operation.

        1. Upload all pending items
        2. Download new tasks
        3. Clean up old synced items

        Args:
            local_brain: LocalBrain instance
            device_config: Device configuration dict

        Returns:
            dict: Sync summary
        """
        print("\n" + "="*40)
        print("  ALFRED Edge - Full Sync")
        print("="*40)

        summary = {
            "success": True,
            "uploaded": 0,
            "tasks_received": 0,
            "errors": []
        }

        # 1. Check connection
        if not self.check_connection():
            summary["success"] = False
            summary["errors"].append("Server unreachable")
            return summary

        # 2. Register device (if first sync)
        self.register_device(device_config)

        # 3. Upload pending items
        pending = local_brain.get_pending()
        if pending:
            print(f"\n[SYNC] Uploading {len(pending)} items...")
            result = self.upload(pending)

            if result.get("success"):
                # Mark as synced
                synced_count = result.get("synced", 0)
                for item in pending[:synced_count]:
                    local_brain.mark_synced(item["id"])
                summary["uploaded"] = synced_count

                # Process any tasks returned
                if result.get("tasks"):
                    for task in result["tasks"]:
                        local_brain.store_task(task)
                    summary["tasks_received"] = len(result["tasks"])
            else:
                summary["errors"].append(f"Upload failed: {result.get('error')}")

        # 4. Fetch new tasks
        print("\n[SYNC] Checking for new tasks...")
        task_result = self.get_tasks(
            device_config.get("worker_id"),
            device_config.get("device_name")
        )

        if task_result.get("success"):
            tasks = task_result.get("tasks", [])
            for task in tasks:
                local_brain.store_task(task)
            summary["tasks_received"] += len(tasks)

            # Acknowledge receipt
            if tasks:
                self.acknowledge_tasks([t["id"] for t in tasks])

        # 5. Clean up old synced items (keep 7 days)
        cleaned = local_brain.delete_synced(older_than_days=7)
        if cleaned > 0:
            print(f"[SYNC] Cleaned {cleaned} old items")

        # Summary
        print("\n" + "-"*40)
        print(f"  Uploaded: {summary['uploaded']} items")
        print(f"  Tasks: {summary['tasks_received']} new")
        print(f"  Status: {'SUCCESS' if summary['success'] else 'PARTIAL'}")
        print("-"*40 + "\n")

        return summary


# ========================================
# Test / Debug
# ========================================

def test_sync_client():
    """Test sync client (requires running server)."""
    print("\n=== Testing Sync Client ===\n")

    client = SyncClient("http://localhost:8765")

    # Test health check
    print("1. Testing health check...")
    if client.check_connection():
        print("   Server is reachable")
    else:
        print("   Server not reachable (expected if not running)")
        return

    # Test device registration
    print("\n2. Testing device registration...")
    result = client.register_device({
        "device_name": "TEST_DEVICE",
        "worker_id": "test_worker",
        "worker_name": "Test Worker"
    })
    print(f"   Result: {result}")

    # Test upload
    print("\n3. Testing upload...")
    test_items = [
        {
            "id": "test_1",
            "type": "note",
            "content": "Test note from sync client",
            "category": "general",
            "timestamp": time.time()
        }
    ]
    result = client.upload(test_items)
    print(f"   Result: {result}")

    # Test task fetch
    print("\n4. Testing task fetch...")
    result = client.get_tasks("test_worker", "TEST_DEVICE")
    print(f"   Result: {result}")

    print("\n=== Tests Complete ===\n")


if __name__ == "__main__":
    test_sync_client()
