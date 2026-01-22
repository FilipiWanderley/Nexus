from typing import List, Dict, Any
from app.services.ai_analysis_service import AIAnalysisService
from app.core.exceptions import AIProcessingError
from app.core.logging import logger
from app.schemas.analysis import RewriteResult, OptimizeResult

class RewriteService:
    """
    Service for rewriting resume content to improve ATS compatibility.
    Strictly enforces factual accuracy while optimizing for keywords and impact.
    """

    @staticmethod
    async def optimize_full_resume(
        resume_text: str,
        job_description: str,
        missing_critical_skills: List[str],
        missing_bonus_skills: List[str],
        suggestions: List[str]
    ) -> OptimizeResult:
        """
        Generates a complete, rewritten resume optimized for the given job description.
        """
        
        prompt = f"""
        You are working inside the Nexus Career AI project.
        
        Context:
        - The system has already analyzed a resume against a job description.
        - The ATS score, missing critical skills, bonus skills, penalties, and improvement suggestions have already been generated.
        - The goal now is to produce a FINAL, OPTIMIZED RESUME TEXT tailored specifically for the job description.
        
        Task:
        Using:
        1. The original resume content:
        "{resume_text}"
        
        2. The job description:
        "{job_description}"
        
        3. The identified gaps (critical and bonus skills):
        Critical: {', '.join(missing_critical_skills)}
        Bonus: {', '.join(missing_bonus_skills)}
        
        4. The improvement suggestions already generated:
        {chr(10).join(['- ' + str(s) for s in suggestions])}
        
        You must now:
        1. Generate a **complete, rewritten resume**, fully optimized for ATS.
        2. Incorporate all suggested improvements naturally into the resume text.
        3. Add missing skills and keywords in the appropriate sections.
        4. Rewrite experience bullet points to align closely with the job description.
        5. Improve clarity, action verbs, and measurable impact where possible.
        6. Ensure the resume follows best ATS practices (clear sections, concise bullets, no graphics).
        
        Output Requirements:
        - Return a STRICT JSON object with a single field "optimized_resume_text".
        - The value of "optimized_resume_text" must be the FULL resume text, formatted in Markdown.
        - Use standard resume sections:
          - Professional Summary
          - Key Skills
          - Professional Experience
          - Education
          - Additional Skills / Tools (if applicable)
        - Do NOT include placeholders like [Your Name], unless absolutely necessary.
        - The text must be realistic, professional, and tailored to the target role.
        - The tone should match a strong candidate applying specifically for this job.
        
        Example Output Format:
        {{
            "optimized_resume_text": "# Name\\n\\n## Professional Summary\\n..."
        }}
        """
        
        try:
            response_data = await AIAnalysisService.run_prompt(
                prompt=prompt,
                temperature=0.7
            )
            
            return OptimizeResult(
                optimized_resume_text=response_data.get("optimized_resume_text", "Failed to generate optimized text.")
            )
            
        except AIProcessingError as e:
            logger.error(f"AI Optimization failed: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in RewriteService: {str(e)}")
            raise AIProcessingError("Failed to generate optimized resume")

    @staticmethod
    async def rewrite_bullet_point(
        original_text: str,
        target_skills: List[str],
        seniority_level: str
    ) -> RewriteResult:
        """
        Rewrites a single bullet point to improve impact and ATS keyword coverage.
        Uses a restrictive prompt to prevent hallucination.
        """
        
        prompt = f"""
        You are an expert Resume Editor. Your task is to rewrite the following resume bullet point to make it more impactful and ATS-friendly.

        CONTEXT:
        - Target Seniority: {seniority_level}
        - Target Skills to Integrate: {', '.join(target_skills)}
        - Original Text: "{original_text}"

        CONSTRAINTS (CRITICAL):
        1. DO NOT invent new facts, numbers, or responsibilities. You must stick to the original meaning.
        2. DO NOT exaggerate the user's role.
        3. INTEGRATE the target skills naturally if they fit the context. If a skill doesn't fit factually, IGNORE it.
        4. Use strong action verbs (e.g., "Architected", "Optimized", "Spearheaded").
        5. Keep it concise (1-2 sentences max).
        6. Return the result in valid JSON format.

        OUTPUT FORMAT (JSON):
        {{
            "rewritten_text": "The optimized version of the text...",
            "explanation": "Brief reason why this version is better...",
            "applied_keywords": ["list", "of", "skills", "actually", "used"]
        }}
        """

        try:
            response_data = await AIAnalysisService.run_prompt(
                prompt=prompt,
                temperature=0.4  # Lower temperature for deterministic/conservative output
            )

            return RewriteResult(
                original_text=original_text,
                rewritten_text=response_data.get("rewritten_text", original_text),
                explanation=response_data.get("explanation", "No explanation provided."),
                applied_keywords=response_data.get("applied_keywords", [])
            )

        except AIProcessingError as e:
            logger.error(f"AI Rewrite failed: {str(e)}")
            return RewriteResult(
                original_text=original_text,
                rewritten_text=original_text,
                explanation="AI optimization unavailable at the moment.",
                applied_keywords=[]
            )
        except Exception as e:
            logger.error(f"Unexpected error in RewriteService: {str(e)}")
            raise AIProcessingError("Failed to generate rewrite suggestion")
