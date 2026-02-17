#!/usr/bin/env python3
"""Unit tests for search functionality."""

import unittest
from unittest.mock import Mock, MagicMock, patch
from rich.text import Text
from claude_multi_terminal.widgets.search_panel import SearchResult, SearchPanel


class TestSearchResult(unittest.TestCase):
    """Test SearchResult data class."""

    def test_search_result_creation(self):
        """Test creating a SearchResult object."""
        result = SearchResult(
            session_id="test-123",
            session_name="Test Session",
            line_idx=10,
            col_idx=5,
            match_text="error",
            context_before="An ",
            context_after=" occurred"
        )

        self.assertEqual(result.session_id, "test-123")
        self.assertEqual(result.session_name, "Test Session")
        self.assertEqual(result.line_idx, 10)
        self.assertEqual(result.col_idx, 5)
        self.assertEqual(result.match_text, "error")
        self.assertEqual(result.context_before, "An ")
        self.assertEqual(result.context_after, " occurred")


class TestSearchPanel(unittest.TestCase):
    """Test SearchPanel widget."""

    def setUp(self):
        """Set up test fixtures."""
        self.search_panel = SearchPanel()

    def test_search_panel_initialization(self):
        """Test SearchPanel initializes correctly."""
        self.assertEqual(self.search_panel.search_query, "")
        self.assertFalse(self.search_panel.case_sensitive)
        self.assertFalse(self.search_panel.use_regex)
        self.assertEqual(self.search_panel.current_match, 0)
        self.assertEqual(self.search_panel.total_matches, 0)
        self.assertEqual(len(self.search_panel.results), 0)
        self.assertFalse(self.search_panel.is_visible)

    def test_search_panel_visibility(self):
        """Test showing and hiding search panel."""
        # Mock the query_one method
        mock_input = Mock()
        self.search_panel.query_one = Mock(return_value=mock_input)

        # Test show
        self.search_panel.show()
        self.assertTrue(self.search_panel.is_visible)
        self.assertTrue(self.search_panel.display)
        mock_input.focus.assert_called_once()

        # Test hide
        self.search_panel._clear_all_highlights = Mock()
        self.search_panel.hide()
        self.assertFalse(self.search_panel.is_visible)
        self.assertFalse(self.search_panel.display)


class TestSearchHighlighting(unittest.TestCase):
    """Test search highlighting in SelectableRichLog."""

    def test_highlight_storage(self):
        """Test storing search highlights."""
        from claude_multi_terminal.widgets.selectable_richlog import SelectableRichLog

        log = SelectableRichLog()

        # Initially empty
        self.assertEqual(len(log.search_highlights), 0)
        self.assertIsNone(log.current_match)

        # Set highlights
        highlights = [(0, 5, 3), (1, 10, 5)]
        log.set_search_highlights(highlights)
        self.assertEqual(log.search_highlights, highlights)

        # Set current match
        log.set_current_match(0, 5, 3)
        self.assertEqual(log.current_match, (0, 5, 3))

        # Clear highlights
        log.clear_search_highlights()
        self.assertEqual(len(log.search_highlights), 0)

        # Clear current match
        log.clear_current_match()
        self.assertIsNone(log.current_match)


class TestSearchIntegration(unittest.TestCase):
    """Integration tests for search functionality."""

    def test_search_query_processing(self):
        """Test search query processing logic."""
        import re

        # Test case-insensitive search
        query = "error"
        pattern = re.compile(re.escape(query), re.IGNORECASE)

        test_text = "An Error occurred in the system"
        matches = list(pattern.finditer(test_text))

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group(), "Error")
        self.assertEqual(matches[0].start(), 3)

    def test_search_result_grouping(self):
        """Test grouping search results by session."""
        results = [
            SearchResult("s1", "Session 1", 0, 0, "test"),
            SearchResult("s1", "Session 1", 1, 0, "test"),
            SearchResult("s2", "Session 2", 0, 0, "test"),
        ]

        # Group by session
        session_counts = {}
        for result in results:
            key = (result.session_id, result.session_name)
            session_counts[key] = session_counts.get(key, 0) + 1

        self.assertEqual(session_counts[("s1", "Session 1")], 2)
        self.assertEqual(session_counts[("s2", "Session 2")], 1)


class TestSearchPerformance(unittest.TestCase):
    """Performance tests for search functionality."""

    def test_large_text_search(self):
        """Test searching through large amounts of text."""
        import re
        import time

        # Generate large text (simulate 10k lines)
        lines = []
        for i in range(10000):
            if i % 100 == 0:
                lines.append(f"Line {i}: This contains an error message")
            else:
                lines.append(f"Line {i}: Normal log output here")

        text = "\n".join(lines)

        # Time the search
        query = "error"
        pattern = re.compile(re.escape(query), re.IGNORECASE)

        start = time.time()
        matches = list(pattern.finditer(text))
        elapsed = time.time() - start

        # Should find 100 matches (every 100th line)
        self.assertEqual(len(matches), 100)

        # Should complete in less than 500ms
        self.assertLess(elapsed, 0.5, f"Search took {elapsed:.3f}s, expected < 0.5s")


def run_tests():
    """Run all search tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSearchResult))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchPanel))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchHighlighting))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchPerformance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
