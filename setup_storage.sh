#!/bin/bash

# Setup script for multi-claude-sessions storage
# This script initializes the storage structure and optionally migrates existing data

set -e

STORAGE_DIR="$HOME/Desktop/multi-claude-sessions"
OLD_STORAGE_DIR="$HOME/.claude_multi_terminal"

echo "═══════════════════════════════════════════════════════"
echo "  Claude Multi-Terminal Storage Setup"
echo "═══════════════════════════════════════════════════════"
echo ""

# Create directory structure
echo "Creating storage structure at: $STORAGE_DIR"
mkdir -p "$STORAGE_DIR/sessions"
mkdir -p "$STORAGE_DIR/history"
mkdir -p "$STORAGE_DIR/projects"
echo "✓ Directory structure created"
echo ""

# Check if old storage exists
if [ -d "$OLD_STORAGE_DIR" ]; then
    echo "Found existing data in: $OLD_STORAGE_DIR"
    echo ""
    echo "Would you like to migrate this data? (y/n)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Migrating data..."

        # Migrate sessions
        if [ -d "$OLD_STORAGE_DIR/sessions" ]; then
            echo "  • Copying session directories..."
            cp -r "$OLD_STORAGE_DIR/sessions/"* "$STORAGE_DIR/sessions/" 2>/dev/null || true
        fi

        # Migrate history
        if [ -d "$OLD_STORAGE_DIR/history" ]; then
            echo "  • Copying session history..."
            cp -r "$OLD_STORAGE_DIR/history/"* "$STORAGE_DIR/history/" 2>/dev/null || true
        fi

        # Migrate workspace state
        if [ -f "$OLD_STORAGE_DIR/workspace_state.json" ]; then
            echo "  • Copying workspace state..."
            cp "$OLD_STORAGE_DIR/workspace_state.json" "$STORAGE_DIR/"
        fi

        echo "✓ Migration complete"
        echo ""
        echo "Old data remains in $OLD_STORAGE_DIR (you can delete it manually if desired)"
    else
        echo "Skipping migration"
    fi
else
    echo "No existing data found in $OLD_STORAGE_DIR"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Setup Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Storage location: $STORAGE_DIR"
echo ""
echo "Directory structure:"
echo "  • sessions/   - Individual session working directories"
echo "  • history/    - Session history backups"
echo "  • projects/   - Recommended location for long-term projects"
echo ""
echo "Next steps:"
echo "  1. Review STORAGE_CONFIGURATION.md for detailed usage"
echo "  2. Run the application normally"
echo "  3. All new work will be stored in the Desktop location"
echo ""
echo "Tips:"
echo "  • Create projects in: $STORAGE_DIR/projects/"
echo "  • Use git for version control"
echo "  • Backup this folder regularly"
echo ""
