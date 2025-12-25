#!/bin/bash
# Setup ALFRED Chat shortcuts and desktop integration for macOS

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ALFRED_DIR="$(dirname "$SCRIPT_DIR")"

echo "================================"
echo "ALFRED Chat - macOS Setup"
echo "================================"
echo ""

# Create Applications folder shortcut
echo "Creating macOS application shortcut..."

# Create app wrapper
APP_DIR="$HOME/Applications/ALFRED.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create launcher script
cat > "$MACOS_DIR/ALFRED" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/../../.."
./launchers/alfred_chat.sh
EOF

chmod +x "$MACOS_DIR/ALFRED"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>ALFRED</string>
    <key>CFBundleIdentifier</key>
    <string>com.batdan007.alfred</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>ALFRED Chat</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2025 Daniel J Rita (BATDAN007). All rights reserved.</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

echo "✓ macOS application created at: $APP_DIR"
echo ""

# Create desktop alias (if Desktop exists)
if [ -d "$HOME/Desktop" ]; then
    echo "Creating Desktop shortcut..."
    ln -sf "$APP_DIR" "$HOME/Desktop/ALFRED Chat"
    echo "✓ Desktop shortcut created"
else
    echo "ℹ Desktop not found, skipping Desktop shortcut"
fi

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "ALFRED is now accessible from:"
echo "  • Applications folder (ALFRED.app)"
echo "  • Desktop (shortcut)"
echo ""
echo "To start ALFRED Chat:"
echo "  • Double-click ALFRED Chat in Applications"
echo "  • Double-click the Desktop shortcut"
echo "  • Or run: ./launchers/alfred_chat.sh"
echo ""
echo "Privacy First:"
echo "  • All data stays on your device by default"
echo "  • Cloud AI requires your explicit permission"
echo "  • Install Ollama for maximum privacy"
echo ""

open "$HOME/Applications"
