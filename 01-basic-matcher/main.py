from google import genai
from google.genai import types
import json
import os
import sys
from dotenv import load_dotenv
from wanted_api import get_job_detail, get_job_list_from_api
from models import JobRequirement, MatchResult
from config import MY_PROFILE, MATCH_THRESHOLD, GEMINI_MODEL
from utils import save_analysis_result

# .env 파일 로드
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

client = genai.Client(api_key=GEMINI_API_KEY)

# Gemini function calling용 도구 정의
tools = [get_job_detail]

# JSON 응답 스키마 정의 (선택사항 - 더 엄격한 출력 제어)
response_schema = {
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

if __name__ == "__main__":
    # 커맨드라인 인자로 job_id 받기
    if len(sys.argv) < 2:
        print("사용법: python3 main.py <job_id>")
        print("예시: python3 main.py 123456")
        sys.exit(1)

    job_id = sys.argv[1]
    print(f"📋 공고 ID {job_id} 분석 중...\n")

    # STEP 1: AI Agent로 공고 요구사항 추출
    print("🔍 1단계: 공고 요구사항 추출 중...")
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"job_id={job_id} 공고를 get_job_detail 도구로 가져와서 분석해줘. "
                f"채용공고 본문에서 기술 스택(skills), 요구 경력 년수(experience_years), 핵심 키워드(keywords)를 추출해서 정리해줘.",
        config={
            "tools": tools,
            "response_mime_type": "application/json",
            "response_schema": response_schema,
            "automatic_function_calling": {"disable": False}
        }
    )

    # 요구사항 파싱
    job_requirement = JobRequirement.model_validate_json(response.text)
    print("✅ 요구사항 추출 완료\n")
    print(f"  - 필요 기술: {', '.join(job_requirement.skills[:5])}")
    print(f"  - 경력: {job_requirement.experience_years}년")
    print(f"  - 키워드: {', '.join(job_requirement.keywords[:3])}\n")

    # STEP 2: 스킬 매칭 분석
    print("🎯 2단계: 스킬 매칭 분석 중...")
    match_prompt = f"""
아래는 채용공고에서 추출한 요구사항이고, 그 다음은 내 스킬 프로필이야.

요구사항:
{job_requirement.model_dump_json(indent=2)}

내 프로필:
{MY_PROFILE}

이 공고가 나한테 얼마나 적합한지 0~100점으로 채점하고,
매칭되는 스킬, 부족한 스킬, 채점 이유를 정리해줘.
"""

    # Pydantic 모델을 JSON Schema로 변환
    match_schema = MatchResult.model_json_schema()

    match_response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=match_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": match_schema,
        },
    )

    # 매칭 결과 파싱
    match = MatchResult.model_validate_json(match_response.text)
    print("✅ 매칭 분석 완료\n")

    # STEP 3: 결과 출력
    print("=" * 60)
    print(f"📊 매칭 점수: {match.score}점")
    print("=" * 60)
    print(f"\n✅ 매칭되는 스킬: {', '.join(match.matched_skills) if match.matched_skills else '없음'}")
    print(f"❌ 부족한 스킬: {', '.join(match.missing_skills) if match.missing_skills else '없음'}")
    print(f"\n💡 이유: {match.reason}\n")

    # STEP 4: 임계값 판단
    if match.score >= MATCH_THRESHOLD:
        print(f"🎉 추천! 이 공고는 {match.score}점으로 매칭됩니다.")
        print(f"   (임계값: {MATCH_THRESHOLD}점 이상)")
        # TODO: Slack 알림 등 추가 가능
    else:
        print(f"⏭️  건너뛰기. 매칭 점수가 낮습니다. ({match.score}점 < {MATCH_THRESHOLD}점)")

    # STEP 5: 결과 저장
    print("\n💾 분석 결과 저장 중...")
    saved_path = save_analysis_result(
        job_id=job_id,
        job_requirement=job_requirement,
        match_result=match,
        model_name=GEMINI_MODEL,
        profile=MY_PROFILE
    )
    print(f"✅ 저장 완료: {saved_path}\n")