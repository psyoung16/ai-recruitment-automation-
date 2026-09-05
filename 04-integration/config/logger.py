"""
로깅 설정 모듈
"""
import logging
import sys
from pathlib import Path


def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    로거 설정

    Args:
        name (str): 로거 이름
        log_file (str): 로그 파일 경로 (None이면 파일 출력 안 함)
        level: 로그 레벨

    Returns:
        logging.Logger: 설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 중복 핸들러 방지
    if logger.handlers:
        return logger

    # 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (옵션)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# 기본 로거 (프로젝트 전역 사용)
default_logger = setup_logger('batch_evaluator', log_file='logs/batch_evaluator.log')
