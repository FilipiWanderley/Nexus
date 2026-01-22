import uuid
from typing import BinaryIO
from fastapi import UploadFile, HTTPException, status
from app.clients.supabase import supabase
from app.core.config import settings
from supabase import create_client, ClientOptions
from app.schemas.resume import ResumeCreate, ResumeResponse
from app.core.exceptions import NexusError, StorageError, ParsingError
from app.core.logging import logger
from app.services.extraction_service import TextExtractionService

class ResumeService:
    BUCKET_NAME = "resumes"
    ALLOWED_CONTENT_TYPE = "application/pdf"
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    @staticmethod
    async def download_resume(user_id: str, file_name: str) -> bytes:
        """
        Downloads a resume from Supabase Storage.
        """
        storage_path = f"{user_id}/{file_name}"
        
        try:
            # Check if file exists (optional, but good for better error messages)
            # For now, we try to download directly.
            
            res = supabase.storage.from_(ResumeService.BUCKET_NAME).download(storage_path)
            
            if not res:
                raise ResourceNotFound(resource="Resume File", resource_id=file_name)
                
            return res
            
        except Exception as e:
            # Supabase might raise different errors for not found vs other issues
            # We assume generic 404 if it fails in a certain way, or log it.
            logger.error(f"Download failed for {storage_path}: {str(e)}")
            # If it's a specific storage error, re-raise as 404
            if "not found" in str(e).lower() or "Object not found" in str(e):
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resume file '{file_name}' not found."
                )
            raise StorageError(detail="Failed to download file from storage")

    @staticmethod
    async def validate_file(file: UploadFile) -> None:
        """
        Validates file type and size.
        Note: Actual size validation for streaming uploads is tricky in FastAPI without reading chunks.
        We rely on Supabase Storage limits as a hard stop, but check content-type here.
        """
        if file.content_type != ResumeService.ALLOWED_CONTENT_TYPE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only PDF files are allowed."
            )

    @staticmethod
    async def upload_resume(user_id: str, file: UploadFile, jwt_token: str = None) -> ResumeResponse:
        """
        Orchestrates the resume upload workflow.
        Handles both authenticated users and guest sessions (no DB persistence for guests).
        """
        await ResumeService.validate_file(file)

        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
        storage_path = f"{user_id}/{safe_filename}"

        # Determine if we should use a scoped client (Auth) or global (Guest)
        client = supabase
        if jwt_token:
            try:
                client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY,
                    options=ClientOptions(headers={"Authorization": f"Bearer {jwt_token}"})
                )
            except Exception as e:
                logger.warning(f"Failed to create scoped client: {e}. Falling back to global client.")
                client = supabase

        try:
            content = await file.read()
            if len(content) > ResumeService.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large. Maximum size is 5MB."
                )
        except Exception as e:
            logger.error(f"Error reading file upload: {str(e)}")
            raise HTTPException(status_code=500, detail="Could not read file content")

        # 1. Upload to Supabase Storage
        try:
            # Upsert ensures we don't fail on duplicate uploads for the same session
            res = client.storage.from_(ResumeService.BUCKET_NAME).upload(
                path=storage_path,
                file=content,
                file_options={"content-type": "application/pdf", "upsert": "true"}
            )
        except Exception as e:
            logger.error(f"Supabase Storage Upload Error: {str(e)}")
            # Fallback: Proceed to text extraction even if storage fails (Guest Mode robustness)
            logger.info("Proceeding to text extraction despite storage upload failure.")

        # 2. Trigger Text Extraction
        # Priority: Storage -> In-Memory Fallback
        try:
            extracted_text = TextExtractionService.extract_text_from_storage(storage_path, client=client)
        except Exception as e:
            logger.warning(f"Storage extraction failed: {e}. Trying in-memory fallback.")
            
            # In-Memory Fallback using PyPDF2
            from io import BytesIO
            import PyPDF2
            try:
                reader = PyPDF2.PdfReader(BytesIO(content))
                text = []
                for page in reader.pages:
                    text.append(page.extract_text())
                extracted_text = "\n".join(text)
            except Exception as pdf_err:
                logger.error(f"In-memory PDF extraction failed: {pdf_err}")
                extracted_text = ""

        # 3. Return Response (Skip DB Persistence for Guests)
        import uuid
        from datetime import datetime
        
        return ResumeResponse(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid4(),
            file_name=file.filename,
            file_path=storage_path,
            parsed_content={},
            raw_text=extracted_text,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

