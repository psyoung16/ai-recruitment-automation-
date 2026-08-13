"""
Prometheus 메트릭 정의

참고: 이 파일의 메트릭들은 batch_matcher.py에서 import되지만,
프로세스가 분리되어 있어 실제 metrics_server.py에는 반영되지 않습니다.
metrics_server.py는 DB에서 직접 데이터를 읽어 메트릭을 생성합니다.

향후 개선 방안:
- Prometheus multiprocess mode 사용
- 또는 모든 메트릭을 DB 기반으로 통일
"""
from prometheus_client import Counter, Histogram, Gauge, Info

# ==================== 비즈니스 메트릭 ====================
# 아래 메트릭들은 batch 프로세스에서 사용되지만,
# 프로세스 메모리에만 존재하므로 Prometheus에 수집되지 않습니다.

# 분석 완료 공고 수
jobs_analyzed_total = Counter(
    'jobs_analyzed_total',
    'Total number of jobs analyzed',
    ['query']
)

# 매칭 점수 분포
job_matching_score = Histogram(
    'job_matching_score',
    'Job matching score distribution',
    ['query'],
    buckets=(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
)

# 추천 공고 수
jobs_recommended_total = Counter(
    'jobs_recommended_total',
    'Total number of recommended jobs',
    ['query']
)

# 처리 중인 공고 수 (게이지)
jobs_processing = Gauge(
    'jobs_processing',
    'Number of jobs currently being processed'
)

# 현재 실행 중인 배치 작업 수
batch_jobs_running = Gauge(
    'batch_jobs_running',
    'Number of batch jobs currently running'
)

# ==================== 시스템 메트릭 ====================

# 시스템 정보
system_info = Info(
    'job_matcher_system',
    'Job Matcher system information'
)