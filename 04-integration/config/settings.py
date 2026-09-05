"""
설정 및 프로필 정보
"""
import os

# Primary LLM 모델 설정
GEMINI_MODEL = "gemini-3.6-flash"

# Fallback LLM 모델 설정 (Primary 모델 실패 시 사용)
FALLBACK_MODEL_NAME = "gpt-5-nano"
FALLBACK_API_KEY_ENV = "GPT_API_KEY"  # .env에서 읽을 키 이름
USE_FALLBACK = True  # Fallback 기능 활성화 여부

# 프로필 정보 (환경변수에서 로드)
def get_profile_from_env():
    """환경변수에서 프로필 정보를 읽어와 문자열로 구성"""
    language = os.getenv('MY_PROFILE_LANGUAGE', 'Java')
    frameworks = os.getenv('MY_PROFILE_FRAMEWORKS', 'Spring Boot')
    database = os.getenv('MY_PROFILE_DATABASE', 'MySQL, PostgreSQL')
    experience = os.getenv('MY_PROFILE_EXPERIENCE_YEARS', '3')
    interests = os.getenv('MY_PROFILE_INTERESTS', '백엔드 API 개발')

    return f"""
- 언어: {language}
- 프레임워크: {frameworks}
- 데이터베이스: {database}
- 경력: {experience}년차 백엔드 개발자
- 관심 도메인: {interests}
"""

MY_PROFILE = get_profile_from_env()

# 매칭 점수 임계값
MATCH_THRESHOLD = 70
