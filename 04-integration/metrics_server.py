"""
Prometheus 메트릭 서버
/metrics 엔드포인트를 제공하여 Prometheus가 메트릭을 수집할 수 있도록 합니다.
"""
from flask import Flask, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge, Info
from monitoring.db import get_db_connection
import platform
import sys

app = Flask(__name__)

# 시스템 정보 설정 (독립적으로)
system_info = Info('job_matcher_system', 'Job Matcher system information')
system_info.info({
    'version': '0.3.0',
    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    'platform': platform.system(),
    'hostname': platform.node()
})

# DB 기반 메트릭 정의
jobs_analyzed = Gauge(
    'jobs_analyzed_total',
    'Total jobs analyzed from database',
    ['query']
)

jobs_recommended = Gauge(
    'jobs_recommended_total',
    'Total recommended jobs from database',
    ['query']
)

avg_matching_score = Gauge(
    'job_avg_score',
    'Average matching score from database',
    ['query']
)


def update_db_metrics():
    """DB에서 메트릭 업데이트"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 쿼리별 통계
        cursor.execute("""
            SELECT
                query,
                COUNT(*) as total,
                SUM(CASE WHEN recommended THEN 1 ELSE 0 END) as recommended,
                AVG(score) as avg_score
            FROM analyzed_jobs
            GROUP BY query
        """)

        for row in cursor.fetchall():
            query, total, recommended, avg_score = row
            jobs_analyzed.labels(query=query).set(total)
            jobs_recommended.labels(query=query).set(recommended or 0)
            avg_matching_score.labels(query=query).set(avg_score or 0)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"메트릭 업데이트 실패: {e}")


@app.route('/metrics')
def metrics():
    """
    Prometheus 메트릭 엔드포인트
    """
    # DB에서 최신 메트릭 업데이트
    update_db_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route('/health')
def health():
    """
    헬스체크 엔드포인트
    """
    return {'status': 'healthy', 'service': 'job-matcher-metrics'}, 200


@app.route('/')
def index():
    """
    루트 엔드포인트
    """
    return {
        'service': 'Job Matcher Metrics Server',
        'version': '0.3.0',
        'endpoints': {
            '/metrics': 'Prometheus metrics',
            '/health': 'Health check'
        }
    }, 200


if __name__ == '__main__':
    print("🚀 Starting Metrics Server on http://localhost:8000")
    print("📊 Metrics available at http://localhost:8000/metrics")
    app.run(host='0.0.0.0', port=8000, debug=False)
