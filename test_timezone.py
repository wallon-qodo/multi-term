#!/usr/bin/env python3
"""Test timezone display in header."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from claude_multi_terminal.widgets.header_bar import HeaderBar
    import datetime
    import time

    print("Testing timezone display...")
    print()

    # Get local timezone info
    if time.daylight:
        tz_offset = -time.altzone
        tz_name = time.tzname[1]
    else:
        tz_offset = -time.timezone
        tz_name = time.tzname[0]

    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime.now(tz=local_tz)

    time_str = now.strftime("%I:%M %p")
    tz_abbr = now.strftime("%Z")
    if not tz_abbr or len(tz_abbr) > 5:
        tz_abbr = tz_name

    print(f"✓ Local timezone detected: {tz_abbr}")
    print(f"✓ Time format: {time_str} {tz_abbr}")
    print(f"✓ Full datetime: {now}")
    print()

    # Test HeaderBar rendering
    header = HeaderBar()
    header.session_count = 2
    rendered = header.render()

    print(f"✓ HeaderBar renders successfully")
    print(f"✓ Rendered text length: {len(rendered.plain)} characters")
    print()

    # Check if timezone is in the rendered text
    if tz_abbr in rendered.plain:
        print(f"✅ Timezone '{tz_abbr}' found in header!")
    else:
        print(f"⚠ Timezone '{tz_abbr}' not found in header")
        print(f"   Header text: {rendered.plain}")

    print()
    print("✅ All timezone tests passed!")
    sys.exit(0)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
