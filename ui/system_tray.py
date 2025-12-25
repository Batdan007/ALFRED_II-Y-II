"""
ALFRED System Tray Integration
Provides a system tray icon for easy access and control

Features:
- Quick access to Mission Control
- Memory stats viewer
- Voice toggle
- Quick research mode
- Graceful shutdown

Author: Daniel J Rita (BATDAN)
Part of ALFRED-UBX / BATCOMPUTER AI Ecosystem
"""

import sys
import webbrowser
from pathlib import Path

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw, ImageFont
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


class AlfredSystemTray:
    """System tray icon for ALFRED"""

    def __init__(self, port: int = 8000, brain=None):
        """
        Initialize system tray

        Args:
            port: Web UI port (default: 8000)
            brain: AlfredBrain instance for memory access
        """
        self.port = port
        self.brain = brain
        self.base_url = f"http://localhost:{port}"
        self.icon = None
        self.voice_enabled = True

    def create_icon(self) -> Image.Image:
        """Create Alfred icon for system tray"""
        width = 64
        height = 64

        # Dark purple background
        image = Image.new('RGB', (width, height), color=(26, 15, 46))
        draw = ImageDraw.Draw(image)

        # Draw "A" for Alfred in cyan
        try:
            # Try to use a font
            font = ImageFont.truetype("arial.ttf", 36)
            draw.text((width//2 - 12, height//2 - 22), "A", fill=(0, 255, 170), font=font)
        except:
            # Fallback to default font
            draw.text((width//2 - 15, height//2 - 20), "A", fill=(0, 255, 170))

        # Draw circle border
        draw.ellipse([5, 5, width-5, height-5], outline=(0, 255, 170), width=3)

        return image

    def open_mission_control(self):
        """Open Mission Control in browser"""
        webbrowser.open(self.base_url)

    def open_memory_stats(self):
        """Open memory stats page"""
        webbrowser.open(f"{self.base_url}#memory")

    def open_security_scan(self):
        """Open security scanning interface"""
        webbrowser.open(f"{self.base_url}#security")

    def toggle_voice(self, icon, item):
        """Toggle voice on/off"""
        self.voice_enabled = not self.voice_enabled
        status = "enabled" if self.voice_enabled else "disabled"
        print(f"[Alfred] Voice {status}")

    def show_status(self, icon, item):
        """Show ALFRED status notification"""
        if self.brain:
            stats = self.brain.get_memory_stats()
            message = f"Conversations: {stats.get('total_conversations', 0)}\n"
            message += f"Knowledge: {stats.get('total_knowledge', 0)}\n"
            message += f"Patterns: {stats.get('total_patterns', 0)}"
        else:
            message = "ALFRED is running"

        # Show notification (platform-specific)
        try:
            icon.notify(message, "ALFRED Status")
        except:
            print(f"[Alfred Status]\n{message}")

    def quit_alfred(self, icon, item):
        """Quit Alfred and close tray icon"""
        print("[Alfred] Shutting down...")

        try:
            import psutil
            # Kill related Python processes
            current_pid = os.getpid()
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('alfred' in str(cmd).lower() for cmd in cmdline):
                        if proc.info['pid'] != current_pid:
                            proc.terminate()
                except:
                    pass
        except ImportError:
            pass

        icon.stop()
        sys.exit(0)

    def create_menu(self) -> Menu:
        """Create tray menu"""
        return Menu(
            MenuItem('Mission Control', lambda: self.open_mission_control()),
            MenuItem('Memory Stats', lambda: self.open_memory_stats()),
            MenuItem('Security Scan', lambda: self.open_security_scan()),
            Menu.SEPARATOR,
            MenuItem(
                'Voice',
                self.toggle_voice,
                checked=lambda item: self.voice_enabled
            ),
            MenuItem('Show Status', self.show_status),
            Menu.SEPARATOR,
            MenuItem('Quit Alfred', self.quit_alfred)
        )

    def run(self):
        """Run the system tray icon"""
        if not TRAY_AVAILABLE:
            print("[!] System tray not available. Install: pip install pystray pillow")
            return False

        icon_image = self.create_icon()
        menu = self.create_menu()

        self.icon = Icon(
            'ALFRED',
            icon_image,
            'ALFRED AI Assistant',
            menu
        )

        print("[OK] System tray icon running")
        self.icon.run()
        return True

    def run_detached(self):
        """Run tray icon in a separate thread"""
        if not TRAY_AVAILABLE:
            return False

        import threading
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return True


def create_tray(port: int = 8000, brain=None) -> AlfredSystemTray:
    """Create system tray instance"""
    return AlfredSystemTray(port=port, brain=brain)


def run_tray(port: int = 8000):
    """Run the system tray icon"""
    tray = AlfredSystemTray(port=port)
    tray.run()


if __name__ == '__main__':
    import os

    # Add os import that was missing
    print("=" * 50)
    print("ALFRED System Tray")
    print("=" * 50)

    if not TRAY_AVAILABLE:
        print("\n[ERROR] pystray not installed!")
        print("Run: pip install pystray pillow")
        sys.exit(1)

    run_tray()
