"""File system watcher for detecting codebase changes."""

import logging
import time
from pathlib import Path
from typing import Optional, Callable, Set, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import hashlib
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Represents a file system change event."""

    path: Path
    change_type: str  # 'created', 'modified', 'deleted'
    timestamp: datetime
    size: Optional[int] = None
    checksum: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.change_type.upper()}: {self.path} at {self.timestamp.strftime('%H:%M:%S')}"


class FileWatcher:
    """Watch file system for changes and notify listeners."""

    def __init__(
        self,
        watch_path: Optional[Path] = None,
        ignore_patterns: Optional[List[str]] = None,
        poll_interval: float = 1.0,
    ):
        """Initialize file watcher.

        Args:
            watch_path: Root path to watch. Defaults to current directory.
            ignore_patterns: List of glob patterns to ignore
            poll_interval: How often to check for changes (seconds)
        """
        self.watch_path = watch_path or Path.cwd()
        self.poll_interval = poll_interval
        self.ignore_patterns = ignore_patterns or [
            "*.pyc",
            "__pycache__",
            ".git",
            ".pytest_cache",
            "*.log",
            ".DS_Store",
            "node_modules",
            "venv",
            ".venv",
            "build",
            "dist",
            "*.egg-info",
        ]

        self._file_states: Dict[Path, tuple[float, int, str]] = {}
        self._listeners: List[Callable[[FileChange], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._change_queue: List[FileChange] = []
        self._change_history: List[FileChange] = []
        self._max_history = 100

        logger.info(f"FileWatcher initialized for {self.watch_path}")

    def _should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on patterns.

        Args:
            path: Path to check

        Returns:
            True if path should be ignored
        """
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern.startswith("*"):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
        return False

    def _compute_checksum(self, path: Path) -> str:
        """Compute checksum of a file.

        Args:
            path: File path

        Returns:
            MD5 checksum as hex string
        """
        try:
            with open(path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.debug(f"Failed to compute checksum for {path}: {e}")
            return ""

    def _scan_directory(self) -> Dict[Path, tuple[float, int, str]]:
        """Scan directory and return current file states.

        Returns:
            Dictionary mapping paths to (mtime, size, checksum) tuples
        """
        states = {}
        try:
            for path in self.watch_path.rglob("*"):
                if path.is_file() and not self._should_ignore(path):
                    try:
                        stat = path.stat()
                        # Only compute checksum for small files (< 1MB)
                        checksum = ""
                        if stat.st_size < 1024 * 1024:
                            checksum = self._compute_checksum(path)
                        states[path] = (stat.st_mtime, stat.st_size, checksum)
                    except Exception as e:
                        logger.debug(f"Failed to stat {path}: {e}")
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")

        return states

    def _detect_changes(self) -> List[FileChange]:
        """Detect changes since last scan.

        Returns:
            List of FileChange objects
        """
        current_states = self._scan_directory()
        changes = []

        # Check for new and modified files
        for path, (mtime, size, checksum) in current_states.items():
            if path not in self._file_states:
                # New file
                changes.append(
                    FileChange(
                        path=path,
                        change_type="created",
                        timestamp=datetime.now(),
                        size=size,
                        checksum=checksum,
                    )
                )
            else:
                old_mtime, old_size, old_checksum = self._file_states[path]
                # Check if modified (compare mtime and checksum if available)
                if mtime > old_mtime and (not checksum or checksum != old_checksum):
                    changes.append(
                        FileChange(
                            path=path,
                            change_type="modified",
                            timestamp=datetime.now(),
                            size=size,
                            checksum=checksum,
                        )
                    )

        # Check for deleted files
        for path in self._file_states:
            if path not in current_states:
                changes.append(
                    FileChange(
                        path=path,
                        change_type="deleted",
                        timestamp=datetime.now(),
                    )
                )

        self._file_states = current_states
        return changes

    def _watch_loop(self) -> None:
        """Main watch loop running in background thread."""
        logger.info("File watcher started")

        # Initial scan
        self._file_states = self._scan_directory()

        while self._running:
            try:
                changes = self._detect_changes()

                for change in changes:
                    # Add to queue and history
                    self._change_queue.append(change)
                    self._change_history.append(change)

                    # Trim history
                    if len(self._change_history) > self._max_history:
                        self._change_history = self._change_history[-self._max_history :]

                    # Notify listeners
                    for listener in self._listeners:
                        try:
                            listener(change)
                        except Exception as e:
                            logger.error(f"Listener error: {e}")

                time.sleep(self.poll_interval)

            except Exception as e:
                logger.error(f"Error in watch loop: {e}")
                time.sleep(self.poll_interval)

        logger.info("File watcher stopped")

    def start(self) -> None:
        """Start watching for file changes."""
        if self._running:
            logger.warning("File watcher already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info("File watcher thread started")

    def stop(self) -> None:
        """Stop watching for file changes."""
        if not self._running:
            return

        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("File watcher stopped")

    def add_listener(self, callback: Callable[[FileChange], None]) -> None:
        """Add a listener for file changes.

        Args:
            callback: Function to call when changes are detected
        """
        if callback not in self._listeners:
            self._listeners.append(callback)
            logger.debug(f"Added listener: {callback}")

    def remove_listener(self, callback: Callable[[FileChange], None]) -> None:
        """Remove a listener.

        Args:
            callback: Callback to remove
        """
        if callback in self._listeners:
            self._listeners.remove(callback)
            logger.debug(f"Removed listener: {callback}")

    def get_changes(self, clear: bool = True) -> List[FileChange]:
        """Get pending changes from queue.

        Args:
            clear: Whether to clear the queue after retrieval

        Returns:
            List of FileChange objects
        """
        changes = self._change_queue.copy()
        if clear:
            self._change_queue.clear()
        return changes

    def get_history(self, count: Optional[int] = None) -> List[FileChange]:
        """Get change history.

        Args:
            count: Number of recent changes to return. None for all.

        Returns:
            List of FileChange objects
        """
        if count is None:
            return self._change_history.copy()
        return self._change_history[-count:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get watcher statistics.

        Returns:
            Dictionary with statistics
        """
        change_counts = defaultdict(int)
        for change in self._change_history:
            change_counts[change.change_type] += 1

        return {
            "watched_files": len(self._file_states),
            "total_changes": len(self._change_history),
            "pending_changes": len(self._change_queue),
            "change_types": dict(change_counts),
            "running": self._running,
            "watch_path": str(self.watch_path),
        }

    def suggest_files(self, query: str, limit: int = 10) -> List[Path]:
        """Suggest files based on query string.

        Args:
            query: Search query (filename or path fragment)
            limit: Maximum number of suggestions

        Returns:
            List of matching file paths
        """
        query_lower = query.lower()
        matches = []

        for path in self._file_states.keys():
            if query_lower in str(path).lower():
                matches.append((path, self._compute_relevance_score(path, query)))

        # Sort by relevance score
        matches.sort(key=lambda x: x[1], reverse=True)

        return [path for path, _ in matches[:limit]]

    def _compute_relevance_score(self, path: Path, query: str) -> float:
        """Compute relevance score for file suggestion.

        Args:
            path: File path
            query: Search query

        Returns:
            Relevance score (higher is better)
        """
        path_str = str(path).lower()
        query_lower = query.lower()

        score = 0.0

        # Exact filename match
        if path.name.lower() == query_lower:
            score += 10.0

        # Filename contains query
        if query_lower in path.name.lower():
            score += 5.0

        # Path contains query
        if query_lower in path_str:
            score += 2.0

        # Prefer shorter paths (closer to root)
        score -= len(path.parts) * 0.1

        # Prefer recently modified files
        if path in self._file_states:
            mtime, _, _ = self._file_states[path]
            age_hours = (time.time() - mtime) / 3600
            score += max(0, 1.0 - age_hours / 24)  # Decay over 24 hours

        return score

    def watch_specific_files(self, patterns: List[str]) -> None:
        """Add specific file patterns to watch.

        Args:
            patterns: List of glob patterns to watch
        """
        # Remove these patterns from ignore list
        for pattern in patterns:
            if pattern in self.ignore_patterns:
                self.ignore_patterns.remove(pattern)

    def get_recent_changes_by_type(self, change_type: str, count: int = 10) -> List[FileChange]:
        """Get recent changes of a specific type.

        Args:
            change_type: Type of change ('created', 'modified', 'deleted')
            count: Number of changes to return

        Returns:
            List of FileChange objects
        """
        filtered = [c for c in self._change_history if c.change_type == change_type]
        return filtered[-count:]

    def get_active_files(self, since_minutes: int = 60) -> List[Path]:
        """Get files that have been active recently.

        Args:
            since_minutes: Time window in minutes

        Returns:
            List of file paths
        """
        cutoff = datetime.now().timestamp() - (since_minutes * 60)
        active_files = set()

        for change in self._change_history:
            if change.timestamp.timestamp() >= cutoff:
                active_files.add(change.path)

        return sorted(active_files)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
