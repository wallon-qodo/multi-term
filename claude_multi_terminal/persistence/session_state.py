"""Session state data structures for persistence.

This module defines the core data structures used for persisting terminal
session state. These dataclasses are serializable to/from JSON for storage.

Classes:
    SessionState: Represents a single terminal session with all metadata
    WorkspaceState: Represents the complete workspace containing all sessions
"""

from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict
import json


@dataclass
class WorkspaceData:
    """Represents a saved workspace containing multiple sessions.

    This class captures workspace metadata for saving and loading workspaces.
    Unlike WorkspaceState (which represents the current workspace), WorkspaceData
    is used for persisting named workspace snapshots.

    Attributes:
        workspace_id: Unique identifier for the workspace
        name: Display name for the workspace
        sessions: List of session states in this workspace
        created_at: Unix timestamp of workspace creation
        modified_at: Unix timestamp of last modification
        description: Optional description of the workspace
        tags: Optional tags for categorizing workspaces

    Example:
        >>> workspace = WorkspaceData(
        ...     workspace_id="ws_123",
        ...     name="Development",
        ...     sessions=[session1, session2],
        ...     created_at=time.time(),
        ...     modified_at=time.time()
        ... )
    """
    workspace_id: str
    name: str
    sessions: List['SessionState']
    created_at: float
    modified_at: float
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert workspace data to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for JSON storage

        Example:
            >>> workspace = WorkspaceData(...)
            >>> data = workspace.to_dict()
            >>> json.dumps(data)
        """
        return {
            'workspace_id': self.workspace_id,
            'name': self.name,
            'sessions': [asdict(s) for s in self.sessions],
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'description': self.description,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceData":
        """Reconstruct workspace data from dictionary.

        Args:
            data: Dictionary representation of workspace data

        Returns:
            WorkspaceData object

        Raises:
            KeyError: If required fields are missing
            TypeError: If field types are incorrect

        Example:
            >>> data = json.load(f)
            >>> workspace = WorkspaceData.from_dict(data)
        """
        # Convert session dicts to SessionState objects
        sessions_data = data.get('sessions', [])
        sessions = [
            SessionState(**s) if isinstance(s, dict) else s
            for s in sessions_data
        ]

        return cls(
            workspace_id=data['workspace_id'],
            name=data['name'],
            sessions=sessions,
            created_at=data['created_at'],
            modified_at=data['modified_at'],
            description=data.get('description'),
            tags=data.get('tags', [])
        )


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
