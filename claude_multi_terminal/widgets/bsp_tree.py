"""Binary Space Partitioning tree for terminal pane layout management.

This module implements a BSP tree that manages the hierarchical layout of terminal
panes with automatic spiral insertion and dynamic resizing support.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, List


class SplitDirection(Enum):
    """Direction of a split in the BSP tree."""
    VERTICAL = auto()
    HORIZONTAL = auto()


@dataclass
class BSPNode:
    """A node in the BSP tree.

    Leaf nodes represent actual terminal panes (pane_id is set).
    Internal nodes represent splits (split_direction and children are set).
    """
    split_direction: Optional[SplitDirection] = None
    ratio: float = 0.5  # Split ratio (0.0 to 1.0)
    left: Optional['BSPNode'] = None
    right: Optional['BSPNode'] = None
    pane_id: Optional[str] = None

    def is_leaf(self) -> bool:
        """Check if this node is a leaf (represents a terminal pane)."""
        return self.pane_id is not None


class BSPTree:
    """Binary Space Partitioning tree for terminal layout management.

    The tree automatically manages terminal pane layout using a spiral insertion
    pattern (alternating vertical/horizontal splits). Supports dynamic resizing
    and pane removal with automatic tree restructuring.
    """

    def __init__(self):
        self.root: Optional[BSPNode] = None
        self.pane_map: Dict[str, BSPNode] = {}
        self.insertion_count = 0

    def insert_spiral(self, session_id: str) -> None:
        """Insert a new pane with automatic V/H alternation (spiral pattern).

        Args:
            session_id: Unique identifier for the terminal session/pane.
        """
        if self.root is None:
            # First pane - create root
            self.root = BSPNode(pane_id=session_id)
            self.pane_map[session_id] = self.root
            return

        # Determine split direction (alternate per insertion)
        split_dir = (SplitDirection.VERTICAL if self.insertion_count % 2 == 0
                    else SplitDirection.HORIZONTAL)
        self.insertion_count += 1

        # Find the newest/rightmost leaf to split
        target = self._find_newest_leaf(self.root)
        if target:
            self._split_node(target, session_id, split_dir)

    def _find_newest_leaf(self, node: BSPNode) -> Optional[BSPNode]:
        """Find the newest (rightmost) leaf node in the tree.

        Args:
            node: Starting node for the search.

        Returns:
            The newest leaf node, or None if tree is empty.
        """
        if node.is_leaf():
            return node

        # Traverse right-most path (newer insertions)
        if node.right:
            return self._find_newest_leaf(node.right)
        elif node.left:
            return self._find_newest_leaf(node.left)

        return None

    def _split_node(self, node: BSPNode, new_session_id: str,
                    direction: SplitDirection) -> None:
        """Split a leaf node into an internal node with two children.

        Args:
            node: The leaf node to split.
            new_session_id: Session ID for the new pane.
            direction: Direction of the split (vertical or horizontal).
        """
        old_session_id = node.pane_id

        # Convert leaf to internal node
        node.pane_id = None
        node.split_direction = direction
        node.ratio = 0.5

        # Create child nodes
        node.left = BSPNode(pane_id=old_session_id)
        node.right = BSPNode(pane_id=new_session_id)

        # Update pane map
        self.pane_map[old_session_id] = node.left
        self.pane_map[new_session_id] = node.right

    def remove_node(self, session_id: str) -> bool:
        """Remove a pane from the tree and restructure.

        When a pane is removed, its parent node is replaced by its sibling,
        effectively collapsing the tree at that point.

        Args:
            session_id: The session ID of the pane to remove.

        Returns:
            True if the node was found and removed, False otherwise.
        """
        if session_id not in self.pane_map:
            return False

        node = self.pane_map[session_id]
        parent = self._find_parent(self.root, node)

        if parent is None:
            # Removing root (last pane)
            self.root = None
            self.pane_map.clear()
            self.insertion_count = 0
            return True

        # Replace parent with sibling
        sibling = parent.left if parent.right == node else parent.right
        if sibling:
            # Copy sibling's properties to parent
            parent.split_direction = sibling.split_direction
            parent.ratio = sibling.ratio
            parent.left = sibling.left
            parent.right = sibling.right
            parent.pane_id = sibling.pane_id

            # Update pane map if sibling was a leaf
            if sibling.pane_id:
                self.pane_map[sibling.pane_id] = parent

        # Remove from pane map
        del self.pane_map[session_id]
        return True

    def _find_parent(self, current: Optional[BSPNode],
                     target: BSPNode) -> Optional[BSPNode]:
        """Find the parent node of a given target node.

        Args:
            current: Current node in the traversal.
            target: The node whose parent we're looking for.

        Returns:
            The parent node, or None if target is root or not found.
        """
        if current is None or current.is_leaf():
            return None

        if current.left == target or current.right == target:
            return current

        # Recursively search left subtree
        result = self._find_parent(current.left, target)
        if result:
            return result

        # Search right subtree
        return self._find_parent(current.right, target)

    def rebalance_subtree(self, session_id: str, delta_ratio: float) -> None:
        """Adjust split ratio for resizing a pane.

        Args:
            session_id: The session ID of the pane being resized.
            delta_ratio: The change in ratio (-1.0 to 1.0).
        """
        if session_id not in self.pane_map:
            return

        node = self.pane_map[session_id]
        parent = self._find_parent(self.root, node)

        if parent:
            # Clamp ratio between 0.1 and 0.9 (10% to 90%)
            parent.ratio = max(0.1, min(0.9, parent.ratio + delta_ratio))

    def get_all_panes(self) -> List[str]:
        """Get a list of all pane IDs in the tree.

        Returns:
            List of session IDs for all panes.
        """
        return list(self.pane_map.keys())

    def get_pane_count(self) -> int:
        """Get the total number of panes in the tree.

        Returns:
            Number of panes.
        """
        return len(self.pane_map)

    def clear(self) -> None:
        """Clear the entire tree."""
        self.root = None
        self.pane_map.clear()
        self.insertion_count = 0

    def swap_panes(self, session_id_a: str, session_id_b: str) -> bool:
        """Swap two panes in the tree.

        Args:
            session_id_a: First session ID
            session_id_b: Second session ID

        Returns:
            True if swap was successful
        """
        if session_id_a not in self.pane_map or session_id_b not in self.pane_map:
            return False

        node_a = self.pane_map[session_id_a]
        node_b = self.pane_map[session_id_b]

        # Swap the pane IDs in the nodes
        node_a.pane_id, node_b.pane_id = node_b.pane_id, node_a.pane_id

        # Update pane_map
        self.pane_map[session_id_a] = node_b
        self.pane_map[session_id_b] = node_a

        return True
