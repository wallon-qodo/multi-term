#!/usr/bin/env python3
"""Simple test of token tracking system."""

import sys
import os

# Import directly
sys.path.insert(0, os.path.dirname(__file__))

from claude_multi_terminal.streaming.token_tracker import (
    TokenTracker,
    TokenUsage,
    format_tokens,
    format_cost,
    format_usage_compact,
    format_usage_detailed,
    MODEL_PRICING,
)


def main():
    """Run token tracking demonstration."""
    print("=" * 80)
    print("TOKEN TRACKER DEMONSTRATION")
    print("=" * 80)
    print()

    # Create tracker with temporary file
    tracker = TokenTracker(persistence_path="/tmp/token_usage_demo.json")

    # Simulate multiple sessions with different models
    print("1. Simulating API requests across multiple sessions...")
    print()

    # Session 1: Research session with Claude Sonnet
    session1_id = "research-session-001"
    tracker.track_request(
        session_id=session1_id,
        model_name="claude-sonnet-4.5",
        input_tokens=1500,
        output_tokens=800,
        cached_tokens=0,
    )
    tracker.track_request(
        session_id=session1_id,
        model_name="claude-sonnet-4.5",
        input_tokens=1200,
        output_tokens=600,
        cached_tokens=400,  # Some cached tokens
    )

    # Session 2: Code generation with Claude Opus
    session2_id = "code-gen-session-002"
    tracker.track_request(
        session_id=session2_id,
        model_name="claude-opus-4.6",
        input_tokens=2000,
        output_tokens=1500,
        cached_tokens=0,
    )

    # Session 3: Quick queries with Haiku
    session3_id = "quick-queries-003"
    tracker.track_request(
        session_id=session3_id,
        model_name="claude-haiku-4.5",
        input_tokens=500,
        output_tokens=300,
        cached_tokens=0,
    )
    tracker.track_request(
        session_id=session3_id,
        model_name="claude-haiku-4.5",
        input_tokens=600,
        output_tokens=400,
        cached_tokens=200,
    )

    print("2. Model Pricing Table:")
    print("-" * 80)
    print(f"{'Model':<25} {'Input (per 1K)':<20} {'Output (per 1K)':<20}")
    print("-" * 80)
    for model, pricing in MODEL_PRICING.items():
        print(f"{model:<25} ${pricing['input']:<19.4f} ${pricing['output']:<19.4f}")
    print(f"{'Cached tokens:':<25} {'90% discount on input':<40}")
    print("-" * 80)
    print()

    print("3. Session Summaries:")
    print("-" * 80)

    for session_id in [session1_id, session2_id, session3_id]:
        session = tracker.get_session_usage(session_id)
        if session:
            print(f"\nSession: {session.session_id}")
            print(f"Model: {session.model_name}")
            print(f"Requests: {session.request_count}")
            print(f"Total tokens: {format_tokens(session.total_usage.total_tokens)}")
            print(f"Input: {format_tokens(session.total_usage.input_tokens)}")
            print(f"Output: {format_tokens(session.total_usage.output_tokens)}")
            print(f"Cached: {format_tokens(session.total_usage.cached_tokens)}")
            print(f"Total cost: {format_cost(session.total_cost_usd)}")
            print()
            print(f"  Compact format: {format_usage_compact(session.total_usage, session.model_name)}")
            print(f"  Detailed format: {format_usage_detailed(session.total_usage, session.model_name)}")

    print("-" * 80)
    print()

    print("4. Global Summary:")
    print("-" * 80)
    global_usage = tracker.get_global_usage()
    global_cost = tracker.get_global_cost()

    print(f"Total tokens: {format_tokens(global_usage.total_tokens)}")
    print(f"Input tokens: {format_tokens(global_usage.input_tokens)}")
    print(f"Output tokens: {format_tokens(global_usage.output_tokens)}")
    print(f"Cached tokens: {format_tokens(global_usage.cached_tokens)}")
    print(f"Total cost: {format_cost(global_cost)}")
    print(f"Sessions: {len(tracker.session_usage)}")
    print("-" * 80)
    print()

    print("5. Export Usage Report:")
    print("-" * 80)
    report = tracker.export_usage_report()
    print(f"Report generated at: {report['generated_at']}")
    print(f"Total sessions: {report['global_summary']['session_count']}")
    print(f"Global cost: {format_cost(report['global_summary']['total_cost_usd'])}")
    print(f"Data saved to: {tracker.persistence_path}")
    print("-" * 80)
    print()

    print("6. Formatting Examples:")
    print("-" * 80)
    examples = [
        (500, 300, 0, "claude-sonnet-4.5", "Small request, no cache"),
        (1500, 800, 500, "claude-sonnet-4.5", "Medium request, 500 cached"),
        (5000, 3000, 2000, "claude-opus-4.6", "Large request, 2K cached"),
        (150000, 80000, 50000, "claude-haiku-4.5", "Very large request, 50K cached"),
    ]

    for input_tok, output_tok, cached_tok, model, description in examples:
        usage = TokenUsage(
            input_tokens=input_tok,
            output_tokens=output_tok,
            cached_tokens=cached_tok,
        )
        print(f"\n{description}:")
        print(f"  Compact: {format_usage_compact(usage, model)}")
        print(f"  Detailed: {format_usage_detailed(usage, model)}")

    print()
    print("-" * 80)
    print()

    print("7. Cost Savings from Caching:")
    print("-" * 80)
    # Show savings calculation
    usage_no_cache = TokenUsage(input_tokens=2000, output_tokens=1000, cached_tokens=0)
    usage_with_cache = TokenUsage(input_tokens=2000, output_tokens=1000, cached_tokens=800)

    cost_no_cache = usage_no_cache.calculate_cost("claude-sonnet-4.5")
    cost_with_cache = usage_with_cache.calculate_cost("claude-sonnet-4.5")
    savings = cost_no_cache - cost_with_cache
    savings_pct = (savings / cost_no_cache) * 100

    print(f"Request: 2K input, 1K output (claude-sonnet-4.5)")
    print(f"Without cache: {format_cost(cost_no_cache)}")
    print(f"With 800 cached: {format_cost(cost_with_cache)}")
    print(f"Savings: {format_cost(savings)} ({savings_pct:.1f}%)")
    print("-" * 80)
    print()

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
