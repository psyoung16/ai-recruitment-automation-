"""
공고 수집 시스템
검색 키워드로 공고를 수집하여 data/{query}/ 폴더에 저장
"""
import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from api import search_jobs_by_query, get_job_full_detail
from config import setup_logger

# .env 파일 로드
load_dotenv()

# 로거 설정
logger = setup_logger('collector', log_file='logs/collector.log')


class JobCollector:
    """공고 수집기"""

    def __init__(self, query: str, base_dir: str = "data"):
        self.query = query
        self.base_dir = Path(base_dir)
        self.query_dir = self.base_dir / query
        self.query_dir.mkdir(parents=True, exist_ok=True)

    def is_collected(self, job_id: str) -> bool:
        """이미 수집된 공고인지 확인"""
        file_path = self.query_dir / f"job_{job_id}.json"
        return file_path.exists()

    def save_job(self, job_id: str, job_data: dict) -> str:
        """공고 데이터 저장"""
        file_path = self.query_dir / f"job_{job_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, ensure_ascii=False, indent=2)

        return str(file_path)

    def collect_job(self, job_id: str) -> dict:
        """단일 공고 수집"""
        logger.info(f"📋 공고 ID {job_id} 수집 중...")

        # 중복 체크
        if self.is_collected(job_id):
            logger.info(f"⏭️  이미 수집됨: {job_id}")
            return {
                "job_id": job_id,
                "status": "skipped",
                "reason": "already_collected"
            }

        try:
            # API 호출
            job_data = get_job_full_detail(job_id)

            if not job_data:
                logger.warning(f"❌ 공고 데이터 없음: {job_id}")
                return {
                    "job_id": job_id,
                    "status": "failed",
                    "error": "empty_response"
                }

            # 저장
            saved_path = self.save_job(job_id, job_data)
            logger.info(f"✅ 저장 완료: {saved_path}")

            return {
                "job_id": job_id,
                "status": "success",
                "saved_path": saved_path
            }

        except Exception as e:
            logger.error(f"❌ 에러 발생 (job_id={job_id}): {str(e)}", exc_info=True)
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }

    def collect_batch(self, job_ids: list) -> list:
        """여러 공고 배치 수집"""
        logger.info(f"\n🚀 배치 수집 시작: '{self.query}' - 총 {len(job_ids)}개")
        logger.info(f"📁 저장 위치: {self.query_dir}")
        logger.info("=" * 60)

        results = []
        for idx, job_id in enumerate(job_ids, 1):
            logger.info(f"\n진행: [{idx}/{len(job_ids)}]")
            result = self.collect_job(job_id)
            results.append(result)

        # 요약
        self._print_summary(results)

        return results

    def _print_summary(self, results: list):
        """수집 결과 요약"""
        logger.info("\n\n" + "=" * 60)
        logger.info("📊 배치 수집 완료 요약")
        logger.info("=" * 60)

        total = len(results)
        success = sum(1 for r in results if r["status"] == "success")
        skipped = sum(1 for r in results if r["status"] == "skipped")
        failed = sum(1 for r in results if r["status"] == "failed")

        logger.info(f"\n전체: {total}개")
        logger.info(f"✅ 신규 수집: {success}개")
        logger.info(f"⏭️  중복 스킵: {skipped}개")
        logger.info(f"❌ 실패: {failed}개\n")

        if failed > 0:
            logger.info("실패한 공고:")
            for r in results:
                if r["status"] == "failed":
                    logger.info(f"  - Job {r['job_id']}: {r.get('error', 'unknown')}")


def main():
    parser = argparse.ArgumentParser(description="공고 수집 시스템")
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="검색 키워드 (예: 백엔드, AI, mlops)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="수집할 공고 개수 (기본: 12)"
    )

    args = parser.parse_args()

    # 공고 ID 검색
    logger.info(f"🔍 '{args.query}' 검색 중... (최대 {args.limit}개)")
    job_ids = search_jobs_by_query(query=args.query, limit=args.limit)

    if not job_ids:
        logger.error(f"❌ 검색 결과가 없습니다.")
        sys.exit(1)

    logger.info(f"✅ {len(job_ids)}개 공고 발견")

    # 수집 시작
    collector = JobCollector(query=args.query)
    collector.collect_batch(job_ids)


if __name__ == "__main__":
    main()
