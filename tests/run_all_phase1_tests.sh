#!/bin/bash
# Run all Phase 1 Modal System tests
# Usage: ./tests/run_all_phase1_tests.sh

set -e

echo "========================================================================"
echo "PHASE 1 MODAL SYSTEM - RUNNING ALL TESTS"
echo "========================================================================"
echo ""

# Activate venv
source venv/bin/activate

# Test 1: Comprehensive Modal System Tests
echo "Running Test Suite 1: Modal System Comprehensive Tests..."
python tests/test_phase1_modal_system.py
echo ""

# Test 2: COPY Feature Tests
echo "Running Test Suite 2: COPY Feature Tests..."
python test_copy_all_feature.py
echo ""

# Test 3: Performance Metrics
echo "Running Test Suite 3: Performance Metrics..."
python tests/test_phase1_performance.py
echo ""

# Final verification
echo "========================================================================"
echo "FINAL VERIFICATION"
echo "========================================================================"
python -c "
from claude_multi_terminal.modes import AppMode, ModeState
state = ModeState()
print(f'✓ ModeState initialized: {state.current_mode.name}')
state.transition_to(AppMode.INSERT)
state.transition_to(AppMode.NORMAL)
state.transition_to(AppMode.COPY)
state.transition_to(AppMode.NORMAL)
print(f'✓ Transitions verified: {len(state.history)} history entries')
print('')
print('=== ALL PHASE 1 TESTS COMPLETED SUCCESSFULLY ✓ ===')
"
echo ""
echo "========================================================================"
echo "Test Reports Available:"
echo "  - tests/PHASE1_TEST_REPORT.md (Detailed markdown report)"
echo "  - tests/PHASE1_SUMMARY.txt (Executive summary)"
echo "========================================================================"
