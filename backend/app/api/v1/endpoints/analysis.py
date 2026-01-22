from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any
from uuid import UUID

from app.core.security import get_current_user
from app.services.ats_scoring_service import ATSScoringService
from app.schemas.scoring import ATSScoreResult
from app.clients.supabase import supabase
from app.services.rewrite_service import RewriteService
from app.schemas.analysis import AnalysisRequest, RewriteRequest, RewriteResult, OptimizeRequest, OptimizeResult
from app.core.logging import logger
from app.core.exceptions import ResourceNotFound, NexusError

router = APIRouter()

@router.post("/optimize", response_model=OptimizeResult)
async def optimize_resume(
    request: OptimizeRequest,
    current_user_id: str = Depends(get_current_user)
) -> Any:
    """
    Generates a full optimized resume based on ATS analysis.
    """
    # Fetch Resume if text not provided
    resume_text = request.resume_text
    if not resume_text:
        if not request.resume_id:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either resume_id or resume_text must be provided")

        try:
            # We fetch only the raw_text field
            response = supabase.table("resumes")\
                .select("raw_text")\
                .eq("id", str(request.resume_id))\
                .eq("user_id", current_user_id)\
                .execute()
                
            if not response.data:
                raise ResourceNotFound(resource="Resume", resource_id=str(request.resume_id))
                
            resume_record = response.data[0]
            resume_text = resume_record.get("raw_text")
            
            if not resume_text:
                raise NexusError("Resume has no extracted text. Please re-upload or wait for processing.")
                
        except ResourceNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except NexusError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        except Exception as e:
            logger.error(f"Database error fetching resume: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    try:
        result = await RewriteService.optimize_full_resume(
            resume_text=resume_text,
            job_description=request.job_description,
            missing_critical_skills=request.missing_critical_skills,
            missing_bonus_skills=request.missing_bonus_skills,
            suggestions=request.suggestions
        )
        return result
        
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate optimized resume"
        )

@router.post("/rewrite", response_model=RewriteResult)
async def rewrite_text(
    request: RewriteRequest,
    current_user_id: str = Depends(get_current_user)
) -> Any:
    """
    Rewrites a resume bullet point to optimize for ATS keywords.
    """
    try:
        result = await RewriteService.rewrite_bullet_point(
            original_text=request.original_text,
            target_skills=request.target_skills,
            seniority_level=request.seniority_level
        )
        return result
        
    except Exception as e:
        logger.error(f"Rewrite failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate rewrite suggestion"
        )

@router.post("/score", response_model=ATSScoreResult)
async def calculate_score(
    request: AnalysisRequest,
    current_user_id: str = Depends(get_current_user)
) -> Any:
    """
    Calculates the ATS Match Score for a given resume and job description.
    
    1. Verifies the resume belongs to the user.
    2. Retrieves the raw text of the resume.
    3. Calls the ATSScoringService to compute the score.
    """
    
    resume_text = request.resume_text
    
    # 1. Fetch Resume if text not provided
    if not resume_text:
        if not request.resume_id:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either resume_id or resume_text must be provided")

        try:
            # We fetch only the raw_text field to save bandwidth
            response = supabase.table("resumes")\
                .select("raw_text")\
                .eq("id", str(request.resume_id))\
                .eq("user_id", current_user_id)\
                .execute()
                
            if not response.data:
                raise ResourceNotFound(resource="Resume", resource_id=str(request.resume_id))
                
            resume_record = response.data[0]
            resume_text = resume_record.get("raw_text")
            
            if not resume_text:
                raise NexusError("Resume has no extracted text. Please re-upload or wait for processing.")
                
        except ResourceNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except NexusError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        except Exception as e:
            logger.error(f"Database error fetching resume: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    logger.info(f"Proceeding to scoring with resume text length: {len(resume_text)}")

    # 2. Calculate Score
    try:
        result = await ATSScoringService.calculate_score(
            resume_text=resume_text,
            job_description=request.job_description
        )
        return result
        
    except Exception as e:
        logger.error(f"Scoring failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to calculate ATS score"
        )
