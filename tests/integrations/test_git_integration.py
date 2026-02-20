"""Tests for Git integration."""

import pytest
import tempfile
import subprocess
from pathlib import Path
from claude_multi_terminal.integrations.git import GitIntegration


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    test_file = repo_path / "test.txt"
    test_file.write_text("Initial content\n")
    subprocess.run(["git", "add", "test.txt"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    return repo_path


def test_git_integration_init(git_repo):
    """Test GitIntegration initialization."""
    git = GitIntegration(git_repo)
    assert git.repo_path == git_repo


def test_get_current_branch(git_repo):
    """Test getting current branch."""
    git = GitIntegration(git_repo)
    branch = git.get_current_branch()
    assert branch in ["main", "master"]


def test_get_status(git_repo):
    """Test getting git status."""
    git = GitIntegration(git_repo)

    # Create a modified file
    test_file = git_repo / "test.txt"
    test_file.write_text("Modified content\n")

    # Create a new untracked file
    new_file = git_repo / "new.txt"
    new_file.write_text("New file\n")

    status = git.get_status()

    print(f"\nStatus dict: {status}")
    print(f"Modified list: {status['modified']}")
    print(f"Untracked list: {status['untracked']}")

    assert "branch" in status
    assert "modified" in status
    assert "untracked" in status
    # Git porcelain format shows " M test.txt" for modified files
    assert any("test.txt" in f for f in status["modified"]), f"test.txt not in {status['modified']}"
    assert any("new.txt" in f for f in status["untracked"]), f"new.txt not in {status['untracked']}"


def test_get_diff(git_repo):
    """Test getting diff."""
    git = GitIntegration(git_repo)

    # Modify a file
    test_file = git_repo / "test.txt"
    test_file.write_text("Modified content\n")

    diff = git.get_diff()
    assert "Initial content" in diff
    assert "Modified content" in diff


def test_get_diff_staged(git_repo):
    """Test getting staged diff."""
    git = GitIntegration(git_repo)

    # Modify and stage a file
    test_file = git_repo / "test.txt"
    test_file.write_text("Staged content\n")
    subprocess.run(["git", "add", "test.txt"], cwd=git_repo, check=True, capture_output=True)

    diff = git.get_diff(staged=True)
    assert "Staged content" in diff


def test_get_log(git_repo):
    """Test getting commit log."""
    git = GitIntegration(git_repo)

    log = git.get_log(count=1)
    assert len(log) == 1
    assert log[0]["message"] == "Initial commit"
    assert "hash" in log[0]
    assert "author" in log[0]


def test_generate_commit_message(git_repo):
    """Test commit message generation."""
    git = GitIntegration(git_repo)

    # Create some changes
    test_file = git_repo / "test.py"
    test_file.write_text("def test():\n    pass\n")
    subprocess.run(["git", "add", "test.py"], cwd=git_repo, check=True, capture_output=True)

    message = git.generate_commit_message()
    assert len(message) > 0
    assert "test.py" in message


def test_create_commit(git_repo):
    """Test creating a commit."""
    git = GitIntegration(git_repo)

    # Create and stage changes
    new_file = git_repo / "feature.txt"
    new_file.write_text("Feature content\n")
    subprocess.run(["git", "add", "feature.txt"], cwd=git_repo, check=True, capture_output=True)

    # Create commit
    success = git.create_commit("Add feature", auto_generate=False)
    assert success

    # Verify commit exists
    log = git.get_log(count=1)
    assert "Add feature" in log[0]["message"]


def test_list_branches(git_repo):
    """Test listing branches."""
    git = GitIntegration(git_repo)

    branches = git.list_branches()
    assert len(branches) > 0
    assert any(b in ["main", "master"] for b in branches)


def test_create_branch(git_repo):
    """Test creating a branch."""
    git = GitIntegration(git_repo)

    success = git.create_branch("feature-test", checkout=False)
    assert success

    branches = git.list_branches()
    assert "feature-test" in branches


def test_checkout_branch(git_repo):
    """Test checking out a branch."""
    git = GitIntegration(git_repo)

    # Create branch
    git.create_branch("test-branch", checkout=False)

    # Checkout branch
    success = git.checkout_branch("test-branch")
    assert success

    # Verify current branch
    assert git.get_current_branch() == "test-branch"


def test_generate_pr_description(git_repo):
    """Test PR description generation."""
    git = GitIntegration(git_repo)

    # Create a feature branch with commits
    git.create_branch("feature-branch")

    new_file = git_repo / "feature.txt"
    new_file.write_text("Feature\n")
    subprocess.run(["git", "add", "feature.txt"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add feature"],
        cwd=git_repo,
        check=True,
        capture_output=True,
    )

    # Generate PR description
    description = git.generate_pr_description(base_branch="main")
    assert "Pull Request" in description
    assert "feature-branch" in description


def test_visualize_diff(git_repo):
    """Test diff visualization."""
    git = GitIntegration(git_repo)

    # Create changes
    test_file = git_repo / "test.txt"
    test_file.write_text("Modified content\n")

    visual_diff = git.visualize_diff()
    assert len(visual_diff) > 0


def test_get_repository_info(git_repo):
    """Test getting repository info."""
    git = GitIntegration(git_repo)

    info = git.get_repository_info()
    assert "path" in info
    assert "branch" in info
    assert "last_commit" in info
    assert info["path"] == str(git_repo)
