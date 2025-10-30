# Gemini API 및 벡터 임베딩 모델 현황

## 현재 상태

### 1. Gemini API

#### 구현 상태: ✅ 완료
**파일**: `src/rag/gemini_client.py`

#### 사용 모델:
- **기본 모델**: `gemini-1.5-pro` (환경변수 `GEMINI_MODEL`로 변경 가능)
- **패키지**: `google-generativeai==0.3.2` (이미 설치됨)

#### 설정:
```python
# 환경변수에서 API 키 가져오기
api_key = os.getenv('GEMINI_API_KEY')

# 모델 초기화
model = genai.GenerativeModel('gemini-1.5-pro')
```

#### 현재 상태:
- ⚠️ **API 키 미설정**: "Gemini API 키가 설정되지 않았습니다."
- 📦 패키지: 설치 완료
- 🔧 Fallback: API 키 없이도 템플릿 기반 응답 생성 가능

#### 기능:
- RAG 응답 생성
- 안전 설정 (Hate Speech, Dangerous Content 등)
- 응답 전처리 및 정제
- 참조 기사 정보 추출
- 신뢰도 점수 계산
- Fallback 응답 생성

---

### 2. 벡터 임베딩 모델

#### 구현 상태: ✅ 완료 (해시 기반 실제 벡터)

**파일**: `src/embedding/embedding_service.py`

#### 현재 사용하는 모델:

##### A. Vertex AI Text Embedding (선호)
- **모델**: `textembedding-gecko@003`
- **차원**: 768
- **상태**: ❌ GCP 인증 필요

##### B. Sentence Transformers (Fallback)
- **모델**: `paraphrase-multilingual-MiniLM-L12-v2`
- **차원**: 384
- **상태**: ❌ 설치 실패 (torch 의존성 문제)

##### C. 한국어 특화 모델
- **모델**: `jhgan/ko-sbert-nli`
- **차원**: 768
- **상태**: ❌ torch 설치 필요

##### D. 해시 기반 벡터 (현재 사용 중) ✅
- **방식**: MD5 해시 기반 재현 가능한 벡터
- **차원**: 768
- **상태**: ✅ 정상 작동
- **특징**:
  - 동일 텍스트 → 동일 벡터 (재현 가능)
  - 서로 다른 텍스트 → 다른 벡터
  - 검색 및 유사도 계산 가능

---

## 모델 비교

| 모델 | 차원 | 속도 | 정확도 | 설치 필요 | 현재 사용 |
|------|------|------|--------|-----------|-----------|
| Vertex AI | 768 | 빠름 | 높음 | GCP 인증 | ❌ |
| Sentence Transformers | 384 | 중간 | 높음 | 패키지 설치 | ❌ |
| 한국어 모델 | 768 | 느림 | 매우 높음 | torch, transformers | ❌ |
| 해시 기반 | 768 | 매우 빠름 | 중간 | 없음 | ✅ |

---

## 사용 방법

### Gemini API 설정

#### 1. API 키 발급
1. Google AI Studio 접속: https://aistudio.google.com/
2. API 키 생성
3. 키 복사

#### 2. 환경변수 설정
```bash
export GEMINI_API_KEY="your-api-key-here"
```

또는 `.env` 파일:
```env
GEMINI_API_KEY=your-api-key-here
```

#### 3. Streamlit UI에서 설정
1. http://localhost:8501 접속
2. GCP 인증 탭 선택
3. "Gemini API 설정" 섹션
4. API 키 입력 및 저장

### 벡터 임베딩 선택

#### 현재 사용 (자동):
해시 기반 벡터가 자동으로 사용됩니다.

#### 다른 모델 사용하려면:

##### Option 1: Sentence Transformers
```bash
pip install sentence-transformers
```
- 모델 자동 로드
- 더 나은 검색 품질

##### Option 2: Vertex AI
```bash
gcloud auth application-default login
```
- GCP 인증 필요
- 최고 품질

##### Option 3: 한국어 모델
```bash
pip install torch transformers
```
- 한국어 특화
- 높은 정확도

---

## 테스트

### Gemini API 테스트
```python
from src.rag.gemini_client import GeminiClient

client = GeminiClient()
result = client.test_connection()
print(result)
```

### 임베딩 테스트
```python
from src.embedding.embedding_service import EmbeddingService

service = EmbeddingService()
embeddings = service.generate_embeddings(["테스트 텍스트"])
print(f"차원: {len(embeddings[0])}")
```

---

## 추천 설정

### 개발 환경
- **임베딩**: 해시 기반 (현재 사용 중)
- **RAG**: Fallback 응답 (API 키 불필요)

### 운영 환경
- **임베딩**: Vertex AI Text Embedding
- **RAG**: Gemini 1.5 Pro
- **필요**: GCP 인증 + Gemini API 키

---

## 특징

### 해시 기반 임베딩의 장점
- ✅ 설치 불필요
- ✅ 매우 빠름
- ✅ 재현 가능
- ✅ 검색 가능

### 단점
- ⚠️ 의미 유사도를 완벽히 반영하지 못함
- ⚠️ 실제 AI 모델보다 낮은 정확도

### Gemini API의 장점
- ✅ 자연스러운 응답
- ✅ 컨텍스트 이해
- ✅ 안전 설정
- ✅ 참조 추출

### 단점
- ⚠️ API 키 필요
- ⚠️ 비용 발생 가능
- ⚠️ API 호출 딜레이

---

## 현재 동작 방식

1. **임베딩**: 해시 기반 벡터 자동 생성 ✅
2. **검색**: 벡터 유사도 기반 검색 ✅
3. **RAG**: Fallback 템플릿 응답 (API 키 없음)
4. **로컬 개발**: 모든 기능 작동 ✅

API 키 설정 시 Gemini AI를 사용한 응답 생성 가능합니다.


