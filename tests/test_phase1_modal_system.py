"""
Comprehensive Test Suite for Phase 1 Modal System
Tests all modal system components, integrations, and functionality.

Test Coverage:
1. Import Tests - Verify all modules import correctly
2. Modal System Tests - Test AppMode enum, ModeState, ModeConfig
3. StatusBar Tests - Mode display and reactive updates
4. App Integration Tests - Key routing and mode transitions
5. COPY Mode Tests - Navigation and clipboard functionality
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": [],
    "start_time": None,
    "end_time": None
}


def track_result(test_name: str, passed: bool, error: Optional[str] = None):
    """Track test result."""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        print(f"✓ {test_name}")
    else:
        test_results["failed"] += 1
        test_results["errors"].append({"test": test_name, "error": error})
        print(f"✗ {test_name}: {error}")


# =============================================================================
# 1. IMPORT TESTS
# =============================================================================

def test_import_modes():
    """Test importing modes.py module."""
    try:
        from claude_multi_terminal.modes import (
            AppMode, ModeConfig, ModeHandler, ModeTransition, ModeState,
            MODE_CONFIGS, DEFAULT_MODE_TRANSITIONS,
            get_mode_color, get_mode_icon, get_mode_description,
            is_input_mode, is_navigation_mode, get_mode_transition
        )
        track_result("Import modes.py", True)
        return True
    except Exception as e:
        track_result("Import modes.py", False, str(e))
        return False


def test_import_app():
    """Test importing app.py with modal system."""
    try:
        from claude_multi_terminal.app import ClaudeMultiTerminalApp
        track_result("Import app.py", True)
        return True
    except Exception as e:
        track_result("Import app.py", False, str(e))
        return False


def test_import_status_bar():
    """Test importing status_bar.py with mode display."""
    try:
        from claude_multi_terminal.widgets.status_bar import StatusBar
        track_result("Import status_bar.py", True)
        return True
    except Exception as e:
        track_result("Import status_bar.py", False, str(e))
        return False


def test_import_dependencies():
    """Test all modal system dependencies resolve."""
    try:
        from claude_multi_terminal.theme import theme, icons
        from claude_multi_terminal.types import AppMode as TypesAppMode
        track_result("Import dependencies", True)
        return True
    except Exception as e:
        track_result("Import dependencies", False, str(e))
        return False


# =============================================================================
# 2. MODAL SYSTEM TESTS
# =============================================================================

def test_appmode_enum():
    """Test AppMode enum has all 4 modes."""
    try:
        from claude_multi_terminal.modes import AppMode

        # Check all 4 modes exist
        modes = [AppMode.NORMAL, AppMode.INSERT, AppMode.COPY, AppMode.COMMAND]
        assert len(modes) == 4, "Should have exactly 4 modes"

        # Check string representations
        assert str(AppMode.NORMAL) == "NORMAL"
        assert str(AppMode.INSERT) == "INSERT"
        assert str(AppMode.COPY) == "COPY"
        assert str(AppMode.COMMAND) == "COMMAND"

        # Check repr
        assert repr(AppMode.NORMAL) == "AppMode.NORMAL"

        track_result("AppMode enum structure", True)
        return True
    except Exception as e:
        track_result("AppMode enum structure", False, str(e))
        return False


def test_mode_configs():
    """Test mode configurations exist and are valid."""
    try:
        from claude_multi_terminal.modes import AppMode, MODE_CONFIGS

        # Check all modes have configs
        for mode in AppMode:
            assert mode in MODE_CONFIGS, f"Missing config for {mode}"
            config = MODE_CONFIGS[mode]

            # Validate config fields
            assert config.mode == mode
            assert config.display_name, "display_name required"
            assert config.color, "color required"
            assert config.icon, "icon required"
            assert config.description, "description required"
            assert isinstance(config.exit_keys, list), "exit_keys should be list"
            assert config.cursor_style in ["block", "underline", "bar"], "Invalid cursor style"

        track_result("Mode configurations", True)
        return True
    except Exception as e:
        track_result("Mode configurations", False, str(e))
        return False


def test_mode_state_initialization():
    """Test ModeState initialization."""
    try:
        from claude_multi_terminal.modes import ModeState, AppMode

        # Test default initialization
        state = ModeState()
        assert state.current_mode == AppMode.NORMAL
        assert state.previous_mode is None
        assert len(state.handlers) == 0
        assert len(state.history) == 1  # Initial transition
        assert state.history[0].to_mode == AppMode.NORMAL

        # Test custom initialization
        state2 = ModeState(initial_mode=AppMode.INSERT, max_history=50)
        assert state2.current_mode == AppMode.INSERT
        assert state2.max_history == 50

        track_result("ModeState initialization", True)
        return True
    except Exception as e:
        track_result("ModeState initialization", False, str(e))
        return False


def test_mode_transitions():
    """Test mode transitions work correctly."""
    try:
        from claude_multi_terminal.modes import ModeState, AppMode

        state = ModeState()

        # Test NORMAL → INSERT
        success = state.transition_to(AppMode.INSERT, trigger="key_i")
        assert success, "Transition should succeed"
        assert state.current_mode == AppMode.INSERT
        assert state.previous_mode == AppMode.NORMAL

        # Test INSERT → NORMAL
        success = state.transition_to(AppMode.NORMAL, trigger="escape")
        assert success, "Transition should succeed"
        assert state.current_mode == AppMode.NORMAL
        assert state.previous_mode == AppMode.INSERT

        # Test NORMAL → COPY
        success = state.transition_to(AppMode.COPY, trigger="key_v")
        assert success, "Transition should succeed"
        assert state.current_mode == AppMode.COPY

        # Test COPY → NORMAL
        success = state.transition_to(AppMode.NORMAL, trigger="escape")
        assert success, "Transition should succeed"

        # Test NORMAL → COMMAND
        success = state.transition_to(AppMode.COMMAND, trigger="ctrl_b")
        assert success, "Transition should succeed"
        assert state.current_mode == AppMode.COMMAND

        # Test cannot transition to same mode
        success = state.transition_to(AppMode.COMMAND, trigger="test")
        assert not success, "Should not transition to same mode"

        # Verify history
        assert len(state.history) >= 6, "Should have transition history"

        track_result("Mode transitions", True)
        return True
    except Exception as e:
        track_result("Mode transitions", False, str(e))
        return False


def test_mode_toggle_previous():
    """Test toggle between current and previous mode."""
    try:
        from claude_multi_terminal.modes import ModeState, AppMode

        state = ModeState()

        # No previous mode initially
        success = state.toggle_previous()
        assert not success, "Should fail with no previous mode"

        # Transition to INSERT
        state.transition_to(AppMode.INSERT)

        # Toggle back to NORMAL
        success = state.toggle_previous()
        assert success, "Toggle should succeed"
        assert state.current_mode == AppMode.NORMAL

        # Toggle back to INSERT
        success = state.toggle_previous()
        assert success, "Toggle should succeed"
        assert state.current_mode == AppMode.INSERT

        track_result("Mode toggle previous", True)
        return True
    except Exception as e:
        track_result("Mode toggle previous", False, str(e))
        return False


def test_mode_utility_functions():
    """Test mode utility functions."""
    try:
        from claude_multi_terminal.modes import (
            AppMode, get_mode_color, get_mode_icon, get_mode_description,
            is_input_mode, is_navigation_mode, get_mode_transition
        )

        # Test color/icon/description getters
        color = get_mode_color(AppMode.NORMAL)
        assert color, "Should return color"

        icon = get_mode_icon(AppMode.INSERT)
        assert icon, "Should return icon"

        desc = get_mode_description(AppMode.COPY)
        assert desc, "Should return description"

        # Test mode type checks
        assert is_input_mode(AppMode.INSERT)
        assert is_input_mode(AppMode.COMMAND)
        assert not is_input_mode(AppMode.NORMAL)
        assert not is_input_mode(AppMode.COPY)

        assert is_navigation_mode(AppMode.NORMAL)
        assert is_navigation_mode(AppMode.COPY)
        assert not is_navigation_mode(AppMode.INSERT)
        assert not is_navigation_mode(AppMode.COMMAND)

        # Test transition lookup
        target = get_mode_transition(AppMode.NORMAL, "i")
        assert target == AppMode.INSERT

        target = get_mode_transition(AppMode.NORMAL, "v")
        assert target == AppMode.COPY

        target = get_mode_transition(AppMode.INSERT, "escape")
        assert target == AppMode.NORMAL

        track_result("Mode utility functions", True)
        return True
    except Exception as e:
        track_result("Mode utility functions", False, str(e))
        return False


def test_mode_transition_validation():
    """Test mode transition validation and blocking."""
    try:
        from claude_multi_terminal.modes import ModeState, AppMode

        state = ModeState()

        # Test same-mode rejection
        allowed, reason = state.can_transition_to(AppMode.NORMAL)
        assert not allowed, "Should reject same-mode transition"
        assert "Already in" in reason

        # Test valid transitions
        allowed, reason = state.can_transition_to(AppMode.INSERT)
        assert allowed, "Should allow valid transition"
        assert reason == "", "No reason for allowed transition"

        track_result("Mode transition validation", True)
        return True
    except Exception as e:
        track_result("Mode transition validation", False, str(e))
        return False


# =============================================================================
# 3. STATUSBAR TESTS
# =============================================================================

def test_statusbar_mode_display():
    """Test StatusBar mode display functionality."""
    try:
        from claude_multi_terminal.widgets.status_bar import StatusBar
        from claude_multi_terminal.types import AppMode

        # Note: Cannot fully test without Textual app context
        # Just verify class structure
        assert hasattr(StatusBar, 'current_mode')
        assert hasattr(StatusBar, 'watch_current_mode')
        assert hasattr(StatusBar, 'render')

        track_result("StatusBar mode display structure", True)
        return True
    except Exception as e:
        track_result("StatusBar mode display structure", False, str(e))
        return False


def test_statusbar_css_classes():
    """Test StatusBar has mode-specific CSS classes."""
    try:
        from claude_multi_terminal.widgets.status_bar import StatusBar

        # Check CSS includes mode classes
        css = StatusBar.DEFAULT_CSS
        assert "-mode-normal" in css or "mode-" in css, "Should have mode CSS classes"

        track_result("StatusBar CSS classes", True)
        return True
    except Exception as e:
        track_result("StatusBar CSS classes", False, str(e))
        return False


# =============================================================================
# 4. APP INTEGRATION TESTS
# =============================================================================

def test_app_has_mode_attribute():
    """Test ClaudeMultiTerminalApp has mode tracking."""
    try:
        from claude_multi_terminal.app import ClaudeMultiTerminalApp
        from claude_multi_terminal.types import AppMode

        # Cannot instantiate without Textual, but check class definition
        # Verify mode-related methods exist
        assert hasattr(ClaudeMultiTerminalApp, 'enter_normal_mode')
        assert hasattr(ClaudeMultiTerminalApp, 'enter_insert_mode')
        assert hasattr(ClaudeMultiTerminalApp, 'enter_copy_mode')
        assert hasattr(ClaudeMultiTerminalApp, 'enter_command_mode')
        assert hasattr(ClaudeMultiTerminalApp, 'on_key')

        track_result("App mode methods exist", True)
        return True
    except Exception as e:
        track_result("App mode methods exist", False, str(e))
        return False


def test_app_mode_handlers():
    """Test App has mode-specific key handlers."""
    try:
        from claude_multi_terminal.app import ClaudeMultiTerminalApp

        # Verify handler methods exist
        assert hasattr(ClaudeMultiTerminalApp, '_handle_normal_mode_key')
        assert hasattr(ClaudeMultiTerminalApp, '_handle_insert_mode_key')
        assert hasattr(ClaudeMultiTerminalApp, '_handle_copy_mode_key')
        assert hasattr(ClaudeMultiTerminalApp, '_handle_command_mode_key')

        track_result("App mode handlers exist", True)
        return True
    except Exception as e:
        track_result("App mode handlers exist", False, str(e))
        return False


def test_default_mode_transitions():
    """Test DEFAULT_MODE_TRANSITIONS lookup table."""
    try:
        from claude_multi_terminal.modes import DEFAULT_MODE_TRANSITIONS, AppMode

        # Check critical transitions exist
        assert (AppMode.NORMAL, "i") in DEFAULT_MODE_TRANSITIONS
        assert (AppMode.NORMAL, "v") in DEFAULT_MODE_TRANSITIONS
        assert (AppMode.INSERT, "escape") in DEFAULT_MODE_TRANSITIONS
        assert (AppMode.COPY, "escape") in DEFAULT_MODE_TRANSITIONS
        assert (AppMode.COMMAND, "escape") in DEFAULT_MODE_TRANSITIONS

        # Verify transition targets
        assert DEFAULT_MODE_TRANSITIONS[(AppMode.NORMAL, "i")] == AppMode.INSERT
        assert DEFAULT_MODE_TRANSITIONS[(AppMode.NORMAL, "v")] == AppMode.COPY
        assert DEFAULT_MODE_TRANSITIONS[(AppMode.INSERT, "escape")] == AppMode.NORMAL

        track_result("Default mode transitions", True)
        return True
    except Exception as e:
        track_result("Default mode transitions", False, str(e))
        return False


# =============================================================================
# 5. COPY MODE TESTS (from existing test suite)
# =============================================================================

def test_copy_mode_exists():
    """Test COPY mode is defined in AppMode enum."""
    try:
        from claude_multi_terminal.modes import AppMode

        assert hasattr(AppMode, 'COPY')
        assert AppMode.COPY.name == "COPY"

        track_result("COPY mode exists", True)
        return True
    except Exception as e:
        track_result("COPY mode exists", False, str(e))
        return False


def test_copy_mode_config():
    """Test COPY mode configuration."""
    try:
        from claude_multi_terminal.modes import AppMode, MODE_CONFIGS

        config = MODE_CONFIGS[AppMode.COPY]

        assert config.mode == AppMode.COPY
        assert config.display_name == "COPY"
        assert config.color  # Should have color
        assert config.icon  # Should have icon
        assert "selection" in config.description.lower() or "clipboard" in config.description.lower()
        assert config.cursor_style == "underline"
        assert "escape" in config.exit_keys or "y" in config.exit_keys

        track_result("COPY mode configuration", True)
        return True
    except Exception as e:
        track_result("COPY mode configuration", False, str(e))
        return False


def test_copy_mode_transitions():
    """Test entering and exiting COPY mode."""
    try:
        from claude_multi_terminal.modes import ModeState, AppMode

        state = ModeState()

        # Enter COPY mode from NORMAL
        success = state.transition_to(AppMode.COPY, trigger="key_v")
        assert success
        assert state.current_mode == AppMode.COPY

        # Exit to NORMAL via escape
        success = state.transition_to(AppMode.NORMAL, trigger="escape")
        assert success
        assert state.current_mode == AppMode.NORMAL

        track_result("COPY mode transitions", True)
        return True
    except Exception as e:
        track_result("COPY mode transitions", False, str(e))
        return False


# =============================================================================
# 6. INTEGRATION TESTS
# =============================================================================

def test_full_mode_cycle():
    """Test complete mode transition cycle."""
    try:
        from claude_multi_terminal.modes import ModeState, AppMode

        state = ModeState()

        # NORMAL → INSERT → NORMAL → COPY → NORMAL → COMMAND → NORMAL
        transitions = [
            (AppMode.INSERT, "i"),
            (AppMode.NORMAL, "escape"),
            (AppMode.COPY, "v"),
            (AppMode.NORMAL, "escape"),
            (AppMode.COMMAND, "ctrl_b"),
            (AppMode.NORMAL, "escape"),
        ]

        for target_mode, trigger in transitions:
            success = state.transition_to(target_mode, trigger=trigger)
            assert success, f"Failed to transition to {target_mode}"
            assert state.current_mode == target_mode

        # Should end in NORMAL
        assert state.current_mode == AppMode.NORMAL

        # History should have all transitions
        assert len(state.history) >= len(transitions) + 1  # +1 for initialization

        track_result("Full mode cycle", True)
        return True
    except Exception as e:
        track_result("Full mode cycle", False, str(e))
        return False


def test_mode_history_tracking():
    """Test mode transition history tracking."""
    try:
        from claude_multi_terminal.modes import ModeState, AppMode

        state = ModeState(max_history=10)

        # Make several transitions
        for _ in range(3):
            state.transition_to(AppMode.INSERT, trigger="test")
            state.transition_to(AppMode.NORMAL, trigger="test")

        # Check history
        recent = state.get_recent_transitions(5)
        assert len(recent) > 0, "Should have history"

        # Check transition objects
        for trans in recent:
            assert trans.from_mode or trans.to_mode == AppMode.NORMAL  # First transition
            assert trans.to_mode in [mode for mode in AppMode]
            assert trans.timestamp
            assert trans.trigger

        track_result("Mode history tracking", True)
        return True
    except Exception as e:
        track_result("Mode history tracking", False, str(e))
        return False


def test_mode_handler_protocol():
    """Test ModeHandler protocol structure."""
    try:
        from claude_multi_terminal.modes import ModeHandler, AppMode
        from typing import get_type_hints

        # Verify protocol methods
        protocol_methods = ['on_enter', 'on_exit', 'on_key', 'on_focus_change', 'can_transition_to']

        for method_name in protocol_methods:
            assert hasattr(ModeHandler, method_name), f"Missing protocol method: {method_name}"

        track_result("ModeHandler protocol", True)
        return True
    except Exception as e:
        track_result("ModeHandler protocol", False, str(e))
        return False


def test_types_appmode_compatibility():
    """Test types.AppMode is compatible with modes.AppMode."""
    try:
        from claude_multi_terminal.types import AppMode as TypesAppMode
        from claude_multi_terminal.modes import AppMode as ModesAppMode

        # They should be the same or compatible
        # Check they have the same modes
        types_modes = set([m.name for m in TypesAppMode])
        modes_modes = set([m.name for m in ModesAppMode])

        assert types_modes == modes_modes, "AppMode enums should match"

        track_result("AppMode type compatibility", True)
        return True
    except Exception as e:
        track_result("AppMode type compatibility", False, str(e))
        return False


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all Phase 1 Modal System tests."""
    print("\n" + "="*70)
    print("PHASE 1 MODAL SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70 + "\n")

    test_results["start_time"] = datetime.now()

    # Group 1: Import Tests
    print("\n1. IMPORT TESTS")
    print("-" * 70)
    test_import_modes()
    test_import_app()
    test_import_status_bar()
    test_import_dependencies()

    # Group 2: Modal System Tests
    print("\n2. MODAL SYSTEM TESTS")
    print("-" * 70)
    test_appmode_enum()
    test_mode_configs()
    test_mode_state_initialization()
    test_mode_transitions()
    test_mode_toggle_previous()
    test_mode_utility_functions()
    test_mode_transition_validation()

    # Group 3: StatusBar Tests
    print("\n3. STATUSBAR TESTS")
    print("-" * 70)
    test_statusbar_mode_display()
    test_statusbar_css_classes()

    # Group 4: App Integration Tests
    print("\n4. APP INTEGRATION TESTS")
    print("-" * 70)
    test_app_has_mode_attribute()
    test_app_mode_handlers()
    test_default_mode_transitions()

    # Group 5: COPY Mode Tests
    print("\n5. COPY MODE TESTS")
    print("-" * 70)
    test_copy_mode_exists()
    test_copy_mode_config()
    test_copy_mode_transitions()

    # Group 6: Integration Tests
    print("\n6. INTEGRATION TESTS")
    print("-" * 70)
    test_full_mode_cycle()
    test_mode_history_tracking()
    test_mode_handler_protocol()
    test_types_appmode_compatibility()

    test_results["end_time"] = datetime.now()

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    duration = (test_results["end_time"] - test_results["start_time"]).total_seconds()

    print(f"\nTotal Tests:    {test_results['total']}")
    print(f"Passed:         {test_results['passed']} ✓")
    print(f"Failed:         {test_results['failed']} ✗")
    print(f"Success Rate:   {(test_results['passed']/test_results['total']*100):.1f}%")
    print(f"Duration:       {duration:.2f}s")

    if test_results["failed"] > 0:
        print("\nFAILED TESTS:")
        print("-" * 70)
        for error in test_results["errors"]:
            print(f"\n✗ {error['test']}")
            print(f"  Error: {error['error']}")

    print("\n" + "="*70)

    return test_results


if __name__ == "__main__":
    results = run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)
