# 🔄 배치 자동화 + Evaluation 시스템

> 단일 공고 분석을 넘어, 여러 공고를 자동으로 처리하고 시스템의 정확도를 측정합니다.

## 💡 02-batch-evaluator

**프로덕션 레벨의 배치 분석 & 평가 시스템 - "돌아간다" → "쓸만하다"로 전환**

1. **2단계 파이프라인**: 수집과 분석 분리로 독립 실행 및 재처리 가능
2. **정량적 평가 시스템 (Evaluation)**: 매칭 정확도를 측정하고 문서화
3. **에러 핸들링 & 재시도**: 실패를 다루는 프로덕션 레벨 설계
4. **Logging & 모듈화**: 관측 가능한 시스템 구조

## 🔄 시스템 흐름도

### 2단계 파이프라인 (수집 → 분석 분리)

```
1단계: 공고 수집
검색 → API 호출 → data/{query}/job_*.json 저장


2단계: 공고 분석 (핵심) ⭐
─────────────────────────────────────
data/{query}/ 읽기
    ↓
각 공고 분석 (LLM API)
    ├─ 요구사항 추출 (Function Calling: get_job_detail)
    └─ 스킬 매칭 분석 (Structured Output: JSON Schema)
    ↓
중복 체크 (이미 분석됨 → 스킵)
    ↓
실패 시 자동 복구 ✅
    ├─ Rate limit(429) → 즉시 Fallback 모델 전환
    └─ 일반 에러 → 재시도 후 Fallback 전환
        ├─ Exponential backoff (2초→4초→8초)
        └─ 최대 3번 재시도
    ↓
output/{query}/job_*_analyzed.json 저장


3단계: Evaluation ⭐
─────────────────────────────────────
Ground Truth 로드 (apply/borderline/no_apply)
    ↓
분석 결과 로드 (output/{query}/)
    ↓
예측 vs 실제 비교 (borderline 제외)
    ↓
메트릭 계산 (Accuracy, Precision, Recall, F1, MAE)
    ↓
리포트 생성 (JSON + Markdown)
```

## 📊 Evaluation 시스템

**목표:** "돌아간다" → "쓸만하다" 검증

### 평가 가능한 방법들

| 평가 항목 | 설명 | 측정 방법 | 중요도 |
|---------|------|---------|--------|
| **1. End-to-End 정확도** | 최종 추천 여부가 맞는가? | Ground Truth와 비교 | ⭐⭐⭐ 가장 중요 |
| **2. 점수 정확도** | 0-100점이 실제와 일치하는가? | MAE, RMSE | ⭐⭐⭐ |
| **3. 스킬 추출 품질** | 공고에서 스킬을 제대로 뽑았는가? | Precision/Recall | ⭐⭐ |
| **4. 경력 해석 정확도** | "3년 이상"을 제대로 이해하는가? | Exact Match | ⭐⭐ |
| **5. 임계값 타당성** | 70점이 적절한 기준인가? | ROC Curve, F1 최적화 | ⭐⭐ |
| **6. 모델 일관성** | 같은 공고를 여러 번 돌려도 같은가? | Standard Deviation | ⭐ |
| **7. 모델 간 일치도** | Gemini vs GPT 점수가 비슷한가? | Cohen's Kappa | ⭐ |

### 선택한 방법

- **End-to-End 정확도** (Accuracy, Precision, Recall, F1) - 사용자 관점에서 가장 중요
- **점수 정확도** (MAE) - 추천 순서 검증용
- **실패 케이스 분석** - 프롬프트 개선 방향 도출

### 실행 결과

- **Accuracy**: 60% (3/5) - borderline 5개 제외
- **False Negative**: 2건 (좋은 공고를 놓침)
  - 코드잇: Kotlin 미경험 과대 페널티 (-40점)
  - 와탭랩스: 인프라 역량 과소평가 (-35점)
- **개선 방향**: 유사 기술 스택 가중치 조정, 신입 포지션 학습 의지 고려

**자세한 내용:** `evaluation/README.md` 참고


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

### 3. Evaluation 시스템 ✅
```bash
# 실행 방법 및 상세 결과는 evaluation/README.md 참고
python evaluation/evaluate.py
```

### 3. 에러 핸들링 ✅
- **자동 재시도**: Exponential backoff (2초→4초→8초)
- **Fallback LLM 전환**: Primary 실패 시 다른 모델로 자동 전환
- **중복 분석 방지**: 이미 처리된 공고는 자동 스킵

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
├── collector.py               # 1단계: 공고 수집
├── batch_matcher.py           # 2단계: 공고 분석
├── matcher.py                 # LLM 모델 조율 (Primary ↔ Fallback)
├── retry_handler.py           # 재시도 로직
├── api/                       # 원티드 API
├── llm/                       # LLM 어댑터 (gemini, openai)
├── config/                    # 설정 & 로깅
├── evaluation/                # 평가 시스템 ✅
│   ├── evaluate.py           # 평가 스크립트
│   ├── test_jobs.json        # Ground Truth
│   └── reports/              # 평가 결과 (JSON + Markdown)
├── data/                      # 수집된 공고 (*.json)
├── output/                    # 분석 결과 (*_analyzed.json)
└── logs/                      # 실행 로그
```


## 🚀 설치 및 실행

### 1. 패키지 설치
```bash
pip install google-genai openai python-dotenv requests pydantic tenacity schedule slack-sdk
```

### 2. 환경변수 설정
```bash
# Primary 모델 (Gemini)
GEMINI_API_KEY=your_gemini_api_key

# Fallback 모델 (OpenAI) - 선택사항
OPENAI_API_KEY=your_openai_api_key

# Slack 알림 (TODO) - 선택사항
SLACK_WEBHOOK_URL=your_slack_webhook
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

### 5. Evaluation 실행
```bash
# 실행 방법 및 결과 해석은 evaluation/README.md 참고
python evaluation/evaluate.py
```

## 🔄 다음 단계 (03-monitoring)

- Grafana + Prometheus 모니터링
- 멀티 플랫폼 크롤링
- DB 기반 데이터 관리


