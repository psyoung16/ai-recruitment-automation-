"""
Slack 알림 봇 (Bot Token 방식)
"""
import os
import sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from monitoring.db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

# Slack 설정
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')
HIGH_SCORE = int(os.getenv('NOTIFICATION_HIGH_SCORE', 80))
MEDIUM_SCORE = int(os.getenv('NOTIFICATION_MEDIUM_SCORE', 70))

# Slack 클라이언트 초기화
client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None


def send_slack_message(blocks, text="새로운 알림이 도착했습니다.", channel=None):
    """Slack 메시지 전송 (Bot Token 방식)"""
    if not client:
        print("⚠️  SLACK_BOT_TOKEN이 설정되지 않았습니다.")
        return False

    if not channel:
        channel = SLACK_CHANNEL_ID

    if not channel:
        print("⚠️  SLACK_CHANNEL_ID가 설정되지 않았습니다.")
        return False

    try:
        response = client.chat_postMessage(
            channel=channel,
            text=text,  # 접근성을 위한 fallback 텍스트
            blocks=blocks
        )
        print(f"✅ Slack 메시지 전송 완료 (채널: {channel})")
        return response["ok"]
    except SlackApiError as e:
        print(f"❌ Slack 메시지 전송 실패: {e.response['error']}")
        return False


def notify_recommended_jobs():
    """추천 공고 알림 (recommended=true인 모든 공고)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 오늘 분석된 추천 공고 조회
        cursor.execute("""
            SELECT job_id, query, company, position, score, reason
            FROM analyzed_jobs
            WHERE analyzed_at >= NOW() - INTERVAL '1 day'
              AND recommended = true
            ORDER BY score DESC
            LIMIT 20
        """)

        jobs = cursor.fetchall()

        if not jobs:
            print("ℹ️  추천 공고가 없습니다.")
            cursor.close()
            conn.close()
            return

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "💼 오늘의 추천 채용공고"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{len(jobs)}개의 공고를 추천드립니다!*"}
            },
            {"type": "divider"}
        ]

        for job in jobs:
            job_id, query, company, position, score, reason = job
            url = f"https://www.wanted.co.kr/wd/{job_id}"

            # 점수에 따른 이모지
            if score >= 80:
                emoji = "🔥"
            elif score >= 70:
                emoji = "⭐"
            else:
                emoji = "✅"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{company}*\n"
                            f"📋 {position}\n"
                            f"🎯 매칭 점수: *{score}점*\n"
                            f"🔍 키워드: `{query}`\n"
                            f"💡 {reason[:150]}..."
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "공고 보기"},
                    "url": url,
                    "action_id": f"view_job_{job_id}"
                }
            })
            blocks.append({"type": "divider"})

        send_slack_message(blocks, text=f"💼 오늘의 추천 채용공고 {len(jobs)}개")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 추천 공고 알림 실패: {e}")


def notify_high_score_jobs():
    """고득점 공고 알림 (80점 이상)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 오늘 분석된 고득점 공고 조회
        cursor.execute("""
            SELECT job_id, query, company, position, score, reason
            FROM analyzed_jobs
            WHERE analyzed_at >= NOW() - INTERVAL '1 day'
              AND score >= %s
            ORDER BY score DESC
            LIMIT 10
        """, (HIGH_SCORE,))

        jobs = cursor.fetchall()

        if not jobs:
            print("ℹ️  고득점 공고가 없습니다.")
            cursor.close()
            conn.close()
            return

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🔥 오늘의 고득점 공고"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{len(jobs)}개의 고득점 공고를 발견했습니다!*"}
            },
            {"type": "divider"}
        ]

        for job in jobs:
            job_id, query, company, position, score, reason = job
            url = f"https://www.wanted.co.kr/wd/{job_id}"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{company}* - {position}\n"
                            f"🎯 매칭 점수: *{score}점*\n"
                            f"🔍 키워드: `{query}`\n"
                            f"💡 {reason[:100]}...\n"
                            f"🔗 <{url}|공고 보기>"
                }
            })
            blocks.append({"type": "divider"})

        send_slack_message(blocks, text=f"🔥 오늘의 고득점 공고 {len(jobs)}개")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 고득점 공고 알림 실패: {e}")


def notify_daily_summary():
    """일일 요약 알림"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 오늘 통계
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN recommended THEN 1 ELSE 0 END) as recommended,
                AVG(score) as avg_score,
                MAX(score) as max_score
            FROM analyzed_jobs
            WHERE analyzed_at >= NOW() - INTERVAL '1 day'
        """)

        row = cursor.fetchone()

        if not row or row[0] == 0:
            print("ℹ️  오늘 분석된 공고가 없습니다.")
            cursor.close()
            conn.close()
            return

        total, recommended, avg_score, max_score = row

        # 포맷팅 값 계산
        avg_score_text = f"{avg_score:.1f}" if avg_score else "0.0"

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📊 일일 분석 요약"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*총 분석:*\n{total}건"},
                    {"type": "mrkdwn", "text": f"*추천:*\n{recommended or 0}건"},
                    {"type": "mrkdwn", "text": f"*평균 점수:*\n{avg_score_text}점"},
                    {"type": "mrkdwn", "text": f"*최고 점수:*\n{max_score or 0}점"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📈 <http://localhost:3000|Grafana 대시보드 보기>"
                }
            }
        ]

        send_slack_message(blocks, text=f"📊 일일 분석 요약 (총 {total}건)")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌일일 요약 알림 실패: {e}")


if __name__ == '__main__':
    if '--summary' in sys.argv:
        print("📊 일일 요약 알림 전송...")
        notify_daily_summary()
    elif '--high-score' in sys.argv:
        print("🔥 고득점 공고 알림 전송...")
        notify_high_score_jobs()
    elif '--recommended' in sys.argv:
        print("💼 추천 공고 알림 전송...")
        notify_recommended_jobs()
    else:
        # 기본: 추천 공고 + 일일 요약
        print("💼 추천 공고 알림 전송...")
        notify_recommended_jobs()
        print("\n📊 일일 요약 알림 전송...")
        notify_daily_summary()