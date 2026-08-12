"""
단일 공고 분석 로직 (01-basic-matcher의 main.py 로직을 함수화)
"""
import os
from models import JobRequirement, MatchResult
from config import FALLBACK_MODEL_NAME, FALLBACK_API_KEY_ENV, USE_FALLBACK, setup_logger
from retry_handler import RateLimitError, RetryExhaustedError
from llm import GeminiModel, OpenAIModel

logger = setup_logger('matcher', log_file='logs/matcher.log')


class JobMatcher:
    """단일 공고 매칭 분석 - 모델 조율"""

    def __init__(self, api_key: str):
        self.primary = GeminiModel(api_key)
        self.fallback = None
        self.last_used_model = None  # 마지막 사용 모델 추적

        if USE_FALLBACK and FALLBACK_MODEL_NAME:
            fallback_api_key = os.getenv(FALLBACK_API_KEY_ENV)
            if fallback_api_key:
                self.fallback = OpenAIModel(fallback_api_key)
                logger.info(f"Fallback 모델 설정됨: {FALLBACK_MODEL_NAME}")
            else:
                logger.warning(f"Fallback API 키가 없습니다: {FALLBACK_API_KEY_ENV}")

    def _analyze_with_model(self, model, job_id: str) -> tuple[JobRequirement, MatchResult]:
        """특정 모델로 분석"""
        logger.info(f"모델: {model.model_name} 시도")

        job_requirement = model.extract_requirements(job_id)
        match_result = model.match_profile(job_requirement)

        self.last_used_model = model.model_name  # 사용한 모델 저장
        logger.info(f"✅ 모델: {model.model_name} 완료 (매칭 점수: {match_result.score}점)")
        return job_requirement, match_result

    def analyze(self, job_id: str) -> tuple[JobRequirement, MatchResult]:
        """공고 분석 전체 프로세스"""
        try:
            return self._analyze_with_model(self.primary, job_id)

        except (RateLimitError, RetryExhaustedError) as e:
            error_type = "Rate limit 감지" if isinstance(e, RateLimitError) else f"재시도 소진 ({e.attempts}회)"

            if self.fallback:
                logger.warning(f"❌ 모델: {self.primary.model_name} {error_type}: {e.function_name}")
                logger.warning(f"   원본 에러: {str(e.original_error)[:200]}")
                return self._analyze_with_model(self.fallback, job_id)
            else:
                logger.error(f"❌ Fallback 모델 미설정, {error_type}")
                raise e.original_error

        except Exception as e:
            logger.error(f"❌ 재시도 불가능한 에러 발생: {str(e)[:100]}")
            raise
