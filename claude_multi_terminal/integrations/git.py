"""Git integration for AI-powered commit messages and PR descriptions."""

import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class GitIntegration:
    """Git integration providing AI-powered commit messages and PR generation."""

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize Git integration.

        Args:
            repo_path: Path to git repository. Defaults to current directory.
        """
        self.repo_path = repo_path or Path.cwd()
        self._verify_git_repo()

    def _verify_git_repo(self) -> bool:
        """Verify that the path is a git repository."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            logger.warning(f"Not a git repository: {self.repo_path}")
            return False
        return True

    def _run_git_command(self, *args: str) -> tuple[bool, str]:
        """Run a git command and return success status and output.

        Args:
            *args: Git command arguments

        Returns:
            Tuple of (success, output)
        """
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: git {' '.join(args)}")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"Git command failed: {e}")
            return False, str(e)

    def get_status(self) -> Dict[str, Any]:
        """Get current git status.

        Returns:
            Dictionary with status information including:
            - branch: current branch name
            - modified: list of modified files
            - staged: list of staged files
            - untracked: list of untracked files
            - ahead: commits ahead of remote
            - behind: commits behind remote
        """
        status = {
            "branch": self.get_current_branch(),
            "modified": [],
            "staged": [],
            "untracked": [],
            "ahead": 0,
            "behind": 0,
        }

        # Get file status
        success, output = self._run_git_command("status", "--porcelain")
        if success:
            # Split lines but don't strip to preserve format
            for line in output.rstrip('\n').split("\n"):
                if not line:
                    continue
                # Git porcelain format: XY filename
                # X = staged status, Y = unstaged status
                # Space = no change
                if len(line) < 3:
                    continue
                status_code = line[:2]
                filename = line[3:]

                # Check staged status (index)
                if status_code[0] in "MARCD":
                    status["staged"].append(filename)
                # Check unstaged status (working tree)
                if len(status_code) > 1 and status_code[1] in "MD":
                    status["modified"].append(filename)
                # Untracked files
                if status_code == "??":
                    status["untracked"].append(filename)

        # Get ahead/behind info
        success, output = self._run_git_command(
            "rev-list", "--left-right", "--count", f"HEAD...origin/{status['branch']}"
        )
        if success and output.strip():
            parts = output.strip().split()
            if len(parts) == 2:
                status["ahead"] = int(parts[0])
                status["behind"] = int(parts[1])

        return status

    def get_current_branch(self) -> str:
        """Get the current branch name."""
        success, output = self._run_git_command("branch", "--show-current")
        return output.strip() if success else "unknown"

    def get_diff(self, staged: bool = False, context: int = 3) -> str:
        """Get diff of changes.

        Args:
            staged: If True, get diff of staged changes. Otherwise, get working tree diff.
            context: Number of context lines to include

        Returns:
            Diff output as string
        """
        args = ["diff"]
        if staged:
            args.append("--cached")
        args.extend([f"--unified={context}", "--no-color"])

        success, output = self._run_git_command(*args)
        return output if success else ""

    def get_log(self, count: int = 10, oneline: bool = False) -> List[Dict[str, str]]:
        """Get commit log.

        Args:
            count: Number of commits to retrieve
            oneline: If True, return simplified format

        Returns:
            List of commit dictionaries with hash, author, date, message
        """
        format_str = "%H%x1f%an%x1f%ad%x1f%s" if not oneline else "%h%x1f%s"
        args = ["log", f"-{count}", f"--format={format_str}", "--date=iso"]

        success, output = self._run_git_command(*args)
        if not success or not output.strip():
            return []

        commits = []
        for line in output.strip().split("\n"):
            parts = line.split("\x1f")
            if oneline:
                commits.append({"hash": parts[0], "message": parts[1]})
            else:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3],
                })

        return commits

    def generate_commit_message(self, diff: Optional[str] = None) -> str:
        """Generate AI-powered commit message based on changes.

        Args:
            diff: Diff content. If None, uses staged changes.

        Returns:
            Generated commit message
        """
        if diff is None:
            diff = self.get_diff(staged=True)

        if not diff:
            return "No changes to commit"

        # Analyze the diff to generate a meaningful commit message
        # This is a rule-based implementation; can be enhanced with LLM later
        status = self.get_status()
        staged_files = status["staged"]

        # Determine change type
        change_types = set()
        for filename in staged_files:
            if any(test in filename.lower() for test in ["test_", "_test", "spec_"]):
                change_types.add("test")
            elif any(doc in filename.lower() for doc in ["readme", "doc", ".md"]):
                change_types.add("docs")
            elif "config" in filename.lower() or filename.endswith((".json", ".toml", ".yaml", ".yml")):
                change_types.add("config")
            else:
                change_types.add("code")

        # Count additions and deletions
        additions = diff.count("\n+") - diff.count("\n+++")
        deletions = diff.count("\n-") - diff.count("\n---")

        # Generate message
        if "test" in change_types:
            prefix = "test"
            summary = "Add/update tests"
        elif "docs" in change_types:
            prefix = "docs"
            summary = "Update documentation"
        elif "config" in change_types:
            prefix = "config"
            summary = "Update configuration"
        else:
            prefix = "feat" if additions > deletions * 2 else "refactor"
            summary = "Implement new feature" if prefix == "feat" else "Refactor code"

        # Build commit message
        files_str = ", ".join(staged_files[:3])
        if len(staged_files) > 3:
            files_str += f" (+{len(staged_files) - 3} more)"

        message = f"{prefix}: {summary}\n\n"
        message += f"Modified files: {files_str}\n"
        message += f"Changes: +{additions} -{deletions}\n\n"
        message += "Generated by Claude Multi-Terminal Git Integration"

        return message

    def create_commit(self, message: Optional[str] = None, auto_generate: bool = True) -> bool:
        """Create a commit with the given or auto-generated message.

        Args:
            message: Commit message. If None and auto_generate is True, generates one.
            auto_generate: Whether to auto-generate message if none provided

        Returns:
            True if commit succeeded
        """
        if message is None and auto_generate:
            message = self.generate_commit_message()

        if not message:
            logger.error("No commit message provided")
            return False

        success, output = self._run_git_command("commit", "-m", message)
        if success:
            logger.info(f"Commit created: {message.split(chr(10))[0]}")
        else:
            logger.error(f"Commit failed: {output}")

        return success

    def generate_pr_description(self, base_branch: str = "main") -> str:
        """Generate PR description based on commits and changes.

        Args:
            base_branch: Base branch to compare against

        Returns:
            Generated PR description in markdown format
        """
        current_branch = self.get_current_branch()

        # Get commits in this branch
        success, output = self._run_git_command(
            "log", f"{base_branch}..HEAD", "--format=%h %s", "--no-merges"
        )
        commits = []
        if success and output.strip():
            commits = [line.strip() for line in output.strip().split("\n")]

        # Get diff statistics
        success, stats = self._run_git_command("diff", base_branch, "--stat")

        # Build PR description
        description = f"## Pull Request: {current_branch}\n\n"
        description += "### Summary\n\n"
        description += f"This PR includes changes from the `{current_branch}` branch.\n\n"

        if commits:
            description += "### Commits\n\n"
            for commit in commits:
                description += f"- {commit}\n"
            description += "\n"

        if stats:
            description += "### Changes\n\n"
            description += "```\n"
            description += stats
            description += "```\n\n"

        description += "### Testing\n\n"
        description += "- [ ] Tests added/updated\n"
        description += "- [ ] Manual testing completed\n"
        description += "- [ ] Documentation updated\n\n"

        description += "---\n"
        description += "*Generated by Claude Multi-Terminal Git Integration*\n"

        return description

    def visualize_diff(self, staged: bool = False) -> str:
        """Generate a visual representation of the diff.

        Args:
            staged: Whether to show staged changes

        Returns:
            Formatted diff with syntax highlighting markers
        """
        diff = self.get_diff(staged=staged)
        if not diff:
            return "No changes to display"

        # Add visual markers for better readability
        lines = []
        for line in diff.split("\n"):
            if line.startswith("+++") or line.startswith("---"):
                lines.append(f"[bold cyan]{line}[/]")
            elif line.startswith("+"):
                lines.append(f"[green]{line}[/]")
            elif line.startswith("-"):
                lines.append(f"[red]{line}[/]")
            elif line.startswith("@@"):
                lines.append(f"[yellow]{line}[/]")
            else:
                lines.append(line)

        return "\n".join(lines)

    def list_branches(self, include_remote: bool = False) -> List[str]:
        """List all branches.

        Args:
            include_remote: Whether to include remote branches

        Returns:
            List of branch names
        """
        args = ["branch", "--list"]
        if include_remote:
            args.append("-a")

        success, output = self._run_git_command(*args)
        if not success:
            return []

        branches = []
        for line in output.strip().split("\n"):
            branch = line.strip().lstrip("* ").strip()
            if branch:
                branches.append(branch)

        return branches

    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """Create a new branch.

        Args:
            branch_name: Name of the new branch
            checkout: Whether to checkout the new branch

        Returns:
            True if branch created successfully
        """
        args = ["branch", branch_name]
        success, output = self._run_git_command(*args)

        if success and checkout:
            success, output = self._run_git_command("checkout", branch_name)

        return success

    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout a branch.

        Args:
            branch_name: Name of the branch to checkout

        Returns:
            True if checkout succeeded
        """
        success, output = self._run_git_command("checkout", branch_name)
        return success

    def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information.

        Returns:
            Dictionary with repository metadata
        """
        info = {
            "path": str(self.repo_path),
            "branch": self.get_current_branch(),
            "remote": None,
            "last_commit": None,
        }

        # Get remote URL
        success, output = self._run_git_command("remote", "get-url", "origin")
        if success:
            info["remote"] = output.strip()

        # Get last commit
        commits = self.get_log(count=1)
        if commits:
            info["last_commit"] = commits[0]

        return info
