"""Subprocess handler with async I/O support for Claude CLI."""

import asyncio
import subprocess
from typing import Callable, Optional
import os
import signal


class PTYHandler:
    """
    Wrapper for subprocess management with async output reading.

    CRITICAL: Uses subprocess.Popen with stdin=PIPE instead of PTY.
    Claude CLI in pipe mode requires stdin to be CLOSED (EOF) before processing,
    so we use a one-shot model: spawn process, send command, close stdin, read output.

    CONVERSATION HISTORY:
    - Each session has a unique working directory: ~/.claude_multi_terminal/sessions/<uuid>/
    - Claude CLI is invoked with --continue flag to continue the most recent conversation in that directory
    - Claude CLI automatically stores conversation history in ~/.claude/projects/[directory-path]/[auto-id].jsonl
    - Each one-shot subprocess invocation continues the same conversation by reading from the session file
    - This maintains conversation context across commands without keeping a persistent process
    - Using --continue avoids session locking issues that occur with --session-id
    """

    def __init__(
        self,
        command: list,
        cwd: str,
        env: dict,
        rows: int = 24,
        cols: int = 80
    ):
        """
        Initialize subprocess handler.

        Args:
            command: Command to execute (e.g., ['/opt/homebrew/bin/claude'])
            cwd: Working directory for the process
            env: Environment variables dict
            rows: Terminal rows (kept for compatibility, not used)
            cols: Terminal columns (kept for compatibility, not used)
        """
        self.command = command
        self.cwd = cwd
        self.env = env
        self.rows = rows
        self.cols = cols
        self.process: Optional[subprocess.Popen] = None
        self.output_callback: Optional[Callable[[str], None]] = None
        self._read_task: Optional[asyncio.Task] = None
        self._running = False
        self._command_queue: asyncio.Queue = asyncio.Queue()
        self._processing = False

    def spawn(self) -> None:
        """
        Initialize the handler (kept for compatibility).

        Note: We don't spawn a long-lived process anymore.
        Each command spawns its own process via execute_command().
        """
        self._running = True

    async def start_reading(self, callback: Callable[[str], None]) -> None:
        """
        Register output callback and start command processor.

        Args:
            callback: Function to call with output chunks
        """
        self.output_callback = callback
        # Start the command processor task
        if not self._processing:
            self._processing = True
            self._read_task = asyncio.create_task(self._command_processor())

    async def _command_processor(self) -> None:
        """
        Process commands from the queue.

        Each command spawns a new Claude process, sends the command,
        closes stdin, reads the output, and terminates.
        """
        while self._running:
            try:
                # Wait for a command
                command = await asyncio.wait_for(
                    self._command_queue.get(),
                    timeout=1.0
                )

                # Execute the command in one-shot mode
                await self._execute_one_shot(command)

            except asyncio.TimeoutError:
                # No command, continue waiting
                continue
            except Exception as e:
                print(f"Command processor error: {e}")
                await asyncio.sleep(0.1)

    async def _execute_one_shot(self, command: str) -> None:
        """
        Execute a single command in one-shot mode with optimized streaming.

        Args:
            command: The command string to send to Claude
        """
        try:
            # Spawn process
            proc = await asyncio.to_thread(
                subprocess.Popen,
                self.command,
                cwd=self.cwd,
                env=self.env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,
                bufsize=0  # Unbuffered for lower latency
            )

            # Store process reference for cancellation
            self.process = proc

            # Send command and close stdin
            await asyncio.to_thread(
                self._send_and_close,
                proc,
                command
            )

            # Read output with small chunks for low latency streaming
            # Use non-blocking I/O with select() to poll for data availability
            last_output_time = asyncio.get_event_loop().time()

            # Make stdout non-blocking so we can poll it efficiently
            import select
            import fcntl

            # Set stdout to non-blocking mode
            fd = proc.stdout.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            while True:
                # Check if process was cancelled
                if not self._running:
                    break

                # Use select to wait for data with timeout
                try:
                    # Wait for data to be available (max 50ms)
                    ready, _, _ = await asyncio.to_thread(
                        select.select, [proc.stdout], [], [], 0.05
                    )

                    if ready:
                        # Data is available, read it (non-blocking)
                        try:
                            chunk = proc.stdout.read(256)

                            if not chunk:
                                # EOF reached
                                break

                            # Send chunks to callback as they arrive
                            if self.output_callback:
                                decoded = chunk.decode('utf-8', errors='replace')
                                self.output_callback(decoded)
                                last_output_time = asyncio.get_event_loop().time()

                            # Yield to event loop for responsive UI
                            await asyncio.sleep(0)

                        except BlockingIOError:
                            # No data available (shouldn't happen after select, but be safe)
                            await asyncio.sleep(0.01)
                            continue
                    else:
                        # Timeout - no data available
                        # Check if process finished
                        if proc.poll() is not None:
                            # Process finished, do one final read for any remaining data
                            try:
                                while True:
                                    chunk = proc.stdout.read(256)
                                    if not chunk:
                                        break
                                    if self.output_callback:
                                        decoded = chunk.decode('utf-8', errors='replace')
                                        self.output_callback(decoded)
                            except Exception:
                                pass
                            break
                        # Process still running, continue waiting
                        continue

                except Exception:
                    break

            # Wait for process to finish (no timeout - wait indefinitely)
            await asyncio.to_thread(proc.wait)

            # Small delay to ensure clean process termination
            await asyncio.sleep(0.05)

            # Send completion signal
            if self.output_callback:
                self.output_callback("\x00COMMAND_COMPLETE\x00")

        except asyncio.CancelledError:
            # Handle cancellation gracefully
            if self.process and self.process.poll() is None:
                try:
                    self.process.terminate()
                    await asyncio.sleep(0.1)
                    if self.process.poll() is None:
                        self.process.kill()
                except Exception:
                    pass
            if self.output_callback:
                self.output_callback("\n\n⚠️ Command cancelled by user\n")
                self.output_callback("\x00COMMAND_COMPLETE\x00")
            raise
        except Exception as e:
            # Send error to callback
            if self.output_callback:
                error_msg = f"\n❌ Error executing command: {e}\n"
                self.output_callback(error_msg)
                self.output_callback("\x00COMMAND_COMPLETE\x00")

    def _send_and_close(self, proc: subprocess.Popen, command: str) -> None:
        """Send command to process and close stdin (blocking)."""
        try:
            proc.stdin.write(command.encode('utf-8'))
            proc.stdin.flush()
            proc.stdin.close()
        except Exception as e:
            print(f"Error sending command: {e}")

    async def write(self, data: str) -> None:
        """
        Queue a command for execution.

        Args:
            data: Command string (including newline if needed)
        """
        # Strip trailing newline since we send complete commands
        command = data.rstrip('\n')
        await self._command_queue.put(command)

    async def resize(self, rows: int, cols: int) -> None:
        """
        Update dimensions (no-op for subprocess, kept for compatibility).

        Args:
            rows: New row count
            cols: New column count
        """
        self.rows = rows
        self.cols = cols
        # No-op: subprocess doesn't have window size like PTY

    async def cancel_current_command(self) -> None:
        """
        Cancel the currently executing command.

        This terminates the active Claude CLI process and cleans up resources.
        """
        if self.process and self.process.poll() is None:
            try:
                # Send SIGTERM first for graceful shutdown
                self.process.terminate()

                # Wait briefly for graceful termination
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(self.process.wait),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    # Force kill if it doesn't terminate gracefully
                    self.process.kill()
                    await asyncio.to_thread(self.process.wait)

            except Exception as e:
                print(f"Error cancelling command: {e}")

    async def terminate(self) -> None:
        """Gracefully terminate the handler."""
        self._running = False
        self._processing = False

        # Cancel current command if running
        await self.cancel_current_command()

        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        # Note: Individual command processes self-terminate after completion
        # No long-lived process to clean up
