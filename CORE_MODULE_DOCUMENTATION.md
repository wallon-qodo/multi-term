# Core Module Documentation

## Overview

The `core` module provides the foundational components for managing multiple Claude CLI sessions in the multi-terminal application. It handles session lifecycle, clipboard operations, and transcript export functionality.

## Module Structure

```
claude_multi_terminal/core/
├── __init__.py              # Module exports
├── session_manager.py       # Session lifecycle management
├── clipboard.py            # Clipboard operations
├── export.py               # Transcript export functionality
└── pty_handler.py          # PTY process management
```

## Components

### 1. SessionManager

**File:** `session_manager.py`

Manages the lifecycle of multiple Claude CLI PTY processes.

#### Class: `SessionManager`

```python
class SessionManager:
    def __init__(self, claude_path: str = "/opt/homebrew/bin/claude")
```

**Attributes:**
- `claude_path: str` - Path to Claude CLI executable
- `sessions: Dict[str, SessionInfo]` - Dictionary of active sessions

**Methods:**

##### `create_session(name, working_dir, claude_args) -> str`
Creates a new Claude CLI session with PTY.

**Parameters:**
- `name: Optional[str]` - Human-readable session name
- `working_dir: Optional[str]` - Working directory for the session
- `claude_args: Optional[list]` - Additional arguments for Claude CLI

**Returns:**
- `str` - UUID string for the new session

**Example:**
```python
manager = SessionManager()
session_id = manager.create_session(
    name="Research Session",
    working_dir="/path/to/project"
)
```

##### `terminate_session(session_id) -> None`
Gracefully terminates a session (async).

**Parameters:**
- `session_id: str` - UUID of session to terminate

##### `get_session(session_id) -> Optional[SessionInfo]`
Retrieves session information by ID.

**Parameters:**
- `session_id: str` - UUID of session to retrieve

**Returns:**
- `Optional[SessionInfo]` - SessionInfo if found, None otherwise

##### `list_sessions() -> List[SessionInfo]`
Lists all active sessions.

**Returns:**
- `List[SessionInfo]` - List of all active SessionInfo objects

**Features:**
- Automatic conversation history management using `--continue` flag
- Isolated working directories per session
- Graceful PTY error handling
- Session-specific environment configuration

---

### 2. SessionInfo

**File:** `session_manager.py`

Data class containing metadata for a Claude CLI session.

#### Dataclass: `SessionInfo`

```python
@dataclass
class SessionInfo:
    session_id: str
    name: str
    pty_handler: PTYHandler
    created_at: float
    working_directory: str
```

**Fields:**
- `session_id: str` - Unique UUID for the session
- `name: str` - Human-readable session name
- `pty_handler: PTYHandler` - PTY process handler
- `created_at: float` - Unix timestamp of creation
- `working_directory: str` - Session's working directory path

---

### 3. ClipboardManager

**File:** `clipboard.py`

Platform-specific clipboard operations with fallback support.

#### Class: `ClipboardManager`

```python
class ClipboardManager:
    def __init__(self)
```

**Methods:**

##### `copy_to_system(text: str) -> bool`
Copies text to system clipboard.

**Parameters:**
- `text: str` - Text to copy

**Returns:**
- `bool` - True if successful, False otherwise

**Example:**
```python
clipboard = ClipboardManager()
success = clipboard.copy_to_system("Hello, world!")
```

##### `get_from_system() -> str`
Gets text from system clipboard.

**Returns:**
- `str` - Clipboard text or empty string on failure

**Example:**
```python
text = clipboard.get_from_system()
```

##### `paste_from_system() -> str`
Alias for `get_from_system()`.

**Platform Support:**
- **macOS**: Uses `pbcopy`/`pbpaste`
- **Linux**: Uses `xclip` or `xsel` (with fallback)
- **Windows**: Not currently supported (returns False/empty string)

---

### 4. TranscriptExporter

**File:** `export.py`

Handles exporting session transcripts to various formats.

#### Class: `TranscriptExporter`

```python
class TranscriptExporter:
    def __init__(self, export_dir: Optional[str] = None)
```

**Parameters:**
- `export_dir: Optional[str]` - Directory for exports (defaults to `~/claude-exports/`)

**Methods:**

##### `export_to_markdown(messages, session_name, filename) -> str`
Exports conversation to Markdown format.

**Parameters:**
- `messages: List[ConversationMessage]` - List of conversation messages
- `session_name: str` - Name of the session
- `filename: Optional[str]` - Custom filename (without extension)

**Returns:**
- `str` - Path to the exported file

**Example:**
```python
exporter = TranscriptExporter()
messages = exporter.parse_transcript(raw_text)
filepath = exporter.export_to_markdown(
    messages,
    session_name="My Session",
    filename="conversation_backup"
)
```

##### `export_to_text(output_lines, filepath) -> bool`
Exports output lines to text file.

**Parameters:**
- `output_lines: List[str]` - List of output lines
- `filepath: Path` - Path object for output file

**Returns:**
- `bool` - True if successful, False otherwise

**Example:**
```python
from pathlib import Path

exporter = TranscriptExporter()
success = exporter.export_to_text(
    output_lines=["Line 1", "Line 2", "Line 3"],
    filepath=Path("/tmp/output.txt")
)
```

##### `export_to_json(messages, session_name, session_id, filename, metadata) -> str`
Exports conversation to JSON format.

**Parameters:**
- `messages: List[ConversationMessage]` - List of conversation messages
- `session_name: str` - Name of the session
- `session_id: str` - Session UUID
- `filename: Optional[str]` - Custom filename (without extension)
- `metadata: Optional[Dict[str, Any]]` - Additional metadata

**Returns:**
- `str` - Path to the exported file

##### `parse_transcript(raw_text: str) -> List[ConversationMessage]`
Parses raw transcript text into structured messages.

**Parameters:**
- `raw_text: str` - Raw text from terminal output

**Returns:**
- `List[ConversationMessage]` - Structured conversation messages

**Supported Formats:**
- Markdown (`.md`) - Human-readable with timestamps
- JSON (`.json`) - Structured data for programmatic access
- Plain text (`.txt`) - Raw transcript with header

---

### 5. Utility Functions

#### `sanitize_filename(name: str) -> str`

**File:** `export.py`

Sanitizes a string for use as a filename.

**Parameters:**
- `name: str` - Raw string to sanitize

**Returns:**
- `str` - Sanitized filename-safe string

**Features:**
- Removes invalid filename characters (`<>:"/\|?*`)
- Strips leading/trailing spaces and dots
- Limits length to 200 characters
- Returns 'unnamed' if empty after sanitization

**Example:**
```python
from claude_multi_terminal.core import sanitize_filename

safe_name = sanitize_filename("My:Project/Name")  # Returns: "My_Project_Name"
```

---

## Usage Examples

### Complete Session Workflow

```python
from claude_multi_terminal.core import SessionManager, ClipboardManager, TranscriptExporter
from pathlib import Path

# Initialize components
manager = SessionManager()
clipboard = ClipboardManager()
exporter = TranscriptExporter()

# Create a new session
session_id = manager.create_session(
    name="Data Analysis",
    working_dir="/Users/me/projects/data"
)

# Get session info
session = manager.get_session(session_id)
print(f"Session: {session.name}")
print(f"Working dir: {session.working_directory}")

# List all sessions
all_sessions = manager.list_sessions()
print(f"Active sessions: {len(all_sessions)}")

# Copy session info to clipboard
clipboard.copy_to_system(f"Session ID: {session_id}")

# Export transcript
output_lines = ["Output line 1", "Output line 2", "Output line 3"]
export_path = Path(f"/tmp/session_{session_id}.txt")
success = exporter.export_to_text(output_lines, export_path)

if success:
    print(f"Exported to: {export_path}")

# Cleanup
await manager.terminate_session(session_id)
```

### Clipboard Operations

```python
from claude_multi_terminal.core import ClipboardManager

clipboard = ClipboardManager()

# Copy text
success = clipboard.copy_to_system("Hello, clipboard!")
if success:
    print("Copied successfully")

# Retrieve text
text = clipboard.get_from_system()
print(f"Clipboard contains: {text}")
```

### Export Transcript

```python
from claude_multi_terminal.core import TranscriptExporter, sanitize_filename

exporter = TranscriptExporter(export_dir="/tmp/exports")

# Parse and export to Markdown
raw_text = "..."  # Raw transcript text
messages = exporter.parse_transcript(raw_text)

md_path = exporter.export_to_markdown(
    messages=messages,
    session_name="My Session",
    filename=sanitize_filename("My Session Backup")
)

print(f"Exported to: {md_path}")

# Export to JSON with metadata
json_path = exporter.export_to_json(
    messages=messages,
    session_name="My Session",
    session_id="uuid-here",
    metadata={"tags": ["research", "data-analysis"]}
)

print(f"JSON export: {json_path}")
```

---

## Error Handling

All components implement graceful error handling:

### SessionManager
- Returns `None` from `get_session()` if session doesn't exist
- PTY errors are logged and handled gracefully
- Session termination is safe even if process already terminated

### ClipboardManager
- Returns `False` from `copy_to_system()` on failure
- Returns empty string from `get_from_system()` on failure
- Platform detection fallback for unsupported systems

### TranscriptExporter
- Creates export directory automatically if it doesn't exist
- Returns `False` from `export_to_text()` on file write errors
- Sanitizes filenames to prevent filesystem errors
- Handles UTF-8 encoding issues gracefully

---

## Type Hints

All components use comprehensive type hints:

```python
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from pathlib import Path
```

This enables:
- IDE autocompletion
- Static type checking with mypy
- Better code documentation
- Runtime type validation (optional)

---

## Dependencies

### Required
- `ptyprocess` - PTY process management
- Python 3.7+ (for dataclasses)

### Platform-specific
- macOS: `pbcopy`, `pbpaste` (built-in)
- Linux: `xclip` or `xsel` (optional)

---

## Testing

Run the verification script:

```bash
cd /Users/wallonwalusayi/claude-multi-terminal
source venv/bin/activate
python verify_core_module.py
```

This validates:
- All imports are successful
- Required methods exist
- Type signatures are correct
- Basic functionality works

---

## Design Principles

### 1. Separation of Concerns
Each component has a single, well-defined responsibility:
- `SessionManager` - Session lifecycle only
- `ClipboardManager` - Clipboard operations only
- `TranscriptExporter` - Export functionality only

### 2. Graceful Degradation
All components handle failures gracefully:
- Return sensible defaults (False, None, empty string)
- Log errors for debugging
- Never raise exceptions to calling code

### 3. Type Safety
Comprehensive type hints enable:
- Static analysis
- IDE support
- Self-documenting code

### 4. Platform Independence
Components detect and adapt to the platform:
- Clipboard uses platform-specific tools
- Filesystem operations use `pathlib.Path`
- PTY management handles OS differences

### 5. Testability
All components are easily testable:
- Minimal dependencies
- Clear interfaces
- Predictable behavior

---

## Future Enhancements

Possible improvements:
- Windows clipboard support
- Session persistence (save/restore)
- Export to additional formats (HTML, PDF)
- Session templates
- Batch export operations
- Session search/filter capabilities

---

## Coding Standards

Following CLAUDE.md guidelines:
- Type hints on all public methods
- Comprehensive docstrings
- Error handling with try/except
- No emoji usage (per CLAUDE.md)
- PEP 8 compliance
- Clear variable names
- Modular design

---

## Support

For issues or questions:
1. Check this documentation first
2. Review the verification script: `verify_core_module.py`
3. Examine test files in the tests directory
4. Check individual file docstrings for implementation details
