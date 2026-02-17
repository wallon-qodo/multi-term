# Processing Indicator Layout Redesign

## Visual Design Specification

### Current Layout (BEFORE)
```
╚══════════════════════════════════════════════════════════╝

📝 Response:

🥘 Brewing...

(response text appears below)
```

### Desired Layout (AFTER)
```
╚══════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing

(animates in place with cycling emoji and word)

When response arrives:

📝 Response:

(actual response text)
```

## Design Requirements

### 1. Layout Requirements
- **Same line composition**: Label and indicator must appear on same line
- **Inline animation**: Animate within the same visual space
- **No extra blank lines**: Maintain compact spacing
- **Smooth transition**: Clean replacement when response arrives

### 2. Animation Requirements
- **Emoji cycling**: 🥘 → 🍳 → 🍲 → 🥄 → 🔥 (every 3 frames)
- **Word cycling**: Brewing → Thinking → Processing → Cooking → Working (every 6 frames)
- **Shimmer effect**: Yellow color pulsing through brightness levels
- **Single word only**: No dots/ellipsis (e.g., "Brewing" not "Brewing...")
- **Frame rate**: 0.3s per frame (300ms)

### 3. Visual Styling
- **Label color**: `rgb(150,255,150)` (green) to match "Response:" theme
- **Emoji**: Natural color (no style override)
- **Word shimmer**: Cycle through:
  - `bold yellow`
  - `bold bright_yellow`
  - `bold yellow`
  - `dim yellow`

## Technical Architecture

### Component Structure

```
SessionPane
├── session-header (Static)
├── terminal-output (RichLog)        ← Command separator + "📝 Response:" label
├── processing-inline (Static)        ← NEW: Inline processing indicator
└── command-input (Input)
```

### Key Changes

#### 1. New Processing Indicator Widget
- **Type**: Static widget with custom positioning
- **CSS class**: `processing-inline`
- **Positioning**: Absolute positioning to overlay after "📝 Response:"
- **Display mode**: `display: none` by default, `display: block` when active

#### 2. Modified Output Flow
```python
# When command submitted:
1. Write separator to RichLog:
   "╚═══...╝\n\n📝 Response: "  # Note: No newline after colon!

2. Show processing-inline widget:
   - Position it inline after the colon
   - Start animation loop
   - Content: "🥘 Brewing" (cycles)

3. When response arrives:
   - Hide processing-inline widget
   - Add newline to RichLog
   - Write response text
```

## CSS Design

### Color Palette
```css
/* Processing Indicator Colors */
--processing-bg: rgb(18,18,24);         /* Match terminal background */
--processing-text: rgb(220,220,240);    /* Match terminal text */
--label-color: rgb(150,255,150);        /* Green for "📝 Response:" */
--shimmer-1: yellow;                     /* Shimmer cycle colors */
--shimmer-2: bright_yellow;
--shimmer-3: yellow;
--shimmer-4: dim yellow;
```

### Layout Specification
```css
SessionPane .processing-inline {
    height: 1;                    /* Single line height */
    width: auto;                  /* Fit content */
    background: transparent;      /* No background - blend with RichLog */
    color: rgb(220,220,240);
    padding: 0 0 0 1;             /* Small left padding for spacing */
    display: none;                /* Hidden by default */
    dock: none;                   /* No docking behavior */
}

SessionPane .processing-inline.visible {
    display: block;               /* Show when active */
}
```

## Implementation Details

### 1. Widget Composition Update

**Location**: `session_pane.py` - `compose()` method (lines 131-158)

```python
def compose(self) -> ComposeResult:
    """Build the pane UI components."""
    yield Static(
        self._render_header(),
        classes="session-header",
        id=f"header-{self.session_id}"
    )
    yield RichLog(
        classes="terminal-output",
        id=f"output-{self.session_id}",
        highlight=True,
        markup=True,
        auto_scroll=True,
        max_lines=10000,
        wrap=True
    )
    # NEW: Inline processing indicator (replaces old processing-indicator)
    yield Static(
        "",
        classes="processing-inline",
        id=f"processing-inline-{self.session_id}"
    )
    yield Input(
        placeholder="⌨ Enter command or question...",
        classes="command-input",
        id=f"input-{self.session_id}"
    )
```

### 2. Command Submission Update

**Location**: `session_pane.py` - `on_input_submitted()` method (lines 471-562)

**Modified separator creation** (lines 489-514):
```python
# Create separator WITHOUT newline after "📝 Response:"
separator = Text()
separator.append("\n\n", style="")
separator.append("╔" + "═" * 78 + "╗\n", style="bold rgb(100,180,255)")
separator.append("║ ", style="bold rgb(100,180,255)")
separator.append(f"⏱ {timestamp} ", style="dim cyan")
separator.append("┊ ", style="dim white")
separator.append("⚡ Command: ", style="bold rgb(150,220,255)")
separator.append(command, style="bold rgb(255,220,100)")
padding = 78 - len(f"⏱ {timestamp} ┊ ⚡ Command: {command}") - 2
if padding > 0:
    separator.append(" " * padding, style="")
separator.append(" ║\n", style="bold rgb(100,180,255)")
separator.append("╚" + "═" * 78 + "╝\n", style="bold rgb(100,180,255)")
separator.append("\n📝 Response: ", style="bold rgb(150,255,150)")  # NO newline!

output_widget.write(separator)
output_widget.scroll_end(animate=False)
output_widget.refresh()
```

**Modified processing indicator setup** (lines 516-537):
```python
# Show inline processing indicator
processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)
processing_widget.display = True
processing_widget.add_class("visible")

# Initialize animation state
self._processing_start_time = __import__('time').time()
self._has_processing_indicator = True
self._animation_frame = 0
self._cooking_emojis = ["🥘", "🍳", "🍲", "🥄", "🔥"]
self._cooking_verbs = ["Brewing", "Thinking", "Processing", "Cooking", "Working"]

# Start with initial frame (NO DOTS!)
initial_text = Text()
initial_text.append("🥘 ", style="")
initial_text.append("Brewing", style="bold yellow")  # NO DOTS!
processing_widget.update(initial_text)

# Start animation
if hasattr(self, 'app') and self.app:
    self.app.set_timer(0.3, self._animate_processing)
```

### 3. Animation Update

**Location**: `session_pane.py` - `_animate_processing()` method (lines 370-418)

**Remove dots, keep shimmer** (lines 390-412):
```python
def _animate_processing(self) -> None:
    """Animate the processing indicator with shimmer and cycling icon."""
    try:
        # Stop if processing is done
        if not hasattr(self, '_has_processing_indicator') or not self._has_processing_indicator:
            return

        processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)

        # Increment frame
        self._animation_frame += 1

        # Cycle through emojis every 3 frames
        emoji_idx = (self._animation_frame // 3) % len(self._cooking_emojis)
        emoji = self._cooking_emojis[emoji_idx]

        # Cycle through verbs every 6 frames
        verb_idx = (self._animation_frame // 6) % len(self._cooking_verbs)
        verb = self._cooking_verbs[verb_idx]

        # Shimmer effect: cycle through brightness (NO DOTS!)
        shimmer_styles = [
            "bold yellow",
            "bold bright_yellow",
            "bold yellow",
            "dim yellow"
        ]
        shimmer_idx = self._animation_frame % len(shimmer_styles)
        shimmer_style = shimmer_styles[shimmer_idx]

        # Update the processing widget - NO DOTS!
        animation_text = Text()
        animation_text.append(f"{emoji} ", style="")
        animation_text.append(verb, style=shimmer_style)  # Just the word!

        processing_widget.update(animation_text)
        processing_widget.refresh()

        # Schedule next frame
        if hasattr(self, 'app') and self.app:
            self.app.set_timer(0.3, self._animate_processing)

    except Exception as e:
        self._log(f"Error in animation: {e}")
```

### 4. Response Arrival Handling

**Location**: `session_pane.py` - `_update_output()` method (lines 290-368)

**Clear indicator and add newline** (lines 327-334):
```python
# Clear processing indicator on first real output
if hasattr(self, '_has_processing_indicator') and self._has_processing_indicator:
    # Hide the inline processing indicator
    processing_widget = self.query_one(f"#processing-inline-{self.session_id}", Static)
    processing_widget.remove_class("visible")
    processing_widget.display = False
    self._has_processing_indicator = False

    # Add newline to move response text to next line
    output_widget.write(Text("\n"))
    self._log("Cleared processing indicator and added newline")
```

### 5. CSS Updates

**Location**: `session_pane.py` - `DEFAULT_CSS` (lines 26-88)

**Replace old processing-indicator CSS** (lines 62-72):
```css
SessionPane .processing-inline {
    height: 1;
    width: auto;
    background: transparent;
    color: rgb(220,220,240);
    padding: 0 0 0 1;
    display: none;
    dock: none;
}

SessionPane .processing-inline.visible {
    display: block;
}
```

## Animation Timing Diagram

```
Time    Emoji    Verb          Shimmer
────────────────────────────────────────
0.0s    🥘      Brewing       bold yellow
0.3s    🥘      Brewing       bold bright_yellow
0.6s    🥘      Brewing       bold yellow
0.9s    🍳      Brewing       dim yellow
1.2s    🍳      Brewing       bold yellow
1.5s    🍳      Brewing       bold bright_yellow
1.8s    🍲      Thinking      bold yellow
2.1s    🍲      Thinking      dim yellow
...
```

**Timing constants:**
- Emoji change: Every 0.9s (3 frames × 0.3s)
- Verb change: Every 1.8s (6 frames × 0.3s)
- Shimmer cycle: Every 1.2s (4 frames × 0.3s)

## Visual Mockup

### Processing State
```
╚══════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing
             ↑ Animates here, yellow shimmer
```

### Response Arrived
```
╚══════════════════════════════════════════════════════════╝

📝 Response:
             ↑ Processing indicator removed, newline added

Here is the actual response text from Claude...
```

## Testing Checklist

- [ ] Processing indicator appears on same line as "📝 Response:"
- [ ] No extra blank lines between label and indicator
- [ ] Emojis cycle correctly (🥘 → 🍳 → 🍲 → 🥄 → 🔥)
- [ ] Words cycle correctly (Brewing → Thinking → Processing → Cooking → Working)
- [ ] NO DOTS appear (just single word)
- [ ] Yellow shimmer effect is visible and smooth
- [ ] Indicator disappears when response arrives
- [ ] Response text appears on new line after label
- [ ] No layout glitches or flickering
- [ ] Works with multiple sessions
- [ ] Scrolling behavior is correct
- [ ] Animation stops when indicator is hidden

## Performance Considerations

- **Animation overhead**: 0.3s timer is lightweight
- **Widget updates**: Static.update() is efficient for single-line changes
- **Memory**: No accumulation - single widget reused
- **CPU**: Minimal - just string formatting and style changes

## Accessibility Notes

- Emoji provide visual variety
- Word changes provide semantic meaning
- Shimmer effect is subtle, not distracting
- Single-word format is easier to read
- Clear transition when response arrives
