#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🚀 Starting Job Matcher Services..."

# 1. Docker Compose 서비스 시작
echo "1️⃣  Starting Docker Compose services..."
docker-compose up -d

# 2. 컨테이너 상태 확인
echo "2️⃣  Checking container status..."
sleep 3
docker ps --filter "name=job-matcher" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 3. 메트릭 서버 시작
echo "3️⃣  Starting metrics server..."
if pgrep -f "python.*metrics_server.py" > /dev/null; then
    echo "   ⚠️  Metrics server already running"
else
    nohup python metrics_server.py > logs/metrics_server.log 2>&1 &
    echo "   ✅ Metrics server started (PID: $!)"
fi

# 4. 헬스체크
echo "4️⃣  Health check..."
sleep 2

echo -n "   - Redis: "
if docker exec job-matcher-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌"
fi

echo -n "   - PostgreSQL: "
if docker exec job-matcher-postgres pg_isready -U matcher > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌"
fi

echo -n "   - Prometheus: "
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌"
fi

echo -n "   - Grafana: "
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌"
fi

echo -n "   - Metrics Server: "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌"
fi

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Access URLs:"
echo "   - Grafana:    http://localhost:3000 (admin/admin)"
echo "   - Prometheus: http://localhost:9090"
echo "   - Metrics:    http://localhost:8000/metrics"
echo ""