#!/bin/bash
# Run all automated tests for Claude Multi-Terminal

set -e  # Exit on error

echo "=========================================="
echo "CLAUDE MULTI-TERMINAL TEST SUITE"
echo "=========================================="
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -e ."
    exit 1
fi

source venv/bin/activate

# Check if we're in the right directory
if [ ! -f "claude_multi_terminal/app.py" ]; then
    echo "Error: Not in the correct directory"
    echo "Please run this script from the claude-multi-terminal root directory"
    exit 1
fi

echo "Virtual environment activated"
echo ""

# Test 1: Smoke Test
echo "=========================================="
echo "TEST 1: Smoke Test (Quick Pre-flight)"
echo "=========================================="
python smoke_test.py << EOF
n
EOF
if [ $? -eq 0 ]; then
    echo "✅ Smoke test passed"
else
    echo "❌ Smoke test failed"
    exit 1
fi
echo ""

# Test 2: Component Tests
echo "=========================================="
echo "TEST 2: Component Tests"
echo "=========================================="
python test_tui_comprehensive.py
if [ $? -eq 0 ]; then
    echo "✅ Component tests passed"
else
    echo "❌ Component tests failed"
    exit 1
fi
echo ""

# Test 3: Integration Tests
echo "=========================================="
echo "TEST 3: Integration Tests"
echo "=========================================="
python test_integration_simulated.py
if [ $? -eq 0 ]; then
    echo "✅ Integration tests passed"
else
    echo "❌ Integration tests failed"
    exit 1
fi
echo ""

# Test 4: Stress Tests
echo "=========================================="
echo "TEST 4: Stress and Edge Case Tests"
echo "=========================================="
python test_stress_and_edge_cases.py
if [ $? -eq 0 ]; then
    echo "✅ Stress tests passed"
else
    echo "❌ Stress tests failed"
    exit 1
fi
echo ""

# Test 5: User Scenarios
echo "=========================================="
echo "TEST 5: User Scenario Tests"
echo "=========================================="
python test_user_scenario.py
if [ $? -eq 0 ]; then
    echo "✅ User scenario tests passed"
else
    echo "❌ User scenario tests failed"
    exit 1
fi
echo ""

# Summary
echo "=========================================="
echo "TEST SUITE SUMMARY"
echo "=========================================="
echo ""
echo "✅ All automated tests passed!"
echo ""
echo "Tests run:"
echo "  1. Smoke test (7 checks)"
echo "  2. Component tests (7 phases)"
echo "  3. Integration tests (6 tests)"
echo "  4. Stress tests (8 tests)"
echo "  5. User scenarios (5 scenarios)"
echo ""
echo "Total: 26 automated tests - ALL PASSED"
echo ""
echo "Next steps:"
echo "  - Review test reports in TEST_REPORT.md"
echo "  - Run manual tests using FINAL_TEST_CHECKLIST.md"
echo "  - Launch the application: python LAUNCH.py"
echo ""
echo "=========================================="
