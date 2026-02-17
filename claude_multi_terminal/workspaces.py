"""Workspace system data model for managing multiple independent workspaces.

This module provides a complete workspace management system that allows users to organize
their Claude CLI sessions across 9 independent workspaces (1-9). Each workspace maintains
its own set of sessions, layout mode, and focus state.

Architecture:
    - Workspace: Dataclass representing a single workspace with its sessions and state
    - LayoutMode: Enum defining the layout strategies (TILED, FLOATING, MONOCLE)
    - WorkspaceManager: Core manager class handling workspace lifecycle and operations

Design Philosophy:
    - Workspaces are numbered 1-9 for quick keyboard switching
    - Each workspace is independent with its own session collection
    - User-renameable workspaces for better organization
    - Automatic timestamp tracking for audit and sorting
    - Type-safe design with comprehensive validation

Usage Example:
    >>> manager = WorkspaceManager()
    >>> ws_id = manager.create_workspace(1, "Development")
    >>> manager.add_session_to_workspace(1, "session-uuid-123")
    >>> manager.switch_to_workspace(1)
    >>> manager.get_workspace(1)
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class LayoutMode(Enum):
    """Layout modes for organizing sessions within a workspace.

    Attributes:
        TILED: Automatic grid layout with equal-sized panes
        FLOATING: Free-form draggable windows with arbitrary positioning
        MONOCLE: Single maximized session (fullscreen mode)
    """

    TILED = "tiled"
    FLOATING = "floating"
    MONOCLE = "monocle"


@dataclass
class Workspace:
    """Data model for a single workspace.

    A workspace is a container for organizing related Claude CLI sessions with
    a specific layout mode. Workspaces can be renamed, switched between, and
    maintain their own focus state.

    Attributes:
        id: Workspace identifier (1-9)
        name: User-visible name (default: "Workspace {id}")
        session_ids: List of session UUIDs belonging to this workspace
        focused_session_id: Currently focused session UUID (None if no focus)
        layout_mode: Current layout strategy for this workspace
        created_at: Unix timestamp of workspace creation
        modified_at: Unix timestamp of last modification

    Design Notes:
        - id is immutable after creation (no setter)
        - session_ids maintains insertion order for predictable layouts
        - focused_session_id can be None if workspace is empty
        - timestamps are float (Unix epoch) for consistent cross-platform support
    """

    id: int
    name: str
    session_ids: List[str] = field(default_factory=list)
    focused_session_id: Optional[str] = None
    layout_mode: LayoutMode = LayoutMode.TILED
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Validate workspace constraints after initialization.

        Raises:
            ValueError: If id is not in valid range (1-9)
        """
        if not 1 <= self.id <= 9:
            raise ValueError(f"Workspace id must be between 1 and 9, got {self.id}")

    def update_modified_time(self) -> None:
        """Update the modified_at timestamp to current time.

        Call this method whenever workspace state changes (sessions added/removed,
        layout changed, focus changed, etc.).
        """
        self.modified_at = time.time()

    def add_session(self, session_id: str) -> None:
        """Add a session to this workspace.

        Args:
            session_id: UUID of the session to add

        Note:
            Automatically updates modified_at timestamp.
            Does not add duplicate session_ids.
        """
        if session_id not in self.session_ids:
            self.session_ids.append(session_id)
            self.update_modified_time()

    def remove_session(self, session_id: str) -> bool:
        """Remove a session from this workspace.

        Args:
            session_id: UUID of the session to remove

        Returns:
            True if session was removed, False if not found

        Note:
            Automatically clears focused_session_id if removing focused session.
            Updates modified_at timestamp on successful removal.
        """
        if session_id in self.session_ids:
            # Remember the index before removing
            session_index = self.session_ids.index(session_id)
            self.session_ids.remove(session_id)

            # Clear focus if we removed the focused session
            if self.focused_session_id == session_id:
                # Try to focus next available session at same index, or previous if at end
                if self.session_ids:
                    # Focus the session at the same index, or the last one if index is now out of bounds
                    focus_index = min(session_index, len(self.session_ids) - 1)
                    self.focused_session_id = self.session_ids[focus_index]
                else:
                    self.focused_session_id = None

            self.update_modified_time()
            return True
        return False

    def set_focus(self, session_id: Optional[str]) -> bool:
        """Set the focused session for this workspace.

        Args:
            session_id: UUID of session to focus, or None to clear focus

        Returns:
            True if focus was set successfully, False if session not in workspace

        Note:
            Passing None always succeeds and clears focus.
            Updates modified_at timestamp on successful focus change.
        """
        if session_id is None:
            self.focused_session_id = None
            self.update_modified_time()
            return True

        if session_id in self.session_ids:
            self.focused_session_id = session_id
            self.update_modified_time()
            return True

        return False

    def set_layout_mode(self, mode: LayoutMode) -> None:
        """Change the layout mode for this workspace.

        Args:
            mode: New layout mode to apply

        Note:
            Automatically updates modified_at timestamp.
        """
        self.layout_mode = mode
        self.update_modified_time()

    def is_empty(self) -> bool:
        """Check if workspace has no sessions.

        Returns:
            True if workspace contains no sessions, False otherwise
        """
        return len(self.session_ids) == 0


class WorkspaceManager:
    """Manager for workspace lifecycle and operations.

    This class handles the creation, modification, and navigation of workspaces.
    It maintains the global workspace state including which workspace is currently active.

    Attributes:
        workspaces: Dictionary mapping workspace id (1-9) to Workspace objects
        active_workspace_id: ID of the currently active workspace

    Design Notes:
        - All 9 workspaces are created at initialization with default names
        - Workspace 1 is active by default
        - Operations are atomic and update timestamps automatically
        - Methods validate workspace IDs before performing operations

    Thread Safety:
        This class is NOT thread-safe. Use external synchronization if accessing
        from multiple threads.
    """

    def __init__(self) -> None:
        """Initialize workspace manager with 9 empty workspaces.

        Creates workspaces 1-9 with default names ("Workspace 1", etc.).
        Sets workspace 1 as the initially active workspace.
        """
        self.workspaces: Dict[int, Workspace] = {}
        self.active_workspace_id: int = 1

        # Pre-create all 9 workspaces with default names
        for i in range(1, 10):
            self.workspaces[i] = Workspace(
                id=i,
                name=f"Workspace {i}"
            )

    def create_workspace(self, workspace_id: int, name: str) -> Workspace:
        """Create or recreate a workspace with a specific name.

        Args:
            workspace_id: Workspace identifier (1-9)
            name: User-visible name for the workspace

        Returns:
            The created Workspace object

        Raises:
            ValueError: If workspace_id is not in range 1-9

        Note:
            If workspace already exists, it is replaced with a new empty workspace.
            Use rename_workspace() if you want to rename without clearing sessions.
        """
        if not 1 <= workspace_id <= 9:
            raise ValueError(f"Workspace id must be between 1 and 9, got {workspace_id}")

        workspace = Workspace(id=workspace_id, name=name)
        self.workspaces[workspace_id] = workspace
        return workspace

    def get_workspace(self, workspace_id: int) -> Optional[Workspace]:
        """Retrieve a workspace by its ID.

        Args:
            workspace_id: Workspace identifier (1-9)

        Returns:
            Workspace object if found, None otherwise
        """
        return self.workspaces.get(workspace_id)

    def get_active_workspace(self) -> Workspace:
        """Get the currently active workspace.

        Returns:
            The active Workspace object

        Note:
            This method always returns a valid workspace since all 9 are pre-created.
        """
        return self.workspaces[self.active_workspace_id]

    def switch_to_workspace(self, workspace_id: int) -> bool:
        """Switch to a different workspace.

        Args:
            workspace_id: ID of workspace to activate (1-9)

        Returns:
            True if switch was successful, False if workspace doesn't exist

        Note:
            Switching updates the active_workspace_id but does not affect
            individual workspace state.
        """
        if workspace_id in self.workspaces:
            self.active_workspace_id = workspace_id
            return True
        return False

    def rename_workspace(self, workspace_id: int, name: str) -> bool:
        """Rename an existing workspace.

        Args:
            workspace_id: ID of workspace to rename (1-9)
            name: New name for the workspace

        Returns:
            True if rename was successful, False if workspace doesn't exist

        Note:
            Updates the workspace's modified_at timestamp.
            Does not affect sessions or layout.
        """
        workspace = self.workspaces.get(workspace_id)
        if workspace:
            workspace.name = name
            workspace.update_modified_time()
            return True
        return False

    def add_session_to_workspace(self, workspace_id: int, session_id: str) -> bool:
        """Add a session to a specific workspace.

        Args:
            workspace_id: ID of workspace to add session to (1-9)
            session_id: UUID of the session to add

        Returns:
            True if session was added, False if workspace doesn't exist

        Note:
            If workspace is empty, the added session becomes the focused session.
            If session already exists in workspace, it is not added again.
        """
        workspace = self.workspaces.get(workspace_id)
        if workspace:
            was_empty = workspace.is_empty()
            workspace.add_session(session_id)

            # Auto-focus first session in empty workspace
            if was_empty and session_id in workspace.session_ids:
                workspace.set_focus(session_id)

            return True
        return False

    def remove_session_from_workspace(self, workspace_id: int, session_id: str) -> bool:
        """Remove a session from a specific workspace.

        Args:
            workspace_id: ID of workspace to remove session from (1-9)
            session_id: UUID of the session to remove

        Returns:
            True if session was removed, False if not found or workspace doesn't exist

        Note:
            If removing the focused session, focus automatically shifts to the next
            available session (or None if workspace becomes empty).
        """
        workspace = self.workspaces.get(workspace_id)
        if workspace:
            return workspace.remove_session(session_id)
        return False

    def move_session(self, session_id: str, from_workspace_id: int, to_workspace_id: int) -> bool:
        """Move a session from one workspace to another.

        Args:
            session_id: UUID of the session to move
            from_workspace_id: Source workspace ID (1-9)
            to_workspace_id: Destination workspace ID (1-9)

        Returns:
            True if move was successful, False if either workspace doesn't exist
            or session not found in source workspace

        Note:
            This is an atomic operation - session is removed from source and added
            to destination. If destination add fails, source removal is not reverted.
            Consider this when handling edge cases.
        """
        from_workspace = self.workspaces.get(from_workspace_id)
        to_workspace = self.workspaces.get(to_workspace_id)

        if not from_workspace or not to_workspace:
            return False

        # Verify session exists in source workspace
        if session_id not in from_workspace.session_ids:
            return False

        # Perform the move
        from_workspace.remove_session(session_id)
        to_workspace.add_session(session_id)

        # If destination was empty, focus the moved session
        if len(to_workspace.session_ids) == 1:
            to_workspace.set_focus(session_id)

        return True

    def get_session_workspace(self, session_id: str) -> Optional[int]:
        """Find which workspace contains a given session.

        Args:
            session_id: UUID of the session to find

        Returns:
            Workspace ID (1-9) if session found, None otherwise

        Note:
            This performs a linear search across all workspaces.
            Consider caching results if calling frequently.
        """
        for workspace_id, workspace in self.workspaces.items():
            if session_id in workspace.session_ids:
                return workspace_id
        return None

    def list_workspaces(self) -> List[Workspace]:
        """Get a list of all workspaces.

        Returns:
            List of Workspace objects sorted by ID (1-9)

        Note:
            Returns a new list; modifications to the list do not affect the manager.
        """
        return [self.workspaces[i] for i in range(1, 10)]

    def get_workspace_session_count(self, workspace_id: int) -> int:
        """Get the number of sessions in a workspace.

        Args:
            workspace_id: ID of workspace to query (1-9)

        Returns:
            Number of sessions in workspace, or 0 if workspace doesn't exist
        """
        workspace = self.workspaces.get(workspace_id)
        return len(workspace.session_ids) if workspace else 0

    def clear_workspace(self, workspace_id: int) -> bool:
        """Remove all sessions from a workspace.

        Args:
            workspace_id: ID of workspace to clear (1-9)

        Returns:
            True if workspace was cleared, False if workspace doesn't exist

        Note:
            Resets focused_session_id to None.
            Does not modify workspace name or layout mode.
            Updates modified_at timestamp.
        """
        workspace = self.workspaces.get(workspace_id)
        if workspace:
            workspace.session_ids.clear()
            workspace.focused_session_id = None
            workspace.update_modified_time()
            return True
        return False

    def set_workspace_layout(self, workspace_id: int, layout_mode: LayoutMode) -> bool:
        """Change the layout mode for a workspace.

        Args:
            workspace_id: ID of workspace to modify (1-9)
            layout_mode: New layout mode to apply

        Returns:
            True if layout was changed, False if workspace doesn't exist

        Note:
            Updates modified_at timestamp.
        """
        workspace = self.workspaces.get(workspace_id)
        if workspace:
            workspace.set_layout_mode(layout_mode)
            return True
        return False
