"""Session lifecycle management for multiple Claude CLI instances."""

import os
import time
import uuid
from typing import Dict, Optional
from dataclasses import dataclass

from .pty_handler import PTYHandler
from ..utils.naming import generate_unique_directory_name


@dataclass
class SessionInfo:
    """Metadata for a Claude CLI session."""
    session_id: str
    name: str
    pty_handler: PTYHandler
    created_at: float
    working_directory: str


class SessionManager:
    """Manages lifecycle of multiple Claude CLI PTY processes."""

    def __init__(self, claude_path: str = "/opt/homebrew/bin/claude"):
        """
        Initialize session manager.

        Args:
            claude_path: Path to Claude CLI executable
        """
        self.claude_path = claude_path
        self.sessions: Dict[str, SessionInfo] = {}
        self._session_counter = 0

    def create_session(
        self,
        name: Optional[str] = None,
        working_dir: Optional[str] = None,
        claude_args: Optional[list] = None
    ) -> str:
        """
        Create a new Claude CLI session with PTY.

        Args:
            name: Human-readable session name
            working_dir: Working directory for the session
            claude_args: Additional arguments for Claude CLI

        Returns:
            session_id: UUID string for the new session
        """
        session_id = str(uuid.uuid4())
        self._session_counter += 1

        if name is None:
            name = f"Session {self._session_counter}"

        if working_dir is None:
            # Create a unique working directory for this session
            # This ensures each session has isolated conversation history with --continue flag
            # Each session gets its own directory under ~/Desktop/multi-claude-sessions/sessions/
            # Using descriptive names based on session name instead of UUID
            sessions_root = os.path.join(os.path.expanduser("~"), "Desktop", "multi-claude-sessions", "sessions")
            os.makedirs(sessions_root, exist_ok=True)

            # Generate a filesystem-safe, descriptive directory name from the session name
            # Examples: "research-and-development", "my-project", "data-analysis"
            # This makes it easy to find and organize work by topic
            dir_name = generate_unique_directory_name(
                base_name=name if name else f"Session {self._session_counter}",
                parent_dir=sessions_root,
                session_id=session_id
            )
            working_dir = os.path.join(sessions_root, dir_name)
            os.makedirs(working_dir, exist_ok=True)

        # Default args: interactive mode with permissions bypass
        if claude_args is None:
            claude_args = []

        # CRITICAL: Add --dangerously-skip-permissions to bypass security prompt
        # Without this flag, Claude shows a "trust this folder" prompt and doesn't accept commands
        if '--dangerously-skip-permissions' not in claude_args:
            claude_args.insert(0, '--dangerously-skip-permissions')

        # CRITICAL: Add --continue to maintain conversation history
        # This tells Claude to continue the most recent conversation in the working directory
        # Each command will extend the same conversation automatically
        # We use unique working directories per session to isolate conversation histories
        # This avoids session locking issues that occur with --session-id
        if '--continue' not in claude_args and '-c' not in claude_args:
            claude_args.append('--continue')

        # Create session-specific environment with isolated config
        session_env = self._get_session_env(session_id)

        # Create PTY handler
        pty_handler = PTYHandler(
            command=[self.claude_path] + claude_args,
            cwd=working_dir,
            env=session_env
        )

        session_info = SessionInfo(
            session_id=session_id,
            name=name,
            pty_handler=pty_handler,
            created_at=time.time(),
            working_directory=working_dir
        )

        self.sessions[session_id] = session_info

        # Start the PTY process
        pty_handler.spawn()

        return session_id

    async def terminate_session(self, session_id: str) -> None:
        """
        Gracefully terminate a session.

        Args:
            session_id: UUID of session to terminate
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            await session.pty_handler.terminate()
            del self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information by ID.

        Args:
            session_id: UUID of session to retrieve

        Returns:
            SessionInfo if session exists, None otherwise
        """
        return self.sessions.get(session_id)

    def list_sessions(self) -> list:
        """
        List all active sessions.

        Returns:
            List of SessionInfo objects for all active sessions
        """
        return list(self.sessions.values())

    def _get_session_env(self, session_id: str) -> dict:
        """
        Prepare environment variables for Claude CLI with isolated config.

        Args:
            session_id: Unique session identifier

        Returns:
            Environment dict with proper settings for pipe mode
        """
        # CRITICAL: Copy the ENTIRE environment including PATH
        # Claude CLI needs node, which requires PATH to be set
        env = os.environ.copy()

        # IMPORTANT: Do NOT set TERM or COLORTERM when using pipes
        # Claude CLI detects non-TTY stdin and automatically switches to pipe mode
        # Setting terminal variables would confuse it
        # Remove them if they exist to ensure clean pipe mode
        env.pop('TERM', None)
        env.pop('COLORTERM', None)

        # Ensure PATH is set (critical for finding node)
        if 'PATH' not in env:
            env['PATH'] = '/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin'

        return env
