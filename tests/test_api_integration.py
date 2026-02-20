"""Tests for Phase 4: Real API Integration."""

import asyncio
import os
import sys
from pathlib import Path

# Set test API key
os.environ["ANTHROPIC_API_KEY"] = "test-key-12345"

# Make pytest optional
try:
    import pytest
except ImportError:
    pytest = None

    # Mock pytest.skip for standalone running
    class MockPytest:
        @staticmethod
        def skip(msg):
            print(f"SKIPPED: {msg}")
            return

    if pytest is None:
        pytest = MockPytest()


def test_anthropic_client_imports():
    """Test that Anthropic client imports correctly."""
    from claude_multi_terminal.api import AnthropicClient
    assert AnthropicClient is not None


def test_token_tracker_imports():
    """Test that token tracker imports correctly."""
    from claude_multi_terminal.api import TokenTracker, TokenUsage, SessionTokenUsage
    assert TokenTracker is not None
    assert TokenUsage is not None
    assert SessionTokenUsage is not None


def test_cache_manager_imports():
    """Test that cache manager imports correctly."""
    from claude_multi_terminal.api import CacheManager
    assert CacheManager is not None


def test_vision_handler_imports():
    """Test that vision handler imports correctly."""
    from claude_multi_terminal.api import VisionHandler
    assert VisionHandler is not None


def test_token_usage_calculation():
    """Test token usage cost calculation."""
    from claude_multi_terminal.api.token_tracker import TokenUsage

    usage = TokenUsage(
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=200,
    )

    # Test properties
    assert usage.total_tokens == 1500
    assert usage.non_cached_input_tokens == 800

    # Test cost calculation for Sonnet
    cost = usage.calculate_cost("claude-sonnet-4-5-20250929")
    assert cost > 0

    # Test legacy model name
    cost_legacy = usage.calculate_cost("claude-sonnet-4.5")
    assert cost_legacy == cost


def test_token_usage_addition():
    """Test adding token usage objects."""
    from claude_multi_terminal.api.token_tracker import TokenUsage

    usage1 = TokenUsage(input_tokens=100, output_tokens=50, cached_tokens=10)
    usage2 = TokenUsage(input_tokens=200, output_tokens=100, cached_tokens=20)

    total = usage1 + usage2

    assert total.input_tokens == 300
    assert total.output_tokens == 150
    assert total.cached_tokens == 30


def test_session_token_usage():
    """Test session token usage tracking."""
    from claude_multi_terminal.api.token_tracker import SessionTokenUsage, TokenUsage

    session = SessionTokenUsage(
        session_id="test-123",
        model_name="claude-sonnet-4-5-20250929",
    )

    # Add requests
    session.add_request(TokenUsage(input_tokens=100, output_tokens=50, cached_tokens=10))
    session.add_request(TokenUsage(input_tokens=200, output_tokens=100, cached_tokens=20))

    assert session.request_count == 2
    assert session.total_usage.input_tokens == 300
    assert session.total_usage.output_tokens == 150
    assert session.cache_hit_rate > 0


def test_token_tracker_persistence():
    """Test token tracker persistence."""
    import tempfile
    from claude_multi_terminal.api.token_tracker import TokenTracker

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        # Create tracker and add data
        tracker = TokenTracker(persistence_path=temp_path)
        tracker.track_request(
            session_id="test-1",
            model_name="claude-sonnet-4-5-20250929",
            input_tokens=100,
            output_tokens=50,
            cached_tokens=10,
        )

        # Create new tracker and verify data loaded
        tracker2 = TokenTracker(persistence_path=temp_path)
        usage = tracker2.get_session_usage("test-1")

        assert usage is not None
        assert usage.total_usage.input_tokens == 100

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_cache_manager_basic():
    """Test cache manager basic functionality."""
    from claude_multi_terminal.api.cache_manager import CacheManager

    manager = CacheManager(enable_caching=True)

    # Build cached system prompt
    system = manager.build_cached_system_prompt("You are a helpful assistant.")

    assert isinstance(system, list)
    assert len(system) > 0
    assert system[0]["type"] == "text"
    assert "cache_control" in system[0]


def test_cache_manager_stats():
    """Test cache manager statistics."""
    from claude_multi_terminal.api.cache_manager import CacheManager

    manager = CacheManager(enable_caching=True)

    # Build multiple prompts
    manager.build_cached_system_prompt("Prompt 1", cache_key="key1")
    manager.build_cached_system_prompt("Prompt 1", cache_key="key1")  # Hit
    manager.build_cached_system_prompt("Prompt 2", cache_key="key2")  # Miss

    stats = manager.get_cache_stats()

    assert stats["total_requests"] == 3
    assert stats["cache_hits"] >= 1
    assert stats["cache_misses"] >= 2


def test_cache_manager_expiration():
    """Test cache entry expiration."""
    from claude_multi_terminal.api.cache_manager import CacheEntry
    import time

    entry = CacheEntry(
        content="test",
        cache_key="key1",
        created_at=time.time() - 400,  # 400 seconds ago
        last_used=time.time() - 400,
    )

    assert entry.is_expired(ttl_seconds=300)  # Should be expired

    entry.mark_used()
    assert not entry.is_expired(ttl_seconds=300)  # Should not be expired


def test_vision_handler_supported_formats():
    """Test vision handler format detection."""
    from claude_multi_terminal.api.vision_handler import VisionHandler

    handler = VisionHandler()

    assert handler.is_supported_format("image.png")
    assert handler.is_supported_format("photo.jpg")
    assert handler.is_supported_format("pic.jpeg")
    assert handler.is_supported_format("animation.gif")
    assert handler.is_supported_format("modern.webp")
    assert not handler.is_supported_format("document.pdf")


def test_vision_handler_load_from_bytes():
    """Test loading image from bytes."""
    from claude_multi_terminal.api.vision_handler import VisionHandler

    handler = VisionHandler()

    # Create fake image bytes
    fake_image = b"fake image data"

    image = handler.load_image_from_bytes(fake_image, media_type="image/png")

    assert image.source_type == "base64"
    assert image.media_type == "image/png"
    assert len(image.data) > 0


def test_vision_handler_url():
    """Test loading image from URL."""
    from claude_multi_terminal.api.vision_handler import VisionHandler

    handler = VisionHandler()

    image = handler.load_image_from_url("https://example.com/image.jpg")

    assert image.source_type == "url"
    assert image.data == "https://example.com/image.jpg"


def test_vision_handler_message_building():
    """Test building vision messages."""
    from claude_multi_terminal.api.vision_handler import VisionHandler, ImageContent

    handler = VisionHandler()

    # Create fake images
    image1 = ImageContent(
        source_type="base64",
        media_type="image/png",
        data="base64data1",
    )
    image2 = ImageContent(
        source_type="base64",
        media_type="image/jpeg",
        data="base64data2",
    )

    message = handler.build_vision_message(
        text="What's in these images?",
        images=[image1, image2],
    )

    assert message["role"] == "user"
    assert isinstance(message["content"], list)
    assert len(message["content"]) == 3  # 2 images + 1 text


def test_api_session_manager_creation():
    """Test API session manager creation."""
    from claude_multi_terminal.core.api_session_manager import APISessionManager

    # This should work even without a real API key for basic testing
    try:
        manager = APISessionManager(
            api_key="test-key",
            default_model="claude-sonnet-4-5-20250929",
        )
        assert manager is not None
    except ImportError as e:
        pytest.skip(f"Anthropic SDK not available: {e}")


def test_format_functions():
    """Test formatting helper functions."""
    from claude_multi_terminal.api.token_tracker import (
        format_tokens,
        format_cost,
        format_usage_compact,
        TokenUsage,
    )

    # Test token formatting
    assert format_tokens(500) == "500"
    assert "K" in format_tokens(1500)
    assert "M" in format_tokens(1500000)

    # Test cost formatting
    assert format_cost(0.0123).startswith("$")

    # Test usage formatting
    usage = TokenUsage(input_tokens=1000, output_tokens=500, cached_tokens=100)
    formatted = format_usage_compact(usage, "claude-sonnet-4-5-20250929")
    assert "tok" in formatted
    assert "$" in formatted


def test_cache_savings_calculation():
    """Test cache savings calculation."""
    from claude_multi_terminal.api.cache_manager import estimate_cache_savings

    savings = estimate_cache_savings(
        input_tokens=1000,
        cached_tokens=500,
        model_name="claude-sonnet-4-5-20250929",
    )

    assert savings > 0
    assert isinstance(savings, float)


if __name__ == "__main__":
    # Run tests
    print("Running Phase 4 API Integration Tests...")
    print()

    test_anthropic_client_imports()
    print("✓ Anthropic client imports")

    test_token_tracker_imports()
    print("✓ Token tracker imports")

    test_cache_manager_imports()
    print("✓ Cache manager imports")

    test_vision_handler_imports()
    print("✓ Vision handler imports")

    test_token_usage_calculation()
    print("✓ Token usage calculation")

    test_token_usage_addition()
    print("✓ Token usage addition")

    test_session_token_usage()
    print("✓ Session token usage")

    test_token_tracker_persistence()
    print("✓ Token tracker persistence")

    test_cache_manager_basic()
    print("✓ Cache manager basic")

    test_cache_manager_stats()
    print("✓ Cache manager stats")

    test_cache_manager_expiration()
    print("✓ Cache expiration")

    test_vision_handler_supported_formats()
    print("✓ Vision handler formats")

    test_vision_handler_load_from_bytes()
    print("✓ Vision handler bytes")

    test_vision_handler_url()
    print("✓ Vision handler URL")

    test_vision_handler_message_building()
    print("✓ Vision message building")

    test_api_session_manager_creation()
    print("✓ API session manager")

    test_format_functions()
    print("✓ Format functions")

    test_cache_savings_calculation()
    print("✓ Cache savings calculation")

    print()
    print("All tests passed! ✅")
