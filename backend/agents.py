# backend/agents.py
"""
Agent wrappers. Each agent calls underlying tools and handles local errors.
Agents are thin and compose tool functions from backend.tools.*.
"""

from typing import Dict, Any, Optional

from backend.tools import (
    resume_parser,
    skill_extractor,
    jd_analyzer,
    semantic_matcher,
    skill_comparator,
    ats_scorer,
    resume_optimizer,
)

from backend.models.llm_client import LLMClient
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Single shared LLM client (lazy initialization)
_llm_client = None


def _get_llm_client():
    """Lazy initialization of shared LLM client instance."""
    global _llm_client
    if _llm_client is None:
        try:
            _llm_client = LLMClient()
            logger.info("LLM client initialized")
        except Exception as e:
            logger.warning("Failed to initialize LLM client: %s", e)
    return _llm_client


class ResumeAgent:
    """Extracts and parses resume content."""
    
    def process(self, resume_input: str | Any) -> Dict[str, Any]:
        """
        Parse and extract resume content.
        
        Args:
            resume_input: File path (str) or file-like object
        
        Returns:
            Dict with raw_text, clean_text, sections, and skills
        """
        try:
            # Extract text and sections
            if isinstance(resume_input, str):
                raw_text, sections = resume_parser.extract_from_path(resume_input)
            else:
                raw_text, sections = resume_parser.extract_from_uploaded(resume_input)
            
            # Clean and extract skills
            clean_text = resume_parser.clean_text(raw_text)
            skills = skill_extractor.extract_skills(raw_text)
            
            return {
                "raw_text": raw_text,
                "clean_text": clean_text,
                "sections": sections,
                "skills": skills,
            }
        except Exception as e:
            logger.exception("Resume processing failed: %s", e)
            raise


class JDAnalyzerAgent:
    """Analyzes and extracts requirements from job descriptions."""
    
    def process(self, jd_text: str) -> Dict[str, Any]:
        """
        Extract structured data from job description.
        
        Args:
            jd_text: Job description text
        
        Returns:
            Dict with requirements, parsed_skills, and seniority level
        """
        try:
            parsed = jd_analyzer.extract_requirements(jd_text)
            jd_skills = skill_extractor.extract_skills(jd_text)
            parsed["parsed_skills"] = jd_skills
            return parsed
        except Exception as e:
            logger.exception("Job description analysis failed: %s", e)
            return {"requirements": {}, "parsed_skills": [], "error": str(e)}


class MatcherAgent:
    """Matches resume to job description using semantic and skill comparison."""
    
    @staticmethod
    def _extract_resume_skills(resume_data: Dict[str, Any]) -> list:
        """Extract and flatten resume skills."""
        skills_dict = resume_data.get("skills", {})
        resume_skills = skills_dict.get("skills", [])
        resume_tools = skills_dict.get("tools", [])
        return list(set(resume_skills + resume_tools))  # deduplicate
    
    def match(self, resume_data: Dict[str, Any], jd_text: str) -> Dict[str, Any]:
        """
        Perform multi-faceted matching between resume and job description.
        
        Args:
            resume_data: Parsed resume from ResumeAgent
            jd_text: Job description text
        
        Returns:
            Dict with semantic matching and skill comparison results
        """
        try:
            # Get resume text (prefer cleaned version)
            resume_text = resume_data.get("clean_text") or resume_data.get("raw_text", "")
            
            # Semantic matching
            semantic_result = semantic_matcher.semantic_similarity_resume_jd(
                resume_text, jd_text
            )
            
            # Extract skills once and reuse
            resume_skill_list = self._extract_resume_skills(resume_data)
            jd_skills = skill_extractor.extract_skills(jd_text).get("skills", [])
            
            # Skill comparison
            embed_fn = semantic_matcher.get_embed_fn_if_available()
            skill_comp = skill_comparator.compare_skills(
                resume_skill_list, jd_skills, embed_fn=embed_fn
            )
            
            return {
                "semantic": semantic_result,
                "skill_comparator": skill_comp
            }
        except Exception as e:
            logger.exception("Resume-JD matching failed: %s", e)
            return {"semantic": {}, "skill_comparator": {}, "error": str(e)}


class ScoringAgent:
    """Computes ATS-like scores for resume-JD matching."""
    
    @staticmethod
    def _extract_jd_keywords(jd_data: Dict[str, Any]) -> Optional[list]:
        """Extract keywords from JD data structure."""
        # Try multiple paths to find skills
        return (
            jd_data.get("requirements", {}).get("required_skills")
            or jd_data.get("parsed_skills", {}).get("skills")
            or jd_data.get("parsed_skills", []) if isinstance(jd_data.get("parsed_skills"), list) else None
        )
    
    def score(
        self, 
        resume_data: Dict[str, Any], 
        jd_data: Dict[str, Any], 
        matcher_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute comprehensive ATS score.
        
        Args:
            resume_data: Parsed resume data
            jd_data: Parsed job description data
            matcher_result: Matching results
        
        Returns:
            ATS scoring breakdown with components and final score
        """
        try:
            # Extract scores from matcher
            semantic_score = matcher_result.get("semantic", {}).get("overall_score", 0.0)
            skill_fit_index = matcher_result.get("skill_comparator", {}).get("skill_fit_index", 0.0)
            
            # Extract JD keywords and text
            jd_keywords = self._extract_jd_keywords(jd_data)
            jd_text = (
                jd_data.get("requirements", {}).get("raw_text")
                or jd_data.get("raw_text", "")
            )
            
            # Get embedding function if available
            embed_fn = semantic_matcher.get_embed_fn_if_available()
            
            # Score the application
            score_output = ats_scorer.score_application(
                resume_text=resume_data.get("raw_text", ""),
                jd_text=jd_text,
                semantic_score=semantic_score,
                skill_fit_index=skill_fit_index,
                jd_keywords=jd_keywords,
                embed_fn=embed_fn
            )
            return score_output
        except Exception as e:
            logger.exception("ATS scoring failed: %s", e)
            return {"ats": {"final_score": 0}, "raw_signals": {}, "error": str(e)}


class OptimizationAgent:
    """Optimizes resume for better JD matching using LLM."""
    
    def __init__(self):
        self.llm = _get_llm_client()
    
    @staticmethod
    def _extract_jd_content(jd_data: Dict[str, Any]) -> str:
        """Extract best available JD content."""
        return (
            jd_data.get("requirements")
            or jd_data.get("raw_text")
            or jd_data.get("parsed_skills")
            or ""
        )
    
    def optimize(
        self, 
        resume_data: Dict[str, Any], 
        jd_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimized resume tailored to job description.
        
        Args:
            resume_data: Parsed resume data
            jd_data: Parsed job description data
        
        Returns:
            Dict with optimized_resume, suggested_keywords, and changelog
        """
        try:
            resume_text = resume_data.get("raw_text", "")
            jd_content = self._extract_jd_content(jd_data)
            
            optimized = resume_optimizer.optimize_resume_text(resume_text, jd_content)
            return optimized
        except Exception as e:
            logger.exception("Resume optimization failed: %s", e)
            return {"error": str(e)}
