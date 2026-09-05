#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🛑 Stopping Job Matcher Services..."

# 1. 메트릭 서버 종료
echo "1️⃣  Stopping metrics server..."
if pgrep -f "python.*metrics_server.py" > /dev/null; then
    pkill -f "python.*metrics_server.py"
    echo "   ✅ Metrics server stopped"
else
    echo "   ⚠️  Metrics server not running"
fi

# 2. Docker Compose 서비스 종료
echo "2️⃣  Stopping Docker Compose services..."
docker-compose down

echo ""
echo "✅ All services stopped!"
echo ""