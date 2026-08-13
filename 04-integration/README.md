# 📊 실시간 모니터링 + 메트릭 시각화

> 배치 시스템의 운영 상태와 매칭 성능을 실시간으로 추적합니다.

## 💡 03-monitoring

**프로덕션 환경에서 시스템을 관측하고 개선하기**

1. **PostgreSQL 기반 메트릭 저장**: 분석 결과를 DB에 저장하여 영속성 보장
2. **Prometheus + Grafana 연동**: 실시간 메트릭 수집 및 시각화
3. **Docker Compose 인프라**: Redis, PostgreSQL, Prometheus, Grafana 통합 구성
4. **프로세스 간 메트릭 공유**: DB를 통한 메트릭 노출 아키텍처

## 🔄 시스템 흐름도

```
배치 분석 (batch_matcher.py)
    ↓
분석 결과 저장
    ├─ output/{query}/job_*_analyzed.json (기존)
    └─ PostgreSQL analyzed_jobs 테이블 (신규) ⭐
        ├─ job_id, query, company, position
        ├─ score, recommended
        ├─ matched_skills, missing_skills
        └─ reason, model, analyzed_at


메트릭 서버 (metrics_server.py) ⭐
    ↓
DB 쿼리 → Prometheus 메트릭 생성
    ├─ jobs_analyzed_total (쿼리별 분석 건수)
    ├─ jobs_recommended_total (쿼리별 추천 건수)
    └─ job_avg_score (쿼리별 평균 점수)
    ↓
/metrics 엔드포인트 노출 (http://localhost:8000/metrics)


Prometheus (스크레이핑)
    ↓
10초마다 메트릭 수집 → 시계열 DB 저장
    ↓
Grafana (시각화) ⭐
    ├─ Total Jobs Analyzed (게이지)
    ├─ Total Recommended Jobs (게이지)
    ├─ Average Matching Score (게이지)
    └─ Jobs Analyzed by Query (테이블)
```

## 🏗️ 아키텍처 특징

### 문제: 프로세스 분리로 인한 메트릭 손실

Python Prometheus 클라이언트는 메트릭을 **프로세스 메모리**에 저장합니다.
- `batch_matcher.py`에서 기록한 메트릭 → 프로세스 종료 시 사라짐
- `metrics_server.py`는 별도 프로세스 → `batch_matcher.py`의 메트릭을 볼 수 없음

### 해결: PostgreSQL을 중간 저장소로 활용

```
batch_matcher.py (분석 프로세스)
    ↓
PostgreSQL (영속 저장)
    ↓
metrics_server.py (메트릭 노출 프로세스)
    ↓
Prometheus (수집)
```

매 `/metrics` 요청마다 DB를 쿼리하여 최신 데이터를 Prometheus에 제공합니다.

## 📊 모니터링 메트릭

### 비즈니스 메트릭 (현재 구현)
- **분석 공고 수**: 쿼리별 총 분석 건수
- **추천 공고 수**: 쿼리별 추천된 공고 수 (recommended=true)
- **평균 매칭 점수**: 쿼리별 평균 점수 (0-100)

### 향후 확장 가능 메트릭
- **LLM 메트릭**: 토큰 사용량, 비용, Fallback 비율
- **API 메트릭**: 응답 시간, 성공/실패율
- **Evaluation 메트릭**: Accuracy, Precision, Recall 추이

## 📈 Grafana 대시보드

**Job Matcher - System Overview**

| 패널 | 설명 | 쿼리 |
|------|------|------|
| Total Jobs Analyzed | 전체 분석 건수 | `sum(jobs_analyzed_total)` |
| Total Recommended | 전체 추천 건수 | `sum(jobs_recommended_total)` |
| Average Matching Score | 전체 평균 점수 | `avg(job_avg_score)` |
| Jobs Analyzed by Query | 쿼리별 상세 통계 | 테이블 형식 |

접속: http://localhost:3000 (admin/admin)

## 📂 프로젝트 구조

```
03-monitoring/
├── batch_matcher.py                # 배치 분석 (DB 저장 추가)
├── metrics_server.py               # Flask 메트릭 서버 (NEW)
├── monitoring/
│   ├── db.py                       # DB 연결 및 저장 로직 (NEW)
│   └── metrics.py                  # 메트릭 정의
├── docker-compose.yml              # 인프라 구성 (NEW)
├── init.sql                        # DB 스키마 (NEW)
├── config/
│   ├── prometheus.yml              # Prometheus 설정 (NEW)
│   └── grafana/                    # Grafana 대시보드 (NEW)
│       ├── provisioning/
│       │   ├── datasources/        # Prometheus 연결
│       │   └── dashboards/         # 대시보드 자동 로드
│       └── dashboards/
│           └── system_overview.json
├── collector.py                    # 공고 수집
├── llm/                            # LLM 어댑터
├── api/                            # 원티드 API
├── data/                           # 수집된 공고
└── output/                         # 분석 결과
```

---

## 🚀 설치 및 실행

### 1. 환경변수 설정

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# API 키 설정
GEMINI_API_KEY=your_gemini_api_key
GPT_API_KEY=your_gpt_api_key

# DB 계정 (기본값 사용 가능)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_matcher
DB_USER=matcher
DB_PASSWORD=matcher123

# Grafana 계정 (기본값 사용 가능)
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

### 2. 인프라 실행 (Docker Compose)

```bash
# 전체 인프라 실행
docker-compose up -d

# 컨테이너 상태 확인
docker ps
# → redis, postgres, prometheus, grafana 실행 확인
```

### 3. Python 패키지 설치

```bash
pip install -r requirements.txt
# → psycopg2-binary, prometheus-client, flask 등 설치
```

### 4. 메트릭 서버 실행

```bash
# 백그라운드 실행
python metrics_server.py &

# 메트릭 확인
curl http://localhost:8000/metrics
```

### 5. 배치 분석 실행

```bash
# 공고 수집
python collector.py --query "백엔드" --limit 10

# 배치 분석 (자동으로 DB에 저장됨)
python batch_matcher.py --query "백엔드"
```

### 6. 대시보드 확인

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
  - Dashboards → Job Matcher - System Overview

### 접속 정보

| 서비스 | URL | 계정 |
|--------|-----|------|
| Metrics Server | http://localhost:8000 | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Redis | localhost:6379 | - |
| PostgreSQL | localhost:5432 | matcher/matcher123 |

---

## 🔄 다음 단계 (04-integration)

- 전체 스택 통합 테스트 (Docker Compose)
- 실데이터 검증 (100+ 공고)
- Slack 알림 연동
- 포트폴리오 자료 수집 (스크린샷, 데모)