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

        # Keyboard matrix pins (M5 Cardputer uses 74HC138 decoder for rows)
        self.row_addr_pins = [8, 9, 11]  # A0, A1, A2
        self.col_pins = [13, 15, 3, 4, 5, 6, 7] # C0, C1, C2, C3, C4, C5, C6

        # Key mapping for M5 Cardputer 8x7 matrix
        self.keymap = self._build_keymap()

        print("[INFO] UI initialized")

    def _build_keymap(self):
        """Build keyboard matrix keymap for 8x7 decoder matrix."""
        # Based on M5 Cardputer physical layout and 74HC138 scan rows
        return {
            # Scan Row 0 (Odd Col physical row 3)
            (0, 0): 'Ctrl', (0, 1): 'Opt', (0, 2): 'Alt', (0, 3): 'z', (0, 4): 'x', (0, 5): 'c', (0, 6): 'v',
            # Scan Row 1 (Odd Col physical row 2)
            (1, 0): 'SHIFT', (1, 1): 'a', (1, 2): 's', (1, 3): 'd', (1, 4): 'f', (1, 5): 'g', (1, 6): 'h',
            # Scan Row 2 (Odd Col physical row 1)
            (2, 0): 'q', (2, 1): 'w', (2, 2): 'e', (2, 3): 'r', (2, 4): 't', (2, 5): 'y', (2, 6): 'u',
            # Scan Row 3 (Odd Col physical row 0)
            (3, 0): '1', (3, 1): '3', (3, 2): '5', (3, 3): '7', (3, 4): '9', (3, 5): '-', (3, 6): 'BS',
            # Scan Row 4 (Even Col physical row 3)
            (4, 0): 'b', (4, 1): 'n', (4, 2): 'm', (4, 3): ',', (4, 4): '.', (4, 5): '/', (4, 6): ' ',
            # Scan Row 5 (Even Col physical row 2)
            (5, 0): 'j', (5, 1): 'k', (5, 2): 'l', (5, 3): ';', (5, 4): "'", (5, 5): 'ENTER', (5, 6): 'FN',
            # Scan Row 6 (Even Col physical row 1)
            (6, 0): 'i', (6, 1): 'o', (6, 2): 'p', (6, 3): '[', (6, 4): ']', (6, 5): '\\', (6, 6): 'TAB',
            # Scan Row 7 (Even Col physical row 0)
            (7, 0): '`', (7, 1): '2', (7, 2): '4', (7, 3): '6', (7, 4): '8', (7, 5): '0', (7, 6): '=',
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
            # Verified M5 Cardputer display pins
            spi = SPI(1, baudrate=20000000, polarity=1, phase=1, sck=Pin(36), mosi=Pin(35))

            # Hardware Reset
            rst_pin = Pin(33, Pin.OUT)
            rst_pin.value(0)
            time.sleep(0.1)
            rst_pin.value(1)
            time.sleep(0.1)

            # Backlight control
            self.backlight = Pin(38, Pin.OUT)
            self.backlight.value(1)

            # The ST7789 driver initialization
            self.display = st7789.ST7789(
                spi,
                135,
                240,
                reset=Pin(33, Pin.OUT),
                cs=Pin(37, Pin.OUT),
                dc=Pin(34, Pin.OUT),
                rotation=1
            )

            self.display.init(self.display.init_cmds)
            self.display.inversion_mode(True)
            self.clear()
            print("[OK] Display initialized")

        except Exception as e:
            print(f"[ERROR] Display init failed: {e}")
            self.display = None

    def init_keyboard(self):
        """Initialize keyboard matrix scanning."""
        try:
            # Setup row address pins as outputs
            self.rows_addr = [Pin(p, Pin.OUT, value=1) for p in self.row_addr_pins]

            # Setup column pins as inputs with pull-up
            self.cols = [Pin(p, Pin.IN, Pin.PULL_UP) for p in self.col_pins]

            print("[OK] Keyboard initialized")

        except Exception as e:
            print(f"[ERROR] Keyboard init failed: {e}")
            self.rows_addr = None
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
        y = self.HEADER_HEIGHT + 2
        for i, item in enumerate(items[:10]):  # Show up to 10 items
            self._draw_text(item[:28], 8, y, Colors.WHITE)
            y += 10  # Final squeeze to fit 0. Exit

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
        Check for key press (non-blocking) using 74HC138 decoder.
        """
        if not self.rows_addr or not self.cols:
            return self._check_key_fallback()

        # Scan each of the 8 decoder rows
        for row_idx in range(8):
            # Set address on A0, A1, A2 (pins 8, 9, 11)
            self.rows_addr[0].value(row_idx & 0x01)
            self.rows_addr[1].value((row_idx >> 1) & 0x01)
            self.rows_addr[2].value((row_idx >> 2) & 0x01)

            # Check each column
            for col_idx, col_pin in enumerate(self.cols):
                if col_pin.value() == 0:  # Key pressed
                    # Debounce
                    time.sleep_ms(10)
                    if col_pin.value() == 0:
                        key = self.keymap.get((row_idx, col_idx))
                        if key and key != self._last_key:
                            self._last_key = key
                            return key

        # No key pressed
        if self._last_key:
            # Simple debounce for release
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
