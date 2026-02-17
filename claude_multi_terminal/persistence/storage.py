"""File-based persistence layer for session state.

This module provides the SessionStorage class which handles all file I/O
operations for persisting session state to disk. It manages both the current
workspace state and historical session data.

The storage structure:
    ~/.multi-term/
        workspace_state.json    - Current active workspace
        history/                - Historical session snapshots
            {timestamp}_{session_id}.json

Classes:
    SessionStorage: Main storage interface for session persistence
"""

import os
import shutil
import time
import glob
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import asdict

from .session_state import WorkspaceState, SessionState, WorkspaceData

# Configure module logger
logger = logging.getLogger(__name__)


class SessionStorage:
    """Manages file-based persistence for terminal session state.

    This class provides methods to save and load workspace state, maintain
    session history, and manage the storage directory. All operations include
    proper error handling and logging.

    The storage directory structure:
        storage_dir/
            workspace_state.json     - Current workspace state
            history/                 - Historical session archives
                {timestamp}_{id}.json

    Attributes:
        storage_dir: Base directory for all storage
        state_file: Path to current workspace state file
        history_dir: Directory for historical session data

    Example:
        >>> storage = SessionStorage()  # Uses default ~/.multi-term/
        >>> workspace = WorkspaceState(sessions=[session1, session2])
        >>> storage.save_state(workspace)
        >>> loaded = storage.load_state()
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize session storage with directory creation.

        Creates the storage directory structure if it doesn't exist. Uses
        ~/.multi-term/ by default, but can be overridden (useful for testing).

        Args:
            storage_dir: Base directory for storage. If None, uses
                ~/.multi-term/ (default). Directory will be created if it
                doesn't exist.

        Example:
            >>> # Use default location
            >>> storage = SessionStorage()
            >>> # Use custom location
            >>> storage = SessionStorage(Path("/tmp/test-sessions"))
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".multi-term"

        self.storage_dir = storage_dir
        self.state_file = self.storage_dir / "workspace_state.json"
        self.history_dir = self.storage_dir / "history"
        self.workspaces_file = self.storage_dir / "workspaces.json"

        # Create directory structure
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self.history_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized storage at {self.storage_dir}")
        except OSError as e:
            logger.error(f"Failed to create storage directories: {e}")
            raise

    def save_state(self, workspace_state: WorkspaceState) -> bool:
        """Save current workspace state to disk.

        Atomically writes the workspace state to disk using a temporary file
        and rename to prevent corruption. Creates a backup of the previous
        state file if it exists.

        Args:
            workspace_state: The WorkspaceState object to persist

        Returns:
            True if save was successful, False otherwise

        Example:
            >>> storage = SessionStorage()
            >>> workspace = WorkspaceState(sessions=[session1, session2])
            >>> if storage.save_state(workspace):
            ...     print("State saved successfully")
        """
        try:
            # Create backup of existing state
            if self.state_file.exists():
                backup_file = self.state_file.with_suffix('.bak')
                shutil.copy2(self.state_file, backup_file)
                logger.debug(f"Created backup at {backup_file}")

            # Write to temporary file first (atomic operation)
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(workspace_state.to_json())
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk

            # Atomic rename
            temp_file.replace(self.state_file)
            logger.info(f"Saved workspace state with {len(workspace_state.sessions)} sessions")
            return True

        except (OSError, IOError) as e:
            logger.error(f"Failed to save workspace state: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error saving state: {e}")
            return False

    def load_state(self) -> Optional[WorkspaceState]:
        """Load workspace state from disk.

        Attempts to load and deserialize the workspace state file. If the
        file is corrupted, attempts to load from backup. Creates a backup
        of any corrupted file for debugging.

        Returns:
            WorkspaceState object if loaded successfully, None if file
            doesn't exist or is unrecoverable

        Example:
            >>> storage = SessionStorage()
            >>> workspace = storage.load_state()
            >>> if workspace:
            ...     print(f"Loaded {len(workspace.sessions)} sessions")
            ... else:
            ...     print("No saved state found")
        """
        if not self.state_file.exists():
            logger.debug("No saved state file found")
            return None

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                content = f.read()
                workspace = WorkspaceState.from_json(content)
                logger.info(f"Loaded workspace state with {len(workspace.sessions)} sessions")
                return workspace

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Corrupted state file: {e}")

            # Try to recover from backup
            backup_file = self.state_file.with_suffix('.bak')
            if backup_file.exists():
                try:
                    logger.info("Attempting to load from backup")
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        workspace = WorkspaceState.from_json(f.read())
                        logger.info("Successfully recovered from backup")
                        return workspace
                except Exception as backup_error:
                    logger.error(f"Backup recovery failed: {backup_error}")

            # Archive corrupted file
            try:
                corrupted_file = self.state_file.with_name(
                    f"corrupted_{int(time.time())}_{self.state_file.name}"
                )
                shutil.copy2(self.state_file, corrupted_file)
                logger.warning(f"Corrupted state archived to {corrupted_file}")
            except Exception:
                pass

            return None

        except (OSError, IOError) as e:
            logger.error(f"Failed to read state file: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error loading state: {e}")
            return None

    def save_session_to_history(self, session_state: SessionState) -> bool:
        """Archive a session to history directory.

        Saves a snapshot of the session state to the history directory with
        a timestamp-based filename for chronological ordering. This allows
        recovery of closed sessions.

        Args:
            session_state: SessionState object to archive

        Returns:
            True if successfully saved, False on error

        Example:
            >>> storage = SessionStorage()
            >>> session = SessionState(
            ...     session_id="abc123",
            ...     name="Build",
            ...     working_directory="/home/user",
            ...     created_at=time.time(),
            ...     modified_at=time.time()
            ... )
            >>> storage.save_session_to_history(session)
        """
        try:
            # Use modified_at for timestamp (prefer over created_at for sorting)
            timestamp = int(session_state.modified_at)
            filename = f"{timestamp}_{session_state.session_id}.json"
            filepath = self.history_dir / filename

            # Atomically write to temp file then rename
            temp_file = filepath.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(session_state), f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            temp_file.replace(filepath)
            logger.debug(f"Archived session {session_state.session_id} to history")
            return True

        except (OSError, IOError) as e:
            logger.error(f"Failed to save session to history: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error saving to history: {e}")
            return False

    def load_session_history(self, limit: int = 50) -> List[SessionState]:
        """Load recent sessions from history directory.

        Retrieves archived sessions sorted by modification time (newest first).
        Skips any corrupted history files and continues loading valid ones.

        Args:
            limit: Maximum number of sessions to return (default: 50)

        Returns:
            List of SessionState objects sorted by modified_at timestamp,
            newest first. Empty list if no history exists or on error.

        Example:
            >>> storage = SessionStorage()
            >>> recent_sessions = storage.load_session_history(limit=10)
            >>> for session in recent_sessions:
            ...     print(f"{session.name}: {session.working_directory}")
        """
        try:
            # Get all history files (exclude temp files)
            pattern = str(self.history_dir / "*.json")
            history_files = [
                f for f in glob.glob(pattern)
                if not f.endswith('.tmp')
            ]

            if not history_files:
                logger.debug("No history files found")
                return []

            # Sort by filename (timestamp prefix) for efficiency
            # Format: {timestamp}_{session_id}.json
            history_files.sort(reverse=True)

            # Load sessions up to limit
            sessions = []
            loaded_count = 0
            skipped_count = 0

            for filepath in history_files:
                if loaded_count >= limit:
                    break

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions.append(SessionState(**data))
                        loaded_count += 1

                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    logger.warning(f"Skipping corrupted history file {filepath}: {e}")
                    skipped_count += 1
                    continue
                except (OSError, IOError) as e:
                    logger.warning(f"Failed to read history file {filepath}: {e}")
                    skipped_count += 1
                    continue

            logger.info(f"Loaded {loaded_count} sessions from history (skipped {skipped_count})")
            return sessions

        except Exception as e:
            logger.exception(f"Unexpected error loading session history: {e}")
            return []

    def delete_session_from_history(self, session_id: str) -> bool:
        """Remove a session from history directory.

        Deletes all history files associated with the given session ID.
        Multiple files may exist if the session was archived multiple times.

        Args:
            session_id: Unique identifier of the session to delete

        Returns:
            True if at least one file was deleted, False if no files found
            or on error

        Example:
            >>> storage = SessionStorage()
            >>> if storage.delete_session_from_history("abc123"):
            ...     print("Session history deleted")
            ... else:
            ...     print("Session not found or error occurred")
        """
        try:
            # Find all history files for this session
            # Format: {timestamp}_{session_id}.json
            pattern = str(self.history_dir / f"*_{session_id}.json")
            files = glob.glob(pattern)

            if not files:
                logger.warning(f"No history files found for session {session_id}")
                return False

            # Delete all matching files
            deleted_count = 0
            for filepath in files:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except OSError as e:
                    logger.error(f"Failed to delete {filepath}: {e}")

            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} history files for session {session_id}")
                return True
            else:
                return False

        except Exception as e:
            logger.exception(f"Unexpected error deleting session history: {e}")
            return False

    def clear_old_history(self, days: int = 30) -> int:
        """Delete history files older than specified number of days.

        Useful for maintenance to prevent unbounded growth of history directory.
        Uses file modification time to determine age.

        Args:
            days: Delete files older than this many days (default: 30)

        Returns:
            Number of files successfully deleted

        Example:
            >>> storage = SessionStorage()
            >>> deleted = storage.clear_old_history(days=7)
            >>> print(f"Deleted {deleted} old sessions")
        """
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            deleted_count = 0
            error_count = 0

            # Get all JSON files in history directory
            pattern = str(self.history_dir / "*.json")
            history_files = [f for f in glob.glob(pattern) if not f.endswith('.tmp')]

            for filepath in history_files:
                try:
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        deleted_count += 1
                except OSError as e:
                    logger.warning(f"Failed to delete old history file {filepath}: {e}")
                    error_count += 1

            if deleted_count > 0:
                logger.info(f"Cleared {deleted_count} history files older than {days} days")
            if error_count > 0:
                logger.warning(f"Failed to delete {error_count} files")

            return deleted_count

        except Exception as e:
            logger.exception(f"Unexpected error clearing old history: {e}")
            return 0

    def get_storage_stats(self) -> dict:
        """Get statistics about storage usage.

        Returns:
            Dictionary containing storage statistics:
                - total_sessions: Number of history files
                - storage_size_mb: Total size in megabytes
                - oldest_session: Timestamp of oldest session
                - newest_session: Timestamp of newest session

        Example:
            >>> storage = SessionStorage()
            >>> stats = storage.get_storage_stats()
            >>> print(f"History contains {stats['total_sessions']} sessions")
        """
        try:
            pattern = str(self.history_dir / "*.json")
            history_files = [f for f in glob.glob(pattern) if not f.endswith('.tmp')]

            if not history_files:
                return {
                    'total_sessions': 0,
                    'storage_size_mb': 0.0,
                    'oldest_session': None,
                    'newest_session': None
                }

            total_size = sum(os.path.getsize(f) for f in history_files)
            timestamps = [os.path.getmtime(f) for f in history_files]

            return {
                'total_sessions': len(history_files),
                'storage_size_mb': round(total_size / (1024 * 1024), 2),
                'oldest_session': min(timestamps) if timestamps else None,
                'newest_session': max(timestamps) if timestamps else None
            }

        except Exception as e:
            logger.exception(f"Error calculating storage stats: {e}")
            return {
                'total_sessions': 0,
                'storage_size_mb': 0.0,
                'oldest_session': None,
                'newest_session': None
            }

    def save_workspaces(self, workspaces: Dict[int, WorkspaceData]) -> bool:
        """Save all workspaces to disk.

        Atomically writes all workspace data to a single JSON file using
        a temporary file and rename to prevent corruption. Creates a backup
        of the previous workspaces file if it exists.

        Args:
            workspaces: Dictionary mapping workspace IDs to WorkspaceData objects

        Returns:
            True if save was successful, False otherwise

        Example:
            >>> storage = SessionStorage()
            >>> workspaces = {
            ...     1: WorkspaceData(workspace_id="ws_1", name="Dev", ...),
            ...     2: WorkspaceData(workspace_id="ws_2", name="Test", ...)
            ... }
            >>> if storage.save_workspaces(workspaces):
            ...     print("Workspaces saved successfully")
        """
        try:
            # Create backup of existing workspaces file
            if self.workspaces_file.exists():
                backup_file = self.workspaces_file.with_suffix('.bak')
                shutil.copy2(self.workspaces_file, backup_file)
                logger.debug(f"Created backup at {backup_file}")

            # Convert workspaces to serializable format
            workspaces_data = {
                str(ws_id): workspace.to_dict()
                for ws_id, workspace in workspaces.items()
            }

            # Write to temporary file first (atomic operation)
            temp_file = self.workspaces_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(workspaces_data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk

            # Atomic rename
            temp_file.replace(self.workspaces_file)
            logger.info(f"Saved {len(workspaces)} workspace(s)")
            return True

        except (OSError, IOError) as e:
            logger.error(f"Failed to save workspaces: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error saving workspaces: {e}")
            return False

    def load_workspaces(self) -> Optional[Dict[int, WorkspaceData]]:
        """Load all workspaces from disk.

        Attempts to load and deserialize the workspaces file. If the file
        is corrupted, attempts to load from backup. Creates a backup of
        any corrupted file for debugging.

        Returns:
            Dictionary mapping workspace IDs to WorkspaceData objects if loaded
            successfully, None if file doesn't exist or is unrecoverable

        Example:
            >>> storage = SessionStorage()
            >>> workspaces = storage.load_workspaces()
            >>> if workspaces:
            ...     print(f"Loaded {len(workspaces)} workspace(s)")
            ... else:
            ...     print("No saved workspaces found")
        """
        if not self.workspaces_file.exists():
            logger.debug("No saved workspaces file found")
            return None

        try:
            with open(self.workspaces_file, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)

                # Convert to WorkspaceData objects
                workspaces = {}
                for ws_id_str, ws_data in data.items():
                    try:
                        ws_id = int(ws_id_str)
                        workspace = WorkspaceData.from_dict(ws_data)
                        workspaces[ws_id] = workspace
                    except (ValueError, KeyError, TypeError) as e:
                        logger.warning(f"Skipping invalid workspace {ws_id_str}: {e}")
                        continue

                logger.info(f"Loaded {len(workspaces)} workspace(s)")
                return workspaces

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Corrupted workspaces file: {e}")

            # Try to recover from backup
            backup_file = self.workspaces_file.with_suffix('.bak')
            if backup_file.exists():
                try:
                    logger.info("Attempting to load from backup")
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        data = json.loads(f.read())

                        # Convert to WorkspaceData objects
                        workspaces = {}
                        for ws_id_str, ws_data in data.items():
                            try:
                                ws_id = int(ws_id_str)
                                workspace = WorkspaceData.from_dict(ws_data)
                                workspaces[ws_id] = workspace
                            except (ValueError, KeyError, TypeError) as e:
                                logger.warning(f"Skipping invalid workspace {ws_id_str}: {e}")
                                continue

                        logger.info("Successfully recovered from backup")
                        return workspaces
                except Exception as backup_error:
                    logger.error(f"Backup recovery failed: {backup_error}")

            # Archive corrupted file
            try:
                corrupted_file = self.workspaces_file.with_name(
                    f"corrupted_{int(time.time())}_{self.workspaces_file.name}"
                )
                shutil.copy2(self.workspaces_file, corrupted_file)
                logger.warning(f"Corrupted workspaces file archived to {corrupted_file}")
            except Exception:
                pass

            return None

        except (OSError, IOError) as e:
            logger.error(f"Failed to read workspaces file: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error loading workspaces: {e}")
            return None
