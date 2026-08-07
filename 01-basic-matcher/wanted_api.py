"""
원티드 API 호출 관련 함수들
"""
import requests


def get_job_list_from_api(query='mlops', offset=0, limit=100):
    """
    Wanted API에서 채용공고 목록을 가져옵니다.

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
        print(f"❌ API 요청 실패: {e}")
        return None


def get_job_detail(job_id: str) -> str:
    """
    원티드 공고 상세 정보를 가져옵니다.

    Args:
        job_id (str): 채용공고 ID

    Returns:
        str: 공고 상세 요구사항 텍스트
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
        return data.get("data", {}).get("job", {}).get("detail", {}).get("requirements", "")
    except Exception as e:
        print(f"❌ 상세 정보 요청 실패 (job_id={job_id}): {e}")
        return ""

"""예시 response는 wanted_api_example.json 참고 """