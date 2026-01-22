from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

@router.get("/me", response_model=User)
def read_users_me(current_user_id: str = Depends(get_current_user)):
    """
    Get the current authenticated user's profile information.
    
    This endpoint demonstrates the usage of the `get_current_user` dependency.
    It returns the user ID extracted from the validated JWT token.
    """
    # In a real-world scenario, you might fetch additional user profile data 
    # from your `profiles` table in Supabase/Postgres here.
    # For now, we return the identity information from the token.
    
    return User(id=current_user_id)
