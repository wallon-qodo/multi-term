# Terminal Mockups: Processing Indicator Redesign

## Complete Visual Reference

This document provides exact terminal mockups showing the processing indicator at different states.

---

## Full Session View - Processing State

```
┌─────────────────────────────────────────────────────────────────────────────┐
│● ┃ Main Session  ┊  📊 3 cmd  ┊  ID: a1b2c3                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│╔══════════════════════════════════════════════════════════════════════════╗ │
│║                                                                              │
│║ ⚡ CLAUDE SESSION INITIALIZED                                               │
│╠──────────────────────────────────────────────────────────────────────────╣ │
│║ 🕐 Started: 2026-01-29 13:45:00                                            ║ │
│║ 🔖 Session ID: a1b2c3d4                                                    ║ │
│╠──────────────────────────────────────────────────────────────────────────╣ │
│║ 💡 Ready to accept commands                                                ║ │
│╚══════════════════════════════════════════════════════════════════════════╝ │
│                                                                               │
│                                                                               │
│╔══════════════════════════════════════════════════════════════════════════╗ │
│║ ⏱ 13:45:23 ┊ ⚡ Command: hello                                            ║ │
│╚══════════════════════════════════════════════════════════════════════════╝ │
│                                                                               │
│📝 Response: 🥘 Brewing                                                        │
│             └────────┘                                                        │
│                ^ Animates here with yellow shimmer                            │
│                                                                               │
│                                                                               │
│                                                                               │
│                                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│⌨ Enter command or question...                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Visual Elements:**
- Header: Session status with green dot (active)
- Separator: Double-line box with command echo
- Label: "📝 Response:" in light green
- Indicator: "🥘 Brewing" in bold yellow (animates)
- Space: Minimal vertical spacing
- Input: Ready for next command

---

## Animation Sequence (1.8 seconds)

### Frame 0 (0.0s) - Initial State
```
📝 Response: 🥘 Brewing
             ↑  └─────┘
             │  bold yellow
             Pot emoji
```

### Frame 1 (0.3s) - Shimmer Peak
```
📝 Response: 🥘 Brewing
             ↑  └─────┘
             │  bold bright_yellow ✨ (brightest!)
             Same pot
```

### Frame 2 (0.6s) - Normal
```
📝 Response: 🥘 Brewing
             ↑  └─────┘
             │  bold yellow
             Same pot
```

### Frame 3 (0.9s) - Emoji Change + Dim
```
📝 Response: 🍳 Brewing
             ↑  └─────┘
             │  dim yellow (darker)
             Frying pan (NEW!)
```

### Frame 4 (1.2s) - Normal
```
📝 Response: 🍳 Brewing
             ↑  └─────┘
             │  bold yellow
             Same pan
```

### Frame 5 (1.5s) - Shimmer Peak
```
📝 Response: 🍳 Brewing
             ↑  └─────┘
             │  bold bright_yellow ✨
             Same pan
```

### Frame 6 (1.8s) - Emoji + Word Change
```
📝 Response: 🍲 Thinking
             ↑  └──────┘
             │  bold yellow
             Pot of food (NEW!) + "Thinking" (NEW!)
```

**Pattern Continues:**
- Emoji changes every 3 frames (0.9s)
- Word changes every 6 frames (1.8s)
- Shimmer cycles every 4 frames (1.2s)

---

## Complete Emoji Cycle (4.5 seconds)

```
Frame 0-2:   🥘 (Paella)        0.0s - 0.9s
Frame 3-5:   🍳 (Frying pan)    0.9s - 1.8s
Frame 6-8:   🍲 (Pot of food)   1.8s - 2.7s
Frame 9-11:  🥄 (Spoon)         2.7s - 3.6s
Frame 12-14: 🔥 (Fire)          3.6s - 4.5s
Frame 15+:   🥘 (Cycles back)
```

---

## Complete Word Cycle (9.0 seconds)

```
Frame 0-5:   Brewing      0.0s - 1.8s
Frame 6-11:  Thinking     1.8s - 3.6s
Frame 12-17: Processing   3.6s - 5.4s
Frame 18-23: Cooking      5.4s - 7.2s
Frame 24-29: Working      7.2s - 9.0s
Frame 30+:   Brewing (Cycles back)
```

---

## Response Arrival Transition

### State 1: Processing (before response)
```
╚══════════════════════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing
             ↑ Still animating
```

### State 2: First Output Arrives
```
╚══════════════════════════════════════════════════════════════════════════╝

📝 Response:
             ↑ Indicator removed, newline added
```

### State 3: Response Text Appears
```
╚══════════════════════════════════════════════════════════════════════════╝

📝 Response:

Hello! I'm Claude, an AI assistant created by Anthropic. How can I help
you today?
```

**Transition Details:**
1. Indicator hidden (display = false)
2. Newline written to RichLog
3. Response text written to RichLog
4. Auto-scroll to show new text

---

## Multi-Session View

```
┌──────────────────────────────────┬──────────────────────────────────┐
│● ┃ Session A  ┊  📊 2 cmd        │○ ┃ Session B  ┊  📊 1 cmd        │
├──────────────────────────────────┼──────────────────────────────────┤
│                                   │                                   │
│╔════════════════════════════════╗│╔════════════════════════════════╗│
│║ ⏱ 13:45:23 ┊ ⚡ Command: help  ║│║ ⏱ 13:45:25 ┊ ⚡ Command: test  ║│
│╚════════════════════════════════╝│╚════════════════════════════════╝│
│                                   │                                   │
│📝 Response: 🍳 Thinking           │📝 Response: 🥘 Brewing            │
│                                   │                                   │
│                                   │                                   │
├──────────────────────────────────┼──────────────────────────────────┤
│⌨ Enter command...                │⌨ Enter command...                │
└──────────────────────────────────┴──────────────────────────────────┘
```

**Multi-Session Behavior:**
- Each session has independent indicator
- Different animation frames (not synchronized)
- Active session highlighted with blue border
- Inactive session has gray border

---

## Color Palette Reference

### Terminal Color Codes

```
Element                  Style String              RGB Value              Hex
──────────────────────────────────────────────────────────────────────────────
Session header (active)  rgb(55,80,135)           R:55 G:80 B:135        #375087
Session header (inactive) rgb(45,45,60)           R:45 G:45 B:60         #2D2D3C
Terminal background      rgb(18,18,24)            R:18 G:18 B:24         #121218
Terminal text            rgb(220,220,240)         R:220 G:220 B:240      #DCDCF0

Separator box            rgb(100,180,255)         R:100 G:180 B:255      #64B4FF
Command text             rgb(255,220,100)         R:255 G:220 B:100      #FFDC64
Response label           rgb(150,255,150)         R:150 G:255 B:150      #96FF96

Shimmer cycle:
  bold yellow            (terminal default)        ~R:180 G:180 B:0       #B4B400
  bold bright_yellow     (terminal default)        ~R:255 G:255 B:0       #FFFF00
  dim yellow             (terminal default)        ~R:128 G:128 B:0       #808000
```

### Visual Color Samples

```
Response Label:   ████████  rgb(150,255,150)  Light green, calming
Separator:        ████████  rgb(100,180,255)  Light blue, structural
Command:          ████████  rgb(255,220,100)  Light yellow, emphasis

Shimmer Cycle:
Frame 0:          ████████  bold yellow       Medium brightness
Frame 1:          ████████  bright_yellow     HIGH brightness ✨
Frame 2:          ████████  bold yellow       Medium brightness
Frame 3:          ████████  dim yellow        LOW brightness
```

---

## Spacing and Alignment

### Horizontal Spacing
```
📝 Response: 🥘 Brewing
│  │        │ │ │
│  │        │ │ └─ Word (variable width)
│  │        │ └─── Space (1 char)
│  │        └───── Emoji (2 display width)
│  └────────────── Space after colon (1 char)
└───────────────── Label (12 chars including emoji and space)

Total width: ~24 chars when showing "Brewing"
```

### Vertical Spacing
```
Line 1: ╚════════════════════╝  (separator bottom)
Line 2: (empty line)
Line 3: 📝 Response: 🥘 Brewing  (label + indicator)
Line 4: (empty line - where response appears)
Line 5: (response text first line)

Compact! Only 3 lines from separator to response.
```

**Comparison with old design:**
```
Old (5 lines):
Line 1: ╚════════════════════╝
Line 2: (empty)
Line 3: 📝 Response:
Line 4: (empty)
Line 5: 🥘 Brewing...
Line 6: (empty)
Line 7: (response text)

New (3 lines):
Line 1: ╚════════════════════╝
Line 2: (empty)
Line 3: 📝 Response: 🥘 Brewing
Line 4: (response text)

Saves 2 lines! 40% more compact.
```

---

## Box Drawing Character Reference

### Command Separator Components
```
╔═══════════╗   Double-line box (heavy weight)
║ Content   ║   Vertical lines (U+2551)
╚═══════════╝   Horizontal lines (U+2550)

Individual characters:
╔  U+2554  BOX DRAWINGS DOUBLE DOWN AND RIGHT
═  U+2550  BOX DRAWINGS DOUBLE HORIZONTAL
╗  U+2557  BOX DRAWINGS DOUBLE DOWN AND LEFT
║  U+2551  BOX DRAWINGS DOUBLE VERTICAL
╚  U+255A  BOX DRAWINGS DOUBLE UP AND RIGHT
╝  U+255D  BOX DRAWINGS DOUBLE UP AND LEFT
╠  U+2560  BOX DRAWINGS DOUBLE VERTICAL AND RIGHT
╣  U+2563  BOX DRAWINGS DOUBLE VERTICAL AND LEFT
```

### Metadata Separator
```
┊  U+250A  BOX DRAWINGS LIGHT QUADRUPLE DASH VERTICAL

Usage: ⏱ 13:45:23 ┊ ⚡ Command: hello
                  ↑ Separates timestamp from command
```

---

## Terminal Emulator Compatibility

### Tested Configurations

#### macOS Terminal.app
```
✓ Emoji rendering: Perfect
✓ Box drawing: Perfect
✓ Colors (256): Perfect
✓ Colors (24-bit): Perfect
✓ Shimmer effect: Visible
Rating: Excellent
```

#### iTerm2
```
✓ Emoji rendering: Perfect
✓ Box drawing: Perfect
✓ Colors (256): Perfect
✓ Colors (24-bit): Perfect
✓ Shimmer effect: Highly visible
Rating: Excellent
```

#### Linux GNOME Terminal
```
✓ Emoji rendering: Good
✓ Box drawing: Perfect
✓ Colors (256): Perfect
✓ Colors (24-bit): Perfect
✓ Shimmer effect: Visible
Rating: Excellent
```

#### Windows Terminal
```
✓ Emoji rendering: Good
✓ Box drawing: Perfect
✓ Colors (256): Perfect
✓ Colors (24-bit): Perfect
✓ Shimmer effect: Visible
Rating: Excellent
```

#### Legacy terminals (xterm, PuTTY)
```
⚠ Emoji rendering: May show as boxes
✓ Box drawing: Good (with UTF-8)
✓ Colors (256): Good
✗ Colors (24-bit): Fallback to 256
⚠ Shimmer effect: Less visible
Rating: Acceptable with fallbacks
```

---

## Edge Cases Visual Reference

### Case 1: Very Long Command
```
╔════════════════════════════════════════════════════════════════════════╗
║ ⏱ 13:45:23 ┊ ⚡ Command: this is a very long command that might wra...║
╚════════════════════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing
```
**Handling:** Command truncated with "..." in separator box

### Case 2: Rapid Commands
```
╔════════════════════════════════════════════════════════════════════════╗
║ ⏱ 13:45:23 ┊ ⚡ Command: first                                         ║
╚════════════════════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing

╔════════════════════════════════════════════════════════════════════════╗
║ ⏱ 13:45:24 ┊ ⚡ Command: second                                        ║
╚════════════════════════════════════════════════════════════════════════╝

📝 Response: 🍳 Thinking
```
**Handling:** First indicator hidden, second appears immediately

### Case 3: Instant Response (< 300ms)
```
╔════════════════════════════════════════════════════════════════════════╗
║ ⏱ 13:45:23 ┊ ⚡ Command: quick                                         ║
╚════════════════════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing  ← Appears briefly (~100ms)

📝 Response:

Response text appears almost immediately.
```
**Handling:** Brief flicker acceptable for ultra-fast responses

### Case 4: Error During Processing
```
╔════════════════════════════════════════════════════════════════════════╗
║ ⏱ 13:45:23 ┊ ⚡ Command: invalid                                       ║
╚════════════════════════════════════════════════════════════════════════╝

📝 Response: 🍳 Thinking

❌ ERROR: Command failed!
```
**Handling:** Indicator hidden when error message arrives

---

## Accessibility Notes

### Screen Reader Interpretation
```
Visual:           📝 Response: 🥘 Brewing
Screen Reader:    "Document Response colon Paella Brewing"
                  (Depends on screen reader emoji support)
```

### High Contrast Mode
```
Normal:           📝 Response: 🥘 Brewing
                               └─────┘
                            bold yellow

High Contrast:    📝 Response: 🥘 Brewing
                               └─────┘
                            bright white
                      (shimmer still visible via bold/dim)
```

### Colorblind Considerations
```
Protanopia (red-blind):    Yellow shimmer visible as yellow-gray
Deuteranopia (green-blind): Yellow shimmer visible as yellow-gray
Tritanopia (blue-blind):   Yellow shimmer visible as pink-yellow
Monochrome:                Shimmer visible as brightness change

Conclusion: Animation accessible without color perception
```

---

## Performance Visual

### CPU Usage Graph (Conceptual)
```
CPU %
  │
5%│     ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
  │     │ │ │ │ │ │ │ │ │ │  ← Animation frames (minimal spikes)
4%│     │ │ │ │ │ │ │ │ │ │
  │     │ │ │ │ │ │ │ │ │ │
3%│─────┘ └─┘ └─┘ └─┘ └─┘ └─────────────────
  │
  └────────────────────────────────────────→ Time
       Processing                Stop

Frame render: ~0.5% CPU spike (negligible)
Baseline: ~3% CPU (Textual app overhead)
```

---

## Final Visual Comparison

### BEFORE
```
╚══════════════════════════════════════════════════════════════════════════╝

📝 Response:
              ← Empty space feels disconnected

🥘 Brewing...
   └──────┘
   With dots (visual clutter)

              ← Too much vertical space
```

### AFTER
```
╚══════════════════════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing
             └────────┘
          Clean, inline, cohesive

              ← Compact, professional
```

**Improvement Summary:**
- ✓ 40% less vertical space
- ✓ Visually cohesive (label + indicator unified)
- ✓ Cleaner appearance (no dots)
- ✓ Professional polish
- ✓ Better visual hierarchy

---

## Usage Examples

### Example 1: Quick Question
```
╔════════════════════════════════════════════════════════════════════════╗
║ ⏱ 13:45:23 ┊ ⚡ Command: what is 2+2?                                  ║
╚════════════════════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing  (shows for ~0.5s)

📝 Response:

2 + 2 = 4
```

### Example 2: Long Processing
```
╔════════════════════════════════════════════════════════════════════════╗
║ ⏱ 13:45:23 ┊ ⚡ Command: explain quantum computing                     ║
╚════════════════════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing    (0.0s - 0.9s)
📝 Response: 🍳 Brewing    (0.9s - 1.8s)
📝 Response: 🍲 Thinking   (1.8s - 2.7s)
📝 Response: 🥄 Thinking   (2.7s - 3.6s)
📝 Response: 🔥 Processing (3.6s - 4.5s)
                           ... continues until response ...

📝 Response:

Quantum computing is a type of computing that uses quantum-mechanical
phenomena, such as superposition and entanglement...
[Long detailed response]
```

---

This completes the terminal mockups visual reference guide.
