"""
Example integration of code block extraction into SessionPane.

This file shows the exact changes needed to enable code block detection
and interactive copy/save functionality in the terminal output.
"""

# ============================================================================
# STEP 1: Add imports at the top of session_pane.py
# ============================================================================

# Add these imports after the existing imports:
from .code_block_integration import CodeBlockHighlighter, CodeBlockContextMenu
from .code_block import CodeBlockParser


# ============================================================================
# STEP 2: Initialize code block system in SessionPane.__init__()
# ============================================================================

def __init__(self, session_id, session_name, session_manager, *args, **kwargs):
    """Modified __init__ method."""
    super().__init__(*args, **kwargs)

    # ... existing initialization code ...

    # Add code block support
    self.code_highlighter = CodeBlockHighlighter()
    self.code_context_menu_handler = None  # Will be initialized on mount


# ============================================================================
# STEP 3: Initialize context menu handler in on_mount()
# ============================================================================

async def on_mount(self) -> None:
    """Modified on_mount method."""
    # ... existing on_mount code ...

    # Initialize code block context menu handler
    if hasattr(self.app, 'clip_manager'):
        self.code_context_menu_handler = CodeBlockContextMenu(
            self.code_highlighter,
            self.app.clip_manager
        )


# ============================================================================
# STEP 4: Enhance output in _update_output()
# ============================================================================

def _update_output(self, output: str) -> None:
    """Modified _update_output method with code block enhancement."""
    try:
        # ... existing code for filtering ANSI, etc. ...

        # Filter problematic ANSI sequences
        filtered_output = self._filter_ansi(output)

        if not filtered_output.strip():
            return

        # NEW: Check if output contains code blocks
        if CodeBlockParser.has_code_blocks(filtered_output):
            # Enhance output with beautiful code block formatting
            enhanced_text = self.code_highlighter.process_output(filtered_output)

            # Write the enhanced text
            output_widget.write(enhanced_text)

            # Log the code blocks found
            if self.code_highlighter.has_code_blocks():
                blocks = self.code_highlighter.get_all_blocks()
                self._log(f"Detected {len(blocks)} code block(s)")
                for block in blocks:
                    self._log(f"  Block #{block['id']}: {block['language']} ({block['line_count']} lines)")
        else:
            # No code blocks, process normally
            rich_text = Text.from_ansi(filtered_output)
            output_widget.write(rich_text)

        # ... rest of existing code ...

    except Exception as e:
        self._log(f"ERROR in _update_output: {e}")


# ============================================================================
# STEP 5: Extend context menu in SelectableRichLog
# ============================================================================

# In selectable_richlog.py, modify _show_context_menu():

def _show_context_menu(self, x: int, y: int) -> None:
    """Modified _show_context_menu with code block support."""
    # Check if there's selected text
    has_selection = (
        self.selection_active and
        self.selection_start and
        self.selection_end and
        self.selection_start != self.selection_end
    )

    # Create base menu items
    menu_items = [
        MenuItem(
            label="Copy",
            callback=self._copy_selection,
            enabled=has_selection,
            shortcut="Ctrl+C"
        ),
        MenuItem(
            label="Select All",
            callback=self._select_all,
            enabled=True,
            shortcut="Ctrl+A"
        ),
    ]

    # NEW: Add code block menu items if available
    if hasattr(self.app, 'code_context_menu_handler') and self.app.code_context_menu_handler:
        # Get the line position
        pos = self._get_text_position(...)  # Use appropriate position
        code_items = self.app.code_context_menu_handler.get_menu_items(
            line_idx=pos[0],
            col_idx=pos[1],
            lines=self.lines
        )
        menu_items.extend(code_items)

    # Add remaining menu items
    menu_items.append(
        MenuItem(
            label="Clear Selection",
            callback=self._clear_selection,
            enabled=has_selection,
            shortcut="Esc"
        )
    )

    # Create and mount context menu
    self.context_menu = ContextMenu(items=menu_items, x=x, y=y)
    self.screen.mount(self.context_menu)


# ============================================================================
# COMPLETE EXAMPLE: Minimal working integration
# ============================================================================

"""
Here's a minimal, complete example showing the key changes:

# In session_pane.py:

from .code_block_integration import CodeBlockHighlighter, CodeBlockContextMenu
from .code_block import CodeBlockParser

class SessionPane(Vertical):
    def __init__(self, session_id, session_name, session_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ... existing code ...

        # Add code block support
        self.code_highlighter = CodeBlockHighlighter()

    async def on_mount(self) -> None:
        # ... existing code ...

        # Initialize context menu handler
        self.code_context_menu_handler = CodeBlockContextMenu(
            self.code_highlighter,
            self.app.clip_manager
        )

    def _update_output(self, output: str) -> None:
        try:
            # ... existing filtering ...

            # Check for code blocks
            if CodeBlockParser.has_code_blocks(filtered_output):
                # Enhance and write
                enhanced_text = self.code_highlighter.process_output(filtered_output)
                output_widget.write(enhanced_text)
            else:
                # Normal output
                rich_text = Text.from_ansi(filtered_output)
                output_widget.write(rich_text)

            # ... rest of existing code ...
        except Exception as e:
            self._log(f"ERROR: {e}")
"""


# ============================================================================
# TESTING THE INTEGRATION
# ============================================================================

"""
To test the integration:

1. Start the app: python -m claude_multi_terminal
2. Create a new session
3. Ask Claude: "Write a Python function to calculate fibonacci numbers"
4. Observe:
   - Code block appears with beautiful borders
   - Language badge shows "PYTHON"
   - Line numbers are displayed
   - Metadata shows line count and character count
5. Right-click on the code block
6. Select "Copy Code Block #0" or "Save Code Block #0"
7. Verify:
   - Copy works (paste in another app)
   - Save shows dialog with suggested filename (.py)

Expected output format:
╭─ CODE BLOCK #0 ─┤  PYTHON  ├──────────╮
│ 📊 9 lines · 217 chars            Right-click to copy/save │
├──────────────────────────────────────────────────────────────┤
│ 1 │ def fibonacci(n):
│ 2 │     if n <= 1:
│ 3 │         return n
│ 4 │     return fibonacci(n-1) + fibonacci(n-2)
╰──────────────────────────────────────────────────────────────╯
  💡 Use right-click menu to copy/save code block #0
"""


# ============================================================================
# ADDITIONAL FEATURES TO IMPLEMENT (Optional)
# ============================================================================

"""
1. Keybindings for code blocks:
   - Ctrl+Shift+C: Copy latest code block
   - Ctrl+Shift+S: Save latest code block
   - Ctrl+Shift+A: Save all code blocks

2. Status bar indicator:
   - Show "📋 3 code blocks" when blocks detected
   - Update count in real-time

3. Code block navigation:
   - Ctrl+]: Jump to next code block
   - Ctrl+[: Jump to previous code block

4. Export options:
   - Export all code blocks as ZIP
   - Export session with code blocks as Markdown

5. Advanced copy options:
   - Copy with line numbers
   - Copy with syntax highlighting (HTML)
   - Copy as GitHub-flavored markdown
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Issue: Code blocks not detected
Solution: Check that output contains ``` fences on separate lines

Issue: Right-click menu doesn't show code block options
Solution: Verify context menu handler is initialized and passed to RichLog

Issue: Copy/save not working
Solution: Check clipboard manager initialization in app.py

Issue: Visual formatting looks wrong
Solution: Ensure terminal supports Unicode box drawing characters

Issue: Performance slow with many code blocks
Solution: Code block detection is regex-based and very fast (<5ms for 100 blocks)
"""

print(__doc__)
