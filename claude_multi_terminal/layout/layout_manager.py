"""Layout Manager - Integration layer between workspaces and BSP/Stack/Tab layout engines.

This module provides the LayoutManager class that bridges workspace management with
various layout modes (BSP tiling, Stack, and Tab). It maintains per-workspace layout
state and handles smooth transitions between layout modes.

Architecture:
    - LayoutManager: Main integration class coordinating all layout operations
    - Per-workspace layout state (BSP trees, stack orders, tab indices)
    - Mode-specific layout calculation methods
    - Efficient layout transitions preserving session state

Layout Modes:
    - BSP (TILED): Binary space partitioning for dynamic tiling
    - STACK (MONOCLE): Single maximized pane with cycling
    - TAB: Tab bar with single visible session

Design Philosophy:
    - Preserve session order across mode changes
    - Efficient layout calculations (< 5ms target)
    - Type-safe with comprehensive error handling
    - Clear separation between layout logic and rendering
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from claude_multi_terminal.workspaces import LayoutMode, Workspace


# Layout direction enum for BSP splits
class SplitDirection(Enum):
    """Direction for BSP split operations."""
    HORIZONTAL = "horizontal"  # Split horizontally (top/bottom)
    VERTICAL = "vertical"      # Split vertically (left/right)


@dataclass
class LayoutRect:
    """Rectangle representing a layout region in terminal grid coordinates.

    Attributes:
        x: Column offset from left (0-based)
        y: Row offset from top (0-based)
        width: Width in columns
        height: Height in rows
    """
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        """Validate rectangle dimensions."""
        if self.width < 1 or self.height < 1:
            raise ValueError(f"Invalid dimensions: {self.width}x{self.height}")


@dataclass
class SessionLayout:
    """Layout information for a single session pane.

    Attributes:
        session_id: UUID of the session
        rect: Terminal grid rectangle for this session
        visible: Whether session is currently visible
        focused: Whether session has focus
        tab_index: Index in tab bar (for TAB mode), None otherwise
    """
    session_id: str
    rect: LayoutRect
    visible: bool = True
    focused: bool = False
    tab_index: Optional[int] = None


@dataclass
class WorkspaceLayoutState:
    """Per-workspace layout state for all modes.

    Attributes:
        workspace_id: Associated workspace ID (1-9)
        mode: Current layout mode
        bsp_tree: BSP tree structure (for TILED mode)
        stack_order: Session stack ordering (for MONOCLE/stack mode)
        stack_index: Current position in stack
        tab_index: Current tab selection (for TAB mode)
        last_layouts: Cached layout calculations
        modified_at: Last modification timestamp
    """
    workspace_id: int
    mode: LayoutMode = LayoutMode.TILED
    bsp_tree: Optional['BSPTree'] = None
    stack_order: List[str] = field(default_factory=list)
    stack_index: int = 0
    tab_index: int = 0
    last_layouts: List[SessionLayout] = field(default_factory=list)
    modified_at: float = field(default_factory=time.time)

    def mark_modified(self) -> None:
        """Update modification timestamp."""
        self.modified_at = time.time()


class LayoutManager:
    """Manager for integrating layout engines with workspace system.

    This class coordinates layout operations across all workspaces, managing
    transitions between layout modes and calculating efficient pane layouts.

    Attributes:
        workspace_layouts: Per-workspace layout state storage
        current_workspace: Currently active workspace ID
        viewport_width: Terminal width in columns
        viewport_height: Terminal height in rows

    Performance:
        - Layout calculations target < 5ms
        - Caches computed layouts per workspace
        - Invalidates cache on state changes only
    """

    def __init__(self, viewport_width: int = 80, viewport_height: int = 24) -> None:
        """Initialize layout manager with viewport dimensions.

        Args:
            viewport_width: Terminal width in columns
            viewport_height: Terminal height in rows
        """
        self.workspace_layouts: Dict[int, WorkspaceLayoutState] = {}
        self.current_workspace: int = 1
        self.viewport_width: int = viewport_width
        self.viewport_height: int = viewport_height

        # Pre-create layout states for all 9 workspaces
        for ws_id in range(1, 10):
            self.workspace_layouts[ws_id] = WorkspaceLayoutState(workspace_id=ws_id)

    def set_viewport_size(self, width: int, height: int) -> None:
        """Update viewport dimensions and invalidate layout cache.

        Args:
            width: New terminal width in columns
            height: New terminal height in rows
        """
        if width < 1 or height < 1:
            raise ValueError(f"Invalid viewport size: {width}x{height}")

        self.viewport_width = width
        self.viewport_height = height

        # Invalidate all cached layouts
        for state in self.workspace_layouts.values():
            state.last_layouts.clear()
            state.mark_modified()

    def get_layout_state(self, workspace_id: int) -> Optional[WorkspaceLayoutState]:
        """Get layout state for a specific workspace.

        Args:
            workspace_id: Workspace ID (1-9)

        Returns:
            WorkspaceLayoutState if found, None otherwise
        """
        return self.workspace_layouts.get(workspace_id)

    def apply_layout(
        self,
        workspace: Workspace,
        force_recalc: bool = False
    ) -> List[SessionLayout]:
        """Calculate layout for all sessions in a workspace.

        This is the main entry point for layout calculation. It delegates to
        mode-specific methods and caches results.

        Args:
            workspace: Workspace to calculate layout for
            force_recalc: Force recalculation even if cache valid

        Returns:
            List of SessionLayout objects with position/visibility info
        """
        state = self.workspace_layouts.get(workspace.id)
        if not state:
            return []

        # Return cached layout if valid
        if not force_recalc and state.last_layouts:
            return state.last_layouts

        # Calculate based on current mode
        if workspace.layout_mode == LayoutMode.TILED:
            layouts = self._calculate_bsp_layout(workspace, state)
        elif workspace.layout_mode == LayoutMode.MONOCLE:
            layouts = self._calculate_stack_layout(workspace, state)
        else:  # FLOATING - treat as tabs for now
            layouts = self._calculate_tab_layout(workspace, state)

        # Cache and return
        state.last_layouts = layouts
        state.mark_modified()
        return layouts

    def _calculate_bsp_layout(
        self,
        workspace: Workspace,
        state: WorkspaceLayoutState
    ) -> List[SessionLayout]:
        """Calculate BSP tiling layout for workspace.

        Args:
            workspace: Source workspace
            state: Layout state

        Returns:
            List of SessionLayout objects with tiled positions
        """
        sessions = workspace.session_ids
        if not sessions:
            return []

        # Single session - fullscreen
        if len(sessions) == 1:
            return [SessionLayout(
                session_id=sessions[0],
                rect=LayoutRect(0, 0, self.viewport_width, self.viewport_height),
                visible=True,
                focused=(sessions[0] == workspace.focused_session_id)
            )]

        # Multiple sessions - use simple grid for now (BSP tree integration point)
        # TODO: Replace with actual BSP tree traversal when bsp_engine is available
        layouts = self._simple_grid_layout(sessions, workspace.focused_session_id)
        return layouts

    def _simple_grid_layout(
        self,
        sessions: List[str],
        focused_id: Optional[str]
    ) -> List[SessionLayout]:
        """Calculate simple grid layout as BSP fallback.

        Arranges sessions in a grid pattern with approximately equal sizes.
        This is a placeholder until BSP tree is integrated.

        Args:
            sessions: List of session IDs
            focused_id: ID of focused session

        Returns:
            List of SessionLayout objects in grid arrangement
        """
        import math

        count = len(sessions)
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)

        col_width = self.viewport_width // cols
        row_height = self.viewport_height // rows

        layouts = []
        for idx, session_id in enumerate(sessions):
            col = idx % cols
            row = idx // cols

            # Calculate dimensions (give extra space to last column/row)
            x = col * col_width
            y = row * row_height
            width = (
                self.viewport_width - x if col == cols - 1
                else col_width
            )
            height = (
                self.viewport_height - y if row == rows - 1
                else row_height
            )

            layouts.append(SessionLayout(
                session_id=session_id,
                rect=LayoutRect(x, y, width, height),
                visible=True,
                focused=(session_id == focused_id)
            ))

        return layouts

    def _calculate_stack_layout(
        self,
        workspace: Workspace,
        state: WorkspaceLayoutState
    ) -> List[SessionLayout]:
        """Calculate stack (monocle) layout - single maximized pane.

        Args:
            workspace: Source workspace
            state: Layout state

        Returns:
            List with single visible SessionLayout
        """
        sessions = workspace.session_ids
        if not sessions:
            return []

        # Sync stack order with workspace sessions
        self._sync_stack_order(state, sessions)

        # Ensure stack index is valid
        if state.stack_index >= len(state.stack_order):
            state.stack_index = 0

        # Get current session in stack
        visible_session = state.stack_order[state.stack_index]

        # Create layouts - only one visible
        layouts = []
        for session_id in sessions:
            is_visible = (session_id == visible_session)
            layouts.append(SessionLayout(
                session_id=session_id,
                rect=LayoutRect(0, 0, self.viewport_width, self.viewport_height),
                visible=is_visible,
                focused=(is_visible and session_id == workspace.focused_session_id)
            ))

        return layouts

    def _calculate_tab_layout(
        self,
        workspace: Workspace,
        state: WorkspaceLayoutState
    ) -> List[SessionLayout]:
        """Calculate tab layout - tab bar with single visible session.

        Args:
            workspace: Source workspace
            state: Layout state

        Returns:
            List of SessionLayout objects with tab indices
        """
        sessions = workspace.session_ids
        if not sessions:
            return []

        # Ensure tab index is valid
        if state.tab_index >= len(sessions):
            state.tab_index = 0

        visible_session_id = sessions[state.tab_index]

        # Reserve 1 row for tab bar at top
        tab_bar_height = 1
        content_height = max(1, self.viewport_height - tab_bar_height)

        layouts = []
        for idx, session_id in enumerate(sessions):
            is_visible = (session_id == visible_session_id)
            layouts.append(SessionLayout(
                session_id=session_id,
                rect=LayoutRect(0, tab_bar_height, self.viewport_width, content_height),
                visible=is_visible,
                focused=(is_visible and session_id == workspace.focused_session_id),
                tab_index=idx
            ))

        return layouts

    def _sync_stack_order(self, state: WorkspaceLayoutState, sessions: List[str]) -> None:
        """Synchronize stack order with current session list.

        Args:
            state: Layout state to update
            sessions: Current session list from workspace
        """
        # Remove sessions no longer in workspace
        state.stack_order = [s for s in state.stack_order if s in sessions]

        # Add new sessions to end of stack
        for session_id in sessions:
            if session_id not in state.stack_order:
                state.stack_order.append(session_id)

    def add_session_to_layout(self, workspace_id: int, session_id: str) -> bool:
        """Add a session to the workspace layout.

        Args:
            workspace_id: Target workspace ID (1-9)
            session_id: Session UUID to add

        Returns:
            True if added successfully, False if workspace not found
        """
        state = self.workspace_layouts.get(workspace_id)
        if not state:
            return False

        # Add to stack order if not present
        if session_id not in state.stack_order:
            state.stack_order.append(session_id)

        # Invalidate layout cache
        state.last_layouts.clear()
        state.mark_modified()

        return True

    def remove_session_from_layout(self, workspace_id: int, session_id: str) -> bool:
        """Remove a session from the workspace layout.

        Args:
            workspace_id: Target workspace ID (1-9)
            session_id: Session UUID to remove

        Returns:
            True if removed successfully, False if workspace not found
        """
        state = self.workspace_layouts.get(workspace_id)
        if not state:
            return False

        # Remove from stack order
        if session_id in state.stack_order:
            state.stack_order.remove(session_id)

            # Adjust stack index if needed
            if state.stack_index >= len(state.stack_order) and state.stack_order:
                state.stack_index = len(state.stack_order) - 1

        # Invalidate layout cache
        state.last_layouts.clear()
        state.mark_modified()

        return True

    def cycle_stack(self, workspace_id: int, direction: int = 1) -> bool:
        """Cycle through sessions in stack mode.

        Args:
            workspace_id: Target workspace ID (1-9)
            direction: 1 for next, -1 for previous

        Returns:
            True if cycled successfully, False if workspace not found or not in stack mode
        """
        state = self.workspace_layouts.get(workspace_id)
        if not state or state.mode != LayoutMode.MONOCLE:
            return False

        if not state.stack_order:
            return False

        # Cycle index with wraparound
        state.stack_index = (state.stack_index + direction) % len(state.stack_order)

        # Invalidate layout cache
        state.last_layouts.clear()
        state.mark_modified()

        return True

    def switch_tab(self, workspace_id: int, tab_index: int) -> bool:
        """Switch to a specific tab.

        Args:
            workspace_id: Target workspace ID (1-9)
            tab_index: Tab index to switch to (0-based)

        Returns:
            True if switched successfully, False if invalid
        """
        state = self.workspace_layouts.get(workspace_id)
        if not state:
            return False

        # Validate tab index (will be validated against actual session count in apply_layout)
        if tab_index < 0:
            return False

        state.tab_index = tab_index

        # Invalidate layout cache
        state.last_layouts.clear()
        state.mark_modified()

        return True

    def change_layout_mode(self, workspace_id: int, mode: LayoutMode) -> bool:
        """Change layout mode for a workspace.

        Preserves session list across mode transitions.

        Args:
            workspace_id: Target workspace ID (1-9)
            mode: New layout mode to apply

        Returns:
            True if changed successfully, False if workspace not found
        """
        state = self.workspace_layouts.get(workspace_id)
        if not state:
            return False

        # No-op if already in this mode
        if state.mode == mode:
            return True

        # Transition logic
        old_mode = state.mode
        state.mode = mode

        # Reset indices when changing modes
        if mode == LayoutMode.MONOCLE:
            state.stack_index = 0
        elif mode == LayoutMode.FLOATING:
            state.tab_index = 0

        # Invalidate layout cache
        state.last_layouts.clear()
        state.mark_modified()

        return True

    def adjust_split(
        self,
        workspace_id: int,
        direction: SplitDirection,
        delta: int
    ) -> bool:
        """Adjust BSP split size (resize operation).

        This is a placeholder for BSP tree integration.

        Args:
            workspace_id: Target workspace ID (1-9)
            direction: Direction of split to adjust
            delta: Size adjustment in terminal cells

        Returns:
            True if adjusted successfully, False if not in BSP mode or workspace not found
        """
        state = self.workspace_layouts.get(workspace_id)
        if not state or state.mode != LayoutMode.TILED:
            return False

        # TODO: Implement BSP tree split adjustment when bsp_engine is available
        # For now, invalidate cache to trigger recalculation
        state.last_layouts.clear()
        state.mark_modified()

        return True

    def get_focused_session_layout(
        self,
        workspace: Workspace
    ) -> Optional[SessionLayout]:
        """Get layout info for the focused session in a workspace.

        Args:
            workspace: Source workspace

        Returns:
            SessionLayout for focused session, or None if no focus
        """
        if not workspace.focused_session_id:
            return None

        layouts = self.apply_layout(workspace)
        for layout in layouts:
            if layout.session_id == workspace.focused_session_id:
                return layout

        return None
