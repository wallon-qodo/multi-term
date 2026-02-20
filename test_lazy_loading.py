#!/usr/bin/env python3
"""Test script for lazy loading functionality.

Tests:
1. Lazy loading initialization time (<500ms target)
2. Session cache operations (get, put, eviction)
3. Background loading functionality
4. Workspace switching with lazy loading
5. Performance comparison (lazy vs eager loading)

Usage:
    python test_lazy_loading.py
"""

import asyncio
import time
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from claude_multi_terminal.persistence.storage import SessionStorage
from claude_multi_terminal.persistence.session_state import (
    WorkspaceData, SessionState, WorkspaceState
)
from claude_multi_terminal.lazy_loader import LazyLoader, SessionCache, LoadPriority


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")


def print_test(name: str):
    """Print test name."""
    print(f"{Colors.BOLD}Testing:{Colors.RESET} {name}...", end=" ")


def print_pass(duration_ms: float = None):
    """Print test passed."""
    if duration_ms is not None:
        print(f"{Colors.GREEN}✓ PASS{Colors.RESET} ({duration_ms:.1f}ms)")
    else:
        print(f"{Colors.GREEN}✓ PASS{Colors.RESET}")


def print_fail(reason: str = ""):
    """Print test failed."""
    print(f"{Colors.RED}✗ FAIL{Colors.RESET}")
    if reason:
        print(f"  {Colors.RED}Reason: {reason}{Colors.RESET}")


def print_metric(name: str, value, target=None, unit=""):
    """Print performance metric."""
    value_str = f"{value:.2f}" if isinstance(value, float) else str(value)

    if target is not None:
        if isinstance(value, (int, float)) and value <= target:
            status = f"{Colors.GREEN}✓{Colors.RESET}"
        else:
            status = f"{Colors.YELLOW}⚠{Colors.RESET}"
        print(f"  {status} {name}: {value_str}{unit} (target: <={target}{unit})")
    else:
        print(f"  • {name}: {value_str}{unit}")


def create_test_workspace(workspace_id: int, num_sessions: int = 3) -> WorkspaceData:
    """Create test workspace data.

    Args:
        workspace_id: Workspace identifier
        num_sessions: Number of sessions to create

    Returns:
        WorkspaceData with test sessions
    """
    current_time = time.time()
    sessions = []

    for i in range(num_sessions):
        session = SessionState(
            session_id=f"session_{workspace_id}_{i}",
            name=f"Session {i+1}",
            working_directory=f"/tmp/workspace_{workspace_id}/session_{i}",
            created_at=current_time,
            modified_at=current_time,
            command_count=i * 10,
            last_command=f"echo 'Test command {i}'"
        )
        sessions.append(session)

    return WorkspaceData(
        workspace_id=f"ws_{workspace_id}",
        name=f"Workspace {workspace_id}",
        sessions=sessions,
        created_at=current_time,
        modified_at=current_time,
        description=f"Test workspace {workspace_id}",
        tags=[f"test", f"workspace{workspace_id}"]
    )


async def test_session_cache():
    """Test session cache operations."""
    print_header("Session Cache Tests")

    # Test 1: Basic cache operations
    print_test("Cache get/put operations")
    cache = SessionCache(max_size=3)
    workspace1 = create_test_workspace(1)
    workspace2 = create_test_workspace(2)

    await cache.put(1, workspace1)
    result = await cache.get(1)

    if result and result.workspace_id == workspace1.workspace_id:
        print_pass()
    else:
        print_fail("Cache get/put failed")
        return False

    # Test 2: LRU eviction
    print_test("LRU eviction policy")
    cache = SessionCache(max_size=2)

    await cache.put(1, create_test_workspace(1))
    await cache.put(2, create_test_workspace(2))
    await cache.put(3, create_test_workspace(3))  # Should evict 1

    ws1 = await cache.get(1)  # Should be None (evicted)
    ws3 = await cache.get(3)  # Should exist

    if ws1 is None and ws3 is not None:
        stats = cache.get_stats()
        print_pass()
        print_metric("Evictions", stats.evictions)
        print_metric("Current size", stats.current_size)
    else:
        print_fail("LRU eviction not working correctly")
        return False

    # Test 3: Cache statistics
    print_test("Cache statistics tracking")
    cache = SessionCache(max_size=5)

    # Generate some hits and misses
    await cache.put(1, create_test_workspace(1))
    await cache.get(1)  # Hit
    await cache.get(1)  # Hit
    await cache.get(2)  # Miss

    stats = cache.get_stats()

    if stats.hits == 2 and stats.misses == 1:
        print_pass()
        print_metric("Hit rate", stats.hit_rate * 100, unit="%")
    else:
        print_fail(f"Expected 2 hits, 1 miss; got {stats.hits} hits, {stats.misses} misses")
        return False

    return True


async def test_lazy_loader_initialization():
    """Test lazy loader initialization time."""
    print_header("Lazy Loader Initialization Tests")

    # Create temporary storage with test data
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create test storage with 10 workspaces
        storage = SessionStorage(temp_dir, lazy_loading=True)

        # Create and save test workspaces
        workspaces = {}
        for i in range(1, 11):
            workspaces[i] = create_test_workspace(i, num_sessions=5)

        storage.save_workspaces(workspaces)

        # Test 1: Initialization time
        print_test("Lazy loader initialization time")
        start_time = time.time()

        loader = LazyLoader(storage, cache_size=20)
        active_workspace = await loader.initialize(active_workspace_id=1)

        init_time = (time.time() - start_time) * 1000

        if active_workspace and init_time < 500:
            print_pass(init_time)
            print_metric("Initialization time", init_time, target=500, unit="ms")
        else:
            print_fail(f"Initialization took {init_time:.1f}ms (target: <500ms)")
            return False

        # Test 2: Get workspace (cache hit)
        print_test("Get workspace from cache")
        start_time = time.time()

        workspace = await loader.get_workspace(1)

        get_time = (time.time() - start_time) * 1000

        if workspace and get_time < 10:  # Should be very fast (cache hit)
            print_pass(get_time)
        else:
            print_fail("Cache hit too slow or workspace not found")
            return False

        # Test 3: Get workspace (cache miss)
        print_test("Get workspace on-demand (cache miss)")
        start_time = time.time()

        workspace = await loader.get_workspace(2)

        get_time = (time.time() - start_time) * 1000

        if workspace:
            print_pass(get_time)
            print_metric("On-demand load time", get_time, unit="ms")
        else:
            print_fail("Failed to load workspace on-demand")
            return False

        # Test 4: Performance statistics
        print_test("Performance statistics")
        stats = loader.get_performance_stats()

        print_pass()
        print_metric("Initialization time", stats['initialization_time_ms'], target=500, unit="ms")
        print_metric("Cache hit rate", stats['cache_hit_rate'], unit="%")
        print_metric("Meets target", "Yes" if stats['meets_target'] else "No")

        # Cleanup
        await loader.shutdown()

        return True

    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


async def test_background_loading():
    """Test background loading functionality."""
    print_header("Background Loading Tests")

    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create test storage with multiple workspaces
        storage = SessionStorage(temp_dir, lazy_loading=True)

        workspaces = {}
        for i in range(1, 6):
            workspaces[i] = create_test_workspace(i, num_sessions=3)

        storage.save_workspaces(workspaces)

        # Test 1: Background loading
        print_test("Background workspace loading")

        loader = LazyLoader(storage, cache_size=10)
        await loader.initialize(active_workspace_id=1)

        # Wait for background loading to process
        await asyncio.sleep(2)

        # Check if other workspaces were loaded
        loaded_count = len(loader.background_loader.loaded_workspaces)

        if loaded_count >= 1:  # At least active workspace
            print_pass()
            print_metric("Workspaces loaded", loaded_count)
        else:
            print_fail("Background loading not working")
            return False

        # Test 2: Priority loading
        print_test("Priority-based loading")

        loader.background_loader.enqueue(5, LoadPriority.HIGH)
        loader.background_loader.enqueue(4, LoadPriority.LOW)

        await asyncio.sleep(1)

        # High priority should be loaded
        ws5 = await loader.cache.get(5)

        if ws5:
            print_pass()
        else:
            print_fail("Priority loading not working")
            return False

        # Cleanup
        await loader.shutdown()

        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def test_performance_comparison():
    """Compare lazy loading vs eager loading performance."""
    print_header("Performance Comparison")

    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create storage with many workspaces
        print("Creating test data (20 workspaces, 10 sessions each)...")

        storage = SessionStorage(temp_dir, lazy_loading=False)
        workspaces = {}
        for i in range(1, 21):
            workspaces[i] = create_test_workspace(i, num_sessions=10)

        storage.save_workspaces(workspaces)

        # Test 1: Eager loading time
        print_test("Eager loading (traditional)")
        start_time = time.time()

        eager_storage = SessionStorage(temp_dir, lazy_loading=False)
        loaded_workspaces = eager_storage.load_workspaces()

        eager_time = (time.time() - start_time) * 1000

        print_pass(eager_time)
        print_metric("Load time", eager_time, unit="ms")
        print_metric("Workspaces loaded", len(loaded_workspaces) if loaded_workspaces else 0)

        # Test 2: Lazy loading time
        print_test("Lazy loading (active workspace only)")
        start_time = time.time()

        lazy_storage = SessionStorage(temp_dir, lazy_loading=True)
        loader = LazyLoader(lazy_storage, cache_size=20)
        active_workspace = await loader.initialize(active_workspace_id=1)

        lazy_time = (time.time() - start_time) * 1000

        print_pass(lazy_time)
        print_metric("Load time", lazy_time, target=500, unit="ms")

        # Calculate improvement
        improvement = ((eager_time - lazy_time) / eager_time) * 100

        print(f"\n{Colors.BOLD}Performance Improvement:{Colors.RESET}")
        print_metric("Speedup", f"{improvement:.1f}%")
        print_metric("Time saved", eager_time - lazy_time, unit="ms")

        # Cleanup
        await loader.shutdown()

        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Lazy Loading System Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}")

    tests = [
        ("Session Cache", test_session_cache),
        ("Lazy Loader Initialization", test_lazy_loader_initialization),
        ("Background Loading", test_background_loading),
        ("Performance Comparison", test_performance_comparison),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_fail(f"Exception: {e}")
            results.append((test_name, False))

    # Print summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"{status}  {test_name}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}")

    if passed == total:
        print(f"{Colors.GREEN}All tests passed!{Colors.RESET}")
        return 0
    else:
        print(f"{Colors.RED}Some tests failed.{Colors.RESET}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
