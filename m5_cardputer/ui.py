"""
ALFRED Edge UI - Display and Keyboard Interface
=================================================
User interface for M5 Cardputer with 240x135 LCD display
and built-in QWERTY keyboard.

Hardware:
- Display: 240x135 ST7789 LCD (1.14 inch)
- Keyboard: 56-key QWERTY keyboard matrix
- RGB LED: Status indicator

Author: Daniel J. Rita (BATDAN)
"""

import time
import gc

# M5 Cardputer hardware imports
try:
    from machine import Pin, SPI
    import st7789
    import vga1_16x16 as font
    M5_DISPLAY_AVAILABLE = True
except ImportError:
    M5_DISPLAY_AVAILABLE = False
    print("[WARN] Display libraries not found - text mode")

# Keyboard matrix
try:
    from machine import Pin
    M5_KEYBOARD_AVAILABLE = True
except ImportError:
    M5_KEYBOARD_AVAILABLE = False

# Colors (RGB565)
class Colors:
    BLACK = 0x0000
    WHITE = 0xFFFF
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    CYAN = 0x07FF
    YELLOW = 0xFFE0
    ORANGE = 0xFD20
    ALFRED_BLUE = 0x2D7F  # Alfred's signature blue
    DARK_GRAY = 0x4208
    LIGHT_GRAY = 0xCE79


class AlfredUI:
    """
    User interface for ALFRED Edge on M5 Cardputer.

    Provides:
    - Menu display
    - Text input with keyboard
    - Status messages
    - Alerts and confirmations
    - Selection lists
    """

    # Display dimensions
    WIDTH = 240
    HEIGHT = 135

    # Layout
    HEADER_HEIGHT = 20
    FOOTER_HEIGHT = 16
    CONTENT_HEIGHT = HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT

    def __init__(self):
        """Initialize UI components."""
        self.display = None
        self.keyboard = None
        self._input_buffer = ""
        self._cursor_visible = True
        self._last_key = None
        self._key_held = False

        # Keyboard matrix pins (M5 Cardputer specific)
        self.row_pins = [1, 2, 3, 4, 5, 6, 7]
        self.col_pins = [8, 9, 10, 11, 12, 13, 14, 15]

        # Key mapping for M5 Cardputer
        self.keymap = self._build_keymap()

        print("[INFO] UI initialized")

    def _build_keymap(self):
        """Build keyboard matrix keymap."""
        # M5 Cardputer keyboard layout (simplified)
        # Actual layout may vary - adjust based on hardware
        return {
            # Row 0: Function keys + numbers
            (0, 0): 'ESC', (0, 1): '1', (0, 2): '2', (0, 3): '3',
            (0, 4): '4', (0, 5): '5', (0, 6): '6', (0, 7): '7',

            # Row 1: More numbers + special
            (1, 0): '8', (1, 1): '9', (1, 2): '0', (1, 3): '-',
            (1, 4): '=', (1, 5): 'BKSP', (1, 6): 'TAB', (1, 7): 'q',

            # Row 2: QWERTY row
            (2, 0): 'w', (2, 1): 'e', (2, 2): 'r', (2, 3): 't',
            (2, 4): 'y', (2, 5): 'u', (2, 6): 'i', (2, 7): 'o',

            # Row 3: More letters
            (3, 0): 'p', (3, 1): '[', (3, 2): ']', (3, 3): 'a',
            (3, 4): 's', (3, 5): 'd', (3, 6): 'f', (3, 7): 'g',

            # Row 4: ASDF row
            (4, 0): 'h', (4, 1): 'j', (4, 2): 'k', (4, 3): 'l',
            (4, 4): ';', (4, 5): "'", (4, 6): 'ENTER', (4, 7): 'SHIFT',

            # Row 5: ZXCV row
            (5, 0): 'z', (5, 1): 'x', (5, 2): 'c', (5, 3): 'v',
            (5, 4): 'b', (5, 5): 'n', (5, 6): 'm', (5, 7): ',',

            # Row 6: Bottom row
            (6, 0): '.', (6, 1): '/', (6, 2): 'CTRL', (6, 3): 'ALT',
            (6, 4): ' ', (6, 5): 'FN', (6, 6): 'UP', (6, 7): 'DOWN',
        }

    # ========================================
    # Hardware Initialization
    # ========================================

    def init_display(self):
        """Initialize ST7789 display."""
        if not M5_DISPLAY_AVAILABLE:
            print("[WARN] Display not available - text mode")
            return

        try:
            # M5 Cardputer display pins
            spi = SPI(1, baudrate=40000000, sck=Pin(36), mosi=Pin(35))

            # The ST7789 driver uses physical dimensions then rotation
            # M5 Cardputer is physically 135x240, used in landscape (rotation 1)
            self.display = st7789.ST7789(
                spi,
                135,
                240,
                reset=Pin(34, Pin.OUT),
                cs=Pin(37, Pin.OUT),
                dc=Pin(38, Pin.OUT),
                backlight=Pin(33, Pin.OUT),
                rotation=1
            )

            self.clear()
            print("[OK] Display initialized")

        except Exception as e:
            print(f"[ERROR] Display init failed: {e}")
            self.display = None

    def init_keyboard(self):
        """Initialize keyboard matrix."""
        if not M5_KEYBOARD_AVAILABLE:
            print("[WARN] Keyboard not available")
            return

        try:
            # Setup row pins as outputs
            self.rows = [Pin(p, Pin.OUT, value=1) for p in self.row_pins]

            # Setup column pins as inputs with pull-up
            self.cols = [Pin(p, Pin.IN, Pin.PULL_UP) for p in self.col_pins]

            print("[OK] Keyboard initialized")

        except Exception as e:
            print(f"[ERROR] Keyboard init failed: {e}")
            self.rows = None
            self.cols = None

    # ========================================
    # Display Operations
    # ========================================

    def clear(self, color=Colors.BLACK):
        """Clear display."""
        if self.display:
            self.display.fill(color)
        else:
            print("\n" + "="*40)

    def _draw_text(self, text, x, y, color=Colors.WHITE, bg=Colors.BLACK):
        """Draw text at position."""
        if self.display and font:
            self.display.text(font, text, x, y, color, bg)
        else:
            print(f"  {text}")

    def _draw_rect(self, x, y, w, h, color):
        """Draw filled rectangle."""
        if self.display:
            self.display.fill_rect(x, y, w, h, color)

    def _draw_header(self, title, status=""):
        """Draw header bar."""
        self._draw_rect(0, 0, self.WIDTH, self.HEADER_HEIGHT, Colors.ALFRED_BLUE)
        self._draw_text(title[:15], 4, 2, Colors.WHITE, Colors.ALFRED_BLUE)

        if status:
            # Right-aligned status
            status_x = self.WIDTH - (len(status) * 8) - 4
            self._draw_text(status[:8], status_x, 2, Colors.WHITE, Colors.ALFRED_BLUE)

    def _draw_footer(self, text):
        """Draw footer bar."""
        y = self.HEIGHT - self.FOOTER_HEIGHT
        self._draw_rect(0, y, self.WIDTH, self.FOOTER_HEIGHT, Colors.DARK_GRAY)
        self._draw_text(text[:30], 4, y + 2, Colors.LIGHT_GRAY, Colors.DARK_GRAY)

    # ========================================
    # UI Components
    # ========================================

    def show_menu(self, title, items, footer=""):
        """
        Display a menu with selectable items.

        Args:
            title: Menu title
            items: List of menu items
            footer: Footer text
        """
        self.clear()
        self._draw_header(title, "ALFRED")

        # Draw menu items
        y = self.HEADER_HEIGHT + 4
        for i, item in enumerate(items[:7]):  # Max 7 items visible
            self._draw_text(item[:28], 8, y, Colors.WHITE)
            y += 16

        self._draw_footer(footer if footer else "Press key to select")

        if not self.display:
            print("-"*40)
            for item in items:
                print(f"  {item}")
            print(f"\n  [{footer}]")
            print("="*40)

    def show_message(self, message, color=Colors.WHITE):
        """
        Display a simple message.

        Args:
            message: Message text
            color: Text color
        """
        self.clear()
        self._draw_header("ALFRED Edge")

        # Center message
        y = self.HEIGHT // 2 - 8
        x = max(0, (self.WIDTH - len(message) * 8) // 2)
        self._draw_text(message[:28], x, y, color)

        if not self.display:
            print(f"\n  >>> {message}")

    def show_status(self, status):
        """
        Show status message in footer area.

        Args:
            status: Status text
        """
        self._draw_footer(status)

        if not self.display:
            print(f"  [STATUS] {status}")

    def show_error(self, error):
        """
        Show error message.

        Args:
            error: Error text
        """
        self._draw_rect(0, self.HEIGHT - 32, self.WIDTH, 32, Colors.RED)
        self._draw_text("ERROR:", 4, self.HEIGHT - 30, Colors.WHITE, Colors.RED)
        self._draw_text(error[:28], 4, self.HEIGHT - 14, Colors.WHITE, Colors.RED)

        if not self.display:
            print(f"  [ERROR] {error}")

    def show_alert(self, message):
        """
        Show important alert with visual highlight.

        Args:
            message: Alert text
        """
        self.clear(Colors.ORANGE)
        self._draw_rect(10, 30, self.WIDTH - 20, self.HEIGHT - 60, Colors.BLACK)

        # Alert icon (exclamation)
        self._draw_text("!", 20, 50, Colors.ORANGE)
        self._draw_text("ALERT", 40, 50, Colors.ORANGE)
        self._draw_text(message[:24], 20, 75, Colors.WHITE)

        self._draw_footer("Press any key")

        if not self.display:
            print(f"\n  !!! ALERT: {message} !!!\n")

    def show_input(self, prompt, default=""):
        """
        Show text input screen.

        Args:
            prompt: Input prompt
            default: Default value
        """
        self._input_buffer = default

        self.clear()
        self._draw_header("Input")
        self._draw_text(prompt[:28], 8, self.HEADER_HEIGHT + 8, Colors.CYAN)

        # Input field
        y = self.HEADER_HEIGHT + 32
        self._draw_rect(8, y, self.WIDTH - 16, 24, Colors.DARK_GRAY)
        self._draw_text(self._input_buffer[:26], 12, y + 4, Colors.WHITE, Colors.DARK_GRAY)

        self._draw_footer("ENTER=confirm ESC=cancel")

        if not self.display:
            print(f"\n  {prompt}")
            print(f"  > {self._input_buffer}_")

    def show_list(self, title, items, selected=0):
        """
        Show scrollable list.

        Args:
            title: List title
            items: List items
            selected: Currently selected index
        """
        self.clear()
        self._draw_header(title, f"{selected+1}/{len(items)}")

        # Calculate visible window
        max_visible = 6
        start = max(0, selected - max_visible // 2)
        end = min(len(items), start + max_visible)

        y = self.HEADER_HEIGHT + 4
        for i in range(start, end):
            item = items[i]
            if i == selected:
                self._draw_rect(4, y - 2, self.WIDTH - 8, 18, Colors.ALFRED_BLUE)
                self._draw_text(f"> {item[:24]}", 8, y, Colors.WHITE, Colors.ALFRED_BLUE)
            else:
                self._draw_text(f"  {item[:24]}", 8, y, Colors.LIGHT_GRAY)
            y += 18

        self._draw_footer("UP/DOWN=nav ENTER=select")

    def show_selection(self, title, options, selected=0):
        """
        Show selection dialog and wait for choice.

        Args:
            title: Dialog title
            options: List of options
            selected: Initial selection

        Returns:
            int: Selected index (-1 if cancelled)
        """
        while True:
            self.show_list(title, options, selected)

            key = self.wait_for_key()

            if key == 'UP' and selected > 0:
                selected -= 1
            elif key == 'DOWN' and selected < len(options) - 1:
                selected += 1
            elif key == 'ENTER':
                return selected
            elif key == 'ESC':
                return -1

    def confirm(self):
        """
        Show confirmation dialog.

        Returns:
            bool: True if confirmed
        """
        self._draw_footer("ENTER=Yes ESC=No")

        while True:
            key = self.wait_for_key()
            if key == 'ENTER':
                return True
            elif key == 'ESC':
                return False

    # ========================================
    # Keyboard Input
    # ========================================

    def check_key(self):
        """
        Check for key press (non-blocking).

        Returns:
            str or None: Key pressed or None
        """
        if not self.rows or not self.cols:
            return self._check_key_fallback()

        # Scan keyboard matrix
        for row_idx, row_pin in enumerate(self.rows):
            # Set current row low
            row_pin.value(0)

            # Check each column
            for col_idx, col_pin in enumerate(self.cols):
                if col_pin.value() == 0:  # Key pressed
                    row_pin.value(1)

                    # Debounce
                    time.sleep_ms(20)

                    key = self.keymap.get((row_idx, col_idx))
                    if key and key != self._last_key:
                        self._last_key = key
                        return key

            row_pin.value(1)

        # No key pressed
        if self._last_key:
            self._last_key = None

        return None

    def _check_key_fallback(self):
        """Fallback key check for non-M5 environments."""
        # In simulation mode, use stdin if available
        try:
            import select
            import sys

            if select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                return key
        except:
            pass
        return None

    def wait_for_key(self):
        """
        Wait for key press (blocking).

        Returns:
            str: Key pressed
        """
        while True:
            key = self.check_key()
            if key:
                return key
            time.sleep(0.05)

    def get_text_input(self):
        """
        Get text input from keyboard.

        Returns:
            str: Entered text (empty if cancelled)
        """
        shift_active = False

        while True:
            key = self.wait_for_key()

            if key == 'ENTER':
                return self._input_buffer
            elif key == 'ESC':
                return ""
            elif key == 'BKSP':
                if self._input_buffer:
                    self._input_buffer = self._input_buffer[:-1]
            elif key == 'SHIFT':
                shift_active = not shift_active
            elif len(key) == 1:
                # Regular character
                if shift_active:
                    key = key.upper()
                if len(self._input_buffer) < 100:  # Max length
                    self._input_buffer += key
            else:
                continue  # Ignore other special keys

            # Update display
            self._update_input_display()

    def _update_input_display(self):
        """Update input field on display."""
        y = self.HEADER_HEIGHT + 32
        self._draw_rect(8, y, self.WIDTH - 16, 24, Colors.DARK_GRAY)

        # Show last 26 chars with cursor
        visible = self._input_buffer[-26:]
        cursor = "_" if self._cursor_visible else " "
        self._draw_text(visible + cursor, 12, y + 4, Colors.WHITE, Colors.DARK_GRAY)

        # Toggle cursor
        self._cursor_visible = not self._cursor_visible

    # ========================================
    # Utility
    # ========================================

    def set_brightness(self, level):
        """
        Set display brightness.

        Args:
            level: 0-100
        """
        # M5 Cardputer uses backlight PWM
        try:
            from machine import PWM
            bl = PWM(Pin(38), freq=1000, duty=int(level * 10.23))
            print(f"[OK] Brightness set to {level}%")
        except:
            pass

    def sleep_display(self):
        """Turn off display to save power."""
        if self.display:
            self.set_brightness(0)
            print("[OK] Display sleeping")

    def wake_display(self):
        """Wake display from sleep."""
        if self.display:
            self.set_brightness(50)
            print("[OK] Display awake")


# ========================================
# Test / Debug
# ========================================

def test_ui():
    """Test UI components."""
    print("\n=== Testing ALFRED Edge UI ===\n")

    ui = AlfredUI()

    # Test menu
    print("1. Testing menu display...")
    ui.show_menu("Main Menu", [
        "1. Add Note",
        "2. Voice Note",
        "3. Observation",
        "4. Settings",
        "0. Exit"
    ], footer="Select option")

    time.sleep(1)

    # Test message
    print("\n2. Testing message...")
    ui.show_message("Welcome to ALFRED Edge")

    time.sleep(1)

    # Test alert
    print("\n3. Testing alert...")
    ui.show_alert("Critical: Safety issue!")

    time.sleep(1)

    # Test input
    print("\n4. Testing input...")
    ui.show_input("Enter your name:", "Worker")

    print("\n=== UI Tests Complete ===\n")


if __name__ == "__main__":
    test_ui()
