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

@app.get("/api/v1/debug")
async def debug_endpoint():
    """
    Debug endpoint to verify environment configuration on Vercel.
    WARNING: Do not expose sensitive values in production.
    """
    import sys
    import os
    
    # Check dependencies
    try:
        import pypdf
        pypdf_status = "installed"
    except ImportError:
        pypdf_status = "missing"
        
    return {
        "status": "online",
        "python_version": sys.version,
        "python_path": sys.path,
        "cwd": os.getcwd(),
        "env_vars_set": {
            "SUPABASE_URL": bool(settings.SUPABASE_URL),
            "SUPABASE_KEY": bool(settings.SUPABASE_KEY),
            "GEMINI_API_KEY": bool(settings.GEMINI_API_KEY),
            "NEXT_PUBLIC_API_URL": bool(os.getenv("NEXT_PUBLIC_API_URL")),
        },
        "dependencies": {
            "pypdf": pypdf_status
        }
    }
