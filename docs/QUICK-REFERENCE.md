# Claude Multi-Terminal Quick Reference

One-page cheat sheet for fast lookups.

---

## Launch

```bash
cd ~/claude-multi-terminal && source venv/bin/activate && python3 -m claude_multi_terminal
```

---

## Modes

| Mode | Status | Purpose | Enter | Exit |
|------|--------|---------|-------|------|
| **NORMAL** ⌘ | Default | Navigate | (default) | - |
| **INSERT** ✏️ | Type | Send prompts | `i` | `Esc` |
| **VISUAL** 📋 | Copy | Copy text | `v` | `Esc` |
| **FOCUS** 🎯 | Fullscreen | Single pane | `F11` | `F11` or `Esc` |

---

## Essential Keys

```
╔══════════════════════════════════════════════════════════╗
║  KEY           ACTION                                    ║
╠══════════════════════════════════════════════════════════╣
║  i             Enter INSERT mode (type prompts)          ║
║  v             Enter VISUAL mode (copy text)             ║
║  F11           Toggle FOCUS mode (fullscreen)            ║
║  Esc           Return to NORMAL mode                     ║
║  q             Quit application                          ║
║                                                          ║
║  Tab           Next pane                                 ║
║  Shift+Tab     Previous pane                             ║
║                                                          ║
║  Ctrl+1-9      Switch to workspace 1-9                   ║
║  Ctrl+N        Next workspace                            ║
║  Ctrl+P        Previous workspace                        ║
║                                                          ║
║  Enter         Send message (INSERT mode)                ║
║  Ctrl+Enter    Send multi-line message                   ║
║                                                          ║
║  PageUp/Down   Scroll page                               ║
║  Home/End      Scroll to top/bottom                      ║
╚══════════════════════════════════════════════════════════╝
```

---

## Workflows

### Quick Question
```
i → type → Enter → done
```

### Copy Text
```
v → arrows → Enter → copied
```

### Switch Workspace
```
Ctrl+2 → now in workspace [2]
```

### Focus on One Pane
```
F11 → fullscreen → F11 → back
```

### Multi-Pane Work
```
Tab → work → Tab → work → Tab → work
```

---

## Status Bar

```
┃ ⌘ NORMAL ┃  ┊  Sonnet 4.5  ┊  180K tok ($1.61)  i:Insert ┊ v:Copy
 ↑mode        ↑model         ↑usage/cost          ↑hints
```

---

## Workspaces

```
[1] [2] [3] [4] [5] [6] [7] [8] [9]
 ↑
Currently active (highlighted)
```

**Switch:** `Ctrl+1` through `Ctrl+9`

**Organization Ideas:**
- By project (1=project A, 2=project B, etc.)
- By task (1=coding, 2=debugging, 3=review, etc.)
- By priority (1-3=urgent, 4-6=normal, 7-9=backlog)

---

## Common Patterns

### Daily Start
```
Ctrl+1 → main project
i → "Continuing yesterday's auth work"
```

### Parallel Tasks
```
Ctrl+1 → Feature A
Ctrl+2 → Feature B
Ctrl+3 → Debugging
(switch as needed)
```

### Deep Focus
```
F11 → focus on problem
[work without distraction]
F11 → return to multi-pane
```

### Copy & Use
```
v → select code → Enter
Paste into editor
```

---

## Session Files

All conversations auto-saved to:
```
~/Desktop/multi-claude-sessions/sessions/YYYY-MM-DD-session-N-XXXX/
```

---

## Smart Features

### Auto Context Loading

Sessions start with:
- Last 1-2 sessions (full)
- Top 10 related sessions (summaries)
- All sessions (searchable)

### On-Demand Loading

In conversation:
```
"Show me the auth session from last week"
"What did we decide about caching?"
→ System loads relevant full context
```

### Knowledge Search

```bash
knowledge-assistant search "authentication"
knowledge-assistant solve "timeout issue"
```

### Codebase Search

```bash
claude-assistant search "session management"
claude-assistant find-function "authenticate"
```

---

## Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| Can't type | Press `i` for INSERT mode |
| Stuck in INSERT | Press `Esc` |
| Pane not responding | Click it or Tab to it |
| App frozen | `Ctrl+C` and restart |
| High costs | Check token budget tracker |
| Can't find session | `knowledge-assistant search` |

---

## Best Practices

1. **Stay in NORMAL** - Default mode after every action
2. **One task per pane** - Don't mix topics
3. **Use workspaces** - Organize by project/task
4. **F11 for focus** - When you need concentration
5. **End with status** - "Status: completed X, next: Y"

---

## Performance Tips

- Monitor status bar cost
- Restart app daily
- Start new sessions for new topics
- Use on-demand loading vs full context
- Close unused workspaces

---

## Getting More Help

- **Full Guide:** `docs/USER-GUIDE.md`
- **GitHub Issues:** Report bugs
- **Knowledge Base:** `knowledge-assistant search "topic"`

---

**Remember:** `i` to type, `Esc` to exit, `F11` to focus, `q` to quit

**Happy coding!** 🚀
