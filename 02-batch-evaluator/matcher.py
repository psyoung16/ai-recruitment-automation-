"""
단일 공고 분석 로직 (01-basic-matcher의 main.py 로직을 함수화)
"""
from google import genai
from models import JobRequirement, MatchResult
from config import MY_PROFILE, GEMINI_MODEL
from api import get_job_detail

# JSON 응답 스키마 정의
REQUIREMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "skills": {
            "type": "array",
            "items": {"type": "string"},
            "description": "필요한 기술 스택 리스트"
        },
        "experience_years": {
            "type": "integer",
            "description": "요구 경력 년수"
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "핵심 키워드"
        }
    },
    "required": ["skills", "experience_years", "keywords"]
}


class JobMatcher:
    """단일 공고 매칭 분석"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.tools = [get_job_detail]

    def extract_requirements(self, job_id: str) -> JobRequirement:
        """공고에서 요구사항 추출"""
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
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

    def match_profile(self, job_requirement: JobRequirement) -> MatchResult:
        """프로필과 매칭 분석"""
        match_prompt = f"""
아래는 채용공고에서 추출한 요구사항이고, 그 다음은 내 스킬 프로필이야.

요구사항:
{job_requirement.model_dump_json(indent=2)}

내 프로필:
{MY_PROFILE}

이 공고가 나한테 얼마나 적합한지 0~100점으로 채점하고,
매칭되는 스킬, 부족한 스킬, 채점 이유를 정리해줘.
"""

        match_schema = MatchResult.model_json_schema()

        match_response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=match_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": match_schema,
            },
        )

        return MatchResult.model_validate_json(match_response.text)

    def analyze(self, job_id: str) -> tuple[JobRequirement, MatchResult]:
        """공고 분석 전체 프로세스"""
        # 1. 요구사항 추출
        job_requirement = self.extract_requirements(job_id)

        # 2. 매칭 분석
        match_result = self.match_profile(job_requirement)

        return job_requirement, match_result
