from fastapi import APIRouter, Depends, UploadFile, File, status, Response
from typing import List
from app.core.security import get_current_user, get_current_token
from app.schemas.resume import ResumeResponse
from app.services.resume_service import ResumeService

router = APIRouter()

@router.post("/upload_resume", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
    token: str = Depends(get_current_token)
):
    """
    Upload a resume PDF.
    
    - Validates file type (PDF only) and size (< 5MB).
    - Stores file in Supabase Storage (private bucket).
    - Creates a database record linked to the user.
    """
    return await ResumeService.upload_resume(user_id=current_user_id, file=file, jwt_token=token)

@router.get("/download_resume")
async def download_resume(
    file_name: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Download a resume PDF.
    
    - Fetches the file from Supabase Storage.
    - Ensures user can only access their own files.
    """
    file_content = await ResumeService.download_resume(user_id=current_user_id, file_name=file_name)
    
    return Response(
        content=file_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )

@router.get("/", response_model=List[ResumeResponse])
async def get_resumes(current_user_id: str = Depends(get_current_user)):
    """
    List all resumes for the authenticated user.
    """
    # This logic should also ideally be in the service layer, but for simple fetches it's ok here.
    # For consistency, let's create a placeholder or call Supabase directly here for now.
    from app.clients.supabase import supabase
    
    # Check if guest
    try:
        response = supabase.table("resumes").select("*").eq("user_id", current_user_id).execute()
        return response.data
    except Exception as e:
        # Guests don't have DB records, return empty list instead of 500
        return []
