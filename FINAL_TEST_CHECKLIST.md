# Final Test Checklist - Claude Multi-Terminal

This checklist can be used for final manual verification before releasing or deploying the application.

---

## Pre-Launch Automated Tests

Run these scripts to verify the application is ready:

### 1. Smoke Test (Quick Pre-flight)
```bash
source venv/bin/activate
python smoke_test.py
```
**Expected:** All 7 checks pass, session spawns successfully

### 2. Component Tests
```bash
python test_tui_comprehensive.py
```
**Expected:** All 7 phases pass (imports, config, session manager, widgets, app, flags, ANSI)

### 3. Integration Tests
```bash
python test_integration_simulated.py
```
**Expected:** All 6 tests pass (multi-session creation, initial output, command responses, rapid commands, independence, termination)

### 4. Stress Tests
```bash
python test_stress_and_edge_cases.py
```
**Expected:** All 8 tests pass (large output, rapid creation, empty commands, special chars, concurrent writes, lifecycle, memory, ANSI)

### 5. User Scenarios
```bash
python test_user_scenario.py
```
**Expected:** All 5 scenarios pass (basic workflow, multiple panes, broadcast, rapid switching, text selection)

---

## Manual Interactive Testing

### Launch Verification

- [ ] **Test:** Run `python LAUNCH.py` or `python -m claude_multi_terminal`
- [ ] **Expected:** Application launches without errors
- [ ] **Expected:** Screen clears and shows TUI interface
- [ ] **Expected:** 2 session panes appear side-by-side

### Visual Rendering

- [ ] **Test:** Observe the UI layout
- [ ] **Expected:** Split panes have visible borders
- [ ] **Expected:** Session headers show names
- [ ] **Expected:** Box drawing characters are correct (not �)
- [ ] **Expected:** Input fields are visible at bottom of each pane

### Initial Output

- [ ] **Test:** Wait 2-3 seconds after launch
- [ ] **Expected:** Each pane shows Claude welcome message
- [ ] **Expected:** Green "SESSION STARTED" box appears
- [ ] **Expected:** Session headers update to show "[X updates]"
- [ ] **Expected:** No error messages or raw ANSI codes visible

### Command Submission - Session 1

- [ ] **Test:** Type `hello` in session 1, press Enter
- [ ] **Expected:** Cyan command separator box appears with timestamp
- [ ] **Expected:** Command is echoed in the box
- [ ] **Expected:** "Response:" header appears
- [ ] **Expected:** Claude responds with a greeting (within 1-3 seconds)
- [ ] **Expected:** After 2 seconds of silence, "Response complete" marker appears
- [ ] **Expected:** No raw escape sequences visible

### Pane Switching

- [ ] **Test:** Press Tab key
- [ ] **Expected:** Focus moves to session 2
- [ ] **Expected:** Session 2 border changes to double line
- [ ] **Expected:** Session 1 border returns to single line
- [ ] **Expected:** Cursor appears in session 2 input field

### Command Submission - Session 2

- [ ] **Test:** Type `pwd` in session 2, press Enter
- [ ] **Expected:** Command separator appears
- [ ] **Expected:** Current directory path is shown in response
- [ ] **Expected:** Output is visible and readable
- [ ] **Expected:** Response complete marker appears

### Independence Test

- [ ] **Test:** Send different commands to each session
- [ ] **Expected:** Each session shows only its own command output
- [ ] **Expected:** Commands don't leak between sessions
- [ ] **Expected:** Session headers update independently

### Broadcast Mode

- [ ] **Test:** Press Ctrl+B
- [ ] **Expected:** Notification appears: "Broadcast mode: ON"
- [ ] **Expected:** Status bar shows broadcast indicator (if visible)
- [ ] **Test:** Type `echo Broadcast test`, press Enter
- [ ] **Expected:** Command is sent to ALL sessions
- [ ] **Expected:** All sessions show the echo output
- [ ] **Test:** Press Ctrl+B again
- [ ] **Expected:** Notification appears: "Broadcast mode: OFF"

### Text Copying - Ctrl+C Method

- [ ] **Test:** Focus a session with output
- [ ] **Test:** Press Ctrl+C
- [ ] **Expected:** Notification appears showing byte count copied
- [ ] **Test:** Paste into another application (Cmd+V)
- [ ] **Expected:** Output text is pasted correctly

### Text Copying - F2 Method

- [ ] **Test:** Press F2
- [ ] **Expected:** Notification: "Mouse mode: OFF"
- [ ] **Expected:** Second notification: "You can now click and drag to select text"
- [ ] **Test:** Click and drag to select text in output pane
- [ ] **Expected:** Text is highlighted by terminal
- [ ] **Test:** Cmd+C to copy selected text
- [ ] **Expected:** Selected text copied to clipboard
- [ ] **Test:** Press F2 again
- [ ] **Expected:** Notification: "Mouse mode: ON"

### New Session

- [ ] **Test:** Press Ctrl+N
- [ ] **Expected:** Grid layout changes (2x1 → 2x2)
- [ ] **Expected:** New session pane appears
- [ ] **Expected:** New session shows "SESSION STARTED" box
- [ ] **Expected:** All existing sessions continue working
- [ ] **Expected:** Header shows increased session count

### Close Session

- [ ] **Test:** Focus a session, press Ctrl+W
- [ ] **Expected:** Notification: "Session closed"
- [ ] **Expected:** Focused session pane disappears
- [ ] **Expected:** Grid layout adjusts
- [ ] **Expected:** Remaining sessions continue working

### Rename Session

- [ ] **Test:** Press Ctrl+R
- [ ] **Expected:** Rename dialog appears with current name
- [ ] **Test:** Type new name, press Enter
- [ ] **Expected:** Session header updates with new name
- [ ] **Expected:** Dialog closes

### Save Sessions

- [ ] **Test:** Press Ctrl+S
- [ ] **Expected:** Notification: "Saved X session(s)"
- [ ] **Expected:** File created at `~/.claude_multi_terminal/state.json`

### Load Sessions

- [ ] **Test:** Press Ctrl+L (after saving sessions)
- [ ] **Expected:** All current sessions close
- [ ] **Expected:** Saved sessions are recreated
- [ ] **Expected:** Notification: "Restored X session(s)"

### Quit Application

- [ ] **Test:** Press Ctrl+Q
- [ ] **Expected:** Application exits gracefully
- [ ] **Expected:** Terminal returns to normal
- [ ] **Expected:** No error messages printed
- [ ] **Expected:** All session processes terminated

---

## Edge Case Testing

### Empty Commands

- [ ] **Test:** Press Enter without typing anything
- [ ] **Expected:** Nothing happens (no separator, no error)

### Very Long Commands

- [ ] **Test:** Type a 200+ character command
- [ ] **Expected:** Text wraps correctly in input field
- [ ] **Expected:** Command is processed normally

### Rapid Typing

- [ ] **Test:** Type rapidly without waiting for responses
- [ ] **Expected:** Input is buffered correctly
- [ ] **Expected:** All characters appear
- [ ] **Expected:** No text is lost

### Special Characters

- [ ] **Test:** Type `echo 'Hello "World"'`
- [ ] **Expected:** Quotes are handled correctly
- [ ] **Test:** Type `echo 你好 🚀`
- [ ] **Expected:** Unicode and emoji render correctly

### Maximum Sessions

- [ ] **Test:** Create 6 sessions (Ctrl+N multiple times)
- [ ] **Expected:** 6 sessions created successfully
- [ ] **Test:** Try to create 7th session
- [ ] **Expected:** Warning: "Maximum 6 sessions reached"

### Rapid Pane Switching

- [ ] **Test:** Press Tab repeatedly and quickly
- [ ] **Expected:** Focus switches smoothly
- [ ] **Expected:** No lag or stuttering
- [ ] **Expected:** Border updates are visible

### Terminal Resize

- [ ] **Test:** Resize terminal window
- [ ] **Expected:** TUI adjusts to new size
- [ ] **Expected:** Panes remain proportional
- [ ] **Expected:** No visual corruption

---

## Performance Testing

### Response Time

- [ ] **Test:** Send 5 simple commands in sequence
- [ ] **Expected:** Each responds within 1-3 seconds
- [ ] **Expected:** No noticeable degradation over time

### Memory Usage

- [ ] **Test:** Create and destroy 3 sessions multiple times
- [ ] **Expected:** Memory usage remains stable
- [ ] **Expected:** No visible memory leaks

### Scrollback Performance

- [ ] **Test:** Generate lots of output (`ls -lR /usr`)
- [ ] **Expected:** Scrolling is smooth
- [ ] **Expected:** No lag when rendering long output

---

## Platform-Specific Tests

### macOS (Darwin)

- [ ] **Test:** Clipboard (pbcopy/pbpaste)
- [ ] **Expected:** Ctrl+C copies to system clipboard
- [ ] **Test:** Terminal app compatibility
- [ ] **Expected:** Works in Terminal.app, iTerm2, etc.

### Linux

- [ ] **Test:** Clipboard (xclip or xsel)
- [ ] **Expected:** Ctrl+C copies to clipboard
- [ ] **Test:** Terminal emulator compatibility
- [ ] **Expected:** Works in gnome-terminal, xterm, etc.

---

## Error Handling

### Invalid Command

- [ ] **Test:** Type `invalidcommandxyz123`
- [ ] **Expected:** Claude responds with error or unknown command
- [ ] **Expected:** Session remains functional
- [ ] **Expected:** No crash

### Ctrl+C During Command

- [ ] **Test:** Send long-running command, press Ctrl+C
- [ ] **Expected:** Output is copied (Ctrl+C is copy, not interrupt in TUI)
- [ ] **Expected:** Command continues running

### Network Issues

- [ ] **Test:** Disable network, send command
- [ ] **Expected:** Claude may show connection error
- [ ] **Expected:** App doesn't crash
- [ ] **Expected:** Can recover when network returns

---

## Final Sign-Off

**All Automated Tests:** ☐ PASS ☐ FAIL
**All Manual Tests:** ☐ PASS ☐ FAIL
**All Edge Cases:** ☐ PASS ☐ FAIL
**Platform Tests:** ☐ PASS ☐ FAIL
**Performance Tests:** ☐ PASS ☐ FAIL

**Overall Status:** ☐ APPROVED ☐ NEEDS WORK

**Notes:**
_________________________________
_________________________________
_________________________________

**Tester Name:** _________________
**Date:** ________________________
**Signature:** ___________________

---

## Known Limitations (Not Bugs)

1. Maximum 6 sessions (configurable in `config.py`)
2. Claude startup takes 2-3 seconds (LLM initialization)
3. Some complex ANSI sequences filtered for compatibility
4. Text selection requires F2 toggle (mouse is captured by TUI)
5. Session persistence saves state but not full command history

---

## Support

If you encounter any issues during testing:

1. Check debug logs: `/tmp/session_*.log`
2. Review test reports: `TEST_REPORT.md` and `TESTING_SUMMARY.md`
3. Run smoke test: `python smoke_test.py`
4. Verify Claude CLI: `/opt/homebrew/bin/claude --version`
5. Check Python version: `python --version` (need 3.10+)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-29
