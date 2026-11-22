import io
from pathlib import Path


class DocumentIngestor:
    """Extracts raw text from plain text, native PDFs, or raster images."""

    SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}

    def extract_from_bytes(self, content: bytes, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext in {".txt", ".md", ".csv", ".json"}:
            return content.decode("utf-8", errors="replace")
        if ext == ".pdf":
            return self._extract_pdf(content)
        if ext in self.SUPPORTED_IMAGE_EXTS:
            return self._extract_image(content)
        # Fallback: attempt UTF-8 text decode
        return content.decode("utf-8", errors="replace")

    def extract_from_path(self, file_path: str | Path) -> str:
        path = Path(file_path)
        return self.extract_from_bytes(path.read_bytes(), path.name)

    def _extract_pdf(self, content: bytes) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "PDF extraction requires 'pypdf'. Install with: pip install 'invoiceflow[ocr]'"
            ) from exc

        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    def _extract_image(self, content: bytes) -> str:
        try:
            from PIL import Image
            import pytesseract
        except ImportError as exc:
            raise RuntimeError(
                "Image OCR requires 'Pillow' and 'pytesseract'. Install with: pip install 'invoiceflow[ocr]'"
            ) from exc

        image = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(image).strip()
