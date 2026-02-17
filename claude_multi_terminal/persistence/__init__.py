"""Session state persistence and storage.

This module provides data structures and storage mechanisms for persisting
multi-terminal session state across application restarts.

Key components:
    - SessionState: Individual terminal session data
    - WorkspaceState: Complete workspace with all sessions
    - SessionStorage: File-based persistence layer
"""

from .session_state import SessionState, WorkspaceState
from .storage import SessionStorage

__all__ = ['SessionState', 'WorkspaceState', 'SessionStorage']
