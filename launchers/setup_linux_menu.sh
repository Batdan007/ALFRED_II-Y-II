#!/bin/bash
# Setup ALFRED Chat shortcuts and desktop integration for Linux

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ALFRED_DIR="$(dirname "$SCRIPT_DIR")"

echo "================================"
echo "ALFRED Chat - Linux Setup"
echo "================================"
echo ""

# Create .desktop file for application menu
echo "Creating Linux desktop entry..."

DESKTOP_FILE="$HOME/.local/share/applications/alfred-chat.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=ALFRED Chat
Comment=Private AI Assistant with Persistent Memory
Icon=brain
Exec=@@ALFRED_DIR@@/launchers/alfred_chat.sh
Terminal=false
Categories=Utility;
StartupNotify=true
X-GNOME-Autostart-enabled=false
EOF

# Replace template with actual path
sed -i "s|@@ALFRED_DIR@@|$ALFRED_DIR|g" "$DESKTOP_FILE"

echo "✓ Desktop entry created at: $DESKTOP_FILE"
echo ""

# Create symlink in home directory for easy access
if [ ! -L "$HOME/ALFRED" ]; then
    ln -s "$ALFRED_DIR" "$HOME/ALFRED"
    echo "✓ ALFRED symlink created in home directory"
fi

echo ""

# Check desktop environment
if command -v xfce4-panel &> /dev/null; then
    echo "Detected XFCE desktop environment"
elif command -v kbuildsycoca5 &> /dev/null; then
    echo "Detected KDE desktop environment"
    kbuildsycoca5
    echo "✓ KDE menu updated"
elif [ "$DESKTOP_SESSION" = "gnome" ] || [ "$DESKTOP_SESSION" = "ubuntu" ]; then
    echo "Detected GNOME desktop environment"
fi

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "ALFRED is now accessible from:"
echo "  • Application menu (ALFRED Chat)"
echo "  • Home directory shortcut"
echo ""
echo "To start ALFRED Chat:"
echo "  • Search for 'ALFRED Chat' in application menu"
echo "  • Or run: ./launchers/alfred_chat.sh"
echo "  • Or click: ~/ALFRED/launchers/alfred_chat.sh"
echo ""
echo "Privacy First:"
echo "  • All data stays on your device by default"
echo "  • Cloud AI requires your explicit permission"
echo "  • Install Ollama for maximum privacy: https://ollama.ai"
echo ""
