"""Integration modules for external tools and services."""

from .git import GitIntegration
from .file_watcher import FileWatcher
from .terminal import TerminalIntegration

__all__ = ["GitIntegration", "FileWatcher", "TerminalIntegration"]
