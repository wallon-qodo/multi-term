"""UI widgets for the multi-terminal interface."""

from .code_block import CodeBlock, CodeBlockParser
from .code_block_integration import CodeBlockHighlighter, CodeBlockContextMenu
from .save_file_dialog import SaveFileDialog
from .enhanced_output import EnhancedOutputPane, CodeBlockIndicator
from .bsp_tree import BSPTree, BSPNode, SplitDirection
from .bsp_renderer import BSPRenderer
from .floating_window import FloatingWindow
from .window_manager import WindowManager
from .image_preview import ImagePreview, CompactImagePreview
from .image_gallery import ImageGallery, ImageGalleryItem, UploadProgressIndicator

__all__ = [
    'CodeBlock',
    'CodeBlockParser',
    'CodeBlockHighlighter',
    'CodeBlockContextMenu',
    'SaveFileDialog',
    'EnhancedOutputPane',
    'CodeBlockIndicator',
    'BSPTree',
    'BSPNode',
    'SplitDirection',
    'BSPRenderer',
    'FloatingWindow',
    'WindowManager',
    'ImagePreview',
    'CompactImagePreview',
    'ImageGallery',
    'ImageGalleryItem',
    'UploadProgressIndicator',
]
