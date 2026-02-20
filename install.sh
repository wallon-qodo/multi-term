#!/bin/bash
#
# Claude Multi-Terminal Installation Script
# One-liner: curl -fsSL https://raw.githubusercontent.com/wallon-qodo/multi-term/main/install.sh | bash
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║       Claude Multi-Terminal Installer v0.1.0        ║
║                                                       ║
║   Multi-session TUI for Claude with vim-style UI    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check OS
info "Detecting operating system..."
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS_TYPE=Linux;;
    Darwin*)    OS_TYPE=Mac;;
    CYGWIN*)    OS_TYPE=Windows;;
    MINGW*)     OS_TYPE=Windows;;
    *)          OS_TYPE="UNKNOWN:${OS}"
esac

if [ "$OS_TYPE" = "Windows" ]; then
    error "Windows is not yet supported. Use WSL2 for now."
    exit 1
fi

success "Detected: $OS_TYPE"

# Check Python version
info "Checking Python installation..."
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cmd" &> /dev/null; then
        VERSION=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        MAJOR=$(echo "$VERSION" | cut -d. -f1)
        MINOR=$(echo "$VERSION" | cut -d. -f2)

        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_CMD="$cmd"
            success "Found Python $VERSION at $(which $cmd)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    error "Python 3.10 or higher is required"
    echo ""
    info "Install Python:"
    if [ "$OS_TYPE" = "Mac" ]; then
        echo "  brew install python@3.12"
    else
        echo "  sudo apt-get install python3.12  # Ubuntu/Debian"
        echo "  sudo dnf install python3.12      # Fedora"
    fi
    exit 1
fi

# Check pip
info "Checking pip installation..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    error "pip is not installed"
    info "Install pip: $PYTHON_CMD -m ensurepip --upgrade"
    exit 1
fi
success "pip is available"

# Check for Claude CLI
info "Checking for Claude CLI..."
if ! command -v claude &> /dev/null; then
    warning "Claude CLI not found"
    echo ""
    info "Install Claude CLI first:"
    echo "  npm install -g @anthropics/claude-cli"
    echo "  # or"
    echo "  brew install anthropics/claude/claude"
    echo ""
    read -p "Continue without Claude CLI? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    success "Claude CLI found at $(which claude)"
fi

# Install method selection
echo ""
info "Select installation method:"
echo "  1) Install from PyPI (recommended)"
echo "  2) Install from source (latest development version)"
echo ""
read -p "Choice [1-2]: " -n 1 -r INSTALL_METHOD
echo ""

case $INSTALL_METHOD in
    1)
        info "Installing from PyPI..."
        if $PYTHON_CMD -m pip install --user claude-multi-terminal; then
            success "Installed claude-multi-terminal from PyPI"
        else
            error "PyPI installation failed. Falling back to source installation..."
            INSTALL_METHOD=2
        fi
        ;;
    2)
        info "Installing from source..."
        ;;
    *)
        error "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Source installation
if [ "$INSTALL_METHOD" = "2" ]; then
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    info "Cloning repository..."
    if ! git clone https://github.com/wallon-qodo/multi-term.git; then
        error "Failed to clone repository"
        exit 1
    fi

    cd multi-term

    info "Installing package..."
    if $PYTHON_CMD -m pip install --user -e .; then
        success "Installed from source"
    else
        error "Installation failed"
        exit 1
    fi

    cd ~
    rm -rf "$TEMP_DIR"
fi

# Verify installation
info "Verifying installation..."
if command -v multi-term &> /dev/null; then
    success "Installation successful!"
else
    warning "Command 'multi-term' not found in PATH"

    # Get Python user bin directory
    USER_BIN=$($PYTHON_CMD -m site --user-base)/bin

    echo ""
    info "Add to your PATH by adding this to your shell profile:"
    echo ""
    if [ "$OS_TYPE" = "Mac" ]; then
        echo "  echo 'export PATH=\"$USER_BIN:\$PATH\"' >> ~/.zshrc"
        echo "  source ~/.zshrc"
    else
        echo "  echo 'export PATH=\"$USER_BIN:\$PATH\"' >> ~/.bashrc"
        echo "  source ~/.bashrc"
    fi
    echo ""

    # Check if PATH needs updating
    if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
        warning "You'll need to restart your shell or run the source command above"
    fi
fi

# Create config directory
CONFIG_DIR="$HOME/.claude"
if [ ! -d "$CONFIG_DIR" ]; then
    info "Creating config directory at $CONFIG_DIR"
    mkdir -p "$CONFIG_DIR/data"
    mkdir -p "$CONFIG_DIR/scripts"
    mkdir -p "$CONFIG_DIR/knowledge"
    success "Config directory created"
fi

# Create sessions directory
SESSIONS_DIR="$HOME/Desktop/multi-claude-sessions/sessions"
if [ ! -d "$SESSIONS_DIR" ]; then
    info "Creating sessions directory at $SESSIONS_DIR"
    mkdir -p "$SESSIONS_DIR"
    success "Sessions directory created"
fi

# Success message
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║            Installation Complete! 🎉                 ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
info "Quick Start:"
echo ""
echo "  1. Launch the application:"
echo "     ${GREEN}multi-term${NC}"
echo ""
echo "  2. Read the quick reference:"
echo "     ${BLUE}https://github.com/wallon-qodo/multi-term/blob/main/docs/QUICK-REFERENCE.md${NC}"
echo ""
echo "  3. Essential shortcuts:"
echo "     • ${YELLOW}i${NC}    - Enter INSERT mode (type prompts)"
echo "     • ${YELLOW}Esc${NC}  - Return to NORMAL mode"
echo "     • ${YELLOW}F11${NC}  - Toggle FOCUS mode"
echo "     • ${YELLOW}q${NC}    - Quit"
echo ""

# Optional: Run first-time setup
echo ""
read -p "Run first-time tutorial? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    info "Launching tutorial..."
    if command -v multi-term &> /dev/null; then
        multi-term --tutorial
    else
        warning "Please add multi-term to your PATH first"
    fi
fi

echo ""
success "Enjoy Claude Multi-Terminal!"
