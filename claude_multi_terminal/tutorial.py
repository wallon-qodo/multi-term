"""
Interactive first-time tutorial system.

Guides new users through the application in 2 minutes with 9 steps.
"""

from typing import Optional
from dataclasses import dataclass
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown


@dataclass
class TutorialStep:
    """A single step in the tutorial."""

    number: int
    title: str
    description: str
    instruction: str
    hint: Optional[str] = None
    completion_trigger: str = "key"  # 'key', 'mode', 'action'
    trigger_value: Optional[str] = None


class Tutorial:
    """
    Interactive tutorial system.

    Guides users through core features with step-by-step instructions.
    Tracks progress and provides contextual help.
    """

    def __init__(self):
        self.current_step = 0
        self.completed_steps = set()
        self.active = False
        self.steps = self._create_steps()

    def _create_steps(self) -> list[TutorialStep]:
        """Create the tutorial steps."""
        return [
            TutorialStep(
                number=1,
                title="Welcome to Claude Multi-Terminal! 🚀",
                description=(
                    "This 2-minute tutorial will teach you the essentials.\n\n"
                    "**Claude Multi-Terminal** is a vim-inspired TUI for managing "
                    "multiple Claude conversations simultaneously."
                ),
                instruction="Press **any key** to continue",
                completion_trigger="key",
            ),
            TutorialStep(
                number=2,
                title="Understanding Modes",
                description=(
                    "The app has 4 modes (like vim):\n\n"
                    "• **NORMAL** ⌘ - Navigate and control (default)\n"
                    "• **INSERT** ✏️  - Type prompts\n"
                    "• **VISUAL** 📋 - Copy text\n"
                    "• **FOCUS** 🎯 - Fullscreen single pane\n\n"
                    "You start in NORMAL mode. Always return here with **Esc**."
                ),
                instruction="Press **any key** to continue",
                completion_trigger="key",
            ),
            TutorialStep(
                number=3,
                title="INSERT Mode - Sending Messages",
                description=(
                    "To talk to Claude, you need INSERT mode:\n\n"
                    "1. Press **i** to enter INSERT mode\n"
                    "2. Type your message\n"
                    "3. Press **Enter** to send\n"
                    "4. Press **Esc** to return to NORMAL\n\n"
                    "The status bar shows your current mode."
                ),
                instruction="Try it now: Press **i** to enter INSERT mode",
                hint="Watch the status bar change to ✏️ INSERT",
                completion_trigger="mode",
                trigger_value="insert",
            ),
            TutorialStep(
                number=4,
                title="Sending Your First Message",
                description=(
                    "Great! You're now in INSERT mode (see ✏️ in status bar).\n\n"
                    "Try sending a message to Claude."
                ),
                instruction=(
                    "Type: **Hello Claude!** and press **Enter**\n\n"
                    "(Then press **Esc** to return to NORMAL)"
                ),
                hint="Remember: Enter to send, Esc to return to NORMAL",
                completion_trigger="mode",
                trigger_value="normal",
            ),
            TutorialStep(
                number=5,
                title="Workspaces - Multiple Projects",
                description=(
                    "You have **9 workspaces** (like virtual desktops).\n"
                    "Each can hold 4 independent conversations.\n\n"
                    "Perfect for:\n"
                    "• Different projects (workspace 1, 2, 3...)\n"
                    "• Different tasks (coding, debugging, docs...)\n"
                    "• Organizing by priority\n\n"
                    "Switch instantly with **Ctrl+1** through **Ctrl+9**"
                ),
                instruction="Try it: Press **Ctrl+2** to switch to workspace 2",
                hint="Look for [1] [2] [3]... at the top - [2] will highlight",
                completion_trigger="action",
                trigger_value="workspace_switch",
            ),
            TutorialStep(
                number=6,
                title="Navigating Panes",
                description=(
                    "Each workspace has up to 4 panes (like tmux).\n\n"
                    "Switch between panes:\n"
                    "• **Tab** - Next pane (clockwise)\n"
                    "• **Shift+Tab** - Previous pane (counter-clockwise)\n\n"
                    "The active pane has a colored border."
                ),
                instruction="Try it: Press **Tab** to switch panes",
                hint="The border color will change as you switch",
                completion_trigger="action",
                trigger_value="pane_switch",
            ),
            TutorialStep(
                number=7,
                title="VISUAL Mode - Copying Text",
                description=(
                    "Need to copy Claude's response?\n\n"
                    "1. Press **v** to enter VISUAL mode\n"
                    "2. Use arrow keys to select text\n"
                    "3. Press **Enter** to copy\n"
                    "4. Press **Esc** to return to NORMAL\n\n"
                    "Selected text is automatically copied to clipboard!"
                ),
                instruction="Try it: Press **v** to enter VISUAL mode",
                hint="Status bar will show 📋 VISUAL",
                completion_trigger="mode",
                trigger_value="visual",
            ),
            TutorialStep(
                number=8,
                title="FOCUS Mode - Deep Work",
                description=(
                    "Need to concentrate on one conversation?\n\n"
                    "**F11** toggles FOCUS mode:\n"
                    "• Hides all other panes\n"
                    "• Maximizes current pane to fullscreen\n"
                    "• Press **F11** again to return\n\n"
                    "Perfect for long conversations or debugging."
                ),
                instruction="Try it: Press **F11** to enter FOCUS mode",
                hint="Press F11 again to return when ready",
                completion_trigger="mode",
                trigger_value="focus",
            ),
            TutorialStep(
                number=9,
                title="Tutorial Complete! 🎉",
                description=(
                    "You've learned the essentials:\n\n"
                    "✓ **Modes**: NORMAL, INSERT, VISUAL, FOCUS\n"
                    "✓ **Workspaces**: Ctrl+1-9\n"
                    "✓ **Panes**: Tab/Shift+Tab\n"
                    "✓ **Messaging**: i → type → Enter → Esc\n"
                    "✓ **Copying**: v → arrows → Enter → Esc\n"
                    "✓ **Focus**: F11\n\n"
                    "**Next Steps:**\n"
                    "• Read the quick reference: [docs/QUICK-REFERENCE.md]\n"
                    "• Try the common workflows: [docs/USER-GUIDE.md]\n"
                    "• Press **q** anytime to quit\n\n"
                    "**Pro tip**: Keep docs/QUICK-REFERENCE.md open for shortcuts!"
                ),
                instruction="Press **any key** to start using the app",
                completion_trigger="key",
            ),
        ]

    def start(self) -> None:
        """Start the tutorial."""
        self.active = True
        self.current_step = 0
        self.completed_steps.clear()

    def stop(self) -> None:
        """Stop the tutorial."""
        self.active = False

    def skip(self) -> None:
        """Skip the tutorial."""
        self.active = False
        self.current_step = len(self.steps)

    def next_step(self) -> None:
        """Move to the next step."""
        if self.current_step < len(self.steps):
            self.completed_steps.add(self.current_step)
            self.current_step += 1

            if self.current_step >= len(self.steps):
                self.stop()

    def handle_key(self, key: str) -> bool:
        """
        Handle a key press during tutorial.

        Args:
            key: The key pressed

        Returns:
            bool: True if tutorial handled the key
        """
        if not self.active:
            return False

        step = self.get_current_step()
        if not step:
            return False

        # Check if this key completes the step
        if step.completion_trigger == "key":
            self.next_step()
            return True

        return False

    def handle_mode_change(self, new_mode: str) -> bool:
        """
        Handle a mode change during tutorial.

        Args:
            new_mode: The new mode ('normal', 'insert', 'visual', 'focus')

        Returns:
            bool: True if tutorial handled the mode change
        """
        if not self.active:
            return False

        step = self.get_current_step()
        if not step:
            return False

        # Check if this mode change completes the step
        if step.completion_trigger == "mode" and step.trigger_value == new_mode:
            self.next_step()
            return True

        return False

    def handle_action(self, action: str) -> bool:
        """
        Handle an action during tutorial.

        Args:
            action: The action performed ('workspace_switch', 'pane_switch', etc.)

        Returns:
            bool: True if tutorial handled the action
        """
        if not self.active:
            return False

        step = self.get_current_step()
        if not step:
            return False

        # Check if this action completes the step
        if step.completion_trigger == "action" and step.trigger_value == action:
            self.next_step()
            return True

        return False

    def get_current_step(self) -> Optional[TutorialStep]:
        """
        Get the current tutorial step.

        Returns:
            Optional[TutorialStep]: Current step or None if tutorial not active
        """
        if not self.active or self.current_step >= len(self.steps):
            return None

        return self.steps[self.current_step]

    def get_progress(self) -> str:
        """
        Get progress string.

        Returns:
            str: Progress like "Step 3/9"
        """
        return f"Step {self.current_step + 1}/{len(self.steps)}"

    def render_current_step(self) -> Panel:
        """
        Render the current step as a Rich Panel.

        Returns:
            Panel: Rendered step panel
        """
        step = self.get_current_step()
        if not step:
            return Panel(
                "[dim]Tutorial not active[/dim]",
                title="Tutorial",
                border_style="dim",
            )

        # Build content
        content = []

        # Description
        content.append(Markdown(step.description))

        # Instruction
        content.append("\n")
        content.append(
            Panel(
                Markdown(step.instruction),
                title="📋 What to do",
                border_style="yellow",
                padding=(0, 1),
            )
        )

        # Hint (if any)
        if step.hint:
            content.append("\n")
            content.append(f"[dim italic]💡 {step.hint}[/dim italic]")

        # Progress
        content.append("\n")
        content.append(
            f"[dim]{self.get_progress()} • Press Ctrl+Shift+X to skip tutorial[/dim]"
        )

        # Combine content
        from rich.console import Group

        panel_content = Group(*content)

        # Create panel
        return Panel(
            panel_content,
            title=f"[bold cyan]Tutorial: {step.title}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
