"""
Collaboration module for Claude Multi-Terminal

Provides session sharing, real-time collaboration, and web viewer integration.
"""

from .share_manager import ShareManager, ShareConfig, ShareInfo

__all__ = ['ShareManager', 'ShareConfig', 'ShareInfo']
