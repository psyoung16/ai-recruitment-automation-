"""
Gemini 모델 어댑터
"""
import google.generativeai as genai
from models import JobRequirement, MatchResult
from config import GEMINI_MODEL
from api import get_job_detail
from retry_handler import retry_with_backoff
from llm.base import REQUIREMENT_SCHEMA, build_matching_prompt


class GeminiModel:
    """Gemini 모델 어댑터"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = GEMINI_MODEL
        self.tools = [get_job_detail]

    @retry_with_backoff
    def extract_requirements(self, job_id: str) -> JobRequirement:
        """요구사항 추출"""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=self.tools,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": REQUIREMENT_SCHEMA,
            }
        )

        response = model.generate_content(
            f"job_id={job_id} 공고를 get_job_detail 도구로 가져와서 분석해줘. "
            f"채용공고 본문에서 기술 스택(skills), 요구 경력 년수(experience_years), 핵심 키워드(keywords)를 추출해서 정리해줘."
        )
        return JobRequirement.model_validate_json(response.text)

    @retry_with_backoff
    def match_profile(self, job_requirement: JobRequirement) -> MatchResult:
        """매칭 분석"""
        prompt = build_matching_prompt(job_requirement)
        schema = MatchResult.model_json_schema()

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            }
        )

        response = model.generate_content(prompt)
        return MatchResult.model_validate_json(response.text)
