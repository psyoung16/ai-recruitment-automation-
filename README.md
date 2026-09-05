# 🎯 AI Job Matching Series

> AI Agent 기술을 단계별로 학습하며 실용적인 채용 자동화 시스템을 구축하는 프로젝트 시리즈
> [정리 blog](https://velog.io/@mumini/series/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-%EC%B6%94%EC%B2%9C-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8-%EB%A7%8C%EB%93%A4%EA%B8%B0)

**핵심 경험:** LLM Agent 설계, Evaluation 시스템 구축, 프로덕션 모니터링 & 운영 자동화


## 📚 프로젝트 목록

### [01-basic-matcher](./01-basic-matcher) ✅
**AI 채용공고 매칭 시스템 (기본편)**

[[AI 채용 자동화 #1] Gemini Function Calling으로 채용공고 매칭 시스템 만들기](https://velog.io/@mumini/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-1-Gemini-Function-Calling%EC%9C%BC%EB%A1%9C-%EC%B1%84%EC%9A%A9%EA%B3%B5%EA%B3%A0-%EB%A7%A4%EC%B9%AD-%EC%8B%9C%EC%8A%A4%ED%85%9C-%EB%A7%8C%EB%93%A4%EA%B8%B0)

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

[[AI 채용 자동화 #2-1] 배치 처리를 위한 파이프라인 분리](https://velog.io/@mumini/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-2-1-%EB%B0%B0%EC%B9%98-%EC%B2%98%EB%A6%AC%EB%A5%BC-%EC%9C%84%ED%95%9C-%ED%8C%8C%EC%9D%B4%ED%94%84%EB%9D%BC%EC%9D%B8-%EB%B6%84%EB%A6%AC)

[[AI 채용 자동화 #2-2] 에러 핸들링 & LLM 어댑터 패턴](https://velog.io/@mumini/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-1-Gemini-Function-Calling%EC%9C%BC%EB%A1%9C-%EC%B1%84%EC%9A%A9%EA%B3%B5%EA%B3%A0-%EB%A7%A4%EC%B9%AD-%EC%8B%9C%EC%8A%A4%ED%85%9C-%EB%A7%8C%EB%93%A4%EA%B8%B0)

[[AI 채용 자동화 #2-3] Evaluation - "쓸만한" 시스템 검증하기](https://velog.io/@mumini/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-2-3-Evaluation-%EC%93%B8%EB%A7%8C%ED%95%9C-%EC%8B%9C%EC%8A%A4%ED%85%9C-%EA%B2%80%EC%A6%9D%ED%95%98%EA%B8%B0)

[[AI 채용 자동화 #2-4] 이제 평가를 돌려보자.](https://velog.io/@mumini/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-2-4-%EC%9D%B4%EC%A0%9C-%ED%8F%89%EA%B0%80%EB%A5%BC-%EB%8F%8C%EB%A0%A4%EB%B3%B4%EC%9E%90)

[[AI 채용 자동화 #2-5] 평가를 기준으로 개선해보자.](https://velog.io/@mumini/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-2-5-%ED%8F%89%EA%B0%80%EB%A5%BC-%EA%B8%B0%EC%A4%80%EC%9C%BC%EB%A1%9C-%EA%B0%9C%EC%84%A0%ED%95%B4%EB%B3%B4%EC%9E%90.%EC%9D%8C-%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8-%EA%B0%9C%EC%84%A0)

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

[[AI 채용 자동화 #3] 실시간 모니터링 & 대시보드 구축](https://velog.io/@mumini/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-3-%EC%8B%A4%EC%8B%9C%EA%B0%84-%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81-%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C-%EA%B5%AC%EC%B6%95-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%B6%94%EA%B0%80-%EB%B0%8F-%EB%A7%88%EB%AC%B4%EB%A6%AC-%ED%95%84%EC%9A%94)

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

[[AI 채용 자동화 #4] 배포 및 실행](https://velog.io/@mumini/AI-%EC%B1%84%EC%9A%A9-%EC%9E%90%EB%8F%99%ED%99%94-4-%EB%B0%B0%ED%8F%AC-%EB%B0%8F-%EC%8B%A4%ED%96%89)

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
├── 02-batch-evaluator/            # 배치 처리 & 평가 ✅
├── 03-monitoring/                 # 모니터링 & 인프라 ✅
├── 04-integration/                # 통합 검증 & 운영 🔄               
```

## 🚀 시작하기

각 프로젝트 폴더의 README를 참고하세요.

---

## 📋 단계별 구현 계획

### **02-batch-evaluator** ✅
- 배치 자동화 + Evaluation 시스템
- 재시도 로직, LLM 어댑터 패턴, Fallback 시스템
- Ground Truth 기반 정량 평가 (Accuracy, Precision, Recall, F1, MAE)

### **03-monitoring** ✅
- Docker Compose 인프라 구축 (Redis, PostgreSQL, Prometheus, Grafana)
- 비즈니스 메트릭 모니터링 (매칭 점수 분포, 추천 비율, 처리 건수)
- 실시간 대시보드 시각화

### **04-integration** 🔄
- **통합 검증 & 운영 자동화**
- Cron 기반 자동 실행 (매일 오전 10시)
- Slack 알림 연동 (추천 공고 상세 + 일일 통계 요약)
- 환경변수 기반 프로필 관리
- 실데이터 검증 (100+ 공고 테스트)

### **05-rag-system** (다음 단계)
- **PDF 이력서 기반 고급 매칭**
- PDF 파싱 및 구조화 (경력, 프로젝트, 기술 스택 추출)
- 벡터 DB 구축 (ChromaDB/Weaviate)
- RAG 기반 컨텍스트 매칭

### **06-advanced** (확장 단계)
- **BI 분석 + 워크플로우 자동화**
- Superset (기술 스택 트렌드, 매칭 패턴 분석)
- n8n (워크플로우 오케스트레이션)
- Airbyte (멀티 플랫폼 데이터 파이프라인)

