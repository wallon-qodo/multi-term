# Visual Guide - Processing Indicator with Real-Time Metrics

## Display Anatomy

```
📝 Response: 🥘 Brewing (1m 9s · ↓ 1.3k tokens · thought for 1m 9s)
^           ^   ^       ^                                          ^
│           │   │       │                                          │
│           │   │       └─ Metrics Section (dim, static)          │
│           │   └─ Processing Word (animated, shimmer effect)     │
│           └─ Cooking Emoji (cycles every 3 frames)              │
└─ Response Label (bold green, static)                            │
                                                                   │
                                                                   │
                       Response text starts here when ready ──────┘
```

## Component Breakdown

### 1. Response Label
```
📝 Response:
```
- **Style:** Bold green (`bold rgb(150,255,150)`)
- **Behavior:** Static, never changes
- **Purpose:** Labels the response section

### 2. Cooking Emoji
```
🥘 🍳 🍲 🥄 🔥
```
- **Style:** Default color
- **Behavior:** Cycles through 5 emojis every 3 animation frames
- **Purpose:** Visual indicator of activity

### 3. Processing Verb
```
Brewing  Thinking  Processing  Cooking  Working
```
- **Style:** Shimmer effect (cycles through 4 brightness levels)
  - `bold yellow`
  - `bold bright_yellow`
  - `bold yellow`
  - `dim yellow`
- **Behavior:** Cycles through 5 verbs every 6 animation frames
- **Purpose:** Action descriptor with visual interest

### 4. Metrics Section
```
(1m 9s · ↓ 1.3k tokens · thought for 1m 9s)
```
- **Style:** Dim colors (non-distracting)
  - Parentheses: `dim white`
  - Time values: `dim cyan`
  - Separators: `dim white`
  - Token arrow: `dim white`
  - Token count: `dim cyan`
  - Thinking label: `dim white`
- **Behavior:** Updates every 0.5 seconds (no animation)
- **Purpose:** Real-time progress feedback

## Animation Timeline

### Frame-by-Frame Progression

```
Frame 0:  📝 Response: 🥘 Brewing    (0s · ↓ 0 tokens · thought for 0s)
Frame 1:  📝 Response: 🥘 Brewing    (0s · ↓ 12 tokens · thought for 0s)
Frame 2:  📝 Response: 🥘 Brewing    (0s · ↓ 34 tokens · thought for 0s)
Frame 3:  📝 Response: 🍳 Brewing    (1s · ↓ 67 tokens · thought for 1s)
Frame 4:  📝 Response: 🍳 Brewing    (1s · ↓ 89 tokens · thought for 1s)
Frame 5:  📝 Response: 🍳 Brewing    (1s · ↓ 123 tokens · thought for 1s)
Frame 6:  📝 Response: 🍲 Thinking   (2s · ↓ 156 tokens · thought for 2s)
Frame 7:  📝 Response: 🍲 Thinking   (2s · ↓ 189 tokens · thought for 2s)
Frame 8:  📝 Response: 🍲 Thinking   (2s · ↓ 234 tokens · thought for 2s)
Frame 9:  📝 Response: 🥄 Processing (3s · ↓ 267 tokens · thought for 3s)
...
```

### Shimmer Effect Visualization

```
Frame 0: Brewing  ←─ bold yellow
Frame 1: Brewing  ←─ bold bright_yellow (brighter)
Frame 2: Brewing  ←─ bold yellow
Frame 3: Brewing  ←─ dim yellow (dimmer)
Frame 4: Brewing  ←─ bold yellow
...
```

## State Transitions

### 1. Command Submitted
```
User types: "What is 2+2?"
            [ENTER]
                │
                ▼
╔══════════════════════════════════════════════════════════════╗
║ ⏱ 12:34:56 ┊ ⚡ Command: What is 2+2?                       ║
╚══════════════════════════════════════════════════════════════╝

📝 Response: 🥘 Brewing (0s · ↓ 0 tokens · thought for 0s)
             └─────────┘ └───────────────────────────────┘
             Animated    Metrics (updating)
```

### 2. Processing (Metrics Update)
```
After 2.5 seconds, 234 tokens received:

📝 Response: 🍲 Processing (2s · ↓ 234 tokens · thought for 2s)
             └──────────┘
             Animation continues
```

### 3. Response Starts Arriving
```
First substantial output arrives:

📝 Response:
The answer is 4. This is a simple arithmetic calculation...
└─────────────┘
Processing indicator removed, response starts on new line
```

### 4. Response Complete
```
Response finishes:

The answer is 4. This is a simple arithmetic calculation...

✻ Baked for 3s
  └───────────┘
  Completion marker
```

## Metrics Formatting Rules

### Elapsed Time
```
0-59 seconds:     "3s", "15s", "45s"
60+ seconds:      "1m 0s", "1m 30s", "2m 15s"
```

### Token Count
```
0-999:            "0", "234", "567"
1000+:            "1.2k", "3.4k", "12.5k"
```

### Thinking Time
```
Same as elapsed time (for now)
```

## Layout Examples

### Short Response (Under 10 seconds)
```
📝 Response: 🥘 Brewing (0s · ↓ 0 tokens · thought for 0s)
📝 Response: 🍳 Thinking (1s · ↓ 23 tokens · thought for 1s)
📝 Response: 🍲 Processing (2s · ↓ 87 tokens · thought for 2s)
📝 Response:
The answer is 4.

✻ Baked for 2s
```

### Medium Response (Under 1 minute)
```
📝 Response: 🥘 Brewing (0s · ↓ 0 tokens · thought for 0s)
📝 Response: 🍳 Thinking (3s · ↓ 156 tokens · thought for 3s)
📝 Response: 🍲 Processing (7s · ↓ 432 tokens · thought for 7s)
📝 Response: 🥄 Cooking (12s · ↓ 789 tokens · thought for 12s)
📝 Response: 🔥 Working (18s · ↓ 1.1k tokens · thought for 18s)
📝 Response:
[Long detailed response starts here...]

✻ Sautéed for 23s
```

### Long Response (Over 1 minute)
```
📝 Response: 🥘 Brewing (0s · ↓ 0 tokens · thought for 0s)
📝 Response: 🍳 Thinking (5s · ↓ 234 tokens · thought for 5s)
📝 Response: 🍲 Processing (15s · ↓ 876 tokens · thought for 15s)
📝 Response: 🥄 Cooking (30s · ↓ 1.5k tokens · thought for 30s)
📝 Response: 🔥 Working (45s · ↓ 2.3k tokens · thought for 45s)
📝 Response: 🥘 Brewing (1m 5s · ↓ 3.1k tokens · thought for 1m 5s)
📝 Response: 🍳 Thinking (1m 25s · ↓ 4.2k tokens · thought for 1m 25s)
📝 Response:
[Very long detailed response starts here...]

✻ Churned for 1m 42s
```

## Color Palette

### Response Label
- RGB: `(150, 255, 150)` - Bright green
- Style: Bold

### Animated Indicator
- Emoji: Default terminal colors
- Verb: Yellow with shimmer
  - Bright: RGB `(255, 255, 0)`
  - Dim: RGB `(128, 128, 0)`

### Metrics
- Time values: Dim cyan RGB `(0, 139, 139)`
- Token counts: Dim cyan RGB `(0, 139, 139)`
- Separators/labels: Dim white RGB `(169, 169, 169)`

## Responsive Behavior

### Terminal Width Considerations
```
Wide terminal (120+ cols):
📝 Response: 🥘 Brewing (1m 9s · ↓ 1.3k tokens · thought for 1m 9s)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        Plenty of space for metrics

Narrow terminal (80 cols):
📝 Response: 🥘 Brewing (1m 9s · ↓ 1.3k tokens · thought for 1m 9s)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        Still fits comfortably
```

### Very Long Time/Token Counts
```
After 10 minutes with many tokens:
📝 Response: 🥘 Brewing (10m 45s · ↓ 12.3k tokens · thought for 10m 45s)
                        Max expected: ~55 characters
```

## User Experience Flow

```
User Input
    │
    ▼
Command Submitted
    │
    ▼
Processing Indicator Appears ─┐
    │                         │
    ├─ Emoji cycles           │
    ├─ Verb shimmers          ├─ Real-time feedback
    └─ Metrics update         │
          every 0.5s          │
    │                         │
    ▼                         ┘
First Output Arrives
    │
    ▼
Indicator Disappears
    │
    ▼
Response Displays
    │
    ▼
Completion Marker
```

## Accessibility Notes

### Visual Indicators
- Emoji provides visual variety
- Verb provides text-based status
- Shimmer provides motion cue
- Metrics provide quantitative feedback

### Color Contrast
- Bold colors for important info (response label, animated verb)
- Dim colors for secondary info (metrics)
- Good contrast ratio for readability

### Screen Reader Compatibility
- Text-based (no images)
- Meaningful emojis with semantic value
- Clear structure (label → indicator → metrics)

## Testing Checklist

Use this visual guide to verify:

- [ ] Response label appears in bold green
- [ ] Emoji cycles through all 5 cooking icons
- [ ] Verb cycles through all 5 action words
- [ ] Shimmer effect visible on verb
- [ ] Metrics appear in parentheses
- [ ] Time format changes at 60 seconds
- [ ] Token format changes at 1000 tokens
- [ ] Separators are " · " (space-bullet-space)
- [ ] Token arrow "↓" displays correctly
- [ ] Metrics are dim (not distracting)
- [ ] Updates occur every 0.5 seconds
- [ ] Indicator disappears when response starts
- [ ] Response starts on new line

---

**Pro Tip:** Run `python3 simulate_metrics.py` to see these visual patterns in action!
