"""UI widgets for the multi-terminal interface."""

from .code_block import CodeBlock, CodeBlockParser
from .code_block_integration import CodeBlockHighlighter, CodeBlockContextMenu
from .save_file_dialog import SaveFileDialog
from .enhanced_output import EnhancedOutputPane, CodeBlockIndicator

__all__ = [
    'CodeBlock',
    'CodeBlockParser',
    'CodeBlockHighlighter',
    'CodeBlockContextMenu',
    'SaveFileDialog',
    'EnhancedOutputPane',
    'CodeBlockIndicator',
]
