"""Resizable grid layout with mouse-draggable dividers."""

from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.reactive import reactive
from textual import events
from textual.app import ComposeResult
from rich.text import Text
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from ..core.session_manager import SessionManager

from .session_pane import SessionPane


class Splitter(Widget):
    """Interactive divider between panes that can be dragged to resize."""

    DEFAULT_CSS = """
    Splitter {
        width: 1;
        background: rgb(60,60,60);
    }

    Splitter:hover {
        background: rgb(255,77,77);
    }

    Splitter.vertical {
        width: 1;
        height: 1fr;
    }

    Splitter.horizontal {
        width: 1fr;
        height: 1;
    }

    Splitter.dragging {
        background: rgb(255,100,100);
    }
    """

    def __init__(self, orientation: str = "vertical", **kwargs):
        """
        Initialize splitter.

        Args:
            orientation: "vertical" (divides left/right) or "horizontal" (divides top/bottom)
        """
        super().__init__(**kwargs)
        self.orientation = orientation
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.add_class(orientation)

    def render(self) -> str:
        """Render the splitter with appropriate character."""
        if self.orientation == "vertical":
            return "┃"
        else:
            return "━"

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Start drag operation."""
        if event.button == 1:  # Left click
            self.is_dragging = True
            # Store starting screen coordinates for delta calculation
            self.drag_start_x = event.screen_x
            self.drag_start_y = event.screen_y
            # Store last position for incremental updates
            self.last_x = event.screen_x
            self.last_y = event.screen_y
            self.add_class("dragging")
            self.capture_mouse()
            event.stop()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """End drag operation."""
        if self.is_dragging:
            self.is_dragging = False
            self.remove_class("dragging")
            self.release_mouse()
            event.stop()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Handle drag movement."""
        if self.is_dragging:
            # Calculate incremental delta from last position for smooth dragging
            if self.orientation == "vertical":
                delta = event.screen_x - self.last_x
                self.last_x = event.screen_x
            else:
                delta = event.screen_y - self.last_y
                self.last_y = event.screen_y

            # Only notify if there's actual movement
            if delta != 0:
                # Notify parent container about resize request
                self.post_message(
                    SplitterDragged(
                        splitter=self,
                        delta=delta
                    )
                )
            event.stop()


class SplitterDragged(events.Message):
    """Message sent when a splitter is dragged."""

    def __init__(self, splitter: Splitter, delta: int):
        super().__init__()
        self.splitter = splitter
        self.delta = delta


class ResizablePane(Container):
    """Container wrapper that can be resized."""

    DEFAULT_CSS = """
    ResizablePane {
        height: auto;
        width: auto;
        min-width: 30;
        min-height: 10;
    }
    """

    def __init__(self, content: Widget, **kwargs):
        """
        Initialize resizable pane.

        Args:
            content: Widget to wrap (SessionPane)
        """
        super().__init__(**kwargs)
        self.content = content

    def compose(self) -> ComposeResult:
        """Compose the pane with its content."""
        yield self.content


class ResizableSessionGrid(Container):
    """
    Container managing resizable session panes with draggable dividers.

    Replaces the fixed Grid layout with a flexible container system
    that allows users to resize panes by dragging dividers.
    """

    DEFAULT_CSS = """
    ResizableSessionGrid {
        height: 1fr;
        width: 1fr;
        padding: 1 2;
    }
    """

    pane_count = reactive(0)

    def __init__(self, *args, **kwargs):
        """Initialize resizable grid."""
        super().__init__(*args, **kwargs)
        self.panes = []  # List of SessionPane instances
        self.containers = []  # List of ResizablePane wrappers
        self.focus_mode_enabled = False
        self.focused_session_id = None
        self.original_panes = []  # Store original panes for restoring

    async def add_session(self, session_id: str, session_manager: "SessionManager") -> None:
        """
        Add a new session pane to the grid.

        Args:
            session_id: UUID of the session
            session_manager: Reference to SessionManager
        """
        session_info = session_manager.sessions.get(session_id)

        if not session_info:
            return

        pane = SessionPane(
            session_id=session_id,
            session_name=session_info.name,
            session_manager=session_manager
        )

        self.panes.append(pane)
        self.pane_count = len(self.panes)

        # Rebuild entire layout
        await self._rebuild_layout()

    async def remove_session(self, session_id: str) -> None:
        """
        Remove a session pane from the grid.

        Args:
            session_id: UUID of the session to remove
        """
        for pane in self.panes:
            if pane.session_id == session_id:
                self.panes.remove(pane)
                self.pane_count = len(self.panes)
                break

        # Rebuild layout
        await self._rebuild_layout()

    async def clear(self) -> None:
        """Remove all session panes."""
        self.panes.clear()
        self.pane_count = 0
        await self._rebuild_layout()

    async def set_focus_mode(self, session_id: Optional[str], enabled: bool) -> None:
        """
        Enable or disable focus mode for a specific session.

        In focus mode, only the focused session is displayed full-screen.
        All other sessions are hidden but remain active.

        Args:
            session_id: ID of session to focus (None if disabling focus mode)
            enabled: True to enable focus mode, False to disable
        """
        self.focus_mode_enabled = enabled
        self.focused_session_id = session_id

        if enabled and session_id:
            # Store original panes list
            self.original_panes = self.panes.copy()

            # Find the focused pane
            focused_pane = None
            for pane in self.panes:
                if pane.session_id == session_id:
                    focused_pane = pane
                    break

            if focused_pane:
                # Temporarily show only the focused pane
                self.panes = [focused_pane]
                self.pane_count = 1
                await self._rebuild_layout()

                # Add visual indicator to focused pane
                focused_pane.add_class("focused-mode")
        else:
            # Restore all panes
            if self.original_panes:
                self.panes = self.original_panes
                self.original_panes = []
                self.pane_count = len(self.panes)
                await self._rebuild_layout()

                # Remove focus mode class from all panes
                for pane in self.panes:
                    pane.remove_class("focused-mode")

    async def _rebuild_layout(self) -> None:
        """
        Rebuild the entire layout based on current pane count.

        Layouts:
        - 1 pane: Full screen
        - 2 panes: Side-by-side (50/50)
        - 3 panes: 2 on top, 1 on bottom
        - 4 panes: 2x2 grid
        - 5+ panes: Dynamic rows with 2 columns
        """
        # Remove all children
        await self.query("*").remove()
        self.containers.clear()

        if self.pane_count == 0:
            return

        if self.pane_count == 1:
            # Single pane - full screen
            container = ResizablePane(self.panes[0])
            self.containers.append(container)
            await self.mount(container)

        elif self.pane_count == 2:
            # Two panes - side by side with splitter
            left = ResizablePane(self.panes[0])
            left.styles.width = "1fr"
            right = ResizablePane(self.panes[1])
            right.styles.width = "1fr"

            splitter = Splitter(orientation="vertical")

            layout = Horizontal(left, splitter, right)
            self.containers.extend([left, right])
            await self.mount(layout)

        elif self.pane_count == 3:
            # Three panes - 2 top, 1 bottom
            top_left = ResizablePane(self.panes[0])
            top_left.styles.width = "1fr"
            top_right = ResizablePane(self.panes[1])
            top_right.styles.width = "1fr"

            v_splitter = Splitter(orientation="vertical")

            top_row = Horizontal(top_left, v_splitter, top_right)
            top_row.styles.height = "1fr"

            h_splitter = Splitter(orientation="horizontal")

            bottom = ResizablePane(self.panes[2])
            bottom.styles.height = "1fr"

            layout = Vertical(top_row, h_splitter, bottom)
            self.containers.extend([top_left, top_right, bottom])
            await self.mount(layout)

        elif self.pane_count == 4:
            # Four panes - 2x2 grid
            top_left = ResizablePane(self.panes[0])
            top_left.styles.width = "1fr"
            top_right = ResizablePane(self.panes[1])
            top_right.styles.width = "1fr"

            v_splitter_top = Splitter(orientation="vertical")

            top_row = Horizontal(top_left, v_splitter_top, top_right)
            top_row.styles.height = "1fr"

            h_splitter = Splitter(orientation="horizontal")

            bottom_left = ResizablePane(self.panes[2])
            bottom_left.styles.width = "1fr"
            bottom_right = ResizablePane(self.panes[3])
            bottom_right.styles.width = "1fr"

            v_splitter_bottom = Splitter(orientation="vertical")

            bottom_row = Horizontal(bottom_left, v_splitter_bottom, bottom_right)
            bottom_row.styles.height = "1fr"

            layout = Vertical(top_row, h_splitter, bottom_row)
            self.containers.extend([top_left, top_right, bottom_left, bottom_right])
            await self.mount(layout)

        else:
            # 5+ panes - dynamic rows with 2 columns
            rows = []
            for i in range(0, self.pane_count, 2):
                left = ResizablePane(self.panes[i])
                left.styles.width = "1fr"

                if i + 1 < self.pane_count:
                    right = ResizablePane(self.panes[i + 1])
                    right.styles.width = "1fr"
                    v_splitter = Splitter(orientation="vertical")
                    row = Horizontal(left, v_splitter, right)
                    self.containers.extend([left, right])
                else:
                    row = Horizontal(left)
                    self.containers.append(left)

                row.styles.height = "1fr"
                rows.append(row)

            # Build vertical layout with horizontal splitters
            layout_children = []
            for i, row in enumerate(rows):
                layout_children.append(row)
                if i < len(rows) - 1:
                    layout_children.append(Splitter(orientation="horizontal"))

            layout = Vertical(*layout_children)
            await self.mount(layout)

    def on_splitter_dragged(self, message: SplitterDragged) -> None:
        """
        Handle splitter drag events to resize panes.

        Args:
            message: SplitterDragged message with drag info
        """
        splitter = message.splitter
        orientation = splitter.orientation

        # Get the parent container of the splitter
        parent = splitter.parent
        if not parent:
            return

        # Find adjacent panes based on orientation
        if orientation == "vertical":
            self._resize_vertical_panes(splitter, parent, message.delta)
        else:
            self._resize_horizontal_panes(splitter, parent, message.delta)

    def _resize_vertical_panes(self, splitter: Splitter, parent: Widget, delta_x: int) -> None:
        """
        Resize panes separated by a vertical splitter (left/right).

        Args:
            splitter: The splitter being dragged
            parent: Parent container holding the splitter and panes
            delta_x: Change in X position from last mouse position (incremental)
        """
        # Get all children in the parent container
        children = list(parent.children)

        # Find the splitter's index
        try:
            splitter_index = children.index(splitter)
        except ValueError:
            return

        # Vertical splitter divides left (before) and right (after) panes
        if splitter_index == 0 or splitter_index >= len(children) - 1:
            return  # Splitter at edge, nothing to resize

        left_pane = children[splitter_index - 1]
        right_pane = children[splitter_index + 1]

        # Only resize ResizablePane instances
        if not isinstance(left_pane, ResizablePane) or not isinstance(right_pane, ResizablePane):
            return

        # Get current actual rendered sizes (in cells/characters)
        left_width = left_pane.size.width
        right_width = right_pane.size.width

        # Calculate total available width
        total_width = left_width + right_width

        if total_width < 2:
            return  # Not enough space to work with

        # Calculate new widths by applying incremental delta
        new_left_width = left_width + delta_x
        new_right_width = right_width - delta_x

        # Enforce minimum sizes (defined in ResizablePane DEFAULT_CSS)
        min_width = 30  # From ResizablePane min-width

        # Clamp to minimum sizes
        if new_left_width < min_width:
            new_left_width = min_width
            new_right_width = total_width - new_left_width
        elif new_right_width < min_width:
            new_right_width = min_width
            new_left_width = total_width - new_right_width

        # Ensure we don't exceed total width
        if new_left_width + new_right_width != total_width:
            # Adjust for rounding
            new_right_width = total_width - new_left_width

        # Convert to fractional units as integers (Textual uses integer fr values)
        # Use a scale factor to preserve precision while using integers
        scale = 1000
        left_fr = int(new_left_width * scale / total_width)
        right_fr = int(new_right_width * scale / total_width)

        # Ensure they sum to scale (handle rounding)
        if left_fr + right_fr != scale:
            right_fr = scale - left_fr

        # Apply new fractional widths using Textual's fr unit format
        left_pane.styles.width = f"{left_fr}fr"
        right_pane.styles.width = f"{right_fr}fr"

    def _resize_horizontal_panes(self, splitter: Splitter, parent: Widget, delta_y: int) -> None:
        """
        Resize panes separated by a horizontal splitter (top/bottom).

        Args:
            splitter: The splitter being dragged
            parent: Parent container holding the splitter and panes
            delta_y: Change in Y position from last mouse position (incremental)
        """
        # Get all children in the parent container
        children = list(parent.children)

        # Find the splitter's index
        try:
            splitter_index = children.index(splitter)
        except ValueError:
            return

        # Horizontal splitter divides top (before) and bottom (after) panes
        if splitter_index == 0 or splitter_index >= len(children) - 1:
            return  # Splitter at edge, nothing to resize

        top_pane = children[splitter_index - 1]
        bottom_pane = children[splitter_index + 1]

        # Get current actual rendered sizes (in cells/lines)
        top_height = top_pane.size.height
        bottom_height = bottom_pane.size.height

        # Calculate total available height
        total_height = top_height + bottom_height

        if total_height < 2:
            return  # Not enough space to work with

        # Calculate new heights by applying incremental delta
        new_top_height = top_height + delta_y
        new_bottom_height = bottom_height - delta_y

        # Enforce minimum sizes
        min_height = 10  # From ResizablePane min-height

        # Clamp to minimum sizes
        if new_top_height < min_height:
            new_top_height = min_height
            new_bottom_height = total_height - new_top_height
        elif new_bottom_height < min_height:
            new_bottom_height = min_height
            new_top_height = total_height - new_bottom_height

        # Ensure we don't exceed total height
        if new_top_height + new_bottom_height != total_height:
            # Adjust for rounding
            new_bottom_height = total_height - new_top_height

        # Convert to fractional units as integers (Textual uses integer fr values)
        # Use a scale factor to preserve precision while using integers
        scale = 1000
        top_fr = int(new_top_height * scale / total_height)
        bottom_fr = int(new_bottom_height * scale / total_height)

        # Ensure they sum to scale (handle rounding)
        if top_fr + bottom_fr != scale:
            bottom_fr = scale - top_fr

        # Apply new fractional heights using Textual's fr unit format
        top_pane.styles.height = f"{top_fr}fr"
        bottom_pane.styles.height = f"{bottom_fr}fr"
