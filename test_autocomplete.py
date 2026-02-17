#!/usr/bin/env python3
"""
Test script to demonstrate slash command autocomplete feature.

This creates a minimal Textual app that showcases the autocomplete dropdown
without needing the full Claude Multi-Terminal application.
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Input, OptionList, Header, Footer
from textual.widgets.option_list import Option
from textual.containers import Vertical, Container
from textual import on, events
from rich.text import Text


class AutocompleteTestApp(App):
    """Minimal app to test autocomplete functionality."""

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }

    #main-container {
        width: 80;
        height: 30;
        border: heavy rgb(66,66,66);
        background: rgb(32,32,32);
        margin: 2 4;
    }

    #instructions {
        background: rgb(28,28,28);
        color: rgb(255,213,128);
        padding: 1 2;
        border-bottom: solid rgb(48,48,48);
    }

    #demo-input {
        dock: bottom;
        background: rgb(36,36,36);
        border-top: heavy rgb(255,183,77);
        padding: 0 2;
    }

    #autocomplete-container {
        display: none;
        layer: overlay;
        width: 60;
        max-height: 12;
        background: rgb(40,40,40);
        border: heavy rgb(255,183,77);
        border-bottom: none;
        offset: 4 -13;
    }

    #autocomplete-container.visible {
        display: block;
    }

    #autocomplete-header {
        background: rgb(48,48,48);
        color: rgb(255,213,128);
        padding: 0 1;
        height: 1;
        text-align: left;
    }

    #autocomplete-list {
        background: rgb(40,40,40);
        color: rgb(224,224,224);
        height: auto;
        max-height: 11;
        border: none;
        padding: 0 1;
    }

    #autocomplete-list > .option-list--option {
        background: rgb(40,40,40);
        color: rgb(189,189,189);
        padding: 0 1;
    }

    #autocomplete-list > .option-list--option-highlighted {
        background: rgb(255,183,77);
        color: rgb(24,24,24);
    }

    #autocomplete-list:focus > .option-list--option-highlighted {
        background: rgb(255,183,77);
        color: rgb(24,24,24);
    }

    #output {
        height: 1fr;
        background: rgb(24,24,24);
        color: rgb(224,224,224);
        padding: 1 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset", "Reset"),
    ]

    def __init__(self):
        super().__init__()
        self._autocomplete_visible = False
        self._slash_commands = [
            ("/model", "Switch Claude model (Sonnet/Opus/Haiku)"),
            ("/help", "Show help and available commands"),
            ("/logout", "Logout from Claude CLI"),
            ("/commit", "Create a git commit with changes"),
            ("/review-pr", "Review a GitHub pull request"),
            ("/test", "Run tests for the project"),
            ("/debug", "Debug mode and diagnostics"),
            ("/clear", "Clear the conversation history"),
            ("/save", "Save current session state"),
            ("/load", "Load a saved session"),
            ("/plan", "Enable plan mode for complex tasks"),
            ("/web", "Search the web for information"),
            ("/diff", "Show git diff of changes"),
            ("/status", "Show git status"),
            ("/branch", "Git branch operations"),
        ]

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        with Container(id="main-container"):
            # Instructions
            instructions = Text()
            instructions.append("┌─ ", style="bold rgb(255,183,77)")
            instructions.append("Autocomplete Demo", style="bold white")
            instructions.append(" ─┐\n", style="bold rgb(255,183,77)")
            instructions.append("Type ", style="dim white")
            instructions.append("/", style="bold rgb(255,213,128)")
            instructions.append(" to show autocomplete dropdown\n", style="dim white")
            instructions.append("Use ", style="dim white")
            instructions.append("↑↓", style="bold rgb(255,213,128)")
            instructions.append(" to navigate, ", style="dim white")
            instructions.append("Enter/Tab", style="bold rgb(255,213,128)")
            instructions.append(" to select, ", style="dim white")
            instructions.append("Esc", style="bold rgb(255,213,128)")
            instructions.append(" to dismiss", style="dim white")

            yield Static(instructions, id="instructions")

            # Output area
            yield Static("", id="output")

            # Autocomplete dropdown (hidden by default)
            with Vertical(id="autocomplete-container"):
                yield Static("╭─ Slash Commands ─╮", id="autocomplete-header")
                yield OptionList(id="autocomplete-list")

            # Input field
            yield Input(placeholder="Type / to see autocomplete...", id="demo-input")

        yield Footer()

    def on_mount(self) -> None:
        """Focus the input when app starts."""
        self.query_one("#demo-input", Input).focus()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        """Show/hide autocomplete based on input."""
        value = event.value

        if value.startswith("/") and not value.startswith("//"):
            self._show_autocomplete(value)
        else:
            self._hide_autocomplete()

    def _show_autocomplete(self, filter_text: str = "") -> None:
        """Show the autocomplete dropdown with filtered commands."""
        dropdown = self.query_one("#autocomplete-container")
        option_list = self.query_one("#autocomplete-list", OptionList)

        # Filter commands
        filter_text = filter_text.lower()
        filtered = [
            (cmd, desc) for cmd, desc in self._slash_commands
            if cmd.lower().startswith(filter_text)
        ]

        if not filtered:
            self._hide_autocomplete()
            return

        # Update options
        option_list.clear_options()
        for cmd, desc in filtered:
            option_text = Text()
            option_text.append(cmd, style="bold rgb(255,213,128)")
            option_text.append("  ", style="")
            option_text.append(desc, style="dim rgb(189,189,189)")
            option_list.add_option(Option(option_text, id=cmd))

        # Show dropdown
        dropdown.add_class("visible")
        self._autocomplete_visible = True

        # Highlight first option
        if len(option_list._options) > 0:
            option_list.highlighted = 0

        # Update output
        output = self.query_one("#output", Static)
        status = Text()
        status.append("✓ ", style="bold bright_green")
        status.append(f"Showing {len(filtered)} command(s) matching ", style="dim white")
        status.append(f"'{filter_text}'", style="bold rgb(255,213,128)")
        output.update(status)

    def _hide_autocomplete(self) -> None:
        """Hide the autocomplete dropdown."""
        dropdown = self.query_one("#autocomplete-container")
        dropdown.remove_class("visible")
        self._autocomplete_visible = False

    async def on_key(self, event: events.Key) -> None:
        """Handle keyboard navigation."""
        if not self._autocomplete_visible:
            return

        input_widget = self.query_one("#demo-input", Input)
        if not input_widget.has_focus:
            return

        option_list = self.query_one("#autocomplete-list", OptionList)

        if event.key == "up":
            if option_list.highlighted is not None and option_list.highlighted > 0:
                option_list.highlighted -= 1
            event.prevent_default()
            event.stop()

        elif event.key == "down":
            if option_list.highlighted is not None:
                max_index = len(option_list._options) - 1
                if option_list.highlighted < max_index:
                    option_list.highlighted += 1
            event.prevent_default()
            event.stop()

        elif event.key in ("enter", "tab"):
            selected = self._get_selected_command()
            if selected:
                input_widget.value = selected + " "
                input_widget.cursor_position = len(input_widget.value)
                self._hide_autocomplete()

                # Show selection in output
                output = self.query_one("#output", Static)
                result = Text()
                result.append("✓ ", style="bold bright_green")
                result.append("Selected: ", style="dim white")
                result.append(selected, style="bold rgb(255,213,128)")
                output.update(result)

                event.prevent_default()
                event.stop()

        elif event.key == "escape":
            self._hide_autocomplete()

            # Show dismissal in output
            output = self.query_one("#output", Static)
            result = Text()
            result.append("✓ ", style="bold rgb(255,183,77)")
            result.append("Autocomplete dismissed", style="dim white")
            output.update(result)

            event.prevent_default()
            event.stop()

    def _get_selected_command(self) -> str:
        """Get the currently selected command."""
        try:
            option_list = self.query_one("#autocomplete-list", OptionList)
            if option_list.highlighted is not None:
                option = option_list.get_option_at_index(option_list.highlighted)
                return option.id or ""
        except Exception:
            pass
        return ""

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection via mouse click."""
        input_widget = self.query_one("#demo-input", Input)
        if event.option.id:
            input_widget.value = event.option.id + " "
            input_widget.cursor_position = len(input_widget.value)
            self._hide_autocomplete()
            input_widget.focus()

            # Show selection in output
            output = self.query_one("#output", Static)
            result = Text()
            result.append("✓ ", style="bold bright_green")
            result.append("Selected via click: ", style="dim white")
            result.append(event.option.id, style="bold rgb(255,213,128)")
            output.update(result)

        event.stop()

    def action_reset(self) -> None:
        """Reset the input field."""
        input_widget = self.query_one("#demo-input", Input)
        input_widget.value = ""
        self._hide_autocomplete()

        output = self.query_one("#output", Static)
        output.update("")

    def action_quit(self) -> None:
        """Quit the app."""
        self.exit()


if __name__ == "__main__":
    app = AutocompleteTestApp()
    app.run()
