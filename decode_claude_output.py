#!/usr/bin/env python3
"""Decode Claude's initial output to see what it's showing."""

import ptyprocess
import os
import time
import select
import re

print("=" * 70)
print("DECODING CLAUDE'S INITIAL OUTPUT")
print("=" * 70)

env = os.environ.copy()
env['TERM'] = 'xterm-256color'

process = ptyprocess.PtyProcess.spawn(
    ['/opt/homebrew/bin/claude'],
    cwd=os.path.expanduser("~"),
    env=env,
    dimensions=(24, 80)
)

print(f"\n✓ Spawned Claude")

# Read ALL initial output
print("\n📥 Reading all initial output (5 seconds)...")
fd = process.fd
all_data = bytearray()

start = time.time()
while time.time() - start < 5:
    ready, _, _ = select.select([fd], [], [], 0.1)
    if ready:
        try:
            data = os.read(fd, 4096)
            all_data.extend(data)
        except:
            break

output = all_data.decode('utf-8', errors='replace')
print(f"✓ Read {len(all_data)} bytes total")

# Strip ANSI codes to see plain text
ansi_escape = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]|\x1b\([0-9;?]*[a-zA-Z]')
plain_text = ansi_escape.sub('', output)

print("\n" + "=" * 70)
print("RAW OUTPUT (with ANSI codes):")
print("=" * 70)
print(repr(output))

print("\n" + "=" * 70)
print("PLAIN TEXT (ANSI stripped):")
print("=" * 70)
print(plain_text)

print("\n" + "=" * 70)
print("RENDERED (approximately):")
print("=" * 70)
# Show what it looks like
print(output)

# Check for key phrases
print("\n" + "=" * 70)
print("ANALYSIS:")
print("=" * 70)

if "press" in plain_text.lower() or "enter" in plain_text.lower():
    print("⚠️  Output contains 'press' or 'enter' - might be waiting for keypress!")

if "?" in plain_text:
    print("⚠️  Output contains '?' - might be asking a question!")

if "y/n" in plain_text.lower():
    print("⚠️  Output contains 'y/n' - waiting for yes/no response!")

# Check what ANSI codes are present
bracketed_paste = '\x1b[?2004h' in output
print(f"Bracketed paste mode: {'YES' if bracketed_paste else 'NO'}")

cursor_hidden = '\x1b[?25l' in output
print(f"Cursor hidden: {'YES' if cursor_hidden else 'NO'}")

# Cleanup
process.terminate(force=True)
