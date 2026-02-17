#!/usr/bin/env python3
"""Test widget callback with call_from_thread."""

import asyncio
import threading
import time
from textual.app import App, ComposeResult
from textual.widgets import Static, RichLog
from textual.containers import Vertical

DEBUG_LOG = open("/tmp/test_widget.log", "w")
def log(msg):
    DEBUG_LOG.write(f"{msg}\n")
    DEBUG_LOG.flush()

class TestWidget(Vertical):
    """Widget that mimics SessionPane."""

    def __init__(self, widget_id: str):
        super().__init__()
        self.widget_id = widget_id

    def compose(self) -> ComposeResult:
        yield Static(f"Widget {self.widget_id}", id=f"header-{self.widget_id}")
        yield RichLog(id=f"output-{self.widget_id}")

    async def on_mount(self) -> None:
        log(f"[DEBUG] Widget {self.widget_id} mounted")
        log(f"[DEBUG] self.app = {self.app}")
        log(f"[DEBUG] self.is_mounted = {self.is_mounted}")

        # Start a thread that will send output
        thread = threading.Thread(target=self.thread_func)
        thread.start()

    def thread_func(self):
        log(f"[DEBUG] Thread started for widget {self.widget_id}")
        time.sleep(1)

        for i in range(3):
            log(f"[DEBUG] Sending output #{i+1}")
            self.handle_output(f"Output line {i+1}\n")
            time.sleep(0.5)

    def handle_output(self, output: str):
        log(f"[DEBUG] handle_output called, is_mounted={self.is_mounted}, has app={hasattr(self, 'app')}")

        if not self.is_mounted:
            log("[DEBUG ERROR] Widget not mounted!")
            return

        if not hasattr(self, 'app') or self.app is None:
            log("[DEBUG ERROR] No app reference!")
            return

        log(f"[DEBUG] Calling app.call_from_thread...")
        try:
            self.app.call_from_thread(self.update_output, output)
            log(f"[DEBUG] call_from_thread returned")
        except Exception as e:
            log(f"[DEBUG ERROR] call_from_thread failed: {e}")

    def update_output(self, output: str):
        log(f"[DEBUG] update_output called with: {repr(output[:50])}")
        try:
            rich_log = self.query_one(f"#output-{self.widget_id}", RichLog)
            rich_log.write(output)
            log(f"[DEBUG] Wrote to RichLog successfully!")
        except Exception as e:
            import traceback
            log(f"[DEBUG ERROR] Failed to write: {e}")
            log(f"{traceback.format_exc()}")

class TestApp(App):
    def compose(self) -> ComposeResult:
        yield TestWidget("test1")

if __name__ == "__main__":
    app = TestApp()
    app.run()
