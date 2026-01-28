# ALFRED Edge - M5 Cardputer

**The AI That Never Forgets - Now In Your Pocket**

ALFRED Edge is a standalone pocket AI assistant for construction workers and field teams. It collects notes, voice recordings, and observations offline, then automatically syncs to the main ALFRED brain when WiFi is available.

## Hardware

**Supported Devices:**
- M5Stack Cardputer (ESP32-S3)
- M5Stack Cardputer ADV (Extended Storage)

**Specifications:**
- CPU: ESP32-S3 dual-core 240MHz
- RAM: 8MB PSRAM
- Flash: 16MB
- Display: 240x135 ST7789 LCD (1.14")
- Input: 56-key QWERTY keyboard
- Audio: Built-in microphone and speaker
- Connectivity: WiFi, Bluetooth
- Battery: 1400mAh (built-in)

## Features

### Offline First
- Works completely offline - no WiFi required
- Records notes, voice, and observations
- Stores everything locally until sync available

### Multi-Worker Support
- Each Cardputer is assigned to a worker
- Multiple workers can collect data simultaneously
- All data syncs to central ALFRED brain

### Auto-Sync
- Automatically connects to WiFi when available
- Syncs pending data to ALFRED server
- Downloads new tasks from server
- No manual intervention required

### Data Collection
- **Notes**: Quick text notes with categories (safety, progress, issue, material, task)
- **Voice Notes**: Voice recordings for transcription
- **Observations**: Site observations with location and severity
- **Task Updates**: Status updates on assigned tasks

## Quick Start

### 1. Install Dependencies

```bash
pip install esptool mpremote
```

### 2. Connect M5 Cardputer

1. Connect USB-C cable to M5 Cardputer
2. Connect other end to your computer
3. Device should be recognized automatically

### 3. Flash ALFRED Edge

```bash
cd ALFRED_IV-Y-VI/m5_cardputer
python flash.py
```

The flash tool will:
- Download MicroPython firmware
- Erase and flash the device
- Upload ALFRED Edge files
- Configure worker settings

### 4. Start Sync Server

On your PC/server that runs ALFRED:

```bash
cd ALFRED_IV-Y-VI
python alfred_sync_server.py --port 8765
```

### 5. Power On Cardputer

Disconnect USB and power on. ALFRED Edge starts automatically.

## Usage

### Main Menu

```
┌─ ALFRED Edge ─────────────────────────┐
│                                        │
│  1. Add Note                           │
│  2. Voice Note                         │
│  3. Observation                        │
│  4. Task Update                        │
│  5. View Pending                       │
│  6. Sync Now                           │
│  7. Settings                           │
│  0. Exit                               │
│                                        │
│  [Pending: 5]                          │
└────────────────────────────────────────┘
```

### Adding Notes

1. Press `1` from main menu
2. Type your note using the keyboard
3. Press `ENTER` to save
4. Select category (general, safety, progress, issue, material, task)

### Recording Voice Notes

1. Press `2` from main menu
2. Recording starts immediately (10 seconds)
3. Speak clearly into the microphone
4. Voice is queued for transcription on sync

### Logging Observations

1. Press `3` from main menu
2. Enter description
3. Enter location (optional)
4. Select severity (info, warning, critical)

### Manual Sync

1. Press `6` from main menu
2. Device connects to configured WiFi
3. Uploads all pending items
4. Downloads any new tasks

### Settings

1. Press `7` from main menu
2. Configure:
   - Worker name
   - WiFi credentials
   - Server URL
   - Voice on/off

## Configuration

Configuration is stored in `/config.json` on the device:

```json
{
    "device_name": "ALFRED_EDGE_001",
    "device_type": "m5_cardputer",
    "worker_id": "john_doe",
    "worker_name": "John Doe",
    "sync_server": "http://192.168.1.100:8765",
    "wifi_ssid": "Construction_WiFi",
    "wifi_password": "your_password",
    "auto_sync_interval": 300,
    "voice_enabled": true
}
```

## Server Integration

ALFRED Edge syncs with the main ALFRED_IV-Y-VI system via REST API:

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/edge/register` | POST | Register device |
| `/api/edge/upload` | POST | Upload sync data |
| `/api/edge/tasks` | GET | Get assigned tasks |
| `/api/edge/tasks/ack` | POST | Acknowledge tasks |

### Data Flow

```
┌─────────────────┐         WiFi          ┌─────────────────┐
│  M5 Cardputer   │ ◄──────────────────► │ ALFRED Sync     │
│  (ALFRED Edge)  │      HTTP REST        │ Server          │
└────────┬────────┘                       └────────┬────────┘
         │                                         │
    Local Brain                              ALFRED Brain
    (JSON files)                             (SQLite DB)
```

### Sync Process

1. **Device** collects data offline (notes, voice, observations)
2. **Device** detects WiFi and connects
3. **Device** uploads all pending items to server
4. **Server** stores data in ALFRED brain
5. **Server** returns any tasks for the worker
6. **Device** stores tasks locally
7. **Device** marks items as synced

## File Structure

```
m5_cardputer/
├── main.py          # Main application
├── local_brain.py   # Offline storage
├── sync_client.py   # WiFi sync client
├── ui.py            # Display & keyboard
├── flash.py         # Flash tool
├── README.md        # This file
└── firmware/        # Downloaded firmware
    └── micropython_s3.bin
```

## Troubleshooting

### Device Not Detected

1. Check USB cable is data-capable (not charge-only)
2. Try different USB port
3. Install CH340/CP210x drivers if needed
4. Manually specify port: `python flash.py --port COM3`

### WiFi Won't Connect

1. Check SSID and password in Settings
2. Ensure WiFi network is 2.4GHz (ESP32 limitation)
3. Try moving closer to access point
4. Check server is running and accessible

### Sync Fails

1. Verify server URL is correct
2. Check server is running: `curl http://server:8765/api/health`
3. Ensure device and server are on same network
4. Check firewall allows port 8765

### Display Issues

1. Reset device (hold power button)
2. Re-flash firmware: `python flash.py`
3. Check for physical damage

## Use Cases

### Construction Sites

- Workers record daily progress notes
- Log safety observations with severity levels
- Voice notes for quick hands-free updates
- Task status updates from the field
- All data syncs when workers return to office WiFi

### Field Inspections

- Record inspection findings offline
- Photograph issues (planned feature)
- Location tagging for observations
- Generate reports on sync

### Warehouse Operations

- Inventory counts and adjustments
- Picking and packing confirmations
- Issue reporting
- Task completion tracking

## Development

### Running on PC (Simulation)

For development without hardware:

```bash
cd ALFRED_IV-Y-VI/m5_cardputer
python main.py
```

Runs in text mode without display/keyboard hardware.

### Testing Local Brain

```bash
python local_brain.py
```

### Testing Sync Client

```bash
python sync_client.py
```

Requires sync server running.

## Patent Notice

This software is part of the ALFRED-UBX system, which includes patent-pending technology. See main repository for details.

## Author

**Daniel J. Rita (BATDAN)**
- Repository: https://github.com/Batdan007/ALFRED_IV-Y-VI
- Contact: danieljrita@hotmail.com

## License

Proprietary - Part of ALFRED-UBX Patent-Pending System

---

*"The AI That Never Forgets - Now In Your Pocket"*
