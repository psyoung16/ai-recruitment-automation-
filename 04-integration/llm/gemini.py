"""
Gemini 모델 어댑터
"""
from google import genai
from models import JobRequirement, MatchResult
from config import GEMINI_MODEL
from api import get_job_detail
from retry_handler import retry_with_backoff
from llm.base import REQUIREMENT_SCHEMA, build_matching_prompt


class GeminiModel:
    """Gemini 모델 어댑터"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = GEMINI_MODEL
        self.tools = [get_job_detail]

    @retry_with_backoff
    def extract_requirements(self, job_id: str) -> JobRequirement:
        """요구사항 추출"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=f"job_id={job_id} 공고를 get_job_detail 도구로 가져와서 분석해줘. "
                    f"채용공고 본문에서 기술 스택(skills), 요구 경력 년수(experience_years), 핵심 키워드(keywords)를 추출해서 정리해줘.",
            config={
                "tools": self.tools,
                "response_mime_type": "application/json",
                "response_schema": REQUIREMENT_SCHEMA,
                "automatic_function_calling": {"disable": False}
            }
        )
        return JobRequirement.model_validate_json(response.text)

    @retry_with_backoff
    def match_profile(self, job_requirement: JobRequirement) -> MatchResult:
        """매칭 분석"""
        prompt = build_matching_prompt(job_requirement)
        schema = MatchResult.model_json_schema()

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )
        return MatchResult.model_validate_json(response.text)
