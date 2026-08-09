"""
배치 공고 분석 시스템
여러 공고를 자동으로 처리하고 결과를 저장
"""
import argparse
import os
import sys
from typing import List
from dotenv import load_dotenv
from matcher import JobMatcher
from utils import save_analysis_result
from config import MATCH_THRESHOLD, GEMINI_MODEL, MY_PROFILE, setup_logger
from api import search_jobs_by_query

# .env 파일 로드
load_dotenv()

# 로거 설정
logger = setup_logger('batch_matcher', log_file='logs/batch_matcher.log')


class BatchMatcher:
    """배치 공고 매칭 처리"""

    def __init__(self, api_key: str):
        self.matcher = JobMatcher(api_key)
        self.results = []

    def process_job(self, job_id: str) -> dict:
        """단일 공고 처리"""
        logger.info(f"\n{'=' * 60}")
        logger.info(f"📋 공고 ID {job_id} 분석 중...")
        logger.info('=' * 60)

        try:
            # 1. 요구사항 추출
            logger.info("🔍 1단계: 공고 요구사항 추출 중...")
            job_requirement, match_result = self.matcher.analyze(job_id)

            logger.info("✅ 요구사항 추출 완료")
            logger.info(f"  - 필요 기술: {', '.join(job_requirement.skills[:5])}")
            logger.info(f"  - 경력: {job_requirement.experience_years}년")
            logger.info(f"  - 키워드: {', '.join(job_requirement.keywords[:3])}")

            # 2. 매칭 분석
            logger.info("\n🎯 2단계: 스킬 매칭 분석 완료")
            logger.info(f"📊 매칭 점수: {match_result.score}점")
            logger.info(f"✅ 매칭되는 스킬: {', '.join(match_result.matched_skills) if match_result.matched_skills else '없음'}")
            logger.info(f"❌ 부족한 스킬: {', '.join(match_result.missing_skills) if match_result.missing_skills else '없음'}")

            # 3. 임계값 판단
            is_recommended = match_result.score >= MATCH_THRESHOLD
            if is_recommended:
                logger.info(f"\n🎉 추천! (임계값: {MATCH_THRESHOLD}점 이상)")
            else:
                logger.info(f"\n⏭️  건너뛰기 (임계값: {MATCH_THRESHOLD}점 미만)")

            # 4. 결과 저장
            logger.info("\n💾 분석 결과 저장 중...")
            saved_path = save_analysis_result(
                job_id=job_id,
                job_requirement=job_requirement,
                match_result=match_result,
                model_name=GEMINI_MODEL,
                profile=MY_PROFILE
            )
            logger.info(f"✅ 저장 완료: {saved_path}")

            return {
                "job_id": job_id,
                "status": "success",
                "score": match_result.score,
                "recommended": is_recommended,
                "saved_path": saved_path
            }

        except Exception as e:
            logger.error(f"\n❌ 에러 발생: {str(e)}", exc_info=True)
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }

    def process_batch(self, job_ids: List[str]) -> List[dict]:
        """여러 공고 배치 처리"""
        logger.info(f"\n🚀 배치 처리 시작: 총 {len(job_ids)}개 공고")
        logger.info("=" * 60)

        results = []
        for idx, job_id in enumerate(job_ids, 1):
            logger.info(f"\n진행: [{idx}/{len(job_ids)}]")
            result = self.process_job(job_id)
            results.append(result)

        # 요약 출력
        self._print_summary(results)

        return results

    def _print_summary(self, results: List[dict]):
        """배치 처리 결과 요약"""
        logger.info("\n\n" + "=" * 60)
        logger.info("📊 배치 처리 완료 요약")
        logger.info("=" * 60)

        total = len(results)
        success = sum(1 for r in results if r["status"] == "success")
        failed = total - success
        recommended = sum(1 for r in results if r.get("recommended", False))

        logger.info(f"\n전체: {total}개")
        logger.info(f"✅ 성공: {success}개")
        logger.info(f"❌ 실패: {failed}개")
        logger.info(f"🎉 추천: {recommended}개\n")

        if recommended > 0:
            logger.info("추천 공고 목록:")
            for r in results:
                if r.get("recommended"):
                    logger.info(f"  - Job {r['job_id']}: {r['score']}점")


def main():
    parser = argparse.ArgumentParser(description="배치 공고 매칭 시스템")
    parser.add_argument(
        "--job-ids",
        type=str,
        help="쉼표로 구분된 공고 ID 리스트 (예: 365200,365201,365202)"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="공고 ID 리스트가 담긴 파일 (한 줄에 하나씩)"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="검색 키워드 (예: 백엔드, AI, mlops)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="검색 결과 개수 (기본: 12)"
    )

    args = parser.parse_args()

    # 공고 ID 리스트 파싱
    job_ids = []
    if args.job_ids:
        job_ids = [jid.strip() for jid in args.job_ids.split(",")]
    elif args.input:
        if not os.path.exists(args.input):
            logger.error(f"❌ 파일을 찾을 수 없습니다: {args.input}")
            sys.exit(1)
        with open(args.input, 'r') as f:
            job_ids = [line.strip() for line in f if line.strip()]
    elif args.query:
        logger.info(f"🔍 '{args.query}' 검색 중... (최대 {args.limit}개)")
        job_ids = search_jobs_by_query(query=args.query, limit=args.limit)
        if not job_ids:
            logger.error(f"❌ 검색 결과가 없습니다.")
            sys.exit(1)
        logger.info(f"✅ {len(job_ids)}개 공고 발견: {', '.join(job_ids[:5])}{'...' if len(job_ids) > 5 else ''}")
    else:
        parser.print_help()
        sys.exit(1)

    if not job_ids:
        logger.error("❌ 공고 ID가 없습니다.")
        sys.exit(1)

    # API 키 확인
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("❌ GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        sys.exit(1)

    # 배치 처리 실행
    batch_matcher = BatchMatcher(api_key)
    batch_matcher.process_batch(job_ids)


if __name__ == "__main__":
    main()
