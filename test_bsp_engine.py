#!/usr/bin/env python3
"""Test script for BSP engine implementation.

This script verifies the core BSP functionality including:
- Tree initialization
- Session insertion with alternating splits
- Session removal and rebalancing
- Layout calculation
- Split adjustment and rotation
- Edge cases (empty tree, single session, etc.)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Direct import to avoid app initialization
from claude_multi_terminal.layout.bsp_engine import BSPTree, SplitDirection


def test_empty_tree():
    """Test empty tree behavior."""
    print("Test 1: Empty tree")
    tree = BSPTree(workspace_id=1)
    assert tree.is_empty()
    assert tree.get_session_count() == 0
    assert tree.get_layout(160, 40) == {}
    print("  ✓ Empty tree behaves correctly")


def test_single_session():
    """Test tree with single session."""
    print("\nTest 2: Single session")
    tree = BSPTree(workspace_id=1)
    assert tree.insert_session("s1")
    assert not tree.is_empty()
    assert tree.get_session_count() == 1
    assert tree.focused_session_id == "s1"

    layout = tree.get_layout(160, 40)
    assert layout["s1"] == (0, 0, 160, 40)
    print("  ✓ Single session takes full space")


def test_two_sessions_horizontal():
    """Test horizontal split (depth 0 = horizontal)."""
    print("\nTest 3: Two sessions (horizontal split)")
    tree = BSPTree(workspace_id=1)
    tree.insert_session("s1")
    tree.insert_session("s2")

    assert tree.get_session_count() == 2
    assert tree.focused_session_id == "s2"

    layout = tree.get_layout(160, 40)
    # Root depth 0 → HORIZONTAL split (left/right)
    assert layout["s1"] == (0, 0, 80, 40)
    assert layout["s2"] == (80, 0, 80, 40)
    print("  ✓ Horizontal split (left/right) at depth 0")


def test_three_sessions_alternating():
    """Test alternating split directions."""
    print("\nTest 4: Three sessions (alternating splits)")
    tree = BSPTree(workspace_id=1)
    tree.insert_session("s1")
    tree.insert_session("s2")
    tree.insert_session("s3")  # Splits s2 (depth 1 → vertical)

    assert tree.get_session_count() == 3

    layout = tree.get_layout(160, 40)
    # s1 on left (0, 0, 80, 40)
    # s2 and s3 on right, split vertically (top/bottom)
    assert layout["s1"] == (0, 0, 80, 40)
    assert layout["s2"] == (80, 0, 80, 20)
    assert layout["s3"] == (80, 20, 80, 20)
    print("  ✓ Alternating splits (H → V)")


def test_session_removal():
    """Test session removal and rebalancing."""
    print("\nTest 5: Session removal")
    tree = BSPTree(workspace_id=1)
    tree.insert_session("s1")
    tree.insert_session("s2")
    tree.insert_session("s3")

    # Remove s2, s3 should be promoted
    assert tree.remove_session("s2")
    assert tree.get_session_count() == 2

    layout = tree.get_layout(160, 40)
    # Should have s1 and s3, split horizontally
    assert "s2" not in layout
    assert "s1" in layout
    assert "s3" in layout
    print("  ✓ Session removal and rebalancing works")


def test_remove_last_session():
    """Test removing the last session."""
    print("\nTest 6: Remove last session")
    tree = BSPTree(workspace_id=1)
    tree.insert_session("s1")
    assert tree.remove_session("s1")
    assert tree.is_empty()
    assert tree.focused_session_id is None
    print("  ✓ Removing last session clears tree")


def test_split_adjustment():
    """Test adjusting split ratios."""
    print("\nTest 7: Split ratio adjustment")
    tree = BSPTree(workspace_id=1)
    tree.insert_session("s1")
    tree.insert_session("s2")

    # Increase s1's space by 20%
    assert tree.adjust_split_ratio("s1", 0.2)

    layout = tree.get_layout(160, 40)
    # s1 should now have 70% (112 cols), s2 has 30% (48 cols)
    assert layout["s1"] == (0, 0, 112, 40)
    assert layout["s2"] == (112, 0, 48, 40)
    print("  ✓ Split ratio adjustment works")


def test_split_rotation():
    """Test rotating split direction."""
    print("\nTest 8: Split rotation")
    tree = BSPTree(workspace_id=1)
    tree.insert_session("s1")
    tree.insert_session("s2")

    # Initial: horizontal split (left/right)
    layout_before = tree.get_layout(160, 40)
    assert layout_before["s1"] == (0, 0, 80, 40)
    assert layout_before["s2"] == (80, 0, 80, 40)

    # Rotate to vertical (top/bottom)
    assert tree.rotate_split("s1")

    layout_after = tree.get_layout(160, 40)
    assert layout_after["s1"] == (0, 0, 160, 20)
    assert layout_after["s2"] == (0, 20, 160, 20)
    print("  ✓ Split rotation (H → V) works")


def test_minimum_pane_size():
    """Test minimum pane size constraints."""
    print("\nTest 9: Minimum pane size")
    tree = BSPTree(workspace_id=1, min_pane_width=20, min_pane_height=5)
    tree.insert_session("s1")
    tree.insert_session("s2")

    # Try to make very small layout
    layout = tree.get_layout(30, 8)

    # Should respect minimums (20 cols, 5 rows)
    for session_id, (x, y, width, height) in layout.items():
        assert width >= 20, f"{session_id} width {width} < 20"
        assert height >= 5, f"{session_id} height {height} < 5"
    print("  ✓ Minimum pane size constraints enforced")


def test_tree_visualization():
    """Test tree visualization output."""
    print("\nTest 10: Tree visualization")
    tree = BSPTree(workspace_id=1)
    tree.insert_session("s1")
    tree.insert_session("s2")
    tree.insert_session("s3")

    viz = tree.get_tree_visualization()
    assert "Root:" in viz
    assert "[s1]" in viz
    assert "[s2]" in viz
    assert "[s3]" in viz
    print("  ✓ Tree visualization generated")
    print("\nTree structure:")
    print(viz)


def test_complex_layout():
    """Test more complex layout with 5 sessions."""
    print("\nTest 11: Complex layout (5 sessions)")
    tree = BSPTree(workspace_id=1)

    # Insert 5 sessions
    for i in range(1, 6):
        tree.insert_session(f"s{i}")

    assert tree.get_session_count() == 5

    layout = tree.get_layout(200, 60)

    # Verify all sessions have valid coordinates
    for session_id, (x, y, width, height) in layout.items():
        assert 0 <= x < 200
        assert 0 <= y < 60
        assert width > 0
        assert height > 0
        print(f"  {session_id}: ({x}, {y}, {width}, {height})")

    print("  ✓ Complex layout calculated correctly")


def test_duplicate_insert():
    """Test inserting duplicate session."""
    print("\nTest 12: Duplicate session insert")
    tree = BSPTree(workspace_id=1)
    assert tree.insert_session("s1")
    assert not tree.insert_session("s1")  # Should fail
    assert tree.get_session_count() == 1
    print("  ✓ Duplicate insert rejected")


def test_remove_nonexistent():
    """Test removing non-existent session."""
    print("\nTest 13: Remove non-existent session")
    tree = BSPTree(workspace_id=1)
    tree.insert_session("s1")
    assert not tree.remove_session("s999")  # Should fail
    assert tree.get_session_count() == 1
    print("  ✓ Non-existent removal handled gracefully")


def run_all_tests():
    """Run all BSP engine tests."""
    print("=" * 60)
    print("BSP Engine Test Suite")
    print("=" * 60)

    test_empty_tree()
    test_single_session()
    test_two_sessions_horizontal()
    test_three_sessions_alternating()
    test_session_removal()
    test_remove_last_session()
    test_split_adjustment()
    test_split_rotation()
    test_minimum_pane_size()
    test_tree_visualization()
    test_complex_layout()
    test_duplicate_insert()
    test_remove_nonexistent()

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
