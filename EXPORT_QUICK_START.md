# Export Feature - Quick Start Guide

## TL;DR

Export your Claude Multi-Terminal conversations with one command:

```bash
/export              # Export as Markdown (default)
/export json         # Export as JSON
/export text         # Export as plain text
```

Or right-click and select "Export Session..." from the context menu.

Files are saved to: `~/claude-exports/`

---

## Common Use Cases

### 1. Save a Debugging Session

```bash
/export markdown debug_session
```
Creates: `~/claude-exports/debug_session.md`

### 2. Export for Analysis

```bash
/export json analysis_data
```
Creates: `~/claude-exports/analysis_data.json`

### 3. Quick Backup

```bash
/export
```
Creates: `~/claude-exports/session_<name>_<timestamp>.md`

---

## Format Comparison

| Format | Best For | File Size | Features |
|--------|----------|-----------|----------|
| **Markdown** | Documentation, sharing | Medium | Syntax highlighting, readable |
| **JSON** | Automation, analysis | Large | Structured, programmatic access |
| **Text** | Simple backup | Small | Plain text, minimal formatting |

---

## What Gets Exported

- ✅ All commands you entered
- ✅ All Claude responses
- ✅ Timestamps for each exchange
- ✅ Code blocks with syntax
- ✅ Session metadata (command count, etc.)
- ✅ Visual formatting (in Markdown)

---

## Command Syntax

```
/export [format] [filename]
```

**Parameters:**
- `format` (optional): `markdown`, `json`, or `text`
- `filename` (optional): Custom name without extension

**Examples:**
```bash
/export                           # Default Markdown export
/export json                      # JSON format
/export markdown my_session       # Custom filename
/export json important_convo      # JSON with custom name
```

---

## Context Menu

1. **Right-click** anywhere in the session output
2. Select **"Export Session..."**
3. Choose format:
   - Export as Markdown
   - Export as JSON
   - Export as Text

---

## Tips & Tricks

### Naming Conventions

Use descriptive filenames:
```bash
/export markdown project_planning_2026_01_30
/export json bug_investigation_session
```

### Large Sessions

Export handles large sessions (1000+ messages) efficiently:
- No performance degradation
- Streams to disk to avoid memory issues
- Progress shown in notifications

### Automation

For programmatic access, use JSON format:

```python
import json

with open('~/claude-exports/session_xxx.json', 'r') as f:
    data = json.load(f)
    for msg in data['messages']:
        print(f"{msg['type']}: {msg['content'][:50]}...")
```

---

## Troubleshooting

### "No conversation to export"
- You need at least one command/response exchange
- Empty sessions cannot be exported

### Permission Denied
- Check write permissions for `~/claude-exports/`
- Or specify a different directory in settings

### Filename Too Long
- Use shorter custom filename
- OS limits filename length to ~200 characters

---

## Default Export Directory

All exports go to: `~/claude-exports/`

**macOS/Linux:** `/Users/username/claude-exports/`
**Windows:** `C:\Users\username\claude-exports\`

The directory is automatically created if it doesn't exist.

---

## Need More Help?

See the full documentation: [EXPORT_FEATURE.md](EXPORT_FEATURE.md)

Or type `/help` in any session for available commands.

---

**Happy Exporting!** 📦
