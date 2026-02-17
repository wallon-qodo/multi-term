#!/usr/bin/env python3
"""Test if Static widget displays updates."""

from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.containers import Vertical
import asyncio

class TestStaticApp(App):
    def compose(self) -> ComposeResult:
        yield Static("Initial text - if you see this, Static works", id="test-static")
        yield Input(placeholder="Type anything and press Enter")

    async def on_mount(self) -> None:
        # Update after 2 seconds
        asyncio.create_task(self.update_static())

    async def update_static(self):
        await asyncio.sleep(2)
        static = self.query_one("#test-static", Static)
        static.update("TEXT CHANGED - if you see this, updates work!")

    def on_input_submitted(self, event):
        static = self.query_one("#test-static", Static)
        static.update(f"You typed: {event.value}")
        event.input.value = ""

if __name__ == "__main__":
    print("This will test if Static widget updates are visible")
    print("1. You should see 'Initial text'")
    print("2. After 2 seconds it should change to 'TEXT CHANGED'")
    print("3. Type something and it should show what you typed")
    print("")
    input("Press Enter to start...")

    app = TestStaticApp()
    app.run()
