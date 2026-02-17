# Testing Conversation Context in Claude Multi-Terminal

## Quick Test Guide

### Launch the Application

```bash
cd /Users/wallonwalusayi/claude-multi-terminal
python3 LAUNCH.py
```

### Test Scenario: Multi-Turn Conversation

Follow this specific test flow to verify conversation context works:

#### Step 1: First Message
```
Type: Remember that my favorite color is blue
Expected: Claude acknowledges and remembers
```

#### Step 2: Second Message (Test Context)
```
Type: What's my favorite color?
Expected: Claude responds "blue" or "Your favorite color is blue"
```

#### Step 3: Third Message (Extended Context)
```
Type: Can you also remember that I live in Seattle?
Expected: Claude acknowledges both pieces of information
```

#### Step 4: Fourth Message (Multiple Context Items)
```
Type: Tell me everything you remember about me
Expected: Claude mentions both favorite color (blue) and location (Seattle)
```

### Success Criteria

- ✅ Claude remembers information from previous messages
- ✅ No "I don't have context" errors
- ✅ Each session maintains independent conversation history
- ✅ No session locking errors in debug logs

### Multi-Session Test

1. Open 2 sessions (Ctrl+N to create new session)
2. In Session 1: "Remember the number 42"
3. In Session 2: "Remember the number 99"
4. In Session 1: "What number do you remember?"
   - Expected: "42" (not 99!)
5. In Session 2: "What number do you remember?"
   - Expected: "99" (not 42!)

This verifies that sessions have isolated conversation histories.

### Debug Verification

Check debug logs if issues occur:
```bash
# Session-specific logs
ls /tmp/session_*.log

# Claude CLI debug logs
tail -f ~/.claude/debug/*.txt
```

### What to Look For

**Good Signs:**
- Responses reference previous messages
- Claude uses context from earlier in conversation
- No "I don't have enough context" messages
- Smooth multi-turn interactions

**Bad Signs:**
- Claude asks "What are you referring to?"
- Repeated questions that were already answered
- "Session ID is already in use" errors
- Context lost between messages

### Technical Verification

Check that unique directories are created:
```bash
ls -la ~/.claude_multi_terminal/sessions/
```

Each active session should have its own directory.

Check Claude conversation files:
```bash
find ~/.claude/projects -name "*.jsonl" | grep -E "claude_multi_terminal/sessions"
```

Each session should have conversation history stored.

### Known Working Example

```
User: I'm working on a Python project
Claude: Great! I can help with Python. What would you like to work on?

User: Can you help me understand asyncio?
Claude: Absolutely! Asyncio is Python's library for writing concurrent code...

User: What language did I say I was using?
Claude: You mentioned you're working on a Python project.  <-- CONTEXT MAINTAINED!
```

### Troubleshooting

**If context is lost:**
1. Check if `--continue` flag is in command:
   ```bash
   ps aux | grep claude | grep continue
   ```

2. Verify unique working directories exist:
   ```bash
   ls ~/.claude_multi_terminal/sessions/
   ```

3. Check for error messages in debug logs:
   ```bash
   tail -100 ~/.claude/debug/*.txt | grep -i error
   ```

**If "Session ID is already in use" appears:**
- This shouldn't happen with the new fix
- If it does, it indicates the `--session-id` approach is still being used
- Verify the code changes were applied correctly

### Performance Check

- Commands should respond within 3-10 seconds
- No noticeable delay between commands
- UI remains responsive during processing

### Automated Test

Run the automated test suite:
```bash
python3 test_conversation_context.py
```

Expected output:
```
ALL TESTS PASSED!
```

## Report Issues

If conversation context is not working:
1. Note the exact commands that failed
2. Copy the error messages
3. Check debug logs for details
4. Verify the working directory structure
