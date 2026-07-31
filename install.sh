#!/usr/bin/env bash
# ==============================================================================
# Trainy TUI — Global Installer & Auto-Cleanup Script
# Usage: curl -fsSL https://raw.githubusercontent.com/fiozxr/trainy-tui/main/install.sh | bash
# ==============================================================================

set -e

# Styling
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

INSTALL_DIR="$HOME/.local/share/trainy"
BIN_DIR="$HOME/.local/bin"
SYS_BIN_DIR="/usr/local/bin"
REPO_URL="https://github.com/fiozxr/trainy-tui.git"

TMP_CLONE_DIR=$(mktemp -d /tmp/trainy-install-XXXXXX)

# Cleanup trap to ensure cloned temp directory is auto-deleted after install
cleanup() {
    if [ -d "$TMP_CLONE_DIR" ]; then
        rm -rf "$TMP_CLONE_DIR"
    fi
}
trap cleanup EXIT

echo -e "${BOLD}${CYAN}"
echo "  _______ _____   ______ _____ _   ___WX"
echo " |__   __|  __ \ / __   |_   _| \ | \ \  / /"
echo "    | |  | |__) | |__| |  | | |  \| |\ \_/ / "
echo "    | |  |  _  /|  __  |  | | | . \ | \   /  "
echo "    | |  | | \ \| |  | | _| |_| |\  |  | |   "
echo "    |_|  |_|  \_\_|  |_|_____|_| \_|  |_|   "
echo -e "${NC}${GREEN}          Trainy TUI Global Installer${NC}\n"

# 1. Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] python3 is required but not installed.${NC}"
    echo "Please install python3 using your system package manager."
    exit 1
fi

# 2. Check FFmpeg / ffplay
if ! command -v ffplay &> /dev/null; then
    echo -e "${YELLOW}[WARNING] 'ffplay' (ffmpeg) was not found in PATH.${NC}"
    echo "Audio playback requires ffplay."
    if command -v apt-get &> /dev/null; then
        echo -e "${CYAN}Run: sudo apt install ffmpeg${NC}"
    elif command -v pacman &> /dev/null; then
        echo -e "${CYAN}Run: sudo pacman -S ffmpeg${NC}"
    elif command -v dnf &> /dev/null; then
        echo -e "${CYAN}Run: sudo dnf install ffmpeg${NC}"
    fi
fi

# 3. Deploy Files Globally
echo -e "${CYAN}[1/4] Deploying Trainy TUI to ${INSTALL_DIR}...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -f "$SCRIPT_DIR/app.py" ]; then
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
else
    if command -v git &> /dev/null; then
        echo -e "${CYAN}Cloning remote repository...${NC}"
        git clone "$REPO_URL" "$TMP_CLONE_DIR"
        cp -r "$TMP_CLONE_DIR"/* "$INSTALL_DIR/"
    else
        echo -e "${RED}[ERROR] git is required for remote installation.${NC}"
        exit 1
    fi
fi

# 4. Install Python Dependencies
echo -e "${CYAN}[2/4] Setting up Python environment & dependencies...${NC}"
USE_VENV=0
if python3 -m venv "$INSTALL_DIR/venv" 2>/dev/null; then
    if "$INSTALL_DIR/venv/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt" 2>/dev/null; then
        USE_VENV=1
    fi
fi

if [ $USE_VENV -eq 1 ]; then
    PYTHON_BIN="$INSTALL_DIR/venv/bin/python3"
else
    echo -e "${YELLOW}Installing dependencies via user pip...${NC}"
    python3 -m pip install -q --user --break-system-packages -r "$INSTALL_DIR/requirements.txt" || python3 -m pip install -q --user -r "$INSTALL_DIR/requirements.txt"
    PYTHON_BIN="python3"
fi

# 5. Create Global Binary Launcher
echo -e "${CYAN}[3/4] Registering global binary 'trainy'...${NC}"
cat <<EOF > "$BIN_DIR/trainy"
#!/usr/bin/env bash
cd "$INSTALL_DIR"
exec "$PYTHON_BIN" "$INSTALL_DIR/app.py" "\$@"
EOF

chmod +x "$BIN_DIR/trainy"

# Try installing to /usr/local/bin if write permission exists or via sudo if available
if [ -w "$SYS_BIN_DIR" ]; then
    ln -sf "$BIN_DIR/trainy" "$SYS_BIN_DIR/trainy" 2>/dev/null || true
fi

# 6. Auto-Cleanup Cloned / Temporary Setup Files
echo -e "${CYAN}[4/4] Auto-cleaning temporary setup files...${NC}"
# Cleanup complete via trap

echo -e "\n${BOLD}${GREEN}✔ Trainy TUI installed globally!${NC}\n"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}[NOTE] Make sure ${BIN_DIR} is in your PATH environment variable.${NC}"
    echo -e "Add this to your ~/.bashrc or ~/.zshrc:\n"
    echo -e "${CYAN}    export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}\n"
fi

echo -e "${BOLD}Launch Trainy TUI from any directory by running:${NC}"
echo -e "${GREEN}    trainy${NC}\n"
