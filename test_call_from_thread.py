#!/usr/bin/env python3
"""Test if call_from_thread works at all."""

import asyncio
import threading
import time
from textual.app import App, ComposeResult
from textual.widgets import Static

DEBUG_LOG = open("/tmp/test_cft.log", "w")
def log(msg):
    DEBUG_LOG.write(f"{msg}\n")
    DEBUG_LOG.flush()

class TestCFT(App):
    def compose(self) -> ComposeResult:
        yield Static("Testing call_from_thread...", id="status")

    def on_mount(self) -> None:
        log("[DEBUG] on_mount called")
        # Start a thread that will try to update UI
        thread = threading.Thread(target=self.thread_func)
        thread.start()
        log("[DEBUG] Thread started")

    def thread_func(self):
        log("[DEBUG] thread_func started")
        time.sleep(1)
        log("[DEBUG] About to call_from_thread")
        try:
            self.call_from_thread(self.update_ui, "Hello from thread!")
            log("[DEBUG] call_from_thread returned")
        except Exception as e:
            log(f"[DEBUG ERROR] call_from_thread failed: {e}")

    def update_ui(self, msg: str):
        log(f"[DEBUG] update_ui called with: {msg}")
        try:
            widget = self.query_one("#status", Static)
            widget.update(msg)
            log("[DEBUG] Widget updated successfully")
        except Exception as e:
            log(f"[DEBUG ERROR] Widget update failed: {e}")

if __name__ == "__main__":
    app = TestCFT()
    app.run()
