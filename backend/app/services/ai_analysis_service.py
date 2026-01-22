import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from app.clients.gemini import GeminiClient
from app.core.exceptions import AIProcessingError
from app.core.logging import logger

class AIAnalysisService:
    """
    Service responsible for all interactions with Google Gemini.
    Handles client initialization, prompt execution, and response parsing.
    """

    @staticmethod
    async def run_prompt(prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Sends a prompt to Gemini and returns the parsed JSON response.
        
        Args:
            prompt: The full prompt string.
            temperature: Creativity control (0.0 to 1.0).
            
        Returns:
            Dict[str, Any]: The structured JSON response from the AI.
            
        Raises:
            AIProcessingError: If the API call fails or response is not valid JSON.
        """
        try:
            model = GeminiClient.get_model()
            
            # Configure generation for JSON response
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json"
            )

            logger.info("Sending request to Gemini...")
            
            # Generate content (Async if supported by the library, but the sync client is standard in simple setups.
            # The google-generativeai python lib has generate_content_async since recent versions.
            # We should try to use async to not block the event loop.)
            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config
            )

            # Check for safety blocks or empty responses
            if not response.parts:
                logger.error(f"Gemini returned empty response. Finish reason: {response.finish_reason}")
                raise AIProcessingError("AI returned no content (possibly triggered safety filters)")

            raw_text = response.text
            
            # Parse JSON
            try:
                data = json.loads(raw_text)
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {raw_text[:200]}... Error: {str(e)}")
                raise AIProcessingError("AI response was not valid JSON")

        except Exception as e:
            # Catch-all for API errors, connection issues, etc.
            if isinstance(e, AIProcessingError):
                raise e
            
            logger.error(f"Gemini API Error: {str(e)}", exc_info=True)
            raise AIProcessingError(f"Failed to communicate with AI service: {str(e)}")

    @staticmethod
    def build_prompt(template: str, **kwargs) -> str:
        """
        Helper to format prompt templates safely.
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing variable for prompt template: {str(e)}")
            raise AIProcessingError(f"Internal error building prompt: missing {str(e)}")

    @staticmethod
    async def get_embedding(text: str) -> list[float]:
        """
        Generates a vector embedding for the given text.
        """
        try:
            # We use the 'embedding-001' model or similar for embeddings
            # Note: The main model 'gemini-2.0-flash' is a generative model.
            # For embeddings, we usually use 'models/text-embedding-004' or similar.
            # We'll hardcode a standard embedding model for now.
            
            # Ensure client is initialized (though embed_content might not need the model object if using module level)
            GeminiClient.get_model() 
            
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="semantic_similarity"
            )
            
            if 'embedding' in result:
                return result['embedding']
            else:
                raise AIProcessingError("No embedding returned from AI service")
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise AIProcessingError(f"Failed to generate embeddings: {str(e)}")
