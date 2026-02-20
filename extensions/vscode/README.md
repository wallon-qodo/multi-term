# Claude Multi-Terminal VSCode Extension

Bidirectional integration between Claude Multi-Terminal and Visual Studio Code.

## Features

- **Open Files**: Open files in VSCode directly from Claude conversations
- **Jump to Lines**: Navigate to specific line numbers instantly
- **Apply Changes**: Automatically apply code changes suggested by Claude
- **Context Sync**: Sync your VSCode context (active file, selection) to Claude
- **Change Highlighting**: Visual feedback when changes are applied
- **Auto-Sync**: Automatically notify Claude of file changes

## Installation

### From Source

```bash
cd extensions/vscode
npm install
npm run build
code --install-extension claude-multi-terminal-vscode-0.1.0.vsix
```

### From Marketplace

(Coming soon)

## Setup

1. Install the extension
2. The integration server will start automatically (default port: 8765)
3. Connect from Claude Multi-Terminal Python side

## Configuration

Open VSCode Settings (`Cmd/Ctrl + ,`) and search for "Claude Multi-Terminal":

| Setting | Description | Default |
|---------|-------------|---------|
| `claude-multi-terminal.serverPort` | WebSocket server port | 8765 |
| `claude-multi-terminal.autoStartServer` | Auto-start server on VSCode launch | true |
| `claude-multi-terminal.autoSync` | Auto-sync file changes to Claude | true |
| `claude-multi-terminal.highlightChanges` | Highlight applied changes | true |

## Commands

Access via Command Palette (`Cmd/Ctrl + Shift + P`):

- **Claude: Open File** - Open a file by path
- **Claude: Apply Changes** - Apply changes from Claude
- **Claude: Sync Context** - Send current context to Claude
- **Claude: Jump to Line** - Jump to specific line
- **Claude: Start Integration Server** - Start WebSocket server
- **Claude: Stop Integration Server** - Stop WebSocket server

## Usage

### From Claude Multi-Terminal (Python)

```python
import asyncio
from claude_multi_terminal.integrations.vscode_connector import VSCodeConnector
from pathlib import Path

async def main():
    vscode = VSCodeConnector()
    await vscode.connect()

    # Open file at specific line
    await vscode.open_file(Path("src/main.py"), line=42)

    await vscode.disconnect()

asyncio.run(main())
```

### Synchronous Usage

```python
from claude_multi_terminal.integrations.vscode_connector import VSCodeSync

vscode = VSCodeSync()
vscode.connect()
vscode.open_file(Path("src/main.py"), line=42)
vscode.disconnect()
```

## Message Protocol

The extension communicates via WebSocket using JSON messages.

### Message Types

#### From Python to VSCode

**openFile**
```json
{
  "type": "openFile",
  "filePath": "/path/to/file.py",
  "line": 42,
  "column": 10,
  "id": 123
}
```

**applyChanges**
```json
{
  "type": "applyChanges",
  "filePath": "/path/to/file.py",
  "changes": [
    {
      "startLine": 10,
      "endLine": 15,
      "startColumn": 0,
      "endColumn": 0,
      "newText": "# New code\n"
    }
  ],
  "description": "Refactor function",
  "id": 124
}
```

**jumpToLine**
```json
{
  "type": "jumpToLine",
  "filePath": "/path/to/file.py",
  "line": 100,
  "column": 5,
  "id": 125
}
```

**getContext**
```json
{
  "type": "getContext",
  "id": 126
}
```

**ping**
```json
{
  "type": "ping",
  "id": 127
}
```

#### From VSCode to Python

**connected**
```json
{
  "type": "connected",
  "version": "0.1.0"
}
```

**fileOpened**
```json
{
  "type": "fileOpened",
  "filePath": "/path/to/file.py",
  "success": true,
  "messageId": 123
}
```

**changesApplied**
```json
{
  "type": "changesApplied",
  "filePath": "/path/to/file.py",
  "success": true,
  "changesCount": 3,
  "messageId": 124
}
```

**context**
```json
{
  "type": "context",
  "context": {
    "activeFile": "/path/to/file.py",
    "workspaceRoot": "/path/to/project",
    "openFiles": ["/path/to/file1.py", "/path/to/file2.py"],
    "selection": {
      "start": { "line": 10, "column": 0 },
      "end": { "line": 15, "column": 20 },
      "text": "selected code"
    }
  },
  "messageId": 126
}
```

**fileChanged** (auto-sync)
```json
{
  "type": "fileChanged",
  "filePath": "/path/to/file.py",
  "timestamp": 1704067200000
}
```

**error**
```json
{
  "type": "error",
  "error": "File not found",
  "messageId": 123
}
```

## Status Bar

The extension adds a status bar item showing connection status:

- `✓ Claude: Connected` (green) - Connected to Claude Multi-Terminal
- `⊘ Claude: Disconnected` (yellow) - Not connected

Click the status bar item for more information.

## Output Channel

View extension logs in the Output panel:

1. Open Output panel: `View > Output`
2. Select "Claude Multi-Terminal" from dropdown

## Troubleshooting

### Extension Not Connecting

1. Check if server is running:
   ```bash
   lsof -i :8765
   ```

2. Verify port in settings matches Python side:
   ```python
   vscode = VSCodeConnector(port=8765)  # Must match
   ```

3. Check firewall settings

4. Review extension logs in Output panel

### Changes Not Applying

1. Ensure file is saved before applying changes
2. Check file path is absolute
3. Verify line numbers are 1-indexed
4. Review error in Output panel

### Auto-Sync Not Working

1. Verify `autoSync` setting is enabled
2. Check Python side has event listener:
   ```python
   async def on_file_changed(data):
       print(f"File changed: {data['filePath']}")

   vscode.on_event("fileChanged", on_file_changed)
   ```

3. Ensure connection is active

## Development

### Build Extension

```bash
cd extensions/vscode
npm install
npm run lint
npm run test
```

### Debug Extension

1. Open `extensions/vscode` in VSCode
2. Press F5 to launch Extension Development Host
3. Test extension in new window

### Package Extension

```bash
npm install -g vsce
vsce package
# Produces: claude-multi-terminal-vscode-0.1.0.vsix
```

## Requirements

- VSCode 1.85.0 or higher
- Node.js 20.x or higher (for development)

## Dependencies

- `ws` ^8.14.0 - WebSocket client/server

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- GitHub Issues: https://github.com/wallonwalusayi/claude-multi-terminal/issues
- Documentation: https://github.com/wallonwalusayi/claude-multi-terminal/blob/main/docs/

## Changelog

### 0.1.0 (2026-02-20)

- Initial release
- Open files with line navigation
- Apply code changes
- Context synchronization
- Auto-sync file changes
- Change highlighting
- Status bar integration
