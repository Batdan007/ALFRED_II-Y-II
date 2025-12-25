eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee#!/bin/bash
# ALFRED Chat Launcher for macOS/Linux
# Start ALFRED with full capabilities in modern chat interface

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ALFRED_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ALFRED_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed${NC}"
    echo "Please install Python 3.10+ from https://www.python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"

# Check if required dependencies are installed
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo -e "${YELLOW}Installing required dependencies...${NC}"
    pip3 install -q fastapi "uvicorn[standard]" aiohttp
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Check if Ollama is running (local-first privacy)
echo -e "${YELLOW}Checking for Ollama (local AI)...${NC}"
if ! python3 -c "import requests; requests.get('http://localhost:11434/api/version', timeout=2)" 2>/dev/null; then
    echo -e "${YELLOW}Ollama not detected. ALFRED can still use cloud models.${NC}"
    echo -e "${YELLOW}For best privacy: Install Ollama from https://ollama.ai${NC}"
    read -p "Continue without local Ollama? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Start ALFRED Chat
echo
echo -e "${GREEN}Starting ALFRED Chat Server...${NC}"
echo
echo -e "${YELLOW}Privacy Mode: LOCAL-FIRST (your data stays on your device)${NC}"
echo -e "${YELLOW}Opening browser in 3 seconds...${NC}"
echo

# Start the server in background
python3 ui/chat_interface.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Open browser
if command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:8000
elif command -v open &> /dev/null; then
    # macOS
    open http://localhost:8000
else
    echo -e "${YELLOW}Open your browser to http://localhost:8000${NC}"
fi

# Display status
echo
echo -e "${GREEN}ALFRED Chat is running at http://localhost:8000${NC}"
echo
echo "Press Ctrl+C to stop the server"
echo

# Keep script running
wait $SERVER_PID
