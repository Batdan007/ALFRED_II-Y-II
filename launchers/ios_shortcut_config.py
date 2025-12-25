"""
iOS/macOS Shortcut Configuration for ALFRED Chat

To use ALFRED on iOS:
1. Install Shortcut app from App Store (if not already installed)
2. Run this configuration script to create the iOS shortcut
3. The shortcut will open ALFRED Chat in Safari

Requirements:
- ALFRED Chat server running on Mac/Linux accessible to iOS device
- Both devices on same network or SSH tunnel configured
- iOS 15+ with Shortcut app
"""

import json
import os
from pathlib import Path
from urllib.parse import quote


class iOSShortcutConfig:
    """Configure iOS Shortcut for ALFRED Chat"""

    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"

    def generate_ios_shortcut_url(self) -> str:
        """
        Generate iOS Shortcut URL that can be imported
        
        This creates a URL that opens ALFRED Chat in Safari on iOS
        """
        # Safari URL
        safari_url = f"safari://{self.url}"

        # iOS Shortcut URL scheme that opens ALFRED in browser
        shortcut_url = f"shortcut-url={quote(self.url)}"

        return safari_url

    def get_shortcut_instructions(self) -> str:
        """Get instructions for setting up iOS shortcut"""
        instructions = f"""
# ALFRED Chat on iOS/macOS

## Setup Instructions

### 1. Make ALFRED accessible on iOS:

Option A: Same Network
- Start ALFRED Chat on your Mac
- Find your Mac's local IP (System Preferences > Network)
- On iOS, open Safari and go to: http://<your-mac-ip>:8000

Option B: Remote Access (requires SSH/VPN)
- Set up SSH tunnel: ssh -L 8000:localhost:8000 your-mac-ip
- Access ALFRED at: http://localhost:8000

### 2. Create iOS Shortcut (Optional):

1. Open "Shortcuts" app on iPhone/iPad
2. Tap "+" to create new shortcut
3. Add action: "Open URL"
4. URL: {self.url}
5. Name it "ALFRED Chat"
6. Add to Home Screen for quick access

### 3. Save for Home Screen:

In Safari:
- Tap Share icon
- Select "Add to Home Screen"
- Name it "ALFRED" or "ALFRED Chat"
- Tap Add

## Security Notes

- Make sure you trust the network ALFRED is running on
- For remote access, use VPN or SSH tunnel
- Never expose ALFRED server to internet without authentication
- Privacy Mode is LOCAL-FIRST by default

## Troubleshooting

If connection fails:
1. Verify ALFRED is running on your Mac
2. Check firewall settings allow port 8000
3. Confirm both devices on same network (if not using tunnel)
4. Try accessing from same Mac first to verify server works
"""
        return instructions

    def save_shortcut_instructions(self, filepath: str = "iOS_SHORTCUT_SETUP.md"):
        """Save instructions to file"""
        content = self.get_shortcut_instructions()
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath


def main():
    """Generate iOS shortcut configuration"""
    config = iOSShortcutConfig()

    print("=" * 50)
    print("ALFRED Chat - iOS/macOS Shortcut Setup")
    print("=" * 50)
    print()

    # Save instructions
    filepath = config.save_shortcut_instructions()
    print(f"✓ Instructions saved to: {filepath}")
    print()

    # Print setup instructions
    print(config.get_shortcut_instructions())


if __name__ == "__main__":
    main()
