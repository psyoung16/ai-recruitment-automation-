"""
유틸리티 함수들
"""
import json
from datetime import datetime
from pathlib import Path
from models import JobRequirement, MatchResult


def save_analysis_result(
    job_id: str,
    job_requirement: JobRequirement,
    match_result: MatchResult,
    model_name: str,
    profile: str,
    output_dir: str = "output"
):
    """
    분석 결과를 JSON 파일로 저장합니다.

    Args:
        job_id: 채용공고 ID
        job_requirement: 추출된 요구사항
        match_result: 매칭 결과
        model_name: 사용한 AI 모델명
        profile: 사용자 프로필
        output_dir: 출력 디렉토리
    """
    # 출력 디렉토리 생성
    Path(output_dir).mkdir(exist_ok=True)

    # 현재 시간
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

    # 파일명: job_<jobid>_<timestamp>.json
    filename = f"job_{job_id}_{timestamp_str}.json"
    filepath = Path(output_dir) / filename

    # 결과 데이터 구성
    result_data = {
        "metadata": {
            "job_id": job_id,
            "analyzed_at": timestamp.isoformat(),
            "model": model_name,
            "profile": profile.strip(),
        },
        "job_requirement": {
            "skills": job_requirement.skills,
            "experience_years": job_requirement.experience_years,
            "keywords": job_requirement.keywords,
        },
        "match_result": {
            "score": match_result.score,
            "matched_skills": match_result.matched_skills,
            "missing_skills": match_result.missing_skills,
            "reason": match_result.reason,
        }
    }

    # JSON 파일로 저장
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    return str(filepath)
