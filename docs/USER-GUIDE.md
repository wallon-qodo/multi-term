# Claude Multi-Terminal User Guide

**Version:** 0.1.0
**Last Updated:** February 2026

A comprehensive guide to mastering the Claude Multi-Terminal TUI (Terminal User Interface).

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Modal System](#modal-system)
4. [Workspace System](#workspace-system)
5. [Navigation](#navigation)
6. [Best Practices](#best-practices)
7. [Common Workflows](#common-workflows)
8. [Advanced Features](#advanced-features)
9. [Keyboard Shortcuts Reference](#keyboard-shortcuts-reference)
10. [Tips & Tricks](#tips--tricks)
11. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Claude Multi-Terminal?

Claude Multi-Terminal is a TUIOS-inspired terminal multiplexer designed specifically for working with multiple Claude Code CLI sessions simultaneously. It combines the power of tiling window managers (like i3/dwm) with the modal efficiency of vim/tmux.

### Key Features

- **9 Workspaces**: Organize sessions by project, topic, or task
- **Multi-Pane Layout**: Up to 6 concurrent Claude sessions per workspace
- **Modal Interface**: vim-like keybindings for efficiency
- **Focus Mode**: Distraction-free single-pane view
- **Session Persistence**: All conversations saved automatically
- **Token Tracking**: Real-time usage and cost monitoring
- **Smart Context**: Integrates with learning and knowledge systems

### Philosophy

The interface follows these principles:

1. **Keyboard-First**: Mouse is optional, keyboard is optimal
2. **Modal Efficiency**: Right mode for the right task
3. **Spatial Memory**: Visual organization aids recall
4. **Minimal Distraction**: Clean, focused interface
5. **Power User Friendly**: Scales from beginner to expert

---

## Getting Started

### Launch

```bash
cd ~/claude-multi-terminal
source venv/bin/activate
python3 -m claude_multi_terminal
```

### First Launch

When you first start the app:

1. You'll see **Workspace [1]** active (highlighted)
2. A single pane in **NORMAL mode** (⌘ indicator)
3. Status bar showing: model, tokens, available keys
4. Empty conversation ready for input

### Your First Interaction

```
1. Press 'i' to enter INSERT mode
2. Type: "Hello, Claude!"
3. Press Enter to send
4. Watch Claude respond
5. Automatically back to NORMAL mode
```

---

## Modal System

The UI uses **four modes** inspired by vim:

### 1. NORMAL Mode ⌘ (Default)

**Purpose:** Navigation, switching panes, issuing commands

**Status:** `⌘ NORMAL` in status bar

**What you can do:**
- Navigate the interface
- Switch between panes and workspaces
- Enter other modes
- Copy text
- Scroll through history

**Key Principle:** This is your "safe" mode. You can't accidentally type or send messages.

**Common Actions:**
```
i          → Enter INSERT mode
v          → Enter VISUAL mode (copy)
F11        → Toggle FOCUS mode
Tab        → Next pane
Shift+Tab  → Previous pane
Ctrl+1-9   → Switch workspaces
q          → Quit application
```

### 2. INSERT Mode ✏️ (Input)

**Purpose:** Type prompts and messages to Claude

**Status:** `✏️ INSERT` in status bar

**What you can do:**
- Type your prompts
- Edit text before sending
- Send messages

**Entry:** Press `i` from NORMAL mode

**Exit:** Press `Esc` to return to NORMAL

**Sending Messages:**

**Single-line mode:** (default)
```
Type your message → Press Enter → Sent!
```

**Multi-line mode:** (toggle with Ctrl+M)
```
Type line 1 → Enter (new line)
Type line 2 → Enter (new line)
Type line 3 → Ctrl+Enter → Sent!
```

**Status bar shows:**
- `Single-line | Enter: Submit` or
- `Multi-line | Ctrl+Enter: Submit`

### 3. VISUAL Mode 📋 (Copy)

**Purpose:** Select and copy text from Claude's responses

**Status:** `📋 VISUAL` in status bar

**What you can do:**
- Select text with arrow keys
- Copy to system clipboard

**Entry:** Press `v` from NORMAL mode

**Exit:** Press `Esc` to return to NORMAL

**Usage:**
```
1. Navigate to text you want (NORMAL mode)
2. Press 'v' to enter VISUAL mode
3. Use arrow keys to select text
4. Press Enter to copy
5. Automatically returns to NORMAL
6. Text is in your clipboard
```

### 4. FOCUS Mode 🎯 (Fullscreen)

**Purpose:** Distraction-free single-pane view

**Status:** Selected pane expands to full screen

**What you can do:**
- Work with one Claude session at a time
- Hide other panes temporarily
- All other mode keys still work

**Entry:** Press `F11` from any mode

**Exit:** Press `F11` again or `Esc`

**Use Cases:**
- Deep conversations requiring concentration
- Reviewing long responses
- Working through complex problems
- Screen recording/presenting

**Important:** Other panes are **hidden**, not deleted. Their state is preserved.

---

## Workspace System

### Overview

The multi-terminal provides **9 independent workspaces**, like virtual desktops:

```
╔═══ ⚡ CLAUDE MULTI-TERMINAL ═══════════════════════════════════╗
║ [1] [2] [3] [4] [5] [6] [7] [8] [9] ┃ ● 2 sessions    ┃
║  ↑   -   -   -   -   -   -   -   -                    ┃
╚═══════════════════════════════════════════════════════════════╝
```

- **Active workspace:** Highlighted (red background with white number)
- **Inactive workspaces:** Dimmed (gray text)

### Switching Workspaces

```
Ctrl+1 → Workspace [1]
Ctrl+2 → Workspace [2]
...
Ctrl+9 → Workspace [9]
```

**Quick switch:**
```
Ctrl+N → Next workspace (wraps around)
Ctrl+P → Previous workspace (wraps around)
```

### Workspace Organization Strategies

#### By Project
```
[1] → Personal projects
[2] → Work project A
[3] → Work project B
[4] → Learning/experiments
[5] → Documentation
...
```

#### By Task Type
```
[1] → Active coding
[2] → Debugging
[3] → Code review
[4] → Research/planning
[5] → Testing
...
```

#### By Context Depth
```
[1] → Quick questions (single pane)
[2] → Standard work (2-3 panes)
[3] → Complex problems (4-6 panes)
[4] → Long-running sessions
...
```

### Best Practice: Workspace Naming

Keep a mental (or written) map:
```
# My Workspace Map (keep in notes)
1. Quick tasks & experiments
2. Main project: auth-service
3. Main project: frontend-app
4. Learning: Rust & system programming
5. Code reviews & PRs
6. Documentation writing
7. Debugging & investigation
8. Research & exploration
9. Temporary/scratch space
```

---

## Navigation

### Pane Navigation

**Keyboard (Recommended):**
```
Tab        → Move to next pane (clockwise)
Shift+Tab  → Move to previous pane (counter-clockwise)
Ctrl+W     → Cycle through panes
```

**Mouse (Optional):**
```
Click pane → Focus that pane
```

**Visual Indication:**
- Active pane: Brighter border
- Inactive panes: Dimmed border

### Scrolling

**Keyboard:**
```
PageUp     → Scroll up one page
PageDown   → Scroll down one page
Home       → Scroll to top
End        → Scroll to bottom
```

**Mouse:**
```
Scroll wheel → Scroll up/down (reduced speed for control)
```

### Finding Your Place

After scrolling up to review history:

```
Press End → Jump back to latest messages
```

---

## Best Practices

### Starting Your Day

**1. Organize Workspaces**
```
Ctrl+1 → Start with main project
Ctrl+2 → Open second priority
Ctrl+3 → Setup monitoring/logs
```

**2. Begin with Context**

In each workspace, start Claude sessions with:
- "Working on [project name]"
- "Continuing [yesterday's task]"
- "New feature: [description]"

This helps the smart context system load relevant history.

**3. Use Descriptive Initial Prompts**

Good:
```
"Debugging authentication timeout in the JWT service.
Users report sessions expire after 5 minutes instead of 15."
```

Better than:
```
"Fix auth"
```

The detail helps knowledge synthesis and future search.

### During Work

**1. Single Task per Pane**

Each pane = one conversation thread:
- ✅ Pane 1: "Implementing feature X"
- ✅ Pane 2: "Debugging issue Y"
- ✅ Pane 3: "Reviewing code Z"

Avoid mixing topics in one pane.

**2. Use Focus Mode for Deep Work**

When you need to concentrate:
```
F11 → Enter focus mode
[Work without distraction]
F11 → Exit when done
```

**3. Switch Workspaces, Not Panes**

For different projects:
- ❌ Don't: Repurpose panes in current workspace
- ✅ Do: Switch to dedicated workspace

**4. Keep NORMAL Mode Default**

After any action:
- You should be in NORMAL mode
- Press Esc if you're not sure
- Prevents accidental typing

### Ending Your Day

**1. Review Active Sessions**

Check what you were working on:
```
Ctrl+1 → Review workspace 1
Ctrl+2 → Review workspace 2
...
```

**2. Document Status**

In each active workspace, send a closing message:
```
"Status: Completed authentication fix.
Next: Deploy to staging and test."
```

This helps when you resume tomorrow.

**3. Close or Leave Open**

Sessions are persistent, so you can:
- **Option A:** Close app (Ctrl+C or 'q') - Sessions saved
- **Option B:** Leave running overnight - Sessions remain active

**4. Check Token Usage**

Review cost in status bar:
```
180K tok ($1.61) → Reasonable
500K tok ($4.50) → High, consider optimizing
```

---

## Common Workflows

### Workflow 1: Quick Question

**Goal:** Ask Claude a quick question

**Steps:**
```
1. Press 'i' (INSERT mode)
2. Type: "What's the difference between git merge and git rebase?"
3. Press Enter
4. Read response (auto-scrolls)
5. Continue or press 'q' to quit
```

**Time:** 30 seconds

### Workflow 2: Multi-Step Problem

**Goal:** Work through a complex problem with back-and-forth

**Steps:**
```
1. Press 'i'
2. Describe problem: "Need to implement caching for API"
3. Enter → Claude responds with approach
4. Press 'i' again
5. Ask follow-up: "What about cache invalidation?"
6. Enter → Claude explains
7. Repeat as needed
8. Copy final solution with 'v' + arrows + Enter
```

**Time:** 5-10 minutes

### Workflow 3: Parallel Development

**Goal:** Work on multiple features simultaneously

**Setup:**
```
1. Ctrl+1 → Workspace for Feature A
2. Press 'i', describe Feature A, work on it
3. Ctrl+2 → Workspace for Feature B
4. Press 'i', describe Feature B, work on it
5. Ctrl+3 → Workspace for debugging
6. Press 'i', describe bug, get help
```

**Switch between:**
```
Ctrl+1 → Back to Feature A
Ctrl+2 → Back to Feature B
Ctrl+3 → Back to debugging
```

**Time:** Throughout the day

### Workflow 4: Code Review

**Goal:** Review a pull request with Claude's help

**Setup:**
```
1. Single workspace with 3 panes (Ctrl+G → grid)
2. Pane 1: Main review conversation
3. Pane 2: Questions about specific code
4. Pane 3: Suggestions and improvements
```

**Process:**
```
Pane 1: "Review this PR: [paste URL]"
Tab → Pane 2: "What does this function do?"
Tab → Pane 3: "Suggest improvements for error handling"
Tab → Cycle through responses
```

**Copy findings:**
```
v → Select text → Enter → Paste into PR comments
```

**Time:** 15-30 minutes

### Workflow 5: Learning Session

**Goal:** Learn a new technology with Claude as tutor

**Setup:**
```
Workspace [4] → Learning
2 panes: Left = theory, Right = practice
```

**Process:**
```
Left pane:
- "Explain Rust ownership model"
- "What are lifetimes?"
- "Compare to garbage collection"

Right pane:
- "Show me example code"
- "Help me fix this compiler error"
- "Explain what this code does"
```

**Use Focus Mode:**
```
F11 on left → Read theory
F11 on right → Practice coding
```

**Time:** 1-2 hours

### Workflow 6: Debugging Marathon

**Goal:** Track down a difficult bug

**Setup:**
```
Workspace [3] → Debugging
4 panes arranged in grid
```

**Pane Organization:**
```
┌─────────────┬─────────────┐
│ Pane 1      │ Pane 2      │
│ Symptom     │ Hypotheses  │
│ description │ & tests     │
├─────────────┼─────────────┤
│ Pane 3      │ Pane 4      │
│ Stack trace │ Solution    │
│ analysis    │ & fix       │
└─────────────┴─────────────┘
```

**Process:**
```
1. Pane 1: Describe bug in detail
2. Tab → Pane 2: Test hypotheses with Claude
3. Tab → Pane 3: Analyze stack traces
4. Tab → Pane 4: Implement fix

Copy final solution from Pane 4
```

**Time:** 30 minutes - 2 hours

---

## Advanced Features

### Session Persistence

**Automatic Saving:**
- All conversations saved to: `~/Desktop/multi-claude-sessions/sessions/`
- Each session gets unique ID: `YYYY-MM-DD-session-N-XXXX`
- Includes: conversation log, context, insights, token usage

**Session Files:**
```
~/Desktop/multi-claude-sessions/sessions/2026-02-20-session-1-a8f3/
├── conversation-log.jsonl    # Full conversation
├── .session-context.md       # Context loaded at start
├── token-usage.json          # Token tracking
└── insights.md               # Extracted learnings
```

**Viewing Past Sessions:**
```bash
# List sessions
ls ~/Desktop/multi-claude-sessions/sessions/

# View a conversation
cat ~/Desktop/multi-claude-sessions/sessions/2026-02-20-*/conversation-log.jsonl | jq .

# View insights
cat ~/Desktop/multi-claude-sessions/sessions/2026-02-20-*/insights.md
```

### Smart Context System

When you start a session, the system automatically:

1. **Loads recent history** - Last 1-2 sessions in full
2. **Finds related work** - Top 10 relevant past sessions (summarized)
3. **Indexes everything** - All 88+ sessions searchable

**Benefit:** Claude knows your full work history and can reference past solutions.

**On-Demand Loading:**
```
In conversation, ask:
"Show me the authentication session from last week"
"What did we decide about caching?"
"Load the JWT implementation"

→ System finds and loads full relevant context
```

**Cost:** ~$0.15-0.30 per session (vs $1-2 for full context)

### Knowledge Synthesis

The system learns from every conversation:

**Automatic Extraction:**
- Solutions that worked
- Decisions and rationale
- Error resolutions
- Code patterns
- Best practices

**Automatic Injection:**

When you start a new session about authentication:
```markdown
💡 Relevant Past Solutions

1. JWT Authentication (2026-02-15)
   Problem: Session management
   Solution: JWT with Redis
   Success: 100%
   Load: "show me the JWT session"
```

**Manual Search:**
```bash
# Search your knowledge
knowledge-assistant search "authentication"
knowledge-assistant solve "session timeout"
```

### Codebase Integration

The system indexes your codebase:

**Automatic Indexing:**
- 750 definitions from your workspace
- Functions, classes, methods
- Semantic search enabled

**In Conversation:**
```
Ask: "Where's the authentication code?"
→ Claude searches index
→ Shows: auth.py:45, login.py:123
→ With full context
```

**Manual Search:**
```bash
# Search codebase
claude-assistant search "session management"
claude-assistant find-function "authenticate"
```

### Token & Cost Tracking

**Real-Time Display:**

Status bar shows:
```
180K tok ($1.61)
```

**Per-Session Tracking:**
- Input tokens
- Output tokens
- Total cost
- Running total

**Check Detailed Usage:**
```bash
cat ~/Desktop/multi-claude-sessions/sessions/2026-02-20-*/token-usage.json
```

**Budget Awareness:**

System warns when approaching limits:
```
⚠️  Approaching context limit (150K/200K tokens)
💡 Consider:
- Starting new session
- Summarizing context
- Loading less history
```

---

## Keyboard Shortcuts Reference

### Essential (Memorize These)

```
NORMAL MODE
───────────
i           Enter INSERT mode (type)
v           Enter VISUAL mode (copy)
F11         Toggle FOCUS mode
Tab         Next pane
Esc         To NORMAL mode (from anywhere)
q           Quit application

WORKSPACES
──────────
Ctrl+1-9    Switch to workspace 1-9
Ctrl+N      Next workspace
Ctrl+P      Previous workspace

INSERT MODE
───────────
Enter       Send message (single-line)
Ctrl+Enter  Send message (multi-line)
Esc         Back to NORMAL

VISUAL MODE
───────────
Arrows      Select text
Enter       Copy selection
Esc         Back to NORMAL
```

### Advanced

```
SCROLLING
─────────
PageUp      Scroll up one page
PageDown    Scroll down one page
Home        Scroll to top
End         Scroll to bottom

NAVIGATION
──────────
Shift+Tab   Previous pane
Ctrl+W      Cycle panes

MODES
─────
Ctrl+M      Toggle single/multi-line (INSERT)
```

### Mouse (Optional)

```
Click pane      → Focus pane
Scroll wheel    → Scroll up/down
Click workspace → Switch workspace (if enabled)
```

---

## Tips & Tricks

### Efficiency Tips

**1. Stay in NORMAL**
```
Default to NORMAL mode
Press Esc habitually
Only enter INSERT when ready to type
```

**2. Use Tab Navigation**
```
Tab through panes faster than mouse
Muscle memory develops quickly
```

**3. Workspace Switching**
```
Ctrl+1, Ctrl+2, Ctrl+3 → Instant context switches
Faster than Alt+Tab between apps
```

**4. Focus for Concentration**
```
F11 → Instant distraction elimination
Works in any mode
F11 again to return
```

**5. Copy Smart**
```
v → Select only what you need
Don't copy entire responses
Saves time pasting elsewhere
```

### Power User Tips

**1. Workspace Patterns**
```
1-3: Active projects (frequently switch)
4-6: Background tasks (check occasionally)
7-9: Experiments (low priority)
```

**2. Pane Specialization**
```
Left panes: Planning & questions
Right panes: Implementation & code
Top panes: Research & documentation
Bottom panes: Testing & debugging
```

**3. Context Continuity**
```
Start each session with: "Continuing [previous task]"
End each session with: "Status: [what was accomplished]"
Helps resume tomorrow
```

**4. Search Before Asking**
```
Before asking Claude a question:
knowledge-assistant search "your topic"
Might already have the answer from past work
```

**5. Token Optimization**
```
Monitor status bar cost
If >$2/session regularly:
- Summarize long conversations
- Start fresh sessions more often
- Use on-demand loading instead of full context
```

### Customization Tips

**1. Adjust Scroll Speed**

Already optimized (40% of normal), but if you want different:
```python
# In selectable_richlog.py
scroll_amount = max(1, int(event.y * 0.4))  # Change 0.4
```

**2. Token Update Frequency**

Current: Updates every 3 seconds (simulated). For real tracking, integrate Claude API SDK.

**3. Workspace Count**

Current: 9 workspaces. To change:
```python
# In app.py
NUM_WORKSPACES = 12  # Or any number
```

---

## Troubleshooting

### App Won't Start

**Problem:** `python3 -m claude_multi_terminal` fails

**Solutions:**
```bash
# Check virtual environment
source venv/bin/activate

# Verify installation
pip list | grep textual

# Reinstall if needed
pip install -r requirements.txt

# Check Python version (need 3.8+)
python3 --version
```

### RuntimeWarning on Start

**Problem:** Module loading warning appears

**Solution:** This is cosmetic and fixed in latest version. Ignore or update:
```bash
git pull origin main
```

### Panes Not Responding

**Problem:** Can't type or navigate

**Check:**
1. Are you in NORMAL mode? (Press Esc)
2. Is the pane focused? (Click it or Tab to it)
3. Is the app frozen? (Ctrl+C and restart)

### Text Not Copying

**Problem:** 'v' mode but text doesn't copy

**Solutions:**
```bash
# Check clipboard access
echo "test" | pbcopy  # macOS
echo "test" | xclip   # Linux

# Try manual copy
Select text → Cmd+C (macOS) or Ctrl+Shift+C (Linux)
```

### Focus Mode Clears Chat

**Problem:** [FIXED] F11 used to clear conversations

**Solution:**
- Fixed in commit 4582c92
- Update to latest version
- F11 now hides panes without destroying them

### Token Tracking Wrong

**Problem:** Tokens don't match actual usage

**Current:** Simulated tracking (demo mode)

**Solution:** For real tracking:
1. Use Claude API SDK directly (not CLI via PTY)
2. Or: Accept simulated tracking as approximation

### High Token Costs

**Problem:** Sessions costing $2-5 each

**Solutions:**
```bash
# 1. Check context loading
~/.claude/scripts/token-budget-tracker.sh status

# 2. Reduce context
Edit ~/.claude/data/smart-context-config.json
Reduce tier1_budget and tier2_budget

# 3. Start fresh sessions more often
Don't let single sessions run for hours

# 4. Use summaries
~/.claude/scripts/batch-summarizer.sh all
```

### Can't Find Past Sessions

**Problem:** Looking for old conversation

**Solution:**
```bash
# Search knowledge base
knowledge-assistant search "what you remember"

# List all sessions
ls ~/Desktop/multi-claude-sessions/sessions/

# Search session files
grep -r "keyword" ~/Desktop/multi-claude-sessions/sessions/*/conversation-log.jsonl
```

### App Freezes

**Problem:** UI becomes unresponsive

**Quick Fix:**
```
Ctrl+C → Kill app
Restart: python3 -m claude_multi_terminal
Sessions are saved, no data lost
```

**Prevention:**
- Don't run sessions for many hours
- Restart daily
- Monitor memory usage

### Performance Slow

**Problem:** App feels sluggish

**Solutions:**
```bash
# Check system resources
top  # or htop

# Close unused workspaces
Switch to workspace → Close panes

# Reduce history
Scroll to bottom (End key) to avoid rendering old messages

# Restart app
Ctrl+C → restart
```

---

## Getting Help

### Documentation

- **This Guide:** Full user documentation
- **README.md:** Quick start and installation
- **API Docs:** For developers extending the app

### Community

- **GitHub Issues:** Report bugs or request features
- **Discussions:** Ask questions, share tips

### Support

For issues:
1. Check this troubleshooting section
2. Search GitHub issues
3. Create new issue with:
   - OS and Python version
   - Steps to reproduce
   - Error messages
   - Screenshots if applicable

---

## Changelog

### Version 0.1.0 (February 2026)

**Initial Release:**
- Multi-pane terminal interface
- 9 workspace system
- Modal operation (NORMAL, INSERT, VISUAL, FOCUS)
- Session persistence
- Token tracking
- Smart context integration
- Knowledge synthesis
- Codebase indexing

**Bug Fixes:**
- Focus mode no longer clears chat (4582c92)
- Scroll speed reduced for better control (77d28a7)
- Module loading warnings eliminated (9176ffd)

---

## Next Steps

**Now that you've read this guide:**

1. **Launch the app** and try the basic workflows
2. **Set up workspaces** for your projects
3. **Practice modal navigation** until it's muscle memory
4. **Review past sessions** to understand persistence
5. **Explore smart context** by asking about past work

**Quick Start Reminder:**
```bash
cd ~/claude-multi-terminal
source venv/bin/activate
python3 -m claude_multi_terminal

Press 'i' → Type → Enter → Start coding!
```

**Remember:** The more you use it, the more powerful it becomes. The knowledge system learns from every interaction.

---

## License

MIT License - See LICENSE file for details

---

**Happy coding with Claude Multi-Terminal!** 🚀
