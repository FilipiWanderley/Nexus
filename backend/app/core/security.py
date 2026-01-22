from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from app.core.logging import logger
from typing import Optional

# Define the security scheme
security = HTTPBearer(auto_error=False) # Make it optional

def get_current_user(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Returns the user ID. 
    Prioritizes X-Session-ID (for no-login mode).
    Falls back to JWT validation.
    """
    if x_session_id:
        return x_session_id

    if not credentials:
        # Fallback to ephemeral guest ID if no session/auth provided
        import uuid
        return str(uuid.uuid4())

    token = credentials.credentials
    
    try:
        if not settings.SUPABASE_JWT_SECRET:
             logger.error("SUPABASE_JWT_SECRET is not set!")

        payload = jwt.decode(
            token, 
            settings.SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload invalid: missing user_id"
            )
            
        return user_id
        
    except JWTError as e:
        logger.warning(f"JWT Validation Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Returns the raw JWT token if present.
    """
    if credentials:
        return credentials.credentials
    return None
