#!/usr/bin/env python3
"""
Comprehensive Phase 0 Infrastructure Test Suite
Tests all core components before moving to Phase 1
"""

import sys
import os
import unittest
import tempfile
import shutil
import time
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_multi_terminal.config import Config
from claude_multi_terminal.core.session_manager import SessionManager
from claude_multi_terminal.core.clipboard import ClipboardManager
from claude_multi_terminal.core.export import TranscriptExporter
from claude_multi_terminal.persistence.session_state import SessionState, WorkspaceState
from claude_multi_terminal.persistence.storage import SessionStorage


class TestSuite1_Imports(unittest.TestCase):
    """Test Suite 1: Verify all imports work correctly"""

    def test_001_config_import(self):
        """Test Config class import"""
        self.assertIsNotNone(Config)

    def test_002_session_manager_import(self):
        """Test SessionManager import"""
        self.assertIsNotNone(SessionManager)

    def test_003_clipboard_manager_import(self):
        """Test ClipboardManager import"""
        self.assertIsNotNone(ClipboardManager)

    def test_004_transcript_exporter_import(self):
        """Test TranscriptExporter import"""
        self.assertIsNotNone(TranscriptExporter)

    def test_005_session_state_import(self):
        """Test SessionState import"""
        self.assertIsNotNone(SessionState)

    def test_006_workspace_state_import(self):
        """Test WorkspaceState import"""
        self.assertIsNotNone(WorkspaceState)

    def test_007_session_storage_import(self):
        """Test SessionStorage import"""
        self.assertIsNotNone(SessionStorage)

    def test_008_class_instantiation(self):
        """Test all classes can be instantiated"""
        try:
            config = Config()
            session_manager = SessionManager()
            clipboard_manager = ClipboardManager()
            transcript_exporter = TranscriptExporter()
            # Storage needs Path object
            temp_dir = Path(tempfile.mkdtemp())
            storage = SessionStorage(storage_dir=temp_dir)
            shutil.rmtree(temp_dir, ignore_errors=True)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to instantiate classes: {e}")


class TestSuite2_Config(unittest.TestCase):
    """Test Suite 2: Config Tests"""

    def setUp(self):
        self.config = Config()

    def test_001_detect_claude_path(self):
        """Test Claude CLI path detection"""
        result = Config.detect_claude_path()
        self.assertIsNotNone(result, "Claude path should be detected")
        self.assertTrue(os.path.exists(result), f"Claude path {result} should exist")

    def test_002_storage_dir_property(self):
        """Test storage directory property"""
        storage_dir = self.config.STORAGE_DIR
        self.assertIsNotNone(storage_dir)
        self.assertIsInstance(storage_dir, Path)

    def test_003_validate_config(self):
        """Test config validation"""
        try:
            self.config.validate()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Config validation failed: {e}")

    def test_004_constants_accessible(self):
        """Test all config constants are accessible"""
        self.assertIsNotNone(self.config.CLAUDE_PATH)
        self.assertIsNotNone(self.config.MAX_SESSIONS)
        self.assertIsNotNone(self.config.STORAGE_DIR)
        # MAX_SESSIONS defaults to 9
        self.assertEqual(self.config.MAX_SESSIONS, 9)


class TestSuite3_CoreModules(unittest.TestCase):
    """Test Suite 3: Core Module Tests"""

    def setUp(self):
        self.session_manager = SessionManager()
        self.clipboard_manager = ClipboardManager()
        self.transcript_exporter = TranscriptExporter()
        self.temp_dir = tempfile.mkdtemp()
        self.sessions_created = []

    def tearDown(self):
        # Clean up any sessions using async termination
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for session_id in self.sessions_created:
            try:
                loop.run_until_complete(self.session_manager.terminate_session(session_id))
            except:
                pass
        loop.close()
        # Clean up temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_001_create_session(self):
        """Test session creation"""
        session_id = self.session_manager.create_session(
            name="Test Session",
            working_dir="/tmp/test"
        )
        self.sessions_created.append(session_id)
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.session_manager.sessions)

    def test_002_list_sessions(self):
        """Test listing sessions"""
        session_id = self.session_manager.create_session(
            name="List Test",
            working_dir="/tmp/test"
        )
        self.sessions_created.append(session_id)
        sessions = self.session_manager.list_sessions()
        self.assertIsInstance(sessions, list)
        self.assertTrue(len(sessions) > 0)
        # Sessions returns SessionInfo objects
        session_info = sessions[0]
        self.assertEqual(session_info.session_id, session_id)
        self.assertEqual(session_info.name, "List Test")

    def test_003_terminate_session(self):
        """Test session termination"""
        session_id = self.session_manager.create_session(
            name="Terminate Test",
            working_dir="/tmp/test"
        )

        # Verify session exists before termination
        self.assertIn(session_id, self.session_manager.sessions)

        # Terminate session asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.session_manager.terminate_session(session_id))
        loop.close()

        # Verify session was removed
        self.assertNotIn(session_id, self.session_manager.sessions)

    def test_004_clipboard_copy_basic(self):
        """Test basic clipboard copy functionality"""
        test_text = "Test clipboard content"
        try:
            result = self.clipboard_manager.copy_to_system(test_text)
            # Result may vary by platform, just check it doesn't crash
            self.assertIsNotNone(result)
        except Exception as e:
            # Clipboard operations may fail in headless environments
            self.skipTest(f"Clipboard operation not supported: {e}")

    def test_005_transcript_export_text(self):
        """Test transcript export to text file"""
        test_lines = [
            "Hello",
            "Hi there!"
        ]
        output_path = Path(self.temp_dir) / "test_transcript.txt"

        result = self.transcript_exporter.export_to_text(
            output_lines=test_lines,
            filepath=output_path
        )

        self.assertTrue(result)
        self.assertTrue(output_path.exists())

        # Verify content
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn("Hello", content)
            self.assertIn("Hi there!", content)


class TestSuite4_Persistence(unittest.TestCase):
    """Test Suite 4: Persistence Tests"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.storage = SessionStorage(storage_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_001_session_state_creation(self):
        """Test SessionState dataclass creation"""
        now = time.time()
        state = SessionState(
            session_id="test-123",
            name="Test Session",
            working_directory="/tmp/test",
            created_at=now,
            modified_at=now,
            command_count=5,
            is_active=True
        )
        self.assertEqual(state.session_id, "test-123")
        self.assertEqual(state.name, "Test Session")
        self.assertEqual(state.working_directory, "/tmp/test")
        self.assertTrue(state.is_active)
        self.assertEqual(state.command_count, 5)

    def test_002_workspace_state_creation(self):
        """Test WorkspaceState dataclass creation"""
        now = time.time()
        session = SessionState(
            session_id="test-123",
            name="Test Session",
            working_directory="/tmp/test",
            created_at=now,
            modified_at=now
        )
        state = WorkspaceState(
            active_session_id="test-123",
            sessions=[session]
        )
        self.assertEqual(state.active_session_id, "test-123")
        self.assertEqual(len(state.sessions), 1)
        self.assertEqual(state.sessions[0].session_id, "test-123")

    def test_003_save_and_load_state(self):
        """Test SessionStorage saves and loads state correctly"""
        now = time.time()
        # Create test state
        session_state = SessionState(
            session_id="test-save-123",
            name="Save Test",
            working_directory="/tmp/test",
            created_at=now,
            modified_at=now,
            is_active=True
        )

        workspace_state = WorkspaceState(
            active_session_id="test-save-123",
            sessions=[session_state]
        )

        # Save state
        result = self.storage.save_state(workspace_state)
        self.assertTrue(result)

        # Load state
        loaded_workspace = self.storage.load_state()

        self.assertIsNotNone(loaded_workspace)
        self.assertEqual(loaded_workspace.active_session_id, "test-save-123")
        self.assertTrue(len(loaded_workspace.sessions) > 0)
        self.assertEqual(loaded_workspace.sessions[0].name, "Save Test")

    def test_004_save_session_history(self):
        """Test save_session_to_history creates history files"""
        now = time.time()
        session_state = SessionState(
            session_id="test-history-123",
            name="History Test",
            working_directory="/tmp/test",
            created_at=now,
            modified_at=now,
            is_active=False
        )

        result = self.storage.save_session_to_history(session_state)
        self.assertTrue(result)

        # Check history file exists
        history_dir = self.temp_dir / "history"
        self.assertTrue(history_dir.exists())
        history_files = list(history_dir.glob("*.json"))
        self.assertTrue(len(history_files) > 0)

    def test_005_load_session_history(self):
        """Test load_session_history retrieves sessions"""
        now = time.time()
        # Save a session first
        session_state = SessionState(
            session_id="test-load-123",
            name="Load Test",
            working_directory="/tmp/test",
            created_at=now,
            modified_at=now,
            is_active=False
        )
        self.storage.save_session_to_history(session_state)

        # Load history
        history = self.storage.load_session_history()

        self.assertIsInstance(history, list)
        self.assertTrue(len(history) > 0)
        self.assertEqual(history[0].session_id, "test-load-123")
        self.assertEqual(history[0].name, "Load Test")


class TestSuite5_AppLaunch(unittest.TestCase):
    """Test Suite 5: App Launch Test"""

    def test_001_import_app(self):
        """Test importing ClaudeMultiTerminalApp from app.py"""
        try:
            from claude_multi_terminal.app import ClaudeMultiTerminalApp
            self.assertIsNotNone(ClaudeMultiTerminalApp)
        except ImportError as e:
            self.fail(f"Failed to import ClaudeMultiTerminalApp: {e}")

    def test_002_app_dependencies_resolved(self):
        """Test all app dependencies are resolved"""
        try:
            from claude_multi_terminal.app import ClaudeMultiTerminalApp
            # Check if key methods exist
            self.assertTrue(hasattr(ClaudeMultiTerminalApp, 'compose'))
            self.assertTrue(hasattr(ClaudeMultiTerminalApp, 'on_mount'))
        except Exception as e:
            self.fail(f"App dependencies not fully resolved: {e}")


def run_tests():
    """Run all test suites and generate report"""

    print("=" * 80)
    print("PHASE 0 INFRASTRUCTURE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test suites
    suite.addTests(loader.loadTestsFromTestCase(TestSuite1_Imports))
    suite.addTests(loader.loadTestsFromTestCase(TestSuite2_Config))
    suite.addTests(loader.loadTestsFromTestCase(TestSuite3_CoreModules))
    suite.addTests(loader.loadTestsFromTestCase(TestSuite4_Persistence))
    suite.addTests(loader.loadTestsFromTestCase(TestSuite5_AppLaunch))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate summary report
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests run: {result.testsRun}")
    print(f"Tests passed: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"Tests failed: {len(result.failures)}")
    print(f"Tests with errors: {len(result.errors)}")
    print(f"Tests skipped: {len(result.skipped)}")
    print()

    if result.failures:
        print("FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            # Print just the last line for brevity
            lines = traceback.strip().split('\n')
            print(f"    {lines[-1]}")
        print()

    if result.errors:
        print("ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            # Print just the last line of the traceback for brevity
            lines = traceback.strip().split('\n')
            print(f"    {lines[-1]}")
        print()

    if result.skipped:
        print("SKIPPED:")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
        print()

    # Final verdict
    if result.wasSuccessful():
        print("=" * 80)
        print("✅ ALL TESTS PASSED - Phase 0 infrastructure is ready!")
        print("=" * 80)
    else:
        print("=" * 80)
        print("⚠️  SOME TESTS HAD ISSUES - Review details above")
        print("=" * 80)

    print()

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
