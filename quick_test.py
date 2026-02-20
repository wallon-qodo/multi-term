#!/usr/bin/env python3
import sys
sys.path.insert(0, 'claude_multi_terminal/streaming')
from token_tracker import TokenTracker, TokenUsage, format_tokens, format_cost, format_usage_compact, MODEL_PRICING

print('TOKEN TRACKER TEST')
print('=' * 60)

tracker = TokenTracker(persistence_path='/tmp/test_tokens.json')
tracker.track_request('test-001', 'claude-sonnet-4.5', 1500, 800, 0)
tracker.track_request('test-001', 'claude-sonnet-4.5', 1200, 600, 400)

session = tracker.get_session_usage('test-001')
print(f'Session: {session.session_id}')
print(f'Model: {session.model_name}')
print(f'Requests: {session.request_count}')
print(f'Tokens: {format_tokens(session.total_usage.total_tokens)}')
print(f'Cost: {format_cost(session.total_cost_usd)}')
print(f'Compact: {format_usage_compact(session.total_usage, session.model_name)}')
print()
print('Model Pricing:')
for model, p in MODEL_PRICING.items():
    print(f'  {model}: input=${p["input"]}, output=${p["output"]}')
print()
usage = TokenUsage(5000, 3000, 2000)
print(f'Format test (5K in, 3K out, 2K cached):')
print(f'  Compact: {format_usage_compact(usage, "claude-opus-4.6")}')
print()
print('TEST COMPLETE')
