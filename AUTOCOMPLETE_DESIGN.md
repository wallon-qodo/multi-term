# Slash Command Autocomplete - Design Documentation

## Visual Design Mockup

### Default State (No Autocomplete)
```
┌─────────────────────────────────────────────────────────────────────┐
│ ● ┃ Session 1                    ┊  📊 5 cmd  ┊  ID: abc123        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Terminal output content here...                                     │
│                                                                       │
│                                                                       │
├─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┤
│ ⌨ Enter command or question...                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Autocomplete Shown (User types "/")
```
┌─────────────────────────────────────────────────────────────────────┐
│ ● ┃ Session 1                    ┊  📊 5 cmd  ┊  ID: abc123        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Terminal output content here...                                     │
│                                                                       │
│                                                                       │
├─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┤
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓                 │
│ ┃ ╭─ Slash Commands ─╮                            ┃                 │
│ ┃ /model    Switch Claude model (Sonnet/Opus)     ┃  ⬅ Highlighted  │
│ ┃ /help     Show help and available commands      ┃                 │
│ ┃ /logout   Logout from Claude CLI                ┃                 │
│ ┃ /commit   Create a git commit with changes      ┃                 │
│ ┃ /review-pr Review a GitHub pull request         ┃                 │
│ ┃ /test     Run tests for the project             ┃                 │
│ ┃ /debug    Debug mode and diagnostics            ┃                 │
│ ┃ /clear    Clear the conversation history        ┃                 │
│ ┃ /save     Save current session state            ┃                 │
│ ┃ /load     Load a saved session                  ┃                 │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                 │
├─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┤
│ /                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Filtered Autocomplete (User types "/m")
```
┌─────────────────────────────────────────────────────────────────────┐
│ ● ┃ Session 1                    ┊  📊 5 cmd  ┊  ID: abc123        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Terminal output content here...                                     │
│                                                                       │
│                                                                       │
├─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┤
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓                 │
│ ┃ ╭─ Slash Commands ─╮                            ┃                 │
│ ┃ /model    Switch Claude model (Sonnet/Opus)     ┃  ⬅ Highlighted  │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                 │
├─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┤
│ /m                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Color Scheme (Homebrew Theme)

### Dropdown Container
- **Background**: `rgb(40,40,40)` - Warm charcoal (elevated surface)
- **Border**: `rgb(255,183,77)` - Amber gold (focus indicator)
- **Border Style**: Heavy weight (━)

### Header
- **Background**: `rgb(48,48,48)` - Subtle darker shade
- **Text**: `rgb(255,213,128)` - Light amber
- **Text**: "╭─ Slash Commands ─╮"

### Option List Items
- **Normal State**:
  - Background: `rgb(40,40,40)` - Matches dropdown
  - Command text: `rgb(255,213,128)` - Bold light amber
  - Description: `rgb(189,189,189)` - Dim gray

- **Highlighted State**:
  - Background: `rgb(255,183,77)` - Amber gold
  - Text: `rgb(24,24,24)` - Dark charcoal (inverted for contrast)

### Layout Specifications
- **Width**: 50 columns (adjustable)
- **Max Height**: 12 rows
- **Position**: Directly above input field
- **Layer**: Overlay (floats above other content)

## User Interaction Flow

### 1. Trigger Autocomplete
- User types "/" in the input field
- Dropdown appears immediately
- All commands are shown
- First command is highlighted

### 2. Filter Commands
- User continues typing (e.g., "/mod")
- List filters in real-time
- Only matching commands shown
- Highlight stays on first item
- If no matches, dropdown hides

### 3. Navigate
- **Arrow Up**: Move highlight up (wraps to bottom)
- **Arrow Down**: Move highlight down (wraps to top)
- Visual feedback: highlighted row changes color

### 4. Select Command
- **Enter Key**: Insert highlighted command + space
- **Tab Key**: Insert highlighted command + space
- **Mouse Click**: Insert clicked command + space
- Cursor moves to end of inserted text
- Dropdown hides
- Input field retains focus

### 5. Dismiss
- **Escape Key**: Hide dropdown
- **Type non-slash**: Hide dropdown (e.g., backspace to empty)
- **Click elsewhere**: Hide dropdown

## Available Slash Commands

| Command | Description |
|---------|-------------|
| `/model` | Switch Claude model (Sonnet/Opus/Haiku) |
| `/help` | Show help and available commands |
| `/logout` | Logout from Claude CLI |
| `/commit` | Create a git commit with changes |
| `/review-pr` | Review a GitHub pull request |
| `/test` | Run tests for the project |
| `/debug` | Debug mode and diagnostics |
| `/clear` | Clear the conversation history |
| `/save` | Save current session state |
| `/load` | Load a saved session |
| `/plan` | Enable plan mode for complex tasks |
| `/web` | Search the web for information |
| `/diff` | Show git diff of changes |
| `/status` | Show git status |
| `/branch` | Git branch operations |
| `/config` | Configure Claude CLI settings |
| `/version` | Show Claude CLI version |
| `/docs` | Open documentation |
| `/feedback` | Send feedback to Anthropic |
| `/privacy` | Privacy and data handling info |

## Implementation Details

### Components Used
- **OptionList**: Textual's built-in widget for selectable lists
- **Vertical Container**: Wraps header + option list
- **Static**: Header text with box-drawing characters

### Event Handlers
1. **`@on(Input.Changed)`**: Detects "/" and filters commands
2. **`on_key()`**: Handles arrow keys, Enter, Tab, Escape
3. **`@on(OptionList.OptionSelected)`**: Handles mouse clicks

### State Management
- `_autocomplete_visible`: Boolean flag for dropdown state
- `_slash_commands`: List of (command, description) tuples
- Dropdown visibility toggled via CSS class "visible"

### Key Features
- ✓ Real-time filtering as user types
- ✓ Keyboard navigation (arrow keys)
- ✓ Multiple selection methods (Enter/Tab/Click)
- ✓ Escape to dismiss
- ✓ Auto-hide when not typing "/"
- ✓ Maintains input focus after selection
- ✓ Adds space after command for convenience
- ✓ Enterprise-grade styling matching app theme

## Testing Checklist

- [ ] Type "/" and verify dropdown appears
- [ ] Type "/m" and verify only "/model" shows
- [ ] Arrow down/up navigates correctly
- [ ] Enter key selects and inserts command
- [ ] Tab key selects and inserts command
- [ ] Mouse click selects and inserts command
- [ ] Escape key dismisses dropdown
- [ ] Backspace to remove "/" hides dropdown
- [ ] Typing "//" (comment) hides dropdown
- [ ] Works correctly in split-pane view
- [ ] Dropdown doesn't interfere with command submission
- [ ] Visual styling matches Homebrew theme
- [ ] Highlight color has good contrast
- [ ] Text is readable in both light/dark terminals

## File Modified

**File**: `/Users/wallonwalusayi/claude-multi-terminal/claude_multi_terminal/widgets/session_pane.py`

### Changes Made:
1. Added imports: `OptionList`, `Option`, `on`
2. Added CSS for `.autocomplete-dropdown`, `.autocomplete-header`, and option states
3. Added `_autocomplete_visible` flag and `_slash_commands` list in `__init__`
4. Added autocomplete dropdown to `compose()` method
5. Implemented `_show_autocomplete()` method
6. Implemented `_hide_autocomplete()` method
7. Implemented `_get_selected_command()` method
8. Added `@on(Input.Changed)` handler for detecting "/"
9. Added `on_key()` handler for arrow/Enter/Tab/Escape keys
10. Added `@on(OptionList.OptionSelected)` handler for mouse clicks

### Lines of Code Added: ~200
### No Breaking Changes: Existing functionality preserved
