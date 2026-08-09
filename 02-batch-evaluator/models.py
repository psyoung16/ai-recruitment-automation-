"""
Pydantic 모델 정의
"""
from pydantic import BaseModel, Field


class JobRequirement(BaseModel):
    """채용공고 요구사항"""
    skills: list[str] = Field(description="필요한 기술 스택 리스트")
    experience_years: int = Field(description="요구 경력 년수")
    keywords: list[str] = Field(description="핵심 키워드")


class MatchResult(BaseModel):
    """스킬 매칭 결과"""
    score: int = Field(description="0~100 매칭 점수")
    matched_skills: list[str] = Field(description="매칭되는 스킬")
    missing_skills: list[str] = Field(description="부족한 스킬")
    reason: str = Field(description="채점 이유 (한두 문장)")
