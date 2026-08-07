from google import genai
import json
import os
import sys
from dotenv import load_dotenv
from wanted_api import get_job_detail, get_job_list_from_api

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

    # LLM이 알아서 get_job_detail을 호출하고, 그 결과를 분석해서 JSON으로 정리
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"job_id={job_id} 공고를 get_job_detail 도구로 가져와서 분석해줘. "
                f"채용공고 본문에서 기술 스택(skills), 요구 경력 년수(experience_years), 핵심 키워드(keywords)를 추출해서 정리해줘.",
        config={
            "tools": tools,
            "response_mime_type": "application/json",
            "response_schema": response_schema,
            "automatic_function_calling": {"disable": False}
        }
    )

    # 결과 출력
    result = json.loads(response.text)
    print("✅ 분석 완료:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))