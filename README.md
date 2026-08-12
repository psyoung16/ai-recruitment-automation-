# 🎯 AI Job Matching Series

> AI Agent 기술을 단계별로 학습하며 실용적인 채용 자동화 시스템을 구축하는 프로젝트 시리즈

## 📚 프로젝트 목록

### [01-basic-matcher](./01-basic-matcher) ✅
**AI 채용공고 매칭 시스템 (기본편)**

원티드 채용공고를 AI가 자동으로 분석하고 내 프로필과의 매칭도를 계산합니다.

**핵심 학습:**
- Gemini Function Calling
- Multi-step Reasoning
- Structured Output (Pydantic)

**주요 기능:**
- 공고 ID 입력 시 자동 분석
- 스킬 매칭 점수 계산 (0-100점)
- JSON 결과 저장

---

### [02-batch-evaluator](./02-batch-evaluator) ✅
**배치 자동화 + Evaluation 시스템**

여러 공고를 자동으로 처리하고 시스템의 정확도를 측정합니다.

**핵심 학습:**
- LLM 어댑터 패턴 & Fallback 시스템
- Exponential Backoff 재시도 로직
- Ground Truth 기반 정량 평가
- 실패 케이스 분석

**주요 기능:**
- 2단계 파이프라인 (수집 → 분석 분리)
- Rate Limit 대응 자동 모델 전환
- Evaluation 시스템 (Accuracy, Precision, Recall, F1, MAE)
- JSON + Markdown 리포트 생성

---

## 단계별 구현 계획


```
01-basic-matcher (현재)
  ↓
  Function Calling 이해
  ↓
```

## 🛠️ 기술 스택

- **AI Framework:** Google Gemini
- **Language:** Python 3.9+
- **Data Validation:** Pydantic
- **API:** Wanted API, (추후 확장)

## 📂 프로젝트 구조

```
ai-job-matcher/
├── README.md                      # 👈 현재 파일
├── 01-basic-matcher/              # 기본 매칭 시스템 ✅
│   ├── README.md
│   ├── main.py
│   └── ...
├── 02-batch-evaluator/            # 배치 처리 & 평가 ✅
│   ├── README.md
│   ├── collector.py               # 공고 수집
│   ├── batch_matcher.py           # 배치 분석
│   ├── evaluation/                # 평가 시스템
│   │   ├── evaluate.py
│   │   ├── test_jobs.json
│   │   └── reports/
│   ├── llm/                       # LLM 어댑터
│   └── ...
```

## 🚀 시작하기

각 프로젝트 폴더의 README를 참고하세요.

## 🚀 Production으로 가는 길

### 1. **진짜 Multi-step Reasoning**
**현재:** 고정된 3단계 파이프라인 (상세조회 → 추출 → 매칭)

**목표:** LLM이 상황에 따라 다른 경로를 선택
- [ ] 공고 본문이 부족하면 회사 소개 페이지 추가 조회
- [ ] 매칭 점수가 애매하면(50~70점) 재검토 판단
- [ ] 컨텍스트 기반 의사결정 및 동적 도구 호출

### 2. **평가(Evaluation)** ✅
**"돌아간다" ≠ "쓸만하다"**

- [x] 정량적 평가: Ground Truth 기반 테스트셋 구축
- [x] 매칭 점수 정확도 측정 및 문서화 (Accuracy, Precision, Recall, F1, MAE)
- [x] 실패 케이스 분석으로 개선 방향 도출
- [ ] 프롬프트 변경 시 회귀 테스트 자동화
- [ ] 실험 설계 및 A/B 테스트

### 3. **LLM 응답 품질 검증** ✅
- [ ] 스키마는 맞지만 내용이 이상한 경우 처리 (예: "Python" → "파이썬 짱짱")
- [x] 재시도 로직 (exponential backoff)
- [x] Rate limiting 및 장애 복구 (Fallback 모델 전환)

### 4. **관측(Observability)**
- [ ] **Grafana + Prometheus**: API 메트릭, 토큰 사용량, trace
- [ ] **Superset**: 매칭 분포, 스킬 트렌드, 실험 결과
- [ ] **ELK**: Agent 추론 과정 로그 분석

### 5. **확장**
- [ ] 자동 스케줄링 & Slack 알림
- [ ] 멀티 플랫폼 크롤링
- [ ] 데이터 파이프라인 (Airbyte)
- [ ] PDF 기반 프로필 분석 (RAGFlow MCP)

---

## 📋 단계별 구현 계획

### **02-batch-evaluator** ✅
```
배치 자동화 + Evaluation 시스템
├── ✅ 재시도 로직 & 에러 핸들링 (Exponential Backoff)
├── ✅ LLM 어댑터 패턴 & Fallback 시스템
├── ✅ 중복 분석 방지
├── ✅ Evaluation 시스템 구축
│   ├── ✅ Ground Truth 테스트셋 구축 (10개 공고)
│   ├── ✅ 매칭 점수 정확도 측정 (Accuracy, Precision, Recall, F1, MAE)
│   └── ✅ 실패 케이스 분석 및 개선 방향 도출
├── 자동 스케줄링 (cron/scheduler) - 보류
└── Slack 알림 연동 - 보류
```

### **03-monitoring** (다음 단계)
```
모니터링 + 멀티 플랫폼
├── Grafana + Prometheus
│   ├── API 호출 메트릭
│   ├── 성공률/실패율 추적
│   └── 비용(토큰 사용량) 추적
├── 여러 플랫폼 크롤링 (사람인, 잡코리아)
└── DB 기반 데이터 관리
```

### **04-advanced** (확장 단계)
```
동적 Reasoning + 고급 분석
├── 진짜 Multi-step Reasoning (동적 경로 선택)
├── Superset BI 대시보드
├── PDF 기반 프로필 분석 (RAGFlow MCP)
└── ELK Stack (선택사항)
```

---
## 아래는 추후 평가후 Readme 지우기 ##
## 💡 이 프로젝트로 얻을 수 있는 경험

✅ **LLM/Agent 시스템의 관측(trace, log, metric) 설계 및 운영**
✅ **장기 실행 AI 워크플로우 설계 (상태 저장, 재시도, 장애 복구)**
✅ **실행 자동화 및 운영 효율화 (MLOps, Workflow Orchestration)**
✅ **품질 평가(Evals), 회귀 테스트, 실험 설계**
✅ **프로덕션 레벨의 소프트웨어 엔지니어링 (API 설계, 모듈화, 테스트, 배포)**
✅ **"돌아간다"와 "쓸만하다"의 차이를 측정하고 개선한 경험**
