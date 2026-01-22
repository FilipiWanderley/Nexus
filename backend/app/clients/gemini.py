import google.generativeai as genai
from app.core.config import settings
from app.core.logging import logger

class GeminiClient:
    _instance = None
    _model = None

    @classmethod
    def get_model(cls, model_name: str = None):
        """
        Get a Gemini model instance.
        If model_name is provided, tries to get that specific model.
        Otherwise returns the default configured model.
        """
        if model_name:
            try:
                return genai.GenerativeModel(model_name)
            except Exception as e:
                logger.warning(f"Failed to initialize requested model {model_name}: {e}")
                # Fallback to default logic if specific model fails
        
        if cls._instance is None:
            if not settings.GEMINI_API_KEY:
                logger.error("GEMINI_API_KEY is not set in environment variables")
                raise ValueError("GEMINI_API_KEY is missing")
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            try:
                # Prioritize flash-latest which usually points to the most stable flash version
                cls._model = genai.GenerativeModel('gemini-flash-latest')
                logger.info("Gemini Client initialized with gemini-flash-latest")
            except Exception as e:
                logger.warning(f"Failed to initialize primary model: {e}. Attempting fallback.")
                try:
                    cls._model = genai.GenerativeModel('gemini-pro')
                    logger.info("Gemini Client initialized with gemini-pro fallback")
                except Exception as ex:
                    logger.error(f"Critical: Failed to initialize any Gemini model: {ex}")
                    raise ex
            cls._instance = cls
            
        return cls._model

# Initialize on import to catch config errors early? 
# No, let's lazy load it like Supabase client to avoid side effects during import if env is missing in tests.
