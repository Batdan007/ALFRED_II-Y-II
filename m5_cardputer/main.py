"""
ALFRED Edge - M5 Cardputer Edition
===================================
Standalone pocket AI assistant for construction workers.
Collects notes, voice recordings, and observations offline.
Auto-syncs to main ALFRED brain when WiFi is available.

Hardware: M5Stack Cardputer (ESP32-S3)
Memory: 8MB PSRAM, 16MB Flash
Display: 240x135 ST7789 LCD
Input: Full QWERTY keyboard
Audio: Built-in microphone and speaker

Author: Daniel J. Rita (BATDAN)
Version: 1.0.0
"""

import gc
import time
import json
import machine
from machine import Pin, SPI, I2S, Timer

# M5 Cardputer specific imports
try:
    import st7789
    M5_LCD_AVAILABLE = True
except ImportError:
    M5_LCD_AVAILABLE = False

try:
    from m5stack import Cardputer
    M5_STACK_AVAILABLE = True
except ImportError:
    M5_STACK_AVAILABLE = False
    print("[WARN] M5Stack libraries not found")

# Local modules
from local_brain import LocalBrain
from sync_client import SyncClient
from ui import AlfredUI
from gsm_handler import GSMHandler

# Configuration
CONFIG = {
    "device_name": "ALFRED_EDGE_001",
    "device_type": "m5_cardputer",
    "worker_id": None,  # Set during setup
    "worker_name": None,
    "sync_server": "http://192.168.1.100:8765",  # ALFRED_UBX sync server
    "wifi_ssid": None,
    "wifi_password": None,
    "auto_sync_interval": 300,  # 5 minutes when connected
    "voice_enabled": True,
    "display_timeout": 30,  # seconds
    "battery_save_mode": True
}

class AlfredEdge:
    """
    ALFRED Edge - Pocket AI Assistant for Construction Workers

    Features:
    - Offline note taking with timestamps and categories
    - Voice recording and transcription queue
    - Task tracking and site observations
    - Auto-sync to main ALFRED brain via WiFi
    - Multi-worker support (each Cardputer is a node)
    """

    def __init__(self):
        print("\n" + "="*40)
        print("  ALFRED EDGE - M5 Cardputer")
        print("  The AI That Never Forgets")
        print("="*40)

        # Initialize components
        self.brain = LocalBrain()
        self.ui = AlfredUI()
        self.sync = SyncClient(CONFIG["sync_server"])
        self.gsm = GSMHandler()

        # State
        self.running = True
        self.wifi_connected = False
        self.last_sync = 0
        self.pending_sync_count = 0

        # Load config from flash
        self._load_config()

        # Initialize hardware
        self._init_hardware()

        print("[OK] ALFRED Edge initialized")
        print(f"[INFO] Device: {CONFIG['device_name']}")
        print(f"[INFO] Worker: {CONFIG.get('worker_name', 'Not configured')}")

    def _load_config(self):
        """Load configuration from flash storage."""
        try:
            with open('/config.json', 'r') as f:
                saved_config = json.load(f)
                CONFIG.update(saved_config)
                print("[OK] Configuration loaded")
        except:
            print("[INFO] No saved config, using defaults")

    def _save_config(self):
        """Save configuration to flash storage."""
        try:
            with open('/config.json', 'w') as f:
                json.dump(CONFIG, f)
            print("[OK] Configuration saved")
        except Exception as e:
            print(f"[ERROR] Could not save config: {e}")

    def _init_hardware(self):
        """Initialize M5 Cardputer hardware."""
        if not M5_LCD_AVAILABLE and not M5_STACK_AVAILABLE:
            print("[WARN] Hardware simulation mode")
            return

        try:
            # Initialize display if available
            if M5_LCD_AVAILABLE or self.ui.M5_DISPLAY_AVAILABLE:
                self.ui.init_display()

            # Initialize keyboard
            self.ui.init_keyboard()

            # Initialize audio (microphone)
            if CONFIG["voice_enabled"]:
                self._init_audio()

            # Initialize WiFi (don't connect yet)
            self._init_wifi()

            print("[OK] Hardware initialized")
        except Exception as e:
            print(f"[ERROR] Hardware init failed: {e}")

    def _init_audio(self):
        """Initialize I2S audio for voice recording."""
        try:
            # M5 Cardputer I2S configuration
            self.i2s = I2S(
                0,
                sck=Pin(41),
                ws=Pin(43),
                sd=Pin(42),
                mode=I2S.RX,
                bits=16,
                format=I2S.MONO,
                rate=16000,
                ibuf=4096
            )
            print("[OK] Audio initialized")
        except Exception as e:
            print(f"[WARN] Audio init failed: {e}")
            CONFIG["voice_enabled"] = False

    def _init_wifi(self):
        """Initialize WiFi interface (don't connect yet)."""
        try:
            import network
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            print("[OK] WiFi interface ready")
        except Exception as e:
            print(f"[WARN] WiFi init failed: {e}")
            self.wlan = None

    def connect_wifi(self):
        """Attempt to connect to configured WiFi network."""
        if not self.wlan:
            return False

        if not CONFIG.get("wifi_ssid"):
            return False

        try:
            if self.wlan.isconnected():
                self.wifi_connected = True
                return True

            print(f"[INFO] Connecting to {CONFIG['wifi_ssid']}...")
            self.wlan.connect(CONFIG["wifi_ssid"], CONFIG.get("wifi_password", ""))

            # Wait up to 10 seconds
            for _ in range(20):
                if self.wlan.isconnected():
                    self.wifi_connected = True
                    ip = self.wlan.ifconfig()[0]
                    print(f"[OK] Connected: {ip}")
                    self.ui.show_status(f"WiFi: {ip}")
                    return True
                time.sleep(0.5)

            print("[WARN] WiFi connection timeout")
            return False
        except Exception as e:
            print(f"[ERROR] WiFi connect failed: {e}")
            return False

    def disconnect_wifi(self):
        """Disconnect from WiFi to save power."""
        if self.wlan and self.wlan.isconnected():
            self.wlan.disconnect()
            self.wifi_connected = False
            print("[OK] WiFi disconnected")

    # ========================================
    # Note Taking
    # ========================================

    def add_note(self, content, category="general"):
        """
        Add a new note to local storage.

        Categories:
        - general: General observations
        - safety: Safety concerns
        - progress: Work progress updates
        - issue: Problems/blockers
        - material: Material/supply notes
        - task: Task assignments
        """
        note = {
            "type": "note",
            "content": content,
            "category": category,
            "worker_id": CONFIG.get("worker_id"),
            "worker_name": CONFIG.get("worker_name"),
            "device": CONFIG["device_name"],
            "timestamp": time.time(),
            "synced": False
        }

        self.brain.store(note)
        self.pending_sync_count = self.brain.get_pending_count()

        print(f"[OK] Note saved: {content[:30]}...")
        self.ui.show_status(f"Note saved ({self.pending_sync_count} pending)")

        return True

    def add_voice_note(self, duration=10):
        """
        Record a voice note for later transcription.

        Voice notes are stored locally and transcribed
        when synced to the main ALFRED brain.
        """
        if not CONFIG["voice_enabled"]:
            print("[WARN] Voice not available")
            self.ui.show_error("Voice disabled")
            return False

        try:
            self.ui.show_status("Recording...")
            print(f"[INFO] Recording {duration}s voice note...")

            # Record audio
            audio_data = bytearray(16000 * 2 * duration)  # 16kHz, 16-bit, mono
            self.i2s.readinto(audio_data)

            # Store as base64 for sync
            import ubinascii
            audio_b64 = ubinascii.b2a_base64(audio_data).decode()

            voice_note = {
                "type": "voice_note",
                "audio_data": audio_b64,
                "duration": duration,
                "format": "pcm_16k_16bit_mono",
                "worker_id": CONFIG.get("worker_id"),
                "worker_name": CONFIG.get("worker_name"),
                "device": CONFIG["device_name"],
                "timestamp": time.time(),
                "synced": False,
                "transcribed": False
            }

            self.brain.store(voice_note)
            self.pending_sync_count = self.brain.get_pending_count()

            print("[OK] Voice note saved")
            self.ui.show_status(f"Voice saved ({self.pending_sync_count} pending)")

            return True
        except Exception as e:
            print(f"[ERROR] Voice recording failed: {e}")
            self.ui.show_error("Recording failed")
            return False

    def add_observation(self, description, location="", severity="info"):
        """
        Log a site observation.

        Severity levels:
        - info: General observation
        - warning: Potential concern
        - critical: Requires immediate attention
        """
        observation = {
            "type": "observation",
            "description": description,
            "location": location,
            "severity": severity,
            "worker_id": CONFIG.get("worker_id"),
            "worker_name": CONFIG.get("worker_name"),
            "device": CONFIG["device_name"],
            "timestamp": time.time(),
            "synced": False
        }

        self.brain.store(observation)
        self.pending_sync_count = self.brain.get_pending_count()

        # Critical observations get highlighted
        if severity == "critical":
            self.ui.show_alert(f"CRITICAL: {description[:20]}...")
        else:
            self.ui.show_status(f"Observation logged")

        return True

    def add_task_update(self, task_id, status, notes=""):
        """
        Update a task status.

        Status values:
        - started: Work begun
        - in_progress: Actively working
        - blocked: Cannot continue
        - completed: Task finished
        - verified: Quality checked
        """
        update = {
            "type": "task_update",
            "task_id": task_id,
            "status": status,
            "notes": notes,
            "worker_id": CONFIG.get("worker_id"),
            "worker_name": CONFIG.get("worker_name"),
            "device": CONFIG["device_name"],
            "timestamp": time.time(),
            "synced": False
        }

        self.brain.store(update)
        self.pending_sync_count = self.brain.get_pending_count()

        self.ui.show_status(f"Task {task_id}: {status}")

        return True

    # ========================================
    # Sync Operations
    # ========================================

    def sync_to_server(self):
        """
        Sync all pending data to ALFRED_UBX server.

        This is called automatically when WiFi is available,
        or can be triggered manually.
        """
        if not self.wifi_connected:
            if not self.connect_wifi():
                print("[WARN] Cannot sync - no WiFi")
                return False

        try:
            self.ui.show_status("Syncing...")
            print("[INFO] Starting sync to ALFRED server...")

            # Get all unsynced items
            pending = self.brain.get_pending()

            if not pending:
                print("[INFO] Nothing to sync")
                self.ui.show_status("Already synced")
                return True

            print(f"[INFO] Syncing {len(pending)} items...")

            # Sync to server
            result = self.sync.upload(pending)

            if result["success"]:
                # Mark items as synced
                for item in pending:
                    self.brain.mark_synced(item["id"])

                self.last_sync = time.time()
                self.pending_sync_count = 0

                print(f"[OK] Synced {len(pending)} items")
                self.ui.show_status(f"Synced {len(pending)} items")

                # Check for any tasks/messages from server
                if result.get("tasks"):
                    self._process_server_tasks(result["tasks"])

                return True
            else:
                print(f"[ERROR] Sync failed: {result.get('error')}")
                self.ui.show_error("Sync failed")
                return False

        except Exception as e:
            print(f"[ERROR] Sync error: {e}")
            self.ui.show_error("Sync error")
            return False

    def _process_server_tasks(self, tasks):
        """Process any tasks sent from the main ALFRED server."""
        for task in tasks:
            print(f"[INFO] New task: {task.get('title', 'Unknown')}")
            self.brain.store_task(task)

        if tasks:
            self.ui.show_alert(f"{len(tasks)} new task(s)!")

    # ========================================
    # UI / Main Loop
    # ========================================

    def show_menu(self):
        """Display main menu on screen."""
        menu_items = [
            "1. Add Note",
            "2. Voice Note",
            "3. Observation",
            "4. Task Update",
            "5. View Pending",
            "6. Sync Now",
            "7. Settings",
            "8. GSM Receiver",
            "0. Exit"
        ]

        self.ui.show_menu("ALFRED Edge", menu_items,
                         footer=f"Pending: {self.pending_sync_count}")

    def handle_input(self, key):
        """Handle keyboard input."""
        if key == '1':
            self._note_input_mode()
        elif key == '2':
            self.add_voice_note()
        elif key == '3':
            self._observation_input_mode()
        elif key == '4':
            self._task_update_mode()
        elif key == '5':
            self._view_pending()
        elif key == '6':
            self.sync_to_server()
        elif key == '7':
            self._settings_menu()
        elif key == '8':
            self.gsm.listen_and_process(self.ui)
        elif key == '0':
            self.running = False
        elif key == 'ESC':
            self.show_menu()

    def _note_input_mode(self):
        """Enter note input mode."""
        self.ui.show_input("Enter note:", "")
        content = self.ui.get_text_input()
        if content:
            # Show category selection
            categories = ["general", "safety", "progress", "issue", "material", "task"]
            cat_idx = self.ui.show_selection("Category:", categories)
            if cat_idx >= 0:
                self.add_note(content, categories[cat_idx])
        self.show_menu()

    def _observation_input_mode(self):
        """Enter observation input mode."""
        self.ui.show_input("Description:", "")
        desc = self.ui.get_text_input()
        if desc:
            self.ui.show_input("Location:", "")
            loc = self.ui.get_text_input()
            severities = ["info", "warning", "critical"]
            sev_idx = self.ui.show_selection("Severity:", severities)
            if sev_idx >= 0:
                self.add_observation(desc, loc, severities[sev_idx])
        self.show_menu()

    def _task_update_mode(self):
        """Enter task update mode."""
        # Get available tasks from local storage
        tasks = self.brain.get_tasks()
        if not tasks:
            self.ui.show_message("No tasks assigned")
            time.sleep(2)
            self.show_menu()
            return

        # Select task
        task_names = [t["title"][:20] for t in tasks]
        task_idx = self.ui.show_selection("Select task:", task_names)
        if task_idx < 0:
            self.show_menu()
            return

        task = tasks[task_idx]

        # Select status
        statuses = ["started", "in_progress", "blocked", "completed", "verified"]
        status_idx = self.ui.show_selection("Status:", statuses)
        if status_idx < 0:
            self.show_menu()
            return

        # Optional notes
        self.ui.show_input("Notes (optional):", "")
        notes = self.ui.get_text_input()

        self.add_task_update(task["id"], statuses[status_idx], notes)
        self.show_menu()

    def _view_pending(self):
        """View pending items waiting for sync."""
        pending = self.brain.get_pending()

        if not pending:
            self.ui.show_message("All synced!")
            time.sleep(2)
            self.show_menu()
            return

        # Format items for display
        items = []
        for p in pending[:10]:  # Show max 10
            ptype = p.get("type", "unknown")[:4]
            preview = ""
            if "content" in p:
                preview = p["content"][:15]
            elif "description" in p:
                preview = p["description"][:15]
            items.append(f"[{ptype}] {preview}...")

        self.ui.show_list(f"Pending ({len(pending)})", items)
        self.ui.wait_for_key()
        self.show_menu()

    def _settings_menu(self):
        """Show settings menu."""
        settings_items = [
            f"1. Worker: {CONFIG.get('worker_name', 'Not set')}",
            f"2. WiFi: {CONFIG.get('wifi_ssid', 'Not set')}",
            f"3. Server: {CONFIG.get('sync_server', 'Not set')[:20]}",
            f"4. Voice: {'On' if CONFIG['voice_enabled'] else 'Off'}",
            "5. Clear Local Data",
            "0. Back"
        ]

        self.ui.show_menu("Settings", settings_items)
        key = self.ui.wait_for_key()

        if key == '1':
            self.ui.show_input("Worker name:", CONFIG.get("worker_name", ""))
            name = self.ui.get_text_input()
            if name:
                CONFIG["worker_name"] = name
                CONFIG["worker_id"] = name.lower().replace(" ", "_")
                self._save_config()
        elif key == '2':
            self.ui.show_input("WiFi SSID:", CONFIG.get("wifi_ssid", ""))
            ssid = self.ui.get_text_input()
            if ssid:
                CONFIG["wifi_ssid"] = ssid
                self.ui.show_input("WiFi Password:", "")
                pwd = self.ui.get_text_input()
                CONFIG["wifi_password"] = pwd
                self._save_config()
        elif key == '3':
            self.ui.show_input("Server URL:", CONFIG.get("sync_server", ""))
            url = self.ui.get_text_input()
            if url:
                CONFIG["sync_server"] = url
                self._save_config()
        elif key == '4':
            CONFIG["voice_enabled"] = not CONFIG["voice_enabled"]
            self._save_config()
        elif key == '5':
            self.ui.show_message("Clear all local data?")
            if self.ui.confirm():
                self.brain.clear_all()
                self.ui.show_message("Data cleared")
                time.sleep(1)

        self.show_menu()

    def run(self):
        """Main application loop."""
        print("[INFO] Starting ALFRED Edge main loop...")
        self.show_menu()

        # Auto-sync timer
        sync_timer = time.time()

        while self.running:
            try:
                # Check for keyboard input
                key = self.ui.check_key()
                if key:
                    self.handle_input(key)

                # Auto-sync check (every 5 minutes if connected)
                if self.wifi_connected and CONFIG.get("auto_sync_interval"):
                    if time.time() - sync_timer > CONFIG["auto_sync_interval"]:
                        self.sync_to_server()
                        sync_timer = time.time()

                # Try to connect WiFi periodically if not connected
                if not self.wifi_connected:
                    if time.time() - sync_timer > 60:  # Every minute
                        self.connect_wifi()
                        if self.wifi_connected:
                            self.sync_to_server()
                        sync_timer = time.time()

                # Memory management
                gc.collect()

                # Small delay to prevent CPU hogging
                time.sleep(0.05)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Main loop error: {e}")
                time.sleep(1)

        # Cleanup
        print("[INFO] Shutting down ALFRED Edge...")
        self.disconnect_wifi()
        self.ui.show_message("Goodbye, sir.")
        time.sleep(1)
        self.ui.clear()

# ========================================
# Entry Point
# ========================================

def main():
    """Entry point for ALFRED Edge."""
    try:
        alfred = AlfredEdge()
        alfred.run()
    except Exception as e:
        print(f"[FATAL] ALFRED Edge crashed: {e}")
        import sys
        sys.print_exception(e)

if __name__ == "__main__":
    main()
