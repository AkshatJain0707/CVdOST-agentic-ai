# backend/orchestration.py
"""
Orchestration engine for Resumate-Agentic-AI

Responsibilities:
- Coordinate agents (parsing, JD analysis, matching, scoring, optimization)
- Run steps asynchronously where it helps latency and responsiveness
- Provide robust error isolation so a failing step doesn't break the whole pipeline
- Save audit result to disk
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, Any, Optional

from backend.agents import (
    ResumeAgent,
    JDAnalyzerAgent,
    MatcherAgent,
    ScoringAgent,
    OptimizationAgent,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OrchestrationEngine:
    def __init__(self, results_dir: str = "data/results"):
        os.makedirs(results_dir, exist_ok=True)
        self.results_dir = results_dir

        # initialize agents (lightweight constructors)
        self.resume_agent = ResumeAgent()
        self.jd_agent = JDAnalyzerAgent()
        self.matcher_agent = MatcherAgent()
        self.scoring_agent = ScoringAgent()
        self.optimizer_agent = OptimizationAgent()

        # concurrency controls for LLM calls
        self._llm_semaphore = asyncio.Semaphore(2)  # tune based on your setup

    async def run(
        self,
        resume_path: str,
        jd_text: str,
        target_role: Optional[str] = None,
        save_result: bool = True,
    ) -> Dict[str, Any]:
        t0 = time.time()
        result: Dict[str, Any] = {
            "meta": {"started_at": int(t0), "target_role": target_role}
        }
        try:
            logger.info("Orchestration: start pipeline")

            # 1. Parse resume and analyze JD concurrently (both IO-bound)
            resume_task = asyncio.create_task(
                asyncio.to_thread(self.resume_agent.process, resume_path)
            )
            jd_task = asyncio.create_task(
                asyncio.to_thread(self.jd_agent.process, jd_text)
            )

            resume_data, jd_data = await asyncio.gather(resume_task, jd_task)
            result["resume"] = resume_data
            result["jd"] = jd_data

            # 2. Run matching and optimization concurrently (both use LLM semaphore)
            async def run_matcher():
                async with self._llm_semaphore:
                    return await asyncio.to_thread(
                        self.matcher_agent.match, resume_data, jd_text
                    )

            async def run_optimizer():
                try:
                    async with self._llm_semaphore:
                        return await asyncio.to_thread(
                            self.optimizer_agent.optimize, resume_data, jd_data
                        )
                except Exception as e:
                    logger.warning("Optimizer failed: %s", e)
                    return None

            matcher, optimized = await asyncio.gather(
                run_matcher(), run_optimizer()
            )
            result["matcher"] = matcher
            result["optimized_resume"] = optimized

            # 3. Scoring (depends on matcher output)
            score = await asyncio.to_thread(
                self.scoring_agent.score, resume_data, jd_data, matcher
            )
            result["ats"] = score

            result["meta"]["elapsed_s"] = round(time.time() - t0, 3)
            result["status"] = "success"
            logger.info("Orchestration: pipeline completed in %.2fs", time.time() - t0)

        except Exception as e:
            logger.exception("Orchestration pipeline failed: %s", e)
            result["status"] = "error"
            result["error"] = str(e)
            result["meta"]["elapsed_s"] = round(time.time() - t0, 3)

        # Save result (best-effort)
        if save_result:
            try:
                filename = f"resumate_result_{int(t0)}.json"
                path = os.path.join(self.results_dir, filename)
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(result, fh, indent=2)
                result["meta"]["result_path"] = path
            except Exception:
                logger.exception("Failed to write orchestration result to disk")

        return result
