# Quick Guide: Three Ways to Rename Sessions

## 1. Keyboard Shortcut (Existing) ⌨️

```
Step 1: Focus the session (click it or use Tab key)
Step 2: Press Ctrl+R
Step 3: Type new name and press Enter

Fast for keyboard users!
```

---

## 2. Double-Click Tab (NEW) 🖱️

```
┌─────────────┐
│ Session 1   │  ← Click once
└─────────────┘

Wait less than 500ms...

┌─────────────┐
│ Session 1   │  ← Click again
└─────────────┘
        ↓
    Rename dialog opens!

Just like VS Code tabs!
```

---

## 3. Right-Click Menu (NEW) 🖱️

```
┌─────────────┐
│ Session 1   │  ← Right-click here
└─────────────┘
        ↓
┌──────────────┐
│ ✏ Rename     │  ← Click this
│ ✗ Close      │
└──────────────┘
        ↓
    Rename dialog opens!

Easy to discover!
```

---

## The Rename Dialog

All three methods open the same dialog:

```
┌────────────────────────────────────┐
│      ✏ Rename Session             │
│                                    │
│  Enter a new name for this session:│
│  ┌──────────────────────────────┐ │
│  │ My New Session Name_         │ │
│  └──────────────────────────────┘ │
│                                    │
│    [✓ Confirm]    [✗ Cancel]      │
└────────────────────────────────────┘

Press Enter to confirm
Press Escape to cancel
```

---

## Quick Comparison

| Method | Best For | Speed |
|--------|----------|-------|
| **Ctrl+R** | Keyboard users, power users | ⚡⚡⚡ |
| **Double-Click** | Mouse users, intuitive | ⚡⚡ |
| **Right-Click** | Discoverable, exploratory | ⚡ |

---

## Tips

💡 **Double-click not working?**
- Make sure you click in the tab body (not the × button)
- Click twice within 500ms
- Both clicks must be on the same tab

💡 **Context menu disappeared?**
- It auto-closes when you click outside
- Just right-click again to reopen

💡 **Prefer keyboard?**
- Ctrl+R is still the fastest way!
- No need to use mouse at all

---

## Try It Now!

```bash
# Start the application
python3 -m claude_multi_terminal

# Then try:
1. Double-click a tab → Rename
2. Right-click a tab → Select Rename → Rename
3. Click a tab, press Ctrl+R → Rename

All three work! 🎉
```
