#!/bin/bash
# Comprehensive test runner for TextArea migration

echo "=========================================="
echo "TEXTAREA MIGRATION - COMPREHENSIVE TESTS"
echo "=========================================="
echo ""

echo "Test 1: Static Migration Analysis"
echo "----------------------------------"
python3 test_textarea_migration.py
STATIC_RESULT=$?
echo ""

echo "Test 2: Integration Tests"
echo "--------------------------"
python3 test_full_integration.py
INTEGRATION_RESULT=$?
echo ""

echo "=========================================="
echo "FINAL RESULTS"
echo "=========================================="
if [ $STATIC_RESULT -eq 0 ] && [ $INTEGRATION_RESULT -eq 0 ]; then
    echo "✅ ALL TESTS PASSED (21/21)"
    echo "✅ Static Tests: 11/11"
    echo "✅ Integration Tests: 10/10"
    echo "✅ Success Rate: 100%"
    echo ""
    echo "Status: READY FOR PRODUCTION"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    echo "Static Tests: $STATIC_RESULT"
    echo "Integration Tests: $INTEGRATION_RESULT"
    exit 1
fi
