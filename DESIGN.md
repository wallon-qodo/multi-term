# Claude Multi-Terminal - Enterprise Design System

## Overview
This document outlines the enterprise-grade design system implemented in Claude Multi-Terminal, a professional TUI application for managing multiple Claude CLI sessions.

## Design Philosophy

### Core Principles
1. **Professional Aesthetics** - Polished, modern interface that feels like a premium development tool
2. **Visual Hierarchy** - Clear information architecture with proper emphasis and spacing
3. **Functional Beauty** - Every visual element serves a purpose
4. **Consistency** - Unified visual language throughout the application
5. **Accessibility** - High contrast, readable fonts, clear focus indicators

## Color Palette

### Background Colors
```
Primary Background:   rgb(15,15,22)   - Main application background
Secondary Background: rgb(20,20,28)   - Session panes
Tertiary Background:  rgb(25,25,35)   - Elevated elements
Input Background:     rgb(30,30,40)   - Input fields
Header Background:    rgb(40,40,55)   - Headers and titles
```

### Accent Colors
```
Primary Accent:   rgb(100,150,255)  - Blue - Primary actions, focus states
Secondary Accent: rgb(150,200,255)  - Light Blue - Highlights
Success:          rgb(100,255,150)  - Green - Success states
Warning:          rgb(255,180,50)   - Orange - Warnings
Error:            rgb(255,100,100)  - Red - Errors
Info:             rgb(100,200,255)  - Cyan - Informational
```

### Text Colors
```
Primary Text:   rgb(220,220,240)  - Main content
Secondary Text: rgb(180,180,200)  - Supporting text
Dim Text:       rgb(120,120,150)  - De-emphasized text
Bright Text:    rgb(240,245,255)  - Emphasized text
```

## Typography

### Font Weights & Styles
- **Bold** - Headers, titles, important labels
- **Normal** - Body text, content
- **Dim** - Secondary information, metadata

### Text Hierarchy
1. **H1 (Application Title)** - Bold, large, accent colored
2. **H2 (Section Headers)** - Bold, medium, with icons
3. **H3 (Labels)** - Bold, normal size
4. **Body** - Normal weight, readable
5. **Caption** - Dim, smaller context

## Visual Elements

### Box Drawing Characters

#### Double Line Borders (Premium Elements)
```
╔═══════════════════╗
║                   ║
╚═══════════════════╝
```
Used for: Command separators, session initialization

#### Single Line Borders (Standard Elements)
```
┌───────────────────┐
│                   │
└───────────────────┘
```
Used for: Dialogs, containers

#### Rounded Borders (Soft Elements)
```
╭───────────────────╮
│                   │
╰───────────────────╯
```
Used for: Response completion markers, notifications

#### Heavy Borders (Focus States)
```
┏━━━━━━━━━━━━━━━━━━━┓
┃                   ┃
┗━━━━━━━━━━━━━━━━━━━┛
```
Used for: Focused panes, primary borders

### Separators
- **Light**: `┊` - Between keybindings
- **Medium**: `│` - Section dividers
- **Heavy**: `┃` - Major separators
- **Dashed**: `┄` - Subtle divisions

## Component Design

### Header Bar
```
╔═══ ⚡ CLAUDE MULTI-TERMINAL ┃ ● 2 Active ═══╗  ┃ 🕐 14:30
```

**Design Elements:**
- Double-line decorative borders
- Lightning bolt icon for branding
- Active session badge with status dot
- Real-time clock on the right
- Gradient background

**Color Scheme:**
- Background: `rgb(25,25,35)`
- Text: `rgb(200,220,255)`
- Accent: `rgb(100,150,255)`
- Active dot: Green when ≤4 sessions, Yellow when >4

### Session Pane

#### Header
```
● ┃ Development Session  ┊  📊 15 cmd  ┊  ID: a3f2e1
```

**Design Elements:**
- Status indicator (● active, ○ inactive)
- Session name (bold white)
- Command counter with chart icon
- Short session ID
- Gradient background (darker when unfocused, blue gradient when focused)

**States:**
- **Unfocused**: Gray gradient, dim text
- **Focused**: Blue gradient, bright text, heavy border

#### Terminal Output
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ ⏱ 14:30:45 ┊ ⚡ Command: help                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

📝 Response:
[Claude's response here...]

╭───────────────────────────────────────────────────────────────────────────────╮
│ ✓ Response complete                                                           │
╰───────────────────────────────────────────────────────────────────────────────╯
```

**Design Elements:**
- **Command Separator**: Double-line box with timestamp and command
- **Response Header**: Green "📝 Response:" label
- **Completion Marker**: Rounded box with checkmark
- Dark background for better readability
- ANSI color support for Claude's output

#### Input Field
```
⌨ Enter command or question...
```

**Design Elements:**
- Keyboard icon prefix
- Contextual placeholder text
- Heavy top border
- Focus state with blue accent

### Status Bar

#### Line 1: Mode & Metrics
```
┃ Ready ┃  CPU: 45%  ┊  MEM: 62%  ┊  Darwin
```

**Normal Mode:**
- Green "Ready" status
- System metrics (CPU, MEM)
- Platform name

```
┃ 📡 BROADCAST MODE ACTIVE ┃ Commands sent to ALL sessions
```

**Broadcast Mode:**
- Orange background
- Radio icon
- Warning styling

#### Line 2: Keybindings
```
^N:New ┊ ^W:Close ┊ ^S:Save ┊ ^R:Rename ┊ ^B:Broadcast ┊ ^C:Copy ┊ F2:Mouse ┊ Tab:Next ┊ ^Q:Quit
```

**Design Elements:**
- Color-coded keybindings
- Light separators
- Action-color mapping:
  - Create (New): Blue
  - Destroy (Close): Red
  - Save: Green
  - Edit (Rename): Yellow
  - Broadcast: Orange
  - Copy: Purple
  - Navigation: Cyan

### Dialogs

#### Rename Dialog
```
╔═════════════════════════════════════════════════════════╗
║  ✏ Rename Session                                       ║
║  Enter a new name for this session:                     ║
║  [Current Name                        ]                 ║
║                                                          ║
║              [✓ Confirm]  [✗ Cancel]                    ║
╚═════════════════════════════════════════════════════════╝
```

**Design Elements:**
- Heavy blue border
- Icon in title
- Clear labels
- Styled buttons (primary/secondary)
- Centered layout

### Notifications

#### Types
1. **Information** (Blue)
   - ✓ Success operations
   - 💡 Tips and hints
   - ⚡ General notifications

2. **Warning** (Orange)
   - ⚠ Caution messages
   - 📡 Broadcast mode alerts
   - Clipboard fallback notices

3. **Error** (Red)
   - ❌ Failed operations
   - Critical issues

## Icons & Symbols

### Status Icons
- `●` Active/Online
- `○` Inactive/Offline
- `⚡` Active processing
- `✓` Success
- `❌` Error
- `⚠` Warning

### Action Icons
- `⌨` Keyboard input
- `🖱` Mouse
- `📋` Clipboard
- `💾` Save
- `✏` Edit/Rename
- `📡` Broadcast
- `🕐` Time/Clock
- `📊` Metrics/Stats
- `💡` Information/Tip
- `🔖` Bookmark/ID

## Layout & Spacing

### Grid System
- 2 sessions: 2x1 (side-by-side)
- 3-4 sessions: 2x2 grid
- 5-6 sessions: 2x3 grid
- 1 cell gutter between panes

### Padding
- Screen edges: 1-2 cells
- Component padding: 1-2 cells
- Input fields: 0-2 horizontal

### Borders
- Session panes: Heavy borders (double width)
- Dialogs: Heavy borders
- Internal elements: Solid borders
- Focus: Heavy borders with blue color

## Interactive States

### Focus States
1. **Unfocused Pane**
   - Gray border `rgb(70,70,90)`
   - Dark background
   - Dim header

2. **Focused Pane**
   - Blue border `rgb(100,150,255)`
   - Slightly lighter background
   - Bright blue header gradient

3. **Input Focus**
   - Blue border on input field
   - Lighter input background
   - Cursor visible

### Activity States
1. **Active Session**
   - Green status dot (●)
   - "Active" label in header
   - Command counter visible

2. **Idle Session**
   - White hollow dot (○)
   - No "Active" label
   - Dimmed appearance

## Animations & Transitions

### Smooth Transitions
- Focus state changes (border color)
- Broadcast mode toggle (background color)
- Notification appearance (slide in)

### No Animation
- Text output (instant rendering)
- Scrolling (instant for responsiveness)
- Pane resizing (instant layout)

## Accessibility

### Contrast Ratios
- Text on background: >7:1 (AAA)
- UI elements: >4.5:1 (AA)
- Focus indicators: >3:1

### Keyboard Navigation
- Tab/Shift+Tab: Navigate between panes
- All features accessible via keyboard
- Clear focus indicators

### Color Independence
- Status not conveyed by color alone
- Icons and text labels accompany colors
- High contrast mode compatible

## Implementation Notes

### Textual CSS
- Uses RGB color values for precise control
- Linear gradients for premium feel
- Heavy borders for emphasis
- Proper padding and spacing

### Rich Text Rendering
- ANSI color support in output
- Rich Text objects for styled content
- Markup support for dynamic styling

### Unicode Support
- Full box-drawing character set
- Emoji support for icons
- Braille patterns available but not used (too subtle)

## Design Decisions

### Why Dark Theme?
- Reduces eye strain for long sessions
- Professional developer tool aesthetic
- Better contrast for syntax highlighting
- Modern, premium appearance

### Why Heavy Borders?
- Clear visual separation
- Professional appearance
- Better emphasis on focus states
- Enterprise-grade polish

### Why RGB Colors?
- Precise color control
- Better than 256-color palette
- True color support in modern terminals
- Consistent across platforms

### Why Icons?
- Quick visual recognition
- International (language-independent)
- Modern, friendly appearance
- Reduces text density

## Future Enhancements

### Potential Additions
1. **Themes** - Light/Dark/Custom theme switching
2. **Color Blind Modes** - Deuteranopia, Protanopia, Tritanopia
3. **Session Icons** - Custom icons per session
4. **Progress Bars** - Visual feedback for long operations
5. **Sparklines** - CPU/Memory mini-graphs
6. **Tabs** - Alternative to grid layout
7. **Panel Shadows** - Subtle depth effects

### Performance Considerations
- Minimize redraws
- Efficient ANSI filtering
- Lazy rendering for off-screen content
- Debounced metric updates

## Conclusion

This design system creates a professional, polished TUI application that feels like an enterprise-grade development tool. Every visual element has been carefully considered for both aesthetics and functionality, resulting in a cohesive, accessible, and pleasant user experience.
