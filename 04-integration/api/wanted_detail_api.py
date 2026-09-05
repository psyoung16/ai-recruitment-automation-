"""
원티드 채용공고 상세 정보 조회 API
"""
import requests
import logging

logger = logging.getLogger('batch_evaluator.api.detail')


def get_job_detail(job_id: str) -> str:
    """
    원티드 공고 상세 정보를 가져옵니다.

    Args:
        job_id (str): 채용공고 ID

    Returns:
        str: 공고 상세 요구사항 텍스트 (실패 시 빈 문자열)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.wanted.co.kr/'
    }

    try:
        resp = requests.get(
            f"https://www.wanted.co.kr/api/chaos/jobs/v4/{job_id}/details",
            headers=headers
        )
        resp.raise_for_status()
        data = resp.json()

        # API 응답 구조: data.job.detail.requirements
        requirements = data.get("data", {}).get("job", {}).get("detail", {}).get("requirements", "")

        return requirements

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"❌ 공고를 찾을 수 없습니다 (job_id={job_id})")
        else:
            logger.error(f"❌ HTTP 에러 (job_id={job_id}): {e}")
        return ""

    except Exception as e:
        logger.error(f"❌ 상세 정보 요청 실패 (job_id={job_id}): {e}", exc_info=True)
        return ""


def get_job_full_detail(job_id: str) -> dict:
    """
    원티드 공고의 전체 상세 정보를 가져옵니다.

    Args:
        job_id (str): 채용공고 ID

    Returns:
        dict: 공고 전체 데이터 (실패 시 빈 dict)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.wanted.co.kr/'
    }

    try:
        resp = requests.get(
            f"https://www.wanted.co.kr/api/chaos/jobs/v4/{job_id}/details",
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()

    except Exception as e:
        logger.error(f"❌ 상세 정보 요청 실패 (job_id={job_id}): {e}", exc_info=True)
        return {}
