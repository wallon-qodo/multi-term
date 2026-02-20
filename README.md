# Claude Multi-Terminal

A modern, TUIOS-inspired multi-session terminal UI for Claude CLI with advanced window management capabilities.

## Overview

Claude Multi-Terminal brings powerful window management and multi-session capabilities to the Claude CLI experience. Inspired by TUIOS (The Ultimate Interactive Operating System), it provides an intuitive, tile-based interface for managing multiple Claude sessions simultaneously.

## Features

### TUIOS-Inspired Design
- **Binary Space Partitioning (BSP) Tiling**: Intelligent automatic window layout that maximizes screen space
- **Drag-to-Swap Windows**: Intuitive mouse-based window reordering
- **Flexible Split Modes**: Split horizontally or vertically on demand
- **Visual Focus Indicators**: Clear borders and highlighting for active windows

### Multi-Session Management
- **Independent Claude Sessions**: Run multiple Claude CLI instances simultaneously
- **Session Persistence**: Sessions maintain state across window operations
- **Quick Navigation**: Keyboard shortcuts for rapid session switching
- **Session Tabs**: Visual tabs for easy session identification

### Terminal Capabilities
- **Full PTY Support**: Native terminal emulation via ptyprocess
- **Rich Text Rendering**: Syntax highlighting and ANSI color support
- **Clipboard Integration**: Copy/paste with system clipboard
- **Scrollback Buffer**: Full terminal history with mouse wheel support

### Window Management
- **Dynamic Layouts**: Resize, split, and reorganize windows on the fly
- **Focus Management**: Intelligent focus handling with visual feedback
- **Keyboard-Driven**: Comprehensive keybindings for power users
- **Mouse-Friendly**: Full mouse support for drag-and-drop operations

### Development Features
- **Hot Reload**: Automatic code reload during development
- **Performance Monitoring**: Built-in metrics and profiling
- **Debug Mode**: Detailed logging and diagnostics
- **Extensible Architecture**: Plugin-ready design for future enhancements

## Installation

### Prerequisites
- Python 3.10 or higher
- Claude CLI installed and configured (`npm install -g @anthropics/claude-cli`)

### One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/wallon-qodo/multi-term/main/install.sh | bash
```

### Install from PyPI

```bash
pip install claude-multi-terminal
```

### Install from source

```bash
# Clone the repository
git clone https://github.com/wallon-qodo/multi-term.git
cd multi-term

# Install the package
pip install -e .
```

### Install with development dependencies

```bash
pip install -e ".[dev]"
```

### Homebrew (Coming Soon)

```bash
brew install claude-multi-terminal
```

## Quick Start

### Launch the application

```bash
multi-term
```

### First-Time Tutorial

Run the interactive 2-minute tutorial:

```bash
multi-term --tutorial
```

### Basic Usage

The app uses **vim-style modes** (like vim/tmux):

1. **NORMAL Mode** (⌘) - Default, navigate and control
   - Press `i` to enter INSERT mode
   - Press `v` to enter VISUAL mode
   - Press `F11` for FOCUS mode

2. **INSERT Mode** (✏️) - Type prompts to Claude
   - Type your message
   - Press `Enter` to send
   - Press `Esc` to return to NORMAL

3. **VISUAL Mode** (📋) - Copy text
   - Use arrow keys to select
   - Press `Enter` to copy
   - Press `Esc` to return to NORMAL

4. **FOCUS Mode** (🎯) - Fullscreen single pane
   - Press `F11` to toggle

### Workspaces

You have **9 workspaces** (like virtual desktops):
- Press `Ctrl+1` through `Ctrl+9` to switch
- Organize by project, task, or priority
- Each workspace holds up to 4 panes

## Keybindings

### Essential Keys
- `i` - Enter INSERT mode (type prompts)
- `v` - Enter VISUAL mode (copy text)
- `F11` - Toggle FOCUS mode (fullscreen)
- `Esc` - Return to NORMAL mode
- `q` - Quit application

### Navigation
- `Tab` - Next pane
- `Shift+Tab` - Previous pane
- `Ctrl+1-9` - Switch to workspace 1-9
- `Ctrl+N` / `Ctrl+P` - Next/Previous workspace

### Session Management
- `Ctrl+N` - Create new session
- `Ctrl+W` - Close current session
- `Ctrl+S` - Save sessions
- `Ctrl+L` - Load sessions

### Advanced
- `Ctrl+F` / `F11` - Toggle focus mode
- `Ctrl+Shift+F` - Search
- `F10` - Workspace manager
- `F9` / `Ctrl+H` - History browser
- `?` - Show help (in NORMAL mode)

## Documentation

📚 **Comprehensive guides available in [`docs/`](docs/)**:

- **[USER-GUIDE.md](docs/USER-GUIDE.md)** - Complete 30+ page user guide
  - Getting started tutorials
  - Modal system explained
  - Best practices
  - Common workflows
  - Advanced features
  - Troubleshooting

- **[QUICK-REFERENCE.md](docs/QUICK-REFERENCE.md)** - One-page cheat sheet
  - Essential keyboard shortcuts
  - Common patterns
  - Quick troubleshooting

- **[README.md](docs/README.md)** - Documentation index and learning path

## Command-Line Options

```bash
multi-term --help          # Show help message
multi-term --version       # Show version
multi-term --tutorial      # Launch interactive tutorial
multi-term --check         # Validate environment
multi-term --no-mouse      # Disable mouse (enable text selection)
multi-term --debug         # Enable debug logging
```
- `Ctrl+Shift+V`: Paste from clipboard
- `Scroll`: Navigate terminal history
- `Ctrl+L`: Clear terminal

### Application
- `Ctrl+Q`: Quit application
- `F1`: Show help
- `F11`: Toggle fullscreen

For a complete keybinding reference, see [KEYBINDINGS.md](docs/KEYBINDINGS.md)

## Screenshots

> Screenshots coming soon

## Architecture

The application is built with a modular architecture:

- **Terminal Engine**: PTY management and terminal emulation
- **Window Manager**: BSP tiling and layout management
- **Session Manager**: Multi-session coordination
- **UI Layer**: Textual-based rich interface
- **Event System**: Reactive event handling

For detailed architecture documentation, see [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Development

### Project Structure

```
claude-multi-terminal/
├── claude_multi_terminal/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py                 # Main application
│   ├── terminal.py            # Terminal management
│   ├── window_manager.py      # Window/layout management
│   └── ui/                    # UI components
├── tests/                     # Test suite
├── docs/                      # Documentation
├── requirements.txt           # Dependencies
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

### Development Guidelines

This project follows the development guidelines outlined in [CLAUDE.md](CLAUDE.md), including:

- Adaptive Intelligence System integration
- Critical thinking framework for problem-solving
- Quality-first approach with automated testing
- Performance optimization with caching

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black .

# Type checking
mypy claude_multi_terminal
```

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details

## Acknowledgments

- Inspired by [TUIOS](https://tuios.org/) window management concepts
- Built with [Textual](https://textual.textualize.io/) framework
- Designed for [Claude CLI](https://claude.ai/claude-code)

## Links

- **Documentation**: [docs/](docs/)
- **Issue Tracker**: [GitHub Issues](https://github.com/wallonwalusayi/claude-multi-terminal/issues)
- **Development Guide**: [CLAUDE.md](CLAUDE.md)

---

**Version**: 0.1.0 | **Status**: Alpha | **Python**: 3.10+
