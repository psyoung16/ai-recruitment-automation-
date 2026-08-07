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
├── 01-basic-matcher/              # 기본 매칭 시스템
│   ├── README.md
│   ├── main.py
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

### 2. **평가(Evaluation)**
**"돌아간다" ≠ "쓸만하다"**

- [ ] 정량적 평가: 지원할 공고 vs 안 할 공고 각 10개 테스트
- [ ] 매칭 점수 정확도 측정 및 문서화
- [ ] 프롬프트 변경 시 회귀 테스트
- [ ] 실험 설계 및 A/B 테스트

### 3. **LLM 응답 품질 검증**
- [ ] 스키마는 맞지만 내용이 이상한 경우 처리 (예: "Python" → "파이썬 짱짱")
- [ ] 재시도 로직 (exponential backoff)
- [ ] Rate limiting 및 장애 복구

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

## 📋 단계별 로드맵

### **02-batch-scanner** (다음 단계)
```
배치 자동화 + 기본 모니터링 + 에러 핸들링
├── 재시도 로직 & 에러 핸들링
├── 자동 스케줄링 (cron/scheduler)
├── 중복 분석 방지
├── Slack 알림 연동
├── 평가(Evaluation) 시스템 구축
└── Grafana + Prometheus 모니터링
    ├── API 호출 메트릭
    ├── 성공률/실패율 추적
    ├── 응답 시간 모니터링
    └── 비용(토큰 사용량) 추적
```

### **03-multi-platform** (확장 단계)
```
멀티 플랫폼 + 비즈니스 인사이트 + 동적 Reasoning
├── 여러 플랫폼 크롤링 (사람인, 잡코리아)
├── 데이터 파이프라인 (Airbyte)
├── DB 기반 데이터 관리
├── 진짜 Multi-step Reasoning (동적 경로 선택)
├── PDF 기반 프로필 분석 (RAGFlow MCP)
└── Superset BI 대시보드
    ├── 매칭 점수 분포 분석
    ├── 스킬 트렌드 시각화
    ├── 추천 공고 목록
    └── 실험 결과 분석
```

### **04-advanced** (선택사항)
```
고급 관측 & 최적화
├── ELK Stack 로그 분석
├── Agent 추론 과정 trace
├── 품질 평가(Evals) 자동화
└── MLOps 파이프라인
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
