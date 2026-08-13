"""
LLM 공통 프롬프트 및 스키마
"""
from models import JobRequirement
from config import MY_PROFILE

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


def build_requirement_extraction_prompt(job_detail: str) -> str:
    """요구사항 추출 프롬프트 생성"""
    return f"""채용공고 본문에서 기술 스택(skills), 요구 경력 년수(experience_years), 핵심 키워드(keywords)를 추출해서 정리해줘.

공고 내용:
{job_detail}

다음 JSON 형식으로 응답해줘:
{{
  "skills": ["기술1", "기술2", ...],
  "experience_years": 숫자,
  "keywords": ["키워드1", "키워드2", ...]
}}"""


def build_matching_prompt(job_requirement: JobRequirement) -> str:
    """매칭 분석 프롬프트 생성"""
    return f"""아래는 채용공고에서 추출한 요구사항이고, 그 다음은 내 스킬 프로필이야.

요구사항:
{job_requirement.model_dump_json(indent=2)}

내 프로필:
{MY_PROFILE}

이 공고가 나한테 얼마나 적합한지 0~100점으로 채점하고,
매칭되는 스킬, 부족한 스킬, 채점 이유를 정리해줘.

다음 JSON 형식으로 응답해줘:
{{
  "score": 숫자,
  "matched_skills": ["스킬1", "스킬2", ...],
  "missing_skills": ["스킬1", "스킬2", ...],
  "reason": "채점 이유"
}}"""
