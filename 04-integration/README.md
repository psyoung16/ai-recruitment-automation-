# 🚀 04. Integration & Production Deployment

## 💡 프로젝트 목표

**맥미니에 전체 시스템을 배포하고 실제 운영 환경에서 검증**

### 📋 운영 시나리오

```
매일 오전 10시, 자동으로:
1. 채용공고 수집 (키워드: 백엔드, backend, ai, ai 에이전트)
2. 내 프로필 기준으로 매칭 점수 계산
3. Slack 알림 (2가지)
   - 추천 공고 상세 정보 (회사명, 포지션, 이유, 링크)
   - 일일 분석 통계 요약 (총 건수, 추천 수, 평균/최고 점수)
4. Grafana 대시보드로 실시간 모니터링
```

**핵심 기능:**
1. **Docker Compose 기반 전체 스택 배포**
2. **Cron 기반 자동화** (매일 오전 10시 실행)
3. **Slack 알림 분리** (사용자용 추천 공고 + 시스템 통계)
4. **환경변수 기반 프로필 관리** (개인정보 보호)
5. **실데이터 검증** (100+ 공고 테스트)

---

## 🏗️ 시스템 아키텍처

### 전체 흐름도

```
[맥미니 - 24/7 운영]

┌─────────────────────────────────────────────────────────┐
│ Cron (매일 10:00)                                        │
│   ↓                                                      │
│ run_daily_job.sh 실행                                    │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ 1. 공고 수집 (collector.py)                              │
│    ├─ 키워드: 백엔드, backend, ai, ai 에이전트           │
│    ├─ 각 키워드당 20개씩 수집                            │
│    └─ Redis 캐싱 (중복 수집 방지)                        │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 배치 분석 (batch_matcher.py)                          │
│    ├─ 프로필: .env 파일에서 로드                         │
│    ├─ LLM 분석 (Gemini + Fallback GPT)                  │
│    └─ PostgreSQL 저장                                    │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Slack 알림 (slack_notifier.py)                       │
│    ├─ 추천 공고 상세 (회사명, 포지션, 이유, 링크)       │
│    │  - 80점 이상: 🔥, 70-79점: ⭐, 나머지: ✅         │
│    └─ 일일 분석 통계 (총 건수, 추천 수, 평균/최고점수) │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. 메트릭 수집 & 시각화                                  │
│    ├─ Prometheus: 10초마다 스크래핑                     │
│    ├─ Grafana: 대시보드 실시간 업데이트                 │
│    └─ 모니터링: 추천 비율, 평균 점수, 처리 건수         │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 프로젝트 구조

```
04-integration/
├── docker-compose.yml              # 전체 인프라 정의 (Redis, PostgreSQL, Prometheus, Grafana)
├── .env.example                    # 환경변수 템플릿
├── scripts/                        # 운영 자동화 스크립트
│   ├── run_daily_job.sh           # 일일 배치 실행 (Cron 연동)
│   ├── start_services.sh          # 전체 서비스 시작 + 헬스체크
│   └── check_health.sh            # 시스템 상태 종합 점검
├── slack_notifier.py               # Slack 알림 봇 (추천 공고 + 통계)
├── collector.py                    # 공고 수집 ( API + Redis 캐싱)
├── batch_matcher.py                # 배치 분석 (LLM 매칭 + PostgreSQL 저장)
├── metrics_server.py               # Prometheus 메트릭 서버
├── matcher.py                      # 매칭 로직 (01, 02 프로젝트 재사용)
├── config/settings.py              # 프로필 환경변수 로드
├── monitoring/                     # DB 연결 및 메트릭 정의
└── llm/                            # LLM 어댑터 (Gemini + GPT Fallback)
```

---

## 📊 Slack 알림 예시

### 1️⃣ 추천 공고 알림

```
💼 오늘의 추천 채용공고
1개의 공고를 추천드립니다!
─────────────────────────
🔥 카카오
📋 백엔드 개발자 (결제시스템)
🎯 매칭 점수: 85점
🔍 키워드: `백엔드`
💡 Spring Boot와 MSA 아키텍처 경험이 풍부하고, PostgreSQL을 활용한 대용량 트랜잭션 처리 경험이 있어 우리 팀과 잘 맞을 것 같습니다...
[공고 보기 버튼]
```

### 2️⃣ 일일 분석 요약

```
📊 일일 분석 요약
총 분석:        15건
추천:           3건
평균 점수:      68.5점
최고 점수:      85점

📈 Grafana 대시보드 보기
```

---

## 🧪 통합 테스트 프로세스

### Phase 1: 인프라 검증 ✅

**목표:** Docker Compose 환경이 정상 동작하는지 확인

**체크리스트:**
- [x] Docker Compose 실행 (`docker-compose up -d`)
- [x] Redis 컨테이너 정상 동작 확인
- [x] PostgreSQL 컨테이너 및 스키마 생성 확인
- [x] Prometheus 컨테이너 실행 및 설정 로드 확인
- [x] Grafana 컨테이너 실행 및 datasource 연결 확인
- [x] 컨테이너 간 네트워크 통신 확인

---

### Phase 2: 파이프라인 검증 ✅

**목표:** 공고 수집 → 분석 → DB 저장 → 메트릭 노출 전체 흐름 확인

**테스트 시나리오:**
```bash
# 1. 공고 10개 수집
python collector.py --query "백엔드" --limit 10

# 2. 배치 분석 실행
python batch_matcher.py --query "백엔드"

# 3. PostgreSQL 데이터 확인
docker exec -it job-matcher-postgres psql -U matcher -d job_matcher \
  -c "SELECT COUNT(*) FROM analyzed_jobs;"

# 4. Prometheus 메트릭 확인
curl http://localhost:8000/metrics

# 5. Grafana 대시보드 확인
# http://localhost:3000 접속
```

---

### Phase 3: 프로덕션 검증 🔄

**목표:** 실제 운영 환경 시뮬레이션

**테스트 시나리오:**
```bash
# 1. 전체 키워드로 수집 (실제 운영 시나리오)
./scripts/run_daily_job.sh

# 2. Slack 알림 테스트
python slack_notifier.py

# 3. Cron 1회 수동 실행
./scripts/run_daily_job.sh

# 4. 24시간 모니터링
# - Grafana 대시보드 확인
# - Slack 알림 수신 확인
# - 에러 로그 확인
```

**측정 지표:**
- 총 처리 시간
- API Rate Limit 발생 빈도
- Fallback 전환 비율
- Slack 알림 정확도
- 메모리/CPU 사용량

---

## 🚀 설치 및 배포

### 환경 설정
```bash
cp .env.example .env  # .env.example 참고하여 환경변수 설정
```

### 서비스 실행
```bash
docker-compose up -d                # Docker 인프라 시작
nohup python metrics_server.py &    # 메트릭 서버 실행
```

### Cron 설정
```bash
crontab -e
# 매일 오전 10시 실행
0 10 * * * /path/to/scripts/run_daily_job.sh >> /path/to/logs/cron.log 2>&1
```

---

## 📸 포트폴리오 자료 수집

### 스크린샷 체크리스트
- [ ] Grafana 대시보드 (실제 데이터)
- [ ] Slack 알림 예시 (고득점 공고)
- [ ] Slack 일일 요약 알림
- [ ] Docker 컨테이너 상태
- [ ] Prometheus 메트릭
- [ ] 성공/실패 로그 예시

### 데모 영상/GIF
- [ ] 전체 파이프라인 실행 과정
- [ ] Grafana 대시보드 실시간 업데이트
- [ ] Slack 알림 수신 (실제 모바일)

---

## 🔄 다음 단계 (05-rag-system)

통합 테스트 완료 후:
- PDF 이력서 파싱 및 구조화
- 벡터 DB (ChromaDB) 구축
- RAG 기반 매칭 시스템
- DB에 프로필 저장 (04의 env → 05의 DB)
- Slack `/profile import resume.pdf` 명령어