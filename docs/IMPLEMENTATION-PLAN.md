# Claude Multi-Terminal: MVP++++ Implementation Plan

**Goal:** Transform claude-multi-terminal into the default Claude Code TUI for all users.

**Timeline:** 12-16 weeks (3-4 months)
**Team Size:** 2-3 developers optimal, 1 possible with extended timeline
**Philosophy:** Ship fast, iterate faster. Weekly releases.

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Installation & Onboarding](#phase-1-installation--onboarding-weeks-1-3)
3. [Phase 2: Visual Polish](#phase-2-visual-polish-weeks-4-5)
4. [Phase 3: Performance & Scale](#phase-3-performance--scale-weeks-6-8)
5. [Phase 4: Real API Integration](#phase-4-real-api-integration-weeks-9-10)
6. [Phase 5: Visual Context & Images](#phase-5-visual-context--images-weeks-11-12)
7. [Phase 6: Smart Integration](#phase-6-smart-integration-weeks-13-14)
8. [Phase 7: Collaboration](#phase-7-collaboration-weeks-15-16)
9. [Architecture Changes](#architecture-changes)
10. [Testing Strategy](#testing-strategy)
11. [Rollout Plan](#rollout-plan)

---

## Overview

### Current State
- ✅ Multi-pane TUI with 9 workspaces
- ✅ Modal interface (NORMAL, INSERT, VISUAL, FOCUS)
- ✅ Session persistence
- ✅ Basic token tracking (simulated)
- ✅ Knowledge synthesis integration
- ⚠️ Manual installation
- ⚠️ No onboarding
- ⚠️ Basic visuals
- ⚠️ PTY-based (limited API access)

### Target State
- ✅ One-liner installation
- ✅ Interactive first-run tutorial
- ✅ Beautiful themes & animations
- ✅ Handles 10K+ message sessions
- ✅ Real Claude API with streaming
- ✅ Image/screenshot support
- ✅ IDE & Git integration
- ✅ Session sharing
- ✅ Smart context recommendations

### Success Metrics
- Installation time: <2 minutes (vs 10+ now)
- FTUE completion: >80% of new users
- Daily active users: 10x increase in 3 months
- GitHub stars: 1000+ in 6 months
- Community plugins: 5+ within 6 months

---

## Phase 1: Installation & Onboarding (Weeks 1-3)

**Goal:** Make installation effortless and first use delightful.

### Week 1: Installation Scripts

#### Task 1.1: Create install.sh Script
**File:** `scripts/install.sh`
**Time:** 1 day

```bash
#!/bin/bash
# Auto-install script for claude-multi-terminal

set -e

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

# Check dependencies
check_deps() {
    command -v python3 >/dev/null 2>&1 || { echo "Python 3.8+ required"; exit 1; }
    command -v pip3 >/dev/null 2>&1 || { echo "pip3 required"; exit 1; }
}

# Install with pipx (preferred) or pip
install_app() {
    if command -v pipx >/dev/null 2>&1; then
        pipx install claude-multi-terminal
    else
        pip3 install --user claude-multi-terminal
    fi
}

# Auto-detect Claude CLI
setup_claude_cli() {
    # Check common locations
    CLAUDE_PATHS=(
        "$HOME/.local/bin/claude"
        "/usr/local/bin/claude"
        "$(which claude 2>/dev/null)"
    )

    for path in "${CLAUDE_PATHS[@]}"; do
        if [ -x "$path" ]; then
            echo "Found Claude CLI: $path"
            return 0
        fi
    done

    echo "⚠️  Claude CLI not found. Install from: https://claude.ai/cli"
    return 1
}

# Create config
create_config() {
    mkdir -p ~/.config/multi-term
    cat > ~/.config/multi-term/config.json <<EOF
{
    "claude_path": "$(which claude)",
    "theme": "default",
    "first_run": true
}
EOF
}

# Add to PATH
add_to_path() {
    SHELL_RC="$HOME/.$(basename $SHELL)rc"
    if ! grep -q "multi-term" "$SHELL_RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo "Added multi-term to PATH in $SHELL_RC"
    fi
}

# Main installation flow
main() {
    echo "🚀 Installing Claude Multi-Terminal..."

    check_deps
    install_app
    setup_claude_cli
    create_config
    add_to_path

    echo "✅ Installation complete!"
    echo ""
    echo "Launch with: multi-term"
    echo "Tutorial will start automatically on first run."
}

main "$@"
```

**Deliverable:** Working install script
**Test:** Fresh macOS/Linux install, <2 minutes total

#### Task 1.2: PyPI Package
**Time:** 2 days

**Files to create:**
- `setup.py` or `pyproject.toml`
- `MANIFEST.in`
- `requirements.txt` (user-facing)

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "claude-multi-terminal"
version = "0.2.0"
description = "Multi-pane terminal interface for Claude Code CLI"
authors = [{name = "Your Name", email = "you@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "textual>=0.47.0",
    "anthropic>=0.18.0",
    "rich>=13.0.0",
]

[project.scripts]
multi-term = "claude_multi_terminal.__main__:main"

[project.urls]
Homepage = "https://github.com/wallon-qodo/multi-term"
Documentation = "https://github.com/wallon-qodo/multi-term/docs"
```

**Steps:**
1. Create `pyproject.toml`
2. Test local build: `python -m build`
3. Test local install: `pip install dist/*.whl`
4. Publish to PyPI: `twine upload dist/*`

**Deliverable:** `pip install claude-multi-terminal` works
**Test:** Fresh Python env, `pip install claude-multi-terminal && multi-term`

#### Task 1.3: Homebrew Formula
**Time:** 1 day

**File:** `homebrew/claude-multi-terminal.rb`

```ruby
class ClaudeMultiTerminal < Formula
  desc "Multi-pane terminal interface for Claude Code CLI"
  homepage "https://github.com/wallon-qodo/multi-term"
  url "https://github.com/wallon-qodo/multi-term/archive/v0.2.0.tar.gz"
  sha256 "..." # Generate with: shasum -a 256 archive.tar.gz
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/multi-term", "--version"
  end
end
```

**Steps:**
1. Create formula
2. Submit to homebrew-core (or create tap: homebrew-multi-term)
3. Test on fresh macOS

**Deliverable:** `brew install claude-multi-terminal` works
**Test:** Fresh macOS, `brew install claude-multi-terminal && multi-term`

#### Task 1.4: One-Liner Install Script
**Time:** 0.5 days

Host `get.claude-multi-term.sh` that:
1. Detects OS
2. Chooses best install method (brew > pipx > pip)
3. Runs installation
4. Verifies success

```bash
curl -fsSL https://get.claude-multi-term.sh | bash
```

**Deliverable:** One-liner works on macOS/Linux
**Test:** 5 different machines, all <2 minutes

### Week 2: First-Run Tutorial

#### Task 2.1: Tutorial State Machine
**File:** `claude_multi_terminal/tutorial/tutorial_manager.py`
**Time:** 2 days

```python
from enum import Enum
from typing import Optional, Callable

class TutorialStep(Enum):
    WELCOME = "welcome"
    INSERT_MODE = "insert_mode"
    SEND_MESSAGE = "send_message"
    VISUAL_MODE = "visual_mode"
    COPY_TEXT = "copy_text"
    PANES = "panes"
    WORKSPACES = "workspaces"
    FOCUS_MODE = "focus_mode"
    COMPLETE = "complete"

class TutorialManager:
    def __init__(self, app):
        self.app = app
        self.current_step = TutorialStep.WELCOME
        self.completed_steps = set()
        self.overlay = None

    def start(self):
        """Begin tutorial"""
        self.show_step(TutorialStep.WELCOME)

    def show_step(self, step: TutorialStep):
        """Display tutorial overlay for step"""
        self.current_step = step
        self.overlay = TutorialOverlay(step, self)
        self.app.mount(self.overlay)

    def complete_step(self, step: TutorialStep):
        """Mark step as completed, advance"""
        self.completed_steps.add(step)
        next_step = self.get_next_step(step)
        if next_step:
            self.show_step(next_step)
        else:
            self.finish_tutorial()

    def get_next_step(self, current: TutorialStep) -> Optional[TutorialStep]:
        """Get next tutorial step"""
        steps = list(TutorialStep)
        try:
            idx = steps.index(current)
            if idx < len(steps) - 1:
                return steps[idx + 1]
        except ValueError:
            pass
        return None

    def finish_tutorial(self):
        """Tutorial complete"""
        self.app.remove(self.overlay)
        self.save_completion()
        self.show_completion_message()

    def save_completion(self):
        """Save to config that tutorial is done"""
        config = self.app.config
        config["first_run"] = False
        config.save()
```

**Deliverable:** Tutorial state machine
**Test:** Can navigate through all steps

#### Task 2.2: Tutorial Overlays
**File:** `claude_multi_terminal/tutorial/tutorial_overlay.py`
**Time:** 3 days

Create interactive overlays for each step:

```python
class TutorialOverlay(Widget):
    """Interactive tutorial overlay"""

    STEP_CONTENT = {
        TutorialStep.WELCOME: {
            "title": "Welcome to Claude Multi-Terminal! 🚀",
            "content": "Let's take a quick 2-minute tour...",
            "action": "Press any key to continue",
        },
        TutorialStep.INSERT_MODE: {
            "title": "Step 1: Type to Claude",
            "content": "Press 'i' to enter INSERT mode, then type your prompt.",
            "highlight": "status_bar",  # Highlight status bar showing mode
            "wait_for": KeyPress("i"),
        },
        # ... more steps
    }

    def __init__(self, step: TutorialStep, manager: TutorialManager):
        super().__init__()
        self.step = step
        self.manager = manager
        self.content = self.STEP_CONTENT[step]

    def render(self) -> RenderableType:
        """Render tutorial overlay"""
        return Panel(
            Align.center(
                Group(
                    Text(self.content["title"], style="bold cyan"),
                    Text(""),
                    Text(self.content["content"]),
                    Text(""),
                    Text(self.content.get("action", ""), style="dim"),
                ),
                vertical="middle",
            ),
            border_style="cyan",
            box=box.DOUBLE,
        )

    def on_key(self, event: Key):
        """Handle key press"""
        expected_key = self.content.get("wait_for")
        if expected_key and event.key == expected_key:
            self.manager.complete_step(self.step)
```

**Steps for each tutorial step:**

1. **WELCOME** - Friendly intro, press any key
2. **INSERT_MODE** - Highlight status bar, wait for 'i' press
3. **SEND_MESSAGE** - Wait for message sent
4. **VISUAL_MODE** - Wait for 'v' press
5. **COPY_TEXT** - Wait for text copied
6. **PANES** - Explain Tab key, wait for pane switch
7. **WORKSPACES** - Explain Ctrl+1-9, wait for workspace switch
8. **FOCUS_MODE** - Explain F11, wait for focus toggle
9. **COMPLETE** - Congratulations screen

**Deliverable:** All 9 tutorial steps with overlays
**Test:** Complete tutorial start to finish, <2 minutes

#### Task 2.3: Tutorial Completion Tracking
**Time:** 0.5 days

```python
# Save to ~/.config/multi-term/config.json
{
    "first_run": false,
    "tutorial_completed": true,
    "tutorial_completion_time": "2026-02-20T15:30:00Z"
}

# Optional: Tutorial metrics (opt-in)
{
    "tutorial_steps_completed": 9,
    "tutorial_duration_seconds": 127,
    "tutorial_skipped": false
}
```

**Deliverable:** Tutorial state persisted
**Test:** Complete tutorial, restart app, no tutorial shown

### Week 3: Polish & Testing

#### Task 3.1: Skip Tutorial Option
**Time:** 0.5 days

```python
# In welcome screen
"Press 's' to skip tutorial"

# Or in settings
multi-term --skip-tutorial
```

**Deliverable:** Can skip tutorial
**Test:** Skip works, config updated

#### Task 3.2: Replay Tutorial
**Time:** 0.5 days

```python
# Add command
multi-term --tutorial

# Or in app
/tutorial  # Replay tutorial anytime
```

**Deliverable:** Can replay tutorial
**Test:** Replay works from completed state

#### Task 3.3: End-to-End Testing
**Time:** 2 days

Test matrix:
- Fresh macOS install (Homebrew)
- Fresh Linux install (pipx)
- Fresh Linux install (pip)
- Tutorial completion
- Tutorial skip
- Tutorial replay

**Deliverable:** All installation methods work
**Test:** 10 fresh installs, all <2 minutes

---

## Phase 2: Visual Polish (Weeks 4-5)

**Goal:** Make the UI beautiful and delightful.

### Week 4: Theme System

#### Task 4.1: Theme Architecture
**File:** `claude_multi_terminal/themes/theme.py`
**Time:** 1 day

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class ColorScheme:
    background: str
    foreground: str
    cursor: str
    selection: str

    # UI elements
    border: str
    border_active: str
    header: str
    status_bar: str

    # Syntax highlighting
    keyword: str
    string: str
    number: str
    comment: str

    # Status colors
    success: str
    warning: str
    error: str
    info: str

class Theme:
    def __init__(self, name: str, colors: ColorScheme):
        self.name = name
        self.colors = colors

    def apply(self, app):
        """Apply theme to app"""
        # Update Textual CSS variables
        app.styles.update({
            "--background": self.colors.background,
            "--foreground": self.colors.foreground,
            # ... more
        })
```

**Deliverable:** Theme system architecture
**Test:** Can create and apply themes

#### Task 4.2: Built-in Themes
**File:** `claude_multi_terminal/themes/builtin.py`
**Time:** 2 days

Implement 6 themes:

1. **Default** (current)
2. **Nord** - Arctic, blue-grey
3. **Dracula** - Dark purple
4. **Gruvbox** - Retro warm
5. **Solarized Dark** - Professional
6. **Tokyo Night** - Modern purple-blue

```python
NORD = Theme(
    name="nord",
    colors=ColorScheme(
        background="#2E3440",
        foreground="#D8DEE9",
        cursor="#88C0D0",
        selection="#434C5E",
        border="#4C566A",
        border_active="#88C0D0",
        # ... complete color scheme
    )
)

THEMES = {
    "default": DEFAULT,
    "nord": NORD,
    "dracula": DRACULA,
    "gruvbox": GRUVBOX,
    "solarized-dark": SOLARIZED_DARK,
    "tokyo-night": TOKYO_NIGHT,
}
```

**Deliverable:** 6 beautiful themes
**Test:** All themes applied correctly

#### Task 4.3: Theme Switcher
**Time:** 1 day

```bash
# Command line
multi-term --theme nord

# In-app
/theme nord
/theme list  # Show available themes

# Settings
~/.config/multi-term/config.json:
{
    "theme": "nord"
}
```

**Deliverable:** Can switch themes
**Test:** Switch between all 6 themes

#### Task 4.4: Custom Theme Support
**Time:** 1 day

```json
// ~/.config/multi-term/themes/my-theme.json
{
    "name": "my-theme",
    "colors": {
        "background": "#1a1b26",
        "foreground": "#c0caf5",
        // ... custom colors
    }
}
```

**Deliverable:** Custom themes loadable
**Test:** Create and load custom theme

### Week 5: Animations & Polish

#### Task 5.1: Smooth Transitions
**File:** `claude_multi_terminal/widgets/animated.py`
**Time:** 2 days

```python
from textual.animation import Animation

class AnimatedPane(Widget):
    def animate_in(self):
        """Fade in animation"""
        self.styles.opacity = 0
        self.animate("opacity", 1.0, duration=0.3, easing="out_cubic")

    def animate_out(self):
        """Fade out animation"""
        self.animate("opacity", 0.0, duration=0.2, easing="in_cubic")

# Apply to:
- Pane switching (fade)
- Mode transitions (color shift)
- Copy action (flash)
- Focus mode (zoom effect)
- Workspace switch (slide)
```

**Deliverable:** Smooth animations throughout
**Test:** All transitions feel polished

#### Task 5.2: Visual Feedback
**Time:** 1 day

**Copy feedback:**
```python
def on_copy(self):
    """Show copy success"""
    self.show_notification("Copied! ✓", style="success", duration=1.0)
    self.flash_selection()  # Brief highlight
```

**Message sent feedback:**
```python
def on_message_sent(self):
    """Animate message send"""
    self.input_area.animate_shrink()
    self.message_area.animate_new_message()
```

**Deliverable:** Visual feedback for all actions
**Test:** Every action has clear feedback

#### Task 5.3: Loading States
**Time:** 1 day

**Response streaming:**
```python
class StreamingIndicator(Widget):
    """Animated thinking indicator"""

    def render(self):
        # Animated dots: ● ○ ○ → ○ ● ○ → ○ ○ ●
        return self.render_dots(self.animation_frame)
```

**Deliverable:** Beautiful loading states
**Test:** Loading indicators smooth

#### Task 5.4: Polish Pass
**Time:** 2 days

- Rounded corners (where supported)
- Shadow effects
- Smooth scrolling (ease in/out)
- Cursor animations
- Selection highlighting
- Error shake animations
- Success checkmarks
- Context-aware colors

**Deliverable:** UI feels premium
**Test:** User testing, "wow" reactions

---

## Phase 3: Performance & Scale (Weeks 6-8)

**Goal:** Handle power users and large sessions gracefully.

### Week 6: Memory Management

#### Task 6.1: Virtual Scrolling
**File:** `claude_multi_terminal/widgets/virtual_richlog.py`
**Time:** 3 days

```python
class VirtualRichLog(Widget):
    """Only render visible messages"""

    def __init__(self):
        self.messages = []  # All messages
        self.visible_start = 0
        self.visible_end = 0
        self.viewport_height = 0

    def render(self) -> RenderableType:
        """Render only visible portion"""
        visible_messages = self.messages[self.visible_start:self.visible_end]
        return Group(*[self.render_message(msg) for msg in visible_messages])

    def on_scroll(self, event):
        """Update visible range on scroll"""
        self.update_visible_range(event.scroll_offset)
        self.refresh()
```

**Deliverable:** Virtual scrolling working
**Test:** 10K messages, smooth scrolling

#### Task 6.2: Lazy Loading
**Time:** 2 days

```python
class LazySession:
    """Load conversation history on demand"""

    def __init__(self, session_path):
        self.session_path = session_path
        self.messages_loaded = False
        self.messages = []

    def load_recent(self, n=50):
        """Load only last N messages"""
        if not self.messages_loaded:
            # Read last N lines from conversation-log.jsonl
            self.messages = read_last_n_messages(self.session_path, n)

    def load_all(self):
        """Load full history (on demand)"""
        self.messages = read_all_messages(self.session_path)
        self.messages_loaded = True
```

**Deliverable:** Only load what's needed
**Test:** 10K message session, instant startup

#### Task 6.3: Automatic Archiving
**Time:** 2 days

```python
def archive_old_messages():
    """Compress old messages to save memory"""

    # If session >5000 messages
    if len(session.messages) > 5000:
        # Keep recent 1000 in memory
        recent = session.messages[-1000:]
        # Archive older to compressed file
        archive_messages(session.messages[:-1000], "archive.jsonl.gz")
        session.messages = recent
        session.archived = True
```

**Deliverable:** Auto-archive at 5K messages
**Test:** Create 10K message session, verify archived

### Week 7: Speed Optimizations

#### Task 7.1: Startup Optimization
**Time:** 2 days

Current: ~2 seconds
Target: <500ms

**Optimizations:**
- Lazy import modules
- Don't load all sessions at startup
- Cache commonly used data
- Parallel initialization
- Defer non-critical work

```python
# Before
from anthropic import Anthropic  # Import at module level

# After
def get_anthropic_client():
    from anthropic import Anthropic  # Import only when needed
    return Anthropic()
```

**Deliverable:** <500ms startup
**Test:** Time from launch to first render

#### Task 7.2: Render Optimization
**Time:** 2 days

Target: 60 FPS (16.67ms per frame)

**Optimizations:**
- Cache rendered content
- Batch DOM updates
- Use CSS transforms for animations
- Minimize re-renders
- Profile with Textual devtools

```python
from functools import lru_cache

class OptimizedWidget(Widget):
    @lru_cache(maxsize=128)
    def render_message(self, message_id):
        """Cache rendered messages"""
        message = self.get_message(message_id)
        return self._render_message(message)
```

**Deliverable:** 60 FPS scrolling
**Test:** Profile with 1K messages

#### Task 7.3: Async Everything
**Time:** 2 days

Make all I/O async:

```python
# File I/O
async def save_session(session):
    async with aiofiles.open(path, 'w') as f:
        await f.write(json.dumps(session))

# API calls
async def send_message(message):
    async with anthropic_client.messages.stream(...) as stream:
        async for chunk in stream:
            yield chunk

# Search/index
async def search_knowledge(query):
    # Run in thread pool
    return await asyncio.to_thread(blocking_search, query)
```

**Deliverable:** No blocking I/O
**Test:** UI stays responsive during heavy I/O

### Week 8: Large Session Handling

#### Task 8.1: Streaming Responses
**Time:** 2 days

Show response as it streams:

```python
async def stream_response(self, message):
    """Stream Claude's response"""
    self.start_streaming_indicator()

    async for chunk in self.client.messages.stream(...):
        if chunk.type == "content_block_delta":
            self.append_chunk(chunk.delta.text)
            self.refresh()  # Update display

    self.stop_streaming_indicator()
```

**Deliverable:** Real-time streaming
**Test:** Long response streams smoothly

#### Task 8.2: Background Processing
**Time:** 2 days

```python
import threading

class BackgroundProcessor:
    """Process tasks in background"""

    def __init__(self):
        self.queue = Queue()
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def worker(self):
        while True:
            task = self.queue.get()
            self.process(task)

    def process(self, task):
        """Process heavy task"""
        # Knowledge extraction
        # Index building
        # Archive compression
        pass

# Usage
processor = BackgroundProcessor()
processor.queue.put(("extract_knowledge", session))
```

**Deliverable:** Heavy tasks don't block UI
**Test:** Extract knowledge while using UI

#### Task 8.3: Memory Limit Warnings
**Time:** 1 day

```python
import psutil

def check_memory():
    """Monitor memory usage"""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024

    if memory_mb > 500:
        show_warning("High memory usage. Consider starting new session.")
```

**Deliverable:** Memory warnings shown
**Test:** Trigger warning at 500MB

---

## Phase 4: Real API Integration (Weeks 9-10)

**Goal:** Replace PTY with native Anthropic API.

### Week 9: API Client

#### Task 9.1: Anthropic Client Wrapper
**File:** `claude_multi_terminal/api/client.py`
**Time:** 2 days

```python
from anthropic import Anthropic, AsyncAnthropic
from typing import AsyncIterator

class ClaudeAPIClient:
    """Wrapper for Anthropic API"""

    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    async def send_message(
        self,
        messages: list,
        system: str = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Send message and stream response"""

        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
            system=system,
        ) as stream:
            async for chunk in stream.text_stream:
                yield chunk

        # Get final usage
        message = await stream.get_final_message()
        return {
            "text": message.content[0].text,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
        }
```

**Deliverable:** API client working
**Test:** Send message, receive streaming response

#### Task 9.2: Token Tracking
**Time:** 1 day

```python
class TokenTracker:
    """Track real token usage"""

    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_tokens = 0

    def update(self, usage):
        """Update from API response"""
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        self.cached_tokens += usage.get("cache_read_input_tokens", 0)

    def get_cost(self):
        """Calculate cost"""
        input_cost = (self.input_tokens / 1000) * 0.003
        output_cost = (self.output_tokens / 1000) * 0.015
        cached_cost = (self.cached_tokens / 1000) * 0.0003
        return input_cost + output_cost + cached_cost
```

**Deliverable:** Accurate token tracking
**Test:** Compare with API dashboard

#### Task 9.3: Prompt Caching
**Time:** 1 day

```python
async def send_with_caching(messages, system):
    """Use prompt caching to save cost"""

    # Mark system prompt for caching
    response = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=messages,
    )
```

**Deliverable:** Prompt caching working
**Test:** Second message uses cache (90% cheaper)

### Week 10: Advanced Features

#### Task 10.1: Vision API
**Time:** 2 days

```python
async def send_with_image(message, image_path):
    """Send message with image"""

    import base64

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": message,
                }
            ],
        }],
    )
```

**Deliverable:** Can send images to Claude
**Test:** Send screenshot, get response

#### Task 10.2: Function Calling
**Time:** 2 days

```python
tools = [
    {
        "name": "search_codebase",
        "description": "Search the codebase for functions, classes, or patterns",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "file_type": {"type": "string"},
            },
            "required": ["query"],
        },
    }
]

# Send with tools
response = await client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=tools,
    messages=messages,
)

# Handle tool use
if response.stop_reason == "tool_use":
    tool_use = response.content[1]
    result = execute_tool(tool_use.name, tool_use.input)
    # Send result back...
```

**Deliverable:** Function calling working
**Test:** Claude can search codebase via tools

#### Task 10.3: Model Selection
**Time:** 1 day

```python
# Let users choose model
MODELS = {
    "sonnet": "claude-sonnet-4-5-20250929",
    "opus": "claude-opus-4-6-20250929",
    "haiku": "claude-haiku-4-5-20251001",
}

# In UI
/model sonnet  # Switch to Sonnet
/model opus    # Switch to Opus (for hard tasks)
/model haiku   # Switch to Haiku (for speed)
```

**Deliverable:** Can switch models
**Test:** Switch between all 3 models

---

## Phase 5: Visual Context & Images (Weeks 11-12)

**Goal:** Make it easy to work with visual content.

### Week 11: Screenshot Integration

#### Task 11.1: Screenshot Capture
**Time:** 2 days

```python
import pyscreenshot as ImageGrab
from PIL import Image

class ScreenshotCapture:
    """Capture screen regions"""

    def capture_region(self):
        """Let user select region"""
        # Show overlay for region selection
        overlay = SelectionOverlay()
        region = await overlay.get_selection()

        # Capture region
        image = ImageGrab.grab(bbox=region)
        return image

    def capture_window(self):
        """Capture current window"""
        # Platform-specific window capture
        pass
```

**Keyboard shortcut:**
```
Ctrl+Shift+S → Select region → Capture → Attach to message
```

**Deliverable:** Can capture screenshots
**Test:** Capture and send screenshot

#### Task 11.2: Image Paste
**Time:** 1 day

```python
def on_paste(self, event):
    """Handle clipboard paste"""
    if event.has_image:
        image = event.image
        self.attach_image(image)
        self.show_image_preview(image)
```

**Deliverable:** Paste images from clipboard
**Test:** Copy image, paste in multi-term

#### Task 11.3: Drag & Drop
**Time:** 2 days

```python
def on_drop(self, event):
    """Handle file drop"""
    for file_path in event.files:
        if is_image(file_path):
            self.attach_image(file_path)
            self.show_image_preview(file_path)
```

**Deliverable:** Drag & drop images
**Test:** Drag image file onto UI

#### Task 11.4: Image Viewer
**Time:** 2 days

```python
class ImageViewer(Widget):
    """Display attached images"""

    def render(self):
        # Show thumbnail
        # Click to expand
        # Render with PIL + Rich
        pass
```

**Deliverable:** View attached images
**Test:** See images in conversation

### Week 12: OCR & Polish

#### Task 12.1: OCR Integration
**Time:** 2 days

```python
import pytesseract
from PIL import Image

def extract_text_from_image(image_path):
    """OCR to extract text"""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Usage
image = capture_screenshot()
text = extract_text_from_image(image)
prompt = f"Fix this error:\n{text}"
```

**Deliverable:** Extract text from screenshots
**Test:** Screenshot error message, extract text

#### Task 12.2: Image Management
**Time:** 1 day

```bash
# Store images
~/.cache/multi-term/images/session-123/image-001.png

# Clean up old images
multi-term clean-images --older-than 30d
```

**Deliverable:** Images stored and cleaned
**Test:** Images persist across sessions

#### Task 12.3: End-to-End Testing
**Time:** 2 days

Test all image features:
- Screenshot capture
- Clipboard paste
- Drag & drop
- Image viewing
- OCR extraction
- API sending

**Deliverable:** All image features work
**Test:** Complete workflow works smoothly

---

## Phase 6: Smart Integration (Weeks 13-14)

**Goal:** Integrate with user's existing workflow.

### Week 13: IDE & Git Integration

#### Task 13.1: VSCode Extension
**New Repo:** `vscode-multi-term`
**Time:** 3 days

```typescript
// extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    // Send selected code to multi-term
    let sendToMultiTerm = vscode.commands.registerCommand(
        'multiterm.sendCode',
        () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const selection = editor.document.getText(editor.selection);
                // Send to multi-term via socket/HTTP
                sendToMultiTerminal(selection);
            }
        }
    );

    context.subscriptions.push(sendToMultiTerm);
}

function sendToMultiTerminal(code: string) {
    // HTTP API to multi-term
    fetch('http://localhost:8765/api/send', {
        method: 'POST',
        body: JSON.stringify({ code }),
    });
}
```

**Deliverable:** VSCode extension working
**Test:** Select code, send to multi-term

#### Task 13.2: Git Integration
**File:** `claude_multi_terminal/integrations/git.py`
**Time:** 2 days

```python
import subprocess

class GitIntegration:
    """Git operations"""

    def get_status(self):
        """Get git status"""
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
        )
        return result.stdout

    def generate_commit_message(self, diff):
        """AI-generated commit message"""
        prompt = f"Write a commit message for:\n{diff}"
        message = await claude.send_message(prompt)
        return message

    def create_pr_description(self):
        """AI-generated PR description"""
        diff = self.get_diff()
        log = self.get_commit_log()
        prompt = f"Write PR description for:\n{log}\n\nDiff:\n{diff}"
        description = await claude.send_message(prompt)
        return description
```

**Keyboard shortcut:**
```
Ctrl+G → Show git status in pane
```

**Deliverable:** Git integration working
**Test:** Generate commit message, create PR

#### Task 13.3: File Watching
**Time:** 2 days

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeWatcher(FileSystemEventHandler):
    """Watch for file changes"""

    def on_modified(self, event):
        if event.src_path.endswith(('.py', '.js', '.ts')):
            # File changed
            self.notify_claude(event.src_path)

    def notify_claude(self, file_path):
        # Update Claude's context
        # Optionally suggest improvements
        pass

# Usage
observer = Observer()
observer.schedule(CodeWatcher(), path="./src", recursive=True)
observer.start()
```

**Deliverable:** Watch files, update context
**Test:** Edit file, Claude's context updates

### Week 14: Terminal & Slack Integration

#### Task 14.1: Terminal Integration
**Time:** 2 days

```python
class TerminalIntegration:
    """Run commands, capture output"""

    def run_command(self, command):
        """Run command, send output to Claude on error"""
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Command failed, ask Claude for help
            self.ask_claude_about_error(command, result.stderr)

        return result
```

**Usage:**
```
In pane:
$ npm test
[tests fail]
→ Automatically sends error to Claude
→ "Here's how to fix the test failures..."
```

**Deliverable:** Terminal integration working
**Test:** Run failing command, get help

#### Task 14.2: Context Recommendations
**Time:** 3 days

```python
class ContextRecommender:
    """Smart context suggestions"""

    def suggest_on_startup(self):
        """What to work on today"""

        time_of_day = get_time_of_day()
        git_activity = get_recent_git_activity()
        calendar = get_upcoming_meetings()

        if time_of_day == "morning":
            return self.morning_suggestions(git_activity, calendar)
        elif time_of_day == "afternoon":
            return self.afternoon_suggestions()

    def morning_suggestions(self, git, calendar):
        """Morning context"""
        return [
            f"Continue {git.last_branch} work from yesterday",
            f"Review {calendar.next_meeting} prep",
            "Daily standup: what to share?",
        ]
```

**Deliverable:** Smart suggestions working
**Test:** Suggestions make sense

---

## Phase 7: Collaboration (Weeks 15-16)

**Goal:** Enable session sharing and collaboration.

### Week 15: Session Sharing

#### Task 15.1: Share Server
**New Repo:** `multi-term-share`
**Time:** 3 days

```python
# Flask/FastAPI server
from fastapi import FastAPI

app = FastAPI()

# Store shared sessions
shared_sessions = {}

@app.post("/share")
async def share_session(session_data):
    """Create shareable link"""
    session_id = generate_id()
    shared_sessions[session_id] = {
        "data": session_data,
        "created_at": now(),
        "views": 0,
        "mode": "read-only",
    }
    return {"url": f"https://share.multi-term.app/{session_id}"}

@app.get("/{session_id}")
async def view_session(session_id):
    """View shared session"""
    session = shared_sessions.get(session_id)
    if session:
        session["views"] += 1
        return render_session(session["data"])
    return {"error": "Not found"}
```

**Deliverable:** Share server running
**Test:** Share session, view via link

#### Task 15.2: Share Command
**Time:** 1 day

```python
# In multi-term
/share → Creates shareable link
       → Copies to clipboard
       → "Shared! Link: https://..."

# Options
/share read-only  # Default
/share collaborative  # Allow editing
/share 24h  # Expires in 24 hours
```

**Deliverable:** Share command working
**Test:** Share session, open link

#### Task 15.3: Web Viewer
**Time:** 3 days

```typescript
// React app for viewing shared sessions
function SessionViewer({ sessionId }) {
    const [session, setSession] = useState(null);

    useEffect(() => {
        fetch(`/api/${sessionId}`)
            .then(res => res.json())
            .then(setSession);
    }, [sessionId]);

    return (
        <div className="session-viewer">
            <ConversationDisplay messages={session.messages} />
            <ShareActions session={session} />
        </div>
    );
}
```

**Deliverable:** Web viewer working
**Test:** Open shared link in browser

### Week 16: Collaborative Editing

#### Task 16.1: WebSocket Server
**Time:** 2 days

```python
from fastapi import WebSocket

@app.websocket("/collaborate/{session_id}")
async def collaborate(websocket: WebSocket, session_id: str):
    """Real-time collaboration"""
    await websocket.accept()

    # Add to session
    active_sessions[session_id].add(websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            # Broadcast to all participants
            for ws in active_sessions[session_id]:
                if ws != websocket:
                    await ws.send_json(data)
    finally:
        active_sessions[session_id].remove(websocket)
```

**Deliverable:** WebSocket collaboration working
**Test:** Two users, real-time sync

#### Task 16.2: Conflict Resolution
**Time:** 2 days

```python
class ConflictResolver:
    """Handle concurrent edits"""

    def resolve(self, local_change, remote_change):
        """Operational transformation"""
        # Last-write-wins for now
        # TODO: CRDT for better resolution
        return remote_change
```

**Deliverable:** Basic conflict resolution
**Test:** Concurrent edits don't break

#### Task 16.3: Polish & Testing
**Time:** 2 days

- Role-based access (viewer, contributor, admin)
- User indicators (who's online)
- Cursor positions
- Comment threads

**Deliverable:** Polished collaboration
**Test:** 3+ users collaborating smoothly

---

## Architecture Changes

### Current Architecture
```
claude_multi_terminal/
├── app.py                 # Main app
├── widgets/               # UI widgets
├── persistence/           # Session storage
├── streaming/             # Token tracking (simulated)
└── config.py              # Configuration
```

### New Architecture
```
claude_multi_terminal/
├── app.py                 # Main app
├── api/                   # NEW: API client
│   ├── client.py          # Anthropic API wrapper
│   ├── streaming.py       # Real streaming
│   └── tokens.py          # Token tracking
├── tutorial/              # NEW: FTUE
│   ├── manager.py         # Tutorial state
│   └── overlays.py        # Tutorial UI
├── themes/                # NEW: Theme system
│   ├── theme.py           # Theme architecture
│   ├── builtin.py         # Built-in themes
│   └── custom.py          # Custom theme loader
├── integrations/          # NEW: External integrations
│   ├── git.py             # Git operations
│   ├── ide.py             # IDE integration
│   ├── terminal.py        # Terminal integration
│   └── slack.py           # Slack integration
├── images/                # NEW: Image handling
│   ├── capture.py         # Screenshot capture
│   ├── viewer.py          # Image viewer
│   └── ocr.py             # Text extraction
├── sharing/               # NEW: Collaboration
│   ├── client.py          # Share client
│   └── sync.py            # Real-time sync
├── performance/           # NEW: Performance
│   ├── virtual_scroll.py  # Virtual scrolling
│   ├── lazy_load.py       # Lazy loading
│   └── cache.py           # Caching layer
└── widgets/               # Existing UI widgets
    ├── animated.py        # NEW: Animations
    └── ...
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_api_client.py
async def test_send_message():
    client = ClaudeAPIClient(api_key="test")
    response = await client.send_message([{"role": "user", "content": "Hi"}])
    assert response["text"]
    assert response["usage"]["input_tokens"] > 0

# tests/test_themes.py
def test_theme_application():
    theme = NORD
    app = MockApp()
    theme.apply(app)
    assert app.styles["--background"] == "#2E3440"
```

### Integration Tests
```python
# tests/test_tutorial.py
async def test_tutorial_completion():
    app = create_test_app()
    tutorial = TutorialManager(app)
    tutorial.start()

    # Simulate user actions
    await simulate_key_press("i")
    await simulate_message_send()
    await simulate_key_press("v")
    # ...

    assert tutorial.current_step == TutorialStep.COMPLETE
```

### End-to-End Tests
```bash
# tests/e2e/test_installation.sh
#!/bin/bash

# Test one-liner install
curl -fsSL https://get.claude-multi-term.sh | bash
multi-term --version

# Test tutorial
echo "i\nHello\n" | multi-term --test-mode

# Test themes
multi-term --theme nord
```

### Performance Tests
```python
# tests/test_performance.py
def test_startup_time():
    start = time.time()
    app = ClaudeMultiTerminalApp()
    end = time.time()
    assert (end - start) < 0.5  # <500ms

def test_10k_messages():
    session = create_session_with_n_messages(10000)
    # Should handle smoothly
    assert session.can_scroll()
```

---

## Rollout Plan

### Alpha (Week 4)
- Internal testing
- Installation + FTUE ready
- Themes working
- Gather feedback

### Beta (Week 8)
- Public beta release
- Performance optimizations complete
- Invite early adopters
- Bug fixes

### v0.2.0 (Week 12)
- Real API integration
- Image support
- Public release
- Marketing push

### v0.3.0 (Week 16)
- All integrations
- Collaboration features
- Feature complete
- Default TUI status

---

## Success Metrics

### Week 4 Targets
- ✅ Installation <2 minutes
- ✅ FTUE completion >80%
- ✅ 6 themes available

### Week 8 Targets
- ✅ Startup <500ms
- ✅ 10K messages handled
- ✅ 60 FPS scrolling

### Week 12 Targets
- ✅ Real API working
- ✅ Image support complete
- ✅ 100+ beta users

### Week 16 Targets
- ✅ All integrations working
- ✅ Collaboration ready
- ✅ 1000+ users
- ✅ 5+ community plugins

---

## Notes

- **Parallel work**: Phases can overlap with 2-3 developers
- **Weekly releases**: Ship incrementally, don't wait for perfection
- **User feedback**: Beta test each phase before moving on
- **Documentation**: Update docs with each feature
- **Marketing**: Blog post for each major milestone

---

**Ready to build the ultimate Claude TUI?** 🚀

Let's start with Phase 1: Installation & Onboarding!
