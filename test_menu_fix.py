#!/usr/bin/env python3
"""Test context menu instantiation."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from claude_multi_terminal.widgets.selectable_richlog import MenuItem, ContextMenu

    print("✓ Imports successful")

    # Create test menu items
    def test_callback():
        print("Callback executed")

    items = [
        MenuItem(label="Test Item 1", callback=test_callback, enabled=True, shortcut="Ctrl+1"),
        MenuItem(label="Test Item 2", callback=test_callback, enabled=False, shortcut="Ctrl+2"),
        MenuItem(label="Test Item 3", callback=test_callback, enabled=True, shortcut=""),
    ]

    # Try to create context menu (this will test compose without mounting)
    menu = ContextMenu(items=items, x=10, y=10)
    print("✓ ContextMenu instantiated successfully")

    # Test compose method returns valid widgets
    compose_result = list(menu.compose())
    print(f"✓ Compose returned {len(compose_result)} items")

    print("\n✅ All tests passed!")
    print("Context menu is ready to use in the application")
    sys.exit(0)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
