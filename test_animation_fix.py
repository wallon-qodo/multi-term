#!/usr/bin/env python3
"""Test script to verify the processing indicator animation fix."""

import asyncio
import sys
from textual.widgets import Static, RichLog
from claude_multi_terminal.app import ClaudeMultiTerminalApp


async def test_animation():
    """Test the processing indicator animation."""
    print("\n" + "="*70)
    print("TESTING PROCESSING INDICATOR ANIMATION FIX")
    print("="*70)

    app = ClaudeMultiTerminalApp()

    async with app.run_test() as pilot:
        print("\n1. App started successfully")

        # Wait for app to mount
        await asyncio.sleep(1)

        # Get the session pane
        session_grid = app.query_one("#session-grid")
        if not session_grid.panes:
            print("   ERROR: No panes found!")
            return False

        pane = session_grid.panes[0]
        session_id = pane.session_id
        print(f"2. Found session pane: {session_id[:8]}")

        # Get widgets
        output_widget = pane.query_one(f"#output-{session_id}", RichLog)
        processing_widget = pane.query_one(f"#processing-{session_id}", Static)

        print(f"3. Found output widget with {len(output_widget.lines)} lines")
        print(f"4. Found processing indicator widget")

        # Check initial state
        if processing_widget.display:
            print("   ERROR: Processing indicator should be hidden initially!")
            return False
        print("5. Processing indicator correctly hidden initially")

        # Get initial line count
        initial_line_count = len(output_widget.lines)
        print(f"6. Initial output lines: {initial_line_count}")

        # Focus the input and type command
        input_widget = pane.query_one(f"#input-{session_id}")
        input_widget.focus()
        await pilot.pause(0.1)

        # Type the command
        await pilot.press(*"what is 2+2?")
        await pilot.pause(0.2)

        # Submit the command
        await pilot.press("enter")
        await asyncio.sleep(0.5)

        # Check processing indicator state
        print(f"   Processing widget display: {processing_widget.display}")
        print(f"   Processing widget classes: {processing_widget.classes}")
        print(f"   Has indicator flag: {getattr(pane, '_has_processing_indicator', None)}")

        # Check processing indicator is visible
        if not processing_widget.display:
            print("   ERROR: Processing indicator should be visible after command!")
            print(f"   Output lines after command: {len(output_widget.lines)}")
            recent = "\n".join([str(line)[:80] for line in output_widget.lines[-5:]])
            print(f"   Recent output:\n{recent}")
            return False
        print("7. Processing indicator correctly visible after command")

        # Capture animation frames to verify it's updating in place
        frame_contents = []
        for i in range(10):
            await asyncio.sleep(0.35)  # Slightly longer than animation interval
            # Get the current content through the render method
            try:
                frame_text = str(processing_widget._renderable) if hasattr(processing_widget, '_renderable') else str(processing_widget.render())
            except:
                # Fallback to trying to get the text content
                frame_text = str(processing_widget)
            frame_contents.append(frame_text)
            print(f"   Frame {i+1}: {frame_text[:50]}")

        # Verify frames are changing (animation is working)
        unique_frames = set(frame_contents)
        if len(unique_frames) < 3:
            print(f"   ERROR: Animation not working! Only {len(unique_frames)} unique frames")
            return False
        print(f"8. Animation working: {len(unique_frames)} unique frames captured")

        # Verify output widget didn't accumulate animation lines
        final_line_count = len(output_widget.lines)
        animation_line_growth = final_line_count - initial_line_count

        # Check what was added to the output
        new_lines = [str(line) for line in output_widget.lines[initial_line_count:]]
        print(f"   Lines added to output: {animation_line_growth}")
        print(f"   Checking for 'Brewing' in new lines:")

        brewing_lines = [line for line in new_lines if 'Brewing' in line or 'Thinking' in line or any(emoji in line for emoji in ['🥘', '🍳', '🍲', '🥄', '🔥'])]

        if brewing_lines:
            print(f"   ERROR: Found {len(brewing_lines)} animation lines in RichLog!")
            for i, line in enumerate(brewing_lines[:5]):
                print(f"      Line {i+1}: {line[:80]}")
            return False

        # Should have separator (~6-8 lines) and maybe Claude response
        if animation_line_growth > 20:
            print(f"   WARNING: Unexpectedly many lines ({animation_line_growth})")
            print("   Showing first and last few:")
            for line in new_lines[:3]:
                print(f"      {line[:80]}")
            print("      ...")
            for line in new_lines[-3:]:
                print(f"      {line[:80]}")

        print(f"9. Output widget clean: no animation frames leaked to RichLog")

        # Check for animation keywords in output lines
        recent_output = "\n".join([str(line) for line in output_widget.lines[-10:]])
        brewing_count = recent_output.count("Brewing")

        if brewing_count > 1:
            print(f"   WARNING: Found {brewing_count} 'Brewing' instances in output")
            print("   This might indicate some animation frames leaked to RichLog")
        else:
            print(f"10. No animation leak detected in RichLog")

        print("\n" + "="*70)
        print("TEST PASSED: Animation updates in place correctly!")
        print("="*70 + "\n")
        return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_animation())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\nERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
