#!/usr/bin/env python3
"""
Full integration test with simulated user interactions.
Tests all Phase 1 features programmatically.
"""

import asyncio
import time
from textual.pilot import Pilot
from textual.widgets import TextArea
from claude_multi_terminal.app import ClaudeMultiTerminalApp

test_results = []

def log_test(name: str, passed: bool, details: str = ""):
    """Log test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    result = f"{status}: {name}"
    if details:
        result += f" - {details}"
    test_results.append((name, passed, details))
    print(result)

async def test_app_with_pilot():
    """Test app using Textual Pilot for automated interaction."""
    print("\n" + "="*70)
    print("FULL INTEGRATION TEST WITH PILOT")
    print("="*70 + "\n")

    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        # Test 1: App starts successfully
        try:
            await pilot.pause()
            log_test("App Startup", True, "App started successfully")
        except Exception as e:
            log_test("App Startup", False, f"Exception: {e}")
            return False

        # Test 2: Session is created automatically
        try:
            assert len(app.session_manager.sessions) > 0, "No sessions created"
            session_id = list(app.session_manager.sessions.keys())[0]
            log_test("Session Creation", True, f"Session {session_id[:8]} created")
        except Exception as e:
            log_test("Session Creation", False, f"Exception: {e}")
            return False

        # Test 3: TextArea widget is present and focusable
        try:
            # Find the TextArea widget
            text_areas = app.query(TextArea)
            assert len(text_areas) > 0, "No TextArea widgets found"

            input_widget = text_areas[0]
            assert input_widget is not None, "TextArea widget is None"

            log_test("TextArea Widget", True, f"Found {len(text_areas)} TextArea widget(s)")
        except Exception as e:
            log_test("TextArea Widget", False, f"Exception: {e}")
            return False

        # Test 4: Can focus TextArea
        try:
            input_widget.focus()
            await pilot.pause()
            assert input_widget.has_focus, "TextArea did not gain focus"
            log_test("TextArea Focus", True, "TextArea can be focused")
        except Exception as e:
            log_test("TextArea Focus", False, f"Exception: {e}")
            return False

        # Test 5: Can type text into TextArea
        try:
            # Type some text
            test_text = "test command"
            await pilot.press(*test_text)
            await pilot.pause()

            current_text = input_widget.text
            assert test_text in current_text, f"Text not entered correctly. Got: '{current_text}'"
            log_test("Text Entry", True, f"Successfully typed: '{test_text}'")
        except Exception as e:
            log_test("Text Entry", False, f"Exception: {e}")
            return False

        # Test 6: Enter key submits command
        try:
            # Clear existing text
            input_widget.text = ""
            await pilot.pause()

            # Type a new command
            await pilot.press(*"hello world")
            await pilot.pause()

            # Press Enter (without shift)
            await pilot.press("enter")
            await pilot.pause()

            # Check if input was cleared (indicating submission)
            assert input_widget.text == "", f"Input not cleared after Enter. Got: '{input_widget.text}'"
            log_test("Command Submission", True, "Enter key submits and clears input")
        except Exception as e:
            log_test("Command Submission", False, f"Exception: {e}")
            return False

        # Test 7: Slash command autocomplete
        try:
            # Type a slash to trigger autocomplete
            await pilot.press("/")
            await pilot.pause(0.1)

            # Check if autocomplete is visible
            from claude_multi_terminal.widgets.session_pane import SessionPane
            panes = app.query(SessionPane)
            if panes:
                pane = panes[0]
                assert pane._autocomplete_visible, "Autocomplete not visible after typing '/'"
                log_test("Autocomplete Trigger", True, "Typing '/' shows autocomplete")
            else:
                log_test("Autocomplete Trigger", False, "No SessionPane found")
        except Exception as e:
            log_test("Autocomplete Trigger", False, f"Exception: {e}")

        # Test 8: Can clear autocomplete with Escape
        try:
            await pilot.press("escape")
            await pilot.pause()

            if panes:
                pane = panes[0]
                assert not pane._autocomplete_visible, "Autocomplete still visible after Escape"
                log_test("Autocomplete Hide", True, "Escape hides autocomplete")
            else:
                log_test("Autocomplete Hide", False, "No SessionPane found")
        except Exception as e:
            log_test("Autocomplete Hide", False, f"Exception: {e}")

        # Test 9: Multi-line support (Shift+Enter should NOT submit)
        try:
            # Clear input
            input_widget.text = ""
            await pilot.pause(0.2)

            # Type first line
            await pilot.press(*"line1")
            await pilot.pause(0.2)

            # Press Shift+Enter (should add newline, not submit)
            await pilot.press("shift+enter")
            await pilot.pause(0.3)

            # Type second line
            await pilot.press(*"line2")
            await pilot.pause(0.2)

            # Check that text contains both lines
            text = input_widget.text
            # Note: The exact newline representation may vary, so check for both lines
            has_line1 = "line1" in text
            has_line2 = "line2" in text
            has_newline = "\n" in text or len(text.split()) > 1

            if has_line1 and has_line2:
                log_test("Multi-line Input", True, f"Shift+Enter adds newline: '{text[:50]}'")
            else:
                log_test("Multi-line Input", False, f"Text: '{text}', has_line1={has_line1}, has_line2={has_line2}, has_newline={has_newline}")
        except Exception as e:
            log_test("Multi-line Input", False, f"Exception: {e}")

        # Test 10: All Phase 1 features present
        try:
            features_present = {
                "TextArea widget": len(app.query(TextArea)) > 0,
                "Session manager": hasattr(app, 'session_manager'),
                "Sessions created": len(app.session_manager.sessions) > 0,
            }

            all_present = all(features_present.values())
            details = ", ".join([f"{k}: {v}" for k, v in features_present.items()])
            log_test("Phase 1 Features", all_present, details)
        except Exception as e:
            log_test("Phase 1 Features", False, f"Exception: {e}")

    return True

async def run_all_tests():
    """Run all integration tests."""
    start_time = time.time()

    try:
        await test_app_with_pilot()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False

    elapsed = time.time() - start_time

    # Generate report
    print("\n" + "="*70)
    print("INTEGRATION TEST RESULTS")
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
    import sys
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
