"""
재시도 로직 처리 모듈
API 호출 실패 시 exponential backoff 전략으로 재시도
"""
import time
from typing import Callable, Any
from functools import wraps
from config import setup_logger

logger = setup_logger('retry_handler', log_file='logs/retry_handler.log')


class RateLimitError(Exception):
    """
    Rate limit 에러 발생 시 즉시 발생하는 예외

    재시도하지 않고 바로 fallback 모델로 전환해야 함
    """
    def __init__(self, original_error: Exception, function_name: str):
        self.original_error = original_error
        self.function_name = function_name
        super().__init__(
            f"{function_name} hit rate limit: {str(original_error)}"
        )

    def __str__(self):
        return f"RateLimit[{self.function_name}]: {str(self.original_error)[:200]}"


class RetryExhaustedError(Exception):
    """
    재시도를 모두 소진한 경우 발생하는 예외

    이 예외가 발생하면 fallback 모델로 전환을 고려해야 함
    """
    def __init__(self, original_error: Exception, attempts: int, function_name: str):
        self.original_error = original_error
        self.attempts = attempts
        self.function_name = function_name
        super().__init__(
            f"{function_name} failed after {attempts} retry attempts: {str(original_error)}"
        )

    def __str__(self):
        return f"RetryExhausted[{self.function_name}, {self.attempts}회 시도]: {str(self.original_error)}"


class RetryConfig:
    """재시도 설정"""
    MAX_ATTEMPTS = 3  # 최대 재시도 횟수
    BASE_DELAY = 2  # 기본 지연 시간 (초)
    MAX_DELAY = 60  # 최대 지연 시간 (초)
    EXPONENTIAL_BASE = 2  # 지수 증가 배수


def is_rate_limit_error(exception: Exception) -> bool:
    """
    Rate limit 에러인지 확인
    - 429 RESOURCE_EXHAUSTED
    - Quota exceeded
    """
    error_message = str(exception).lower()

    # Gemini API의 rate limit 관련 에러 메시지 패턴
    rate_limit_patterns = [
        '429',
        'resource_exhausted',
        'quota exceeded',
        'rate limit',
        'too many requests'
    ]

    return any(pattern in error_message for pattern in rate_limit_patterns)


def extract_retry_delay(exception: Exception) -> float:
    """
    에러 메시지에서 retry delay 추출
    예: "Please retry in 48.83571079s" -> 48.84
    """
    error_message = str(exception)

    # "retry in X.Xs" 또는 "retry in Xs" 패턴 찾기
    import re
    match = re.search(r'retry in ([\d.]+)s', error_message, re.IGNORECASE)

    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    return 0.0


def calculate_backoff_delay(attempt: int, suggested_delay: float = 0.0) -> float:
    """
    Exponential backoff 지연 시간 계산

    Args:
        attempt: 현재 시도 횟수 (1부터 시작)
        suggested_delay: API에서 제안한 지연 시간 (있으면 우선 사용)

    Returns:
        지연 시간 (초)
    """
    # API가 제안한 delay가 있으면 우선 사용
    if suggested_delay > 0:
        return min(suggested_delay, RetryConfig.MAX_DELAY)

    # Exponential backoff: 2^(attempt-1) * BASE_DELAY
    # attempt 1: 2초, attempt 2: 4초, attempt 3: 8초
    delay = (RetryConfig.EXPONENTIAL_BASE ** (attempt - 1)) * RetryConfig.BASE_DELAY

    return min(delay, RetryConfig.MAX_DELAY)


def retry_with_backoff(func: Callable) -> Callable:
    """
    Exponential backoff 재시도 데코레이터

    Usage:
        @retry_with_backoff
        def api_call():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        last_exception = None

        for attempt in range(1, RetryConfig.MAX_ATTEMPTS + 1):
            try:
                logger.info(f"🔄 {func.__name__} 호출 (시도 {attempt}/{RetryConfig.MAX_ATTEMPTS})")
                result = func(*args, **kwargs)

                if attempt > 1:
                    logger.info(f"✅ {func.__name__} 재시도 성공 (시도 {attempt})")

                return result

            except Exception as e:
                last_exception = e

                # Rate limit 에러면 재시도 없이 즉시 RateLimitError 발생
                if is_rate_limit_error(e):
                    logger.warning(
                        f"⚠️  {func.__name__} Rate limit 감지 → 재시도 없이 Fallback으로 전환\n"
                        f"   에러: {str(e)[:200]}"
                    )
                    raise RateLimitError(
                        original_error=e,
                        function_name=func.__name__
                    )

                # Rate limit 외 다른 에러는 재시도
                # 마지막 시도였으면 RetryExhaustedError 발생
                if attempt >= RetryConfig.MAX_ATTEMPTS:
                    logger.error(
                        f"❌ {func.__name__} 최종 실패 "
                        f"({RetryConfig.MAX_ATTEMPTS}번 시도 후 포기): {str(e)}"
                    )
                    raise RetryExhaustedError(
                        original_error=e,
                        attempts=RetryConfig.MAX_ATTEMPTS,
                        function_name=func.__name__
                    )

                # Retry delay 계산
                delay = calculate_backoff_delay(attempt)

                logger.warning(
                    f"⚠️  {func.__name__} 일시적 에러 발생 (시도 {attempt}/{RetryConfig.MAX_ATTEMPTS})\n"
                    f"   에러: {str(e)[:200]}\n"
                    f"   대기 시간: {delay:.2f}초\n"
                    f"   {delay:.2f}초 후 재시도..."
                )

                time.sleep(delay)

        # 이론상 여기 도달 불가 (위에서 raise 되어야 함)
        raise last_exception

    return wrapper


# 별도 함수로도 사용 가능
def retry_api_call(func: Callable, *args, **kwargs) -> Any:
    """
    함수를 재시도 로직과 함께 실행

    Usage:
        result = retry_api_call(api_function, arg1, arg2, kwarg1=value1)
    """
    decorated_func = retry_with_backoff(func)
    return decorated_func(*args, **kwargs)
