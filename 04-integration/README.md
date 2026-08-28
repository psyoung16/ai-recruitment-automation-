# 🚀 Integration & Validation

> "구현했다"를 넘어 "실제로 돌아간다"

## 💡 04-integration

**전체 시스템을 통합하고 실제 환경에서 검증**

1. **End-to-End 통합 테스트**: Docker Compose로 전체 스택 실행
2. **실데이터 검증**: 실제 공고 100+개로 파이프라인 전체 테스트
3. **운영 편의 기능**: Slack 알림, 헬스체크 추가
4. **문제 발견 및 해결**: 실제 운영 시 발생한 이슈 해결 과정 기록

## 🔄 통합 테스트 프로세스

### Phase 1: 인프라 검증 ✅
**목표:** Docker Compose 환경이 정상 동작하는지 확인

**체크리스트:**
- [ ] Docker Compose 실행 (`docker-compose up -d`)
- [ ] Redis 컨테이너 정상 동작 확인
- [ ] PostgreSQL 컨테이너 및 스키마 생성 확인
- [ ] Prometheus 컨테이너 실행 및 설정 로드 확인
- [ ] Grafana 컨테이너 실행 및 datasource 연결 확인
- [ ] 컨테이너 간 네트워크 통신 확인

**예상 문제:**
- 포트 충돌 (6379, 5432, 9090, 3000, 8000)
- 볼륨 권한 문제
- 환경변수 누락

---

### Phase 2: 데이터 파이프라인 검증 ✅
**목표:** 공고 수집 → 분석 → DB 저장 → 메트릭 노출 전체 흐름 확인

**테스트 시나리오:**
```bash
# 1. 공고 10개 수집
python collector.py --query "백엔드" --limit 10

# 2. 배치 분석 실행
python batch_matcher.py --query "백엔드"

# 3. PostgreSQL 데이터 확인
psql -U matcher -d job_matcher -c "SELECT COUNT(*) FROM analyzed_jobs;"

# 4. metrics_server 실행
python metrics_server.py &

# 5. Prometheus 메트릭 확인
curl http://localhost:8000/metrics

# 6. Grafana 대시보드 확인
# http://localhost:3000 접속
```

**측정 지표:**
- 처리 시간: 공고당 평균 N초
- 성공률: X/10 성공
- Fallback 발생: Y건
- DB 저장 성공률

---

### Phase 3: 대용량 테스트 ✅
**목표:** 100개+ 공고로 안정성 및 성능 확인

**테스트 시나리오:**
```bash
# 다양한 키워드로 100개 이상 수집
python collector.py --query "백엔드" --limit 50
python collector.py --query "DevOps" --limit 30
python collector.py --query "데이터엔지니어" --limit 30

# 배치 분석 실행
python batch_matcher.py --query "백엔드"
python batch_matcher.py --query "DevOps"
python batch_matcher.py --query "데이터엔지니어"
```

**측정 지표:**
- 총 처리 시간
- 메모리 사용량
- API Rate Limit 발생 빈도
- Fallback 전환 비율
- 에러 발생 및 재시도 패턴
- Grafana 대시보드 성능

---

### Phase 4: 운영 편의 기능 추가 🔄
**목표:** Slack 알림 등 실제 사용에 필요한 기능 추가

**구현 항목:**
- [ ] Slack webhook 연동
  - 고득점 공고 발견 시 알림 (80점 이상)
  - 배치 완료 알림
  - 에러 발생 알림
- [ ] 헬스체크 엔드포인트
  - `/health`: 서비스 상태 확인
  - `/metrics`: Prometheus 메트릭 (기존)
- [ ] 운영 스크립트
  - 전체 스택 시작/종료
  - 로그 확인

---

## 📊 테스트 결과 (작성 예정)

### Phase 1: 인프라 검증
```
상태: ⏳ 진행 예정
```

### Phase 2: 파이프라인 검증
```
상태: ⏳ 진행 예정
```

### Phase 3: 대용량 테스트
```
상태: ⏳ 진행 예정
```

### Phase 4: 운영 기능
```
상태: ⏳ 진행 예정
```

---

## 📸 포트폴리오 자료 (수집 예정)

### 스크린샷 체크리스트
- [ ] Grafana 대시보드 (데이터 표시)
- [ ] Slack 알림 예시
- [ ] Prometheus 메트릭
- [ ] 성공/실패 로그 예시
- [ ] Docker 컨테이너 상태

### 데모 영상/GIF
- [ ] 전체 파이프라인 실행 과정
- [ ] Grafana 대시보드 실시간 업데이트
- [ ] Slack 알림 수신

---

## 🔧 추가 기능 (구현 예정)

### 1. Slack 알림
```python
# slack_notifier.py
def notify_high_score_job(job_id, company, position, score):
    """80점 이상 고득점 공고 알림"""
    pass

def notify_batch_complete(query, total, recommended):
    """배치 완료 알림"""
    pass

def notify_error(error_type, message):
    """에러 발생 알림"""
    pass
```

### 2. 헬스체크 엔드포인트
```python
# health_check.py
@app.route('/health')
def health():
    return {
        "status": "healthy",
        "services": {
            "redis": check_redis(),
            "postgres": check_postgres(),
            "prometheus": check_prometheus()
        }
    }
```

### 3. 운영 스크립트
```bash
# scripts/start.sh
#!/bin/bash
echo "Starting all services..."
docker-compose up -d
python metrics_server.py &
echo "All services started!"

# scripts/stop.sh
#!/bin/bash
echo "Stopping all services..."
pkill -f metrics_server.py
docker-compose down
echo "All services stopped!"

# scripts/logs.sh
#!/bin/bash
tail -f logs/metrics_server.log
```

---

## 📂 프로젝트 구조

```
04-integration/
├── README.md                       # 이 파일
├── test_results/                   # 테스트 결과 (작성 예정)
│   ├── phase1_infrastructure.md
│   ├── phase2_pipeline.md
│   ├── phase3_load_test.md
│   └── screenshots/
├── slack_notifier.py               # Slack 알림 (구현 예정)
├── health_check.py                 # 헬스체크 (구현 예정)
├── scripts/                        # 운영 스크립트 (구현 예정)
│   ├── start.sh
│   ├── stop.sh
│   └── logs.sh
├── docs/                           # 문서 (작성 예정)
│   ├── troubleshooting.md          # 트러블슈팅 가이드
│   └── operations.md               # 운영 가이드
│
├── batch_matcher.py                # 03-monitoring에서 복사
├── collector.py
├── metrics_server.py
├── docker-compose.yml
└── ...                             # 기타 파일들
```

---

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# .env 파일 생성
cp .env.example .env

# API 키 입력
# GEMINI_API_KEY=...
# GPT_API_KEY=...
```

### 2. 인프라 실행
```bash
# Docker Compose 실행
docker-compose up -d

# 컨테이너 상태 확인
docker ps
```

### 3. 메트릭 서버 실행
```bash
python metrics_server.py &
```

### 4. 통합 테스트 시작
```bash
# Phase 2 시작
python collector.py --query "백엔드" --limit 10
python batch_matcher.py --query "백엔드"
```

### 5. 대시보드 확인
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Metrics: http://localhost:8000/metrics

---

## 🤔 배포 전략: 왜 클라우드가 아닌 로컬인가?

### 클라우드 배포를 고려했지만...

**AWS/GCP 무료 티어의 한계:**
- EC2 하나에 `docker-compose up`만 하는 건 포트폴리오 차별화 안 됨
- 의미 있으려면 Auto Scaling, RDS Multi-AZ, CloudWatch 등 여러 서비스 조합 필요
- 무료 티어로는 제한적, 유료로 하기엔 비용 부담

**이미 충분한 기술 스택:**
```
현재 시스템이 이미 "여러 서비스 통합 운영"
├── Redis (캐싱)
├── PostgreSQL (데이터)
├── Prometheus (메트릭 수집)
├── Grafana (시각화)
└── Flask (메트릭 서버)

→ 로컬이든 클라우드든 동일한 구조
→ Docker Compose로 어디서든 실행 가능
```

### 대신 집중한 것

**1. 실제 문제 해결 경험**
- 프로세스 분리로 인한 메트릭 손실 문제
- PostgreSQL을 통한 아키텍처 재설계
- Grafana datasource uid 불일치 트러블슈팅
- Gauge 메트릭에 rate() 함수 사용 불가 이슈

**2. 포트폴리오 자료의 질**
- 스크린샷 (Grafana 대시보드, 로그)
- 데모 영상/GIF
- 트러블슈팅 문서
- 성능 테스트 결과

**3. 실무 적용 가능성**
- Production-ready 코드 품질
- 모니터링, 로깅, 메트릭 설계
- Evaluation을 통한 품질 검증

### 결론

"어디서 돌리는가"보다 "무엇을 배웠는가"가 중요합니다.
- 맥미니에서 테스트하여 자료 확보
- 필요 시 언제든 재실행 가능
- 시간과 비용을 RAG 구현에 집중

---

## 🔄 다음 단계 (05-rag-system)

통합 테스트 완료 후:
- PDF 이력서 파싱 및 구조화
- 벡터 DB (ChromaDB) 구축
- RAG 기반 매칭 시스템
- 매칭 정확도 개선