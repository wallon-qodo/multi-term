#!/usr/bin/env python3
"""
Quick smoke test to verify the application is ready to run.
This is a fast pre-flight check before launching the TUI.
"""

import sys
import os

sys.path.insert(0, '/Users/wallonwalusayi/claude-multi-terminal')

print("=" * 70)
print("CLAUDE MULTI-TERMINAL - SMOKE TEST")
print("=" * 70)

# Test 1: Python version
print("\n1. Python Version Check")
print(f"   Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
if sys.version_info >= (3, 10):
    print("   ✅ Python version OK (3.10+)")
else:
    print("   ❌ Python version too old (need 3.10+)")
    sys.exit(1)

# Test 2: Required imports
print("\n2. Module Import Check")
required_modules = [
    ('textual', 'Textual TUI framework'),
    ('ptyprocess', 'PTY process management'),
    ('rich', 'Terminal formatting'),
]

all_imports_ok = True
for module_name, description in required_modules:
    try:
        __import__(module_name)
        print(f"   ✅ {module_name:12} - {description}")
    except ImportError as e:
        print(f"   ❌ {module_name:12} - MISSING ({e})")
        all_imports_ok = False

if not all_imports_ok:
    print("\n   Install missing modules:")
    print("   pip install -e .")
    sys.exit(1)

# Test 3: Application imports
print("\n3. Application Import Check")
try:
    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    from claude_multi_terminal.core.session_manager import SessionManager
    from claude_multi_terminal.config import Config
    print("   ✅ Application modules import successfully")
except ImportError as e:
    print(f"   ❌ Application import failed: {e}")
    sys.exit(1)

# Test 4: Claude CLI check
print("\n4. Claude CLI Check")
if os.path.exists(Config.CLAUDE_PATH):
    print(f"   ✅ Claude CLI found at {Config.CLAUDE_PATH}")
else:
    print(f"   ❌ Claude CLI NOT found at {Config.CLAUDE_PATH}")
    print("   Install Claude CLI: https://claude.ai/download")
    sys.exit(1)

# Test 5: TTY check
print("\n5. Terminal Check")
if sys.stdin.isatty():
    print("   ✅ Running in a TTY (terminal)")
else:
    print("   ⚠️  Not running in a TTY (may not work correctly)")

# Test 6: Quick session test
print("\n6. Quick Session Test")
import asyncio

async def quick_test():
    session_mgr = SessionManager(claude_path=Config.CLAUDE_PATH)
    try:
        session_id = session_mgr.create_session(name="Smoke Test")
        session = session_mgr.sessions[session_id]

        # Check PTY is alive
        if session.pty_handler.process and session.pty_handler.process.isalive():
            print("   ✅ PTY process spawned successfully")

            # Quick read test
            output_received = []

            def capture(output):
                output_received.append(output)

            await session.pty_handler.start_reading(callback=capture)
            await asyncio.sleep(1.5)

            if output_received:
                print(f"   ✅ PTY output received ({len(output_received)} chunks)")
            else:
                print("   ⚠️  No output received (may need longer wait)")

            await session_mgr.terminate_session(session_id)
            print("   ✅ Session terminated cleanly")
            return True
        else:
            print("   ❌ PTY process failed to start")
            return False
    except Exception as e:
        print(f"   ❌ Session test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

test_result = asyncio.run(quick_test())

if not test_result:
    sys.exit(1)

# Test 7: Config validation
print("\n7. Configuration Check")
print(f"   Default Sessions: {Config.DEFAULT_SESSION_COUNT}")
print(f"   Max Sessions:     {Config.MAX_SESSIONS}")
print(f"   PTY Size:         {Config.PTY_ROWS}x{Config.PTY_COLS}")
print(f"   Terminal Type:    {Config.TERM_TYPE}")
print("   ✅ Configuration loaded")

# All tests passed
print("\n" + "=" * 70)
print("SMOKE TEST RESULTS")
print("=" * 70)
print("""
✅ All smoke tests passed!

The application is ready to launch.

To start the application:
  python LAUNCH.py

Or directly:
  python -m claude_multi_terminal

Expected behavior:
  - App launches with 2 session panes
  - Each pane shows Claude's welcome message
  - You can type commands and see responses
  - Press Ctrl+Q to quit

Keyboard shortcuts:
  Tab         - Switch between panes
  Ctrl+N      - New session
  Ctrl+W      - Close session
  Ctrl+B      - Toggle broadcast mode
  Ctrl+C      - Copy output
  F2          - Toggle mouse mode (for text selection)
  Ctrl+Q      - Quit

For detailed test results, see: TEST_REPORT.md
""")

print("=" * 70)
print("Ready to launch! Press Enter to continue...")
try:
    input()
except KeyboardInterrupt:
    print("\nCancelled.")
    sys.exit(0)

print("\nLaunching Claude Multi-Terminal...")
print("=" * 70)

# Launch the app
try:
    app = ClaudeMultiTerminalApp()
    app.run()
    print("\n✅ Application exited normally")
except KeyboardInterrupt:
    print("\n✅ Application interrupted by user")
except Exception as e:
    print(f"\n❌ Application crashed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
