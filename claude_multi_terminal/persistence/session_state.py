"""Session state data structures for persistence.

This module defines the core data structures used for persisting terminal
session state. These dataclasses are serializable to/from JSON for storage.

Classes:
    SessionState: Represents a single terminal session with all metadata
    WorkspaceState: Represents the complete workspace containing all sessions
"""

from dataclasses import dataclass, asdict, field
from typing import List, Optional
import json


@dataclass
class SessionState:
    """Represents the persistent state of a single terminal session.

    This class captures all metadata needed to save and restore a terminal
    session, including working directory, command history, and output snapshots.

    Attributes:
        session_id: Unique identifier for the session
        name: Display name for the session
        working_directory: Current working directory path
        created_at: Unix timestamp of session creation
        modified_at: Unix timestamp of last modification
        command_count: Number of commands executed in this session
        last_command: Most recent command executed (for preview)
        conversation_file: Path to Claude's conversation file (.jsonl)
        output_snapshot: Recent output lines for preview (last N lines)
        is_active: Whether this session is currently active

    Example:
        >>> session = SessionState(
        ...     session_id="abc123",
        ...     name="Main",
        ...     working_directory="/home/user/project",
        ...     created_at=time.time()
        ... )
        >>> session.command_count += 1
        >>> session.last_command = "ls -la"
    """
    session_id: str
    name: str
    working_directory: str
    created_at: float
    modified_at: float
    command_count: int = 0
    last_command: Optional[str] = None
    conversation_file: Optional[str] = None
    output_snapshot: List[str] = field(default_factory=list)
    is_active: bool = False

    def __post_init__(self) -> None:
        """Initialize computed fields after dataclass initialization.

        Ensures output_snapshot is always a list (never None) for safe operations.
        """
        if not isinstance(self.output_snapshot, list):
            self.output_snapshot = list(self.output_snapshot) if self.output_snapshot else []


@dataclass
class WorkspaceState:
    """Represents the complete workspace state containing all sessions.

    This is the top-level state object that gets serialized to disk. It contains
    all active and inactive sessions, along with metadata about which session
    is currently active.

    Attributes:
        sessions: List of all session states in the workspace
        active_session_id: ID of the currently active session (if any)
        version: Schema version for forward/backward compatibility

    Example:
        >>> workspace = WorkspaceState()
        >>> session = SessionState(...)
        >>> workspace.sessions.append(session)
        >>> workspace.active_session_id = session.session_id
        >>> json_str = workspace.to_json()
    """
    sessions: List[SessionState] = field(default_factory=list)
    active_session_id: Optional[str] = None
    version: str = "1.0"

    def to_json(self) -> str:
        """Serialize workspace state to JSON string.

        Converts the entire workspace state, including all nested sessions,
        into a formatted JSON string suitable for file storage.

        Returns:
            Formatted JSON string with 2-space indentation

        Example:
            >>> workspace = WorkspaceState(sessions=[session1, session2])
            >>> json_str = workspace.to_json()
            >>> with open('state.json', 'w') as f:
            ...     f.write(json_str)
        """
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "WorkspaceState":
        """Deserialize workspace state from JSON string.

        Parses a JSON string and reconstructs the WorkspaceState object,
        converting nested session dictionaries back into SessionState objects.

        Args:
            json_str: JSON string representation of workspace state

        Returns:
            Reconstructed WorkspaceState object

        Raises:
            json.JSONDecodeError: If the JSON string is malformed
            TypeError: If required fields are missing or have wrong types

        Example:
            >>> with open('state.json', 'r') as f:
            ...     json_str = f.read()
            >>> workspace = WorkspaceState.from_json(json_str)
            >>> print(len(workspace.sessions))
        """
        data = json.loads(json_str)

        # Convert session dicts to SessionState objects
        if 'sessions' in data and data['sessions']:
            data['sessions'] = [
                SessionState(**s) if isinstance(s, dict) else s
                for s in data['sessions']
            ]

        return cls(**data)
