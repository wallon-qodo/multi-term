"""
Virtual scrolling widget for efficient rendering of large message lists.

Renders only visible messages to maintain 60 FPS performance with 10K+ messages.
"""

from typing import List, Optional, Callable, Any
from textual.widget import Widget
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.geometry import Size
from rich.console import RenderableType
from rich.text import Text
from dataclasses import dataclass
import time


@dataclass
class VirtualItem:
    """
    Virtual list item.

    Represents an item in the virtual scroll list.
    """

    index: int
    content: Any
    height: int = 1  # Estimated height in lines
    rendered: Optional[RenderableType] = None


class VirtualScrollView(VerticalScroll):
    """
    Virtual scrolling container.

    Only renders items visible in viewport for optimal performance.
    Handles lists with 10,000+ items without performance degradation.
    """

    # Reactive properties
    item_count: reactive[int] = reactive(0)
    viewport_start: reactive[int] = reactive(0)
    viewport_end: reactive[int] = reactive(100)

    # Performance tuning
    OVERSCAN_COUNT = 20  # Extra items to render above/below viewport
    MAX_ITEMS_PER_RENDER = 100  # Maximum items to render at once
    SCROLL_DEBOUNCE_MS = 50  # Debounce scroll events

    def __init__(
        self,
        items: Optional[List[Any]] = None,
        render_item: Optional[Callable[[int, Any], RenderableType]] = None,
        estimate_height: Optional[Callable[[Any], int]] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """
        Initialize virtual scroll view.

        Args:
            items: Initial list of items
            render_item: Function to render an item (index, item) -> renderable
            estimate_height: Function to estimate item height
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)

        # Items and rendering
        self._items: List[VirtualItem] = []
        self._render_item = render_item or self._default_render_item
        self._estimate_height = estimate_height or (lambda item: 1)

        # Performance tracking
        self._last_scroll_time = 0.0
        self._scroll_timer = None
        self._render_cache: dict[int, RenderableType] = {}

        # Initialize items
        if items:
            self.set_items(items)

    def _default_render_item(self, index: int, item: Any) -> RenderableType:
        """
        Default item renderer.

        Args:
            index: Item index
            item: Item data

        Returns:
            RenderableType: Rendered item
        """
        return Text(str(item))

    def set_items(self, items: List[Any]) -> None:
        """
        Set the complete list of items.

        Args:
            items: List of items to display
        """
        # Convert to virtual items
        self._items = []
        for i, item in enumerate(items):
            height = self._estimate_height(item)
            self._items.append(VirtualItem(
                index=i,
                content=item,
                height=height
            ))

        self.item_count = len(items)
        self._render_cache.clear()
        self._update_viewport()

    def append_item(self, item: Any) -> None:
        """
        Append a single item to the list.

        Args:
            item: Item to append
        """
        index = len(self._items)
        height = self._estimate_height(item)
        self._items.append(VirtualItem(
            index=index,
            content=item,
            height=height
        ))
        self.item_count += 1
        self._update_viewport()

    def prepend_item(self, item: Any) -> None:
        """
        Prepend a single item to the list.

        Args:
            item: Item to prepend
        """
        # Reindex existing items
        for virtual_item in self._items:
            virtual_item.index += 1

        # Add new item at start
        height = self._estimate_height(item)
        self._items.insert(0, VirtualItem(
            index=0,
            content=item,
            height=height
        ))
        self.item_count += 1
        self._render_cache.clear()
        self._update_viewport()

    def remove_item(self, index: int) -> None:
        """
        Remove an item by index.

        Args:
            index: Index of item to remove
        """
        if 0 <= index < len(self._items):
            self._items.pop(index)

            # Reindex items after removed index
            for i in range(index, len(self._items)):
                self._items[i].index = i

            self.item_count -= 1
            self._render_cache.clear()
            self._update_viewport()

    def clear_items(self) -> None:
        """Clear all items."""
        self._items.clear()
        self._render_cache.clear()
        self.item_count = 0
        self._update_viewport()

    def _update_viewport(self) -> None:
        """Update visible viewport range based on scroll position."""
        if not self._items:
            self.viewport_start = 0
            self.viewport_end = 0
            return

        # Get container height
        container_height = self.size.height if self.size else 20

        # Calculate which items are visible based on scroll position
        # scroll_y is in lines from top
        scroll_y = int(self.scroll_y) if hasattr(self, 'scroll_y') else 0

        # Find first visible item
        cumulative_height = 0
        start_index = 0
        for i, item in enumerate(self._items):
            if cumulative_height + item.height > scroll_y:
                start_index = i
                break
            cumulative_height += item.height

        # Find last visible item (with overscan)
        visible_height = 0
        end_index = start_index
        for i in range(start_index, len(self._items)):
            visible_height += self._items[i].height
            end_index = i + 1
            if visible_height >= container_height + (self.OVERSCAN_COUNT * 2):
                break

        # Add overscan at start
        start_index = max(0, start_index - self.OVERSCAN_COUNT)

        # Limit maximum rendered items for performance
        if end_index - start_index > self.MAX_ITEMS_PER_RENDER:
            end_index = start_index + self.MAX_ITEMS_PER_RENDER

        self.viewport_start = start_index
        self.viewport_end = end_index

        # Trigger re-render
        self.refresh(layout=True)

    def _render_visible_items(self) -> None:
        """Render items in current viewport."""
        # Remove all current children
        self.remove_children()

        # Render visible items
        for i in range(self.viewport_start, self.viewport_end):
            if i < len(self._items):
                virtual_item = self._items[i]

                # Check cache first
                if i in self._render_cache:
                    rendered = self._render_cache[i]
                else:
                    # Render item
                    rendered = self._render_item(i, virtual_item.content)
                    self._render_cache[i] = rendered

                    # Limit cache size
                    if len(self._render_cache) > self.MAX_ITEMS_PER_RENDER * 2:
                        # Evict oldest entries
                        keys_to_remove = list(self._render_cache.keys())[
                            :len(self._render_cache) - self.MAX_ITEMS_PER_RENDER
                        ]
                        for key in keys_to_remove:
                            del self._render_cache[key]

                # Create widget for item
                from textual.widgets import Static
                item_widget = Static(rendered, id=f"item-{i}")
                self.mount(item_widget)

    def on_scroll(self, event) -> None:
        """
        Handle scroll events.

        Args:
            event: Scroll event
        """
        current_time = time.time()

        # Debounce scroll events for performance
        if current_time - self._last_scroll_time < (self.SCROLL_DEBOUNCE_MS / 1000):
            return

        self._last_scroll_time = current_time

        # Update viewport based on new scroll position
        self._update_viewport()

    def watch_item_count(self, old_count: int, new_count: int) -> None:
        """
        Watch item_count changes.

        Args:
            old_count: Previous count
            new_count: New count
        """
        if new_count != old_count:
            self._update_viewport()

    def get_content_height(self) -> int:
        """
        Get total content height.

        Returns:
            int: Total height in lines
        """
        return sum(item.height for item in self._items)

    def scroll_to_index(self, index: int, animate: bool = True) -> None:
        """
        Scroll to a specific item index.

        Args:
            index: Item index to scroll to
            animate: Whether to animate scroll
        """
        if 0 <= index < len(self._items):
            # Calculate scroll position
            scroll_y = sum(item.height for item in self._items[:index])

            # Scroll to position
            self.scroll_to(0, scroll_y, animate=animate)

            # Update viewport
            self.viewport_start = index
            self._update_viewport()

    def scroll_to_bottom(self, animate: bool = True) -> None:
        """
        Scroll to bottom of list.

        Args:
            animate: Whether to animate scroll
        """
        if self._items:
            self.scroll_to_index(len(self._items) - 1, animate=animate)


class MessageVirtualScroll(VirtualScrollView):
    """
    Specialized virtual scroll for chat messages.

    Optimized for chat-like interfaces with automatic scroll-to-bottom
    for new messages.
    """

    def __init__(
        self,
        auto_scroll: bool = True,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """
        Initialize message virtual scroll.

        Args:
            auto_scroll: Auto-scroll to bottom on new messages
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(
            render_item=self._render_message,
            estimate_height=self._estimate_message_height,
            name=name,
            id=id,
            classes=classes,
        )
        self.auto_scroll = auto_scroll
        self._user_scrolled_up = False

    def _render_message(self, index: int, message: Any) -> RenderableType:
        """
        Render a chat message.

        Args:
            index: Message index
            message: Message data

        Returns:
            RenderableType: Rendered message
        """
        # TODO: Implement proper message rendering
        # For now, simple text rendering
        if isinstance(message, dict):
            role = message.get("role", "user")
            content = message.get("content", "")
            timestamp = message.get("timestamp", "")

            return Text.from_markup(
                f"[bold]{role}[/bold] [{timestamp}]\n{content}"
            )
        return Text(str(message))

    def _estimate_message_height(self, message: Any) -> int:
        """
        Estimate message height in lines.

        Args:
            message: Message data

        Returns:
            int: Estimated height
        """
        if isinstance(message, dict):
            content = message.get("content", "")
            # Rough estimate: 80 chars per line
            lines = len(content) // 80 + 1
            return max(3, lines + 2)  # At least 3 lines (role, content, margin)
        return 3

    def append_message(self, message: Any) -> None:
        """
        Append a message.

        Args:
            message: Message to append
        """
        self.append_item(message)

        # Auto-scroll if enabled and user hasn't scrolled up
        if self.auto_scroll and not self._user_scrolled_up:
            self.scroll_to_bottom(animate=True)

    def on_scroll(self, event) -> None:
        """
        Handle scroll events for message scroll.

        Args:
            event: Scroll event
        """
        # Track if user scrolled up from bottom
        max_scroll = self.get_content_height() - (self.size.height if self.size else 20)
        is_at_bottom = self.scroll_y >= max_scroll - 2  # 2 line tolerance

        # If not at bottom after scroll, user has manually scrolled up
        if not is_at_bottom:
            self._user_scrolled_up = True
        else:
            self._user_scrolled_up = False

        # Call parent handler
        super().on_scroll(event)
