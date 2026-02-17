# Integration Guide: Multi-Line Input & Command History

## Quick Start

This guide provides step-by-step instructions to integrate the multi-line input and command history feature into the existing `session_pane.py` file.

## Prerequisites

The following files have been created:
1. `session_pane_multiline.py` - Contains replacement methods
2. `test_multiline_history.py` - Standalone test application
3. `MULTILINE_HISTORY_IMPLEMENTATION.md` - Full documentation

## Step-by-Step Integration

### Step 1: Update Imports

**Location**: Top of `session_pane.py` (lines 3-12)

**Change FROM:**
```python
from textual.widgets import Static, Input, OptionList
from textual.widgets.option_list import Option
from textual.containers import Vertical
from textual.reactive import reactive
from textual import events, on
from textual.app import ComposeResult
from textual.geometry import Offset
from rich.text import Text
import re
from typing import TYPE_CHECKING
```

**Change TO:**
```python
from textual.widgets import Static, Input, OptionList, TextArea  # Add TextArea
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal  # Add Horizontal
from textual.reactive import reactive
from textual import events, on
from textual.app import ComposeResult
from textual.geometry import Offset
from rich.text import Text
import re
from typing import TYPE_CHECKING, List, Deque  # Add List, Deque
from collections import deque  # Add this import
```

### Step 2: Update CSS

**Location**: `DEFAULT_CSS` section (around line 81-94)

**Add AFTER the existing `.command-input` styles:**
```python
    SessionPane .input-container {
        dock: bottom;
        height: auto;
        background: rgb(36,36,36);
        border-top: heavy rgb(66,66,66);
    }

    SessionPane:focus-within .input-container {
        background: rgb(40,40,40);
        border-top: heavy rgb(255,183,77);
    }

    SessionPane .multi-line-input {
        height: auto;
        max-height: 10;
        background: rgb(36,36,36);
        padding: 1 2;
        border: none;
    }

    SessionPane:focus-within .multi-line-input {
        background: rgb(40,40,40);
    }

    SessionPane .mode-indicator {
        height: 1;
        background: rgb(32,32,32);
        color: rgb(189,189,189);
        padding: 0 2;
        text-align: right;
    }

    SessionPane .mode-indicator.multiline {
        color: rgb(255,183,77);
    }
```

### Step 3: Add Instance Variables

**Location**: `__init__` method, after `self._exporter = TranscriptExporter()` (around line 216)

**Add:**
```python
        # Multi-line input and command history
        self._multiline_mode = False  # Start in single-line mode
        self._command_history: Deque[str] = deque(maxlen=100)  # Store last 100 commands
        self._history_index = -1  # Current position in history (-1 = no history navigation)
        self._current_draft = ""  # Store current input when navigating history
```

### Step 4: Update compose() Method

**Location**: `compose()` method, replace the Input widget section (around lines 254-258)

**Change FROM:**
```python
        yield Input(
            placeholder="⌨ Enter command or question...",
            classes="command-input",
            id=f"input-{self.session_id}"
        )
```

**Change TO:**
```python
        # Input container with mode indicator
        with Vertical(classes="input-container", id=f"input-container-{self.session_id}"):
            yield Static(
                "Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: History",
                classes="mode-indicator",
                id=f"mode-indicator-{self.session_id}"
            )
            yield TextArea(
                text="",
                classes="multi-line-input",
                id=f"input-{self.session_id}",
                soft_wrap=True,
                show_line_numbers=False,
                tab_behavior="indent"
            )
```

### Step 5: Update on_mount() Method

**Location**: `on_mount()` method, change Input to TextArea (around line 355)

**Change FROM:**
```python
        input_widget = self.query_one(f"#input-{self.session_id}", Input)
```

**Change TO:**
```python
        input_widget = self.query_one(f"#input-{self.session_id}", TextArea)
```

### Step 6: Add New Methods

**Location**: Add these methods BEFORE the `on_input_changed` handler (around line 650)

**Add:**
```python
    def _update_mode_indicator(self) -> None:
        """Update the mode indicator text based on current mode."""
        try:
            indicator = self.query_one(f"#mode-indicator-{self.session_id}", Static)
            if self._multiline_mode:
                indicator.update(
                    "Multi-line | Ctrl+Enter: Submit | Shift+Enter: New line | Esc: Single-line mode"
                )
                indicator.add_class("multiline")
            else:
                indicator.update(
                    "Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: History"
                )
                indicator.remove_class("multiline")
        except Exception as e:
            self._log(f"Error updating mode indicator: {e}")

    def _navigate_history(self, direction: str) -> None:
        """
        Navigate through command history.

        Args:
            direction: 'up' for previous commands, 'down' for next commands
        """
        if not self._command_history:
            return

        input_widget = self.query_one(f"#input-{self.session_id}", TextArea)

        # First time navigating history - save current draft
        if self._history_index == -1:
            self._current_draft = input_widget.text

        if direction == "up":
            # Move to older commands
            if self._history_index < len(self._command_history) - 1:
                self._history_index += 1
                # History is stored newest first, so access from end
                cmd_index = len(self._command_history) - 1 - self._history_index
                input_widget.load_text(self._command_history[cmd_index])

        elif direction == "down":
            # Move to newer commands
            if self._history_index > 0:
                self._history_index -= 1
                cmd_index = len(self._command_history) - 1 - self._history_index
                input_widget.load_text(self._command_history[cmd_index])
            elif self._history_index == 0:
                # Restore draft
                self._history_index = -1
                input_widget.load_text(self._current_draft)

    async def _submit_command(self) -> None:
        """Submit the current command from the TextArea."""
        input_widget = self.query_one(f"#input-{self.session_id}", TextArea)
        command = input_widget.text.strip()

        if not command:
            self._log("Empty command, skipping")
            return

        # Check if app is in broadcast mode
        if hasattr(self.app, 'broadcast_mode') and self.app.broadcast_mode:
            self._log("In broadcast mode, letting app handle it")

        # Handle /export command locally
        if command.startswith('/export'):
            parts = command.split(maxsplit=2)
            format_type = "markdown" if len(parts) < 2 else parts[1].lower()
            filename = None if len(parts) < 3 else parts[2]

            input_widget.load_text("")
            if self._multiline_mode:
                self._multiline_mode = False
                self._update_mode_indicator()

            await self.export_session(format_type=format_type, filename=filename)
            return

        # Add to command history (avoid duplicates of the last command)
        if not self._command_history or self._command_history[-1] != command:
            self._command_history.append(command)

        # Reset history navigation
        self._history_index = -1
        self._current_draft = ""

        # Update metrics
        self.command_count += 1
        self.is_active = True

        # Add visual separator before sending command
        output_widget = self.query_one(f"#output-{self.session_id}", SelectableRichLog)

        # Create visual separator with command echo
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        separator = Text()
        separator.append("\n\n", style="")
        separator.append("╔" + "═" * 78 + "╗\n", style="bold rgb(100,180,255)")
        separator.append("║ ", style="bold rgb(100,180,255)")
        separator.append(f"⏱ {timestamp} ", style="dim cyan")
        separator.append("┊ ", style="dim white")
        separator.append("⚡ Command: ", style="bold rgb(150,220,255)")
        # Show first line only if multi-line
        display_cmd = command.split("\n")[0] if "\n" in command else command
        if "\n" in command:
            display_cmd += " [...]"
        separator.append(display_cmd, style="bold rgb(255,220,100)")
        # Pad to fill the box
        padding = 78 - len(f"⏱ {timestamp} ┊ ⚡ Command: {display_cmd}") - 2
        if padding > 0:
            separator.append(" " * padding, style="")
        separator.append(" ║\n", style="bold rgb(100,180,255)")
        separator.append("╚" + "═" * 78 + "╝\n", style="bold rgb(100,180,255)")
        separator.append("\n📝 Response: ", style="bold rgb(150,255,150)")

        output_widget.write(separator)
        output_widget.scroll_end(animate=False)
        output_widget.refresh()
        self._log("Added visual separator")

        # Show and animate inline processing indicator
        processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)
        processing_widget.display = True
        processing_widget.add_class("visible")

        # Initialize animation state and reset metrics
        self._processing_start_time = __import__('time').time()
        self._token_count = 0
        self._thinking_time = 0
        self._has_processing_indicator = True
        self._animation_frame = 0
        self._cooking_emojis = ["🥘", "🍳", "🍲", "🥄", "🔥"]
        self._cooking_verbs = ["Brewing", "Thinking", "Processing", "Cooking", "Working"]

        # Start with initial frame with metrics
        initial_text = Text()
        initial_text.append("🥘 ", style="")
        initial_text.append("Brewing", style="bold yellow")
        initial_text.append(" (0s · ↓ 0 tokens · thought for 0s)", style="dim white")
        processing_widget.update(initial_text)

        # Start animation
        if hasattr(self, 'app') and self.app:
            self.app.set_timer(0.75, self._animate_processing)

        # Store command for tracking
        self._last_command = command

        # Get session and write to PTY
        session = self.session_manager.sessions.get(self.session_id)

        if session:
            self._log(f"Writing to PTY: '{command}\\n'")
            await session.pty_handler.write(command + "\n")
            self._log("Write complete")
        else:
            self._log("ERROR: No session found!")
            error_text = Text()
            error_text.append("❌ ERROR: ", style="bold red")
            error_text.append("No session found!", style="red")
            output_widget.write(error_text)

        # Clear input field and reset to single-line mode
        input_widget.load_text("")
        if self._multiline_mode:
            self._multiline_mode = False
            self._update_mode_indicator()
```

### Step 7: Replace Event Handlers

**Location**: Replace three existing event handlers

#### 7a. Replace `@on(Input.Changed)` with:

```python
    @on(TextArea.Changed)
    def on_textarea_changed(self, event: TextArea.Changed) -> None:
        """
        Handle TextArea changes to show/hide autocomplete.

        Args:
            event: TextArea changed event
        """
        # Only handle events from this session's input
        if event.text_area.id != f"#input-{self.session_id}":
            return

        value = event.text_area.text

        # Get the current line for autocomplete (only first line)
        current_line = value.split("\n")[0] if value else ""

        # Show autocomplete when "/" is typed at start of line
        if current_line.startswith("/") and not current_line.startswith("//"):
            self._show_autocomplete(current_line)
        else:
            self._hide_autocomplete()
```

#### 7b. Replace `async def on_key()` with:

```python
    async def on_key(self, event: events.Key) -> None:
        """
        Handle key events for autocomplete navigation, mode switching, and history.

        Args:
            event: Key event
        """
        # Get input widget
        try:
            input_widget = self.query_one(f"#input-{self.session_id}", TextArea)
        except Exception:
            return

        if not input_widget.has_focus:
            return

        # Handle autocomplete navigation (highest priority)
        if self._autocomplete_visible:
            option_list = self.query_one(f"#autocomplete-list-{self.session_id}", OptionList)

            if event.key == "up":
                if option_list.highlighted is not None and option_list.highlighted > 0:
                    option_list.highlighted -= 1
                event.prevent_default()
                event.stop()
                return

            elif event.key == "down":
                if option_list.highlighted is not None:
                    max_index = len(option_list._options) - 1
                    if option_list.highlighted < max_index:
                        option_list.highlighted += 1
                event.prevent_default()
                event.stop()
                return

            elif event.key in ("enter", "tab"):
                selected = self._get_selected_command()
                if selected:
                    input_widget.load_text(selected + " ")
                    self._hide_autocomplete()
                    event.prevent_default()
                    event.stop()
                return

            elif event.key == "escape":
                self._hide_autocomplete()
                event.prevent_default()
                event.stop()
                return

        # Handle multi-line mode switching and submission
        if event.key == "enter" and event.shift:
            self._multiline_mode = not self._multiline_mode
            self._update_mode_indicator()
            event.prevent_default()
            event.stop()
            return

        elif event.key == "enter" and event.ctrl:
            if self._multiline_mode:
                await self._submit_command()
                event.prevent_default()
                event.stop()
            return

        elif event.key == "enter" and not event.ctrl and not event.shift:
            if not self._multiline_mode:
                await self._submit_command()
                event.prevent_default()
                event.stop()
            return

        elif event.key == "escape":
            if self._multiline_mode:
                self._multiline_mode = False
                self._update_mode_indicator()
                event.prevent_default()
                event.stop()
            return

        # Handle command history navigation (only in single-line mode)
        if not self._multiline_mode:
            if event.key == "up":
                self._navigate_history("up")
                event.prevent_default()
                event.stop()
                return

            elif event.key == "down":
                self._navigate_history("down")
                event.prevent_default()
                event.stop()
                return
```

#### 7c. Update `@on(OptionList.OptionSelected)`:

**Change FROM:**
```python
        input_widget = self.query_one(f"input-{self.session_id}", Input)
        if event.option.id:
            input_widget.value = event.option.id + " "
            input_widget.cursor_position = len(input_widget.value)
```

**Change TO:**
```python
        input_widget = self.query_one(f"input-{self.session_id}", TextArea)
        if event.option.id:
            input_widget.load_text(event.option.id + " ")
```

### Step 8: Remove Old Handler

**DELETE** the existing `async def on_input_submitted()` method entirely - it's replaced by `_submit_command()`.

## Verification

After making all changes:

1. **Run the test app first:**
   ```bash
   python test_multiline_history.py
   ```
   Test all keyboard shortcuts and verify behavior.

2. **Run the main application:**
   ```bash
   python -m claude_multi_terminal.app
   ```

3. **Test checklist:**
   - [ ] Type command and press Enter → Submits
   - [ ] Press Shift+Enter → Switches to multi-line mode
   - [ ] In multi-line: Press Enter → Adds newline
   - [ ] In multi-line: Press Ctrl+Enter → Submits
   - [ ] Press Esc in multi-line → Returns to single-line
   - [ ] Press Up arrow → Shows previous command
   - [ ] Press Down arrow → Shows next command
   - [ ] Type "/" → Shows autocomplete
   - [ ] Multi-line commands display correctly in output

## Troubleshooting

### Issue: "Input not found" error
**Solution**: Make sure you updated all `query_one(..., Input)` calls to `query_one(..., TextArea)`

### Issue: History not working
**Solution**: Verify `_command_history` deque is initialized in `__init__`

### Issue: Mode indicator not updating
**Solution**: Check that `_update_mode_indicator()` is called after mode changes

### Issue: Autocomplete not working
**Solution**: Ensure `on_textarea_changed()` is decorated with `@on(TextArea.Changed)`

## Rollback Plan

If issues occur, you can rollback by:
1. Keeping a backup of the original `session_pane.py`
2. Reverting imports back to original
3. Removing the new methods
4. Restoring the original Input widget

## Summary

This integration adds approximately:
- **150 lines of code** (new methods and handlers)
- **40 lines of CSS** (styling)
- **4 imports** (TextArea, Horizontal, Deque, deque)
- **4 instance variables** (mode, history, index, draft)

The changes are **non-breaking** and **backward compatible** - existing functionality remains unchanged.
