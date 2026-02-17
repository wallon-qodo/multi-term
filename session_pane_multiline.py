"""
Multi-line input and command history implementation for SessionPane.

This file contains the replacement methods for session_pane.py to add:
- Multi-line input mode (TextArea instead of Input)
- Command history navigation (last 100 commands)
- Mode indicator showing current state
- Keyboard shortcuts (Shift+Enter, Ctrl+Enter, Up/Down arrows)
"""

# ============================================================================
# REPLACEMENT FOR compose() METHOD
# ============================================================================

def compose_replacement(self) -> ComposeResult:
    """Build the pane UI components with multi-line input support."""
    yield Static(
        self._render_header(),
        classes="session-header",
        id=f"header-{self.session_id}"
    )
    # Use SelectableRichLog for terminal output with ANSI support
    yield SelectableRichLog(
        classes="terminal-output",
        id=f"output-{self.session_id}",
        highlight=True,
        markup=True,
        auto_scroll=True,
        max_lines=10000,
        wrap=True
    )
    # Inline processing indicator (hidden by default)
    yield Static(
        "",
        classes="processing-inline",
        id=f"processing-inline-{self.session_id}"
    )
    # Slash command autocomplete dropdown (positioned above input)
    with Vertical(classes="autocomplete-dropdown", id=f"autocomplete-{self.session_id}"):
        yield Static(
            "╭─ Slash Commands ─╮",
            classes="autocomplete-header",
            id=f"autocomplete-header-{self.session_id}"
        )
        yield OptionList(id=f"autocomplete-list-{self.session_id}")

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


# ============================================================================
# REPLACEMENT EVENT HANDLERS
# ============================================================================

@on(TextArea.Changed)
def on_textarea_changed(self, event: TextArea.Changed) -> None:
    """
    Handle TextArea changes to show/hide autocomplete.

    Args:
        event: TextArea changed event
    """
    # Only handle events from this session's input
    if event.text_area.id != f"input-{self.session_id}":
        return

    value = event.text_area.text

    # Get the current line for autocomplete (only first line in single-line mode)
    current_line = value.split("\n")[0] if value else ""

    # Show autocomplete when "/" is typed at start of line
    if current_line.startswith("/") and not current_line.startswith("//"):
        self._show_autocomplete(current_line)
    else:
        self._hide_autocomplete()


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
            # Navigate up in autocomplete list
            if option_list.highlighted is not None and option_list.highlighted > 0:
                option_list.highlighted -= 1
            event.prevent_default()
            event.stop()
            return

        elif event.key == "down":
            # Navigate down in autocomplete list
            if option_list.highlighted is not None:
                max_index = len(option_list._options) - 1
                if option_list.highlighted < max_index:
                    option_list.highlighted += 1
            event.prevent_default()
            event.stop()
            return

        elif event.key in ("enter", "tab"):
            # Select the highlighted command
            selected = self._get_selected_command()
            if selected:
                # Fill input with selected command and add a space
                input_widget.load_text(selected + " ")
                self._hide_autocomplete()
                event.prevent_default()
                event.stop()
            return

        elif event.key == "escape":
            # Hide autocomplete on Escape
            self._hide_autocomplete()
            event.prevent_default()
            event.stop()
            return

    # Handle multi-line mode switching and submission
    if event.key == "enter" and event.shift:
        # Shift+Enter: Toggle multi-line mode
        self._multiline_mode = not self._multiline_mode
        self._update_mode_indicator()
        event.prevent_default()
        event.stop()
        return

    elif event.key == "enter" and event.ctrl:
        # Ctrl+Enter: Submit in multi-line mode
        if self._multiline_mode:
            await self._submit_command()
            event.prevent_default()
            event.stop()
        return

    elif event.key == "enter" and not event.ctrl and not event.shift:
        # Plain Enter: Submit in single-line mode, newline in multi-line mode
        if not self._multiline_mode:
            await self._submit_command()
            event.prevent_default()
            event.stop()
        # In multi-line mode, let TextArea handle Enter normally (adds newline)
        return

    elif event.key == "escape":
        # Escape: Exit multi-line mode
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
        # Still process locally for history

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

    # Create enterprise-grade visual separator with command echo
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


# Update the on_option_selected handler to work with TextArea
@on(OptionList.OptionSelected)
def on_option_selected(self, event: OptionList.OptionSelected) -> None:
    """
    Handle option selection from autocomplete dropdown.

    Args:
        event: Option selected event
    """
    # Only handle events from this session's autocomplete
    if event.option_list.id != f"autocomplete-list-{self.session_id}":
        return

    # Fill input with selected command
    input_widget = self.query_one(f"input-{self.session_id}", TextArea)
    if event.option.id:
        input_widget.load_text(event.option.id + " ")
        self._hide_autocomplete()
        input_widget.focus()

    event.stop()
