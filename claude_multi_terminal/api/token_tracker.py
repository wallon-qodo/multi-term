"""Real token tracking from Anthropic API responses."""

import json
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# Model pricing per 1M tokens (USD)
MODEL_PRICING = {
    "claude-opus-4-6-20250118": {
        "input": 15.00,
        "output": 75.00,
        "cached_input": 1.50,  # 90% discount
    },
    "claude-sonnet-4-5-20250929": {
        "input": 3.00,
        "output": 15.00,
        "cached_input": 0.30,
    },
    "claude-haiku-4-5-20250124": {
        "input": 1.00,
        "output": 5.00,
        "cached_input": 0.10,
    },
}

# Legacy model names for backward compatibility
MODEL_ALIASES = {
    "claude-opus-4.6": "claude-opus-4-6-20250118",
    "claude-sonnet-4.5": "claude-sonnet-4-5-20250929",
    "claude-haiku-4.5": "claude-haiku-4-5-20250124",
}


@dataclass
class TokenUsage:
    """Token usage statistics from API response."""

    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    timestamp: float = field(default_factory=time.time)

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.input_tokens + self.output_tokens

    @property
    def non_cached_input_tokens(self) -> int:
        """Input tokens that were not cached."""
        return max(0, self.input_tokens - self.cached_tokens)

    def calculate_cost(self, model_name: str) -> float:
        """
        Calculate cost in USD based on actual API token counts.

        Args:
            model_name: Model name (e.g., "claude-sonnet-4-5-20250929")

        Returns:
            Cost in USD
        """
        # Handle legacy model names
        model_name = MODEL_ALIASES.get(model_name, model_name)

        pricing = MODEL_PRICING.get(model_name)
        if not pricing:
            # Unknown model, return 0
            return 0.0

        # Calculate costs per million tokens
        non_cached_cost = (self.non_cached_input_tokens / 1_000_000) * pricing["input"]
        cached_cost = (self.cached_tokens / 1_000_000) * pricing["cached_input"]
        output_cost = (self.output_tokens / 1_000_000) * pricing["output"]

        return non_cached_cost + cached_cost + output_cost

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        """Add two TokenUsage objects together."""
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cached_tokens=self.cached_tokens + other.cached_tokens,
            timestamp=max(self.timestamp, other.timestamp),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "total_tokens": self.total_tokens,
            "timestamp": self.timestamp,
        }


@dataclass
class SessionTokenUsage:
    """Token usage statistics for a session with real API data."""

    session_id: str
    model_name: str
    total_usage: TokenUsage = field(default_factory=TokenUsage)
    request_history: List[TokenUsage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

    @property
    def total_cost_usd(self) -> float:
        """Total cost for this session based on actual API usage."""
        return self.total_usage.calculate_cost(self.model_name)

    @property
    def request_count(self) -> int:
        """Number of API requests tracked."""
        return len(self.request_history)

    @property
    def cache_hit_rate(self) -> float:
        """Percentage of input tokens that were cached."""
        if self.total_usage.input_tokens == 0:
            return 0.0
        return (self.total_usage.cached_tokens / self.total_usage.input_tokens) * 100

    @property
    def cost_savings_from_cache(self) -> float:
        """Cost savings from prompt caching in USD."""
        # Handle legacy model names
        model_name = MODEL_ALIASES.get(self.model_name, self.model_name)
        pricing = MODEL_PRICING.get(model_name)

        if not pricing:
            return 0.0

        # Calculate what we would have paid without caching
        full_price = (self.total_usage.cached_tokens / 1_000_000) * pricing["input"]
        # Calculate what we actually paid with caching
        cached_price = (self.total_usage.cached_tokens / 1_000_000) * pricing["cached_input"]

        return full_price - cached_price

    def add_request(self, usage: TokenUsage) -> None:
        """
        Add a request from API response to the history.

        Args:
            usage: Token usage from API response
        """
        self.request_history.append(usage)
        self.total_usage = self.total_usage + usage
        self.last_updated = time.time()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "model_name": self.model_name,
            "total_usage": self.total_usage.to_dict(),
            "request_history": [u.to_dict() for u in self.request_history],
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "total_cost_usd": self.total_cost_usd,
            "request_count": self.request_count,
            "cache_hit_rate": self.cache_hit_rate,
            "cost_savings_from_cache": self.cost_savings_from_cache,
        }


class TokenTracker:
    """
    Tracks real token usage from Anthropic API responses.

    Replaces estimated tracking with actual API data including:
    - Real input/output token counts
    - Cached token counts
    - Actual costs
    - Cache hit rates
    """

    def __init__(self, persistence_path: Optional[str] = None):
        """
        Initialize token tracker with real API tracking.

        Args:
            persistence_path: Path to save usage data (default: ~/.multi-term/token_usage.json)
        """
        if persistence_path is None:
            persistence_path = os.path.expanduser("~/.multi-term/token_usage.json")

        self.persistence_path = Path(persistence_path)
        self.session_usage: Dict[str, SessionTokenUsage] = {}
        self._lock = threading.Lock()
        self._auto_save = True

        # Load existing data if available
        self._load_data()

    def track_request(
        self,
        session_id: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> None:
        """
        Track a request's actual token usage from API response.

        Args:
            session_id: Session identifier
            model_name: Model used (e.g., "claude-sonnet-4-5-20250929")
            input_tokens: Actual input tokens from API
            output_tokens: Actual output tokens from API
            cached_tokens: Cached input tokens from API
        """
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
        )

        with self._lock:
            if session_id not in self.session_usage:
                self.session_usage[session_id] = SessionTokenUsage(
                    session_id=session_id,
                    model_name=model_name,
                )

            self.session_usage[session_id].add_request(usage)

            # Auto-save to disk
            if self._auto_save:
                self._save_data()

    def get_session_usage(self, session_id: str) -> Optional[SessionTokenUsage]:
        """
        Get usage statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            SessionTokenUsage with real API data if session exists, None otherwise
        """
        with self._lock:
            return self.session_usage.get(session_id)

    def get_global_usage(self) -> TokenUsage:
        """
        Get total usage across all sessions from real API data.

        Returns:
            Aggregated TokenUsage from API responses
        """
        with self._lock:
            total = TokenUsage()
            for session in self.session_usage.values():
                total = total + session.total_usage
            return total

    def get_global_cost(self) -> float:
        """
        Get total cost across all sessions from real API data.

        Returns:
            Total cost in USD based on actual API usage
        """
        with self._lock:
            total_cost = 0.0
            for session in self.session_usage.values():
                total_cost += session.total_cost_usd
            return total_cost

    def get_global_cache_savings(self) -> float:
        """
        Get total cost savings from prompt caching across all sessions.

        Returns:
            Total savings in USD from prompt caching
        """
        with self._lock:
            total_savings = 0.0
            for session in self.session_usage.values():
                total_savings += session.cost_savings_from_cache
            return total_savings

    def reset_session_usage(self, session_id: str) -> bool:
        """
        Reset usage statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session existed and was reset, False otherwise
        """
        with self._lock:
            if session_id in self.session_usage:
                del self.session_usage[session_id]
                if self._auto_save:
                    self._save_data()
                return True
            return False

    def export_usage_report(self) -> dict:
        """
        Export complete usage report with real API data.

        Returns:
            JSON-serializable dictionary with all real usage data
        """
        with self._lock:
            global_usage = self.get_global_usage()
            global_cost = self.get_global_cost()
            global_savings = self.get_global_cache_savings()

            return {
                "generated_at": time.time(),
                "generated_at_readable": datetime.fromtimestamp(time.time()).isoformat(),
                "data_source": "Anthropic API",
                "global_summary": {
                    "total_tokens": global_usage.total_tokens,
                    "input_tokens": global_usage.input_tokens,
                    "output_tokens": global_usage.output_tokens,
                    "cached_tokens": global_usage.cached_tokens,
                    "total_cost_usd": global_cost,
                    "cache_savings_usd": global_savings,
                    "session_count": len(self.session_usage),
                },
                "sessions": {
                    session_id: session.to_dict()
                    for session_id, session in self.session_usage.items()
                },
                "model_pricing": MODEL_PRICING,
            }

    def _save_data(self) -> None:
        """Save real usage data to disk."""
        try:
            # Create directory if it doesn't exist
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)

            # Write data
            data = self.export_usage_report()
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # Log error but don't crash
            print(f"Warning: Failed to save token usage data: {e}")

    def _load_data(self) -> None:
        """Load usage data from disk."""
        try:
            if not self.persistence_path.exists():
                return

            with open(self.persistence_path, 'r') as f:
                data = json.load(f)

            # Reconstruct session usage
            sessions_data = data.get("sessions", {})
            for session_id, session_data in sessions_data.items():
                # Reconstruct total usage
                total_usage_data = session_data.get("total_usage", {})
                total_usage = TokenUsage(
                    input_tokens=total_usage_data.get("input_tokens", 0),
                    output_tokens=total_usage_data.get("output_tokens", 0),
                    cached_tokens=total_usage_data.get("cached_tokens", 0),
                    timestamp=total_usage_data.get("timestamp", time.time()),
                )

                # Reconstruct request history
                request_history = []
                for req_data in session_data.get("request_history", []):
                    request_history.append(TokenUsage(
                        input_tokens=req_data.get("input_tokens", 0),
                        output_tokens=req_data.get("output_tokens", 0),
                        cached_tokens=req_data.get("cached_tokens", 0),
                        timestamp=req_data.get("timestamp", time.time()),
                    ))

                # Create session usage
                self.session_usage[session_id] = SessionTokenUsage(
                    session_id=session_id,
                    model_name=session_data.get("model_name", "claude-sonnet-4-5-20250929"),
                    total_usage=total_usage,
                    request_history=request_history,
                    created_at=session_data.get("created_at", time.time()),
                    last_updated=session_data.get("last_updated", time.time()),
                )
        except Exception as e:
            # Log error but don't crash - start fresh
            print(f"Warning: Failed to load token usage data: {e}")


def format_tokens(count: int, precision: int = 1) -> str:
    """
    Format token count with K/M suffixes.

    Args:
        count: Token count
        precision: Decimal precision for K/M values

    Returns:
        Formatted string (e.g., "1.2K", "500", "2.5M")
    """
    if count >= 1_000_000:
        return f"{count / 1_000_000:.{precision}f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.{precision}f}K"
    else:
        return str(count)


def format_cost(cost_usd: float, precision: int = 4) -> str:
    """
    Format cost in USD with appropriate precision.

    Args:
        cost_usd: Cost in dollars
        precision: Decimal precision

    Returns:
        Formatted string (e.g., "$0.0012", "$1.2345")
    """
    return f"${cost_usd:.{precision}f}"


def format_usage_compact(usage: TokenUsage, model_name: str) -> str:
    """
    Format usage in compact form: "1.2K tok ($0.05)"

    Args:
        usage: Token usage from API
        model_name: Model name for cost calculation

    Returns:
        Compact formatted string with real API data
    """
    tokens = format_tokens(usage.total_tokens)
    cost = format_cost(usage.calculate_cost(model_name))

    if usage.cached_tokens > 0:
        cached = format_tokens(usage.cached_tokens)
        cache_pct = (usage.cached_tokens / usage.input_tokens * 100) if usage.input_tokens > 0 else 0
        return f"{tokens} tok ({cached} cached, {cache_pct:.0f}%) {cost}"
    else:
        return f"{tokens} tok {cost}"


def format_usage_detailed(usage: TokenUsage, model_name: str) -> str:
    """
    Format usage in detailed form with real API data.

    Args:
        usage: Token usage from API
        model_name: Model name for cost calculation

    Returns:
        Detailed formatted string
    """
    input_str = format_tokens(usage.input_tokens)
    output_str = format_tokens(usage.output_tokens)
    cost = format_cost(usage.calculate_cost(model_name))

    result = f"In: {input_str}, Out: {output_str}, Cost: {cost}"

    if usage.cached_tokens > 0:
        cached = format_tokens(usage.cached_tokens)
        cache_pct = (usage.cached_tokens / usage.input_tokens * 100) if usage.input_tokens > 0 else 0
        result += f" (Cached: {cached}, {cache_pct:.0f}%)"

    return result
