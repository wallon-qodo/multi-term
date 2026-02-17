# Code Block Extraction - Integration Guide

## Overview

The code block extraction system automatically detects, highlights, and enables interactive copy/save operations for code blocks in Claude's responses. This document explains the architecture and how to integrate it.

## Architecture

### Core Components

1. **CodeBlock Widget** (`widgets/code_block.py`)
   - Interactive widget for displaying code blocks
   - Hover-activated copy/save buttons
   - Syntax highlighting using Rich Syntax
   - Line numbers and metadata display
   - Beautiful Homebrew theme styling

2. **CodeBlockParser** (`widgets/code_block.py`)
   - Detects fenced code blocks (```language...```)
   - Extracts language and code content
   - Returns structured data for rendering

3. **CodeBlockHighlighter** (`widgets/code_block_integration.py`)
   - Post-processes terminal output
   - Adds beautiful visual indicators around code blocks
   - Stores code block data for operations
   - Works with existing RichLog architecture

4. **SaveFileDialog** (`widgets/save_file_dialog.py`)
   - Modal dialog for saving code to files
   - Filename suggestions based on language
   - Working directory display
   - Input validation

## Visual Design

### Code Block Display

```
╭─ CODE BLOCK #0 ─┤  PYTHON  ├──────────╮
│ 📊 15 lines · 342 chars            Right-click to copy/save │
├──────────────────────────────────────────────────────────────┤
│  1 │ def hello_world():
│  2 │     print("Hello, World!")
│  3 │     return 42
╰──────────────────────────────────────────────────────────────╯
  💡 Use right-click menu to copy/save code block #0
```

### Features

- **Language Badge**: Colorful badge showing programming language
- **Metadata**: Line count and character count
- **Line Numbers**: Easy reference with syntax-highlighted code
- **Action Hints**: Clear instructions for user interaction
- **Border Styling**: Beautiful Unicode box drawing characters
- **Homebrew Theme**: Consistent with application color scheme

## Integration Methods

### Method 1: Visual Enhancement (Recommended)

This method adds visual indicators to code blocks without changing the core architecture.

**Advantages:**
- Works with existing RichLog
- No major refactoring needed
- Beautiful visual feedback
- Context menu integration

**Implementation:**

```python
from .code_block_integration import CodeBlockHighlighter, CodeBlockContextMenu

# In SessionPane.__init__():
self.code_highlighter = CodeBlockHighlighter()
self.code_context_menu = CodeBlockContextMenu(
    self.code_highlighter,
    self.app.clip_manager
)

# In SessionPane._update_output():
# Process output for code blocks
enhanced_text = self.code_highlighter.process_output(filtered_output)

# Write enhanced text
output_widget.write(enhanced_text)

# Update context menu to include code block operations
# (Extend the existing _show_context_menu method)
```

### Method 2: Widget-Based (Future Enhancement)

This method replaces code blocks with interactive CodeBlock widgets.

**Advantages:**
- True interactive widgets
- Hover-activated buttons
- More polished UX

**Limitations:**
- Requires switching from RichLog to VerticalScroll
- More complex integration
- May affect text selection

**Implementation:**

```python
from .enhanced_output import EnhancedOutputPane

# Replace SelectableRichLog with EnhancedOutputPane in session_pane.py
yield EnhancedOutputPane(
    classes="terminal-output",
    id=f"output-{self.session_id}"
)

# Write output
await output_widget.write_output(filtered_output)
```

## Usage Examples

### Detecting Code Blocks

```python
from claude_multi_terminal.widgets.code_block import CodeBlockParser

text = '''
Here's some Python code:

```python
def hello():
    print("Hello, World!")
```

And here's some JavaScript:

```javascript
console.log("Hello, World!");
```
'''

# Extract all code blocks
blocks = CodeBlockParser.extract_code_blocks(text)
# Returns: [('python', 'def hello():\n    print("Hello, World!")', 25, 78), ...]

# Check if text has code blocks
has_blocks = CodeBlockParser.has_code_blocks(text)
# Returns: True
```

### Creating Code Block Widgets

```python
from claude_multi_terminal.widgets.code_block import CodeBlock

# Create a code block widget
code_widget = CodeBlock(
    code='def hello():\n    print("Hello!")',
    language='python'
)

# Mount in your container
await self.mount(code_widget)
```

### Enhancing Output

```python
from claude_multi_terminal.widgets.code_block_integration import CodeBlockHighlighter

highlighter = CodeBlockHighlighter()

# Process output
enhanced = highlighter.process_output(raw_output)

# Check what blocks were found
if highlighter.has_code_blocks():
    blocks = highlighter.get_all_blocks()
    for block in blocks:
        print(f"Block {block['id']}: {block['language']} ({block['line_count']} lines)")
```

## Context Menu Integration

The code block system integrates with the existing right-click context menu:

1. When right-clicking within a code block, additional menu items appear
2. "📋 Copy Code Block #N" - copies the code to clipboard
3. "💾 Save Code Block #N" - opens save dialog

### Extending SelectableRichLog Context Menu

```python
# In SelectableRichLog._show_context_menu():

# Get code block menu items if applicable
code_items = []
if hasattr(self, 'code_context_menu'):
    code_items = self.code_context_menu.get_menu_items(
        line_idx=pos[0],
        col_idx=pos[1],
        lines=self.lines
    )

# Merge with existing menu items
menu_items = [
    MenuItem("Copy", self._copy_selection, has_selection),
    MenuItem("Select All", self._select_all, True),
    *code_items,  # Add code block items
    MenuItem("Clear Selection", self._clear_selection, has_selection),
]
```

## File Extensions by Language

The system automatically suggests file extensions based on detected language:

| Language   | Extension |
|------------|-----------|
| python     | .py       |
| javascript | .js       |
| typescript | .ts       |
| java       | .java     |
| cpp        | .cpp      |
| rust       | .rs       |
| go         | .go       |
| ruby       | .rb       |
| php        | .php      |
| swift      | .swift    |
| kotlin     | .kt       |
| bash       | .sh       |
| sql        | .sql      |
| html       | .html     |
| css        | .css      |
| json       | .json     |
| yaml       | .yaml     |
| markdown   | .md       |
| text       | .txt      |

## Color Scheme

All components use the Homebrew theme:

- **Primary**: rgb(255,183,77) - Orange/amber highlight
- **Secondary**: rgb(100,180,255) - Light blue accents
- **Background**: rgb(24,24,24) - Dark gray
- **Text**: rgb(224,224,224) - Light gray
- **Success**: rgb(76,175,80) - Green
- **Code**: rgb(129,212,250) - Cyan

## Testing

### Manual Testing

1. Start a Claude session
2. Ask Claude to write some code
3. Observe:
   - Beautiful code block borders appear
   - Language badge displays correctly
   - Line numbers and metadata show
   - Right-click menu includes "Copy Code Block" option
4. Test copy functionality
5. Test save functionality

### Test Cases

```python
# Test 1: Single code block
text = "```python\nprint('hello')\n```"
# Expected: 1 block detected, Python badge

# Test 2: Multiple code blocks
text = "```python\n...\n```\n\nSome text\n\n```javascript\n...\n```"
# Expected: 2 blocks detected, correct languages

# Test 3: No language specified
text = "```\nplain code\n```"
# Expected: 1 block detected, "TEXT" badge

# Test 4: Incomplete code block
text = "```python\nprint('hello')"
# Expected: No blocks detected (incomplete)

# Test 5: No code blocks
text = "Just some regular text"
# Expected: No blocks detected, text unchanged
```

## Performance Considerations

- **Regex Parsing**: Code block detection uses compiled regex (fast)
- **Streaming**: Handles streaming output gracefully
- **Memory**: Code blocks stored in memory (minimal overhead)
- **Rendering**: Visual enhancements add ~10-20 lines per block (negligible)

## Future Enhancements

1. **Inline Copy Button**: Small button in top-right of code block
2. **Language Auto-Detection**: Detect language if not specified
3. **Code Execution**: "Run" button for executable code
4. **Diff Highlighting**: Show code changes/edits
5. **Syntax Themes**: Multiple color schemes (monokai, github, etc.)
6. **Export All**: Save all code blocks in session to ZIP
7. **Search in Code**: Highlight search terms in code blocks
8. **Line Wrapping Toggle**: Enable/disable wrapping

## Troubleshooting

### Code blocks not detected

- Check if using correct fence markers (```)
- Ensure closing fence is on its own line
- Verify output hasn't been stripped

### Copy not working

- Verify clipboard manager is initialized
- Check platform-specific clipboard tools (pbcopy, xclip, xsel)
- Try "Copy to internal buffer" as fallback

### Styling issues

- Ensure terminal supports 24-bit color
- Check that Unicode box drawing characters render correctly
- Verify Homebrew theme CSS is loaded

## API Reference

### CodeBlockParser

```python
@classmethod
def extract_code_blocks(cls, text: str) -> list[tuple[str, str, int, int]]:
    """Extract all code blocks from text."""

@classmethod
def has_code_blocks(cls, text: str) -> bool:
    """Check if text contains any code blocks."""
```

### CodeBlock

```python
def __init__(self, code: str, language: str = "", **kwargs):
    """Create interactive code block widget."""
```

### CodeBlockHighlighter

```python
def process_output(self, text: str) -> Text:
    """Process output and enhance code blocks."""

def get_block(self, block_id: int) -> Optional[dict]:
    """Get code block data by ID."""

def has_code_blocks(self) -> bool:
    """Check if any blocks detected."""
```

### SaveFileDialog

```python
def __init__(self, suggested_name: str, code_content: str, **kwargs):
    """Create save dialog modal."""
```

## Contributing

When adding new language support:

1. Add language to extension_map in `code_block.py`
2. Test syntax highlighting with Rich Syntax
3. Update this documentation
4. Add test cases

## License

Same as main application (Claude Multi-Terminal).
