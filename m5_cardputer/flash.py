#!/usr/bin/env python3
"""
ALFRED Edge - M5 Cardputer Flash Tool
======================================
Flashes ALFRED Edge firmware to M5 Cardputer devices.

Supports:
- M5Stack Cardputer (ESP32-S3)
- M5Stack Cardputer ADV (ESP32-S3 with extended storage)

Requirements:
- esptool (pip install esptool)
- mpremote (pip install mpremote)
- USB cable connected to M5 Cardputer

Author: Daniel J. Rita (BATDAN)
https://github.com/Batdan007/ALFRED_UBX
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

# Colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def print_banner():
    """Print ALFRED Edge banner."""
    print(f"""
{Colors.CYAN}    _    _     _____ ____  _____ ____    _____ ____   ____ _____
   / \\  | |   |  ___|  _ \\| ____|  _ \\  | ____|  _ \\ / ___| ____|
  / _ \\ | |   | |_  | |_) |  _| | | | | |  _| | | | | |  _|  _|
 / ___ \\| |___|  _| |  _ <| |___| |_| | | |___| |_| | |_| | |___
/_/   \\_\\_____|_|   |_| \\_\\_____|____/  |_____|____/ \\____|_____|
{Colors.NC}
{Colors.YELLOW}  M5 Cardputer Flash Tool - The AI That Never Forgets{Colors.NC}
{Colors.BLUE}  https://github.com/Batdan007/ALFRED_UBX{Colors.NC}
""")


def check_dependencies():
    """Check if required tools are installed."""
    missing = []

    # Check esptool
    try:
        result = subprocess.run(["esptool.py", "--help"],
                              capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        try:
            result = subprocess.run(["esptool", "--help"],
                                  capture_output=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            missing.append("esptool")

    # Check mpremote
    try:
        result = subprocess.run(["mpremote", "version"],
                              capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        missing.append("mpremote")

    if missing:
        print(f"{Colors.RED}[ERROR] Missing dependencies: {', '.join(missing)}{Colors.NC}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False

    print(f"{Colors.GREEN}[OK] All dependencies installed{Colors.NC}")
    return True


def find_device():
    """Find connected M5 Cardputer device."""
    print(f"\n{Colors.CYAN}[INFO] Searching for M5 Cardputer...{Colors.NC}")

    # Common serial port patterns
    import glob

    # Windows
    if sys.platform == "win32":
        ports = ["COM%d" % i for i in range(256)]
    # Linux
    elif sys.platform.startswith("linux"):
        ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
    # macOS
    else:
        ports = glob.glob("/dev/tty.usbserial*") + glob.glob("/dev/cu.usbserial*")

    for port in ports:
        try:
            # Try to read chip info
            result = subprocess.run(
                ["esptool.py", "--port", port, "chip_id"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "ESP32-S3" in result.stdout or result.returncode == 0:
                print(f"{Colors.GREEN}[OK] Found M5 Cardputer on {port}{Colors.NC}")
                return port
        except:
            continue

    print(f"{Colors.YELLOW}[WARN] No device found automatically{Colors.NC}")
    return None


def download_micropython_firmware():
    """Download MicroPython firmware for ESP32-S3."""
    print(f"\n{Colors.CYAN}[INFO] Downloading MicroPython firmware...{Colors.NC}")

    firmware_url = "https://micropython.org/resources/firmware/ESP32_GENERIC_S3-20240222-v1.22.2.bin"
    firmware_path = Path(__file__).parent / "firmware" / "micropython_s3.bin"

    firmware_path.parent.mkdir(exist_ok=True)

    if firmware_path.exists():
        print(f"{Colors.GREEN}[OK] Firmware already downloaded{Colors.NC}")
        return firmware_path

    try:
        import urllib.request
        print(f"Downloading from {firmware_url}...")
        urllib.request.urlretrieve(firmware_url, firmware_path)
        print(f"{Colors.GREEN}[OK] Firmware downloaded{Colors.NC}")
        return firmware_path
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Download failed: {e}{Colors.NC}")
        return None


def erase_flash(port):
    """Erase ESP32-S3 flash."""
    print(f"\n{Colors.CYAN}[INFO] Erasing flash...{Colors.NC}")

    try:
        subprocess.run(
            ["esptool.py", "--chip", "esp32s3", "--port", port, "erase_flash"],
            check=True
        )
        print(f"{Colors.GREEN}[OK] Flash erased{Colors.NC}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[ERROR] Erase failed: {e}{Colors.NC}")
        return False


def flash_micropython(port, firmware_path):
    """Flash MicroPython firmware."""
    print(f"\n{Colors.CYAN}[INFO] Flashing MicroPython...{Colors.NC}")

    try:
        subprocess.run(
            ["esptool.py", "--chip", "esp32s3", "--port", port,
             "--baud", "460800", "write_flash", "-z", "0x0", str(firmware_path)],
            check=True
        )
        print(f"{Colors.GREEN}[OK] MicroPython flashed{Colors.NC}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[ERROR] Flash failed: {e}{Colors.NC}")
        return False


def upload_alfred_edge(port):
    """Upload ALFRED Edge files to device."""
    print(f"\n{Colors.CYAN}[INFO] Uploading ALFRED Edge files...{Colors.NC}")

    # Files to upload
    files = [
        "main.py",
        "local_brain.py",
        "sync_client.py",
        "ui.py"
    ]

    script_dir = Path(__file__).parent

    for filename in files:
        filepath = script_dir / filename
        if not filepath.exists():
            print(f"{Colors.YELLOW}[WARN] Missing {filename}, skipping{Colors.NC}")
            continue

        print(f"  Uploading {filename}...")
        try:
            subprocess.run(
                ["mpremote", "connect", port, "cp", str(filepath), f":/{filename}"],
                check=True
            )
            print(f"  {Colors.GREEN}[OK] {filename}{Colors.NC}")
        except subprocess.CalledProcessError as e:
            print(f"  {Colors.RED}[ERROR] Failed to upload {filename}: {e}{Colors.NC}")

    # Create data directory
    print("  Creating /data directory...")
    try:
        subprocess.run(
            ["mpremote", "connect", port, "mkdir", "/data"],
            check=True
        )
    except:
        pass  # Directory may already exist

    print(f"\n{Colors.GREEN}[OK] ALFRED Edge files uploaded{Colors.NC}")
    return True


def configure_device(port, config):
    """Configure device with WiFi and worker settings."""
    print(f"\n{Colors.CYAN}[INFO] Configuring device...{Colors.NC}")

    import json
    config_content = json.dumps(config, indent=2)

    # Write config.json
    try:
        # Create temp file with config
        temp_config = Path(__file__).parent / "temp_config.json"
        with open(temp_config, 'w') as f:
            f.write(config_content)

        subprocess.run(
            ["mpremote", "connect", port, "cp", str(temp_config), ":/config.json"],
            check=True
        )

        temp_config.unlink()  # Remove temp file

        print(f"{Colors.GREEN}[OK] Configuration saved{Colors.NC}")
        return True
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Configuration failed: {e}{Colors.NC}")
        return False


def verify_installation(port):
    """Verify ALFRED Edge installation."""
    print(f"\n{Colors.CYAN}[INFO] Verifying installation...{Colors.NC}")

    try:
        # List files on device
        result = subprocess.run(
            ["mpremote", "connect", port, "ls", "/"],
            capture_output=True,
            text=True
        )

        if "main.py" in result.stdout and "local_brain.py" in result.stdout:
            print(f"{Colors.GREEN}[OK] ALFRED Edge installed successfully!{Colors.NC}")
            return True
        else:
            print(f"{Colors.YELLOW}[WARN] Some files may be missing{Colors.NC}")
            return False
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Verification failed: {e}{Colors.NC}")
        return False


def main():
    """Main flash script."""
    print_banner()

    parser = argparse.ArgumentParser(description="ALFRED Edge Flash Tool")
    parser.add_argument("--port", "-p", help="Serial port (auto-detected if not specified)")
    parser.add_argument("--skip-flash", action="store_true", help="Skip MicroPython flash (only upload files)")
    parser.add_argument("--worker", "-w", help="Worker name for this device")
    parser.add_argument("--device-name", "-d", help="Device name (default: ALFRED_EDGE_XXX)")
    parser.add_argument("--wifi-ssid", "-s", help="WiFi SSID")
    parser.add_argument("--wifi-pass", help="WiFi password")
    parser.add_argument("--server", help="ALFRED sync server URL")
    args = parser.parse_args()

    # Check dependencies
    if not check_dependencies():
        return 1

    # Find device
    port = args.port or find_device()
    if not port:
        port = input(f"\n{Colors.YELLOW}Enter serial port manually (e.g., COM3, /dev/ttyUSB0): {Colors.NC}").strip()
        if not port:
            print(f"{Colors.RED}[ERROR] No port specified{Colors.NC}")
            return 1

    print(f"\n{Colors.CYAN}Using port: {port}{Colors.NC}")

    # Flash MicroPython if needed
    if not args.skip_flash:
        firmware = download_micropython_firmware()
        if not firmware:
            return 1

        if not erase_flash(port):
            return 1

        if not flash_micropython(port, firmware):
            return 1

        # Wait for device to reboot
        print(f"\n{Colors.CYAN}[INFO] Waiting for device to reboot...{Colors.NC}")
        time.sleep(5)

    # Upload ALFRED Edge files
    if not upload_alfred_edge(port):
        return 1

    # Configure device
    config = {
        "device_name": args.device_name or f"ALFRED_EDGE_{int(time.time()) % 1000:03d}",
        "device_type": "m5_cardputer",
        "worker_name": args.worker or input(f"\n{Colors.YELLOW}Enter worker name: {Colors.NC}").strip() or "Worker",
        "wifi_ssid": args.wifi_ssid or input(f"{Colors.YELLOW}Enter WiFi SSID (or leave blank): {Colors.NC}").strip(),
        "wifi_password": args.wifi_pass or "",
        "sync_server": args.server or "http://192.168.1.100:8765",
        "voice_enabled": True,
        "auto_sync_interval": 300
    }

    # Get WiFi password if SSID was provided
    if config["wifi_ssid"] and not config["wifi_password"]:
        config["wifi_password"] = input(f"{Colors.YELLOW}Enter WiFi password: {Colors.NC}").strip()

    config["worker_id"] = config["worker_name"].lower().replace(" ", "_")

    configure_device(port, config)

    # Verify installation
    verify_installation(port)

    # Final message
    print(f"""
{Colors.GREEN}{'='*50}
  ALFRED Edge Installation Complete!
{'='*50}{Colors.NC}

{Colors.CYAN}Device Settings:{Colors.NC}
  Name:     {config['device_name']}
  Worker:   {config['worker_name']}
  WiFi:     {config['wifi_ssid'] or '(not configured)'}
  Server:   {config['sync_server']}

{Colors.YELLOW}Next Steps:{Colors.NC}
  1. Disconnect USB cable
  2. Power on the M5 Cardputer
  3. ALFRED Edge will start automatically
  4. Configure WiFi from Settings menu if needed

{Colors.CYAN}On your PC/Server:{Colors.NC}
  Run the sync server:
    python alfred_sync_server.py --port 8765

{Colors.GREEN}The AI That Never Forgets - Now In Your Pocket!{Colors.NC}
""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
