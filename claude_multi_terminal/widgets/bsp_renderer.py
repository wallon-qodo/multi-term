"""Renderer for converting BSP tree to Textual widget hierarchy.

This module handles the conversion of the abstract BSP tree structure into
concrete Textual widgets with proper layout containers and splitters.
"""

from typing import Dict, Any
from textual.containers import Horizontal, Vertical, Container
from textual.widget import Widget

from .bsp_tree import BSPTree, BSPNode, SplitDirection


class ResizablePane(Container):
    """Wrapper for a session pane that can be resized."""

    def __init__(self, content: Widget, **kwargs: Any):
        super().__init__(**kwargs)
        self.content = content
        self._compose_children = [content]

    def compose(self):
        yield self.content


class Splitter(Widget):
    """A draggable splitter between panes.

    Attributes:
        orientation: 'vertical' for left/right split, 'horizontal' for top/bottom split.
    """

    DEFAULT_CSS = """
    Splitter {
        width: 1;
        height: 1;
        background: $surface;
    }

    Splitter.vertical {
        width: 1;
        height: 100%;
    }

    Splitter.horizontal {
        width: 100%;
        height: 1;
    }

    Splitter:hover {
        background: $primary;
    }
    """

    def __init__(self, orientation: str = "vertical", **kwargs: Any):
        super().__init__(**kwargs)
        self.orientation = orientation
        self.add_class(orientation)


class BSPRenderer:
    """Converts BSP tree structure to Textual widget hierarchy.

    The renderer traverses the BSP tree and creates the appropriate container
    widgets (Horizontal/Vertical) with splitters between panes.
    """

    def render(self, tree: BSPTree, panes: Dict[str, Widget]) -> Widget:
        """Convert BSP tree to Textual widget hierarchy.

        Args:
            tree: The BSP tree to render.
            panes: Dictionary mapping session IDs to their widget instances.

        Returns:
            A Textual widget containing the entire layout.
        """
        if tree.root is None:
            return Vertical()  # Empty container

        return self._render_node(tree.root, panes)

    def _render_node(self, node: BSPNode, panes: Dict[str, Widget]) -> Widget:
        """Recursively render a BSP node and its children.

        Args:
            node: The BSP node to render.
            panes: Dictionary mapping session IDs to their widget instances.

        Returns:
            A Textual widget representing this node and its subtree.
        """
        if node.is_leaf():
            # Leaf node - return the pane directly (already has session_id)
            if node.pane_id in panes:
                pane_widget = panes[node.pane_id]
                # Ensure session_id is set
                if not hasattr(pane_widget, 'session_id'):
                    pane_widget.session_id = node.pane_id
                return pane_widget
            return Vertical()  # Fallback for missing pane

        # Internal node - create container with splitter
        left_widget = (self._render_node(node.left, panes)
                      if node.left else Vertical())
        right_widget = (self._render_node(node.right, panes)
                       if node.right else Vertical())

        # Apply ratio to widgets using fractional units
        # Scale to integers to avoid floating point precision issues
        left_fr = int(node.ratio * 1000)
        right_fr = int((1 - node.ratio) * 1000)

        if node.split_direction == SplitDirection.VERTICAL:
            # Vertical split (left/right)
            left_widget.styles.width = f"{left_fr}fr"
            right_widget.styles.width = f"{right_fr}fr"
            splitter = Splitter(orientation="vertical")
            container = Horizontal(left_widget, splitter, right_widget)
        else:
            # Horizontal split (top/bottom)
            left_widget.styles.height = f"{left_fr}fr"
            right_widget.styles.height = f"{right_fr}fr"
            splitter = Splitter(orientation="horizontal")
            container = Vertical(left_widget, splitter, right_widget)

        # Store split info on container for resize handling
        container.split_node = node
        return container


class MockSessionPane(Widget):
    """Mock session pane for testing purposes."""

    DEFAULT_CSS = """
    MockSessionPane {
        width: 100%;
        height: 100%;
        border: solid $primary;
    }
    """

    def __init__(self, session_id: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.session_id = session_id

    def render(self) -> str:
        return f"Session: {self.session_id}"
