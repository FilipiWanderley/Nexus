from fastapi import APIRouter
from app.api.v1.endpoints import resumes, users, analysis

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
