"""
Example code showing how to integrate workspace indicators with the main app.

This is a reference implementation - not meant to be run directly.
Shows how to add workspace switching functionality to ClaudeMultiTerminalApp.
"""

from textual.binding import Binding
from typing import Dict, List


# ============================================================================
# STEP 1: Add workspace state to app initialization
# ============================================================================

class ClaudeMultiTerminalApp(App):
    """Extended app with workspace support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ... existing initialization ...

        # Add workspace state
        self.current_workspace = 1
        self.workspaces: Dict[int, List[SessionPane]] = {i: [] for i in range(1, 10)}
        # Store sessions by workspace ID


# ============================================================================
# STEP 2: Add workspace switching keybindings
# ============================================================================

    BINDINGS = [
        # ... existing bindings ...

        # Workspace switching (Alt+1 through Alt+9)
        Binding("alt+1", "switch_workspace(1)", "Workspace 1", priority=True),
        Binding("alt+2", "switch_workspace(2)", "Workspace 2", priority=True),
        Binding("alt+3", "switch_workspace(3)", "Workspace 3", priority=True),
        Binding("alt+4", "switch_workspace(4)", "Workspace 4", priority=True),
        Binding("alt+5", "switch_workspace(5)", "Workspace 5", priority=True),
        Binding("alt+6", "switch_workspace(6)", "Workspace 6", priority=True),
        Binding("alt+7", "switch_workspace(7)", "Workspace 7", priority=True),
        Binding("alt+8", "switch_workspace(8)", "Workspace 8", priority=True),
        Binding("alt+9", "switch_workspace(9)", "Workspace 9", priority=True),

        # Move session to workspace (Ctrl+Shift+1 through Ctrl+Shift+9)
        Binding("ctrl+shift+1", "move_to_workspace(1)", "Move to WS 1"),
        Binding("ctrl+shift+2", "move_to_workspace(2)", "Move to WS 2"),
        Binding("ctrl+shift+3", "move_to_workspace(3)", "Move to WS 3"),
        Binding("ctrl+shift+4", "move_to_workspace(4)", "Move to WS 4"),
        Binding("ctrl+shift+5", "move_to_workspace(5)", "Move to WS 5"),
        Binding("ctrl+shift+6", "move_to_workspace(6)", "Move to WS 6"),
        Binding("ctrl+shift+7", "move_to_workspace(7)", "Move to WS 7"),
        Binding("ctrl+shift+8", "move_to_workspace(8)", "Move to WS 8"),
        Binding("ctrl+shift+9", "move_to_workspace(9)", "Move to WS 9"),
    ]


# ============================================================================
# STEP 3: Implement workspace switching action
# ============================================================================

    async def action_switch_workspace(self, workspace_id: int) -> None:
        """Switch to a different workspace.

        Args:
            workspace_id: Target workspace (1-9)
        """
        if not 1 <= workspace_id <= 9:
            self.notify(f"Invalid workspace ID: {workspace_id}", severity="error")
            return

        if workspace_id == self.current_workspace:
            # Already on this workspace
            return

        # Save current workspace sessions
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        self.workspaces[self.current_workspace] = list(grid.panes)

        # Clear grid
        for pane in list(grid.panes):
            await grid.remove_pane(pane)

        # Update current workspace
        old_workspace = self.current_workspace
        self.current_workspace = workspace_id

        # Load target workspace sessions
        target_sessions = self.workspaces[workspace_id]
        if target_sessions:
            for pane in target_sessions:
                await grid.add_pane(pane)
        else:
            # Empty workspace - create default session
            await self.action_new_session()

        # Update header
        await self._update_workspace_indicators()

        # Notify user
        self.notify(
            f"Switched from workspace {old_workspace} to {workspace_id}",
            severity="information",
            timeout=2
        )


# ============================================================================
# STEP 4: Implement move session to workspace action
# ============================================================================

    async def action_move_to_workspace(self, workspace_id: int) -> None:
        """Move the focused session to a different workspace.

        Args:
            workspace_id: Target workspace (1-9)
        """
        if not 1 <= workspace_id <= 9:
            return

        if workspace_id == self.current_workspace:
            self.notify("Already in this workspace", severity="information")
            return

        # Get focused pane
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        focused_pane = None
        for pane in grid.panes:
            if pane.has_focus:
                focused_pane = pane
                break

        if not focused_pane:
            self.notify("No session focused", severity="warning")
            return

        # Remove from current workspace
        await grid.remove_pane(focused_pane)
        self.workspaces[self.current_workspace].remove(focused_pane)

        # Add to target workspace
        self.workspaces[workspace_id].append(focused_pane)

        # Update indicators
        await self._update_workspace_indicators()

        # Notify
        self.notify(
            f"Moved session to workspace {workspace_id}",
            severity="information",
            timeout=2
        )


# ============================================================================
# STEP 5: Update workspace indicators helper
# ============================================================================

    async def _update_workspace_indicators(self) -> None:
        """Update workspace indicators in header bar."""
        header = self.query_one(HeaderBar)

        # Set active workspace
        header.set_active_workspace(self.current_workspace)

        # Update session counts for all workspaces
        session_counts = {
            ws_id: len(sessions)
            for ws_id, sessions in self.workspaces.items()
        }
        header.update_all_workspace_sessions(session_counts)

        # Update total session count
        total_sessions = sum(len(sessions) for sessions in self.workspaces.values())
        header.session_count = total_sessions


# ============================================================================
# STEP 6: Update on_mount to initialize workspace indicators
# ============================================================================

    async def on_mount(self) -> None:
        """Initialize the application with workspace support."""
        # ... existing initialization code ...

        # Initialize workspace 1 with current sessions
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        self.workspaces[1] = list(grid.panes)

        # Update workspace indicators
        await self._update_workspace_indicators()


# ============================================================================
# STEP 7: Update session creation to track workspace
# ============================================================================

    async def action_new_session(self) -> None:
        """Create a new session in the current workspace."""
        # ... existing session creation code ...

        # Add to current workspace
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        if grid.panes:
            newest_pane = grid.panes[-1]  # Get the newly created pane
            if newest_pane not in self.workspaces[self.current_workspace]:
                self.workspaces[self.current_workspace].append(newest_pane)

        # Update indicators
        await self._update_workspace_indicators()


# ============================================================================
# STEP 8: Update session closing to track workspace
# ============================================================================

    async def action_close_session(self) -> None:
        """Close the focused session and update workspace."""
        # Get focused pane before closing
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        focused_pane = None
        for pane in grid.panes:
            if pane.has_focus:
                focused_pane = pane
                break

        # ... existing session closing code ...

        # Remove from workspace
        if focused_pane and focused_pane in self.workspaces[self.current_workspace]:
            self.workspaces[self.current_workspace].remove(focused_pane)

        # Update indicators
        await self._update_workspace_indicators()


# ============================================================================
# STEP 9: Add workspace persistence
# ============================================================================

    async def _save_workspace_state(self) -> None:
        """Save all workspaces to disk."""
        workspace_data = {
            'current_workspace': self.current_workspace,
            'workspaces': {}
        }

        for ws_id, panes in self.workspaces.items():
            workspace_data['workspaces'][ws_id] = [
                self._capture_session_state(pane)
                for pane in panes
            ]

        # Save using existing storage
        self.storage.save_workspace_state(workspace_data)

    async def _load_workspace_state(self) -> None:
        """Load all workspaces from disk."""
        workspace_data = self.storage.load_workspace_state()

        if not workspace_data:
            return

        # Restore workspaces
        self.current_workspace = workspace_data.get('current_workspace', 1)
        # ... restore panes for each workspace ...

        # Update indicators
        await self._update_workspace_indicators()


# ============================================================================
# EXAMPLE USAGE IN PRACTICE
# ============================================================================

"""
User workflow examples:

1. Switch to workspace 3:
   - Press Alt+3
   - Current sessions are saved to current workspace
   - Workspace 3 sessions are loaded (or empty workspace created)
   - Header shows [3] with coral background

2. Move session to workspace 5:
   - Focus the session to move
   - Press Ctrl+Shift+5
   - Session disappears from current workspace
   - Session is now in workspace 5
   - Header updates to show workspace 5 has sessions: [5•1]

3. View workspace status:
   - Look at header bar
   - Active workspace has coral background: [2•3]
   - Other workspaces with sessions shown in gray: [1•2] [5•1]
   - Empty workspaces very dim: [4] [6] [7] [8] [9]
   - Total sessions shown: ● 6 Active

4. Quick workspace navigation:
   - Alt+1 → Workspace 1 (development)
   - Alt+2 → Workspace 2 (testing)
   - Alt+3 → Workspace 3 (documentation)
   - etc.

5. Organize by project:
   - Workspace 1: Project A sessions
   - Workspace 2: Project B sessions
   - Workspace 3: Project C sessions
   - Workspace 9: Scratch space
"""


# ============================================================================
# ADVANCED: Click handler for workspace indicators (future enhancement)
# ============================================================================

"""
To add click handling for workspace indicators:

1. Make workspace indicators clickable regions in header_bar.py
2. Emit custom messages when clicked
3. Handle messages in app.py:

class WorkspaceClicked(Message):
    def __init__(self, workspace_id: int):
        super().__init__()
        self.workspace_id = workspace_id

# In HeaderBar:
async def on_click(self, event: Click) -> None:
    # Determine which workspace was clicked based on click position
    workspace_id = self._get_workspace_at_position(event.x)
    if workspace_id:
        self.post_message(WorkspaceClicked(workspace_id))

# In App:
async def on_workspace_clicked(self, message: WorkspaceClicked) -> None:
    await self.action_switch_workspace(message.workspace_id)
"""
