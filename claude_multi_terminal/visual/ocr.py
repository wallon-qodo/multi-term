"""OCR (Optical Character Recognition) integration."""

import asyncio
from pathlib import Path
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass


class OCREngine(Enum):
    """Supported OCR engines."""
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    APPLE_VISION = "apple_vision"  # macOS only


@dataclass
class OCRResult:
    """OCR extraction result."""
    text: str
    confidence: float
    bounding_boxes: List[Tuple[int, int, int, int]]  # (x, y, w, h)
    language: str
    engine: OCREngine


class OCRProcessor:
    """
    OCR text extraction from images.

    Features:
    - Multiple OCR engines (Tesseract, EasyOCR, Apple Vision)
    - Multi-language support
    - Confidence scoring
    - Bounding box detection
    - Text overlay on images
    - Searchable content

    Usage:
        processor = OCRProcessor()
        result = await processor.extract_text(image_path)
        overlay_image = await processor.create_text_overlay(image_path, result)
    """

    def __init__(self, preferred_engine: Optional[OCREngine] = None):
        """
        Initialize OCR processor.

        Args:
            preferred_engine: Preferred OCR engine (auto-detect if None)
        """
        self.preferred_engine = preferred_engine
        self.available_engines: List[OCREngine] = []
        self._detect_available_engines()

    def _detect_available_engines(self) -> None:
        """Detect available OCR engines on the system."""
        import platform
        import subprocess

        # Check Tesseract
        try:
            subprocess.run(['tesseract', '--version'],
                         capture_output=True, check=True)
            self.available_engines.append(OCREngine.TESSERACT)
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        # Check EasyOCR
        try:
            import easyocr
            self.available_engines.append(OCREngine.EASYOCR)
        except ImportError:
            pass

        # Check Apple Vision (macOS only)
        if platform.system() == "Darwin":
            try:
                import Vision
                self.available_engines.append(OCREngine.APPLE_VISION)
            except ImportError:
                pass

    def get_available_engines(self) -> List[OCREngine]:
        """Get list of available OCR engines."""
        return self.available_engines.copy()

    async def extract_text(self, image_path: Path,
                          language: str = 'eng') -> Optional[OCRResult]:
        """
        Extract text from image using OCR.

        Args:
            image_path: Path to image
            language: Language code (e.g., 'eng', 'fra', 'spa')

        Returns:
            OCRResult with extracted text and metadata
        """
        if not image_path.exists():
            return None

        # Determine which engine to use
        engine = self._select_engine()
        if engine is None:
            print("No OCR engine available")
            return None

        # Extract text based on engine
        if engine == OCREngine.TESSERACT:
            return await self._extract_tesseract(image_path, language)
        elif engine == OCREngine.EASYOCR:
            return await self._extract_easyocr(image_path, language)
        elif engine == OCREngine.APPLE_VISION:
            return await self._extract_apple_vision(image_path, language)

        return None

    def _select_engine(self) -> Optional[OCREngine]:
        """Select best available OCR engine."""
        if not self.available_engines:
            return None

        if self.preferred_engine and self.preferred_engine in self.available_engines:
            return self.preferred_engine

        # Priority: Apple Vision > EasyOCR > Tesseract
        if OCREngine.APPLE_VISION in self.available_engines:
            return OCREngine.APPLE_VISION
        elif OCREngine.EASYOCR in self.available_engines:
            return OCREngine.EASYOCR
        elif OCREngine.TESSERACT in self.available_engines:
            return OCREngine.TESSERACT

        return None

    async def _extract_tesseract(self, image_path: Path,
                                 language: str) -> Optional[OCRResult]:
        """Extract text using Tesseract OCR."""
        try:
            import pytesseract
            from PIL import Image

            # Open image
            with Image.open(image_path) as img:
                # Extract text with details
                data = pytesseract.image_to_data(img, lang=language,
                                                output_type=pytesseract.Output.DICT)

                # Get text
                text = pytesseract.image_to_string(img, lang=language)

                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

                # Extract bounding boxes
                boxes = []
                n_boxes = len(data['text'])
                for i in range(n_boxes):
                    if int(data['conf'][i]) > 0:
                        x, y, w, h = (data['left'][i], data['top'][i],
                                    data['width'][i], data['height'][i])
                        boxes.append((x, y, w, h))

                return OCRResult(
                    text=text.strip(),
                    confidence=avg_confidence / 100.0,
                    bounding_boxes=boxes,
                    language=language,
                    engine=OCREngine.TESSERACT
                )

        except Exception as e:
            print(f"Tesseract OCR failed: {e}")
            return None

    async def _extract_easyocr(self, image_path: Path,
                               language: str) -> Optional[OCRResult]:
        """Extract text using EasyOCR."""
        try:
            import easyocr

            # Map language codes
            lang_map = {
                'eng': 'en',
                'fra': 'fr',
                'spa': 'es',
                'deu': 'de',
                'jpn': 'ja',
                'kor': 'ko',
                'chi_sim': 'ch_sim',
                'chi_tra': 'ch_tra',
            }
            lang_code = lang_map.get(language, 'en')

            # Initialize reader (cached)
            reader = easyocr.Reader([lang_code], gpu=False)

            # Extract text
            results = await asyncio.get_event_loop().run_in_executor(
                None, reader.readtext, str(image_path)
            )

            # Parse results
            text_parts = []
            boxes = []
            confidences = []

            for (bbox, text, confidence) in results:
                text_parts.append(text)
                confidences.append(confidence)

                # Convert bbox to (x, y, w, h)
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                x, y = min(x_coords), min(y_coords)
                w = max(x_coords) - x
                h = max(y_coords) - y
                boxes.append((int(x), int(y), int(w), int(h)))

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return OCRResult(
                text=' '.join(text_parts),
                confidence=avg_confidence,
                bounding_boxes=boxes,
                language=language,
                engine=OCREngine.EASYOCR
            )

        except Exception as e:
            print(f"EasyOCR failed: {e}")
            return None

    async def _extract_apple_vision(self, image_path: Path,
                                    language: str) -> Optional[OCRResult]:
        """Extract text using Apple Vision framework (macOS only)."""
        try:
            import Vision
            from Foundation import NSURL
            from CoreGraphics import CGImageSourceCreateWithURL, CGImageSourceCreateImageAtIndex

            # Load image
            image_url = NSURL.fileURLWithPath_(str(image_path))
            image_source = CGImageSourceCreateWithURL(image_url, None)
            image = CGImageSourceCreateImageAtIndex(image_source, 0, None)

            # Create request
            request = Vision.VNRecognizeTextRequest.alloc().init()
            request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)

            # Perform request
            handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(image, {})
            success = handler.performRequests_error_([request], None)

            if not success:
                return None

            # Extract results
            observations = request.results()
            text_parts = []
            boxes = []
            confidences = []

            for observation in observations:
                text = observation.text()
                confidence = observation.confidence()

                # Get bounding box
                bbox = observation.boundingBox()
                x = int(bbox.origin.x * image.width)
                y = int(bbox.origin.y * image.height)
                w = int(bbox.size.width * image.width)
                h = int(bbox.size.height * image.height)

                text_parts.append(text)
                boxes.append((x, y, w, h))
                confidences.append(confidence)

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return OCRResult(
                text=' '.join(text_parts),
                confidence=avg_confidence,
                bounding_boxes=boxes,
                language=language,
                engine=OCREngine.APPLE_VISION
            )

        except Exception as e:
            print(f"Apple Vision OCR failed: {e}")
            return None

    async def create_text_overlay(self, image_path: Path,
                                 ocr_result: OCRResult,
                                 output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Create image with text overlay showing detected text regions.

        Args:
            image_path: Path to original image
            ocr_result: OCR result with bounding boxes
            output_path: Output path (auto-generated if None)

        Returns:
            Path to overlay image
        """
        try:
            from PIL import Image, ImageDraw, ImageFont

            # Open image
            with Image.open(image_path) as img:
                # Create drawing context
                draw = ImageDraw.Draw(img)

                # Draw bounding boxes
                for (x, y, w, h) in ocr_result.bounding_boxes:
                    # Draw rectangle
                    draw.rectangle(
                        [(x, y), (x + w, y + h)],
                        outline='red',
                        width=2
                    )

                # Generate output path
                if output_path is None:
                    output_path = image_path.with_stem(f"{image_path.stem}_ocr")

                # Save
                img.save(output_path)
                return output_path

        except Exception as e:
            print(f"Failed to create text overlay: {e}")
            return None

    async def preprocess_for_ocr(self, image_path: Path,
                                 output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Preprocess image for better OCR accuracy.

        Args:
            image_path: Path to image
            output_path: Output path (auto-generated if None)

        Returns:
            Path to preprocessed image
        """
        try:
            from PIL import Image, ImageEnhance, ImageFilter

            with Image.open(image_path) as img:
                # Convert to grayscale
                img = img.convert('L')

                # Enhance contrast
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(2.0)

                # Sharpen
                img = img.filter(ImageFilter.SHARPEN)

                # Generate output path
                if output_path is None:
                    output_path = image_path.with_stem(f"{image_path.stem}_preprocessed")

                # Save
                img.save(output_path)
                return output_path

        except Exception as e:
            print(f"Image preprocessing failed: {e}")
            return None

    def search_text(self, ocr_result: OCRResult, query: str,
                   case_sensitive: bool = False) -> List[Tuple[int, int, int, int]]:
        """
        Search for text in OCR result and return bounding boxes.

        Args:
            ocr_result: OCR result
            query: Search query
            case_sensitive: Whether search is case-sensitive

        Returns:
            List of bounding boxes containing the query
        """
        text = ocr_result.text
        if not case_sensitive:
            text = text.lower()
            query = query.lower()

        # Find all occurrences
        matches = []
        start = 0

        while True:
            pos = text.find(query, start)
            if pos == -1:
                break

            # Find corresponding bounding box (simplified)
            # In practice, you'd need to map character positions to boxes
            matches.append(ocr_result.bounding_boxes[0] if ocr_result.bounding_boxes else (0, 0, 0, 0))

            start = pos + 1

        return matches
