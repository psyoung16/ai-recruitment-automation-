"""
배치 공고 분석 시스템
data/{query}/ 폴더의 수집된 공고를 분석하여 output/{query}/에 저장
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from matcher import JobMatcher
from config import MATCH_THRESHOLD, GEMINI_MODEL, MY_PROFILE, setup_logger
from monitoring.db import save_analyzed_job
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge, push_to_gateway

# .env 파일 로드
load_dotenv()

# 로거 설정
logger = setup_logger('batch_matcher', log_file='logs/batch_matcher.log')


class BatchMatcher:
    """배치 공고 매칭 처리"""

    def __init__(self, api_key: str, query: str, base_data_dir: str = "data", base_output_dir: str = "output"):
        self.matcher = JobMatcher(api_key)
        self.query = query
        self.data_dir = Path(base_data_dir) / query
        self.output_dir = Path(base_output_dir) / query
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Push Gateway용 독립적인 레지스트리
        self.registry = CollectorRegistry()

        # 메트릭 정의
        self.jobs_analyzed_total = Counter(
            'batch_jobs_analyzed_total',
            'Total number of jobs analyzed in batch',
            ['query'],
            registry=self.registry
        )
        self.jobs_recommended_total = Counter(
            'batch_jobs_recommended_total',
            'Total number of recommended jobs in batch',
            ['query'],
            registry=self.registry
        )
        self.job_matching_score = Histogram(
            'batch_job_matching_score',
            'Job matching score distribution in batch',
            ['query'],
            buckets=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100),
            registry=self.registry
        )
        self.jobs_processing = Gauge(
            'batch_jobs_processing',
            'Number of jobs currently being processed',
            registry=self.registry
        )
        self.batch_duration_seconds = Histogram(
            'batch_duration_seconds',
            'Batch processing duration in seconds',
            ['query'],
            registry=self.registry
        )

    def is_analyzed(self, job_id: str) -> bool:
        """이미 분석된 공고인지 확인"""
        file_path = self.output_dir / f"job_{job_id}_analyzed.json"
        return file_path.exists()

    def get_collected_jobs(self) -> List[str]:
        """수집된 공고 파일 목록 가져오기"""
        if not self.data_dir.exists():
            logger.error(f"❌ 데이터 폴더가 없습니다: {self.data_dir}")
            return []

        job_files = list(self.data_dir.glob("job_*.json"))
        job_ids = [f.stem.replace("job_", "") for f in job_files]

        logger.info(f"📁 수집된 공고: {len(job_ids)}개 ({self.data_dir})")
        return job_ids

    def get_job_detail(self, job_id: str) -> dict:
        """공고 상세 정보 읽기"""
        job_file = self.data_dir / f"job_{job_id}.json"
        if not job_file.exists():
            return {}

        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"공고 파일 읽기 실패 ({job_id}): {e}")
            return {}

    def process_job(self, job_id: str) -> dict:
        """단일 공고 분석"""
        logger.info(f"\n{'=' * 60}")
        logger.info(f"📋 공고 ID {job_id} 분석 중...")
        logger.info('=' * 60)

        # 처리 중인 공고 수 증가
        self.jobs_processing.inc()

        # 중복 체크
        if self.is_analyzed(job_id):
            logger.info(f"⏭️  이미 분석됨: {job_id}")
            self.jobs_processing.dec()
            return {
                "job_id": job_id,
                "status": "skipped",
                "reason": "already_analyzed"
            }

        try:
            # 공고 상세 정보 읽기
            job_detail = self.get_job_detail(job_id)
            company = job_detail.get('data', {}).get('job', {}).get('company', {}).get('name', '')
            position = job_detail.get('data', {}).get('job', {}).get('detail', {}).get('position', '')

            # 1. 분석
            logger.info("🔍 공고 분석 중...")
            job_requirement, match_result = self.matcher.analyze(job_id)

            logger.info("✅ 분석 완료")
            logger.info(f"  - 필요 기술: {', '.join(job_requirement.skills[:5])}")
            logger.info(f"  - 경력: {job_requirement.experience_years}년")
            logger.info(f"  - 키워드: {', '.join(job_requirement.keywords[:3])}")

            # 2. 매칭 결과
            logger.info(f"\n📊 매칭 점수: {match_result.score}점")
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
            result_data = {
                "job_id": job_id,
                "query": self.query,
                "requirement": job_requirement.model_dump(),
                "match_result": match_result.model_dump(),
                "recommended": is_recommended,
                "model": self.matcher.last_used_model,  # 실제 사용된 모델
                "profile": MY_PROFILE
            }

            saved_path = self.output_dir / f"job_{job_id}_analyzed.json"
            with open(saved_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 저장 완료: {saved_path}")

            # DB에 저장
            logger.info("💾 DB에 저장 중...")
            db_saved = save_analyzed_job(
                job_id=job_id,
                query=self.query,
                company=company,
                position=position,
                score=match_result.score,
                recommended=is_recommended,
                matched_skills=match_result.matched_skills,
                missing_skills=match_result.missing_skills,
                reason=match_result.reason,
                model=self.matcher.last_used_model
            )

            if db_saved:
                logger.info("✅ DB 저장 완료")
            else:
                logger.warning("⚠️  DB 저장 실패 (계속 진행)")

            # 메트릭 기록
            self.jobs_analyzed_total.labels(query=self.query).inc()
            self.job_matching_score.labels(query=self.query).observe(match_result.score)
            if is_recommended:
                self.jobs_recommended_total.labels(query=self.query).inc()

            # 처리 중인 공고 수 감소
            self.jobs_processing.dec()

            return {
                "job_id": job_id,
                "status": "success",
                "score": match_result.score,
                "recommended": is_recommended,
                "saved_path": str(saved_path)
            }

        except Exception as e:
            logger.error(f"\n❌ 에러 발생: {str(e)}", exc_info=True)
            self.jobs_processing.dec()
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }

    def process_batch(self, job_ids: List[str]) -> List[dict]:
        """여러 공고 배치 처리"""
        logger.info(f"\n🚀 배치 처리 시작: '{self.query}' - 총 {len(job_ids)}개")
        logger.info(f"📂 출력 위치: {self.output_dir}")
        logger.info("=" * 60)

        start_time = time.time()

        results = []
        for idx, job_id in enumerate(job_ids, 1):
            logger.info(f"\n진행: [{idx}/{len(job_ids)}]")
            result = self.process_job(job_id)
            results.append(result)

        # 배치 처리 시간 기록
        duration = time.time() - start_time
        self.batch_duration_seconds.labels(query=self.query).observe(duration)

        # 요약 출력
        self._print_summary(results)

        # Push Gateway로 메트릭 전송
        self._push_metrics()

        return results

    def _push_metrics(self):
        """Push Gateway로 메트릭 전송"""
        try:
            push_gateway_url = os.getenv('PUSH_GATEWAY_URL', 'localhost:9091')
            logger.info(f"\n📤 Push Gateway로 메트릭 전송 중... ({push_gateway_url})")

            push_to_gateway(
                push_gateway_url,
                job='batch_matcher',
                registry=self.registry
            )

            logger.info("✅ 메트릭 전송 완료")
        except Exception as e:
            logger.warning(f"⚠️  메트릭 전송 실패: {e}")

    def _print_summary(self, results: List[dict]):
        """배치 처리 결과 요약"""
        logger.info("\n\n" + "=" * 60)
        logger.info("📊 배치 처리 완료 요약")
        logger.info("=" * 60)

        total = len(results)
        success = sum(1 for r in results if r["status"] == "success")
        skipped = sum(1 for r in results if r["status"] == "skipped")
        failed = sum(1 for r in results if r["status"] == "failed")
        recommended = sum(1 for r in results if r.get("recommended", False))

        logger.info(f"\n전체: {total}개")
        logger.info(f"✅ 신규 분석: {success}개")
        logger.info(f"⏭️  중복 스킵: {skipped}개")
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
        "--query",
        type=str,
        required=True,
        help="검색 키워드 (data/{query}/ 폴더에서 읽기)"
    )

    args = parser.parse_args()

    # API 키 확인
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("❌ GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        sys.exit(1)

    # 배치 처리 실행
    batch_matcher = BatchMatcher(api_key, query=args.query)

    # 수집된 공고 가져오기
    job_ids = batch_matcher.get_collected_jobs()

    if not job_ids:
        logger.error("❌ 수집된 공고가 없습니다.")
        logger.info(f"먼저 공고를 수집하세요: python collector.py --query \"{args.query}\"")
        sys.exit(1)

    # 분석 시작
    batch_matcher.process_batch(job_ids)


if __name__ == "__main__":
    main()
