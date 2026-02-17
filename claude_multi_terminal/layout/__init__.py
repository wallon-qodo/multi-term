"""Layout management system for BSP (Binary Space Partitioning) tiling.

This module provides the core BSP layout engine for TUIOS-inspired multi-terminal
workspace management. The BSP tree structure enables efficient dynamic tiling with
manual split control and automatic rebalancing.

Exports:
    # Layout Manager (integration layer)
    LayoutManager: Main layout coordinator
    LayoutRect: Terminal grid rectangle
    SessionLayout: Per-session layout information
    WorkspaceLayoutState: Per-workspace layout state
    SplitDirection: Enum for horizontal/vertical splits

    # BSP Engine (core implementation - when available)
    BSPNode: Binary tree node representing a split
    BSPTree: Manager for BSP layout within a workspace
"""

from claude_multi_terminal.layout.layout_manager import (
    LayoutManager,
    LayoutRect,
    SessionLayout,
    SplitDirection,
    WorkspaceLayoutState,
)

# BSP engine will be imported when available
# from claude_multi_terminal.layout.bsp_engine import (
#     BSPNode,
#     BSPTree,
# )

__all__ = [
    "LayoutManager",
    "LayoutRect",
    "SessionLayout",
    "SplitDirection",
    "WorkspaceLayoutState",
    # "BSPNode",    # Available when bsp_engine is implemented
    # "BSPTree",    # Available when bsp_engine is implemented
]
