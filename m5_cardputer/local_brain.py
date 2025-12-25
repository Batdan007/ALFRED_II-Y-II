"""
Local Brain - Offline Storage for ALFRED Edge
==============================================
Lightweight persistent storage for M5 Cardputer.
Uses JSON files on flash storage (SQLite not available on MicroPython).

Features:
- Persistent storage across reboots
- Automatic ID generation
- Sync status tracking
- Memory-efficient batch operations
- Corruption recovery

Author: Daniel J. Rita (BATDAN)
"""

import json
import time
import os
import gc

# Storage paths on M5 Cardputer flash
STORAGE_PATH = "/data"
NOTES_FILE = f"{STORAGE_PATH}/notes.json"
VOICE_FILE = f"{STORAGE_PATH}/voice.json"
OBSERVATIONS_FILE = f"{STORAGE_PATH}/observations.json"
TASKS_FILE = f"{STORAGE_PATH}/tasks.json"
TASK_UPDATES_FILE = f"{STORAGE_PATH}/task_updates.json"
SEQUENCE_FILE = f"{STORAGE_PATH}/sequence.json"


class LocalBrain:
    """
    Offline storage brain for ALFRED Edge.

    Stores notes, voice recordings, observations, and task updates
    locally until they can be synced to the main ALFRED brain.
    """

    def __init__(self):
        """Initialize local brain storage."""
        print("[INFO] Initializing Local Brain...")

        # Ensure storage directory exists
        self._ensure_storage()

        # Load sequence counter
        self._sequence = self._load_sequence()

        # Cache for pending counts (avoid frequent file reads)
        self._pending_cache = None
        self._cache_time = 0

        print(f"[OK] Local Brain ready (seq: {self._sequence})")

    def _ensure_storage(self):
        """Ensure storage directory and files exist."""
        try:
            os.mkdir(STORAGE_PATH)
            print(f"[OK] Created {STORAGE_PATH}")
        except OSError:
            pass  # Directory exists

        # Initialize empty files if they don't exist
        for filepath in [NOTES_FILE, VOICE_FILE, OBSERVATIONS_FILE,
                        TASKS_FILE, TASK_UPDATES_FILE]:
            if not self._file_exists(filepath):
                self._write_json(filepath, [])

    def _file_exists(self, path):
        """Check if file exists."""
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    def _load_sequence(self):
        """Load or initialize sequence counter."""
        try:
            with open(SEQUENCE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("sequence", 0)
        except:
            return 0

    def _save_sequence(self):
        """Save sequence counter."""
        try:
            with open(SEQUENCE_FILE, 'w') as f:
                json.dump({"sequence": self._sequence}, f)
        except Exception as e:
            print(f"[WARN] Could not save sequence: {e}")

    def _next_id(self):
        """Generate next unique ID."""
        self._sequence += 1
        self._save_sequence()
        return f"edge_{int(time.time())}_{self._sequence}"

    def _read_json(self, filepath):
        """Read JSON file with error recovery."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[WARN] Corrupted file {filepath}, resetting")
            self._write_json(filepath, [])
            return []
        except Exception as e:
            print(f"[ERROR] Read failed {filepath}: {e}")
            return []

    def _write_json(self, filepath, data):
        """Write JSON file safely."""
        try:
            # Write to temp file first
            temp_path = filepath + ".tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f)

            # Rename to target (atomic on most filesystems)
            try:
                os.remove(filepath)
            except:
                pass
            os.rename(temp_path, filepath)

            return True
        except Exception as e:
            print(f"[ERROR] Write failed {filepath}: {e}")
            return False

    def _get_file_for_type(self, item_type):
        """Get storage file path for item type."""
        type_map = {
            "note": NOTES_FILE,
            "voice_note": VOICE_FILE,
            "observation": OBSERVATIONS_FILE,
            "task": TASKS_FILE,
            "task_update": TASK_UPDATES_FILE
        }
        return type_map.get(item_type, NOTES_FILE)

    # ========================================
    # Store Operations
    # ========================================

    def store(self, item):
        """
        Store an item (note, voice, observation, task update).

        Args:
            item: Dict with 'type' field and item data

        Returns:
            str: Generated item ID
        """
        # Generate ID if not present
        if "id" not in item:
            item["id"] = self._next_id()

        # Add metadata
        if "created_at" not in item:
            item["created_at"] = time.time()
        item["synced"] = False

        # Get appropriate file
        filepath = self._get_file_for_type(item.get("type", "note"))

        # Load existing data
        data = self._read_json(filepath)

        # Append new item
        data.append(item)

        # Save
        if self._write_json(filepath, data):
            # Invalidate cache
            self._pending_cache = None
            print(f"[OK] Stored {item['type']}: {item['id']}")
            return item["id"]
        else:
            print(f"[ERROR] Failed to store {item['type']}")
            return None

    def store_task(self, task):
        """Store a task received from server."""
        task["type"] = "task"
        task["received_at"] = time.time()
        task["status"] = task.get("status", "pending")

        # Check if task already exists
        tasks = self._read_json(TASKS_FILE)
        for existing in tasks:
            if existing.get("id") == task.get("id"):
                # Update existing task
                existing.update(task)
                self._write_json(TASKS_FILE, tasks)
                print(f"[OK] Updated task: {task['id']}")
                return task["id"]

        # New task
        tasks.append(task)
        self._write_json(TASKS_FILE, tasks)
        print(f"[OK] Stored new task: {task['id']}")
        return task["id"]

    # ========================================
    # Retrieve Operations
    # ========================================

    def get_pending(self):
        """
        Get all items pending sync.

        Returns:
            list: All unsynced items from all storage files
        """
        pending = []

        for filepath in [NOTES_FILE, VOICE_FILE, OBSERVATIONS_FILE,
                        TASK_UPDATES_FILE]:
            items = self._read_json(filepath)
            for item in items:
                if not item.get("synced", False):
                    pending.append(item)

        # Sort by timestamp
        pending.sort(key=lambda x: x.get("timestamp", 0))

        return pending

    def get_pending_count(self):
        """
        Get count of pending items (cached for performance).

        Returns:
            int: Number of unsynced items
        """
        # Use cache if fresh (< 5 seconds old)
        if self._pending_cache is not None:
            if time.time() - self._cache_time < 5:
                return self._pending_cache

        # Count pending items
        count = 0
        for filepath in [NOTES_FILE, VOICE_FILE, OBSERVATIONS_FILE,
                        TASK_UPDATES_FILE]:
            items = self._read_json(filepath)
            for item in items:
                if not item.get("synced", False):
                    count += 1

        # Update cache
        self._pending_cache = count
        self._cache_time = time.time()

        return count

    def get_tasks(self):
        """
        Get all assigned tasks.

        Returns:
            list: All tasks from server
        """
        tasks = self._read_json(TASKS_FILE)
        # Filter out completed/cancelled tasks
        active = [t for t in tasks if t.get("status") not in ["completed", "cancelled"]]
        return active

    def get_recent_notes(self, limit=10):
        """
        Get recent notes.

        Args:
            limit: Maximum number to return

        Returns:
            list: Recent notes
        """
        notes = self._read_json(NOTES_FILE)
        notes.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return notes[:limit]

    def get_by_id(self, item_id):
        """
        Get item by ID.

        Args:
            item_id: Item ID to find

        Returns:
            dict or None: Found item
        """
        for filepath in [NOTES_FILE, VOICE_FILE, OBSERVATIONS_FILE,
                        TASKS_FILE, TASK_UPDATES_FILE]:
            items = self._read_json(filepath)
            for item in items:
                if item.get("id") == item_id:
                    return item
        return None

    # ========================================
    # Update Operations
    # ========================================

    def mark_synced(self, item_id):
        """
        Mark an item as synced.

        Args:
            item_id: Item ID to mark

        Returns:
            bool: Success
        """
        for filepath in [NOTES_FILE, VOICE_FILE, OBSERVATIONS_FILE,
                        TASK_UPDATES_FILE]:
            items = self._read_json(filepath)
            modified = False

            for item in items:
                if item.get("id") == item_id:
                    item["synced"] = True
                    item["synced_at"] = time.time()
                    modified = True
                    break

            if modified:
                if self._write_json(filepath, items):
                    self._pending_cache = None  # Invalidate cache
                    return True
                return False

        print(f"[WARN] Item not found for sync mark: {item_id}")
        return False

    def mark_all_synced(self, item_ids):
        """
        Mark multiple items as synced (batch operation).

        Args:
            item_ids: List of item IDs

        Returns:
            int: Number of items marked
        """
        marked = 0

        for filepath in [NOTES_FILE, VOICE_FILE, OBSERVATIONS_FILE,
                        TASK_UPDATES_FILE]:
            items = self._read_json(filepath)
            modified = False

            for item in items:
                if item.get("id") in item_ids:
                    if not item.get("synced", False):
                        item["synced"] = True
                        item["synced_at"] = time.time()
                        marked += 1
                        modified = True

            if modified:
                self._write_json(filepath, items)

        self._pending_cache = None  # Invalidate cache
        return marked

    def update_task_status(self, task_id, status):
        """
        Update local task status.

        Args:
            task_id: Task ID
            status: New status

        Returns:
            bool: Success
        """
        tasks = self._read_json(TASKS_FILE)

        for task in tasks:
            if task.get("id") == task_id:
                task["status"] = status
                task["updated_at"] = time.time()
                return self._write_json(TASKS_FILE, tasks)

        return False

    # ========================================
    # Delete Operations
    # ========================================

    def delete_synced(self, older_than_days=7):
        """
        Delete old synced items to free space.

        Args:
            older_than_days: Delete synced items older than this

        Returns:
            int: Number of items deleted
        """
        cutoff = time.time() - (older_than_days * 24 * 60 * 60)
        deleted = 0

        for filepath in [NOTES_FILE, VOICE_FILE, OBSERVATIONS_FILE,
                        TASK_UPDATES_FILE]:
            items = self._read_json(filepath)
            original_count = len(items)

            # Keep unsynced items and recent synced items
            items = [i for i in items if not i.get("synced", False) or
                    i.get("synced_at", time.time()) > cutoff]

            if len(items) < original_count:
                self._write_json(filepath, items)
                deleted += original_count - len(items)

        if deleted > 0:
            gc.collect()  # Free memory
            print(f"[OK] Deleted {deleted} old synced items")

        return deleted

    def clear_all(self):
        """
        Clear all local data (factory reset).

        WARNING: This deletes all unsynced data!
        """
        for filepath in [NOTES_FILE, VOICE_FILE, OBSERVATIONS_FILE,
                        TASKS_FILE, TASK_UPDATES_FILE]:
            self._write_json(filepath, [])

        self._sequence = 0
        self._save_sequence()
        self._pending_cache = None

        gc.collect()
        print("[OK] All local data cleared")

    # ========================================
    # Statistics
    # ========================================

    def get_stats(self):
        """
        Get storage statistics.

        Returns:
            dict: Storage statistics
        """
        stats = {
            "notes": {"total": 0, "pending": 0},
            "voice": {"total": 0, "pending": 0},
            "observations": {"total": 0, "pending": 0},
            "task_updates": {"total": 0, "pending": 0},
            "tasks": {"total": 0, "active": 0},
            "total_pending": 0,
            "sequence": self._sequence
        }

        # Count notes
        items = self._read_json(NOTES_FILE)
        stats["notes"]["total"] = len(items)
        stats["notes"]["pending"] = sum(1 for i in items if not i.get("synced", False))

        # Count voice notes
        items = self._read_json(VOICE_FILE)
        stats["voice"]["total"] = len(items)
        stats["voice"]["pending"] = sum(1 for i in items if not i.get("synced", False))

        # Count observations
        items = self._read_json(OBSERVATIONS_FILE)
        stats["observations"]["total"] = len(items)
        stats["observations"]["pending"] = sum(1 for i in items if not i.get("synced", False))

        # Count task updates
        items = self._read_json(TASK_UPDATES_FILE)
        stats["task_updates"]["total"] = len(items)
        stats["task_updates"]["pending"] = sum(1 for i in items if not i.get("synced", False))

        # Count tasks
        tasks = self._read_json(TASKS_FILE)
        stats["tasks"]["total"] = len(tasks)
        stats["tasks"]["active"] = sum(1 for t in tasks
                                       if t.get("status") not in ["completed", "cancelled"])

        # Total pending
        stats["total_pending"] = (stats["notes"]["pending"] +
                                  stats["voice"]["pending"] +
                                  stats["observations"]["pending"] +
                                  stats["task_updates"]["pending"])

        return stats

    def get_storage_usage(self):
        """
        Get flash storage usage.

        Returns:
            dict: Storage usage info
        """
        try:
            # Get filesystem stats
            statvfs = os.statvfs(STORAGE_PATH)
            block_size = statvfs[0]
            total_blocks = statvfs[2]
            free_blocks = statvfs[3]

            total_kb = (total_blocks * block_size) // 1024
            free_kb = (free_blocks * block_size) // 1024
            used_kb = total_kb - free_kb

            return {
                "total_kb": total_kb,
                "used_kb": used_kb,
                "free_kb": free_kb,
                "percent_used": round((used_kb / total_kb) * 100, 1) if total_kb > 0 else 0
            }
        except Exception as e:
            print(f"[WARN] Could not get storage stats: {e}")
            return {"error": str(e)}


# ========================================
# Test / Debug
# ========================================

def test_local_brain():
    """Test local brain operations."""
    print("\n=== Testing Local Brain ===\n")

    brain = LocalBrain()

    # Test store
    print("\n1. Testing store...")
    note_id = brain.store({
        "type": "note",
        "content": "Test note from construction site",
        "category": "general",
        "worker_name": "Test Worker"
    })
    print(f"   Created note: {note_id}")

    obs_id = brain.store({
        "type": "observation",
        "description": "Foundation crack observed",
        "location": "Building A, East Wall",
        "severity": "warning"
    })
    print(f"   Created observation: {obs_id}")

    # Test retrieve
    print("\n2. Testing retrieve...")
    pending = brain.get_pending()
    print(f"   Pending items: {len(pending)}")

    count = brain.get_pending_count()
    print(f"   Pending count: {count}")

    # Test mark synced
    print("\n3. Testing mark synced...")
    brain.mark_synced(note_id)
    new_count = brain.get_pending_count()
    print(f"   Pending after sync: {new_count}")

    # Test stats
    print("\n4. Testing stats...")
    stats = brain.get_stats()
    print(f"   Stats: {json.dumps(stats, indent=2)}")

    storage = brain.get_storage_usage()
    print(f"   Storage: {storage}")

    print("\n=== Tests Complete ===\n")


if __name__ == "__main__":
    test_local_brain()
