# M5Stack Mini Setup Guide - Windows 10/11
## Flashing Alfred Firmware to Your M5Stack Mini

**Author**: Daniel J Rita (BATDAN)
**Date**: November 29, 2025
**Hardware**: M5Stack Mini (ESP32-based)
**Goal**: Install MicroPython + Alfred firmware for standalone AI assistant

---

## Prerequisites

### What You Need:
- ✅ M5Stack Mini (you have this!)
- ✅ USB-C cable (connected to laptop)
- ✅ Windows 10/11 laptop (you have this!)
- ✅ 8GB+ microSD card (formatted as FAT32)
- ⬜ Python 3.7+ (we'll install this)
- ⬜ USB drivers (we'll install this)
- ⬜ esptool (we'll install this)

---

## Step 1: Check Python Installation

Open PowerShell (Windows key + X, then "Windows PowerShell") and run:

```powershell
python --version
```

**If you see**: `Python 3.x.x` → Great! Skip to Step 2.
**If you see**: `'python' is not recognized...` → Install Python below.

### Install Python (if needed):
1. Download Python 3.11: https://www.python.org/downloads/
2. Run installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"
5. Close and reopen PowerShell
6. Verify: `python --version`

---

## Step 2: Install USB Drivers

M5Stack Mini uses a USB-to-serial chip. Let's find out which one:

### Identify Your USB Chip:
1. With M5Stack plugged in, open **Device Manager** (Windows key + X → Device Manager)
2. Look under "Ports (COM & LPT)"
3. You should see one of these:
   - `USB-SERIAL CH340 (COMx)` → **CH340 driver**
   - `Silicon Labs CP210x (COMx)` → **CP2102 driver**
   - `USB Serial Device (COMx)` → Already working!

**Note the COM port number** (e.g., COM3, COM5) - you'll need this!

### Install CH340 Driver (most common):
If you see "Unknown Device" or no serial port:

1. Download CH340 driver: http://www.wch.cn/downloads/CH341SER_ZIP.html
2. Extract ZIP file
3. Run `SETUP.EXE` as Administrator
4. Click "Install"
5. Unplug and replug M5Stack
6. Check Device Manager again - should now see `USB-SERIAL CH340 (COMx)`

### Install CP2102 Driver (alternative):
If M5Stack uses CP2102 chip instead:

1. Download: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
2. Install driver
3. Restart if prompted

---

## Step 3: Install esptool (Flash Tool)

In PowerShell:

```powershell
pip install esptool
```

Verify installation:
```powershell
esptool.py version
```

Should show: `esptool.py v4.x.x` or similar.

---

## Step 4: Download MicroPython Firmware

We need MicroPython firmware for ESP32.

### Option A: Download Pre-built (Recommended)
```powershell
# Create firmware directory
cd C:\Alfred_UBX
mkdir m5stack_firmware\downloads
cd m5stack_firmware\downloads

# Download MicroPython for ESP32
# Go to: https://micropython.org/download/esp32/
# Download latest: esp32-xxxxxxxx.bin (e.g., esp32-20231005-v1.21.0.bin)
```

### Option B: Direct Download (PowerShell)
```powershell
# Download latest stable MicroPython for ESP32
Invoke-WebRequest -Uri "https://micropython.org/resources/firmware/esp32-20231005-v1.21.0.bin" -OutFile "micropython-esp32.bin"
```

**Save location**: `C:\Alfred_UBX\m5stack_firmware\downloads\micropython-esp32.bin`

---

## Step 5: Backup Existing Firmware (Optional)

If you want to restore factory firmware later:

```powershell
# Replace COM3 with your actual COM port
esptool.py --chip esp32 --port COM3 read_flash 0 0x400000 m5stack_backup.bin
```

This creates a full backup. **Takes 5-10 minutes**.

---

## Step 6: Erase Flash Memory

**⚠️ WARNING**: This will erase everything on the M5Stack!

```powershell
# Replace COM3 with your actual COM port
esptool.py --chip esp32 --port COM3 erase_flash
```

You should see:
```
Detecting chip type... ESP32
Erasing flash (this may take a while)...
Chip erase completed successfully
```

---

## Step 7: Flash MicroPython Firmware

Now let's install MicroPython:

```powershell
# Replace COM3 with your actual COM port
esptool.py --chip esp32 --port COM3 --baud 460800 write_flash -z 0x1000 micropython-esp32.bin
```

**This takes 30-60 seconds**. You'll see:
```
Writing at 0x00001000... (3 %)
Writing at 0x00002000... (6 %)
...
Hash of data verified.
Leaving...
Hard resetting via RTS pin...
```

✅ **MicroPython is now installed!**

---

## Step 8: Test MicroPython Installation

Let's verify it worked!

### Install Thonny IDE (MicroPython Editor):
1. Download: https://thonny.org/
2. Install Thonny
3. Open Thonny
4. Go to: **Tools → Options → Interpreter**
5. Select: **MicroPython (ESP32)**
6. Port: Select your COM port (e.g., COM3)
7. Click **OK**

### Test REPL:
In Thonny's Shell window, you should see:
```
MicroPython v1.21.0 on 2023-10-05; ESP32 module with ESP32
Type "help()" for more information.
>>>
```

Try typing:
```python
>>> print("Hello Alfred!")
Hello Alfred!
>>> import sys
>>> sys.platform
'esp32'
```

✅ **MicroPython is working!**

---

## Step 9: Format SD Card (FAT32)

Your M5Stack needs an SD card for:
- Alfred Brain database (SQLite)
- AI models (TinyLlama, Vosk)
- Voice recordings

### Format SD Card:
1. Insert microSD card into your laptop
2. Open **File Explorer**
3. Right-click SD card → **Format**
4. Settings:
   - File system: **FAT32** (important!)
   - Allocation unit size: Default
   - Volume label: `ALFRED`
5. Click **Start**
6. ⚠️ Warning: This will erase everything on SD card
7. Click **OK**

### Insert SD Card into M5Stack:
1. Power off M5Stack (unplug USB)
2. Insert SD card into M5Stack's SD slot
3. Plug USB back in

---

## Step 10: Upload Simple Test Program

Let's test with a simple "Hello Alfred" program before the full firmware.

### Create Test Program:

In Thonny, create a new file (`File → New`) and paste:

```python
"""
Alfred Test Program - M5Stack Mini
Simple test to verify hardware is working
"""

import time
from machine import Pin

# M5Stack Mini has built-in LED (usually GPIO 10 or 13)
# Try GPIO 10 first
led = Pin(10, Pin.OUT)

print("=" * 40)
print("Alfred Test Program")
print("M5Stack Mini - Hardware Check")
print("=" * 40)
print()

# Blink LED test
print("Testing LED (GPIO 10)...")
for i in range(5):
    led.value(1)  # LED on
    print(f"  Blink {i+1}/5")
    time.sleep(0.5)
    led.value(0)  # LED off
    time.sleep(0.5)

print()
print("✓ LED test complete!")
print()
print("Alfred says: Good evening, sir.")
print("Hardware initialization successful.")
print()
print("=" * 40)
```

### Upload and Run:
1. Save as: `test_alfred.py`
2. Click **Run → Run current script**
3. Watch the output in Shell window
4. M5Stack's LED should blink 5 times

**If it works**: ✅ M5Stack is ready for Alfred firmware!
**If LED doesn't blink**: Try changing `Pin(10, ...)` to `Pin(13, ...)`

---

## Step 11: Check SD Card Access

Test if MicroPython can read/write to SD card:

```python
import os

# Mount SD card
try:
    import machine
    sd = machine.SDCard(slot=2, sck=18, miso=19, mosi=23, cs=4)
    os.mount(sd, '/sd')
    print("✓ SD card mounted at /sd")

    # List files
    print("\nFiles on SD card:")
    print(os.listdir('/sd'))

    # Test write
    with open('/sd/test_alfred.txt', 'w') as f:
        f.write('Alfred Brain Test\n')
    print("\n✓ SD card write test passed")

    # Test read
    with open('/sd/test_alfred.txt', 'r') as f:
        content = f.read()
    print(f"✓ SD card read test passed: {content.strip()}")

except Exception as e:
    print(f"✗ SD card error: {e}")
    print("Check that SD card is inserted and formatted as FAT32")
```

**Expected output**:
```
✓ SD card mounted at /sd
Files on SD card:
['test_alfred.txt']
✓ SD card write test passed
✓ SD card read test passed: Alfred Brain Test
```

---

## Troubleshooting

### Error: "Failed to connect to ESP32"
- **Solution 1**: Hold BOOT button on M5Stack while running esptool
- **Solution 2**: Try lower baud rate: `--baud 115200` instead of 460800
- **Solution 3**: Use different USB cable (some cables are power-only)
- **Solution 4**: Try different USB port

### Error: "Serial exception: could not open port"
- **Solution**: Close Thonny (it's using the COM port)
- Run esptool again

### Error: "A fatal error occurred: MD5 of file does not match"
- **Solution**: Re-download MicroPython firmware (file may be corrupted)

### M5Stack screen stays blank
- **Normal**: MicroPython doesn't display anything by default
- Screen will work once we upload Alfred firmware with display code

### SD card not detected
- **Check**: SD card is FAT32 (not exFAT or NTFS)
- **Check**: SD card is inserted fully
- **Try**: Different SD card (some cheap cards don't work well)

---

## Next Steps

Once you complete these steps:
1. ✅ MicroPython flashed and working
2. ✅ LED blink test passed
3. ✅ SD card readable/writable
4. ✅ Thonny IDE connected

**You're ready for the full Alfred firmware!**

We'll then upload:
- Brain Lite (SQLite database)
- TinyML AI engine (TinyLlama)
- Voice interface (Vosk STT + TTS)
- Sync manager (WiFi + brain sync)
- Display UI (LCD + buttons)

---

## Quick Reference

### Your M5Stack COM Port:
`COM___` ← Fill in your port number

### Flash MicroPython (one command):
```powershell
esptool.py --chip esp32 --port COM___ --baud 460800 write_flash -z 0x1000 micropython-esp32.bin
```

### Connect with Thonny:
Tools → Options → Interpreter → MicroPython (ESP32) → Select COM port

### SD Card Path:
`/sd/` (when mounted in MicroPython)

---

## Resources

- **MicroPython Docs**: https://docs.micropython.org/en/latest/esp32/
- **M5Stack Docs**: https://docs.m5stack.com/
- **esptool Docs**: https://docs.espressif.com/projects/esptool/
- **Thonny IDE**: https://thonny.org/

---

**Status**: Ready to flash! Follow steps 1-11 above.
**Estimated Time**: 30-45 minutes for first-time setup
**Difficulty**: Beginner-friendly (detailed instructions provided)

🤖 **Alfred says**: "Excellent choice, sir. Let's get started."
