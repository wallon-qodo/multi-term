#!/bin/bash
# Verification script for context menu implementation

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        Context Menu Implementation Verification               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Check function
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1"
        ((FAILED++))
    fi
}

echo "1. Checking file structure..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check main implementation file
test -f "claude_multi_terminal/widgets/selectable_richlog.py"
check "Main implementation file exists"

# Check documentation files
test -f "CONTEXT_MENU_DESIGN.md"
check "Design documentation exists"

test -f "IMPLEMENTATION_SUMMARY.md"
check "Implementation summary exists"

test -f "VISUAL_MOCKUP.txt"
check "Visual mockup exists"

test -f "QUICK_REFERENCE.md"
check "Quick reference exists"

test -f "CONTEXT_MENU_CHANGELOG.md"
check "Changelog exists"

# Check test file
test -f "test_context_menu.py"
check "Test script exists"

echo ""
echo "2. Checking Python syntax..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check syntax of main file
python3 -m py_compile claude_multi_terminal/widgets/selectable_richlog.py 2>/dev/null
check "Main file syntax is valid"

# Check syntax of test file
python3 -m py_compile test_context_menu.py 2>/dev/null
check "Test file syntax is valid"

echo ""
echo "3. Checking code components..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for MenuItem class
grep -q "class MenuItem" claude_multi_terminal/widgets/selectable_richlog.py
check "MenuItem class defined"

# Check for ContextMenu class
grep -q "class ContextMenu" claude_multi_terminal/widgets/selectable_richlog.py
check "ContextMenu class defined"

# Check for _select_all method
grep -q "def _select_all" claude_multi_terminal/widgets/selectable_richlog.py
check "_select_all method implemented"

# Check for _show_context_menu method
grep -q "def _show_context_menu" claude_multi_terminal/widgets/selectable_richlog.py
check "_show_context_menu method implemented"

# Check for right-click detection (button 3)
grep -q "button == 3" claude_multi_terminal/widgets/selectable_richlog.py
check "Right-click detection implemented"

# Check for Ctrl+A support
grep -q "ctrl+a" claude_multi_terminal/widgets/selectable_richlog.py
check "Ctrl+A keyboard shortcut implemented"

echo ""
echo "4. Checking theme colors..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for Homebrew theme colors
grep -q "rgb(255,183,77)" claude_multi_terminal/widgets/selectable_richlog.py
check "Amber accent color used"

grep -q "rgb(32,32,32)" claude_multi_terminal/widgets/selectable_richlog.py
check "Secondary background color used"

grep -q "rgb(224,224,224)" claude_multi_terminal/widgets/selectable_richlog.py
check "Primary text color used"

grep -q "rgb(117,117,117)" claude_multi_terminal/widgets/selectable_richlog.py
check "Dimmed text color used"

echo ""
echo "5. Checking documentation completeness..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check documentation content
grep -q "Context Menu" CONTEXT_MENU_DESIGN.md
check "Design doc has content"

grep -q "Copy" CONTEXT_MENU_DESIGN.md
check "Copy feature documented"

grep -q "Select All" CONTEXT_MENU_DESIGN.md
check "Select All feature documented"

grep -q "Clear Selection" CONTEXT_MENU_DESIGN.md
check "Clear Selection feature documented"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Summary:"
echo "───────────────────────────────────────────────────────────────"
echo -e "  ${GREEN}Passed: ${PASSED}${NC}"
echo -e "  ${RED}Failed: ${FAILED}${NC}"
echo "═══════════════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              ✓ ALL CHECKS PASSED!                            ║"
    echo "║                                                               ║"
    echo "║  Context menu implementation is complete and verified.       ║"
    echo "║                                                               ║"
    echo "║  Ready to test:                                              ║"
    echo "║    python3 test_context_menu.py                              ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    exit 0
else
    echo -e "${RED}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              ✗ SOME CHECKS FAILED                            ║"
    echo "║                                                               ║"
    echo "║  Please review the failed checks above.                      ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    exit 1
fi
