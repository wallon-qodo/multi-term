"""Automatic session archiving system.

This module provides automatic archiving of old sessions to reduce storage usage
and improve performance. Sessions older than a configurable threshold are compressed
and moved to an archive directory, with easy restore functionality.

Features:
    - Automatic archiving based on age threshold (default: 30 days)
    - Gzip compression for space savings (typically 5-10x reduction)
    - Background archiving (non-blocking)
    - Easy restore functionality
    - Archive browsing and search
    - Maintains archive index for fast lookups

Architecture:
    ~/.multi-term/
        history/                 - Active session history
            {timestamp}_{id}.json
        archive/                 - Archived sessions
            {year}/             - Organized by year
                {month}/        - Organized by month
                    {timestamp}_{id}.json.gz
        archive_index.json      - Fast lookup index

Classes:
    SessionArchiver: Main archiving interface
    ArchiveIndex: Maintains searchable archive index
"""

import os
import gzip
import json
import time
import logging
import threading
from pathlib import Path
from typing import Optional, List, Dict, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

from .persistence.session_state import SessionState

# Configure module logger
logger = logging.getLogger(__name__)


@dataclass
class ArchiveEntry:
    """Represents a single archived session entry.

    Attributes:
        session_id: Unique identifier for the session
        name: Display name of the session
        archived_at: Unix timestamp when archived
        original_timestamp: Original session timestamp
        archive_path: Relative path to archived file
        size_bytes: Size of archived file
        original_size_bytes: Size before compression
        working_directory: Session's working directory
        last_command: Last command executed
    """
    session_id: str
    name: str
    archived_at: float
    original_timestamp: float
    archive_path: str
    size_bytes: int
    original_size_bytes: int
    working_directory: str
    last_command: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveEntry":
        """Reconstruct from dictionary."""
        return cls(**data)


class ArchiveIndex:
    """Maintains searchable index of archived sessions.

    The index provides fast lookups without decompressing archive files.
    It tracks metadata for all archived sessions and supports searching.

    Attributes:
        index_file: Path to index JSON file
        entries: Dictionary mapping session_id to ArchiveEntry
    """

    def __init__(self, index_file: Path):
        """Initialize archive index.

        Args:
            index_file: Path to index JSON file
        """
        self.index_file = index_file
        self.entries: Dict[str, ArchiveEntry] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        """Load index from disk."""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = {
                        session_id: ArchiveEntry.from_dict(entry_data)
                        for session_id, entry_data in data.items()
                    }
                logger.info(f"Loaded archive index with {len(self.entries)} entries")
            else:
                logger.debug("No archive index found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load archive index: {e}")
            self.entries = {}

    def _save(self) -> bool:
        """Save index to disk.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Atomic write using temp file
            temp_file = self.index_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                data = {
                    session_id: entry.to_dict()
                    for session_id, entry in self.entries.items()
                }
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            temp_file.replace(self.index_file)
            logger.debug(f"Saved archive index with {len(self.entries)} entries")
            return True

        except Exception as e:
            logger.error(f"Failed to save archive index: {e}")
            return False

    def add_entry(self, entry: ArchiveEntry) -> bool:
        """Add an entry to the index.

        Args:
            entry: Archive entry to add

        Returns:
            True if added successfully, False otherwise
        """
        with self._lock:
            self.entries[entry.session_id] = entry
            return self._save()

    def remove_entry(self, session_id: str) -> bool:
        """Remove an entry from the index.

        Args:
            session_id: Session ID to remove

        Returns:
            True if removed successfully, False if not found
        """
        with self._lock:
            if session_id in self.entries:
                del self.entries[session_id]
                self._save()
                return True
            return False

    def get_entry(self, session_id: str) -> Optional[ArchiveEntry]:
        """Get an entry by session ID.

        Args:
            session_id: Session ID to lookup

        Returns:
            ArchiveEntry if found, None otherwise
        """
        return self.entries.get(session_id)

    def search(
        self,
        name: Optional[str] = None,
        working_dir: Optional[str] = None,
        after_date: Optional[float] = None,
        before_date: Optional[float] = None,
        limit: int = 50
    ) -> List[ArchiveEntry]:
        """Search archived sessions.

        Args:
            name: Filter by session name (case-insensitive partial match)
            working_dir: Filter by working directory (partial match)
            after_date: Only sessions archived after this timestamp
            before_date: Only sessions archived before this timestamp
            limit: Maximum number of results

        Returns:
            List of matching archive entries, sorted by archived_at (newest first)
        """
        results = []

        for entry in self.entries.values():
            # Apply filters
            if name and name.lower() not in entry.name.lower():
                continue
            if working_dir and working_dir not in entry.working_directory:
                continue
            if after_date and entry.archived_at < after_date:
                continue
            if before_date and entry.archived_at > before_date:
                continue

            results.append(entry)

        # Sort by archived_at, newest first
        results.sort(key=lambda e: e.archived_at, reverse=True)
        return results[:limit]

    def get_stats(self) -> dict:
        """Get archive statistics.

        Returns:
            Dictionary with statistics:
                - total_sessions: Number of archived sessions
                - total_size_mb: Total size of archives in MB
                - space_saved_mb: Space saved by compression in MB
                - oldest_archive: Timestamp of oldest archive
                - newest_archive: Timestamp of newest archive
        """
        if not self.entries:
            return {
                'total_sessions': 0,
                'total_size_mb': 0.0,
                'space_saved_mb': 0.0,
                'oldest_archive': None,
                'newest_archive': None
            }

        total_size = sum(e.size_bytes for e in self.entries.values())
        original_size = sum(e.original_size_bytes for e in self.entries.values())
        timestamps = [e.archived_at for e in self.entries.values()]

        return {
            'total_sessions': len(self.entries),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'space_saved_mb': round((original_size - total_size) / (1024 * 1024), 2),
            'oldest_archive': min(timestamps) if timestamps else None,
            'newest_archive': max(timestamps) if timestamps else None
        }


class SessionArchiver:
    """Manages automatic archiving of old sessions.

    This class provides the main interface for archiving old sessions,
    with support for background archiving, compression, and restoration.

    Attributes:
        storage_dir: Base storage directory
        archive_dir: Archive directory
        history_dir: Active history directory
        archive_days: Age threshold for archiving (days)
        index: Archive index for fast lookups
    """

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        archive_days: int = 30
    ):
        """Initialize session archiver.

        Args:
            storage_dir: Base storage directory. If None, uses ~/.multi-term/
            archive_days: Age threshold for archiving (default: 30 days)
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".multi-term"

        self.storage_dir = storage_dir
        self.archive_dir = storage_dir / "archive"
        self.history_dir = storage_dir / "history"
        self.archive_days = archive_days
        self.index_file = storage_dir / "archive_index.json"

        # Create directories
        try:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized archiver at {self.archive_dir}")
        except OSError as e:
            logger.error(f"Failed to create archive directory: {e}")
            raise

        # Initialize index
        self.index = ArchiveIndex(self.index_file)

        # Background thread management
        self._background_thread: Optional[threading.Thread] = None
        self._stop_background = threading.Event()

    def _get_archive_path(self, timestamp: float) -> Path:
        """Generate archive path based on timestamp.

        Organizes archives by year/month for better directory structure.

        Args:
            timestamp: Unix timestamp

        Returns:
            Path to archive file
        """
        dt = datetime.fromtimestamp(timestamp)
        year_dir = self.archive_dir / str(dt.year)
        month_dir = year_dir / f"{dt.month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)
        return month_dir

    def archive_session(self, session_state: SessionState, history_file: Path) -> bool:
        """Archive a single session.

        Compresses the session and moves it to the archive directory,
        then updates the index.

        Args:
            session_state: Session state to archive
            history_file: Path to the history file

        Returns:
            True if archived successfully, False otherwise
        """
        try:
            # Read original session data
            with open(history_file, 'r', encoding='utf-8') as f:
                session_data = f.read()
                original_size = len(session_data.encode('utf-8'))

            # Generate archive path
            archive_month_dir = self._get_archive_path(session_state.modified_at)
            timestamp = int(session_state.modified_at)
            archive_filename = f"{timestamp}_{session_state.session_id}.json.gz"
            archive_path = archive_month_dir / archive_filename

            # Compress and write
            with gzip.open(archive_path, 'wt', encoding='utf-8') as f:
                f.write(session_data)

            # Get compressed size
            compressed_size = os.path.getsize(archive_path)

            # Create index entry
            relative_path = str(archive_path.relative_to(self.archive_dir))
            entry = ArchiveEntry(
                session_id=session_state.session_id,
                name=session_state.name,
                archived_at=time.time(),
                original_timestamp=session_state.modified_at,
                archive_path=relative_path,
                size_bytes=compressed_size,
                original_size_bytes=original_size,
                working_directory=session_state.working_directory,
                last_command=session_state.last_command
            )

            # Update index
            if not self.index.add_entry(entry):
                logger.error("Failed to update archive index")
                return False

            # Delete original history file
            history_file.unlink()

            compression_ratio = (1 - compressed_size / original_size) * 100
            logger.info(
                f"Archived session {session_state.session_id} "
                f"(compressed {compression_ratio:.1f}%)"
            )
            return True

        except Exception as e:
            logger.exception(f"Failed to archive session {session_state.session_id}: {e}")
            return False

    def restore_session(self, session_id: str) -> Optional[SessionState]:
        """Restore an archived session.

        Decompresses the session and returns the SessionState object.
        The session remains in the archive (not moved back to history).

        Args:
            session_id: Session ID to restore

        Returns:
            SessionState object if restored successfully, None otherwise
        """
        try:
            # Lookup in index
            entry = self.index.get_entry(session_id)
            if not entry:
                logger.warning(f"Session {session_id} not found in archive")
                return None

            # Read and decompress
            archive_path = self.archive_dir / entry.archive_path
            if not archive_path.exists():
                logger.error(f"Archive file not found: {archive_path}")
                return None

            with gzip.open(archive_path, 'rt', encoding='utf-8') as f:
                data = json.load(f)
                session = SessionState(**data)

            logger.info(f"Restored session {session_id} from archive")
            return session

        except Exception as e:
            logger.exception(f"Failed to restore session {session_id}: {e}")
            return None

    def auto_archive_old_sessions(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> dict:
        """Automatically archive sessions older than threshold.

        Scans the history directory and archives all sessions older than
        the configured threshold (archive_days).

        Args:
            progress_callback: Optional callback(current, total) for progress updates

        Returns:
            Dictionary with results:
                - archived_count: Number of sessions archived
                - failed_count: Number of failures
                - space_saved_mb: Space saved by archiving (MB)
        """
        try:
            cutoff_time = time.time() - (self.archive_days * 24 * 60 * 60)
            archived_count = 0
            failed_count = 0
            space_saved = 0

            # Find old history files
            import glob
            pattern = str(self.history_dir / "*.json")
            history_files = [
                Path(f) for f in glob.glob(pattern)
                if not f.endswith('.tmp')
            ]

            # Filter by age
            old_files = []
            for filepath in history_files:
                try:
                    # Extract timestamp from filename: {timestamp}_{session_id}.json
                    filename = filepath.stem
                    timestamp_str = filename.split('_')[0]
                    timestamp = float(timestamp_str)
                    if timestamp < cutoff_time:
                        old_files.append((filepath, timestamp))
                except Exception as e:
                    logger.warning(f"Failed to parse timestamp from {filepath}: {e}")
                    continue

            total = len(old_files)
            logger.info(f"Found {total} sessions to archive (older than {self.archive_days} days)")

            # Archive each old session
            for idx, (filepath, timestamp) in enumerate(old_files, 1):
                try:
                    # Load session state
                    with open(filepath, 'r', encoding='utf-8') as f:
                        original_size = len(f.read())
                        f.seek(0)
                        data = json.load(f)
                        session = SessionState(**data)

                    # Archive it
                    if self.archive_session(session, filepath):
                        archived_count += 1

                        # Calculate space saved
                        entry = self.index.get_entry(session.session_id)
                        if entry:
                            space_saved += (entry.original_size_bytes - entry.size_bytes)
                    else:
                        failed_count += 1

                    # Progress callback
                    if progress_callback:
                        progress_callback(idx, total)

                except Exception as e:
                    logger.error(f"Failed to process {filepath}: {e}")
                    failed_count += 1

            space_saved_mb = space_saved / (1024 * 1024)
            logger.info(
                f"Archiving complete: {archived_count} archived, {failed_count} failed, "
                f"{space_saved_mb:.2f} MB saved"
            )

            return {
                'archived_count': archived_count,
                'failed_count': failed_count,
                'space_saved_mb': round(space_saved_mb, 2)
            }

        except Exception as e:
            logger.exception(f"Auto-archive failed: {e}")
            return {
                'archived_count': 0,
                'failed_count': 0,
                'space_saved_mb': 0.0
            }

    def start_background_archiving(self, interval_hours: int = 24) -> None:
        """Start background archiving thread.

        Automatically archives old sessions at regular intervals.

        Args:
            interval_hours: Hours between archiving runs (default: 24)
        """
        if self._background_thread and self._background_thread.is_alive():
            logger.warning("Background archiving already running")
            return

        def _background_worker():
            logger.info(f"Background archiving started (interval: {interval_hours}h)")
            while not self._stop_background.is_set():
                try:
                    # Run archiving
                    result = self.auto_archive_old_sessions()
                    if result['archived_count'] > 0:
                        logger.info(
                            f"Background archiving: {result['archived_count']} sessions, "
                            f"{result['space_saved_mb']:.2f} MB saved"
                        )
                except Exception as e:
                    logger.error(f"Background archiving error: {e}")

                # Wait for next interval
                self._stop_background.wait(interval_hours * 3600)

            logger.info("Background archiving stopped")

        self._stop_background.clear()
        self._background_thread = threading.Thread(
            target=_background_worker,
            daemon=True,
            name="SessionArchiver"
        )
        self._background_thread.start()

    def stop_background_archiving(self) -> None:
        """Stop background archiving thread."""
        if self._background_thread and self._background_thread.is_alive():
            logger.info("Stopping background archiving...")
            self._stop_background.set()
            self._background_thread.join(timeout=5.0)
            if self._background_thread.is_alive():
                logger.warning("Background thread did not stop cleanly")
            else:
                logger.info("Background archiving stopped")

    def get_archive_stats(self) -> dict:
        """Get comprehensive archive statistics.

        Returns:
            Dictionary with statistics from index plus additional info
        """
        stats = self.index.get_stats()
        stats['archive_days_threshold'] = self.archive_days
        stats['archive_directory'] = str(self.archive_dir)
        return stats
