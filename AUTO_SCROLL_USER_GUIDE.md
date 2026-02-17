# Auto-Scroll Toggle - User Guide

## Quick Start

### What is Auto-Scroll?
Auto-scroll keeps the terminal output scrolled to the bottom so you always see the latest output from Claude. This is especially useful when Claude is generating long responses or streaming content.

### Default Behavior
- Auto-scroll is **enabled by default** in all sessions
- New output automatically scrolls into view
- Each session has its own independent auto-scroll setting

## How to Use

### Method 1: Keyboard Shortcut (Recommended)
Press **Ctrl+Shift+A** to toggle auto-scroll on/off

You'll see a notification:
- **▼ Auto-scroll enabled** (green) - New output will auto-scroll
- **▬ Auto-scroll disabled** (gray) - View stays at current position

### Method 2: Smart Auto-Detection (Automatic)

#### Scroll Up = Pause Auto-Scroll
When you scroll up (mouse wheel, trackpad, or scrollbar), auto-scroll automatically pauses.

**Notification:** "▬ Auto-scroll paused (scroll to bottom to resume)"

**Why?** So you can read old output without being interrupted by new content.

#### Scroll to Bottom = Resume Auto-Scroll
When you scroll back down to the bottom, auto-scroll automatically resumes.

**Notification:** "▼ Auto-scroll re-enabled"

**Why?** Seamless transition back to following new output.

## Common Scenarios

### Scenario 1: Reviewing Old Output While Claude Responds
1. Claude starts generating a long response
2. You want to review something earlier in the conversation
3. **Scroll up** with mouse wheel → Auto-scroll pauses automatically
4. Read at your own pace
5. When ready, **scroll to bottom** → Auto-scroll resumes

**Result:** You can review history without losing your place or being disrupted by new content.

### Scenario 2: Keeping View Fixed While Testing Code
1. You ask Claude to generate code
2. You want to keep your editor/terminal visible at the same position
3. Press **Ctrl+Shift+A** → Auto-scroll disabled
4. New output appears but view doesn't jump
5. Press **Ctrl+Shift+A** again when ready to resume

**Result:** You control when and how you view new output.

### Scenario 3: Multi-Session Workflow
1. You have 3 sessions open (Ctrl+N to create new sessions)
2. Session 1: Auto-scroll enabled (default)
3. Session 2: Press Ctrl+Shift+A to disable
4. Session 3: Scroll up to review old output (auto-pauses)

**Result:** Each session remembers its own auto-scroll state. Perfect for monitoring one session while working in another.

## Visual Indicators

### Notifications
All auto-scroll actions show clear, temporary notifications:

| Action | Notification | Duration |
|--------|-------------|----------|
| Manual toggle ON | ▼ Auto-scroll enabled | 2 seconds |
| Manual toggle OFF | ▬ Auto-scroll disabled | 2 seconds |
| Auto-pause (scroll up) | ▬ Auto-scroll paused (scroll to bottom to resume) | 2 seconds |
| Auto-resume (scroll to bottom) | ▼ Auto-scroll re-enabled | 1.5 seconds |

### Icons
- **▼** = Auto-scroll active (view follows new output)
- **▬** = Auto-scroll paused (view stays fixed)

## Tips & Tricks

### Tip 1: Quick Review
While Claude is responding, quickly scroll up, review what you need, then scroll back to bottom. Auto-scroll handles the state transitions automatically.

### Tip 2: Multiple Monitors
If using multiple monitors, disable auto-scroll in one session while monitoring another. Each session is independent.

### Tip 3: Keyboard Navigation
Combine with other keyboard shortcuts:
- **Ctrl+Shift+A** - Toggle auto-scroll
- **Ctrl+C** - Copy selected text
- **Ctrl+A** - Select all text
- **Ctrl+F** - Search across sessions

### Tip 4: Long Responses
For very long responses, disable auto-scroll and use Page Up/Down or scroll bar to navigate at your own pace. Enable when ready to jump to the end.

## Troubleshooting

### Q: Auto-scroll isn't working?
**A:** Check if you've scrolled up recently. If so, scroll to the very bottom to re-enable. Or press Ctrl+Shift+A twice (off then on).

### Q: Too many notifications?
**A:** Notifications auto-dismiss after 1.5-2 seconds. They won't stack up or clutter the UI.

### Q: Want to disable for all sessions?
**A:** Currently per-session only. Press Ctrl+Shift+A in each session you want to disable. (Future: global preference)

### Q: Forgot the keyboard shortcut?
**A:** **Ctrl+Shift+A** (think "A" for "Auto-scroll")

## Advanced Usage

### Precision Control
- Use keyboard shortcut for instant toggle
- Let auto-detection handle routine scrolling
- Combine both for maximum flexibility

### Workflow Integration
1. **Research mode:** Disable auto-scroll, scroll freely, take notes
2. **Monitoring mode:** Enable auto-scroll, watch responses stream
3. **Review mode:** Scroll up (auto-pauses), read carefully, scroll down (auto-resumes)

## Keyboard Shortcuts Summary

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift+A | Toggle auto-scroll on/off |
| Scroll Up | Auto-pause (if at bottom) |
| Scroll to Bottom | Auto-resume (if paused) |

## Benefits

✓ **Intuitive:** Works how you'd expect
✓ **Non-Intrusive:** No scroll jumping or jittering
✓ **Clear Feedback:** Always know the state
✓ **Flexible:** Both manual and automatic control
✓ **Per-Session:** Independent control for each terminal

---

**Note:** This is a Quick Win feature designed for simplicity and polish. Feedback welcome!
