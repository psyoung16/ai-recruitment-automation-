# 📊 모니터링 & 관측 시스템

> 시스템을 "볼 수 있게" 만들기 - Metrics, Logs, Traces

## 💡 03-monitoring

**프로덕션 환경에서 시스템을 관측하고 개선하기**

02-batch-evaluator의 배치 시스템에 관측 가능성(Observability)을 추가합니다.
- "얼마나 많은 공고를 분석했는가?"
- "LLM API 호출은 얼마나 성공/실패했는가?"
- "비용(토큰 사용량)은 얼마나 발생했는가?"
- "어떤 공고가 높은/낮은 점수를 받았는가?"

## 🎯 핵심 목표

1. **Prometheus + Grafana**: 실시간 메트릭 수집 및 시각화
2. **구조화된 로깅**: JSON 로그로 분석 가능한 데이터 생성
3. **비용 추적**: LLM API 토큰 사용량 및 비용 모니터링
4. **알림 시스템**: 이상 징후 발생 시 자동 알림

---

## 📊 모니터링 대상

### 1. API 메트릭
- **호출 횟수**: 총 API 호출, 성공/실패 건수
- **응답 시간**: 평균/최대/최소 응답 시간
- **에러율**: HTTP 4xx, 5xx 에러 비율
- **Rate Limit**: 429 에러 발생 빈도

### 2. LLM 메트릭
- **토큰 사용량**: 입력/출력 토큰 개수
- **비용**: 모델별 사용 비용 (Gemini vs GPT)
- **Fallback 비율**: Primary 실패 → Fallback 전환 비율
- **모델별 성능**: 각 모델의 평균 점수, 응답 시간

### 3. 비즈니스 메트릭
- **매칭 점수 분포**: 0-100점 히스토그램
- **추천 공고 수**: recommended=true 비율
- **처리량**: 시간당/일당 분석 공고 수
- **스킬 트렌드**: 자주 등장하는 기술 스택

---

## 🏗️ 아키텍처

```
┌─────────────────┐
│  batch_matcher  │ ← 기존 배치 시스템
└────────┬────────┘
         │
         ├─→ Prometheus Exporter (메트릭 노출)
         │   - /metrics 엔드포인트
         │   - Counter, Histogram, Gauge
         │
         ├─→ JSON Logs (구조화된 로그)
         │   - logs/batch_YYYYMMDD.json
         │   - 타임스탬프, 레벨, 메시지, 컨텍스트
         │
         └─→ 분석 결과 저장
             - output/{query}/job_*_analyzed.json

┌──────────────┐      ┌──────────────┐
│  Prometheus  │ ───→ │   Grafana    │
│ (메트릭 수집) │      │ (시각화)      │
└──────────────┘      └──────────────┘
```

---

## 📈 Grafana 대시보드

### Dashboard 1: 시스템 개요
- 총 분석 공고 수 (게이지)
- API 호출 성공률 (게이지)
- 시간당 처리량 (그래프)
- 에러 발생 추이 (그래프)

### Dashboard 2: LLM 사용량
- 모델별 호출 비율 (파이 차트)
- 토큰 사용량 추이 (그래프)
- 누적 비용 (게이지)
- Fallback 발생 비율 (그래프)

### Dashboard 3: 매칭 분석
- 매칭 점수 분포 (히스토그램)
- 추천 공고 비율 (게이지)
- 스킬별 등장 빈도 (막대 차트)
- 점수별 시간대 분포 (히트맵)

---

## 🚀 설치 및 실행

### 1. Prometheus 설치 (Docker)

```bash
# prometheus.yml 설정 파일 생성
cat > prometheus.yml <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'job-matcher'
    static_configs:
      - targets: ['host.docker.internal:8000']
EOF

# Prometheus 실행
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 2. Grafana 설치 (Docker)

```bash
# Grafana 실행
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana

# 접속: http://localhost:3000
# 기본 계정: admin / admin
```

### 3. 메트릭 서버 실행

```bash
# 백그라운드로 메트릭 서버 실행
python metrics_server.py &

# 메트릭 확인
curl http://localhost:8000/metrics
```

### 4. 배치 분석 실행

```bash
# 기존과 동일하게 실행 (메트릭 자동 수집)
python batch_matcher.py --query "백엔드" --limit 20
```

---

## 📂 프로젝트 구조

```
03-monitoring/
├── README.md                       # 이 파일
├── batch_matcher.py                # 배치 분석 (메트릭 추가)
├── collector.py                    # 공고 수집
├── metrics_server.py               # Prometheus 메트릭 서버 (NEW)
├── monitoring/                     # 모니터링 모듈 (NEW)
│   ├── __init__.py
│   ├── prometheus.py              # Prometheus 메트릭 정의
│   └── logger.py                  # 구조화된 로깅
├── config/
│   ├── prometheus.yml             # Prometheus 설정
│   └── grafana_dashboards/        # Grafana 대시보드 JSON
│       ├── system_overview.json
│       ├── llm_usage.json
│       └── matching_analysis.json
├── llm/                           # LLM 어댑터
├── api/                           # 원티드 API
└── logs/                          # JSON 로그 저장
```

---

## 💡 다음 단계

### 03-monitoring (현재)
- [ ] Prometheus Exporter 구현
- [ ] 기본 메트릭 수집 (API 호출, 성공/실패)
- [ ] Grafana 대시보드 작성
- [ ] LLM 토큰 사용량 추적
- [ ] 비용 계산 로직 추가
- [ ] 알림 규칙 설정 (Alertmanager)

### 04-advanced (이후 계획)
- **Superset 추가**: BI 분석 및 데이터 인사이트
  - 기술 스택 트렌드 분석 (SQL 기반 차트)
  - 매칭 점수 분포 및 패턴 발견
  - 월별/요일별 추천 공고 분석
- **n8n**: 워크플로우 자동화 (공고 수집 → 분석 → Slack 알림)
- **Airbyte**: 멀티 플랫폼 데이터 파이프라인 (원티드/사람인 → PostgreSQL)
- **RAGFlow**: PDF 이력서 분석 및 RAG 파이프라인

---

## 🔗 참고 자료

- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
