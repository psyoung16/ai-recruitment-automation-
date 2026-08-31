#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# .env 파일 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env 파일이 없습니다. .env.example을 복사하여 .env를 생성하세요."
    exit 1
fi

echo "[$(date)] ========== 일일 배치 시작 =========="

# 1. 공고 수집
echo "[$(date)] 1. 공고 수집 중..."
IFS=',' read -ra KEYWORDS <<< "$SEARCH_KEYWORDS"
for keyword in "${KEYWORDS[@]}"; do
    # 앞뒤 공백 제거
    keyword=$(echo "$keyword" | xargs)
    echo "[$(date)] - 키워드: $keyword"
    python collector.py --query "$keyword" --limit 20
done

# 2. 배치 분석
echo "[$(date)] 2. 배치 분석 중..."
for keyword in "${KEYWORDS[@]}"; do
    keyword=$(echo "$keyword" | xargs)
    echo "[$(date)] - 분석: $keyword"
    python batch_matcher.py --query "$keyword"
done

# 3. Slack 알림
echo "[$(date)] 3. Slack 알림 발송..."
python slack_notifier.py  # 기본: 추천 공고 + 일일 요약

echo "[$(date)] ========== 일일 배치 완료 =========="