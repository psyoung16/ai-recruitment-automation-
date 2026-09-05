#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🏥 Job Matcher Health Check"
echo "=============================="
echo ""

# 1. Docker 컨테이너 상태
echo "📦 Docker Containers:"
docker ps --filter "name=job-matcher" --format "   {{.Names}}: {{.Status}}" 2>/dev/null || echo "   ❌ Docker not running"
echo ""

# 2. 서비스 헬스체크
echo "🔍 Service Health:"

# Redis
echo -n "   - Redis (6379): "
if docker exec job-matcher-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ PONG"
else
    echo "❌ DOWN"
fi

# PostgreSQL
echo -n "   - PostgreSQL (5432): "
if docker exec job-matcher-postgres pg_isready -U matcher > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "❌ DOWN"
fi

# Prometheus
echo -n "   - Prometheus (9090): "
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ DOWN"
fi

# Grafana
echo -n "   - Grafana (3000): "
GRAFANA_STATUS=$(curl -s http://localhost:3000/api/health 2>/dev/null | grep -o '"database":"ok"' || echo "")
if [ -n "$GRAFANA_STATUS" ]; then
    echo "✅ Healthy"
else
    echo "❌ DOWN"
fi

# Metrics Server
echo -n "   - Metrics Server (8000): "
METRICS_STATUS=$(curl -s http://localhost:8000/health 2>/dev/null | grep -o '"status":"healthy"' || echo "")
if [ -n "$METRICS_STATUS" ]; then
    echo "✅ Healthy"
else
    echo "❌ DOWN"
fi

echo ""

# 3. 메트릭 서버 프로세스
echo "🔧 Processes:"
if pgrep -f "python.*metrics_server.py" > /dev/null; then
    PID=$(pgrep -f "python.*metrics_server.py")
    echo "   - Metrics Server: ✅ Running (PID: $PID)"
else
    echo "   - Metrics Server: ❌ Not running"
fi

echo ""

# 4. 디스크 사용량
echo "💾 Storage:"
echo "   - Data folder:"
du -sh data/ logs/ output/ 2>/dev/null | sed 's/^/     /'

echo ""

# 5. 최근 분석 통계
echo "📊 Recent Activity (Last 24h):"
if docker exec job-matcher-postgres psql -U matcher -d job_matcher -t -c "SELECT COUNT(*) FROM analyzed_jobs WHERE analyzed_at >= NOW() - INTERVAL '1 day'" 2>/dev/null | grep -q '[0-9]'; then
    JOBS=$(docker exec job-matcher-postgres psql -U matcher -d job_matcher -t -c "SELECT COUNT(*) FROM analyzed_jobs WHERE analyzed_at >= NOW() - INTERVAL '1 day'" 2>/dev/null | xargs)
    RECOMMENDED=$(docker exec job-matcher-postgres psql -U matcher -d job_matcher -t -c "SELECT COUNT(*) FROM analyzed_jobs WHERE analyzed_at >= NOW() - INTERVAL '1 day' AND recommended = true" 2>/dev/null | xargs)
    AVG_SCORE=$(docker exec job-matcher-postgres psql -U matcher -d job_matcher -t -c "SELECT ROUND(AVG(score), 1) FROM analyzed_jobs WHERE analyzed_at >= NOW() - INTERVAL '1 day'" 2>/dev/null | xargs)

    echo "   - Total analyzed: $JOBS jobs"
    echo "   - Recommended: $RECOMMENDED jobs"
    echo "   - Average score: $AVG_SCORE points"
else
    echo "   ❌ Cannot fetch statistics (DB not available)"
fi

echo ""
echo "=============================="