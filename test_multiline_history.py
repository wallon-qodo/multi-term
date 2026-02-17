#!/usr/bin/env python3
"""
Test script for multi-line input and command history feature.

This creates a minimal Textual app that demonstrates:
- Multi-line input with mode toggle (Shift+Enter)
- Command history navigation (Up/Down arrows)
- Submission with Enter (single-line) or Ctrl+Enter (multi-line)
- Visual mode indicator
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea, Header, Footer
from textual.containers import Vertical
from textual import events
from rich.text import Text
from collections import deque
from typing import Deque


class MultiLineHistoryTestApp(App):
    """Minimal app to test multi-line input and command history."""

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }

    #main-container {
        width: 100%;
        height: 1fr;
        border: heavy rgb(66,66,66);
        background: rgb(32,32,32);
        margin: 0;
    }

    #instructions {
        background: rgb(28,28,28);
        color: rgb(255,213,128);
        padding: 1 2;
        height: auto;
        border-bottom: solid rgb(48,48,48);
    }

    #output {
        height: 1fr;
        background: rgb(24,24,24);
        color: rgb(224,224,224);
        padding: 1 2;
        overflow-y: scroll;
    }

    #input-container {
        dock: bottom;
        height: auto;
        background: rgb(36,36,36);
        border-top: heavy rgb(255,183,77);
    }

    #mode-indicator {
        height: 1;
        background: rgb(32,32,32);
        color: rgb(189,189,189);
        padding: 0 2;
        text-align: right;
    }

    #mode-indicator.multiline {
        color: rgb(255,183,77);
    }

    #input-area {
        height: auto;
        max-height: 10;
        background: rgb(36,36,36);
        padding: 1 2;
        border: none;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear", "Clear"),
    ]

    def __init__(self):
        super().__init__()
        self._multiline_mode = False
        self._command_history: Deque[str] = deque(maxlen=100)
        self._history_index = -1
        self._current_draft = ""
        self._submitted_commands = []

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        with Vertical(id="main-container"):
            # Instructions
            instructions = Text()
            instructions.append("┌─ ", style="bold rgb(255,183,77)")
            instructions.append("Multi-Line Input & Command History Demo", style="bold white")
            instructions.append(" ─┐\n", style="bold rgb(255,183,77)")
            instructions.append("\n📝 Modes:\n", style="bold rgb(150,220,255)")
            instructions.append("  • ", style="dim white")
            instructions.append("Single-line", style="bold rgb(255,213,128)")
            instructions.append(": Press ", style="dim white")
            instructions.append("Enter", style="bold rgb(100,255,100)")
            instructions.append(" to submit, ", style="dim white")
            instructions.append("Shift+Enter", style="bold rgb(100,255,100)")
            instructions.append(" to switch to multi-line\n", style="dim white")
            instructions.append("  • ", style="dim white")
            instructions.append("Multi-line", style="bold rgb(255,213,128)")
            instructions.append(": Press ", style="dim white")
            instructions.append("Ctrl+Enter", style="bold rgb(100,255,100)")
            instructions.append(" to submit, ", style="dim white")
            instructions.append("Esc", style="bold rgb(100,255,100)")
            instructions.append(" to exit multi-line mode\n", style="dim white")
            instructions.append("\n⏱ History:\n", style="bold rgb(150,220,255)")
            instructions.append("  • Use ", style="dim white")
            instructions.append("↑↓", style="bold rgb(255,213,128)")
            instructions.append(" arrows to navigate command history (single-line mode only)\n", style="dim white")
            instructions.append("  • History stores last 100 commands\n\n", style="dim white")

            yield Static(instructions, id="instructions")

            # Output area
            yield Static("", id="output")

            # Input container with mode indicator
            with Vertical(id="input-container"):
                yield Static(
                    "Single-line | Enter: Submit | Shift+Enter: Multi-line mode | ↑↓: History",
                    id="mode-indicator"
                )
                yield TextArea(
                    text="",
                    id="input-area",
                    soft_wrap=True,
                    show_line_numbers=False,
                    tab_behavior="indent"
                )

        yield Footer()

    def on_mount(self) -> None:
        """Focus the input when app starts."""
        self.query_one("#input-area", TextArea).focus()
        self._update_output("Ready! Type a command and press Enter to submit.")

    def _update_mode_indicator(self) -> None:
        """Update the mode indicator text based on current mode."""
        indicator = self.query_one("#mode-indicator", Static)
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

    def _navigate_history(self, direction: str) -> None:
        """Navigate through command history."""
        if not self._command_history:
            return

        input_widget = self.query_one("#input-area", TextArea)

        # First time navigating history - save current draft
        if self._history_index == -1:
            self._current_draft = input_widget.text

        if direction == "up":
            # Move to older commands
            if self._history_index < len(self._command_history) - 1:
                self._history_index += 1
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
        """Handle keyboard events."""
        input_widget = self.query_one("#input-area", TextArea)

        if not input_widget.has_focus:
            return

        # Handle multi-line mode switching and submission
        if event.key == "enter" and event.shift:
            # Shift+Enter: Toggle multi-line mode
            self._multiline_mode = not self._multiline_mode
            self._update_mode_indicator()
            self._update_output(
                f"✓ Switched to {'multi-line' if self._multiline_mode else 'single-line'} mode"
            )
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
            # In multi-line mode, let TextArea handle Enter normally
            return

        elif event.key == "escape":
            # Escape: Exit multi-line mode
            if self._multiline_mode:
                self._multiline_mode = False
                self._update_mode_indicator()
                self._update_output("✓ Exited multi-line mode")
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
        """Submit the current command."""
        input_widget = self.query_one("#input-area", TextArea)
        command = input_widget.text.strip()

        if not command:
            return

        # Add to history (avoid duplicates of last command)
        if not self._command_history or self._command_history[-1] != command:
            self._command_history.append(command)

        # Reset history navigation
        self._history_index = -1
        self._current_draft = ""

        # Store submitted command
        self._submitted_commands.append(command)

        # Update output
        result = Text()
        result.append("\n", style="")
        result.append("═" * 80 + "\n", style="bold rgb(100,180,255)")
        result.append(f"Command #{len(self._submitted_commands)}", style="bold rgb(255,213,128)")
        result.append(f" (History: {len(self._command_history)} commands)\n", style="dim white")
        result.append("─" * 80 + "\n", style="dim rgb(100,180,255)")

        # Show command (with line numbers if multi-line)
        lines = command.split("\n")
        if len(lines) > 1:
            for i, line in enumerate(lines, 1):
                result.append(f"{i:3d} │ ", style="dim cyan")
                result.append(line + "\n", style="white")
        else:
            result.append(command + "\n", style="white")

        result.append("═" * 80 + "\n", style="bold rgb(100,180,255)")

        output_widget = self.query_one("#output", Static)
        current_output = output_widget.render()
        output_widget.update(str(current_output) + str(result))

        # Clear input and reset to single-line mode
        input_widget.load_text("")
        if self._multiline_mode:
            self._multiline_mode = False
            self._update_mode_indicator()

        # Scroll to bottom
        self.call_after_refresh(lambda: output_widget.scroll_end(animate=False))

    def _update_output(self, message: str) -> None:
        """Add a status message to output."""
        output_widget = self.query_one("#output", Static)
        current = str(output_widget.render())
        new_msg = Text()
        new_msg.append("\n✓ ", style="bold bright_green")
        new_msg.append(message + "\n", style="dim white")
        output_widget.update(current + str(new_msg))

    def action_clear(self) -> None:
        """Clear the output area."""
        output_widget = self.query_one("#output", Static)
        output_widget.update("")
        self._submitted_commands = []
        self._update_output("Output cleared")

    def action_quit(self) -> None:
        """Quit the app."""
        # Show summary before quitting
        summary = Text()
        summary.append("\n\n", style="")
        summary.append("═" * 80 + "\n", style="bold rgb(255,183,77)")
        summary.append("  Session Summary\n", style="bold white")
        summary.append("═" * 80 + "\n", style="bold rgb(255,183,77)")
        summary.append(f"  Commands submitted: ", style="dim white")
        summary.append(f"{len(self._submitted_commands)}\n", style="bold cyan")
        summary.append(f"  Commands in history: ", style="dim white")
        summary.append(f"{len(self._command_history)}\n", style="bold cyan")
        summary.append("═" * 80 + "\n", style="bold rgb(255,183,77)")

        output_widget = self.query_one("#output", Static)
        current = str(output_widget.render())
        output_widget.update(current + str(summary))

        # Wait a moment before exiting
        self.set_timer(1.0, self.exit)


if __name__ == "__main__":
    app = MultiLineHistoryTestApp()
    app.run()
