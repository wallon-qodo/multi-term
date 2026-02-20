"""Lazy loading system for terminal sessions.

This module provides efficient on-demand loading of sessions, background loading
for inactive workspaces, and session caching with eviction policies. It dramatically
improves startup time by only loading what's immediately needed.

Architecture:
    - LazyLoader: Main coordinator for lazy loading operations
    - SessionCache: LRU cache with configurable eviction policy
    - BackgroundLoader: Asynchronous loader for inactive workspaces

Performance targets:
    - Startup time: <500ms (loading only active workspace)
    - Background loading: Non-blocking, low priority
    - Cache hit rate: >80% for typical usage patterns

Classes:
    LazyLoader: Main lazy loading coordinator
    SessionCache: Manages cached sessions with eviction
    BackgroundLoader: Asynchronous background loader
"""

import asyncio
import logging
import time
from collections import OrderedDict
from pathlib import Path
from typing import Optional, List, Dict, Set, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from .persistence.session_state import WorkspaceState, SessionState, WorkspaceData

logger = logging.getLogger(__name__)


class LoadPriority(Enum):
    """Priority levels for loading operations."""
    IMMEDIATE = 0  # Active workspace - load immediately
    HIGH = 1       # Recently used workspaces
    NORMAL = 2     # Standard background loading
    LOW = 3        # Rarely used workspaces


@dataclass
class LoadTask:
    """Represents a loading task with priority."""
    workspace_id: int
    priority: LoadPriority
    created_at: float = field(default_factory=time.time)

    def __lt__(self, other):
        """Compare tasks by priority for queue ordering."""
        return self.priority.value < other.priority.value


@dataclass
class CacheStats:
    """Statistics for cache performance monitoring."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    current_size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def reset(self):
        """Reset statistics."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0


class SessionCache:
    """LRU cache for session states with configurable eviction policy.

    Implements a Least Recently Used (LRU) cache for session states to minimize
    disk I/O and improve performance. Automatically evicts least recently used
    sessions when the cache reaches its size limit.

    Features:
        - LRU eviction policy
        - Configurable maximum size
        - Performance statistics tracking
        - Thread-safe operations

    Attributes:
        max_size: Maximum number of workspaces to cache
        cache: Ordered dictionary maintaining LRU order
        stats: Cache performance statistics

    Example:
        >>> cache = SessionCache(max_size=10)
        >>> cache.put(1, workspace_data)
        >>> workspace = cache.get(1)  # Cache hit
        >>> cache.stats.hit_rate  # Check performance
    """

    def __init__(self, max_size: int = 20):
        """Initialize session cache.

        Args:
            max_size: Maximum number of workspaces to cache (default: 20)
        """
        self.max_size = max_size
        self.cache: OrderedDict[int, WorkspaceData] = OrderedDict()
        self.stats = CacheStats(max_size=max_size)
        self._lock = asyncio.Lock()
        logger.info(f"Initialized SessionCache with max_size={max_size}")

    async def get(self, workspace_id: int) -> Optional[WorkspaceData]:
        """Get workspace from cache.

        Retrieves a workspace from the cache and moves it to the end (most
        recently used position) in the LRU order.

        Args:
            workspace_id: Workspace identifier to retrieve

        Returns:
            WorkspaceData if found in cache, None otherwise
        """
        async with self._lock:
            if workspace_id in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(workspace_id)
                self.stats.hits += 1
                logger.debug(f"Cache HIT for workspace {workspace_id}")
                return self.cache[workspace_id]
            else:
                self.stats.misses += 1
                logger.debug(f"Cache MISS for workspace {workspace_id}")
                return None

    async def put(self, workspace_id: int, workspace_data: WorkspaceData):
        """Add workspace to cache with LRU eviction.

        Adds a workspace to the cache. If the cache is at capacity, evicts
        the least recently used workspace first.

        Args:
            workspace_id: Workspace identifier
            workspace_data: Workspace data to cache
        """
        async with self._lock:
            # If already exists, update and move to end
            if workspace_id in self.cache:
                self.cache.move_to_end(workspace_id)
                self.cache[workspace_id] = workspace_data
                logger.debug(f"Updated workspace {workspace_id} in cache")
                return

            # Check if we need to evict
            if len(self.cache) >= self.max_size:
                evicted_id, _ = self.cache.popitem(last=False)
                self.stats.evictions += 1
                logger.debug(f"Evicted workspace {evicted_id} from cache (LRU)")

            # Add new entry
            self.cache[workspace_id] = workspace_data
            self.stats.current_size = len(self.cache)
            logger.debug(f"Added workspace {workspace_id} to cache")

    async def invalidate(self, workspace_id: int):
        """Remove workspace from cache.

        Args:
            workspace_id: Workspace identifier to invalidate
        """
        async with self._lock:
            if workspace_id in self.cache:
                del self.cache[workspace_id]
                self.stats.current_size = len(self.cache)
                logger.debug(f"Invalidated workspace {workspace_id} from cache")

    async def clear(self):
        """Clear all cached workspaces."""
        async with self._lock:
            self.cache.clear()
            self.stats.current_size = 0
            logger.info("Cleared all cached workspaces")

    def get_stats(self) -> CacheStats:
        """Get current cache statistics.

        Returns:
            CacheStats object with current performance metrics
        """
        self.stats.current_size = len(self.cache)
        return self.stats


class BackgroundLoader:
    """Asynchronous background loader for inactive workspaces.

    Loads workspaces in the background without blocking the UI. Uses a priority
    queue to ensure important workspaces are loaded first. Automatically throttles
    to avoid overwhelming the system.

    Features:
        - Priority-based loading
        - Automatic throttling
        - Cancellable operations
        - Progress callbacks

    Attributes:
        load_queue: Priority queue of pending load tasks
        is_running: Whether background loading is active
        loaded_workspaces: Set of successfully loaded workspace IDs

    Example:
        >>> loader = BackgroundLoader(storage, cache)
        >>> await loader.start()
        >>> loader.enqueue(workspace_id=2, priority=LoadPriority.NORMAL)
        >>> await loader.stop()
    """

    def __init__(self, storage, cache: SessionCache):
        """Initialize background loader.

        Args:
            storage: SessionStorage instance for disk I/O
            cache: SessionCache instance for caching loaded workspaces
        """
        self.storage = storage
        self.cache = cache
        self.load_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.is_running = False
        self.loaded_workspaces: Set[int] = set()
        self._worker_task: Optional[asyncio.Task] = None
        self._progress_callback: Optional[Callable[[int, WorkspaceData], None]] = None
        logger.info("Initialized BackgroundLoader")

    async def start(self):
        """Start background loading worker."""
        if self.is_running:
            logger.warning("BackgroundLoader already running")
            return

        self.is_running = True
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("Started BackgroundLoader worker")

    async def stop(self):
        """Stop background loading worker."""
        if not self.is_running:
            return

        self.is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped BackgroundLoader worker")

    def enqueue(self, workspace_id: int, priority: LoadPriority = LoadPriority.NORMAL):
        """Add workspace to loading queue.

        Args:
            workspace_id: Workspace identifier to load
            priority: Loading priority (default: NORMAL)
        """
        if workspace_id not in self.loaded_workspaces:
            task = LoadTask(workspace_id=workspace_id, priority=priority)
            self.load_queue.put_nowait((priority.value, task))
            logger.debug(f"Enqueued workspace {workspace_id} with priority {priority.name}")

    def set_progress_callback(self, callback: Callable[[int, WorkspaceData], None]):
        """Set callback for load progress updates.

        Args:
            callback: Function called with (workspace_id, workspace_data) on load
        """
        self._progress_callback = callback

    async def _worker(self):
        """Background worker that processes load queue."""
        logger.info("BackgroundLoader worker started")

        while self.is_running:
            try:
                # Get next task with timeout to allow checking is_running
                try:
                    priority, task = await asyncio.wait_for(
                        self.load_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Check if already loaded or cached
                if task.workspace_id in self.loaded_workspaces:
                    logger.debug(f"Workspace {task.workspace_id} already loaded, skipping")
                    continue

                cached = await self.cache.get(task.workspace_id)
                if cached:
                    logger.debug(f"Workspace {task.workspace_id} in cache, skipping load")
                    self.loaded_workspaces.add(task.workspace_id)
                    continue

                # Load workspace from storage
                start_time = time.time()
                workspace_data = await self._load_workspace(task.workspace_id)
                load_time = (time.time() - start_time) * 1000

                if workspace_data:
                    # Add to cache
                    await self.cache.put(task.workspace_id, workspace_data)
                    self.loaded_workspaces.add(task.workspace_id)

                    logger.info(
                        f"Loaded workspace {task.workspace_id} in {load_time:.1f}ms "
                        f"(priority: {task.priority.name})"
                    )

                    # Notify callback
                    if self._progress_callback:
                        try:
                            self._progress_callback(task.workspace_id, workspace_data)
                        except Exception as e:
                            logger.error(f"Progress callback error: {e}")

                # Throttle to avoid overwhelming system
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                logger.info("BackgroundLoader worker cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in background loader worker: {e}")
                await asyncio.sleep(1)  # Back off on error

    async def _load_workspace(self, workspace_id: int) -> Optional[WorkspaceData]:
        """Load workspace data from storage.

        Args:
            workspace_id: Workspace identifier to load

        Returns:
            WorkspaceData if loaded successfully, None otherwise
        """
        try:
            # Run blocking I/O in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            workspaces = await loop.run_in_executor(
                None,
                self.storage.load_workspaces
            )

            if workspaces and workspace_id in workspaces:
                return workspaces[workspace_id]
            else:
                logger.warning(f"Workspace {workspace_id} not found in storage")
                return None

        except Exception as e:
            logger.error(f"Failed to load workspace {workspace_id}: {e}")
            return None


class LazyLoader:
    """Main coordinator for lazy loading operations.

    Orchestrates on-demand loading of sessions and workspaces to minimize startup
    time. Loads only the active workspace immediately, then background loads other
    workspaces as needed.

    Features:
        - Immediate loading of active workspace only
        - Background loading of inactive workspaces
        - Session caching with LRU eviction
        - Performance monitoring and statistics

    Usage:
        >>> loader = LazyLoader(storage)
        >>> await loader.initialize(active_workspace_id=1)
        >>> workspace = await loader.get_workspace(workspace_id=2)
        >>> stats = loader.get_performance_stats()
    """

    def __init__(self, storage, cache_size: int = 20):
        """Initialize lazy loader.

        Args:
            storage: SessionStorage instance for disk I/O
            cache_size: Maximum number of workspaces to cache (default: 20)
        """
        self.storage = storage
        self.cache = SessionCache(max_size=cache_size)
        self.background_loader = BackgroundLoader(storage, self.cache)
        self.active_workspace_id: Optional[int] = None
        self.initialization_time: float = 0.0
        self._initialized = False
        logger.info(f"Initialized LazyLoader with cache_size={cache_size}")

    async def initialize(self, active_workspace_id: int) -> Optional[WorkspaceData]:
        """Initialize lazy loader with active workspace.

        Loads only the active workspace immediately for fast startup. Starts
        background loading for other workspaces.

        Args:
            active_workspace_id: ID of the currently active workspace

        Returns:
            WorkspaceData for active workspace if loaded, None otherwise
        """
        if self._initialized:
            logger.warning("LazyLoader already initialized")
            return await self.get_workspace(active_workspace_id)

        start_time = time.time()
        self.active_workspace_id = active_workspace_id

        # Load only active workspace immediately
        logger.info(f"Loading active workspace {active_workspace_id}")
        active_workspace = await self._load_workspace_immediate(active_workspace_id)

        if active_workspace:
            await self.cache.put(active_workspace_id, active_workspace)
            logger.info("Active workspace loaded successfully")

        # Start background loader for other workspaces
        await self.background_loader.start()

        # Enqueue other workspaces for background loading
        await self._enqueue_inactive_workspaces(active_workspace_id)

        self.initialization_time = (time.time() - start_time) * 1000
        self._initialized = True

        logger.info(
            f"LazyLoader initialized in {self.initialization_time:.1f}ms "
            f"(target: <500ms)"
        )

        return active_workspace

    async def get_workspace(self, workspace_id: int) -> Optional[WorkspaceData]:
        """Get workspace with lazy loading.

        Attempts to get workspace from cache first. If not cached, loads from
        storage with loading indicator.

        Args:
            workspace_id: Workspace identifier to retrieve

        Returns:
            WorkspaceData if found, None otherwise
        """
        # Try cache first
        workspace = await self.cache.get(workspace_id)
        if workspace:
            return workspace

        # Load from storage
        logger.info(f"Loading workspace {workspace_id} on-demand")
        workspace = await self._load_workspace_immediate(workspace_id)

        if workspace:
            await self.cache.put(workspace_id, workspace)

        return workspace

    async def prefetch_workspace(self, workspace_id: int, priority: LoadPriority = LoadPriority.HIGH):
        """Prefetch workspace for upcoming use.

        Useful when you know a workspace will be needed soon (e.g., user is
        hovering over a workspace button).

        Args:
            workspace_id: Workspace identifier to prefetch
            priority: Loading priority (default: HIGH)
        """
        # Check if already cached
        cached = await self.cache.get(workspace_id)
        if cached:
            logger.debug(f"Workspace {workspace_id} already cached, no prefetch needed")
            return

        # Enqueue for background loading with high priority
        self.background_loader.enqueue(workspace_id, priority)
        logger.debug(f"Prefetching workspace {workspace_id}")

    async def invalidate_workspace(self, workspace_id: int):
        """Invalidate cached workspace (e.g., after modification).

        Args:
            workspace_id: Workspace identifier to invalidate
        """
        await self.cache.invalidate(workspace_id)
        logger.info(f"Invalidated workspace {workspace_id} cache")

    async def shutdown(self):
        """Shutdown lazy loader and background workers."""
        logger.info("Shutting down LazyLoader")
        await self.background_loader.stop()
        await self.cache.clear()
        self._initialized = False
        logger.info("LazyLoader shutdown complete")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics.

        Returns:
            Dictionary containing performance metrics
        """
        cache_stats = self.cache.get_stats()

        return {
            'initialization_time_ms': round(self.initialization_time, 2),
            'cache_hit_rate': round(cache_stats.hit_rate * 100, 2),
            'cache_hits': cache_stats.hits,
            'cache_misses': cache_stats.misses,
            'cache_evictions': cache_stats.evictions,
            'cache_size': cache_stats.current_size,
            'cache_max_size': cache_stats.max_size,
            'loaded_workspaces': len(self.background_loader.loaded_workspaces),
            'meets_target': self.initialization_time < 500
        }

    async def _load_workspace_immediate(self, workspace_id: int) -> Optional[WorkspaceData]:
        """Load workspace immediately (blocking).

        Args:
            workspace_id: Workspace identifier to load

        Returns:
            WorkspaceData if loaded, None otherwise
        """
        try:
            # Run blocking I/O in executor
            loop = asyncio.get_event_loop()
            workspaces = await loop.run_in_executor(
                None,
                self.storage.load_workspaces
            )

            if workspaces and workspace_id in workspaces:
                return workspaces[workspace_id]
            else:
                logger.warning(f"Workspace {workspace_id} not found")
                return None

        except Exception as e:
            logger.error(f"Failed to load workspace {workspace_id}: {e}")
            return None

    async def _enqueue_inactive_workspaces(self, active_workspace_id: int):
        """Enqueue inactive workspaces for background loading.

        Args:
            active_workspace_id: ID of active workspace (to skip)
        """
        try:
            # Load workspace IDs from storage
            loop = asyncio.get_event_loop()
            workspaces = await loop.run_in_executor(
                None,
                self.storage.load_workspaces
            )

            if not workspaces:
                logger.info("No inactive workspaces to load")
                return

            # Enqueue all workspaces except active one
            for ws_id in workspaces.keys():
                if ws_id != active_workspace_id:
                    # Use NORMAL priority for background loading
                    self.background_loader.enqueue(ws_id, LoadPriority.NORMAL)

            logger.info(f"Enqueued {len(workspaces) - 1} workspace(s) for background loading")

        except Exception as e:
            logger.error(f"Failed to enqueue inactive workspaces: {e}")
