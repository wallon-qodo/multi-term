"""
Phase 1 Modal System - Performance Metrics Test
Measures performance characteristics of modal system operations.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def measure_import_time():
    """Measure import time for modal system modules."""
    print("\n1. MODULE IMPORT PERFORMANCE")
    print("-" * 70)

    # Test modes.py import
    start = time.time()
    from claude_multi_terminal.modes import (
        AppMode, ModeConfig, ModeState, MODE_CONFIGS
    )
    modes_time = (time.time() - start) * 1000

    # Test app.py import
    start = time.time()
    from claude_multi_terminal.app import ClaudeMultiTerminalApp
    app_time = (time.time() - start) * 1000

    # Test status_bar.py import
    start = time.time()
    from claude_multi_terminal.widgets.status_bar import StatusBar
    statusbar_time = (time.time() - start) * 1000

    print(f"modes.py import:      {modes_time:>8.2f} ms")
    print(f"app.py import:        {app_time:>8.2f} ms")
    print(f"status_bar.py import: {statusbar_time:>8.2f} ms")
    print(f"Total import time:    {modes_time + app_time + statusbar_time:>8.2f} ms")

    return {
        "modes": modes_time,
        "app": app_time,
        "statusbar": statusbar_time,
        "total": modes_time + app_time + statusbar_time
    }


def measure_mode_transition_speed():
    """Measure speed of mode transitions."""
    print("\n2. MODE TRANSITION PERFORMANCE")
    print("-" * 70)

    from claude_multi_terminal.modes import ModeState, AppMode

    state = ModeState()

    # Single transition
    start = time.time()
    state.transition_to(AppMode.INSERT)
    single_time = (time.time() - start) * 1000000  # microseconds

    # Reset
    state.transition_to(AppMode.NORMAL)

    # 100 transitions
    transitions = [
        (AppMode.INSERT, AppMode.NORMAL),
        (AppMode.COPY, AppMode.NORMAL),
        (AppMode.COMMAND, AppMode.NORMAL),
    ]

    start = time.time()
    for _ in range(100):
        for target, back in transitions:
            state.transition_to(target)
            state.transition_to(back)
    batch_time = (time.time() - start) * 1000  # milliseconds

    avg_time = batch_time / (100 * len(transitions) * 2)

    print(f"Single transition:     {single_time:>8.2f} μs")
    print(f"100 cycles (600 ops):  {batch_time:>8.2f} ms")
    print(f"Average per operation: {avg_time:>8.2f} ms")
    print(f"Throughput:            {1000/avg_time:>8.0f} ops/sec")

    return {
        "single_us": single_time,
        "batch_ms": batch_time,
        "avg_ms": avg_time,
        "ops_per_sec": 1000/avg_time
    }


def measure_mode_state_memory():
    """Measure memory footprint of ModeState."""
    print("\n3. MEMORY FOOTPRINT")
    print("-" * 70)

    from claude_multi_terminal.modes import ModeState, AppMode
    import sys

    # Single ModeState
    state = ModeState()
    base_size = sys.getsizeof(state)

    # With history (100 transitions)
    for i in range(50):
        state.transition_to(AppMode.INSERT)
        state.transition_to(AppMode.NORMAL)

    with_history_size = sys.getsizeof(state)
    history_size = sys.getsizeof(state.history)

    print(f"Base ModeState:        {base_size:>8} bytes")
    print(f"With 100 transitions:  {with_history_size:>8} bytes")
    print(f"History list:          {history_size:>8} bytes")
    print(f"Per transition:        {history_size/100:>8.1f} bytes")

    return {
        "base_bytes": base_size,
        "with_history_bytes": with_history_size,
        "history_bytes": history_size,
        "per_transition_bytes": history_size/100
    }


def measure_config_lookup_speed():
    """Measure speed of config lookups."""
    print("\n4. CONFIGURATION LOOKUP PERFORMANCE")
    print("-" * 70)

    from claude_multi_terminal.modes import (
        AppMode, MODE_CONFIGS, get_mode_color, get_mode_icon
    )

    # Direct dictionary lookup
    start = time.time()
    for _ in range(10000):
        config = MODE_CONFIGS[AppMode.NORMAL]
    direct_time = (time.time() - start) * 1000

    # Utility function lookup
    start = time.time()
    for _ in range(10000):
        color = get_mode_color(AppMode.NORMAL)
        icon = get_mode_icon(AppMode.NORMAL)
    utility_time = (time.time() - start) * 1000

    print(f"10k direct lookups:    {direct_time:>8.2f} ms")
    print(f"10k utility lookups:   {utility_time:>8.2f} ms")
    print(f"Per lookup (direct):   {direct_time/10000*1000:>8.2f} μs")
    print(f"Per lookup (utility):  {utility_time/10000*1000:>8.2f} μs")

    return {
        "direct_ms": direct_time,
        "utility_ms": utility_time,
        "direct_us": direct_time/10000*1000,
        "utility_us": utility_time/10000*1000
    }


def measure_mode_validation_speed():
    """Measure speed of transition validation."""
    print("\n5. TRANSITION VALIDATION PERFORMANCE")
    print("-" * 70)

    from claude_multi_terminal.modes import ModeState, AppMode

    state = ModeState()

    # Validation checks
    start = time.time()
    for _ in range(10000):
        allowed, reason = state.can_transition_to(AppMode.INSERT)
    validation_time = (time.time() - start) * 1000

    print(f"10k validations:       {validation_time:>8.2f} ms")
    print(f"Per validation:        {validation_time/10000*1000:>8.2f} μs")

    return {
        "total_ms": validation_time,
        "per_validation_us": validation_time/10000*1000
    }


def run_performance_tests():
    """Run all performance tests and generate report."""
    print("\n" + "="*70)
    print("PHASE 1 MODAL SYSTEM - PERFORMANCE METRICS")
    print("="*70)

    start_time = datetime.now()

    results = {}
    results["import"] = measure_import_time()
    results["transition"] = measure_mode_transition_speed()
    results["memory"] = measure_mode_state_memory()
    results["lookup"] = measure_config_lookup_speed()
    results["validation"] = measure_mode_validation_speed()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Summary
    print("\n" + "="*70)
    print("PERFORMANCE SUMMARY")
    print("="*70)

    print(f"\nTest Duration: {duration:.2f}s")

    print("\nKey Metrics:")
    print(f"  Import overhead:     {results['import']['total']:.1f} ms (one-time)")
    print(f"  Transition speed:    {results['transition']['single_us']:.1f} μs per transition")
    print(f"  Throughput:          {results['transition']['ops_per_sec']:.0f} transitions/sec")
    print(f"  Memory per state:    {results['memory']['base_bytes']} bytes")
    print(f"  Config lookup:       {results['lookup']['direct_us']:.2f} μs")
    print(f"  Validation:          {results['validation']['per_validation_us']:.2f} μs")

    print("\nPerformance Ratings:")

    # Rate import time
    import_time = results['import']['total']
    if import_time < 50:
        import_rating = "EXCELLENT"
    elif import_time < 100:
        import_rating = "GOOD"
    elif import_time < 200:
        import_rating = "ACCEPTABLE"
    else:
        import_rating = "NEEDS IMPROVEMENT"
    print(f"  Import Time:         {import_rating} ({import_time:.1f} ms)")

    # Rate transition speed
    transition_us = results['transition']['single_us']
    if transition_us < 50:
        transition_rating = "EXCELLENT"
    elif transition_us < 100:
        transition_rating = "GOOD"
    elif transition_us < 500:
        transition_rating = "ACCEPTABLE"
    else:
        transition_rating = "NEEDS IMPROVEMENT"
    print(f"  Transition Speed:    {transition_rating} ({transition_us:.1f} μs)")

    # Rate throughput
    throughput = results['transition']['ops_per_sec']
    if throughput > 50000:
        throughput_rating = "EXCELLENT"
    elif throughput > 10000:
        throughput_rating = "GOOD"
    elif throughput > 1000:
        throughput_rating = "ACCEPTABLE"
    else:
        throughput_rating = "NEEDS IMPROVEMENT"
    print(f"  Throughput:          {throughput_rating} ({throughput:.0f} ops/sec)")

    # Rate memory footprint
    memory_bytes = results['memory']['base_bytes']
    if memory_bytes < 500:
        memory_rating = "EXCELLENT"
    elif memory_bytes < 1000:
        memory_rating = "GOOD"
    elif memory_bytes < 5000:
        memory_rating = "ACCEPTABLE"
    else:
        memory_rating = "NEEDS IMPROVEMENT"
    print(f"  Memory Footprint:    {memory_rating} ({memory_bytes} bytes)")

    print("\n" + "="*70)

    return results


if __name__ == "__main__":
    results = run_performance_tests()
