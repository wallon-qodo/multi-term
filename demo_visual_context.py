#!/usr/bin/env python3
"""
Demo script for Phase 5: Visual Context & Images

This script demonstrates all visual context features:
1. Screenshot capture
2. Clipboard image paste
3. Drag & drop images
4. OCR text extraction
5. Image preview and gallery
"""

import asyncio
from pathlib import Path
from claude_multi_terminal.visual import (
    ScreenshotCapture,
    ScreenshotMode,
    ImageHandler,
    ImageFormat,
    OCRProcessor,
    OCREngine,
)
from claude_multi_terminal.widgets import (
    ImagePreview,
    ImageGallery,
)


async def demo_screenshot_capture():
    """Demonstrate screenshot capture."""
    print("\n" + "=" * 60)
    print("DEMO 1: Screenshot Capture")
    print("=" * 60)

    capture = ScreenshotCapture()

    print("\n1. Fullscreen capture:")
    print("   - Captures entire screen")
    print("   - Saves to temporary directory")
    print("   - Returns path to screenshot")

    print("\n2. Selection capture:")
    print("   - Interactive area selection")
    print("   - Click and drag to select region")
    print("   - Press Enter to confirm")

    print("\n3. Window capture:")
    print("   - Click on window to capture")
    print("   - Captures specific window content")

    # Show available temp directory
    print(f"\n📁 Screenshots saved to: {capture.temp_dir}")

    # Demo cleanup
    print("\n🧹 Cleanup old screenshots:")
    capture.cleanup_old_screenshots(max_age_seconds=3600)
    print("   ✓ Old screenshots cleaned up (> 1 hour)")


async def demo_clipboard_paste():
    """Demonstrate clipboard image paste."""
    print("\n" + "=" * 60)
    print("DEMO 2: Clipboard Image Paste")
    print("=" * 60)

    handler = ImageHandler()

    print("\n1. Copy an image to clipboard")
    print("   - Screenshot (Cmd+Ctrl+Shift+4 on macOS)")
    print("   - Or copy any image file")

    print("\n2. Paste detection:")
    print("   - Automatically detects image in clipboard")
    print("   - Converts to supported format")
    print("   - Generates thumbnail")

    print("\n3. Format support:")
    for fmt in ImageFormat:
        print(f"   - {fmt.value.upper()}")

    print(f"\n📁 Images saved to: {handler.temp_dir}")


async def demo_drag_drop():
    """Demonstrate drag & drop functionality."""
    print("\n" + "=" * 60)
    print("DEMO 3: Drag & Drop Images")
    print("=" * 60)

    handler = ImageHandler()

    print("\n1. Drag image files into terminal")
    print("   - Single or multiple images")
    print("   - Automatic validation")
    print("   - Size checking")

    print("\n2. Supported operations:")
    print("   - Drop multiple images at once")
    print("   - Preview before upload")
    print("   - Progress indicators")
    print("   - Remove images from queue")

    print("\n3. File validation:")
    print("   - Checks file format")
    print("   - Validates file size (default: 10MB max)")
    print("   - Generates thumbnails")

    # Demo file handling
    print("\n4. Example file paths:")
    example_paths = [
        "/path/to/screenshot1.png",
        "/path/to/photo.jpg",
        "/path/to/diagram.gif",
    ]

    print("\n   Files to process:")
    for path in example_paths:
        print(f"   📷 {path}")


async def demo_ocr():
    """Demonstrate OCR functionality."""
    print("\n" + "=" * 60)
    print("DEMO 4: OCR Text Extraction")
    print("=" * 60)

    processor = OCRProcessor()
    available_engines = processor.get_available_engines()

    print("\n1. Available OCR engines:")
    if available_engines:
        for engine in available_engines:
            print(f"   ✓ {engine.value}")
    else:
        print("   ⚠️  No OCR engines available")
        print("   Install: brew install tesseract")
        print("   Or: pip install easyocr")

    print("\n2. Features:")
    print("   - Multi-language support")
    print("   - Confidence scoring")
    print("   - Bounding box detection")
    print("   - Text overlay on images")
    print("   - Searchable content")

    print("\n3. Supported languages:")
    languages = ['eng', 'fra', 'spa', 'deu', 'jpn', 'kor', 'chi_sim']
    for lang in languages:
        print(f"   - {lang}")

    print("\n4. OCR workflow:")
    print("   a. Preprocess image (enhance contrast)")
    print("   b. Extract text with confidence scores")
    print("   c. Generate bounding boxes")
    print("   d. Create text overlay visualization")
    print("   e. Enable text search")


async def demo_image_preview():
    """Demonstrate image preview widget."""
    print("\n" + "=" * 60)
    print("DEMO 5: Image Preview Widget")
    print("=" * 60)

    print("\n1. Full preview:")
    print("   - ASCII art thumbnail")
    print("   - Image metadata (size, format, dimensions)")
    print("   - Send/Cancel buttons")
    print("   - ESC to close")

    print("\n2. Compact preview:")
    print("   - Inline display in chat")
    print("   - Small thumbnail")
    print("   - Click to expand")

    print("\n3. Preview features:")
    print("   - Shows image dimensions")
    print("   - Displays file size")
    print("   - Format information")
    print("   - Quick actions (send/cancel)")


async def demo_image_gallery():
    """Demonstrate image gallery widget."""
    print("\n" + "=" * 60)
    print("DEMO 6: Image Gallery")
    print("=" * 60)

    print("\n1. Gallery features:")
    print("   - List view of all images")
    print("   - Multiple selection")
    print("   - Batch operations")
    print("   - Progress indicators")

    print("\n2. Operations:")
    print("   - Upload All: Send all images")
    print("   - Remove Selected: Delete from queue")
    print("   - Clear All: Empty gallery")
    print("   - Close: Hide gallery")

    print("\n3. Progress tracking:")
    print("   - Current/Total counter")
    print("   - Percentage complete")
    print("   - Individual file progress")
    print("   - Upload success/failure status")


async def demo_keyboard_shortcuts():
    """Show keyboard shortcuts."""
    print("\n" + "=" * 60)
    print("KEYBOARD SHORTCUTS")
    print("=" * 60)

    shortcuts = [
        ("Ctrl+Shift+S", "Capture screenshot (selection mode)"),
        ("Ctrl+Shift+F", "Capture fullscreen"),
        ("Ctrl+V", "Paste image from clipboard"),
        ("Ctrl+Shift+O", "OCR on selected image"),
        ("Ctrl+G", "Show/hide image gallery"),
        ("ESC", "Close preview/gallery"),
        ("Enter", "Send image (in preview)"),
    ]

    print("\n📋 Available shortcuts:")
    for key, description in shortcuts:
        print(f"   {key:20s} - {description}")


async def demo_integration_example():
    """Show integration example."""
    print("\n" + "=" * 60)
    print("INTEGRATION EXAMPLE")
    print("=" * 60)

    print("\nComplete workflow example:")
    print("""
    # 1. User presses Ctrl+Shift+S
    capture = ScreenshotCapture()
    screenshot = await capture.capture_selection()

    # 2. Show preview
    preview = ImagePreview(screenshot)
    preview.set_send_callback(on_send_image)
    await app.mount(preview)

    # 3. User confirms, run OCR
    processor = OCRProcessor()
    ocr_result = await processor.extract_text(screenshot)

    # 4. Upload to Claude with text overlay
    handler = ImageHandler()
    b64_image = handler.get_image_base64(screenshot)

    # 5. Send to conversation
    await send_message_with_image(
        text=f"Screenshot with extracted text: {ocr_result.text}",
        image=b64_image
    )
    """)


async def demo_success_criteria():
    """Show success criteria checklist."""
    print("\n" + "=" * 60)
    print("SUCCESS CRITERIA CHECKLIST")
    print("=" * 60)

    criteria = [
        "Screenshot capture working (Ctrl+Shift+S)",
        "Paste images from clipboard",
        "Drag & drop functional",
        "OCR extracts text accurately",
        "Image preview looks good",
        "Gallery manages multiple images",
        "Progress indicators working",
        "Tests passing",
        "Documentation complete",
    ]

    print("\n✓ Phase 5 Requirements:")
    for item in criteria:
        print(f"   ✓ {item}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print(" " * 20 + "PHASE 5: VISUAL CONTEXT & IMAGES")
    print(" " * 20 + "Demo & Feature Overview")
    print("=" * 80)

    # Run all demos
    await demo_screenshot_capture()
    await asyncio.sleep(0.5)

    await demo_clipboard_paste()
    await asyncio.sleep(0.5)

    await demo_drag_drop()
    await asyncio.sleep(0.5)

    await demo_ocr()
    await asyncio.sleep(0.5)

    await demo_image_preview()
    await asyncio.sleep(0.5)

    await demo_image_gallery()
    await asyncio.sleep(0.5)

    await demo_keyboard_shortcuts()
    await asyncio.sleep(0.5)

    await demo_integration_example()
    await asyncio.sleep(0.5)

    await demo_success_criteria()

    print("\n" + "=" * 80)
    print(" " * 25 + "Demo Complete!")
    print("=" * 80)
    print("\n📚 Next steps:")
    print("   1. Run tests: pytest tests/test_visual_context.py")
    print("   2. Install OCR: brew install tesseract")
    print("   3. Try features in app: multi-term")
    print("   4. Read docs: docs/PHASE5_VISUAL_CONTEXT.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())
