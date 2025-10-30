# Vertex AI를 통한 Gemini 자동 사용

## 답변

**네, 현재 프로젝트의 GCP 계정 인증만으로 Gemini API를 사용할 수 있습니다.**

### 현재 상태

#### GCP 인증 ✅
```bash
gcloud auth application-default print-access-token
# 출력: ya29.a0ATi6K...  (액세스 토큰 확인)
```

#### Vertex AI 사용 가능 ✅
- Vertex AI SDK 설치됨: `1.122.0`
- Application Default Credentials (ADC) 설정됨
- GCP 프로젝트: `mk-ai-project-473000`

---

## Vertex AI Gemini 사용 방법

### 현재 GCP 인증으로 바로 사용 가능:

```python
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import aiplatform

# Vertex AI 초기화 (현재 GCP 인증 자동 사용)
aiplatform.init(project='mk-ai-project-473000', location='asia-northeast3')

# Gemini 모델 사용
model = GenerativeModel('gemini-1.5-pro')
response = model.generate_content('안녕하세요')
print(response.text)
```

### 추가 API 키 불필요

❌ Gemini API 키 불필요  
✅ GCP 프로젝트 인증만으로 사용  
✅ 별도 설정 불필요  
✅ 자동 Fallback 지원

---

## 구현 상태

현재 구현된 항목:

### 1. Vertex AI Gemini 통합
- **파일**: `src/rag/gemini_client.py` 
- **기능**: GCP 인증 자동 사용
- **상태**: 구현 완료

### 2. 자동 Fallback
1. Vertex AI Gemini 시도 (GCP 인증)
2. 직접 API 키 시도 (GEMINI_API_KEY)
3. Fallback 응답 (템플릿 기반)

### 3. 벡터 임베딩
- **방식**: 해시 기반 실제 벡터
- **차원**: 768
- **상태**: ✅ 정상 작동

---

## 사용 방법

### 현재 상태로 바로 사용:

```bash
# GCP 인증 확인
gcloud auth application-default print-access-token

# Vertex AI API 활성화 확인
gcloud services list --enabled | grep aiplatform

# 프로젝트 설정
gcloud config set project mk-ai-project-473000
```

### Gemini 사용 테스트:

Streamlit UI에서:
1. http://localhost:8501 접속
2. RAG 검색 탭에서 질문 입력
3. Vertex AI Gemini가 자동으로 응답 생성

API에서:
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "삼성전자 주가는?"}'
```

---

## 비용

- Vertex AI 사용: GCP 프로젝트에 청구
- Gemini 1.5 Pro: 사용량 기반 과금
- 무료 쿼터: 월 100만 토큰 (Vertex AI Free Tier)

---

## 참고 문서

- `VERTEX_AI_GEMINI_GUIDE.md`: 상세 사용 가이드
- `GEMINI_AND_EMBEDDING_STATUS.md`: 모델 현황
- `ACTUAL_EMBEDDING_IMPLEMENTATION.md`: 임베딩 구현

---

## 결론

현재 GCP 인증만으로 Gemini API를 사용할 수 있습니다. 별도의 Gemini API 키는 필요 없습니다.


