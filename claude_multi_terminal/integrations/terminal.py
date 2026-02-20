"""Terminal integration for command execution and output capture."""

import logging
import subprocess
import shlex
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import threading
import queue

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command execution."""

    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timestamp: datetime
    success: bool

    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"[{status}] {self.command} (exit: {self.exit_code}, took {self.duration:.2f}s)"


class CommandHistory:
    """Manages command history with search and statistics."""

    def __init__(self, max_size: int = 1000):
        """Initialize command history.

        Args:
            max_size: Maximum number of commands to keep
        """
        self.max_size = max_size
        self._history: List[CommandResult] = []

    def add(self, result: CommandResult) -> None:
        """Add a command result to history.

        Args:
            result: Command result to add
        """
        self._history.append(result)
        if len(self._history) > self.max_size:
            self._history = self._history[-self.max_size :]

    def get_all(self) -> List[CommandResult]:
        """Get all command history."""
        return self._history.copy()

    def get_recent(self, count: int = 10) -> List[CommandResult]:
        """Get most recent commands.

        Args:
            count: Number of commands to return

        Returns:
            List of recent CommandResult objects
        """
        return self._history[-count:]

    def search(self, query: str) -> List[CommandResult]:
        """Search command history.

        Args:
            query: Search query

        Returns:
            List of matching CommandResult objects
        """
        query_lower = query.lower()
        return [r for r in self._history if query_lower in r.command.lower()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get command history statistics.

        Returns:
            Dictionary with statistics
        """
        if not self._history:
            return {
                "total_commands": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "most_common": [],
            }

        total = len(self._history)
        successes = sum(1 for r in self._history if r.success)
        total_duration = sum(r.duration for r in self._history)

        # Count command frequencies
        command_counts: Dict[str, int] = {}
        for result in self._history:
            cmd = result.command.split()[0] if result.command else "unknown"
            command_counts[cmd] = command_counts.get(cmd, 0) + 1

        most_common = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_commands": total,
            "success_rate": (successes / total) * 100 if total > 0 else 0.0,
            "average_duration": total_duration / total if total > 0 else 0.0,
            "most_common": [{"command": cmd, "count": count} for cmd, count in most_common],
        }

    def clear(self) -> None:
        """Clear command history."""
        self._history.clear()


class TerminalIntegration:
    """Terminal integration for executing commands and capturing output."""

    def __init__(self, working_dir: Optional[Path] = None, shell: str = "/bin/bash"):
        """Initialize terminal integration.

        Args:
            working_dir: Working directory for commands
            shell: Shell to use for command execution
        """
        self.working_dir = working_dir or Path.cwd()
        self.shell = shell
        self.history = CommandHistory()
        self._output_listeners: List[Callable[[str], None]] = []
        self._env_vars: Dict[str, str] = {}

        logger.info(f"TerminalIntegration initialized (cwd: {self.working_dir})")

    def execute(
        self,
        command: str,
        timeout: Optional[float] = None,
        capture_output: bool = True,
        check: bool = False,
    ) -> CommandResult:
        """Execute a command and return the result.

        Args:
            command: Command to execute
            timeout: Timeout in seconds
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit

        Returns:
            CommandResult object
        """
        start_time = datetime.now()

        try:
            # Prepare environment
            env = self._env_vars.copy()

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                executable=self.shell,
                cwd=self.working_dir,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                env=env if env else None,
                check=check,
            )

            duration = (datetime.now() - start_time).total_seconds()
            success = result.returncode == 0

            cmd_result = CommandResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                duration=duration,
                timestamp=start_time,
                success=success,
            )

            # Add to history
            self.history.add(cmd_result)

            # Notify listeners
            if capture_output and result.stdout:
                for listener in self._output_listeners:
                    try:
                        listener(result.stdout)
                    except Exception as e:
                        logger.error(f"Output listener error: {e}")

            logger.info(f"Executed: {command} (exit: {result.returncode})")
            return cmd_result

        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            cmd_result = CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr="Command timed out",
                duration=duration,
                timestamp=start_time,
                success=False,
            )
            self.history.add(cmd_result)
            logger.error(f"Command timed out: {command}")
            return cmd_result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            cmd_result = CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=duration,
                timestamp=start_time,
                success=False,
            )
            self.history.add(cmd_result)
            logger.error(f"Command execution failed: {e}")
            return cmd_result

    def execute_async(
        self,
        command: str,
        callback: Optional[Callable[[CommandResult], None]] = None,
        timeout: Optional[float] = None,
    ) -> threading.Thread:
        """Execute a command asynchronously.

        Args:
            command: Command to execute
            callback: Callback function to call with result
            timeout: Timeout in seconds

        Returns:
            Thread object
        """

        def _run():
            result = self.execute(command, timeout=timeout)
            if callback:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"Async callback error: {e}")

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread

    def execute_with_input(
        self, command: str, input_data: str, timeout: Optional[float] = None
    ) -> CommandResult:
        """Execute a command with stdin input.

        Args:
            command: Command to execute
            input_data: Data to send to stdin
            timeout: Timeout in seconds

        Returns:
            CommandResult object
        """
        start_time = datetime.now()

        try:
            result = subprocess.run(
                command,
                shell=True,
                executable=self.shell,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                input=input_data,
                timeout=timeout,
            )

            duration = (datetime.now() - start_time).total_seconds()

            cmd_result = CommandResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration,
                timestamp=start_time,
                success=result.returncode == 0,
            )

            self.history.add(cmd_result)
            return cmd_result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            cmd_result = CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=duration,
                timestamp=start_time,
                success=False,
            )
            self.history.add(cmd_result)
            return cmd_result

    def execute_pipeline(self, commands: List[str], timeout: Optional[float] = None) -> CommandResult:
        """Execute a pipeline of commands.

        Args:
            commands: List of commands to pipe together
            timeout: Timeout in seconds

        Returns:
            CommandResult object
        """
        pipeline = " | ".join(commands)
        return self.execute(pipeline, timeout=timeout)

    def add_output_listener(self, callback: Callable[[str], None]) -> None:
        """Add a listener for command output.

        Args:
            callback: Function to call with output
        """
        if callback not in self._output_listeners:
            self._output_listeners.append(callback)

    def remove_output_listener(self, callback: Callable[[str], None]) -> None:
        """Remove an output listener.

        Args:
            callback: Callback to remove
        """
        if callback in self._output_listeners:
            self._output_listeners.remove(callback)

    def set_env_var(self, name: str, value: str) -> None:
        """Set an environment variable for command execution.

        Args:
            name: Variable name
            value: Variable value
        """
        self._env_vars[name] = value

    def get_env_var(self, name: str) -> Optional[str]:
        """Get an environment variable.

        Args:
            name: Variable name

        Returns:
            Variable value or None
        """
        return self._env_vars.get(name)

    def clear_env_vars(self) -> None:
        """Clear all custom environment variables."""
        self._env_vars.clear()

    def get_completion_suggestions(self, partial_command: str) -> List[str]:
        """Get shell completion suggestions for partial command.

        Args:
            partial_command: Partial command string

        Returns:
            List of completion suggestions
        """
        # Simple completion based on command history
        suggestions = set()

        # Add from history
        for result in self.history.get_all():
            if result.command.startswith(partial_command):
                suggestions.add(result.command)

        # Add common commands if partial is short
        if len(partial_command) <= 2:
            common_commands = [
                "ls", "cd", "pwd", "cat", "grep", "find", "git", "python",
                "pip", "npm", "node", "docker", "make", "cmake", "cargo"
            ]
            suggestions.update(cmd for cmd in common_commands if cmd.startswith(partial_command))

        return sorted(suggestions)[:10]

    def validate_command(self, command: str) -> tuple[bool, str]:
        """Validate a command before execution.

        Args:
            command: Command to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not command.strip():
            return False, "Empty command"

        # Check for dangerous commands
        dangerous = ["rm -rf /", ":(){ :|:& };:", "mkfs", "dd if=/dev/zero"]
        for danger in dangerous:
            if danger in command:
                return False, f"Dangerous command detected: {danger}"

        # Check for valid syntax (basic)
        try:
            shlex.split(command)
            return True, ""
        except ValueError as e:
            return False, f"Invalid command syntax: {e}"

    def get_command_help(self, command: str) -> str:
        """Get help/man page for a command.

        Args:
            command: Command name

        Returns:
            Help text
        """
        result = self.execute(f"man {command} 2>/dev/null || {command} --help 2>&1", timeout=5)
        if result.success:
            return result.stdout
        return f"No help available for: {command}"

    def change_directory(self, path: Path) -> bool:
        """Change working directory.

        Args:
            path: New working directory

        Returns:
            True if successful
        """
        if path.exists() and path.is_dir():
            self.working_dir = path
            logger.info(f"Changed directory to: {path}")
            return True
        logger.error(f"Directory does not exist: {path}")
        return False

    def get_working_directory(self) -> Path:
        """Get current working directory."""
        return self.working_dir

    def get_history_statistics(self) -> Dict[str, Any]:
        """Get command history statistics."""
        return self.history.get_statistics()
