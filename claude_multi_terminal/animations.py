"""
Animation system for smooth transitions and visual effects.

Provides easing functions and animation utilities for the TUI.
"""

from typing import Callable, Optional
from textual.app import App
from textual.widgets import Widget
from textual import on
from textual.reactive import reactive
import math


class Easing:
    """
    Easing functions for smooth animations.

    Based on standard easing equations.
    """

    @staticmethod
    def linear(t: float) -> float:
        """Linear easing (no easing)."""
        return t

    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic easing in (accelerating)."""
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic easing out (decelerating)."""
        return t * (2 - t)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic easing in/out."""
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic easing in."""
        return t * t * t

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic easing out."""
        return (--t) * t * t + 1

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic easing in/out (smooth and natural)."""
        return 4 * t * t * t if t < 0.5 else (t - 1) * (2 * t - 2) * (2 * t - 2) + 1

    @staticmethod
    def ease_in_quart(t: float) -> float:
        """Quartic easing in."""
        return t * t * t * t

    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic easing out."""
        return 1 - (--t) * t * t * t

    @staticmethod
    def ease_in_out_quart(t: float) -> float:
        """Quartic easing in/out."""
        return 8 * t * t * t * t if t < 0.5 else 1 - 8 * (--t) * t * t * t

    @staticmethod
    def ease_in_out_sine(t: float) -> float:
        """Sinusoidal easing in/out (very smooth)."""
        return -(math.cos(math.pi * t) - 1) / 2

    @staticmethod
    def ease_in_expo(t: float) -> float:
        """Exponential easing in (very fast acceleration)."""
        return 0 if t == 0 else math.pow(2, 10 * t - 10)

    @staticmethod
    def ease_out_expo(t: float) -> float:
        """Exponential easing out (very fast deceleration)."""
        return 1 if t == 1 else 1 - math.pow(2, -10 * t)

    @staticmethod
    def ease_in_out_expo(t: float) -> float:
        """Exponential easing in/out."""
        if t == 0:
            return 0
        if t == 1:
            return 1
        if t < 0.5:
            return math.pow(2, 20 * t - 10) / 2
        return (2 - math.pow(2, -20 * t + 10)) / 2

    @staticmethod
    def ease_in_back(t: float) -> float:
        """Back easing in (overshoot)."""
        c1 = 1.70158
        c3 = c1 + 1
        return c3 * t * t * t - c1 * t * t

    @staticmethod
    def ease_out_back(t: float) -> float:
        """Back easing out (overshoot and settle)."""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * math.pow(t - 1, 3) + c1 * math.pow(t - 1, 2)

    @staticmethod
    def ease_in_out_back(t: float) -> float:
        """Back easing in/out."""
        c1 = 1.70158
        c2 = c1 * 1.525
        if t < 0.5:
            return (math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
        return (math.pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2

    @staticmethod
    def ease_out_bounce(t: float) -> float:
        """Bounce easing out (bouncy landing)."""
        n1 = 7.5625
        d1 = 2.75
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375


# Animation presets for common transitions
ANIMATION_PRESETS = {
    # Mode transitions (fast and smooth)
    "mode_transition": {
        "duration": 0.15,  # 150ms
        "easing": Easing.ease_in_out_cubic,
    },
    # Workspace switching (slightly longer, emphasize change)
    "workspace_switch": {
        "duration": 0.25,  # 250ms
        "easing": Easing.ease_in_out_back,
    },
    # Pane focus (quick feedback)
    "pane_focus": {
        "duration": 0.2,  # 200ms
        "easing": Easing.ease_in_out_quad,
    },
    # Overlay appearance (smooth slide in)
    "overlay_show": {
        "duration": 0.3,  # 300ms
        "easing": Easing.ease_out_cubic,
    },
    # Overlay disappearance (quick slide out)
    "overlay_hide": {
        "duration": 0.2,  # 200ms
        "easing": Easing.ease_in_cubic,
    },
    # Focus mode (dramatic transition)
    "focus_mode": {
        "duration": 0.35,  # 350ms
        "easing": Easing.ease_in_out_expo,
    },
    # Notification toast (bouncy entrance)
    "toast": {
        "duration": 0.3,  # 300ms
        "easing": Easing.ease_out_bounce,
    },
    # Button press (instant feedback)
    "button_press": {
        "duration": 0.1,  # 100ms
        "easing": Easing.ease_out_quad,
    },
    # Hover effect (subtle)
    "hover": {
        "duration": 0.15,  # 150ms
        "easing": Easing.ease_in_out_sine,
    },
}


class AnimationHelper:
    """
    Helper class for common animation tasks.
    """

    @staticmethod
    def fade_in(widget: Widget, duration: float = 0.3) -> None:
        """
        Fade in a widget.

        Args:
            widget: Widget to fade in
            duration: Animation duration in seconds
        """
        widget.styles.opacity = 0.0
        widget.styles.animate("opacity", 1.0, duration=duration, easing="out_cubic")

    @staticmethod
    def fade_out(widget: Widget, duration: float = 0.2, callback: Optional[Callable] = None) -> None:
        """
        Fade out a widget.

        Args:
            widget: Widget to fade out
            duration: Animation duration in seconds
            callback: Optional callback when animation completes
        """
        widget.styles.animate("opacity", 0.0, duration=duration, easing="in_cubic", on_complete=callback)

    @staticmethod
    def slide_in_from_top(widget: Widget, duration: float = 0.3) -> None:
        """
        Slide in from top.

        Args:
            widget: Widget to slide in
            duration: Animation duration in seconds
        """
        widget.styles.offset = (0, -10)
        widget.styles.opacity = 0.0
        widget.styles.animate("offset", (0, 0), duration=duration, easing="out_back")
        widget.styles.animate("opacity", 1.0, duration=duration * 0.5, easing="out_cubic")

    @staticmethod
    def slide_in_from_bottom(widget: Widget, duration: float = 0.3) -> None:
        """
        Slide in from bottom.

        Args:
            widget: Widget to slide in
            duration: Animation duration in seconds
        """
        widget.styles.offset = (0, 10)
        widget.styles.opacity = 0.0
        widget.styles.animate("offset", (0, 0), duration=duration, easing="out_back")
        widget.styles.animate("opacity", 1.0, duration=duration * 0.5, easing="out_cubic")

    @staticmethod
    def slide_out_to_top(widget: Widget, duration: float = 0.2, callback: Optional[Callable] = None) -> None:
        """
        Slide out to top.

        Args:
            widget: Widget to slide out
            duration: Animation duration in seconds
            callback: Optional callback when animation completes
        """
        widget.styles.animate("offset", (0, -10), duration=duration, easing="in_cubic")
        widget.styles.animate("opacity", 0.0, duration=duration, easing="in_cubic", on_complete=callback)

    @staticmethod
    def scale_in(widget: Widget, duration: float = 0.3) -> None:
        """
        Scale in (zoom in).

        Args:
            widget: Widget to scale in
            duration: Animation duration in seconds
        """
        # Note: Textual doesn't support scale directly, simulate with opacity
        widget.styles.opacity = 0.0
        widget.styles.animate("opacity", 1.0, duration=duration, easing="out_back")

    @staticmethod
    def pulse(widget: Widget, intensity: float = 0.2, duration: float = 0.5) -> None:
        """
        Pulse animation (brief brightness increase).

        Args:
            widget: Widget to pulse
            intensity: Pulse intensity (0.0-1.0)
            duration: Animation duration in seconds
        """
        # Pulse by animating opacity slightly
        original_opacity = widget.styles.opacity or 1.0
        target_opacity = min(1.0, original_opacity + intensity)

        # Animate to brighter, then back
        widget.styles.animate("opacity", target_opacity, duration=duration / 2, easing="out_quad")
        widget.set_timer(
            duration / 2,
            lambda: widget.styles.animate("opacity", original_opacity, duration=duration / 2, easing="in_quad")
        )

    @staticmethod
    def shake(widget: Widget, intensity: int = 5, duration: float = 0.5) -> None:
        """
        Shake animation (horizontal oscillation).

        Args:
            widget: Widget to shake
            intensity: Shake intensity in cells
            duration: Animation duration in seconds
        """
        # Shake by animating offset back and forth
        steps = 4
        step_duration = duration / steps

        def shake_step(step: int, direction: int) -> None:
            if step >= steps:
                widget.styles.offset = (0, 0)
                return

            offset_x = intensity * direction * (1 - step / steps)  # Decay intensity
            widget.styles.animate("offset", (offset_x, 0), duration=step_duration, easing="linear")
            widget.set_timer(
                step_duration,
                lambda: shake_step(step + 1, -direction)
            )

        shake_step(0, 1)

    @staticmethod
    def flash_border(widget: Widget, color: str = "red", duration: float = 0.5) -> None:
        """
        Flash border color (visual feedback).

        Args:
            widget: Widget to flash
            color: Border color to flash
            duration: Animation duration in seconds
        """
        original_border = widget.styles.border
        widget.styles.border = ("solid", color)
        widget.set_timer(duration, lambda: setattr(widget.styles, "border", original_border))


# Export commonly used presets as module-level constants
MODE_TRANSITION = ANIMATION_PRESETS["mode_transition"]
WORKSPACE_SWITCH = ANIMATION_PRESETS["workspace_switch"]
PANE_FOCUS = ANIMATION_PRESETS["pane_focus"]
OVERLAY_SHOW = ANIMATION_PRESETS["overlay_show"]
OVERLAY_HIDE = ANIMATION_PRESETS["overlay_hide"]
FOCUS_MODE = ANIMATION_PRESETS["focus_mode"]
TOAST = ANIMATION_PRESETS["toast"]
BUTTON_PRESS = ANIMATION_PRESETS["button_press"]
HOVER = ANIMATION_PRESETS["hover"]
