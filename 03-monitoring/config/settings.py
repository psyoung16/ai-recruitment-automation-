"""
설정 및 프로필 정보
"""

# Primary LLM 모델 설정
GEMINI_MODEL = "gemini-3.6-flash"

# Fallback LLM 모델 설정 (Primary 모델 실패 시 사용)
# FALLBACK_MODEL_NAME = "gpt-5.6-luna"
FALLBACK_MODEL_NAME = "gpt-5-nano"
#gpt-5-nano
FALLBACK_API_KEY_ENV = "GPT_API_KEY"  # .env에서 읽을 키 이름
USE_FALLBACK = True  # Fallback 기능 활성화 여부

MY_PROFILE = """
- 언어: Java
- 프레임워크: Spring Boot, Spring MVC
- 데이터베이스: MySQL, PostgreSQL
- 경력: 3년차 백엔드 개발자
- 기타: Git, Docker 사용 가능
- 관심 도메인: 백엔드 API 개발, MSA
"""

# 매칭 점수 임계값
MATCH_THRESHOLD = 70
