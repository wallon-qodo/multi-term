"""Anthropic prompt caching management for 90% cost reduction."""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """Represents a cached prompt segment."""

    content: str
    cache_key: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    use_count: int = 0
    tokens_saved: int = 0

    def mark_used(self, tokens_saved: int = 0) -> None:
        """Mark this cache entry as used."""
        self.last_used = time.time()
        self.use_count += 1
        self.tokens_saved += tokens_saved

    def is_expired(self, ttl_seconds: int = 300) -> bool:
        """
        Check if cache entry is expired.

        Anthropic's prompt caching has a 5-minute TTL.

        Args:
            ttl_seconds: Time to live in seconds (default: 300 = 5 minutes)

        Returns:
            True if expired, False otherwise
        """
        return (time.time() - self.last_used) > ttl_seconds


class CacheManager:
    """
    Manages Anthropic prompt caching for cost optimization.

    Anthropic's prompt caching provides:
    - 90% cost reduction on cached prompts
    - 5-minute cache TTL
    - Automatic cache key management
    - Cache hit tracking

    Usage:
    - System prompts are prime candidates for caching
    - Long context (tool definitions, documentation) benefits most
    - Repeated prompts within 5 minutes get cached
    """

    def __init__(
        self,
        cache_ttl: int = 300,  # 5 minutes (Anthropic's TTL)
        enable_caching: bool = True,
    ):
        """
        Initialize cache manager.

        Args:
            cache_ttl: Cache time-to-live in seconds
            enable_caching: Whether to enable caching
        """
        self.cache_ttl = cache_ttl
        self.enable_caching = enable_caching
        self.cache_entries: Dict[str, CacheEntry] = {}

        # Statistics
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_tokens_saved = 0

    def build_cached_system_prompt(
        self,
        system_content: str,
        cache_key: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build a system prompt with caching enabled.

        Args:
            system_content: System prompt content
            cache_key: Optional cache key (default: hash of content)

        Returns:
            List of system message blocks with cache control
        """
        if not self.enable_caching:
            # Return simple system prompt
            return system_content

        # Generate cache key
        if cache_key is None:
            cache_key = f"sys_{hash(system_content)}"

        # Track cache entry
        self._track_cache_entry(cache_key, system_content)

        # Return system prompt with cache control
        # Anthropic API format for cached prompts
        return [
            {
                "type": "text",
                "text": system_content,
                "cache_control": {"type": "ephemeral"}
            }
        ]

    def build_cached_messages(
        self,
        messages: List[Dict[str, Any]],
        cache_recent: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Build message list with caching on recent messages.

        Useful for caching long conversation history.

        Args:
            messages: List of message dicts
            cache_recent: Number of recent messages to cache (0 = none)

        Returns:
            Messages with cache control on specified entries
        """
        if not self.enable_caching or cache_recent == 0:
            return messages

        # Add cache control to recent messages
        result = []
        cache_start = max(0, len(messages) - cache_recent)

        for i, msg in enumerate(messages):
            if i >= cache_start:
                # Add cache control
                msg_copy = msg.copy()
                if isinstance(msg_copy.get("content"), str):
                    msg_copy["content"] = [
                        {
                            "type": "text",
                            "text": msg_copy["content"],
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
                result.append(msg_copy)
            else:
                result.append(msg)

        return result

    def _track_cache_entry(self, cache_key: str, content: str) -> None:
        """Track a cache entry."""
        self.total_requests += 1

        if cache_key in self.cache_entries:
            entry = self.cache_entries[cache_key]

            # Check if expired
            if entry.is_expired(self.cache_ttl):
                # Cache miss - expired
                self.cache_misses += 1
                # Create new entry
                self.cache_entries[cache_key] = CacheEntry(
                    content=content,
                    cache_key=cache_key,
                )
            else:
                # Cache hit
                self.cache_hits += 1
                entry.mark_used()
        else:
            # Cache miss - new entry
            self.cache_misses += 1
            self.cache_entries[cache_key] = CacheEntry(
                content=content,
                cache_key=cache_key,
            )

    def record_cache_hit(
        self,
        cache_key: str,
        tokens_saved: int,
    ) -> None:
        """
        Record a cache hit from API response.

        Args:
            cache_key: Cache key
            tokens_saved: Number of tokens saved by caching
        """
        if cache_key in self.cache_entries:
            self.cache_entries[cache_key].mark_used(tokens_saved)
            self.total_tokens_saved += tokens_saved

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with cache statistics
        """
        hit_rate = (self.cache_hits / self.total_requests * 100) if self.total_requests > 0 else 0

        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "total_tokens_saved": self.total_tokens_saved,
            "active_entries": len([
                e for e in self.cache_entries.values()
                if not e.is_expired(self.cache_ttl)
            ]),
            "expired_entries": len([
                e for e in self.cache_entries.values()
                if e.is_expired(self.cache_ttl)
            ]),
        }

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self.cache_entries.items()
            if entry.is_expired(self.cache_ttl)
        ]

        for key in expired_keys:
            del self.cache_entries[key]

        return len(expired_keys)

    def clear_cache(self) -> None:
        """Clear all cache entries."""
        self.cache_entries.clear()

    def enable(self) -> None:
        """Enable caching."""
        self.enable_caching = True

    def disable(self) -> None:
        """Disable caching."""
        self.enable_caching = False


def estimate_cache_savings(
    input_tokens: int,
    cached_tokens: int,
    model_name: str = "claude-sonnet-4-5-20250929",
) -> float:
    """
    Estimate cost savings from prompt caching.

    Args:
        input_tokens: Total input tokens
        cached_tokens: Cached input tokens
        model_name: Model name

    Returns:
        Savings in USD
    """
    from .token_tracker import MODEL_PRICING, MODEL_ALIASES

    # Handle legacy names
    model_name = MODEL_ALIASES.get(model_name, model_name)
    pricing = MODEL_PRICING.get(model_name)

    if not pricing:
        return 0.0

    # Calculate what we would have paid without caching
    full_price = (cached_tokens / 1_000_000) * pricing["input"]

    # Calculate what we paid with caching
    cached_price = (cached_tokens / 1_000_000) * pricing["cached_input"]

    return full_price - cached_price


def format_cache_stats(stats: Dict[str, Any]) -> str:
    """
    Format cache statistics for display.

    Args:
        stats: Statistics dictionary from get_cache_stats()

    Returns:
        Formatted string
    """
    return (
        f"Cache Performance:\n"
        f"  Requests: {stats['total_requests']}\n"
        f"  Hits: {stats['cache_hits']} ({stats['hit_rate']:.1f}%)\n"
        f"  Misses: {stats['cache_misses']}\n"
        f"  Tokens Saved: {stats['total_tokens_saved']:,}\n"
        f"  Active Entries: {stats['active_entries']}\n"
        f"  Expired Entries: {stats['expired_entries']}"
    )
