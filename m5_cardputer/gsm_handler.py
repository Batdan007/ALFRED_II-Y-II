"""
ALFRED Edge - GSM Handler
=========================
Handles incoming GSM data via UART.
Ported from GSM Receiver.c (AVR logic).

Logic:
1. Waits for 99 characters from GSM module.
2. Displays "SMS Received".
3. Displays slices of the message on the screen.
"""

import machine
import time
import utime

class GSMHandler:
    def __init__(self, uart_id=1, tx_pin=1, rx_pin=2, baudrate=9600):
        """
        Initialize GSM Handler.
        Default pins are placeholders; change based on hardware connection.
        """
        try:
            self.uart = machine.UART(uart_id, baudrate=baudrate, tx=tx_pin, rx=rx_pin)
            self.uart.init(baudrate, bits=8, parity=None, stop=1)
            print(f"[OK] GSM UART {uart_id} initialized at {baudrate} baud")
        except Exception as e:
            print(f"[ERROR] Could not initialize UART: {e}")
            self.uart = None

        self.buffer = bytearray(100)
        self.count = 0

    def listen_and_process(self, ui):
        """
        Listen for 99 bytes and process them according to ported logic.
        
        Args:
            ui: AlfredUI instance for display output
        """
        if not self.uart:
            return

        print("[INFO] Waiting for GSM data (99 bytes)...")
        self.count = 0
        
        while self.count < 99:
            # Check if user wants to cancel
            key = ui.check_key()
            if key in ['ESC', '0']:
                print("[INFO] GSM listening cancelled by user")
                return

            if self.uart.any():
                data = self.uart.read(1)
                if data:
                    self.buffer[self.count] = data[0]
                    self.count += 1
            utime.sleep_ms(1)

        # Ported logic from GSM Receiver.c
        print("[OK] 99 bytes received. Processing SMS...")
        
        ui.show_message("SMS Received!", color=0x07E0) # GREEN
        time.sleep_ms(500)
        ui.clear()

        # Display first chunk [47:63]
        line1 = self.buffer[47:63].decode('utf-8', 'ignore')
        ui.show_message(line1)
        
        # Display second chunk [64:82] - The UI doesn't have a direct "line 2" method 
        # in show_message, so we append or use _draw_text if we want exact layout.
        line2 = self.buffer[64:82].decode('utf-8', 'ignore')
        # Using a custom multi-line display approach
        ui.clear()
        ui._draw_header("SMS Received")
        ui._draw_text(line1, 10, 40)
        ui._draw_text(line2, 10, 60)
        
        time.sleep(1)
        ui.clear()

        # Display third chunk [82:99]
        line3 = self.buffer[82:99].decode('utf-8', 'ignore')
        ui._draw_header("SMS Received (Cont)")
        ui._draw_text(line3, 10, 40)
        
        time.sleep(2)
        ui.clear()
        ui.show_menu("ALFRED Edge", ["1. Add Note", "2. Voice Note", "3. Observation"]) # Return to menu
