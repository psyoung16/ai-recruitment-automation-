# 📊 Evaluation (평가 시스템)

## 🎯 목적

매칭 시스템이 "얼마나 정확하게 공고를 추천하는가?"를 측정합니다.

---

## 📝 Ground Truth 작성 가이드

### Step 1: 템플릿 복사

```bash
cd evaluation
cp test_jobs_template.json test_jobs.json
```

### Step 2: 공고 읽기 및 라벨링

각 공고를 **직접 읽고** 다음 3가지로 분류:

| 분류 | 기준             | 예시 |
|------|----------------|------|
| **apply** | 지원 추천          | Django + 3년차 백엔드 + MSA 관심 → 완벽 매칭 |
| **no_apply** | 지원 비추천         | AI/ML 전문가 구인 → 스킬 불일치 |
| **borderline** | 애매함 (평가 제외 가능) | 일부 스킬 매칭하나 경력/도메인 애매 |

### Step 3: 라벨링 예시

```json
{
  "apply": [
    {
      "job_id": "284183",
      "company": "코드잇",
      "position": "백엔드 엔지니어",
      "url": "https://www.wanted.co.kr/wd/284183",
      "label_reason": "Kotlin + Spring + Kubernetes 사용. 3년차 백엔드 요구사항 정확히 일치. MSA 환경 경험 가능",
      "my_expected_score": 80,
      "key_match": ["Spring", "Kubernetes", "AWS", "3년차"],
      "concerns": ["Kotlin 미경험 (하지만 Java 경험으로 학습 가능)"]
    }
  ],

  "no_apply": [
    {
      "job_id": "231846",
      "company": "위레이저",
      "position": "백엔드 개발자",
      "url": "https://www.wanted.co.kr/wd/231846",
      "label_reason": "하드웨어/펌웨어 도메인, C/C++ 위주. 백엔드 웹 개발과 거리 멀음",
      "my_expected_score": 20,
      "key_mismatch": ["C/C++", "펌웨어", "하드웨어"],
      "why_not": "도메인 완전 불일치"
    }
  ]
}
```

### Step 4: 점수 매기기 (선택)

- **70-100점**: apply (추천)
- **0-69점**: no_apply (비추천)
- **my_expected_score**는 선택사항 (MAE 계산용)

---

## 🚀 평가 실행

### 1. 분석 먼저 실행

```bash
# Ground Truth 작성 후, 시스템으로 분석
python batch_matcher.py --query "백엔드-eval"
```

### 2. 평가 실행

```bash
python evaluation/evaluate.py
# 또는 커스텀 옵션으로
python evaluation/evaluate.py --query "백엔드-eval" --test-jobs evaluation/test_jobs.json
```

### 3. 결과 확인

평가가 완료되면 자동으로 2가지 형식의 리포트가 생성됩니다:

**콘솔 출력 (요약):**
```
📊 Evaluation Report - eval_20260812_132049
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: 2026-08-12 13:20:49
🔍 Query: 백엔드-eval
🤖 Model: gemini-3.6-flash

📈 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Jobs:      10
Evaluated:       5 (borderline 5개 제외)

Accuracy:        60.0% (3/5)
Precision:       0.0%
Recall:          0.0%
F1-Score:        0.000
MAE:             19.2점

🎯 Confusion Matrix
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
True Positive:   0 ✅
False Positive:  0 ⚠️  (잘못 추천)
True Negative:   3 ✅
False Negative:  2 ❌ (놓친 공고)

🔍 Failure Cases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Job 284183 - 코드잇
   Error Type: FALSE_NEGATIVE
   GT: apply / Pred: no_apply
   Score: 75 → 35 (-40점)

2. Job 300610 - 와탭랩스
   Error Type: FALSE_NEGATIVE
   GT: apply / Pred: no_apply
   Score: 80 → 45 (-35점)
```

**파일 출력:**
- `evaluation/reports/eval_YYYYMMDD_HHMMSS.json` - 구조화된 JSON (대시보드 연동용)
- `evaluation/reports/eval_YYYYMMDD_HHMMSS.md` - 마크다운 리포트 (사람이 읽기 편함)
- `evaluation/reports/latest.json` - 최신 결과 심볼릭 링크

---

## 📊 평가 메트릭

| 메트릭 | 의미 | 목표 |
|--------|------|------|
| **Accuracy** | 전체 정확도 | 85% 이상 |
| **Precision** | 추천한 것 중 실제 좋은 공고 비율 | 90% 이상 (FP 최소화) |
| **Recall** | 좋은 공고 중 추천된 비율 | 80% 이상 |
| **MAE** | 점수 평균 절대 오차 | 10점 이하 |

**우선순위:**
1. **Precision** (가장 중요) - 잘못 추천하면 안 됨
2. **Recall** - 좋은 공고 놓치는 것은 덜 치명적
3. **MAE** - 점수 정확도는 보조 지표

---

## 📂 파일 구조

```
evaluation/
├── README.md                       # 이 파일
├── test_jobs_template.json         # 템플릿
├── test_jobs.json                  # Ground Truth (직접 작성)
├── evaluate.py                     # 평가 스크립트
└── reports/                        # 평가 결과 저장
    ├── eval_2026-08-12.json
    └── eval_2026-08-12.md
```

---

## 💡 Tips

### 라벨링 시 주의사항

1. **감정 배제**: "회사가 좋아 보인다" ✗ → "스킬이 매칭된다" ✓
2. **프로필 기준**: 내 프로필(Python, Java, Django, Spring Boot, 3년차)에 맞춰 판단
3. **애매하면 borderline**: 확신 없으면 borderline으로 분류
4. **일관성 유지**: 비슷한 공고는 비슷한 기준으로 판단

### 빠른 라벨링 전략

```bash
# 공고별로 핵심만 확인
1. 요구 기술 스택 (Django/Spring 있는가?)
2. 경력 요구사항 (3년차 적합한가?)
3. 도메인 (백엔드 웹 개발인가? 아니면 AI/하드웨어?)

→ 3가지 모두 맞으면 apply
→ 1가지라도 크게 안 맞으면 no_apply
→ 애매하면 borderline
```

---

## 🔄 회귀 테스트

프롬프트 변경 후 성능 비교:

```bash
# 베이스라인 저장
python evaluation/evaluate.py --save-baseline v1

# 프롬프트 수정 (llm/base.py)

# 재평가 및 비교
python evaluation/evaluate.py --compare-baseline v1
```
