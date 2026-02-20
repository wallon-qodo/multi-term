# Phase 6: Smart Integrations

## Overview

Phase 6 adds powerful integrations with external tools and services, enabling seamless workflow between Claude Multi-Terminal and your development environment.

## Components

### 1. Git Integration

Provides AI-powered git operations including commit message generation and PR descriptions.

#### Features

- **Status & Diff**: Get current git status and visualize diffs
- **Commit Message Generation**: AI-powered commit messages based on changes
- **PR Description Generation**: Automatic pull request descriptions
- **Branch Management**: Create, checkout, and list branches
- **Commit History**: View and search commit logs
- **Diff Visualization**: Syntax-highlighted diff display

#### Usage

```python
from claude_multi_terminal.integrations.git import GitIntegration

# Initialize
git = GitIntegration(repo_path=Path("/path/to/repo"))

# Get status
status = git.get_status()
print(f"Branch: {status['branch']}")
print(f"Modified: {status['modified']}")
print(f"Staged: {status['staged']}")

# Generate commit message
message = git.generate_commit_message()
print(message)

# Create commit
git.create_commit(message)

# Generate PR description
pr_desc = git.generate_pr_description(base_branch="main")
print(pr_desc)

# Branch operations
git.create_branch("feature-branch")
git.checkout_branch("feature-branch")
branches = git.list_branches()
```

#### API Reference

**GitIntegration(repo_path: Optional[Path] = None)**
- `get_status() -> Dict[str, Any]` - Get current git status
- `get_diff(staged: bool = False, context: int = 3) -> str` - Get diff
- `get_log(count: int = 10, oneline: bool = False) -> List[Dict]` - Get commit log
- `generate_commit_message(diff: Optional[str] = None) -> str` - Generate commit message
- `create_commit(message: Optional[str] = None, auto_generate: bool = True) -> bool` - Create commit
- `generate_pr_description(base_branch: str = "main") -> str` - Generate PR description
- `visualize_diff(staged: bool = False) -> str` - Get visual diff
- `list_branches(include_remote: bool = False) -> List[str]` - List branches
- `create_branch(branch_name: str, checkout: bool = True) -> bool` - Create branch
- `checkout_branch(branch_name: str) -> bool` - Checkout branch
- `get_repository_info() -> Dict[str, Any]` - Get repo metadata

### 2. File Watcher

Real-time file system monitoring for automatic context updates.

#### Features

- **Change Detection**: Monitors file creation, modification, and deletion
- **Pattern Filtering**: Ignore specific files/patterns
- **Event Listeners**: Subscribe to file change events
- **Change History**: Track and query file change history
- **File Suggestions**: Smart file suggestions based on activity
- **Active File Tracking**: Identify recently modified files

#### Usage

```python
from claude_multi_terminal.integrations.file_watcher import FileWatcher, FileChange

# Initialize
watcher = FileWatcher(
    watch_path=Path("/path/to/project"),
    ignore_patterns=["*.pyc", "__pycache__", ".git"],
    poll_interval=1.0
)

# Add event listener
def on_change(change: FileChange):
    print(f"{change.change_type}: {change.path}")

watcher.add_listener(on_change)

# Start watching
watcher.start()

# Get pending changes
changes = watcher.get_changes()

# Get statistics
stats = watcher.get_statistics()
print(f"Watching {stats['watched_files']} files")
print(f"Total changes: {stats['total_changes']}")

# File suggestions
suggestions = watcher.suggest_files("module", limit=5)

# Get active files
active = watcher.get_active_files(since_minutes=60)

# Stop watching
watcher.stop()

# Or use as context manager
with FileWatcher(watch_path=path) as watcher:
    # Automatically starts and stops
    pass
```

#### API Reference

**FileWatcher(watch_path: Optional[Path], ignore_patterns: Optional[List[str]], poll_interval: float = 1.0)**
- `start() -> None` - Start watching
- `stop() -> None` - Stop watching
- `add_listener(callback: Callable) -> None` - Add change listener
- `remove_listener(callback: Callable) -> None` - Remove listener
- `get_changes(clear: bool = True) -> List[FileChange]` - Get pending changes
- `get_history(count: Optional[int] = None) -> List[FileChange]` - Get change history
- `get_statistics() -> Dict[str, Any]` - Get watcher statistics
- `suggest_files(query: str, limit: int = 10) -> List[Path]` - Suggest files
- `get_active_files(since_minutes: int = 60) -> List[Path]` - Get recently active files
- `get_recent_changes_by_type(change_type: str, count: int = 10) -> List[FileChange]` - Get changes by type

### 3. Terminal Integration

Execute commands and capture output with full history tracking.

#### Features

- **Command Execution**: Run shell commands with timeout support
- **Output Capture**: Capture stdout and stderr
- **Async Execution**: Run commands asynchronously
- **Command History**: Track and search command history
- **Input Support**: Execute commands with stdin input
- **Pipelines**: Execute command pipelines
- **Environment Variables**: Manage custom environment variables
- **Command Validation**: Validate commands before execution
- **Shell Completion**: Get completion suggestions

#### Usage

```python
from claude_multi_terminal.integrations.terminal import TerminalIntegration

# Initialize
terminal = TerminalIntegration(working_dir=Path("/path/to/project"))

# Execute command
result = terminal.execute("ls -la")
print(f"Exit code: {result.exit_code}")
print(f"Output: {result.stdout}")

# Execute with timeout
result = terminal.execute("long_running_command", timeout=10.0)

# Execute with input
result = terminal.execute_with_input("grep pattern", "line1\nline2\nline3")

# Execute pipeline
result = terminal.execute_pipeline([
    "find . -name '*.py'",
    "grep 'def '",
    "wc -l"
])

# Async execution
def on_complete(result):
    print(f"Command finished: {result.command}")

thread = terminal.execute_async("make build", callback=on_complete)

# Add output listener
def on_output(output):
    print(f"Output: {output}")

terminal.add_output_listener(on_output)

# Environment variables
terminal.set_env_var("MY_VAR", "value")

# Command history
history = terminal.history.get_all()
recent = terminal.history.get_recent(count=10)
search_results = terminal.history.search("git")

# Statistics
stats = terminal.get_history_statistics()
print(f"Success rate: {stats['success_rate']}%")

# Completion suggestions
suggestions = terminal.get_completion_suggestions("gi")

# Validate command
valid, error = terminal.validate_command("rm -rf /")
```

#### API Reference

**TerminalIntegration(working_dir: Optional[Path], shell: str = "/bin/bash")**
- `execute(command: str, timeout: Optional[float], capture_output: bool = True, check: bool = False) -> CommandResult`
- `execute_async(command: str, callback: Optional[Callable], timeout: Optional[float]) -> threading.Thread`
- `execute_with_input(command: str, input_data: str, timeout: Optional[float]) -> CommandResult`
- `execute_pipeline(commands: List[str], timeout: Optional[float]) -> CommandResult`
- `add_output_listener(callback: Callable) -> None`
- `remove_output_listener(callback: Callable) -> None`
- `set_env_var(name: str, value: str) -> None`
- `get_env_var(name: str) -> Optional[str]`
- `clear_env_vars() -> None`
- `get_completion_suggestions(partial_command: str) -> List[str]`
- `validate_command(command: str) -> tuple[bool, str]`
- `get_command_help(command: str) -> str`
- `change_directory(path: Path) -> bool`
- `get_working_directory() -> Path`
- `get_history_statistics() -> Dict[str, Any]`

### 4. VSCode Extension

Bidirectional integration with Visual Studio Code.

#### Features

- **Open Files**: Open files in VSCode from conversation
- **Jump to Line**: Navigate to specific lines
- **Apply Changes**: Automatically apply code changes
- **Context Sync**: Sync VSCode context to Claude
- **Change Highlighting**: Visual feedback for applied changes
- **File Watching**: Detect VSCode file changes
- **WebSocket Communication**: Real-time bidirectional messaging

#### Installation

```bash
# Install VSCode extension
cd extensions/vscode
npm install
npm run build

# Install in VSCode
code --install-extension claude-multi-terminal-vscode-0.1.0.vsix
```

#### Configuration

Open VSCode settings and configure:

```json
{
  "claude-multi-terminal.serverPort": 8765,
  "claude-multi-terminal.autoStartServer": true,
  "claude-multi-terminal.autoSync": true,
  "claude-multi-terminal.highlightChanges": true
}
```

#### Usage (VSCode Commands)

- `Claude: Open File` - Open file from path
- `Claude: Apply Changes` - Apply changes from Claude
- `Claude: Sync Context` - Sync current context to Claude
- `Claude: Jump to Line` - Jump to specific line
- `Claude: Start Integration Server` - Start WebSocket server
- `Claude: Stop Integration Server` - Stop WebSocket server

#### Usage (Python Side)

```python
import asyncio
from claude_multi_terminal.integrations.vscode_connector import VSCodeConnector, CodeChange
from pathlib import Path

async def main():
    # Initialize connector
    vscode = VSCodeConnector(host="localhost", port=8765)

    # Connect
    await vscode.connect()

    # Open file
    await vscode.open_file(Path("src/main.py"), line=42)

    # Apply changes
    changes = [
        CodeChange(
            start_line=10,
            end_line=10,
            new_text="# Updated function\n"
        )
    ]
    await vscode.apply_changes(Path("src/main.py"), changes)

    # Jump to line
    await vscode.jump_to_line(Path("src/main.py"), line=100)

    # Get context
    context = await vscode.get_context()
    print(f"Active file: {context['activeFile']}")

    # Disconnect
    await vscode.disconnect()

asyncio.run(main())
```

#### Synchronous Wrapper

```python
from claude_multi_terminal.integrations.vscode_connector import VSCodeSync

# Synchronous usage
vscode = VSCodeSync()
vscode.connect()
vscode.open_file(Path("src/main.py"), line=42)
vscode.disconnect()
```

#### API Reference

**VSCodeConnector(host: str = "localhost", port: int = 8765)**
- `async connect(timeout: float = 5.0) -> bool` - Connect to VSCode
- `async disconnect() -> None` - Disconnect
- `is_connected() -> bool` - Check connection status
- `async open_file(file_path: Path, line: Optional[int], column: Optional[int]) -> bool`
- `async apply_changes(file_path: Path, changes: List[CodeChange], description: Optional[str]) -> bool`
- `async jump_to_line(file_path: Path, line: int, column: int = 0) -> bool`
- `async get_context() -> Optional[Dict[str, Any]]`
- `async ping() -> bool` - Ping VSCode
- `on_event(event_type: str, handler: Callable) -> None` - Register event handler
- `remove_event_handler(event_type: str, handler: Callable) -> None`

## Integration Examples

### Example 1: Auto-Commit on File Save

```python
from claude_multi_terminal.integrations import FileWatcher, GitIntegration
from pathlib import Path

git = GitIntegration()
watcher = FileWatcher(poll_interval=2.0)

def on_file_change(change):
    if change.change_type == "modified":
        # Stage file
        git._run_git_command("add", str(change.path))

        # Generate and create commit
        message = git.generate_commit_message()
        git.create_commit(message)

watcher.add_listener(on_file_change)
watcher.start()
```

### Example 2: Run Tests on File Change

```python
from claude_multi_terminal.integrations import FileWatcher, TerminalIntegration

terminal = TerminalIntegration()
watcher = FileWatcher()

def on_python_file_change(change):
    if change.path.suffix == ".py" and change.change_type in ["created", "modified"]:
        # Run tests
        result = terminal.execute("pytest tests/", timeout=30)
        if result.success:
            print("✓ All tests passed")
        else:
            print("✗ Tests failed")

watcher.add_listener(on_python_file_change)
watcher.start()
```

### Example 3: VSCode Integration with Git

```python
import asyncio
from claude_multi_terminal.integrations import GitIntegration
from claude_multi_terminal.integrations.vscode_connector import VSCodeConnector

async def review_changes():
    git = GitIntegration()
    vscode = VSCodeConnector()

    await vscode.connect()

    # Get modified files
    status = git.get_status()

    for file in status["modified"]:
        # Open file in VSCode
        await vscode.open_file(Path(file))

        # Show diff
        diff = git.get_diff()
        print(diff)

        await asyncio.sleep(1)

    await vscode.disconnect()

asyncio.run(review_changes())
```

### Example 4: Smart Command Suggestions

```python
from claude_multi_terminal.integrations import TerminalIntegration

terminal = TerminalIntegration()

def get_smart_suggestions(partial: str):
    # Get completion suggestions
    suggestions = terminal.get_completion_suggestions(partial)

    # Validate suggestions
    valid = []
    for cmd in suggestions:
        is_valid, _ = terminal.validate_command(cmd)
        if is_valid:
            valid.append(cmd)

    return valid

suggestions = get_smart_suggestions("git ")
print(suggestions)
```

## Testing

Run integration tests:

```bash
# All integration tests
pytest tests/integrations/ -v

# Specific integration
pytest tests/integrations/test_git_integration.py -v
pytest tests/integrations/test_file_watcher.py -v
pytest tests/integrations/test_terminal_integration.py -v

# With coverage
pytest tests/integrations/ --cov=claude_multi_terminal.integrations
```

## Configuration

### File Watcher Configuration

```python
watcher = FileWatcher(
    watch_path=Path.cwd(),
    ignore_patterns=[
        "*.pyc",
        "__pycache__",
        ".git",
        ".pytest_cache",
        "*.log",
        ".DS_Store",
        "node_modules",
        "venv",
        ".venv",
        "build",
        "dist",
        "*.egg-info",
    ],
    poll_interval=1.0  # Check every second
)
```

### Terminal Configuration

```python
terminal = TerminalIntegration(
    working_dir=Path.cwd(),
    shell="/bin/bash"  # or "/bin/zsh", etc.
)

# Set environment variables
terminal.set_env_var("DEBUG", "1")
terminal.set_env_var("API_KEY", "secret")
```

### VSCode Configuration

```javascript
// In VSCode settings.json
{
  "claude-multi-terminal.serverPort": 8765,
  "claude-multi-terminal.autoStartServer": true,
  "claude-multi-terminal.autoSync": true,
  "claude-multi-terminal.highlightChanges": true
}
```

## Performance Considerations

### File Watcher
- Default poll interval: 1 second
- Checksums only computed for files < 1MB
- History limited to 100 most recent changes
- Automatically ignores common build artifacts

### Terminal Integration
- Default command timeout: None (no timeout)
- Async execution for long-running commands
- History limited to 1000 commands
- Output listeners run in separate threads

### VSCode Integration
- WebSocket connection with auto-reconnect
- Message timeout: 10 seconds
- Ping/pong for connection health
- Efficient JSON serialization

## Troubleshooting

### File Watcher Not Detecting Changes
- Check poll interval (increase for faster detection)
- Verify patterns are not ignored
- Ensure directory is readable
- Check thread is running: `watcher._running`

### Terminal Commands Timing Out
- Increase timeout parameter
- Use async execution for long commands
- Check command validity first
- Verify working directory exists

### VSCode Connection Failed
- Ensure extension is installed and running
- Check port is not in use: `lsof -i :8765`
- Verify firewall settings
- Check extension output logs

### Git Integration Issues
- Verify git repository exists
- Check git is installed: `git --version`
- Ensure proper git config (user.name, user.email)
- Verify repository is not corrupted

## Best Practices

1. **Use Context Managers**: Always use context managers for proper cleanup
   ```python
   with FileWatcher(path) as watcher:
       # Automatically starts and stops
       pass
   ```

2. **Validate Commands**: Always validate before execution
   ```python
   valid, error = terminal.validate_command(cmd)
   if valid:
       terminal.execute(cmd)
   ```

3. **Handle Timeouts**: Set appropriate timeouts for commands
   ```python
   result = terminal.execute(cmd, timeout=30.0)
   ```

4. **Check Connections**: Verify connections before operations
   ```python
   if vscode.is_connected():
       await vscode.open_file(path)
   ```

5. **Use Listeners Carefully**: Remove listeners when done
   ```python
   watcher.add_listener(callback)
   # ... use watcher ...
   watcher.remove_listener(callback)
   ```

## Future Enhancements

- [ ] LLM-powered commit message generation
- [ ] Jupyter notebook integration
- [ ] Docker container integration
- [ ] GitHub API integration
- [ ] Slack/Discord notifications
- [ ] Custom shell completions
- [ ] Advanced diff algorithms
- [ ] Multi-repository support

## Contributing

Contributions welcome! Please ensure:
- All tests pass
- New features have tests
- Documentation is updated
- Code follows project style

## License

MIT License - see LICENSE file for details
