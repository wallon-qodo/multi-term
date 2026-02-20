# Status Bar Visual Examples

## Layout Examples

### Normal Mode (Idle)
```
┃ 🎯 NORMAL ┃  Sonnet 4.5  ┊  0 tok ($0.00)  ┊  14:32  ┊  CPU: 45%  ┊  MEM: 60%  ┊  Darwin
i:Insert ┊ v:Copy ┊ ^B:Command ┊ n:New ┊ x:Close ┊ h/j/k/l:Navigate ┊ r:Rename ┊ q:Quit
```

### Normal Mode (Streaming Active)
```
┃ 🎯 NORMAL ┃  ⠋ 127 tok (45 tok/s)  ┊  Sonnet 4.5  ┊  1.2K tok ($0.05)  ┊  14:32  ┊  CPU: 45%  ┊  MEM: 60%  ┊  Darwin
i:Insert ┊ v:Copy ┊ ^B:Command ┊ n:New ┊ x:Close ┊ h/j/k/l:Navigate ┊ r:Rename ┊ q:Quit
```

### Insert Mode (Streaming)
```
┃ ✏️ INSERT ┃  ⠙ 523 tok (62 tok/s)  ┊  Opus 4.6  ┊  15.6K tok ($1.24)  ┊  14:33  ┊  CPU: 78%  ┊  MEM: 72%  ┊  Darwin
ESC:Normal ┊ Type:Input to session ┊ Enter:Submit ┊ Shift+Enter:Newline
```

### Copy Mode
```
┃ 📋 COPY ┃  Haiku 4.5  ┊  234 tok ($0.01)  ┊  14:34  ┊  CPU: 32%  ┊  MEM: 55%  ┊  Darwin
ESC:Normal ┊ j/k:Scroll ┊ d/u:Half Page ┊ f/b:Full Page ┊ g/G:Top/Bottom ┊ y:Yank
```

### Command Mode
```
┃ ⚡ COMMAND ┃  Sonnet 4.5  ┊  5.8K tok ($0.42)  ┊  14:35  ┊  CPU: 56%  ┊  MEM: 64%  ┊  Darwin
ESC:Cancel ┊ c:New ┊ x:Close ┊ n/p:Next/Prev ┊ [:Copy mode ┊ r:Rename
```

### Broadcast Mode (Active)
```
┃ 🎯 NORMAL ┃  ⠹ 89 tok (38 tok/s)  ┊  Sonnet 4.5  ┊  2.4K tok ($0.18)  ┊  ┃ 📡 BROADCAST  ┃  ┊  14:36  ┊  CPU: 61%  ┊  MEM: 68%  ┊  Darwin
i:Insert ┊ v:Copy ┊ ^B:Command ┊ n:New ┊ x:Close ┊ h/j/k/l:Navigate ┊ r:Rename ┊ q:Quit
```

## Color Coding Reference

### Mode Indicators
- **Normal**: Blue `rgb(100,180,240)` - Border: heavy blue
- **Insert**: Green `rgb(120,200,120)` - Border: heavy green
- **Copy**: Orange `rgb(255,180,70)` - Border: heavy orange
- **Command**: Red `rgb(255,77,77)` - Border: heavy red

### Streaming Indicator
- **Spinner**: Bold blue `rgb(100,180,240)`
- **Token Count**: Gray `rgb(180,180,180)`
- **Speed**: Light gray `rgb(120,120,120)`

### Model Name
- **All Models**: Bold coral red `rgb(255,77,77)`

### Token Usage
- **Token Count**: Gray `rgb(180,180,180)`
- **Cost < $0.10**: Bold green `rgb(120,200,120)`
- **Cost $0.10-$1.00**: Bold yellow `rgb(255,180,70)`
- **Cost > $1.00**: Bold red `rgb(255,77,77)`

### System Metrics
- **CPU < 50%**: Green `rgb(120,200,120)`
- **CPU 50-80%**: Yellow `rgb(255,180,70)`
- **CPU > 80%**: Red `rgb(255,77,77)`
- **MEM < 60%**: Green `rgb(120,200,120)`
- **MEM 60-80%**: Yellow `rgb(255,180,70)`
- **MEM > 80%**: Red `rgb(255,77,77)`

### Separators
- **Main**: Gray `rgb(60,60,60)` `┊`
- **Mode Border**: Mode color `┃`

## Spinner Animation Sequence (10fps)

```
Frame 0: ⠋
Frame 1: ⠙
Frame 2: ⠹
Frame 3: ⠸
Frame 4: ⠼
Frame 5: ⠴
Frame 6: ⠦
Frame 7: ⠧
Frame 8: ⠇
Frame 9: ⠏
(repeat)
```

## Token Formatting Examples

| Actual Tokens | Display Format |
|--------------|----------------|
| 0            | `0 tok`        |
| 127          | `127 tok`      |
| 999          | `999 tok`      |
| 1,234        | `1.2K tok`     |
| 15,678       | `15.7K tok`    |
| 123,456      | `123.5K tok`   |

## Cost Formatting Examples

| Actual Cost | Display | Color |
|------------|---------|-------|
| $0.00      | `($0.00)` | Green |
| $0.05      | `($0.05)` | Green |
| $0.09      | `($0.09)` | Green |
| $0.18      | `($0.18)` | Yellow |
| $0.42      | `($0.42)` | Yellow |
| $0.99      | `($0.99)` | Yellow |
| $1.24      | `($1.24)` | Red |
| $15.67     | `($15.67)` | Red |

## State Transitions

### Idle → Streaming
1. User submits request
2. `stream_state` = `CONNECTING`
3. Spinner appears, no speed/tokens yet
4. `stream_state` = `STREAMING`
5. Spinner animates, speed/tokens update

### Streaming → Complete
1. Response finishes
2. `stream_state` = `COMPLETE`
3. Spinner stops, final tokens/speed shown
4. After 2 seconds: indicator fades out
5. `stream_state` = `IDLE`

### Error Handling
1. Error occurs during streaming
2. `stream_state` = `ERROR`
3. Spinner changes to error indicator (future)
4. After 2 seconds: returns to `IDLE`

## Performance Characteristics

- **Update Frequency**: 100ms (10fps) during streaming
- **Refresh Time**: < 10ms per render
- **Memory**: ~50 bytes per reactive property
- **Animation Overhead**: Negligible (single frame index)

## Integration Timeline

1. **Phase 4a (Complete)**: Status bar structure and reactive properties
2. **Phase 4b (Agent 1)**: StreamMonitor integration
3. **Phase 4c (Agent 2)**: TokenTracker integration
4. **Phase 4d (Testing)**: End-to-end validation

## Spacing and Alignment

The status bar uses consistent spacing:
- Between sections: `  ` (2 spaces)
- Around separators: `  ┊  ` (2 spaces each side)
- Mode indicator: ` ` (1 space padding inside)

Total width adapts to terminal width, with Line 2 keybindings wrapping if needed.

## Known Limitations

1. No tooltip support yet (Textual limitation)
2. No click interactions (future enhancement)
3. Fixed 3-line height (design choice)
4. No session name display yet (future enhancement)
5. Time updates on refresh only (not continuous clock)

## Testing Scenarios

### Scenario 1: Quick Response
```
IDLE → CONNECTING (50ms) → STREAMING (200ms) → COMPLETE → IDLE
Tokens: 0 → 0 → 45 → 45 → 0
Speed: 0 → 0 → 225 tok/s → 225 tok/s → 0
```

### Scenario 2: Long Streaming Response
```
IDLE → CONNECTING (100ms) → STREAMING (5000ms) → COMPLETE → IDLE
Tokens: 0 → 0 → 50...250...450...750...1250 → 1250 → 0
Speed: 0 → 0 → 25...48...52...51...50 tok/s → 50 tok/s → 0
```

### Scenario 3: Error During Streaming
```
IDLE → CONNECTING (50ms) → STREAMING (1000ms) → ERROR → IDLE
Tokens: 0 → 0 → 120 → 120 → 0
Speed: 0 → 0 → 45 tok/s → 0 → 0
```

### Scenario 4: Multiple Requests
```
Request 1: Session tokens 0 → 450 ($0.03)
Request 2: Session tokens 450 → 1200 ($0.08)
Request 3: Session tokens 1200 → 5600 ($0.38)
Cost color: Green → Green → Yellow
```
