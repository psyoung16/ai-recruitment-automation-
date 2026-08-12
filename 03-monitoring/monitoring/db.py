"""
PostgreSQL 데이터베이스 연결 및 저장 헬퍼
"""
import os
import psycopg2
from psycopg2.extras import Json
from typing import Optional
from datetime import datetime


def get_db_connection():
    """DB 연결 생성"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'jobmatcher'),
        user=os.getenv('DB_USER', 'jobmatcher'),
        password=os.getenv('DB_PASSWORD', 'jobmatcher123')
    )


def save_analyzed_job(
    job_id: str,
    query: str,
    company: Optional[str],
    position: Optional[str],
    score: int,
    recommended: bool,
    matched_skills: list,
    missing_skills: list,
    reason: str,
    model: str
) -> bool:
    """
    분석된 공고 정보를 DB에 저장

    Args:
        job_id: 공고 ID
        query: 검색 키워드
        company: 회사명
        position: 포지션명
        score: 매칭 점수
        recommended: 추천 여부
        matched_skills: 매칭된 스킬 목록
        missing_skills: 부족한 스킬 목록
        reason: 추천/비추천 이유
        model: 사용된 모델명

    Returns:
        성공 여부
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # UPSERT (INSERT ... ON CONFLICT UPDATE)
        cursor.execute("""
            INSERT INTO analyzed_jobs (
                job_id, query, company, position, score,
                recommended, matched_skills, missing_skills, reason, model, analyzed_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (job_id) DO UPDATE SET
                query = EXCLUDED.query,
                company = EXCLUDED.company,
                position = EXCLUDED.position,
                score = EXCLUDED.score,
                recommended = EXCLUDED.recommended,
                matched_skills = EXCLUDED.matched_skills,
                missing_skills = EXCLUDED.missing_skills,
                reason = EXCLUDED.reason,
                model = EXCLUDED.model,
                analyzed_at = EXCLUDED.analyzed_at
        """, (
            job_id,
            query,
            company,
            position,
            score,
            recommended,
            Json(matched_skills),
            Json(missing_skills),
            reason,
            model,
            datetime.now()
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"DB 저장 실패: {e}")
        return False