from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import NexusError, ResourceNotFound, AuthError
from app.api.v1.api import api_router

# Initialize logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Error Handler
@app.exception_handler(NexusError)
async def nexus_exception_handler(request: Request, exc: NexusError):
    # Ensure message attribute exists, fallback to string representation if needed
    error_msg = getattr(exc, 'message', str(exc))
    logger.error(f"NexusError: {error_msg}")
    status_code = 500
    if isinstance(exc, ResourceNotFound):
        status_code = 404
    elif isinstance(exc, AuthError):
        status_code = 401
    
    return JSONResponse(
        status_code=status_code,
        content={"error": error_msg}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"}
    )

# Include Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
