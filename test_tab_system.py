#!/usr/bin/env python3
"""Test script to verify Tab System implementation."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    try:
        from claude_multi_terminal.widgets.tab_item import Tab
        from claude_multi_terminal.widgets.tab_bar import TabBar
        from claude_multi_terminal.app import ClaudeMultiTerminalApp
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_tab_widget():
    """Test Tab widget creation and properties."""
    print("\nTesting Tab widget...")
    try:
        from claude_multi_terminal.widgets.tab_item import Tab

        # Create a tab
        tab = Tab(
            session_id="test-123",
            session_name="Test Session",
            is_active=True
        )

        assert tab.session_id == "test-123"
        assert tab.session_name == "Test Session"
        assert tab.is_active == True

        # Test render method
        rendered = tab.render()
        assert "Test Session" in str(rendered)
        assert "×" in str(rendered)  # Close button

        print("✓ Tab widget works correctly")
        return True
    except Exception as e:
        print(f"✗ Tab widget test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tab_bar_widget():
    """Test TabBar widget creation."""
    print("\nTesting TabBar widget...")
    try:
        from claude_multi_terminal.widgets.tab_bar import TabBar

        # Create a tab bar
        tab_bar = TabBar()

        assert tab_bar.tabs == []
        assert tab_bar.active_session_id is None

        print("✓ TabBar widget works correctly")
        return True
    except Exception as e:
        print(f"✗ TabBar widget test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_classes():
    """Test Tab message classes."""
    print("\nTesting Tab message classes...")
    try:
        from claude_multi_terminal.widgets.tab_item import Tab

        # Create a tab
        tab = Tab(
            session_id="test-123",
            session_name="Test Session"
        )

        # Test Clicked message
        clicked_msg = Tab.Clicked(tab, "test-123")
        assert clicked_msg.session_id == "test-123"
        assert clicked_msg.tab == tab

        # Test CloseRequested message
        close_msg = Tab.CloseRequested(tab, "test-123")
        assert close_msg.session_id == "test-123"
        assert close_msg.tab == tab

        print("✓ Tab message classes work correctly")
        return True
    except Exception as e:
        print(f"✗ Tab message classes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Tab System Implementation Tests")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Tab Widget", test_tab_widget()))
    results.append(("TabBar Widget", test_tab_bar_widget()))
    results.append(("Message Classes", test_message_classes()))

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(result[1] for result in results)

    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
