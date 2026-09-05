"""
원티드 채용공고 목록 조회 API
"""
import requests
import logging
from typing import List, Optional

logger = logging.getLogger('batch_evaluator.api.list')


def get_job_list(query: str = 'mlops', offset: int = 0, limit: int = 100) -> Optional[dict]:
    """
    Wanted API에서 채용공고 목록을 가져옵니다. (position 엔드포인트)

    Args:
        query (str): 검색 키워드
        offset (int): 시작 위치
        limit (int): 가져올 개수 (최대 100)

    Returns:
        dict: API 응답 데이터 (실패 시 None)
    """
    base_url = "https://www.wanted.co.kr/api/chaos/search/v1/position"

    params = {
        'query': query,
        'country': 'kr',
        'years': [1, 7],
        'locations': ['seoul.all', 'incheon.all', 'gyeonggi.all'],
        'sort': 'job.recommend_order',
        'limit': limit,
        'offset': offset
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.wanted.co.kr/'
    }

    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"❌ API 요청 실패: {e}", exc_info=True)
        return None


def search_jobs_by_query(query: str, offset: int = 0, limit: int = 12) -> List[str]:
    """
    키워드로 채용공고 검색하여 job_id 리스트 반환

    Args:
        query (str): 검색 키워드 (예: "백엔드", "AI", "mlops")
        offset (int): 시작 위치
        limit (int): 가져올 개수

    Returns:
        List[str]: job_id 리스트
    """
    data = get_job_list(query=query, offset=offset, limit=limit)

    if not data:
        return []

    job_ids = []

    # API 응답 구조에서 job_id 추출
    # 실제 응답 구조에 따라 조정 필요
    if 'data' in data:
        for item in data['data']:
            if 'id' in item:
                job_ids.append(str(item['id']))

    return job_ids


def extract_job_ids_from_response(response_data: dict) -> List[str]:
    """
    API 응답에서 job_id만 추출하는 헬퍼 함수

    Args:
        response_data (dict): API 응답 데이터

    Returns:
        List[str]: job_id 리스트
    """
    job_ids = []

    if not response_data or 'data' not in response_data:
        return job_ids

    for item in response_data['data']:
        # 여러 가능한 필드명 시도
        job_id = None

        if 'id' in item:
            job_id = item['id']
        elif 'position_id' in item:
            job_id = item['position_id']
        elif 'position' in item and isinstance(item['position'], dict):
            if 'id' in item['position']:
                job_id = item['position']['id']

        if job_id:
            job_ids.append(str(job_id))

    return job_ids
