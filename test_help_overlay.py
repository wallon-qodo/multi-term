#!/usr/bin/env python3
"""Test script to verify help overlay and count entries."""

from claude_multi_terminal.help.help_overlay import HelpOverlay, HelpCategory, HelpEntry
from claude_multi_terminal.types import AppMode

# Create help overlay instance
overlay = HelpOverlay()

# Count total entries
total_entries = len(overlay.help_entries)
print(f'Total help entries: {total_entries}')

# Count by category
print('\nEntries by category:')
for category in HelpCategory:
    count = len([e for e in overlay.help_entries if e.category == category])
    print(f'  {category.value:15} : {count:2} entries')

# Count by mode
print('\nEntries by mode:')
for mode in AppMode:
    count = len([e for e in overlay.help_entries if e.mode == mode])
    print(f'  {mode.value:10} : {count:2} entries')

# Count mode-agnostic entries
mode_agnostic = len([e for e in overlay.help_entries if e.mode is None])
print(f'  {"(all modes)":10} : {mode_agnostic:2} entries')

print('\n✓ Help overlay module loaded successfully!')
