# 🔄 배치 자동화 + Evaluation 시스템

> 단일 공고 분석을 넘어, 여러 공고를 자동으로 처리하고 시스템의 정확도를 측정합니다.

## 💡 01-basic-matcher와의 차이점

### 01-basic-matcher
- 수동으로 공고 ID 입력
- 한 번에 하나씩 분석
- "잘 되는 것 같다"는 느낌

### 02-batch-evaluator
- 여러 공고 자동 배치 처리
- 에러 핸들링 & 재시도
- **정량적 평가**: "실제로 얼마나 정확한가?"

## 🎯 핵심 목표

**"돌아간다" → "쓸만하다"로 전환**

1. **Evaluation 시스템**: 매칭 정확도를 측정하고 문서화
2. **배치 자동화**: 여러 공고를 안정적으로 처리
3. **에러 핸들링**: 실패를 다루는 프로덕션 레벨 설계

## 🔄 시스템 흐름도

### 2단계 파이프라인 (수집 → 분석 분리)

```
1단계: 공고 수집
검색 → API 호출 → data/{query}/job_*.json 저장


2단계: 공고 분석 (핵심) ⭐
─────────────────────────────────────
data/{query}/ 읽기
    ↓
각 공고 분석 (Gemini API)
    ├─ 요구사항 추출
    └─ 스킬 매칭 분석
    ↓
중복 체크 (이미 분석됨 → 스킵)
    ↓
실패 시 재시도 로직 (TODO)
    ├─ Retry with exponential backoff
    ├─ Rate limiting 처리
    └─ 최종 실패 시 로그
    ↓
output/{query}/job_*_analyzed.json 저장


3단계: Evaluation (다음 구현) ⭐
─────────────────────────────────────
테스트셋 로드 (추천/비추천 공고)
    ↓
각 공고 분석
    ↓
예측 vs 실제 비교
    ↓
정확도 계산 & 리포트 생성
```

## 🏗️ 주요 기능

### 1. 공고 수집 (collector.py)
```bash
# 검색 키워드로 공고 수집
python collector.py --query "백엔드" --limit 20

# 결과: data/백엔드/job_*.json 생성
# - 중복 자동 스킵
# - 실패한 공고는 로그 기록
```

### 2. 공고 분석 (batch_matcher.py)
```bash
# 수집된 공고 분석
python batch_matcher.py --query "백엔드"

# 결과: output/백엔드/job_*_analyzed.json 생성
# - 매칭 점수, 추천 여부, 분석 상세 정보
```

### 3. Evaluation 시스템 (TODO)
```python
# 테스트셋으로 정확도 측정
python evaluate.py --test-set evaluation/test_jobs.json

# 출력 예시:
# ✅ 정확도: 85%
# ✅ 추천 공고 정확도: 90% (9/10)
# ❌ 비추천 공고 정확도: 80% (8/10)
#
# 실패 케이스:
# - Job 365200: 예측 75점 (추천) / 실제: 비추천
#   이유: 경력 요구사항 과대평가
```

### 3. 에러 핸들링
- API 실패 시 자동 재시도 (exponential backoff)
- Rate limiting 처리
- 중복 분석 방지 (캐싱)

### 4. 자동 스케줄링
```bash
# 매일 오전 9시 신규 공고 자동 스캔
python scheduler.py --cron "0 9 * * *"
```

### 5. Slack 알림
```
🎯 매칭도 높은 공고 발견!

📋 백엔드 개발자 - 토스페이먼츠
💯 매칭 점수: 88점
🔗 https://www.wanted.co.kr/wd/365200

✅ Python, Django, AWS
❌ Kotlin (보완 필요)
```

## 📂 프로젝트 구조

```
02-batch-evaluator/
├── README.md
├── api/                       # 외부 API 모듈
│   ├── __init__.py
│   ├── wanted_list_api.py     # 공고 목록 검색
│   └── wanted_detail_api.py   # 공고 상세 조회
├── config/                    # 설정 모듈
│   ├── __init__.py
│   ├── settings.py            # 프로필, 임계값 등
│   └── logger.py              # 로깅 설정
├── utils/                     # 유틸리티 모듈
│   ├── __init__.py
│   └── file_handler.py        # 파일 저장
├── collector.py               # 1단계: 공고 수집
├── batch_matcher.py           # 2단계: 공고 분석
├── matcher.py                 # 단일 공고 분석 로직
├── models.py                  # 데이터 모델
├── scheduler.py               # 자동 스케줄링 (TODO)
├── retry_handler.py           # 재시도 로직 (TODO)
├── slack_notifier.py          # Slack 알림 (TODO)
├── evaluation/                # (TODO)
│   ├── evaluate.py            # Evaluation 실행
│   ├── test_jobs.json         # 테스트셋
│   └── metrics.py             # 정확도 계산
├── data/                      # 수집된 원본 공고
│   ├── 백엔드/
│   │   └── job_*.json
│   └── AI/
│       └── job_*.json
├── output/                    # 분석 결과
│   ├── 백엔드/
│   │   └── job_*_analyzed.json
│   └── AI/
│       └── job_*_analyzed.json
└── logs/                      # 실행 로그
    ├── collector.log
    └── batch_matcher.log
```

## 🎓 핵심 학습 포인트

### 1. Evaluation 설계
```python
# test_jobs.json 구조
{
  "recommended": [  # 추천 공고
    {"job_id": 365200, "expected_score_range": [70, 100]},
    {"job_id": 365201, "expected_score_range": [75, 100]}
  ],
  "not_recommended": [  # 비추천 공고
    {"job_id": 365300, "expected_score_range": [0, 69]},
    {"job_id": 365301, "expected_score_range": [0, 69]}
  ]
}
```

### 2. 재시도 로직 (Exponential Backoff)
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def analyze_job(job_id):
    # API 호출
    pass
```

### 3. 회귀 테스트
```python
# 프롬프트 변경 전후 비교
python evaluate.py --compare baseline_v1 current_v2

# 출력:
# Baseline v1: 85% 정확도
# Current v2:  88% 정확도 (+3%p 개선)
```

## 🚀 설치 및 실행

### 1. 패키지 설치
```bash
pip install google-genai python-dotenv requests pydantic tenacity schedule slack-sdk
```

### 2. 환경변수 설정
```
GEMINI_API_KEY=your_api_key
SLACK_WEBHOOK_URL=your_slack_webhook  # (선택사항)
```

### 3. 공고 수집
```bash
# 검색 키워드로 공고 수집
python collector.py --query "백엔드" --limit 20

# 결과 확인
ls data/백엔드/
# → job_365200.json, job_365201.json, ...
```

### 4. 공고 분석
```bash
# 수집된 공고 분석
python batch_matcher.py --query "백엔드"

# 결과 확인
ls output/백엔드/
# → job_365200_analyzed.json, ...
```

### 5. Evaluation 실행 (TODO)
```bash
python evaluation/evaluate.py --query "백엔드"
```

## 📊 Evaluation 결과 예시

```
=== Evaluation Report ===
날짜: 2026-08-09
테스트셋: 20개 (추천 10개, 비추천 10개)

전체 정확도: 85% (17/20)

추천 공고:
  ✅ 정확도: 90% (9/10)
  ❌ False Negative: 1개 (추천인데 비추천으로 예측)

비추천 공고:
  ✅ 정확도: 80% (8/10)
  ❌ False Positive: 2개 (비추천인데 추천으로 예측)

실패 케이스 분석:
1. Job 365200 (False Negative)
   - 예측: 68점 (비추천)
   - 실제: 추천
   - 원인: "3년차 경력" 요구사항을 너무 엄격하게 해석

2. Job 365300 (False Positive)
   - 예측: 72점 (추천)
   - 실제: 비추천
   - 원인: "Kotlin" 필수 요구사항을 선택사항으로 오해

개선 방향:
- 경력 요구사항 해석 로직 개선
- 필수 vs 우대 요구사항 구분 강화
```

## 🔄 다음 단계 (03-monitoring)

- Grafana + Prometheus 모니터링
- 멀티 플랫폼 크롤링
- DB 기반 데이터 관리

---

## 💡 이 프로젝트로 얻을 수 있는 경험

✅ **Evaluation 설계**: AI 시스템의 품질을 정량적으로 측정
✅ **회귀 테스트**: 프롬프트 변경 시 성능 추적
✅ **에러 핸들링**: 재시도 로직, Rate limiting
✅ **배치 처리**: 대량 데이터 안정적 처리
✅ **"돌아간다"와 "쓸만하다"의 차이를 측정하고 개선**
