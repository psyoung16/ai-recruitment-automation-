# 🎯 AI Job Matching Series

> AI Agent 기술을 단계별로 학습하며 실용적인 채용 자동화 시스템을 구축하는 프로젝트 시리즈
> 정리 blog https://velog.io/@mumini/series/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-%EC%B6%94%EC%B2%9C-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8-%EB%A7%8C%EB%93%A4%EA%B8%B0


## 📚 프로젝트 목록

### [01-basic-matcher](./01-basic-matcher) ✅
**AI 채용공고 매칭 시스템 (기본편)**

채용공고를 AI가 자동으로 분석하고 내 프로필과의 매칭도를 계산합니다.

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

### [03-monitoring](./03-monitoring) ✅
**실시간 모니터링 + 메트릭 시각화**

배치 시스템의 운영 상태와 매칭 성능을 실시간으로 추적합니다.

**핵심 학습:**
- Prometheus + Grafana 메트릭 수집 및 시각화
- PostgreSQL 기반 시계열 데이터 저장
- Docker Compose 인프라 구축
- 프로세스 간 메트릭 공유 아키텍처

**주요 기능:**
- 분석 공고 수, 추천 비율 실시간 추적
- 쿼리별 평균 매칭 점수 모니터링
- Grafana 대시보드를 통한 시각화
- DB 기반 메트릭 영속성 보장

---

### [04-integration](./04-integration) 🔄
**통합 검증 & 운영 준비**

구현한 시스템을 실제 환경에서 통합하고 검증합니다.

**핵심 학습:**
- End-to-End 통합 테스트
- 실데이터 검증 및 성능 측정
- 운영 편의 기능 구현 (Slack 알림)
- 트러블슈팅 및 문제 해결

**주요 기능:**
- Docker Compose 전체 스택 검증
- 100+ 공고로 대용량 테스트
- Slack 알림 연동
- 포트폴리오 자료 수집 (스크린샷, 데모)

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
├── 03-monitoring/                 # 모니터링 & 인프라 ✅
│   ├── README.md
│   ├── batch_matcher.py           # DB 저장 기능 추가
│   ├── metrics_server.py          # 메트릭 노출 서버
│   ├── docker-compose.yml         # 인프라 구성
│   ├── monitoring/
│   │   ├── db.py                  # DB 연결 및 저장
│   │   └── metrics.py             # 메트릭 정의
│   └── config/
│       ├── prometheus.yml         # Prometheus 설정
│       └── grafana/               # Grafana 대시보드
├── 04-integration/                # 통합 검증 & 운영 🔄
│   ├── README.md
│   ├── test_results/              # 테스트 결과 (예정)
│   ├── slack_notifier.py          # Slack 알림 (예정)
│   └── docs/                      # 운영 문서 (예정)
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

### 4. **관측(Observability)** ✅ (부분)
- [x] **Grafana + Prometheus**: 비즈니스 메트릭 (분석 건수, 추천 비율, 매칭 점수)
- [ ] **Grafana + Prometheus**: API 메트릭, 토큰 사용량, trace (향후 확장)
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

### **03-monitoring** ✅
```
실시간 모니터링 + 인프라 구축
├── ✅ Docker Compose (전체 시스템 컨테이너화)
├── ✅ Redis (공고 데이터 캐싱)
├── ✅ PostgreSQL (분석 결과 저장)
├── ✅ Grafana + Prometheus
│   ├── 비즈니스 메트릭 (매칭 점수 분포, 추천 비율) - 완료
│   ├── API 호출 메트릭 (성공/실패율, 응답시간) - 향후 확장
│   ├── LLM 메트릭 (토큰 사용량, 비용, Fallback 비율) - 향후 확장
│   └── Evaluation 메트릭 (Accuracy, Precision, Recall 추이) - 향후 확장
├── 구조화된 JSON 로깅 - 보류
└── 알림 시스템 (Alertmanager) - 보류
```

### **04-rag-system** (다음 단계 - RAG 파이프라인)
```
PDF 이력서 기반 고급 매칭 시스템
├── PDF 파싱 및 구조화
│   ├── 경력 사항 추출
│   ├── 프로젝트 경험 추출
│   └── 기술 스택 추출
├── 벡터 DB 구축 (ChromaDB/Weaviate)
│   ├── 이력서 청킹 전략
│   ├── 임베딩 생성 (OpenAI/Sentence Transformers)
│   └── 유사도 기반 검색
├── RAG 기반 매칭 개선
│   ├── 공고 요구사항 vs 이력서 경험 매칭
│   ├── 컨텍스트 기반 스킬 평가
│   └── 프로젝트 경험 기반 적합도 분석
└── Docker Compose 통합
    └── ChromaDB 컨테이너 추가
```

### **05-advanced** (확장 단계)
```
BI 분석 + 워크플로우 자동화
├── Superset (BI 대시보드)
│   ├── 기술 스택 트렌드 분석 (SQL 기반)
│   ├── 매칭 패턴 발견 및 인사이트
│   └── 월별/요일별 추천 공고 분석
├── n8n (워크플로우 자동화)
│   └── 공고 수집 → 분석 → Slack 알림 파이프라인
└── Airbyte (선택)
    └── 멀티 플랫폼 데이터 파이프라인 (원티드/사람인 → PostgreSQL)
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
