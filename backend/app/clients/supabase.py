from supabase import create_client, Client
from app.core.config import settings
from app.core.logging import logger

class SupabaseClient:
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            try:
                if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                    logger.warning("Supabase credentials missing. Supabase client will be disabled.")
                    return None
                    
                cls._instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                return None
        return cls._instance

supabase = SupabaseClient.get_client()
