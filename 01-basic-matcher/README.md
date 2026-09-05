# 🤖 AI 채용공고 매칭 시스템

> 수백 개의 채용공고를 일일이 확인하는 대신, AI가 자동으로 내 스킬과 매칭도를 분석합니다.

## 💡 왜 만들었나?

매일 쏟아지는 채용공고를 하나씩 읽고 "이게 나한테 맞나?"를 판단하는 건 비효율적입니다.
**AI Agent가 공고를 분석하고 내 프로필과 비교해서 점수를 매겨주면 어떨까?**

## 🎯 학습 목표

AI Agent 개발의 핵심 개념을 단계별로 학습하기 위한 프로젝트입니다.

1. **Function Calling** - LLM이 필요할 때 함수를 직접 호출하도록 구현
2. **Multi-step Reasoning** - 여러 단계를 거쳐 결론을 도출하는 추론 과정 구현
3. **실용적 자동화** - 실제 API와 연동하여 동작하는 시스템 구축

## 🏗️ 어떻게 작동하나?

```
원티드 API 조회
    ↓
AI가 공고 분석 (Function Calling)
    ↓
내 프로필과 비교 (0-100점 매칭)
    ↓
결과 저장 & 추천 판단
```

**핵심 기술:**
- Gemini Function Calling으로 공고 본문 자동 분석
- Pydantic으로 구조화된 데이터 추출
- JSON Schema로 응답 형식 강제

## 📊 실행 결과

```bash
$ python3 main.py 365200

📋 공고 ID 365200 분석 중...

🔍 1단계: 공고 요구사항 추출 중...
✅ 요구사항 추출 완료
  - 필요 기술: Python, Django, Kotlin, Spring, AWS
  - 경력: 5년
  - 키워드: 백엔드, MSA, 결제

🎯 2단계: 스킬 매칭 분석 중...
✅ 매칭 분석 완료

============================================================
📊 매칭 점수: 75점
============================================================

✅ 매칭되는 스킬: Python, Django, Spring Boot
❌ 부족한 스킬: Kotlin, AWS, 5년 경력

💡 이유: Django와 Python 경험이 매칭되지만, 경력 년수가 부족하고 Kotlin 경험이 없습니다.

🎉 추천! (임계값 70점 이상)
💾 저장 완료: output/job_365200_20260807_143052.json
```

## 🎓 핵심 학습 포인트

### Function Calling
```python
# LLM이 필요 시 자동으로 함수 호출
tools = [get_job_detail]

response = client.models.generate_content(
    contents="job_id=365200 공고를 분석해줘",
    config={"tools": tools, "automatic_function_calling": True}
)
```

### Multi-step Reasoning
1. 공고 분석 (Function Calling으로 데이터 수집)
2. 스킬 매칭 (수집된 데이터를 기반으로 분석)
3. 결과 판단 (점수를 바탕으로 추천 여부 결정)

## 📂 프로젝트 구조

```
├── main.py           # 메인 파이프라인
├── wanted_api.py     # 원티드 API 호출
├── models.py         # Pydantic 데이터 모델
├── config.py         # 설정 (모델, 프로필)
├── utils.py          # 유틸리티 (결과 저장)
└── output/           # 분석 결과 JSON
```

## 🔮 향후 개선 계획

- [ ] Slack 알림 연동
- [ ] 여러 플랫폼 크롤링
- [ ] 배치 자동 스캔
- [ ] 웹 대시보드

---

## 🚀 설치 및 실행

### 1. 패키지 설치
```bash
pip install google-genai python-dotenv requests pydantic
```

### 2. 환경변수 설정
`.env` 파일 생성:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. 프로필 설정
`config.py`에서 본인 프로필 수정:
```python
MY_PROFILE = """
- 언어: Python, Java
- 프레임워크: Django, Spring Boot
- 경력: 3년차 백엔드
"""
```

### 4. 실행
```bash
python3 main.py <job_id>
```

## 📝 참고 자료
- [Gemini Function Calling 가이드](https://ai.google.dev/gemini-api/docs/function-calling)

### 🔄 Function Calling & Structured Output 전체 흐름
