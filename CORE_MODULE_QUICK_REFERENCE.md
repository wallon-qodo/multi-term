# Core Module Quick Reference

## Import Statement

```python
from claude_multi_terminal.core import (
    SessionManager,
    SessionInfo,
    ClipboardManager,
    TranscriptExporter,
    sanitize_filename
)
```

## SessionManager

```python
# Initialize
manager = SessionManager()

# Create session
session_id = manager.create_session(
    name="My Session",              # Optional: defaults to "Session N"
    working_dir="/path/to/dir",     # Optional: auto-generated if None
    claude_args=["--flag"]           # Optional: additional CLI args
)

# Get session
session = manager.get_session(session_id)  # Returns SessionInfo or None

# List all sessions
sessions = manager.list_sessions()  # Returns List[SessionInfo]

# Terminate session (async)
await manager.terminate_session(session_id)
```

## SessionInfo (Dataclass)

```python
session = manager.get_session(session_id)
print(session.session_id)        # str: UUID
print(session.name)              # str: Human-readable name
print(session.working_directory) # str: Working directory path
print(session.created_at)        # float: Unix timestamp
print(session.pty_handler)       # PTYHandler: Process handler
```

## ClipboardManager

```python
# Initialize
clipboard = ClipboardManager()

# Copy to clipboard
success = clipboard.copy_to_system("text to copy")  # Returns bool

# Get from clipboard
text = clipboard.get_from_system()  # Returns str (empty on failure)

# Alternative method (same as get_from_system)
text = clipboard.paste_from_system()
```

## TranscriptExporter

```python
# Initialize
exporter = TranscriptExporter()
# Or with custom directory:
exporter = TranscriptExporter(export_dir="/custom/path")

# Export to text file
from pathlib import Path
success = exporter.export_to_text(
    output_lines=["line1", "line2", "line3"],
    filepath=Path("/tmp/output.txt")
)  # Returns bool

# Parse transcript
messages = exporter.parse_transcript(raw_text)  # Returns List[ConversationMessage]

# Export to Markdown
md_path = exporter.export_to_markdown(
    messages=messages,
    session_name="My Session",
    filename="backup"  # Optional, auto-generated if None
)  # Returns str (file path)

# Export to JSON
json_path = exporter.export_to_json(
    messages=messages,
    session_name="My Session",
    session_id="uuid-here",
    filename="backup",  # Optional
    metadata={"tags": ["research"]}  # Optional
)  # Returns str (file path)
```

## sanitize_filename

```python
# Sanitize filename
safe_name = sanitize_filename("My:Unsafe/Filename")  # Returns "My_Unsafe_Filename"
```

## Common Patterns

### Create and Use Session

```python
manager = SessionManager()
session_id = manager.create_session(name="Data Analysis")
session = manager.get_session(session_id)

# Use session...
# Write to PTY: await session.pty_handler.write("command\n")

# Cleanup
await manager.terminate_session(session_id)
```

### Export Workflow

```python
exporter = TranscriptExporter()
clipboard = ClipboardManager()

# Get transcript
output_lines = ["Output line 1", "Output line 2"]

# Export to file
from pathlib import Path
filepath = Path(f"/tmp/{sanitize_filename(session_name)}.txt")
success = exporter.export_to_text(output_lines, filepath)

# Copy to clipboard
if success:
    clipboard.copy_to_system(f"Exported to: {filepath}")
```

### Complete Example

```python
from claude_multi_terminal.core import (
    SessionManager,
    ClipboardManager,
    TranscriptExporter,
    sanitize_filename
)
from pathlib import Path
import asyncio

async def main():
    # Setup
    manager = SessionManager()
    clipboard = ClipboardManager()
    exporter = TranscriptExporter()

    # Create session
    session_id = manager.create_session(name="Test Session")
    session = manager.get_session(session_id)

    print(f"Created: {session.name}")
    print(f"Working dir: {session.working_directory}")

    # Simulate some work...
    output = ["Line 1", "Line 2", "Line 3"]

    # Export
    safe_name = sanitize_filename(session.name)
    filepath = Path(f"/tmp/{safe_name}.txt")
    success = exporter.export_to_text(output, filepath)

    if success:
        print(f"Exported to: {filepath}")
        clipboard.copy_to_system(str(filepath))

    # Cleanup
    await manager.terminate_session(session_id)

# Run
asyncio.run(main())
```

## Error Handling

All methods handle errors gracefully:

```python
# Returns None if not found
session = manager.get_session("invalid-id")  # None

# Returns False on failure
success = clipboard.copy_to_system("text")  # False if clipboard unavailable

# Returns empty string on failure
text = clipboard.get_from_system()  # "" if clipboard unavailable

# Returns False on failure
success = exporter.export_to_text(lines, path)  # False if write fails
```

## Type Hints

All methods use type hints for IDE support:

```python
def create_session(
    self,
    name: Optional[str] = None,
    working_dir: Optional[str] = None,
    claude_args: Optional[list] = None
) -> str:
    ...

def get_session(self, session_id: str) -> Optional[SessionInfo]:
    ...

def copy_to_system(self, text: str) -> bool:
    ...

def export_to_text(self, output_lines: List[str], filepath: Path) -> bool:
    ...
```

## Platform Support

- **macOS**: Full support (pbcopy/pbpaste)
- **Linux**: Full support (xclip/xsel with fallback)
- **Windows**: Partial support (clipboard operations not supported)

## Dependencies

- Python 3.7+ (for dataclasses)
- ptyprocess
- asyncio (standard library)
- pathlib (standard library)
- subprocess (standard library)

## Files Location

```
/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/core/
├── __init__.py              # Exports
├── session_manager.py       # SessionManager, SessionInfo
├── clipboard.py            # ClipboardManager
├── export.py               # TranscriptExporter, sanitize_filename
└── pty_handler.py          # PTYHandler (used by SessionManager)
```

## Verification

Run verification script:

```bash
cd /Users/wallonwalusayi/claude-multi-terminal
source venv/bin/activate
python verify_core_module.py
```

## Documentation

Full documentation: `/Users/wallonwalusayi/claude-multi-terminal/CORE_MODULE_DOCUMENTATION.md`
