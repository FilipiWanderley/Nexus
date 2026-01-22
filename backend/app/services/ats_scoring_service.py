import math
import json
from typing import List, Dict, Any
from app.services.ai_analysis_service import AIAnalysisService
from app.schemas.scoring import ATSScoreResult, ScoreBreakdown, KeywordMatch
from app.core.exceptions import AIProcessingError
from app.core.logging import logger

class ATSScoringService:
    
    # Weights defined in SCORING_LOGIC.md
    # Updated for Vercel deployment sync
    WEIGHT_KWS = 0.40
    WEIGHT_SEMS = 0.40
    WEIGHT_SENS = 0.20
    
    PENALTY_MISSING_CRITICAL = 5
    PENALTY_LENGTH = 5
    MAX_PENALTY_MISSING = 20

    @staticmethod
    async def calculate_score(resume_text: str, job_description: str) -> ATSScoreResult:
        """
        Calculates the ATS Match Score based on the formula:
        Score = (KwS * 0.4) + (SemS * 0.4) + (SenS * 0.2) - Penalties
        """
        
        # 1. Parallel Execution: Get AI Analysis and Embeddings
        # In a real async environment, we would run these concurrently using asyncio.gather
        # For simplicity/readability here, we run sequentially but they are async calls.
        
        # A. Semantic Analysis (Keywords, YOE, etc.)
        analysis_data = await ATSScoringService._get_ai_analysis(resume_text, job_description)
        
        # B. Embeddings for Semantic Similarity
        sem_score = await ATSScoringService._calculate_semantic_similarity(resume_text, job_description)
        
        # 2. Calculate Keyword Score (KwS)
        keyword_score, missing_critical, missing_bonus = ATSScoringService._calculate_keyword_score(
            analysis_data["jd_analysis"]["critical_keywords"],
            analysis_data["jd_analysis"]["bonus_keywords"]
        )
        
        # 3. Calculate Seniority Score (SenS)
        seniority_score = ATSScoringService._calculate_seniority_score(
            analysis_data["jd_analysis"].get("required_yoe", 0),
            analysis_data["resume_analysis"].get("candidate_yoe", 0),
            analysis_data["jd_analysis"].get("seniority_level", "Mid-Level")
        )
        
        # 4. Calculate Penalties
        penalties = ATSScoringService._calculate_penalties(
            resume_text,
            missing_critical
        )
        
        # 5. Final Formula
        raw_score = (
            (keyword_score * ATSScoringService.WEIGHT_KWS) +
            (sem_score * ATSScoringService.WEIGHT_SEMS) +
            (seniority_score * ATSScoringService.WEIGHT_SENS)
        )
        final_score = max(0, min(100, int(raw_score - penalties)))
        
        # 6. Generate Explanation
        explanation = ATSScoringService._generate_explanation(
            final_score, keyword_score, sem_score, seniority_score, penalties
        )

        # 7. Collect Suggestions
        raw_suggestions = analysis_data["resume_analysis"].get("suggestions", [])
        ai_suggestions = []
        
        for suggestion in raw_suggestions:
            if isinstance(suggestion, str):
                ai_suggestions.append(suggestion)
            elif isinstance(suggestion, dict):
                # Try to flatten dict to string
                parts = []
                for k, v in suggestion.items():
                    parts.append(f"{k}: {v}")
                ai_suggestions.append(" - ".join(parts))
            else:
                ai_suggestions.append(str(suggestion))
        
        # Add System-generated Penalty Suggestions
        system_suggestions = []
        if missing_critical:
            system_suggestions.append(f"PENALIDADE CRÍTICA: Você não possui {len(missing_critical)} habilidades críticas ({', '.join(missing_critical[:3])}{'...' if len(missing_critical)>3 else ''}). Adicione-as à sua seção de Habilidades imediatamente para aumentar sua pontuação.")
        
        word_count = len(resume_text.split())
        if word_count < 300:
            system_suggestions.append(f"PENALIDADE DE TAMANHO: Seu currículo é muito curto ({word_count} palavras). Expanda seus pontos de experiência para alcançar pelo menos 300 palavras.")
        elif word_count > 2000:
            system_suggestions.append(f"PENALIDADE DE TAMANHO: Seu currículo é muito longo ({word_count} palavras). Condense-o para menos de 2000 palavras para melhor legibilidade.")

        # Combine suggestions (System first, then AI)
        all_suggestions = system_suggestions + ai_suggestions
        
        return ATSScoreResult(
            final_score=final_score,
            breakdown=ScoreBreakdown(
                keyword_score=round(keyword_score, 1),
                semantic_score=round(sem_score, 1),
                seniority_score=round(seniority_score, 1),
                penalties=penalties
            ),
            missing_critical_skills=missing_critical,
            missing_bonus_skills=missing_bonus,
            detected_yoe=analysis_data["resume_analysis"].get("candidate_yoe"),
            required_yoe=analysis_data["jd_analysis"].get("required_yoe"),
            explanation=explanation,
            suggestions=all_suggestions
        )

    @staticmethod
    async def _get_ai_analysis(resume_text: str, jd_text: str) -> Dict[str, Any]:
        prompt_template = """
        You are an ATS (Applicant Tracking System) Expert and Resume Coach. Analyze the following Resume and Job Description (JD).
        
        Job Description:
        {jd_text}
        
        Resume:
        {resume_text}
        
        Task:
        1. Extract 'critical_keywords' (must-have technical skills) from JD. Check if they exist in Resume.
        2. Extract 'bonus_keywords' (nice-to-have tools/skills) from JD. Check if they exist in Resume.
        3. Extract 'required_yoe' (Years of Experience) from JD. Use 0 if not specified.
        4. Extract 'seniority_level' from JD (Junior, Mid-Level, Senior, Lead, Principal). Default to 'Mid-Level'.
        5. Estimate 'candidate_yoe' (Total Years of Experience) from Resume.
        6. Provide 'suggestions' as a list of 5-7 HIGHLY SPECIFIC, ACTIONABLE improvements IN PORTUGUESE (PT-BR).
           - For missing critical keywords: Suggest exactly where to add them (e.g., "Adicione 'Python' na seção de 'Habilidades Técnicas'").
           - For weak bullet points: Provide a direct rewrite for 1-2 bullets to better match the JD (e.g., "Reescreva 'Trabalhei com API' para 'Projetei e implementei APIs RESTful usando FastAPI...'").
           - For formatting/sections: Suggest structural changes if needed (e.g., "Mova 'Educação' para baixo e 'Experiência' para o topo").
           - For seniority gaps: Suggest how to frame experience to sound more senior/junior as needed.
           - Ensure suggestions are constructive and directly address the gaps found.
        
        Return STRICT JSON format:
        {{
            "jd_analysis": {{
                "critical_keywords": [{{"keyword": "Skill", "present_in_resume": true}}],
                "bonus_keywords": [{{"keyword": "Skill", "present_in_resume": false}}],
                "required_yoe": 5,
                "seniority_level": "Senior"
            }},
            "resume_analysis": {{
                "candidate_yoe": 4,
                "suggestions": [
                    "Ação: Adicione 'Docker' em Habilidades - Motivo: Exigido pela vaga",
                    "Reescrita: Mude 'Gerenciei equipe' para 'Liderei uma equipe multifuncional de 5 desenvolvedores...'"
                ]
            }}
        }}
        """
        
        prompt = AIAnalysisService.build_prompt(prompt_template, jd_text=jd_text, resume_text=resume_text)
        logger.info(f"Sending prompt to AI (Length: {len(prompt)})")
        
        try:
            response = await AIAnalysisService.run_prompt(prompt, temperature=0.0)
            logger.info(f"AI Response keys: {response.keys()}")
            return response
        except Exception as e:
            logger.error(f"AI Analysis Failed: {str(e)}")
            raise e

    @staticmethod
    async def _calculate_semantic_similarity(text1: str, text2: str) -> float:
        """Calculates cosine similarity between text embeddings."""
        try:
            vec1 = await AIAnalysisService.get_embedding(text1)
            vec2 = await AIAnalysisService.get_embedding(text2)
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm_a = math.sqrt(sum(a * a for a in vec1))
            norm_b = math.sqrt(sum(b * b for b in vec2))
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
                
            similarity = dot_product / (norm_a * norm_b)
            
            # Threshold: < 0.5 implies low relevance
            if similarity < 0.5:
                return 0.0
            
            return similarity * 100
            
        except Exception as e:
            logger.error(f"Semantic scoring failed: {str(e)}")
            return 0.0

    @staticmethod
    def _calculate_keyword_score(critical: List[Dict], bonus: List[Dict]) -> tuple[float, List[str], List[str]]:
        # Weighted formula: 70% critical, 30% bonus
        
        total_crit = len(critical)
        found_crit = sum(1 for k in critical if k.get("present_in_resume"))
        crit_rate = (found_crit / total_crit * 100) if total_crit > 0 else 100
        
        total_bonus = len(bonus)
        found_bonus = sum(1 for k in bonus if k.get("present_in_resume"))
        bonus_rate = (found_bonus / total_bonus * 100) if total_bonus > 0 else 100
        
        score = (crit_rate * 0.70) + (bonus_rate * 0.30)
        
        missing_crit_list = [k["keyword"] for k in critical if not k.get("present_in_resume")]
        missing_bonus_list = [k["keyword"] for k in bonus if not k.get("present_in_resume")]
        
        return score, missing_crit_list, missing_bonus_list

    @staticmethod
    def _calculate_seniority_score(required: float, candidate: float, level: str) -> float:
        if candidate >= required:
            return 100.0
        
        diff = required - candidate
        if diff <= 1:
            return 80.0
        elif diff <= 2:
            return 50.0
        else:
            return 0.0

    @staticmethod
    def _calculate_penalties(text: str, missing_critical: List[str]) -> int:
        penalties = 0
        
        # 1. Critical Keywords Penalty (capped)
        penalties += min(
            len(missing_critical) * ATSScoringService.PENALTY_MISSING_CRITICAL, 
            ATSScoringService.MAX_PENALTY_MISSING
        )
        
        # 2. Length Penalty (<300 or >2000 words)
        word_count = len(text.split())
        if word_count < 300 or word_count > 2000:
            penalties += ATSScoringService.PENALTY_LENGTH
            
        return penalties

    @staticmethod
    def _generate_explanation(final: int, kw: float, sem: float, sen: float, pen: int) -> str:
        if final >= 90:
            return "Excelente compatibilidade! Seu perfil está altamente alinhado com esta vaga."
        elif final >= 75:
            return "Boa compatibilidade. Você tem a maioria das habilidades principais, mas pode faltar alguns requisitos específicos."
        elif final >= 50:
            return "Compatibilidade média. Considere personalizar seu currículo para destacar as habilidades e experiências exigidas."
        else:
            return "Baixa compatibilidade. Esta vaga pode ser um desafio ou exigir experiência significativamente diferente."
