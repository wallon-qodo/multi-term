#!/usr/bin/env python3
"""Test if Textual works at all in this terminal."""

from textual.app import App, ComposeResult
from textual.widgets import Static

class BasicTestApp(App):
    """Minimal Textual app to test if TUI works."""

    def compose(self) -> ComposeResult:
        yield Static("Hello! If you see this, Textual is working!")
        yield Static("Press 'q' to quit")

    def on_key(self, event) -> None:
        if event.key == "q":
            self.exit()

if __name__ == "__main__":
    print("Starting basic Textual test...")
    print("You should see a message appear.")
    print("Press 'q' to quit when you see it.")
    print("")

    app = BasicTestApp()
    app.run()

    print("App exited successfully!")
