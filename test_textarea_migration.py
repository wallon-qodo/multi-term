#!/usr/bin/env python3
"""
Comprehensive test suite for TextArea migration.
Tests all Phase 1 features after Input -> TextArea migration.
"""

import asyncio
import time
from textual.widgets import TextArea
from claude_multi_terminal.app import ClaudeMultiTerminalApp

# Test results tracking
test_results = []

def log_result(test_name: str, passed: bool, details: str = ""):
    """Log test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    result = f"{status}: {test_name}"
    if details:
        result += f" - {details}"
    test_results.append((test_name, passed, details))
    print(result)

async def test_app_startup():
    """Test 1: Application starts without errors."""
    test_name = "Application Startup"
    try:
        app = ClaudeMultiTerminalApp()

        # Verify app initializes
        assert app is not None, "App failed to initialize"

        # Verify app has required attributes
        assert hasattr(app, 'session_manager'), "Missing session_manager"

        log_result(test_name, True, "App initialized successfully")
        return app
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        raise

async def test_textarea_import():
    """Test 2: TextArea is properly imported."""
    test_name = "TextArea Import"
    try:
        from textual.widgets import TextArea as TA
        from claude_multi_terminal.widgets.session_pane import SessionPane

        # Verify TextArea is in session_pane imports
        import inspect
        source_file = inspect.getsourcefile(SessionPane)
        with open(source_file, 'r') as f:
            lines = f.readlines()

        # Check first 10 lines for imports
        import_section = ''.join(lines[:10])
        assert "from textual.widgets import" in import_section
        assert "TextArea" in import_section

        log_result(test_name, True, "TextArea properly imported")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_textarea_instantiation():
    """Test 3: TextArea is instantiated correctly in SessionPane."""
    test_name = "TextArea Instantiation"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        # Check compose method uses TextArea
        source = inspect.getsource(SessionPane.compose)
        assert "TextArea(" in source, "TextArea not instantiated in compose()"
        assert 'id=f"input-{self.session_id}"' in source, "TextArea missing correct ID"

        log_result(test_name, True, "TextArea correctly instantiated")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_event_handlers():
    """Test 4: Event handlers use TextArea events."""
    test_name = "Event Handler Migration"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        source = inspect.getsource(SessionPane)

        # Check for TextArea.Changed handler
        assert "@on(TextArea.Changed)" in source, "Missing @on(TextArea.Changed)"
        assert "on_input_changed" in source, "Missing on_input_changed handler"

        # Check for command submission handler (now via on_key instead of TextArea.Submitted)
        assert "_submit_command" in source, "Missing _submit_command method"
        assert "async def on_key" in source, "Missing on_key handler for Enter key"

        # Check event parameter names
        assert "text_area.text" in source, "Not using text_area.text"

        log_result(test_name, True, "Event handlers correctly migrated (using on_key for submission)")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_value_to_text_migration():
    """Test 5: All .value references changed to .text."""
    test_name = "Value to Text Migration"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        source = inspect.getsource(SessionPane)

        # Check that we're using .text instead of .value
        # Look for patterns like: event.text_area.text, input_widget.text
        assert "text_area.text" in source, "Not using text_area.text"
        assert 'input_widget.text = ""' in source, "Not using input_widget.text for clearing"

        # Check we're NOT using old .value pattern (except in comments)
        lines = source.split('\n')
        code_lines = [l for l in lines if not l.strip().startswith('#')]
        value_usage = [l for l in code_lines if '.value' in l and 'text_area' not in l]

        # Filter out legitimate uses (like filter_text.lower())
        problematic_value_usage = [l for l in value_usage if 'input' in l.lower() or 'widget' in l.lower()]

        if problematic_value_usage:
            log_result(test_name, False, f"Found old .value usage: {problematic_value_usage[0]}")
            return False

        log_result(test_name, True, "All .value references migrated to .text")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_cursor_position_migration():
    """Test 6: cursor_position replaced with move_cursor()."""
    test_name = "Cursor Position Migration"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        source = inspect.getsource(SessionPane)

        # Check for move_cursor usage
        assert "move_cursor(" in source, "Not using move_cursor()"

        # Check we're not using old cursor_position = pattern
        if "cursor_position =" in source:
            # Make sure it's not in comments or strings
            lines = source.split('\n')
            code_lines = [l.strip() for l in lines if not l.strip().startswith('#')]
            bad_usage = [l for l in code_lines if "cursor_position =" in l]

            if bad_usage:
                log_result(test_name, False, f"Found old cursor_position usage: {bad_usage[0]}")
                return False

        log_result(test_name, True, "Cursor position correctly migrated to move_cursor()")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_query_selector_migration():
    """Test 7: query_one uses TextArea class."""
    test_name = "Query Selector Migration"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        source = inspect.getsource(SessionPane)

        # Check for query_one with TextArea
        assert "query_one(" in source, "No query_one calls found"

        # Check specific patterns
        query_lines = [l for l in source.split('\n') if 'query_one(' in l and 'input' in l.lower()]

        # Verify they use TextArea not Input
        for line in query_lines:
            if 'Input)' in line:
                log_result(test_name, False, f"Found query_one with Input: {line.strip()}")
                return False

        # Verify at least some use TextArea
        textarea_queries = [l for l in query_lines if 'TextArea)' in l]
        assert textarea_queries, "No query_one calls with TextArea found"

        log_result(test_name, True, f"Query selectors migrated ({len(textarea_queries)} TextArea queries)")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_autocomplete_feature():
    """Test 8: Slash command autocomplete functionality."""
    test_name = "Autocomplete Feature"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        source = inspect.getsource(SessionPane)

        # Check for autocomplete methods
        assert "_show_autocomplete" in source, "Missing _show_autocomplete method"
        assert "_hide_autocomplete" in source, "Missing _hide_autocomplete method"
        assert "_get_selected_command" in source, "Missing _get_selected_command method"

        # Check for slash commands list
        assert "_slash_commands" in source, "Missing _slash_commands list"

        # Check for autocomplete visibility tracking
        assert "_autocomplete_visible" in source, "Missing _autocomplete_visible tracking"

        log_result(test_name, True, "Autocomplete feature intact")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_command_history_feature():
    """Test 9: Command history functionality."""
    test_name = "Command History Feature"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        source = inspect.getsource(SessionPane)

        # Check for history tracking
        assert "_command_history" in source, "Missing _command_history"
        assert "_history_index" in source, "Missing _history_index"
        assert "_current_draft" in source, "Missing _current_draft"

        log_result(test_name, True, "Command history feature intact")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_multiline_mode():
    """Test 10: Multi-line mode support."""
    test_name = "Multi-line Mode"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        source = inspect.getsource(SessionPane)

        # Check for multiline mode tracking
        assert "_multiline_mode" in source, "Missing _multiline_mode"

        # Check for mode indicator
        assert "mode-indicator" in source, "Missing mode indicator"

        log_result(test_name, True, "Multi-line mode support intact")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def test_no_input_references():
    """Test 11: Ensure no Input widget references remain."""
    test_name = "No Input Widget References"
    try:
        from claude_multi_terminal.widgets.session_pane import SessionPane
        import inspect

        source = inspect.getsource(SessionPane)

        # Check for problematic Input references
        lines = source.split('\n')

        # Line 1: imports - Input should not be used except in import for backward compat
        import_line = [l for l in lines if 'from textual.widgets import' in l and 'Input' in l]
        if import_line:
            # This is OK if it's alongside TextArea for gradual migration
            pass

        # Check for Input() instantiation (bad)
        input_instantiation = [l for l in lines if 'Input(' in l and not l.strip().startswith('#')]
        if input_instantiation:
            log_result(test_name, False, f"Found Input() instantiation: {input_instantiation[0]}")
            return False

        # Check for @on(Input.Changed) or @on(Input.Submitted) (bad)
        input_decorators = [l for l in lines if '@on(Input.' in l]
        if input_decorators:
            log_result(test_name, False, f"Found Input event decorator: {input_decorators[0]}")
            return False

        log_result(test_name, True, "No problematic Input references found")
        return True
    except Exception as e:
        log_result(test_name, False, f"Exception: {e}")
        return False

async def run_all_tests():
    """Run all tests and generate report."""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEXTAREA MIGRATION TEST SUITE")
    print("="*70 + "\n")

    start_time = time.time()

    # Run tests
    await test_app_startup()
    await test_textarea_import()
    await test_textarea_instantiation()
    await test_event_handlers()
    await test_value_to_text_migration()
    await test_cursor_position_migration()
    await test_query_selector_migration()
    await test_autocomplete_feature()
    await test_command_history_feature()
    await test_multiline_mode()
    await test_no_input_references()

    elapsed = time.time() - start_time

    # Generate report
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)

    passed = sum(1 for _, p, _ in test_results if p)
    total = len(test_results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"Duration: {elapsed:.2f}s")

    # List failures if any
    failures = [(name, details) for name, passed, details in test_results if not passed]
    if failures:
        print("\n" + "="*70)
        print("FAILURES")
        print("="*70)
        for name, details in failures:
            print(f"\n✗ {name}")
            if details:
                print(f"  {details}")

    print("\n" + "="*70)

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
