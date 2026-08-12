"""
OpenAI 모델 어댑터
"""
from openai import OpenAI
from models import JobRequirement, MatchResult
from config import FALLBACK_MODEL_NAME
from api import get_job_detail
from llm.base import build_requirement_extraction_prompt, build_matching_prompt


class OpenAIModel:
    """OpenAI 모델 어댑터"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model_name = FALLBACK_MODEL_NAME

    def extract_requirements(self, job_id: str) -> JobRequirement:
        """요구사항 추출"""
        job_detail = get_job_detail(job_id)
        if not job_detail:
            raise ValueError(f"공고 ID {job_id}의 상세 정보를 가져올 수 없습니다.")

        prompt = build_requirement_extraction_prompt(job_detail)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return JobRequirement.model_validate_json(response.choices[0].message.content)

    def match_profile(self, job_requirement: JobRequirement) -> MatchResult:
        """매칭 분석"""
        prompt = build_matching_prompt(job_requirement)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return MatchResult.model_validate_json(response.choices[0].message.content)
