import io
import pypdf
from typing import Optional
from app.clients.supabase import supabase
from app.core.exceptions import ParsingError, StorageError
from app.core.logging import logger

class TextExtractionService:
    BUCKET_NAME = "resumes"

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Normalizes extracted text:
        - Removes null bytes (Postgres compatibility)
        - Strips excessive whitespace while preserving structural newlines
        """
        if not text:
            return ""
            
        text = text.replace("\x00", "")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    @staticmethod
    def extract_text_from_storage(file_path: str, client=None) -> str:
        """
        Downloads PDF from Supabase Storage and extracts text content.
        Uses pypdf for extraction and handles both text-based and empty/image PDFs gracefully.
        """
        logger.info(f"Starting text extraction for: {file_path}")
        
        target_client = client if client else supabase

        # 1. Download from Storage
        try:
            response = target_client.storage.from_(TextExtractionService.BUCKET_NAME).download(file_path)
            if not response:
                raise ValueError("Empty response from storage")
            file_bytes = response
        except Exception as e:
            logger.error(f"Failed to download PDF from storage: {str(e)}")
            raise StorageError(f"Could not retrieve file {file_path}")

        # 2. Extract Text (pypdf)
        try:
            pdf_stream = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_stream)
            
            full_text = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)
                else:
                    logger.warning(f"Page {i+1} in {file_path} yielded no text (scanned image?)")

            if not full_text:
                logger.warning(f"No text extracted from {file_path}. Possibly an image-only PDF.")
                return ""

            raw_text = "\n\n".join(full_text)
            clean_text = TextExtractionService._clean_text(raw_text)
            
            logger.info(f"Successfully extracted {len(clean_text)} characters from {file_path}")
            return clean_text

        except Exception as e:
            logger.error(f"pypdf extraction error for {file_path}: {str(e)}")
            raise ParsingError("File content is corrupted or unreadable")
