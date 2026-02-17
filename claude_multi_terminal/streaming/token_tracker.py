"""Token usage tracking and cost calculation for Claude API calls."""

import json
import os
import threading
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional


# Model pricing per 1K tokens (USD)
MODEL_PRICING = {
    "claude-opus-4.6": {
        "input": 0.015,
        "output": 0.075,
    },
    "claude-sonnet-4.5": {
        "input": 0.003,
        "output": 0.015,
    },
    "claude-haiku-4.5": {
        "input": 0.001,
        "output": 0.005,
    },
}

# Cached tokens get 90% discount on input pricing
CACHE_DISCOUNT = 0.90


@dataclass
class TokenUsage:
    """Token usage statistics for a single request."""

    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output, cached tokens count toward input)."""
        return self.input_tokens + self.output_tokens

    @property
    def non_cached_input_tokens(self) -> int:
        """Input tokens that were not cached."""
        return max(0, self.input_tokens - self.cached_tokens)

    def calculate_cost(self, model_name: str) -> float:
        """
        Calculate cost in USD for this usage.

        Args:
            model_name: Name of the model used (e.g., "claude-sonnet-4.5")

        Returns:
            Cost in USD
        """
        pricing = MODEL_PRICING.get(model_name)
        if not pricing:
            # Unknown model, return 0
            return 0.0

        # Calculate input cost (non-cached at full price, cached at 10%)
        non_cached_cost = (self.non_cached_input_tokens / 1000) * pricing["input"]
        cached_cost = (self.cached_tokens / 1000) * pricing["input"] * (1 - CACHE_DISCOUNT)
        input_cost = non_cached_cost + cached_cost

        # Calculate output cost
        output_cost = (self.output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        """Add two TokenUsage objects together."""
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cached_tokens=self.cached_tokens + other.cached_tokens,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class SessionTokenUsage:
    """Token usage statistics for a session."""

    session_id: str
    model_name: str
    total_usage: TokenUsage = field(default_factory=TokenUsage)
    request_history: List[TokenUsage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

    @property
    def total_cost_usd(self) -> float:
        """Total cost for this session."""
        return self.total_usage.calculate_cost(self.model_name)

    @property
    def request_count(self) -> int:
        """Number of requests tracked."""
        return len(self.request_history)

    def add_request(self, usage: TokenUsage) -> None:
        """
        Add a request to the history.

        Args:
            usage: Token usage for the request
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
        }


class TokenTracker:
    """Tracks token usage across all sessions."""

    def __init__(self, persistence_path: Optional[str] = None):
        """
        Initialize token tracker.

        Args:
            persistence_path: Path to save usage data (default: ~/.multi-term/token_usage.json)
        """
        if persistence_path is None:
            persistence_path = os.path.expanduser("~/.multi-term/token_usage.json")

        self.persistence_path = Path(persistence_path)
        self.session_usage: Dict[str, SessionTokenUsage] = {}
        self._lock = threading.Lock()

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
        Track a request's token usage.

        Args:
            session_id: Session identifier
            model_name: Model used (e.g., "claude-sonnet-4.5")
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
            cached_tokens: Cached input tokens (optional)
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

            # Persist to disk
            self._save_data()

    def get_session_usage(self, session_id: str) -> Optional[SessionTokenUsage]:
        """
        Get usage statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            SessionTokenUsage if session exists, None otherwise
        """
        with self._lock:
            return self.session_usage.get(session_id)

    def get_global_usage(self) -> TokenUsage:
        """
        Get total usage across all sessions.

        Returns:
            Aggregated TokenUsage
        """
        with self._lock:
            total = TokenUsage()
            for session in self.session_usage.values():
                total = total + session.total_usage
            return total

    def get_global_cost(self, model_name: str = "claude-sonnet-4.5") -> float:
        """
        Get total cost across all sessions.

        Args:
            model_name: Model to use for cost calculation (if sessions use different models)

        Returns:
            Total cost in USD
        """
        with self._lock:
            total_cost = 0.0
            for session in self.session_usage.values():
                total_cost += session.total_cost_usd
            return total_cost

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
                self._save_data()
                return True
            return False

    def export_usage_report(self) -> dict:
        """
        Export complete usage report.

        Returns:
            JSON-serializable dictionary with all usage data
        """
        with self._lock:
            global_usage = self.get_global_usage()
            global_cost = self.get_global_cost()

            return {
                "generated_at": time.time(),
                "global_summary": {
                    "total_tokens": global_usage.total_tokens,
                    "input_tokens": global_usage.input_tokens,
                    "output_tokens": global_usage.output_tokens,
                    "cached_tokens": global_usage.cached_tokens,
                    "total_cost_usd": global_cost,
                    "session_count": len(self.session_usage),
                },
                "sessions": {
                    session_id: session.to_dict()
                    for session_id, session in self.session_usage.items()
                },
                "model_pricing": MODEL_PRICING,
            }

    def _save_data(self) -> None:
        """Save usage data to disk."""
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
                )

                # Reconstruct request history
                request_history = []
                for req_data in session_data.get("request_history", []):
                    request_history.append(TokenUsage(
                        input_tokens=req_data.get("input_tokens", 0),
                        output_tokens=req_data.get("output_tokens", 0),
                        cached_tokens=req_data.get("cached_tokens", 0),
                    ))

                # Create session usage
                self.session_usage[session_id] = SessionTokenUsage(
                    session_id=session_id,
                    model_name=session_data.get("model_name", "claude-sonnet-4.5"),
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


def format_cost(cost_usd: float, precision: int = 2) -> str:
    """
    Format cost in USD.

    Args:
        cost_usd: Cost in dollars
        precision: Decimal precision

    Returns:
        Formatted string (e.g., "$0.05", "$1.23")
    """
    return f"${cost_usd:.{precision}f}"


def format_usage_compact(usage: TokenUsage, model_name: str) -> str:
    """
    Format usage in compact form: "1.2K tok ($0.05)"

    Args:
        usage: Token usage
        model_name: Model name for cost calculation

    Returns:
        Compact formatted string
    """
    tokens = format_tokens(usage.total_tokens)
    cost = format_cost(usage.calculate_cost(model_name))

    if usage.cached_tokens > 0:
        cached = format_tokens(usage.cached_tokens)
        return f"{tokens} tok ({cached} cached) {cost}"
    else:
        return f"{tokens} tok {cost}"


def format_usage_detailed(usage: TokenUsage, model_name: str) -> str:
    """
    Format usage in detailed form: "In: 800 tok, Out: 400 tok, Cost: $0.05"

    Args:
        usage: Token usage
        model_name: Model name for cost calculation

    Returns:
        Detailed formatted string
    """
    input_str = format_tokens(usage.input_tokens)
    output_str = format_tokens(usage.output_tokens)
    cost = format_cost(usage.calculate_cost(model_name))

    result = f"In: {input_str} tok, Out: {output_str} tok, Cost: {cost}"

    if usage.cached_tokens > 0:
        cached = format_tokens(usage.cached_tokens)
        result += f" ({cached} cached)"

    return result
