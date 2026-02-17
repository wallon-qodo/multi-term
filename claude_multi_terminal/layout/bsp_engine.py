"""BSP (Binary Space Partitioning) layout engine for TUIOS-inspired tiling.

This module implements a binary tree-based tiling window manager inspired by bspwm.
Each workspace maintains a BSP tree where leaf nodes contain sessions and internal
nodes represent splits. This enables manual tiling control with automatic rebalancing.

Design Philosophy:
    - Simple binary tree structure for predictable behavior
    - Alternating split directions (H → V → H) for balanced layouts
    - Default 50/50 splits with manual adjustment capability
    - Minimum pane constraints to prevent unusable splits
    - TUIOS principles: efficiency, clarity, user control

Color References (HomebrewTheme):
    - BORDER_FOCUS (rgb(255,77,77)): Focused pane border (coral red)
    - BORDER_DEFAULT (rgb(60,60,60)): Unfocused pane borders
    - BG_PRIMARY (rgb(24,24,24)): Session background
    - ACCENT_PRIMARY (rgb(255,77,77)): Split adjustment indicators

Architecture:
    BSPNode: Binary tree node (leaf = session, internal = split)
    BSPTree: Manager for tree operations and layout calculation
    SplitDirection: Enum for horizontal/vertical orientation

Example Usage:
    >>> tree = BSPTree(workspace_id=1)
    >>> tree.insert_session("session-1")  # Creates root
    >>> tree.insert_session("session-2")  # Splits root horizontally
    >>> tree.insert_session("session-3")  # Splits focused vertically
    >>> layout = tree.get_layout(terminal_width=160, terminal_height=40)
    >>> # Returns: {"session-1": (0, 0, 80, 40), "session-2": (80, 0, 80, 20), ...}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import uuid


class SplitDirection(Enum):
    """Direction of split in BSP tree.

    Attributes:
        HORIZONTAL: Split left/right (creates vertical divider)
        VERTICAL: Split top/bottom (creates horizontal divider)

    Note:
        HORIZONTAL split means the split line is vertical (splits horizontally).
        VERTICAL split means the split line is horizontal (splits vertically).
        This matches tmux/bspwm terminology.
    """
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class BSPNode:
    """Binary tree node representing a split or session in BSP layout.

    A BSPNode is either:
    - Leaf node: Contains a session_id, no children
    - Internal node: Contains split metadata and left/right children

    Attributes:
        node_id: Unique identifier for this node (UUID)
        is_leaf: True if node contains a session (leaf), False if split (internal)
        session_id: Session UUID if leaf node, None otherwise
        split_direction: Orientation of split if internal node
        split_ratio: Split position ratio (0.0-1.0), default 0.5 for balanced split
        left: Left child node (or top if vertical split)
        right: Right child node (or bottom if vertical split)
        parent: Parent node reference for tree navigation

    Design Notes:
        - Leaf nodes have session_id set, internal nodes have children
        - split_ratio of 0.5 means equal 50/50 split
        - split_ratio of 0.3 means left/top gets 30%, right/bottom gets 70%
        - Minimum ratio constraints enforced during adjustment (0.2-0.8)
    """

    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_leaf: bool = True
    session_id: Optional[str] = None
    split_direction: Optional[SplitDirection] = None
    split_ratio: float = 0.5
    left: Optional[BSPNode] = None
    right: Optional[BSPNode] = None
    parent: Optional[BSPNode] = None

    def __post_init__(self) -> None:
        """Validate node state after initialization.

        Raises:
            ValueError: If leaf node without session_id or internal node without children
        """
        if self.is_leaf and not self.session_id:
            raise ValueError("Leaf node must have session_id")
        if not self.is_leaf and (not self.left or not self.right):
            raise ValueError("Internal node must have both left and right children")
        if not 0.0 <= self.split_ratio <= 1.0:
            raise ValueError(f"split_ratio must be 0.0-1.0, got {self.split_ratio}")

    def is_root(self) -> bool:
        """Check if this node is the root of the tree."""
        return self.parent is None

    def get_sibling(self) -> Optional[BSPNode]:
        """Get the sibling node (other child of same parent).

        Returns:
            Sibling BSPNode if parent exists, None otherwise
        """
        if not self.parent:
            return None
        return self.parent.right if self.parent.left is self else self.parent.left

    def get_depth(self) -> int:
        """Calculate depth of this node in tree (root = 0)."""
        depth = 0
        node = self
        while node.parent:
            depth += 1
            node = node.parent
        return depth

    def find_session_node(self, session_id: str) -> Optional[BSPNode]:
        """Recursively find leaf node containing given session_id.

        Args:
            session_id: Session UUID to search for

        Returns:
            BSPNode if found, None otherwise
        """
        if self.is_leaf:
            return self if self.session_id == session_id else None

        # Search left subtree
        if self.left:
            result = self.left.find_session_node(session_id)
            if result:
                return result

        # Search right subtree
        if self.right:
            return self.right.find_session_node(session_id)

        return None

    def get_all_sessions(self) -> List[str]:
        """Recursively collect all session IDs in subtree.

        Returns:
            List of session_id strings in left-to-right order
        """
        if self.is_leaf:
            return [self.session_id] if self.session_id else []

        sessions = []
        if self.left:
            sessions.extend(self.left.get_all_sessions())
        if self.right:
            sessions.extend(self.right.get_all_sessions())
        return sessions


class BSPTree:
    """BSP (Binary Space Partitioning) tree manager for workspace layouts.

    Manages a binary tree structure for organizing sessions in a tiling layout.
    Provides operations for inserting/removing sessions, adjusting splits, and
    calculating screen coordinates for rendering.

    Attributes:
        workspace_id: Associated workspace identifier (1-9)
        root: Root node of BSP tree (None if empty)
        focused_session_id: Currently focused session UUID
        min_pane_width: Minimum pane width in columns (default: 10)
        min_pane_height: Minimum pane height in rows (default: 3)

    Design Notes:
        - New sessions split the focused node
        - Alternating split directions based on depth (even=H, odd=V)
        - Default 50/50 splits, adjustable via adjust_split_ratio()
        - Removing a session promotes its sibling to parent's position
        - Empty tree (no root) returns empty layout

    Example:
        >>> tree = BSPTree(workspace_id=1)
        >>> tree.insert_session("s1")  # Root: s1
        >>> tree.insert_session("s2")  # Root: split(s1, s2) horizontal
        >>> tree.insert_session("s3")  # Focused s2 -> split(s2, s3) vertical
        >>> layout = tree.get_layout(160, 40)
    """

    def __init__(
        self,
        workspace_id: int,
        min_pane_width: int = 10,
        min_pane_height: int = 3,
    ):
        """Initialize empty BSP tree for workspace.

        Args:
            workspace_id: Workspace identifier (1-9)
            min_pane_width: Minimum pane width in columns
            min_pane_height: Minimum pane height in rows
        """
        self.workspace_id = workspace_id
        self.root: Optional[BSPNode] = None
        self.focused_session_id: Optional[str] = None
        self.min_pane_width = min_pane_width
        self.min_pane_height = min_pane_height
        self._session_node_map: Dict[str, BSPNode] = {}

    def is_empty(self) -> bool:
        """Check if tree has no sessions."""
        return self.root is None

    def get_session_count(self) -> int:
        """Get total number of sessions in tree."""
        if not self.root:
            return 0
        return len(self.root.get_all_sessions())

    def get_all_session_ids(self) -> List[str]:
        """Get list of all session IDs in tree (left-to-right order)."""
        if not self.root:
            return []
        return self.root.get_all_sessions()

    def find_node(self, session_id: str) -> Optional[BSPNode]:
        """Find node containing given session_id.

        Args:
            session_id: Session UUID to find

        Returns:
            BSPNode if found, None otherwise
        """
        return self._session_node_map.get(session_id)

    def _determine_split_direction(self, node: BSPNode) -> SplitDirection:
        """Determine split direction based on node depth (alternating).

        Args:
            node: Node being split

        Returns:
            SplitDirection.HORIZONTAL for even depth (0, 2, 4...)
            SplitDirection.VERTICAL for odd depth (1, 3, 5...)

        Design:
            Alternating splits create more balanced layouts:
            Root (depth 0) → HORIZONTAL (split left/right)
            Children (depth 1) → VERTICAL (split top/bottom)
            Grandchildren (depth 2) → HORIZONTAL again
        """
        depth = node.get_depth()
        return SplitDirection.HORIZONTAL if depth % 2 == 0 else SplitDirection.VERTICAL

    def insert_session(self, session_id: str, target_session_id: Optional[str] = None) -> bool:
        """Insert new session into BSP tree.

        Behavior:
            - Empty tree: Create root leaf with session
            - Non-empty: Split focused node (or target node) and insert
            - Split direction alternates by depth (H/V/H/V...)
            - Default 50/50 split ratio

        Args:
            session_id: UUID of session to insert
            target_session_id: Optional target session to split (uses focused if None)

        Returns:
            True if inserted successfully, False if session already exists

        Example:
            >>> tree.insert_session("s1")  # Creates root
            >>> tree.insert_session("s2")  # Splits root horizontally
            >>> tree.focused_session_id = "s2"
            >>> tree.insert_session("s3")  # Splits s2 vertically
        """
        # Check if session already exists
        if self.find_node(session_id):
            return False

        # Empty tree case: create root
        if not self.root:
            self.root = BSPNode(
                is_leaf=True,
                session_id=session_id,
            )
            self._session_node_map[session_id] = self.root
            self.focused_session_id = session_id
            return True

        # Find target node to split (focused or specified)
        target_id = target_session_id or self.focused_session_id
        if not target_id:
            # No focus, use first session
            target_id = self.get_all_session_ids()[0]

        target_node = self.find_node(target_id)
        if not target_node or not target_node.is_leaf:
            return False

        # Determine split direction based on depth
        split_dir = self._determine_split_direction(target_node)

        # Create new nodes
        new_node = BSPNode(
            is_leaf=True,
            session_id=session_id,
        )

        # Convert target to internal node
        old_session_id = target_node.session_id
        target_node.is_leaf = False
        target_node.session_id = None
        target_node.split_direction = split_dir
        target_node.split_ratio = 0.5

        # Create left child with old session
        left_child = BSPNode(
            is_leaf=True,
            session_id=old_session_id,
            parent=target_node,
        )

        # Set up tree structure
        target_node.left = left_child
        target_node.right = new_node
        new_node.parent = target_node

        # Update session map
        self._session_node_map[old_session_id] = left_child
        self._session_node_map[session_id] = new_node

        # Update focus to new session
        self.focused_session_id = session_id

        return True

    def remove_session(self, session_id: str) -> bool:
        """Remove session from BSP tree and rebalance.

        Behavior:
            - Find and remove leaf node containing session
            - Promote sibling to parent's position
            - Update parent references
            - Adjust focus if removed session was focused

        Args:
            session_id: UUID of session to remove

        Returns:
            True if removed successfully, False if not found

        Example:
            >>> tree.insert_session("s1")
            >>> tree.insert_session("s2")
            >>> tree.insert_session("s3")
            >>> tree.remove_session("s2")  # Promotes s3 to parent position
        """
        node = self._session_node_map.get(session_id)
        if not node or not node.is_leaf:
            return False

        # Remove from map
        del self._session_node_map[session_id]

        # Special case: root node (only session)
        if node.is_root():
            self.root = None
            self.focused_session_id = None
            return True

        # Get parent and sibling
        parent = node.parent
        sibling = node.get_sibling()

        if not parent or not sibling:
            return False

        # Promote sibling to parent's position
        grandparent = parent.parent

        if grandparent:
            # Update grandparent's child reference
            if grandparent.left is parent:
                grandparent.left = sibling
            else:
                grandparent.right = sibling
            sibling.parent = grandparent
        else:
            # Parent was root, sibling becomes new root
            self.root = sibling
            sibling.parent = None

        # Update focus if necessary
        if self.focused_session_id == session_id:
            # Focus on sibling or first session
            if sibling.is_leaf:
                self.focused_session_id = sibling.session_id
            else:
                sessions = sibling.get_all_sessions()
                self.focused_session_id = sessions[0] if sessions else None

        return True

    def adjust_split_ratio(self, session_id: str, delta: float) -> bool:
        """Adjust split ratio of node's parent split.

        Changes the split ratio of the parent node that contains the given session.
        Positive delta increases the session's space, negative delta decreases it.

        Args:
            session_id: Session whose parent split to adjust
            delta: Amount to adjust ratio (-1.0 to 1.0), typically ±0.05 for 5% changes

        Returns:
            True if adjusted, False if at root or invalid

        Constraints:
            - Ratio clamped to 0.2-0.8 range (min 20%, max 80%)
            - Respects minimum pane size constraints

        Example:
            >>> tree.adjust_split_ratio("s1", 0.1)  # Increase s1's space by 10%
            >>> tree.adjust_split_ratio("s2", -0.05)  # Decrease s2's space by 5%
        """
        node = self.find_node(session_id)
        if not node or not node.parent:
            return False

        parent = node.parent

        # Determine if we're adjusting left/right or top/bottom
        is_left = parent.left is node

        # Calculate new ratio
        if is_left:
            new_ratio = parent.split_ratio + delta
        else:
            new_ratio = parent.split_ratio - delta

        # Clamp to reasonable bounds (20%-80%)
        new_ratio = max(0.2, min(0.8, new_ratio))

        parent.split_ratio = new_ratio
        return True

    def rotate_split(self, session_id: str) -> bool:
        """Toggle split direction of node's parent (H ↔ V).

        Changes the parent node's split orientation from horizontal to vertical
        or vice versa. Useful for manual layout adjustments.

        Args:
            session_id: Session whose parent split to rotate

        Returns:
            True if rotated, False if at root or invalid

        Example:
            >>> tree.rotate_split("s1")  # H → V or V → H
        """
        node = self.find_node(session_id)
        if not node or not node.parent:
            return False

        parent = node.parent

        # Toggle direction
        if parent.split_direction == SplitDirection.HORIZONTAL:
            parent.split_direction = SplitDirection.VERTICAL
        else:
            parent.split_direction = SplitDirection.HORIZONTAL

        return True

    def get_layout(
        self,
        terminal_width: int,
        terminal_height: int,
    ) -> Dict[str, Tuple[int, int, int, int]]:
        """Calculate layout coordinates for all sessions.

        Recursively traverses BSP tree and calculates screen coordinates for each
        session pane based on splits and ratios.

        Args:
            terminal_width: Total terminal width in columns
            terminal_height: Total terminal height in rows

        Returns:
            Dictionary mapping session_id to (x, y, width, height) tuple
            Empty dict if tree is empty

        Coordinate System:
            - Origin (0, 0) is top-left corner
            - x increases rightward (columns)
            - y increases downward (rows)
            - width/height are inclusive dimensions

        Example:
            >>> layout = tree.get_layout(160, 40)
            >>> # {"s1": (0, 0, 80, 40), "s2": (80, 0, 80, 20), "s3": (80, 20, 80, 20)}
        """
        if not self.root:
            return {}

        layout: Dict[str, Tuple[int, int, int, int]] = {}

        def calculate_recursive(
            node: BSPNode,
            x: int,
            y: int,
            width: int,
            height: int,
        ) -> None:
            """Recursive helper to calculate node bounds.

            Args:
                node: Current node being processed
                x: Left coordinate of node's region
                y: Top coordinate of node's region
                width: Width of node's region in columns
                height: Height of node's region in rows
            """
            if node.is_leaf:
                # Leaf node: record session coordinates
                if node.session_id:
                    # Ensure minimum size constraints
                    actual_width = max(width, self.min_pane_width)
                    actual_height = max(height, self.min_pane_height)
                    layout[node.session_id] = (x, y, actual_width, actual_height)
                return

            # Internal node: calculate split and recurse
            if node.split_direction == SplitDirection.HORIZONTAL:
                # Horizontal split: divide width (left/right)
                split_point = int(width * node.split_ratio)

                # Ensure minimum sizes
                left_width = max(split_point, self.min_pane_width)
                right_width = max(width - split_point, self.min_pane_width)

                # Adjust if total exceeds available space
                if left_width + right_width > width:
                    left_width = width // 2
                    right_width = width - left_width

                # Recurse on children
                if node.left:
                    calculate_recursive(node.left, x, y, left_width, height)
                if node.right:
                    calculate_recursive(node.right, x + left_width, y, right_width, height)

            else:  # VERTICAL split
                # Vertical split: divide height (top/bottom)
                split_point = int(height * node.split_ratio)

                # Ensure minimum sizes
                top_height = max(split_point, self.min_pane_height)
                bottom_height = max(height - split_point, self.min_pane_height)

                # Adjust if total exceeds available space
                if top_height + bottom_height > height:
                    top_height = height // 2
                    bottom_height = height - top_height

                # Recurse on children
                if node.left:
                    calculate_recursive(node.left, x, y, width, top_height)
                if node.right:
                    calculate_recursive(node.right, x, y + top_height, width, bottom_height)

        # Start recursive calculation from root
        calculate_recursive(self.root, 0, 0, terminal_width, terminal_height)

        return layout

    def get_tree_visualization(self) -> str:
        """Generate ASCII visualization of BSP tree structure.

        Returns:
            Multi-line string representing tree structure
            Empty string if tree is empty

        Format:
            Root
            ├── H(0.5)
            │   ├── [session-1]
            │   └── V(0.5)
            │       ├── [session-2]
            │       └── [session-3]

        Legend:
            H/V: Split direction (Horizontal/Vertical)
            (0.5): Split ratio
            [session-id]: Leaf node with session
        """
        if not self.root:
            return "(empty tree)"

        lines: List[str] = []

        def visualize_recursive(node: BSPNode, prefix: str, is_last: bool) -> None:
            """Recursive helper to build visualization.

            Args:
                node: Current node being visualized
                prefix: Current line prefix for indentation
                is_last: True if this is the last child of parent
            """
            # Current node line
            connector = "└── " if is_last else "├── "

            if node.is_leaf:
                lines.append(f"{prefix}{connector}[{node.session_id}]")
            else:
                split_char = "H" if node.split_direction == SplitDirection.HORIZONTAL else "V"
                lines.append(f"{prefix}{connector}{split_char}({node.split_ratio:.2f})")

                # Prepare prefix for children
                child_prefix = prefix + ("    " if is_last else "│   ")

                # Recurse on children
                if node.left:
                    visualize_recursive(node.left, child_prefix, False)
                if node.right:
                    visualize_recursive(node.right, child_prefix, True)

        # Start with root
        if self.root.is_leaf:
            lines.append(f"Root: [{self.root.session_id}]")
        else:
            split_char = "H" if self.root.split_direction == SplitDirection.HORIZONTAL else "V"
            lines.append(f"Root: {split_char}({self.root.split_ratio:.2f})")

            if self.root.left:
                visualize_recursive(self.root.left, "", False)
            if self.root.right:
                visualize_recursive(self.root.right, "", True)

        return "\n".join(lines)

    def __repr__(self) -> str:
        """String representation for debugging."""
        session_count = self.get_session_count()
        return (
            f"BSPTree(workspace_id={self.workspace_id}, "
            f"sessions={session_count}, "
            f"focused={self.focused_session_id})"
        )
