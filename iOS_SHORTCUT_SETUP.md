# iOS Quick Setup - ALFRED Chat

## Access ALFRED from iPhone/iPad

### Method 1: Same WiFi Network (Easiest)

**On Your Mac:**
1. Start ALFRED Chat
   ```bash
   ./launchers/alfred_chat.sh
   # or use the ALFRED.app from Applications
   ```

2. Find your Mac's IP address:
   - Click WiFi icon in menu bar
   - Select your network
   - IP shown as "192.168.x.x"

**On iPhone/iPad:**
1. Open Safari
2. Type in address bar: `http://192.168.1.X:8000`
   (Replace X with your actual Mac IP)
3. Bookmark the page (optional)

That's it! ALFRED Chat works in Safari.

### Method 2: Create Home Screen Shortcut

**On iPhone/iPad:**
1. Open Safari
2. Go to `http://192.168.1.X:8000`
3. Tap Share button (⬆️)
4. Select "Add to Home Screen"
5. Name it "ALFRED" or "ALFRED Chat"
6. Tap "Add"

Now ALFRED launches like an app from your home screen.

### Method 3: SSH Tunnel (Remote Access)

For accessing ALFRED when not on the same network:

**On Mac terminal:**
```bash
ssh -L 8000:localhost:8000 your-username@your-mac-ip
```

**On iPhone:**
1. Set up SSH client (e.g., Terminus)
2. Connect to your Mac via SSH
3. Open Safari: `http://localhost:8000`

### Method 4: VPN Access

1. Set up VPN on your Mac or network
2. Connect iPhone to same VPN
3. Use Method 1 with your Mac's IP

## Tips

- **Faster access:** Create a bookmark in Safari
- **Home screen app:** Use "Add to Home Screen" option
- **Multiple devices:** Works on iPhone, iPad, and Mac
- **Performance:** Local network access is fastest
- **Privacy:** All data stays on your Mac by default

## Troubleshooting

### Connection Failed
```
✗ Can't reach 192.168.1.X:8000
```

**Fix:**
1. Verify ALFRED is running on Mac
2. Check correct IP address (open `http://localhost:8000` on Mac)
3. Confirm both devices on same WiFi
4. Check Mac firewall allows port 8000

### Offline Mode
- If WiFi disconnects, ALFRED still works on your Mac
- iPhone loses connection but ALFRED saves locally

### Slow Performance
- Local network (same WiFi) = fastest
- Close other apps on iPad to free memory
- Check WiFi signal strength

## Security Notes

- ✅ Your data stays on your device
- ✅ No cloud access without permission
- ✅ Encrypted on local network (same as any WiFi traffic)
- ⚠️ Don't access ALFRED over untrusted networks
- ⚠️ Use VPN for accessing remotely

## Features

ALFRED works the same on iOS as on Mac:
- Task classification
- Agent selection
- Response quality checking
- Brain integration
- All learning features

## Support

For issues:
1. Verify ALFRED is running: `http://localhost:8000` on Mac
2. Check brain is working: `/memory` command
3. Review logs: `alfred_chat.log` in ALFRED directory

---

**Quick Links:**
- Main Setup: ALFRED_CHAT_SETUP_GUIDE.md
- Full Guide: ALFRED_BRAIN_LEARNING_GUIDE.md
- Reference: QUICK_REFERENCE_BRAIN_LEARNING.md
