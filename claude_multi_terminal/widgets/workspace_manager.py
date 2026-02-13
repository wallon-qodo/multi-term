"""Workspace manager dialog for saving and loading workspaces."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static, ListView, ListItem
from textual.binding import Binding
from pathlib import Path
import json
from datetime import datetime


class WorkspaceListItem(ListItem):
    """A workspace list item."""

    def __init__(self, workspace_data: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_data = workspace_data


class WorkspaceManager(ModalScreen):
    """Modal screen for managing workspaces."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("ctrl+s", "save_current", "Save Current"),
        Binding("enter", "load_selected", "Load Selected"),
        Binding("delete", "delete_selected", "Delete"),
    ]

    CSS = """
    WorkspaceManager {
        align: center middle;
    }

    #workspace-dialog {
        width: 80;
        height: 30;
        background: rgb(32,32,32);
        border: solid rgb(100,180,240);
        padding: 1 2;
    }

    #workspace-title {
        text-align: center;
        color: rgb(100,180,240);
        text-style: bold;
        margin-bottom: 1;
    }

    #workspace-list {
        height: 1fr;
        border: solid rgb(60,60,60);
        margin: 1 0;
    }

    #workspace-info {
        height: 5;
        border: solid rgb(60,60,60);
        padding: 1;
        margin: 1 0;
    }

    #button-container {
        height: auto;
        align-horizontal: center;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, storage_dir: Path, current_sessions: list):
        super().__init__()
        self.storage_dir = storage_dir
        self.current_sessions = current_sessions
        self.workspaces = []
        self.selected_workspace = None

    def compose(self) -> ComposeResult:
        """Compose the workspace manager UI."""
        with Container(id="workspace-dialog"):
            yield Label("💾 Workspace Manager", id="workspace-title")

            # Workspace list
            yield ListView(id="workspace-list")

            # Info panel
            with Container(id="workspace-info"):
                yield Label("Select a workspace to see details", id="info-text")

            # Action buttons
            with Horizontal(id="button-container"):
                yield Button("💾 Save Current", id="save-btn", variant="primary")
                yield Button("📂 Load Selected", id="load-btn", variant="success")
                yield Button("🗑️  Delete", id="delete-btn", variant="error")
                yield Button("✖ Close", id="close-btn")

    async def on_mount(self) -> None:
        """Load and display available workspaces."""
        await self.load_workspaces()

    async def load_workspaces(self) -> None:
        """Load all saved workspaces."""
        workspace_file = self.storage_dir / "workspace_state.json"

        self.workspaces = []

        # Load current workspace
        if workspace_file.exists():
            try:
                with open(workspace_file, 'r') as f:
                    data = json.load(f)
                    self.workspaces.append({
                        'name': 'Current Workspace',
                        'file': 'workspace_state.json',
                        'sessions': data.get('sessions', []),
                        'modified': workspace_file.stat().st_mtime
                    })
            except:
                pass

        # Load saved workspace snapshots
        snapshots_dir = self.storage_dir / "workspaces"
        if snapshots_dir.exists():
            for snapshot_file in sorted(snapshots_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
                try:
                    with open(snapshot_file, 'r') as f:
                        data = json.load(f)
                        self.workspaces.append({
                            'name': snapshot_file.stem,
                            'file': str(snapshot_file),
                            'sessions': data.get('sessions', []),
                            'modified': snapshot_file.stat().st_mtime
                        })
                except:
                    pass

        # Populate list
        list_view = self.query_one("#workspace-list", ListView)
        await list_view.clear()

        for workspace in self.workspaces:
            modified_time = datetime.fromtimestamp(workspace['modified']).strftime('%Y-%m-%d %H:%M')
            session_count = len(workspace['sessions'])

            label_text = f"📁 {workspace['name']}\n   {session_count} sessions · Modified: {modified_time}"

            item = WorkspaceListItem(workspace)
            item.add_class("workspace-item")
            await list_view.append(Static(label_text))

        if not self.workspaces:
            await list_view.append(Static("No workspaces found"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle workspace selection."""
        if event.item.index < len(self.workspaces):
            self.selected_workspace = self.workspaces[event.item.index]
            self.update_info_panel()

    def update_info_panel(self) -> None:
        """Update the info panel with selected workspace details."""
        if not self.selected_workspace:
            return

        info_text = self.query_one("#info-text", Label)

        workspace = self.selected_workspace
        modified = datetime.fromtimestamp(workspace['modified']).strftime('%Y-%m-%d %H:%M:%S')

        session_names = [s['name'] for s in workspace['sessions'][:5]]
        if len(workspace['sessions']) > 5:
            session_names.append(f"... and {len(workspace['sessions']) - 5} more")

        details = [
            f"Name: {workspace['name']}",
            f"Sessions: {len(workspace['sessions'])}",
            f"Modified: {modified}",
            f"Sessions: {', '.join(session_names) if session_names else 'None'}"
        ]

        info_text.update("\n".join(details))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            await self.action_save_current()
        elif event.button.id == "load-btn":
            await self.action_load_selected()
        elif event.button.id == "delete-btn":
            await self.action_delete_selected()
        elif event.button.id == "close-btn":
            self.dismiss(None)

    async def action_save_current(self) -> None:
        """Save current workspace as a new snapshot."""
        snapshots_dir = self.storage_dir / "workspaces"
        snapshots_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        snapshot_name = f"workspace-{timestamp}"
        snapshot_file = snapshots_dir / f"{snapshot_name}.json"

        # Create workspace data from current sessions
        workspace_data = {
            'version': '1.0',
            'sessions': self.current_sessions,
            'saved_at': timestamp
        }

        try:
            with open(snapshot_file, 'w') as f:
                json.dump(workspace_data, f, indent=2)

            await self.load_workspaces()  # Refresh list
            self.app.notify(f"✓ Workspace saved: {snapshot_name}", severity="information")
        except Exception as e:
            self.app.notify(f"❌ Failed to save: {e}", severity="error")

    async def action_load_selected(self) -> None:
        """Load the selected workspace."""
        if not self.selected_workspace:
            self.app.notify("⚠ No workspace selected", severity="warning")
            return

        self.dismiss(self.selected_workspace)

    async def action_delete_selected(self) -> None:
        """Delete the selected workspace snapshot."""
        if not self.selected_workspace:
            self.app.notify("⚠ No workspace selected", severity="warning")
            return

        if self.selected_workspace['name'] == 'Current Workspace':
            self.app.notify("⚠ Cannot delete current workspace", severity="warning")
            return

        try:
            Path(self.selected_workspace['file']).unlink()
            await self.load_workspaces()  # Refresh list
            self.selected_workspace = None
            self.app.notify("✓ Workspace deleted", severity="information")
        except Exception as e:
            self.app.notify(f"❌ Failed to delete: {e}", severity="error")
