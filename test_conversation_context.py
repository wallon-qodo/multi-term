#!/usr/bin/env python3
"""Test script to verify conversation context is maintained across commands."""

import asyncio
import time
import sys
import os

# Add the package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_multi_terminal.core.session_manager import SessionManager
from claude_multi_terminal.core.pty_handler import PTYHandler


class ConversationContextTester:
    """Test harness for verifying conversation context persistence."""

    def __init__(self):
        self.session_manager = SessionManager(claude_path="/opt/homebrew/bin/claude")
        self.output_buffer = []
        self.current_session_id = None

    def output_callback(self, output: str):
        """Callback to collect output."""
        self.output_buffer.append(output)
        print(f"[OUTPUT] {output[:100]}...", flush=True)

        # Check if this is the command complete signal
        if "\x00COMMAND_COMPLETE\x00" in output:
            self.command_complete = True

    async def test_conversation_context(self):
        """
        Test that conversation context is maintained across multiple commands.

        Test flow:
        1. Create a session
        2. Ask Claude to remember a number
        3. In a separate command, ask Claude what the number was
        4. Verify Claude remembers it (proving context was maintained)
        """
        print("\n" + "="*80)
        print("CONVERSATION CONTEXT TEST")
        print("="*80 + "\n")

        # Step 1: Create a session
        print("[TEST] Creating session...")
        self.current_session_id = self.session_manager.create_session(
            name="Context Test Session"
            # Let it use the default unique working directory
        )

        session = self.session_manager.sessions[self.current_session_id]
        print(f"[TEST] Session created with ID: {self.current_session_id}")

        # Verify continue flag is in command
        command_line = " ".join(session.pty_handler.command)
        print(f"[TEST] Command line: {command_line}")

        if "--continue" in command_line or "-c" in command_line:
            print("[PASS] --continue flag is present in command")
        else:
            print("[FAIL] --continue flag is MISSING from command")
            return False

        # Verify working directory is unique for this session
        print(f"[TEST] Working directory: {session.working_directory}")
        if self.current_session_id in session.working_directory:
            print("[PASS] Working directory is unique for this session")
        else:
            print("[WARN] Working directory may not be unique")

        # Start reading output
        await session.pty_handler.start_reading(callback=self.output_callback)
        print("[TEST] Started reading PTY output")

        # Wait for initial output to settle
        await asyncio.sleep(2)

        # Step 2: First command - ask Claude to remember something
        print("\n[TEST] Sending first command: Ask Claude to remember a number")
        self.output_buffer = []  # Clear buffer
        self.command_complete = False  # Reset flag

        first_command = "Please remember this number: 42. Just respond with 'OK, I'll remember 42'"
        await session.pty_handler.write(first_command + "\n")
        print(f"[TEST] Sent: {first_command}")

        # Wait for command to complete (poll for COMMAND_COMPLETE signal)
        print("[TEST] Waiting for response to first command...")
        max_wait = 30  # Maximum 30 seconds
        waited = 0
        while not self.command_complete and waited < max_wait:
            await asyncio.sleep(0.5)
            waited += 0.5

        if not self.command_complete:
            print(f"[WARN] Command did not complete after {max_wait}s")
        else:
            print(f"[TEST] Command completed after {waited}s")

        first_response = "".join(self.output_buffer)
        print(f"\n[RESPONSE 1] Length: {len(first_response)} chars")
        print(f"[RESPONSE 1] Content preview: {first_response[:200]}...")

        # Check if we got a response
        if len(first_response) < 10:
            print("[FAIL] No substantial response received from first command")
            return False

        # Step 3: Second command - ask Claude what the number was
        print("\n[TEST] Sending second command: Ask Claude to recall the number")
        self.output_buffer = []  # Clear buffer
        self.command_complete = False  # Reset flag

        second_command = "What number did I ask you to remember?"
        await session.pty_handler.write(second_command + "\n")
        print(f"[TEST] Sent: {second_command}")

        # Wait for command to complete (poll for COMMAND_COMPLETE signal)
        print("[TEST] Waiting for response to second command...")
        max_wait = 30  # Maximum 30 seconds
        waited = 0
        while not self.command_complete and waited < max_wait:
            await asyncio.sleep(0.5)
            waited += 0.5

        if not self.command_complete:
            print(f"[WARN] Command did not complete after {max_wait}s")
        else:
            print(f"[TEST] Command completed after {waited}s")

        second_response = "".join(self.output_buffer)
        print(f"\n[RESPONSE 2] Length: {len(second_response)} chars")
        print(f"[RESPONSE 2] Content preview: {second_response[:500]}...")

        # Step 4: Verify Claude remembers (mentions "42")
        print("\n[TEST] Checking if Claude remembers the number...")

        if "42" in second_response:
            print("[PASS] Claude remembered the number 42!")
            print("[PASS] Conversation context is working correctly!")
            success = True
        else:
            print("[FAIL] Claude did NOT remember the number")
            print("[FAIL] Conversation context is NOT working")
            print(f"[DEBUG] Full second response:\n{second_response}")
            success = False

        # Cleanup
        print("\n[TEST] Cleaning up session...")
        await self.session_manager.terminate_session(self.current_session_id)

        # Check session file was created
        home = os.path.expanduser("~")
        session_file = os.path.join(
            home,
            ".claude",
            "projects",
            f"-{home.replace('/', '-')}",
            f"{self.current_session_id}.jsonl"
        )

        if os.path.exists(session_file):
            print(f"[PASS] Session file created: {session_file}")
            file_size = os.path.getsize(session_file)
            print(f"[INFO] Session file size: {file_size} bytes")
        else:
            print(f"[WARN] Session file not found: {session_file}")

        return success

    async def test_continue_flag_propagation(self):
        """
        Verify that --continue flag is correctly passed to Claude CLI.
        """
        print("\n" + "="*80)
        print("CONTINUE FLAG PROPAGATION TEST")
        print("="*80 + "\n")

        # Create a session
        print("[TEST] Creating session...")
        session_id = self.session_manager.create_session(
            name="Propagation Test"
        )

        session = self.session_manager.sessions[session_id]
        command = session.pty_handler.command

        print(f"[TEST] Session ID: {session_id}")
        print(f"[TEST] Command: {command}")
        print(f"[TEST] Working dir: {session.working_directory}")

        # Verify --continue is in command
        if "--continue" in command or "-c" in command:
            print("[PASS] --continue flag is present!")
            result = True
        else:
            print("[FAIL] --continue flag not found in command")
            result = False

        # Verify working directory is unique
        if session_id in session.working_directory:
            print("[PASS] Working directory is unique to this session!")
        else:
            print("[WARN] Working directory may not be unique")

        # Cleanup
        await self.session_manager.terminate_session(session_id)

        return result


async def main():
    """Run all tests."""
    tester = ConversationContextTester()

    print("\n" + "#"*80)
    print("# CONVERSATION CONTEXT TEST SUITE")
    print("#"*80 + "\n")

    # Test 1: Continue flag propagation
    test1_pass = await tester.test_continue_flag_propagation()

    # Test 2: Actual conversation context
    test2_pass = await tester.test_conversation_context()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Test 1 (Continue Flag Propagation): {'PASS' if test1_pass else 'FAIL'}")
    print(f"Test 2 (Conversation Context):       {'PASS' if test2_pass else 'FAIL'}")
    print("="*80 + "\n")

    if test1_pass and test2_pass:
        print("ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
