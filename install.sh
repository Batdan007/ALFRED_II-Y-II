#!/usr/bin/env bash
#
# ALFRED_UBX Installation Script for Linux/macOS/WSL
# AI Assistant with Persistent Memory & Adaptive Learning
# Author: Daniel J. Rita aka BATDAN007
# https://github.com/Batdan007/ALFRED_UBX
#
# Usage: ./install.sh [options]
# Options:
#   --skip-venv     Skip virtual environment creation
#   --force         Force reinstall (remove existing venv)
#   --python PATH   Specify Python executable path
#   --help          Show this help message

set -e

# Configuration
PYTHON_CMD="${PYTHON_CMD:-python3}"
VENV_DIR="venv"
MIN_PYTHON_VERSION="3.10"
SKIP_VENV=false
FORCE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Logging functions
info() { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
show_banner() {
    echo ""
    echo -e "${CYAN}    _    _     _____ ____  _____ ____    _   _ ______  __${NC}"
    echo -e "${CYAN}   / \\  | |   |  ___|  _ \\| ____|  _ \\  | | | | __ ) \\/ /${NC}"
    echo -e "${CYAN}  / _ \\ | |   | |_  | |_) |  _| | | | | | | | |  _ \\\\  / ${NC}"
    echo -e "${CYAN} / ___ \\| |___|  _| |  _ <| |___| |_| | | |_| | |_) /  \\ ${NC}"
    echo -e "${CYAN}/_/   \\_\\_____|_|   |_| \\_\\_____|____/   \\___/|____/_/\\_\\${NC}"
    echo ""
    echo -e "${WHITE}  AI Assistant with Persistent Memory & Adaptive Learning${NC}"
    echo -e "${GRAY}  https://github.com/Batdan007/ALFRED_UBX${NC}"
    echo ""
}

# Show help
show_help() {
    echo "ALFRED_UBX Installation Script"
    echo ""
    echo "Usage: ./install.sh [options]"
    echo ""
    echo "Options:"
    echo "  --skip-venv     Skip virtual environment creation"
    echo "  --force         Force reinstall (remove existing venv)"
    echo "  --python PATH   Specify Python executable path"
    echo "  --help          Show this help message"
    echo ""
    exit 0
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-venv)
                SKIP_VENV=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --python)
                PYTHON_CMD="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                ;;
            *)
                error "Unknown option: $1"
                show_help
                ;;
        esac
    done
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)
            if grep -q Microsoft /proc/version 2>/dev/null; then
                OS="wsl"
            else
                OS="linux"
            fi
            ;;
        Darwin*)
            OS="macos"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            OS="windows"
            ;;
        *)
            OS="unknown"
            ;;
    esac
    info "Detected OS: $OS"
}

# Check Python version
check_python() {
    info "Checking Python installation..."
    
    # Try different Python commands
    for cmd in "$PYTHON_CMD" python3 python; do
        if command -v "$cmd" &> /dev/null; then
            version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
            if [[ -n "$version" ]]; then
                major=$(echo "$version" | cut -d. -f1)
                minor=$(echo "$version" | cut -d. -f2)
                
                if [[ $major -ge 3 && $minor -ge 10 ]]; then
                    PYTHON_CMD="$cmd"
                    success "Found Python $version ($cmd)"
                    return 0
                fi
            fi
        fi
    done
    
    error "Python 3.10+ is required but not found"
    echo ""
    echo "Please install Python 3.10 or higher:"
    case $OS in
        macos)
            echo "  brew install python@3.12"
            ;;
        linux|wsl)
            echo "  sudo apt update && sudo apt install python3.12 python3.12-venv"
            echo "  # or"
            echo "  sudo dnf install python3.12"
            ;;
    esac
    exit 1
}

# Check Git
check_git() {
    info "Checking Git installation..."
    
    if command -v git &> /dev/null; then
        version=$(git --version 2>/dev/null)
        success "Found $version"
        return 0
    else
        warn "Git not found. Some features may be limited."
        return 1
    fi
}

# Create virtual environment
create_venv() {
    if [[ "$SKIP_VENV" == "true" ]]; then
        warn "Skipping virtual environment creation (--skip-venv)"
        return 0
    fi
    
    info "Creating virtual environment..."
    
    if [[ -d "$VENV_DIR" ]]; then
        if [[ "$FORCE" == "true" ]]; then
            warn "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            success "Virtual environment already exists"
            return 0
        fi
    fi
    
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    success "Virtual environment created at $VENV_DIR"
}

# Activate virtual environment
activate_venv() {
    if [[ "$SKIP_VENV" == "true" ]]; then
        return 0
    fi
    
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
        success "Virtual environment activated"
    else
        warn "Could not activate virtual environment"
    fi
}

# Install dependencies
install_dependencies() {
    info "Installing dependencies..."
    
    # Determine pip command
    if [[ "$SKIP_VENV" != "true" && -f "$VENV_DIR/bin/pip" ]]; then
        PIP_CMD="$VENV_DIR/bin/pip"
    else
        PIP_CMD="pip3"
    fi
    
    # Upgrade pip
    info "Upgrading pip..."
    "$PIP_CMD" install --upgrade pip --quiet 2>/dev/null || true
    success "pip upgraded"
    
    # Install from requirements.txt if exists
    if [[ -f "requirements.txt" ]]; then
        info "Installing from requirements.txt..."
        "$PIP_CMD" install -r requirements.txt --quiet
        success "Dependencies installed from requirements.txt"
    else
        # Install core dependencies
        info "Installing core dependencies..."
        packages=(
            "anthropic"
            "openai"
            "groq"
            "fastapi"
            "uvicorn[standard]"
            "mcp"
            "rich"
            "prompt-toolkit"
            "pyttsx3"
            "pydantic"
            "python-dotenv"
            "aiohttp"
            "httpx"
        )
        
        for package in "${packages[@]}"; do
            info "  Installing $package..."
            "$PIP_CMD" install "$package" --quiet 2>/dev/null || warn "  Could not install $package"
        done
        success "Core dependencies installed"
    fi
    
    # macOS-specific: install speech dependencies
    if [[ "$OS" == "macos" ]]; then
        info "Installing macOS speech dependencies..."
        "$PIP_CMD" install pyobjc-framework-Cocoa --quiet 2>/dev/null || true
    fi
    
    # Linux-specific: check for espeak
    if [[ "$OS" == "linux" || "$OS" == "wsl" ]]; then
        if ! command -v espeak &> /dev/null && ! command -v espeak-ng &> /dev/null; then
            warn "espeak not found. Text-to-speech may not work."
            echo "  Install with: sudo apt install espeak-ng"
        fi
    fi
}

# Create .env file
create_env_file() {
    info "Setting up environment configuration..."
    
    if [[ -f ".env" ]]; then
        success ".env file already exists"
        return 0
    fi
    
    if [[ -f ".env.example" ]]; then
        cp ".env.example" ".env"
        success "Created .env from .env.example"
    else
        cat > ".env" << 'EOF'
# ALFRED_UBX Configuration
# Fill in your API keys below

# AI Provider API Keys (at least one required)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here

# Optional: Default AI Provider (anthropic, openai, groq)
DEFAULT_PROVIDER=anthropic

# Optional: Model Settings
DEFAULT_MODEL=claude-sonnet-4-20250514

# Optional: Memory Settings
MEMORY_ENABLED=true
MEMORY_PATH=./memory

# Optional: Server Settings
HOST=127.0.0.1
PORT=8000
EOF
        success "Created .env template"
    fi
}

# Create launcher script
create_launcher() {
    info "Creating launcher script..."
    
    cat > "alfred" << 'EOF'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
fi

# Run Alfred
python main.py "$@"
EOF
    
    chmod +x "alfred"
    success "Created ./alfred launcher"
}

# Create systemd service (Linux only)
create_systemd_service() {
    if [[ "$OS" != "linux" ]]; then
        return 0
    fi
    
    info "Creating systemd service template..."
    
    INSTALL_DIR="$(pwd)"
    
    cat > "alfred.service" << EOF
[Unit]
Description=ALFRED_UBX AI Assistant
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python main.py
Restart=on-failure
RestartSec=5
Environment=PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF
    
    success "Created alfred.service (copy to /etc/systemd/system/ to enable)"
}

# Show final instructions
show_instructions() {
    echo ""
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN} Installation Complete!${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo -e "${WHITE}1. Configure your API keys:${NC}"
    echo -e "${GRAY}   Edit the .env file and add your API key(s):${NC}"
    echo ""
    echo -e "${YELLOW}   export ANTHROPIC_API_KEY=\"your-key\"${NC}"
    echo -e "${YELLOW}   export OPENAI_API_KEY=\"your-key\"${NC}"
    echo -e "${YELLOW}   export GROQ_API_KEY=\"your-key\"${NC}"
    echo ""
    echo -e "${WHITE}2. Activate the virtual environment:${NC}"
    echo -e "${YELLOW}   source venv/bin/activate${NC}"
    echo ""
    echo -e "${WHITE}3. Run ALFRED:${NC}"
    echo -e "${YELLOW}   python main.py${NC}"
    echo -e "${GRAY}   # Or use the launcher:${NC}"
    echo -e "${YELLOW}   ./alfred${NC}"
    echo ""
    
    if [[ "$OS" == "linux" ]]; then
        echo -e "${WHITE}4. (Optional) Install as a service:${NC}"
        echo -e "${YELLOW}   sudo cp alfred.service /etc/systemd/system/${NC}"
        echo -e "${YELLOW}   sudo systemctl daemon-reload${NC}"
        echo -e "${YELLOW}   sudo systemctl enable alfred${NC}"
        echo -e "${YELLOW}   sudo systemctl start alfred${NC}"
        echo ""
    fi
    
    echo -e "${GRAY}Documentation: https://github.com/Batdan007/ALFRED_UBX${NC}"
    echo ""
}

# Main installation
main() {
    parse_args "$@"
    show_banner
    detect_os
    check_python
    check_git || true
    create_venv
    activate_venv
    install_dependencies
    create_env_file
    create_launcher
    create_systemd_service
    show_instructions
}

main "$@"
