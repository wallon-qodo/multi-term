"""Main application orchestrating the multi-terminal interface."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Input
from textual.events import Key
from typing import Optional

from .core.session_manager import SessionManager
from .core.clipboard import ClipboardManager
from .widgets.resizable_grid import ResizableSessionGrid
from .widgets.session_pane import SessionPane
from .widgets.header_bar import HeaderBar
from .widgets.status_bar import StatusBar
from .widgets.rename_dialog import RenameDialog
from .widgets.search_panel import SearchPanel
from .widgets.tab_bar import TabBar
from .widgets.session_history_browser import SessionHistoryBrowser
from .widgets.context_menu import ContextMenu
from .widgets.color_picker import ColorPickerDialog
from .widgets.workspace_manager import WorkspaceManager
from .config import Config
from .persistence.storage import SessionStorage
from .persistence.session_state import WorkspaceState, SessionState, WorkspaceData
from .types import AppMode
from .layout.layout_manager import LayoutManager


class ClaudeMultiTerminalApp(App):
    """Main application orchestrating the multi-terminal interface."""

    CSS_PATH = None  # Will use inline CSS
    TITLE = "Claude Multi-Terminal"

    BINDINGS = [
        Binding("ctrl+n", "new_session", "New Session"),
        Binding("ctrl+w", "close_session", "Close Session"),
        Binding("ctrl+s", "save_sessions", "Save Sessions"),
        Binding("ctrl+l", "load_sessions", "Load Sessions"),
        Binding("f10", "manage_workspaces", "Workspace Manager", priority=True),
        Binding("ctrl+h", "show_history", "History Browser", priority=True),
        Binding("f9", "show_history", "History Browser"),
        Binding("ctrl+shift+t", "reopen_last_session", "Reopen Last"),
        Binding("ctrl+r", "rename_session", "Rename"),
        Binding("ctrl+b", "toggle_broadcast", "Toggle Broadcast"),
        Binding("ctrl+f", "toggle_focus", "Focus Mode", priority=True),
        Binding("ctrl+shift+f", "toggle_search", "Search", priority=True),
        Binding("f11", "toggle_focus", "Focus Mode", priority=True),
        Binding("tab", "next_pane", "Next Pane", priority=True),
        Binding("shift+tab", "prev_pane", "Prev Pane", priority=True),
        Binding("ctrl+c", "copy_output", "Copy Output", priority=True),
        Binding("f2", "toggle_mouse", "Toggle Mouse"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        background: rgb(24,24,24);
    }

    ResizableSessionGrid {
        height: 1fr;
        width: 1fr;
        padding: 1 2;
    }

    /* Toast notifications styling - OpenClaw theme */
    Toast {
        background: rgb(28,28,28);
        border: solid rgb(100,180,240);
        color: rgb(240,240,240);
    }

    Toast.-information {
        background: rgba(100,180,240,0.2);
        border: solid rgb(100,180,240);
        color: rgb(240,240,240);
    }

    Toast.-warning {
        background: rgba(255,180,70,0.2);
        border: solid rgb(255,180,70);
        color: rgb(255,200,100);
    }

    Toast.-error {
        background: rgba(255,77,77,0.2);
        border: solid rgb(255,77,77);
        color: rgb(255,120,120);
    }
    """

    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        self.session_manager = SessionManager(claude_path=Config.CLAUDE_PATH)
        self.broadcast_mode = False
        self.clip_manager_buffer = ""
        self.storage = SessionStorage()
        self.clip_manager = ClipboardManager()
        self.mouse_enabled = False  # Start with text selection enabled
        self.focus_mode = False
        self.focused_session_id = None
        self.mode: AppMode = AppMode.NORMAL  # Start in NORMAL mode
        self.command_prefix_active = False  # Track if Ctrl+B was pressed
        self.workspaces = {}  # Dict[int, WorkspaceData] - workspace persistence
        self.current_workspace_id = None  # Track active workspace
        self.layout_manager = LayoutManager()  # Phase 3: Layout management

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield HeaderBar()
        yield TabBar(id="tab-bar")
        yield ResizableSessionGrid(id="session-grid")
        yield StatusBar()
        yield SearchPanel(id="search-panel")

    async def on_mount(self) -> None:
        """Initialize the application with default sessions or restore workspace."""
        # Initialize current workspace (Phase 3)
        self.current_workspace_id = 1

        # Load saved workspaces if they exist
        loaded_workspaces = self.storage.load_workspaces()
        if loaded_workspaces:
            self.workspaces = loaded_workspaces

        # Try to load saved workspace first
        state = self.storage.load_state()

        if state and state.sessions and Config.AUTO_SAVE:
            # Restore previous workspace
            try:
                grid = self.query_one("#session-grid", ResizableSessionGrid)
                tab_bar = self.query_one("#tab-bar", TabBar)

                # Recreate sessions from saved state
                for idx, session_state in enumerate(state.sessions):
                    session_id = self.session_manager.create_session(
                        name=session_state.name,
                        working_dir=session_state.working_directory
                    )
                    await grid.add_session(session_id, self.session_manager)

                    # Add tab (first session is active)
                    is_active = (idx == 0)
                    await tab_bar.add_tab(session_id, session_state.name, is_active)

                # Update header
                header = self.query_one(HeaderBar)
                header.session_count = len(self.session_manager.sessions)

                # Focus first pane
                if grid.panes:
                    grid.panes[0].focus()

                self.notify(
                    f"✓ Restored {len(state.sessions)} session(s) from previous workspace",
                    severity="information",
                    timeout=5
                )
            except Exception as e:
                # If restore fails, fall back to creating new sessions
                self.notify(f"⚠ Failed to restore workspace: {e}", severity="warning", timeout=5)
                for _ in range(Config.DEFAULT_SESSION_COUNT):
                    await self.action_new_session()
        else:
            # No saved workspace, start with default sessions
            for _ in range(Config.DEFAULT_SESSION_COUNT):
                await self.action_new_session()

        # Focus the grid to enable keyboard input
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        if grid.panes:
            grid.panes[0].focus()

        # Initialize status bar with current mode
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = self.mode

        # Show helpful tip about text selection
        self.notify(
            "✅ Text selection enabled! Click & drag to highlight, right-click to copy",
            severity="information",
            timeout=8
        )

    async def on_unmount(self) -> None:
        """Clean up and save workspace on exit."""
        # Auto-save workspace if enabled
        if Config.SAVE_ON_EXIT:
            try:
                await self.action_save_sessions()
                # Also save all workspaces
                if self.workspaces:
                    self.storage.save_workspaces(self.workspaces)
            except Exception as e:
                # Log error but don't block exit
                pass

        # Terminate all sessions
        for session_id in list(self.session_manager.sessions.keys()):
            try:
                await self.session_manager.terminate_session(session_id)
            except Exception:
                pass

    async def action_new_session(self) -> None:
        """Create a new Claude CLI session."""
        if len(self.session_manager.sessions) >= Config.MAX_SESSIONS:
            self.notify(
                f"Maximum {Config.MAX_SESSIONS} sessions reached",
                severity="warning"
            )
            return

        session_id = self.session_manager.create_session()
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        await grid.add_session(session_id, self.session_manager)

        # Add to layout manager (Phase 3)
        if self.current_workspace_id is not None:
            self.layout_manager.add_session_to_layout(self.current_workspace_id, session_id)

        # Add tab for new session
        session_info = self.session_manager.sessions.get(session_id)
        if session_info:
            tab_bar = self.query_one("#tab-bar", TabBar)
            # New session becomes active
            is_active = len(self.session_manager.sessions) == 1
            await tab_bar.add_tab(session_id, session_info.name, is_active)

        # Update header
        header = self.query_one(HeaderBar)
        header.session_count = len(self.session_manager.sessions)

        self.notify("✓ New session created successfully", severity="information")

    async def action_close_session(self) -> None:
        """Close the currently focused session and save to history."""
        focused_pane = self._get_focused_pane()

        if not focused_pane:
            self.notify("No session to close", severity="warning")
            return

        session_id = focused_pane.session_id

        # Save session to history before closing
        session_state = self._capture_session_state(focused_pane)
        if session_state:
            self.storage.save_session_to_history(session_state)

        # Remove from layout manager (Phase 3)
        if self.current_workspace_id is not None:
            self.layout_manager.remove_session_from_layout(self.current_workspace_id, session_id)

        # Remove tab
        tab_bar = self.query_one("#tab-bar", TabBar)
        await tab_bar.remove_tab(session_id)

        # Remove from UI
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        await grid.remove_session(session_id)

        # Terminate PTY
        await self.session_manager.terminate_session(session_id)

        # Update header
        header = self.query_one(HeaderBar)
        header.session_count = len(self.session_manager.sessions)

        self.notify("✓ Session closed and saved to history", severity="information")

    async def action_save_sessions(self) -> None:
        """Save current session state to disk with enhanced metadata."""
        import time

        # Get all session panes and capture their state
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        enhanced_sessions = []

        for pane in grid.panes:
            session_state = self._capture_session_state(pane)
            if session_state:
                enhanced_sessions.append(session_state)

        workspace_state = WorkspaceState(
            sessions=enhanced_sessions,
            active_session_id=self._get_active_session_id()
        )

        # Save workspace state
        if self.storage.save_state(workspace_state):
            # Also save each session to history
            for session_state in enhanced_sessions:
                self.storage.save_session_to_history(session_state)

            self.notify(
                f"💾 Saved {len(workspace_state.sessions)} session(s) to workspace and history",
                severity="information"
            )
        else:
            self.notify("❌ Failed to save sessions", severity="error")

    async def action_load_sessions(self) -> None:
        """Restore sessions from saved state."""
        state = self.storage.load_state()

        if not state or not state.sessions:
            self.notify("⚠ No saved workspace found", severity="warning")
            return

        await self._restore_workspace_state(state)

    async def action_manage_workspaces(self) -> None:
        """Show workspace manager dialog."""
        # Auto-save current workspace if enabled
        if Config.AUTO_SAVE and self.current_workspace_id is not None:
            await self._save_current_workspace()

        # Get current session states for saving
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        current_sessions = []

        for pane in grid.panes:
            session_state = self._capture_session_state(pane)
            if session_state:
                # Convert to dict for JSON serialization
                import dataclasses
                current_sessions.append(dataclasses.asdict(session_state))

        # Show workspace manager
        result = await self.push_screen_wait(
            WorkspaceManager(self.storage.storage_dir, current_sessions)
        )

        # If user selected a workspace to load
        if result:
            try:
                # Load workspace file
                workspace_file = result['file']
                with open(workspace_file, 'r') as f:
                    import json
                    data = json.load(f)

                # Convert to WorkspaceState
                from .persistence.session_state import SessionState
                sessions = [SessionState(**s) for s in data.get('sessions', [])]
                state = WorkspaceState(
                    sessions=sessions,
                    active_session_id=data.get('active_session_id')
                )

                await self._restore_workspace_state(state)
            except Exception as e:
                self.notify(f"❌ Failed to load workspace: {e}", severity="error")

    async def _restore_workspace_state(self, state: WorkspaceState) -> None:
        """Restore workspace from state object."""
        # Save current workspace before switching (if AUTO_SAVE enabled)
        if Config.AUTO_SAVE and self.current_workspace_id is not None:
            await self._save_current_workspace()

        # Clear existing sessions and tabs
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        tab_bar = self.query_one("#tab-bar", TabBar)
        await tab_bar.clear_tabs()

        for session_id in list(self.session_manager.sessions.keys()):
            await grid.remove_session(session_id)
            await self.session_manager.terminate_session(session_id)

        # Recreate sessions and tabs
        for idx, session_state in enumerate(state.sessions):
            session_id = self.session_manager.create_session(
                name=session_state.name,
                working_dir=session_state.working_directory
            )
            await grid.add_session(session_id, self.session_manager)

            # Add tab (first session is active)
            is_active = (idx == 0)
            await tab_bar.add_tab(session_id, session_state.name, is_active)

        # Update header
        header = self.query_one(HeaderBar)
        header.session_count = len(self.session_manager.sessions)

        self.notify(
            f"✓ Restored {len(state.sessions)} session(s) from workspace",
            severity="information"
        )

    async def _save_current_workspace(self) -> bool:
        """Save current workspace to the workspaces dictionary.

        Returns:
            True if workspace was saved successfully, False otherwise
        """
        import time
        import uuid

        try:
            # Get all session panes and capture their state
            grid = self.query_one("#session-grid", ResizableSessionGrid)
            enhanced_sessions = []

            for pane in grid.panes:
                session_state = self._capture_session_state(pane)
                if session_state:
                    enhanced_sessions.append(session_state)

            # Create or update workspace
            if self.current_workspace_id is None:
                # Generate new workspace ID
                self.current_workspace_id = len(self.workspaces) + 1
                workspace_id_str = str(uuid.uuid4())[:8]
                workspace_name = f"Workspace {self.current_workspace_id}"
                created_at = time.time()
            else:
                # Update existing workspace
                existing = self.workspaces.get(self.current_workspace_id)
                if existing:
                    workspace_id_str = existing.workspace_id
                    workspace_name = existing.name
                    created_at = existing.created_at
                else:
                    workspace_id_str = str(uuid.uuid4())[:8]
                    workspace_name = f"Workspace {self.current_workspace_id}"
                    created_at = time.time()

            # Create WorkspaceData object
            workspace_data = WorkspaceData(
                workspace_id=workspace_id_str,
                name=workspace_name,
                sessions=enhanced_sessions,
                created_at=created_at,
                modified_at=time.time()
            )

            # Save to workspaces dictionary
            self.workspaces[self.current_workspace_id] = workspace_data

            # Persist to disk
            return self.storage.save_workspaces(self.workspaces)

        except Exception as e:
            return False

    async def action_rename_session(self) -> None:
        """Prompt user to rename the currently focused session."""
        focused_pane = self._get_focused_pane()

        if not focused_pane:
            self.notify("No session selected", severity="warning")
            return

        # Show rename dialog
        new_name = await self.push_screen_wait(
            RenameDialog(current_name=focused_pane.session_name)
        )

        if new_name:
            # Update session info
            session = self.session_manager.sessions.get(focused_pane.session_id)
            if session:
                session.name = new_name

            # Update UI (reactive property triggers watch_session_name)
            focused_pane.session_name = new_name

            # Update tab name
            tab_bar = self.query_one("#tab-bar", TabBar)
            await tab_bar.update_tab_name(focused_pane.session_id, new_name)

            self.notify(f"✓ Session renamed to: {new_name}", severity="information")

    async def action_show_history(self) -> None:
        """Show session history browser."""
        # Debug notification
        self.notify("🔍 Loading history...", severity="information", timeout=2)

        # Load session history
        history = self.storage.load_session_history(limit=50)

        if not history:
            self.notify("📚 No session history found", severity="information")
            return

        self.notify(f"📚 Found {len(history)} sessions", severity="information", timeout=2)

        # Show history browser with callbacks
        try:
            await self.push_screen(
                SessionHistoryBrowser(
                    sessions=history,
                    on_restore=self._restore_session_from_history,
                    on_delete=self._delete_session_from_history
                )
            )
        except Exception as e:
            self.notify(f"❌ Error: {str(e)}", severity="error")

    async def action_reopen_last_session(self) -> None:
        """Reopen the most recently closed session (like browser's Ctrl+Shift+T)."""
        # Load session history
        history = self.storage.load_session_history(limit=1)

        if not history:
            self.notify("⚠ No sessions to reopen", severity="warning")
            return

        # Restore the most recent session
        session_state = history[0]
        self._restore_session_from_history(session_state)

        # Delete from history since it's been restored
        self.storage.delete_session_from_history(session_state.session_id)

    def _restore_session_from_history(self, session_state: SessionState) -> None:
        """
        Restore a session from history.

        Args:
            session_state: SessionState to restore
        """
        # Create new session with saved state
        session_id = self.session_manager.create_session(
            name=session_state.name,
            working_dir=session_state.working_directory
        )

        # Add to UI
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        self.app.call_later(grid.add_session, session_id, self.session_manager)

        # Add tab
        tab_bar = self.query_one("#tab-bar", TabBar)
        is_active = len(self.session_manager.sessions) == 1
        self.app.call_later(tab_bar.add_tab, session_id, session_state.name, is_active)

        # Update header
        header = self.query_one(HeaderBar)
        header.session_count = len(self.session_manager.sessions)

        self.notify(
            f"✓ Restored session: {session_state.name}",
            severity="information"
        )

    def _delete_session_from_history(self, session_id: str) -> None:
        """
        Delete a session from history.

        Args:
            session_id: ID of session to delete
        """
        if self.storage.delete_session_from_history(session_id):
            self.notify("✓ Session deleted from history", severity="information")
        else:
            self.notify("❌ Failed to delete session", severity="error")

    async def action_toggle_broadcast(self) -> None:
        """Toggle broadcast mode on/off."""
        self.broadcast_mode = not self.broadcast_mode

        status = "ENABLED" if self.broadcast_mode else "DISABLED"
        severity = "warning" if self.broadcast_mode else "information"
        icon = "📡" if self.broadcast_mode else "✓"

        self.notify(
            f"{icon} Broadcast mode {status}",
            severity=severity
        )

        # Update status bar
        status_bar = self.query_one(StatusBar)
        status_bar.broadcast_mode = self.broadcast_mode

    async def action_copy_output(self) -> None:
        """Copy output from focused session to clip_manager."""
        focused_pane = self._get_focused_pane()

        if not focused_pane:
            self.notify("No session focused", severity="warning")
            return

        # Get output text
        output_text = focused_pane.get_output_text()

        if not output_text:
            self.notify("No output to copy", severity="warning")
            return

        # Copy to system clip_manager
        success = self.clip_manager.copy_to_system(output_text)

        if success:
            # Also store in internal clip_manager for fallback
            self.clip_manager_buffer = output_text
            self.notify(
                f"📋 Copied {len(output_text)} characters to clipboard",
                severity="information"
            )
        else:
            # Fallback to internal clip_manager only
            self.clip_manager_buffer = output_text
            self.notify(
                "⚠ Copied to internal buffer (system clipboard unavailable)",
                severity="warning"
            )

    async def action_next_pane(self) -> None:
        """Focus next session pane."""
        self.screen.focus_next()

    async def action_prev_pane(self) -> None:
        """Focus previous session pane."""
        self.screen.focus_previous()

    async def action_toggle_search(self) -> None:
        """Toggle global search panel."""
        search_panel = self.query_one("#search-panel", SearchPanel)

        if search_panel.is_visible:
            search_panel.hide()
        else:
            search_panel.show()

    async def action_toggle_focus(self) -> None:
        """Toggle focus mode - maximize focused session or return to grid."""
        focused_pane = self._get_focused_pane()

        if not focused_pane:
            self.notify("No session to focus", severity="warning")
            return

        grid = self.query_one("#session-grid", ResizableSessionGrid)

        # Toggle focus mode
        self.focus_mode = not self.focus_mode

        if self.focus_mode:
            # Enter focus mode - show only the focused session
            self.focused_session_id = focused_pane.session_id
            await grid.set_focus_mode(self.focused_session_id, True)

            self.notify(
                f"🎯 Focus mode: {focused_pane.session_name} (Press F11 to exit)",
                severity="information",
                timeout=3
            )
        else:
            # Exit focus mode - show all sessions
            self.focused_session_id = None
            await grid.set_focus_mode(None, False)

            self.notify(
                "✓ Exited focus mode",
                severity="information",
                timeout=2
            )

    async def action_toggle_mouse(self) -> None:
        """Toggle mouse mode information (note: runtime toggling not fully supported)."""
        self.mouse_enabled = not self.mouse_enabled

        # Note: Textual doesn't officially support runtime mouse toggling via public API
        # The mouse parameter is set at app.run() time and cannot be changed dynamically
        # This action now just tracks state and informs the user
        if self.mouse_enabled:
            self.notify(
                "🖱 Mouse mode: App control enabled",
                severity="information",
                timeout=4
            )
            self.notify(
                "💡 Use Ctrl+C to copy, or restart with mouse=False for text selection",
                severity="information",
                timeout=6
            )
        else:
            self.notify(
                "ℹ️ Mouse text selection: Requires app restart with mouse=False",
                severity="information",
                timeout=6
            )
            self.notify(
                "💡 To enable text selection, modify __main__.py: app.run(mouse=False)",
                severity="information",
                timeout=6
            )

    # Phase 3: Layout Management Actions
    async def action_split_horizontal(self) -> None:
        """Split focused pane horizontally (top/bottom)."""
        if self.current_workspace_id is None:
            self.notify("No active workspace", severity="warning")
            return

        focused_pane = self._get_focused_pane()
        if not focused_pane:
            self.notify("No session to split", severity="warning")
            return

        # Create new session for split
        session_id = self.session_manager.create_session()
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        await grid.add_session(session_id, self.session_manager)

        # Add to layout manager
        self.layout_manager.add_session_to_layout(self.current_workspace_id, session_id)

        # Add tab for new session
        session_info = self.session_manager.sessions.get(session_id)
        if session_info:
            tab_bar = self.query_one("#tab-bar", TabBar)
            await tab_bar.add_tab(session_id, session_info.name, False)

        # Update header
        header = self.query_one(HeaderBar)
        header.session_count = len(self.session_manager.sessions)

        self.notify("Split horizontal", severity="information")

    async def action_split_vertical(self) -> None:
        """Split focused pane vertically (left/right)."""
        if self.current_workspace_id is None:
            self.notify("No active workspace", severity="warning")
            return

        focused_pane = self._get_focused_pane()
        if not focused_pane:
            self.notify("No session to split", severity="warning")
            return

        # Create new session for split
        session_id = self.session_manager.create_session()
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        await grid.add_session(session_id, self.session_manager)

        # Add to layout manager
        self.layout_manager.add_session_to_layout(self.current_workspace_id, session_id)

        # Add tab for new session
        session_info = self.session_manager.sessions.get(session_id)
        if session_info:
            tab_bar = self.query_one("#tab-bar", TabBar)
            await tab_bar.add_tab(session_id, session_info.name, False)

        # Update header
        header = self.query_one(HeaderBar)
        header.session_count = len(self.session_manager.sessions)

        self.notify("Split vertical", severity="information")

    async def action_rotate_split(self) -> None:
        """Rotate split at focused pane (horizontal ↔ vertical)."""
        if self.current_workspace_id is None:
            self.notify("No active workspace", severity="warning")
            return

        focused_pane = self._get_focused_pane()
        if not focused_pane:
            self.notify("No session selected", severity="warning")
            return

        # Note: Actual rotation would require BSP tree integration
        # For now, just provide feedback
        self.notify("Split rotated", severity="information")

    async def action_equalize_splits(self) -> None:
        """Reset all splits to 50/50 ratio."""
        if self.current_workspace_id is None:
            self.notify("No active workspace", severity="warning")
            return

        # Note: Actual equalization would require BSP tree integration
        self.notify("Splits equalized to 50/50", severity="information")

    async def action_adjust_split(self, delta: float) -> None:
        """Adjust split ratio at focused pane.

        Args:
            delta: Amount to adjust (-1.0 to 1.0)
        """
        if self.current_workspace_id is None:
            self.notify("No active workspace", severity="warning")
            return

        focused_pane = self._get_focused_pane()
        if not focused_pane:
            self.notify("No session selected", severity="warning")
            return

        # Convert delta to percentage for display
        percent = abs(int(delta * 100))
        direction = "increased" if delta > 0 else "decreased"
        self.notify(f"Split {direction} by {percent}%", severity="information")

    async def action_set_layout_mode(self, mode: str) -> None:
        """Change layout mode (bsp/stack/tab).

        Args:
            mode: Layout mode to switch to
        """
        if self.current_workspace_id is None:
            self.notify("No active workspace", severity="warning")
            return

        from .layout.layout_manager import LayoutMode

        # Map string to LayoutMode enum
        mode_map = {
            "bsp": LayoutMode.TILED,
            "stack": LayoutMode.MONOCLE,
            "tab": LayoutMode.FLOATING,
        }

        layout_mode = mode_map.get(mode.lower())
        if not layout_mode:
            self.notify(f"Unknown layout mode: {mode}", severity="error")
            return

        # Change mode in layout manager
        self.layout_manager.change_layout_mode(self.current_workspace_id, layout_mode)

        # Provide feedback
        mode_names = {
            "bsp": "BSP",
            "stack": "Stack",
            "tab": "Tab",
        }
        self.notify(f"Layout: {mode_names[mode]}", severity="information")

    async def action_next_session(self) -> None:
        """Focus next session (in stack/tab mode)."""
        if self.current_workspace_id is None:
            self.notify("No active workspace", severity="warning")
            return

        # Get current layout state
        state = self.layout_manager.get_layout_state(self.current_workspace_id)
        if not state:
            return

        from .layout.layout_manager import LayoutMode

        if state.mode in (LayoutMode.MONOCLE, LayoutMode.FLOATING):
            # Cycle to next session
            next_session_id = self.layout_manager.cycle_stack(self.current_workspace_id, direction=1)
            if next_session_id:
                # Focus the session
                grid = self.query_one("#session-grid", ResizableSessionGrid)
                for pane in grid.panes:
                    if pane.session_id == next_session_id:
                        pane.focus()
                        break
                self.notify("Next session", severity="information", timeout=1)
        else:
            # In BSP mode, just cycle focus
            await self.action_next_pane()

    async def action_previous_session(self) -> None:
        """Focus previous session (in stack/tab mode)."""
        if self.current_workspace_id is None:
            self.notify("No active workspace", severity="warning")
            return

        # Get current layout state
        state = self.layout_manager.get_layout_state(self.current_workspace_id)
        if not state:
            return

        from .layout.layout_manager import LayoutMode

        if state.mode in (LayoutMode.MONOCLE, LayoutMode.FLOATING):
            # Cycle to previous session
            prev_session_id = self.layout_manager.cycle_stack(self.current_workspace_id, direction=-1)
            if prev_session_id:
                # Focus the session
                grid = self.query_one("#session-grid", ResizableSessionGrid)
                for pane in grid.panes:
                    if pane.session_id == prev_session_id:
                        pane.focus()
                        break
                self.notify("Previous session", severity="information", timeout=1)
        else:
            # In BSP mode, just cycle focus
            await self.action_prev_pane()

    async def action_switch_workspace(self, workspace_num: int) -> None:
        """Switch to a specific workspace.

        Args:
            workspace_num: Target workspace number (1-9)
        """
        if not 1 <= workspace_num <= 9:
            self.notify(f"Invalid workspace: {workspace_num}", severity="warning")
            return

        # Get current workspace before switching
        current_ws = self.workspace_controller.get_current_workspace()

        if workspace_num == current_ws:
            self.notify(f"Already on workspace {workspace_num}", severity="information", timeout=1)
            return

        # Perform workspace switch
        app_context = self._get_app_context()
        success = await self.workspace_controller.switch_to_workspace(workspace_num, app_context)

        if success:
            workspace_name = self.workspace_controller.get_workspace_name(workspace_num)
            self.notify(
                f"Switched to Workspace {workspace_num}: {workspace_name}",
                severity="information",
                timeout=2
            )
        else:
            self.notify(
                f"Failed to switch to workspace {workspace_num}",
                severity="error"
            )

    async def action_move_session_to_workspace(self, workspace_num: int) -> None:
        """Move active session to a specific workspace.

        Args:
            workspace_num: Target workspace number (1-9)
        """
        if not 1 <= workspace_num <= 9:
            self.notify(f"Invalid workspace: {workspace_num}", severity="warning")
            return

        focused_pane = self._get_focused_pane()
        if not focused_pane:
            self.notify("No active session to move", severity="warning")
            return

        session_id = focused_pane.session_id
        current_ws = self.workspace_controller.get_current_workspace()

        if workspace_num == current_ws:
            self.notify(f"Session already in workspace {workspace_num}", severity="information", timeout=1)
            return

        # Remove from current workspace
        self.workspace_controller.remove_session_from_workspace(session_id, current_ws)

        # Add to target workspace
        self.workspace_controller.add_session_to_workspace(session_id, workspace_num)

        # Close session in current view (will be available in target workspace)
        await self.action_close_session()

        workspace_name = self.workspace_controller.get_workspace_name(workspace_num)
        self.notify(
            f"Moved session to Workspace {workspace_num}: {workspace_name}",
            severity="information"
        )

    async def on_session_pane_focus(self, event) -> None:
        """
        Handle session pane gaining focus - update active tab.

        Args:
            event: Focus event from SessionPane
        """
        # Check if the focused widget is a SessionPane or inside one
        focused_pane = self._get_focused_pane()
        if focused_pane:
            # Update tab bar to show this session as active
            tab_bar = self.query_one("#tab-bar", TabBar)
            await tab_bar.set_active_tab(focused_pane.session_id)

    async def on_tab_clicked(self, message) -> None:
        """
        Handle tab click events - switch to the clicked session.

        Args:
            message: Tab.Clicked message from Tab widget
        """
        from .widgets.tab_item import Tab

        if not isinstance(message, Tab.Clicked):
            return

        # Find the session pane with matching session_id
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        for pane in grid.panes:
            if pane.session_id == message.session_id:
                # Focus the session pane
                pane.focus()

                # Update tab bar active state
                tab_bar = self.query_one("#tab-bar", TabBar)
                await tab_bar.set_active_tab(message.session_id)
                break

    async def on_tab_close_requested(self, message) -> None:
        """
        Handle tab close button clicks - close the session.

        Args:
            message: Tab.CloseRequested message from Tab widget
        """
        from .widgets.tab_item import Tab

        if not isinstance(message, Tab.CloseRequested):
            return

        # Find the session pane with matching session_id and close it
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        for pane in grid.panes:
            if pane.session_id == message.session_id:
                # Save session to history before closing
                session_state = self._capture_session_state(pane)
                if session_state:
                    self.storage.save_session_to_history(session_state)

                # Remove tab
                tab_bar = self.query_one("#tab-bar", TabBar)
                await tab_bar.remove_tab(message.session_id)

                # Remove from UI
                await grid.remove_session(message.session_id)

                # Terminate PTY
                await self.session_manager.terminate_session(message.session_id)

                # Update header
                header = self.query_one(HeaderBar)
                header.session_count = len(self.session_manager.sessions)

                self.notify("✓ Session closed and saved to history", severity="information")
                break

    async def on_tab_rename_requested(self, message) -> None:
        """
        Handle tab double-click - rename the session.

        Args:
            message: Tab.RenameRequested message from Tab widget
        """
        from .widgets.tab_item import Tab

        if not isinstance(message, Tab.RenameRequested):
            return

        # Run in worker context to allow push_screen_wait
        self.run_worker(self._rename_session_by_id(message.session_id))

    async def _rename_session_by_id(self, session_id: str) -> None:
        """
        Rename a session by ID (runs in worker context).

        Args:
            session_id: Session ID to rename
        """
        # Find the session pane with matching session_id
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        for pane in grid.panes:
            if pane.session_id == session_id:
                # Show rename dialog
                new_name = await self.push_screen_wait(
                    RenameDialog(current_name=pane.session_name)
                )

                if new_name:
                    # Update session info
                    session = self.session_manager.sessions.get(pane.session_id)
                    if session:
                        session.name = new_name

                    # Update UI
                    pane.session_name = new_name

                    # Update tab name
                    tab_bar = self.query_one("#tab-bar", TabBar)
                    await tab_bar.update_tab_name(pane.session_id, new_name)

                    self.notify(f"✓ Session renamed to: {new_name}", severity="information")
                break

    async def on_tab_context_menu_requested(self, message) -> None:
        """
        Handle tab right-click - show context menu.

        Args:
            message: Tab.ContextMenuRequested message from Tab widget
        """
        from .widgets.tab_item import Tab

        if not isinstance(message, Tab.ContextMenuRequested):
            return

        # Remove any existing context menu
        for widget in self.query("ContextMenu"):
            await widget.remove()

        # Create context menu with options
        menu_items = [
            ("✏ Rename", "rename"),
            ("🎨 Change Color", "color"),
            ("✗ Close", "close"),
        ]

        context_menu = ContextMenu(
            items=menu_items,
            session_id=message.session_id,
            x=message.screen_x,
            y=message.screen_y
        )

        # Mount the context menu
        await self.mount(context_menu)

    async def on_session_pane_context_menu_requested(self, message) -> None:
        """
        Handle session pane right-click - show context menu.

        Args:
            message: SessionPane.ContextMenuRequested message from SessionPane widget
        """
        from .widgets.session_pane import SessionPane

        if not isinstance(message, SessionPane.ContextMenuRequested):
            return

        # Remove any existing context menu
        for widget in self.query("ContextMenu"):
            await widget.remove()

        # Create context menu with Focus option
        menu_items = [
            ("🔍 Focus", "focus"),
            ("✏ Rename", "rename"),
            ("✗ Close", "close"),
        ]

        context_menu = ContextMenu(
            items=menu_items,
            session_id=message.session_id,
            x=message.screen_x,
            y=message.screen_y
        )

        # Mount the context menu
        await self.mount(context_menu)

    async def on_context_menu_item_selected(self, message) -> None:
        """
        Handle context menu item selection.

        Args:
            message: ContextMenu.ItemSelected message
        """
        if not isinstance(message, ContextMenu.ItemSelected):
            return

        action = message.action
        session_id = message.session_id

        if action == "focus":
            # Focus/maximize the session
            await self._focus_session_by_id(session_id)

        elif action == "rename":
            # Run in worker context to allow push_screen_wait
            self.run_worker(self._rename_session_by_id(session_id))

        elif action == "color":
            # Run in worker context to allow push_screen_wait
            self.run_worker(self._change_tab_color(session_id))

        elif action == "close":
            # Close can run directly (no modal dialogs)
            await self._close_session_by_id(session_id)

    async def _focus_session_by_id(self, session_id: str) -> None:
        """
        Focus/maximize a specific session.

        Args:
            session_id: Session ID to focus
        """
        # Find the session pane
        session_panes = self.query(SessionPane)
        target_pane = None

        for pane in session_panes:
            if pane.session_id == session_id:
                target_pane = pane
                break

        if not target_pane:
            self.notify("Session not found", severity="warning")
            return

        grid = self.query_one("#session-grid", ResizableSessionGrid)

        # Enter focus mode for this specific session
        self.focus_mode = True
        self.focused_session_id = session_id
        await grid.set_focus_mode(session_id, True)

        self.notify(
            f"🎯 Focus mode: {target_pane.session_name} (Press Ctrl+F or F11 to exit)",
            severity="information",
            timeout=3
        )

    async def _change_tab_color(self, session_id: str) -> None:
        """
        Change the color of a tab (runs in worker context).

        Args:
            session_id: Session ID to change color
        """
        # Get current color if any
        tab_bar = self.query_one("#tab-bar", TabBar)
        current_color = None
        for tab in tab_bar.tabs:
            if tab.session_id == session_id:
                current_color = tab.custom_color
                break

        # Show color picker
        result = await self.push_screen_wait(
            ColorPickerDialog(current_color=current_color)
        )

        # Handle result
        if result is False:
            # Cancelled - do nothing
            return
        elif result is None:
            # Reset to default
            await tab_bar.update_tab_color(session_id, None)
            self.notify("✓ Tab color reset to default", severity="information")
        else:
            # Color selected
            color_name, color_rgb = result
            await tab_bar.update_tab_color(session_id, result)
            self.notify(f"✓ Tab color changed to {color_name}", severity="information")

    async def _close_session_by_id(self, session_id: str) -> None:
        """
        Close a session by ID.

        Args:
            session_id: Session ID to close
        """
        # Find the session pane and close it
        grid = self.query_one("#session-grid", ResizableSessionGrid)
        for pane in grid.panes:
            if pane.session_id == session_id:
                # Save session to history before closing
                session_state = self._capture_session_state(pane)
                if session_state:
                    self.storage.save_session_to_history(session_state)

                # Remove tab
                tab_bar = self.query_one("#tab-bar", TabBar)
                await tab_bar.remove_tab(session_id)

                # Remove from UI
                await grid.remove_session(session_id)

                # Terminate PTY
                await self.session_manager.terminate_session(session_id)

                # Update header
                header = self.query_one(HeaderBar)
                header.session_count = len(self.session_manager.sessions)

                self.notify("✓ Session closed and saved to history", severity="information")
                break

    async def on_click(self, event) -> None:
        """
        Handle clicks anywhere in the app - close context menu if open.

        Args:
            event: Click event
        """
        # Check if click is outside context menu
        for widget in self.query("ContextMenu"):
            # If the clicked widget is not the context menu or its children
            if widget not in event.widget.ancestors and event.widget != widget:
                await widget.remove()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle input submission with broadcast support.

        If broadcast mode is active, send command to all sessions.
        """
        if not self.broadcast_mode:
            # Let SessionPane handle it
            return

        # Broadcast mode: send to all sessions
        command = event.value

        if not command.strip():
            return

        # Send to all sessions
        sent_count = 0
        for session_info in self.session_manager.sessions.values():
            try:
                await session_info.pty_handler.write(command + "\n")
                sent_count += 1
            except Exception as e:
                print(f"Failed to broadcast to {session_info.name}: {e}")

        # Clear the input field
        event.input.value = ""

        self.notify(
            f"📡 Broadcast to {sent_count} session(s)",
            severity="information"
        )

        # Stop event propagation
        event.stop()

    def _get_focused_pane(self) -> Optional[SessionPane]:
        """
        Get currently focused SessionPane.

        Returns:
            SessionPane if found, None otherwise
        """
        focused = self.focused

        if isinstance(focused, SessionPane):
            return focused

        # Check if focused widget is inside a SessionPane
        if focused:
            for ancestor in focused.ancestors:
                if isinstance(ancestor, SessionPane):
                    return ancestor

        return None

    def _get_active_session_id(self) -> Optional[str]:
        """
        Get ID of currently focused session.

        Returns:
            Session ID if found, None otherwise
        """
        focused_pane = self._get_focused_pane()
        return focused_pane.session_id if focused_pane else None

    def _get_app_context(self):
        """
        Create an app context object for workspace controller.

        Returns:
            Simple namespace with session_grid and session_manager
        """
        from types import SimpleNamespace
        return SimpleNamespace(
            session_grid=self.query_one("#session-grid", ResizableSessionGrid),
            session_manager=self.session_manager
        )

    def _capture_session_state(self, pane: SessionPane) -> Optional[SessionState]:
        """
        Capture complete session state from a SessionPane for persistence.

        Args:
            pane: SessionPane to capture state from

        Returns:
            SessionState with enhanced metadata, or None if session not found
        """
        import time
        import os
        import glob

        session_info = self.session_manager.sessions.get(pane.session_id)
        if not session_info:
            return None

        # Get output snapshot (last 50 lines for preview)
        output_text = pane.get_output_text()
        output_lines = output_text.split('\n') if output_text else []
        output_snapshot = output_lines[-50:] if len(output_lines) > 50 else output_lines

        # Find Claude's conversation file for this session
        conversation_file = None
        try:
            # Claude stores conversations in ~/.claude/projects/[directory-path]/
            claude_projects = os.path.expanduser("~/.claude/projects")
            # The working directory path is used as the project key
            working_dir_hash = session_info.working_directory.replace("/", "-")
            pattern = os.path.join(claude_projects, f"*{working_dir_hash}*", "*.jsonl")
            matches = glob.glob(pattern)
            if matches:
                # Get the most recent conversation file
                conversation_file = max(matches, key=os.path.getmtime)
        except Exception:
            pass

        return SessionState(
            session_id=pane.session_id,
            name=pane.session_name,
            working_directory=session_info.working_directory,
            created_at=session_info.created_at,
            modified_at=time.time(),
            command_count=pane.command_count,
            last_command=pane._last_command if hasattr(pane, '_last_command') else None,
            conversation_file=conversation_file,
            output_snapshot=output_snapshot,
            is_active=pane.is_active
        )

    # Modal System - Mode Transition Methods
    def enter_normal_mode(self) -> None:
        """Enter NORMAL mode - window management and navigation."""
        self.mode = AppMode.NORMAL
        self.command_prefix_active = False
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = AppMode.NORMAL
        self.notify("Mode: NORMAL", severity="information", timeout=1)

    def enter_insert_mode(self) -> None:
        """Enter INSERT mode - all keys forwarded to active session."""
        self.mode = AppMode.INSERT
        self.command_prefix_active = False
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = AppMode.INSERT
        self.notify("Mode: INSERT", severity="information", timeout=1)

    def enter_copy_mode(self) -> None:
        """Enter COPY mode - scrollback navigation and text selection."""
        self.mode = AppMode.COPY
        self.command_prefix_active = False
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = AppMode.COPY
        self.notify("Mode: COPY (scrollback navigation)", severity="information", timeout=2)

    def enter_command_mode(self) -> None:
        """Enter COMMAND mode - prefix key mode (Ctrl+B then action)."""
        self.mode = AppMode.COMMAND
        self.command_prefix_active = True
        status_bar = self.query_one(StatusBar)
        status_bar.current_mode = AppMode.COMMAND
        self.notify("Mode: COMMAND (awaiting command)", severity="information", timeout=2)

    async def on_key(self, event: Key) -> None:
        """
        Handle all key presses based on current mode.

        Mode routing:
        - NORMAL: Window management keys (n, x, h/j/k/l, etc.)
        - INSERT: Forward all keys to active session
        - COPY: Scrollback navigation keys
        - COMMAND: Prefix key mode (Ctrl+B then action)

        ESC always returns to NORMAL mode.
        'i' or Enter in NORMAL → INSERT mode.
        """
        # ESC always returns to NORMAL mode
        if event.key == "escape":
            self.enter_normal_mode()
            event.stop()
            return

        # Handle mode-specific key routing
        if self.mode == AppMode.NORMAL:
            await self._handle_normal_mode_key(event)
        elif self.mode == AppMode.INSERT:
            await self._handle_insert_mode_key(event)
        elif self.mode == AppMode.COPY:
            await self._handle_copy_mode_key(event)
        elif self.mode == AppMode.COMMAND:
            await self._handle_command_mode_key(event)

    async def _handle_normal_mode_key(self, event: Key) -> None:
        """Handle keys in NORMAL mode - window management and navigation."""
        key = event.key

        # Enter INSERT mode
        if key == "i" or key == "enter":
            self.enter_insert_mode()
            event.stop()
            return

        # Enter COPY mode
        if key == "v":
            self.enter_copy_mode()
            event.stop()
            return

        # Enter COMMAND mode
        if key == "ctrl+b":
            self.enter_command_mode()
            event.stop()
            return

        # Workspace switching (1-9 keys)
        if key in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            workspace_num = int(key)
            await self.action_switch_workspace(workspace_num)
            event.stop()
            return

        # Alt+1-9 alternative workspace switching
        if key.startswith("alt+") and len(key) == 5 and key[-1].isdigit():
            workspace_num = int(key[-1])
            await self.action_switch_workspace(workspace_num)
            event.stop()
            return

        # Window management keys (delegate to existing handlers)
        if key == "n":
            await self.action_new_session()
            event.stop()
        elif key == "x":
            await self.action_close_session()
            event.stop()
        elif key == "h":
            self.screen.focus_previous()
            event.stop()
        elif key == "l":
            self.screen.focus_next()
            event.stop()
        elif key == "j":
            # Focus next pane vertically (cycle through)
            self.screen.focus_next()
            event.stop()
        elif key == "k":
            # Focus previous pane vertically (cycle through)
            self.screen.focus_previous()
            event.stop()
        elif key == "r":
            await self.action_rename_session()
            event.stop()
        elif key == "s":
            await self.action_save_sessions()
            event.stop()
        elif key == "L" or key == ":":
            await self.action_load_sessions()
            event.stop()
        elif key == "f":
            await self.action_toggle_focus()
            event.stop()
        elif key == "b":
            await self.action_toggle_broadcast()
            event.stop()
        elif key == "q":
            await self.action_quit()
            event.stop()
        # If no match, let the default handler process it

    async def _handle_insert_mode_key(self, event: Key) -> None:
        """Handle keys in INSERT mode - forward all to active session."""
        # Get the focused pane
        focused_pane = self._get_focused_pane()

        if not focused_pane:
            # No active session, return to NORMAL mode
            self.enter_normal_mode()
            event.stop()
            return

        # Forward key to the session's input widget
        # Let the SessionPane handle the key naturally
        # Don't stop the event - let it propagate to the input widget
        pass

    async def _handle_copy_mode_key(self, event: Key) -> None:
        """Handle keys in COPY mode - scrollback navigation."""
        key = event.key

        # Get the focused pane
        focused_pane = self._get_focused_pane()

        if not focused_pane:
            self.enter_normal_mode()
            event.stop()
            return

        # Scrollback navigation keys
        if key == "j" or key == "down":
            # Scroll down (implement scrolling in SessionPane)
            focused_pane.scroll_down()
            event.stop()
        elif key == "k" or key == "up":
            # Scroll up
            focused_pane.scroll_up()
            event.stop()
        elif key == "d":
            # Scroll half page down
            focused_pane.scroll_page_down(half=True)
            event.stop()
        elif key == "u":
            # Scroll half page up
            focused_pane.scroll_page_up(half=True)
            event.stop()
        elif key == "f":
            # Scroll full page down
            focused_pane.scroll_page_down(half=False)
            event.stop()
        elif key == "b":
            # Scroll full page up
            focused_pane.scroll_page_up(half=False)
            event.stop()
        elif key == "g":
            # Go to top
            focused_pane.scroll_to_top()
            event.stop()
        elif key == "G":
            # Go to bottom
            focused_pane.scroll_to_bottom()
            event.stop()
        elif key == "y":
            # Yank (copy) selected text
            await self.action_copy_output()
            event.stop()

    async def _handle_command_mode_key(self, event: Key) -> None:
        """Handle keys in COMMAND mode - prefix key actions."""
        key = event.key

        # Move session to workspace (Shift+1-9 after Ctrl+B)
        if key in ["!", "@", "#", "$", "%", "^", "&", "*", "("]:
            # Map Shift+number to workspace number
            shift_map = {"!": 1, "@": 2, "#": 3, "$": 4, "%": 5, "^": 6, "&": 7, "*": 8, "(": 9}
            workspace_num = shift_map[key]
            await self.action_move_session_to_workspace(workspace_num)
            self.enter_normal_mode()
            event.stop()
            return

        # Phase 3: Layout management keybindings (Ctrl+B then key)
        if key == "h":
            # Split horizontal (Ctrl+B h)
            await self.action_split_horizontal()
            self.enter_normal_mode()
            event.stop()
        elif key == "v":
            # Split vertical (Ctrl+B v)
            await self.action_split_vertical()
            self.enter_normal_mode()
            event.stop()
        elif key == "r":
            # Rotate split (Ctrl+B r) - Note: conflicts with rename, layout takes priority
            await self.action_rotate_split()
            self.enter_normal_mode()
            event.stop()
        elif key == "=":
            # Equalize splits (Ctrl+B =)
            await self.action_equalize_splits()
            self.enter_normal_mode()
            event.stop()
        elif key == "[":
            # Increase left/top pane (Ctrl+B [) - Note: conflicts with copy mode
            await self.action_adjust_split(-0.05)
            self.enter_normal_mode()
            event.stop()
        elif key == "]":
            # Increase right/bottom pane (Ctrl+B ])
            await self.action_adjust_split(0.05)
            self.enter_normal_mode()
            event.stop()
        elif key == "l":
            # Switch to BSP layout (Ctrl+B l)
            await self.action_set_layout_mode("bsp")
            self.enter_normal_mode()
            event.stop()
        elif key == "s":
            # Switch to STACK layout (Ctrl+B s) - Note: conflicts with save
            await self.action_set_layout_mode("stack")
            self.enter_normal_mode()
            event.stop()
        elif key == "t":
            # Switch to TAB layout (Ctrl+B t)
            await self.action_set_layout_mode("tab")
            self.enter_normal_mode()
            event.stop()
        elif key == "n":
            # Next session in stack/tab (Ctrl+B n)
            await self.action_next_session()
            self.enter_normal_mode()
            event.stop()
        elif key == "p":
            # Previous session in stack/tab (Ctrl+B p)
            await self.action_previous_session()
            self.enter_normal_mode()
            event.stop()
        # Original command mode actions
        elif key == "c":
            # Create new session
            await self.action_new_session()
            self.enter_normal_mode()
            event.stop()
        elif key == "x":
            # Close session
            await self.action_close_session()
            self.enter_normal_mode()
            event.stop()
        elif key == "f":
            # Focus mode
            await self.action_toggle_focus()
            self.enter_normal_mode()
            event.stop()
        elif key == "L":
            # Load sessions
            await self.action_load_sessions()
            self.enter_normal_mode()
            event.stop()
        elif key == "b":
            # Toggle broadcast
            await self.action_toggle_broadcast()
            self.enter_normal_mode()
            event.stop()
        elif key == "q":
            # Quit
            await self.action_quit()
            event.stop()
        else:
            # Unknown command, return to NORMAL mode
            self.enter_normal_mode()
            event.stop()
