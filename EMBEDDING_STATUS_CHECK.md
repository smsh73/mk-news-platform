# 벡터 임베딩 현재 상태 확인

## 현재 상태: ❌ Mock 모드

### 발견된 문제

1. **sentence-transformers 미설치**
   - 로그: `sentence-transformers not available. Some features will be limited.`
   - 결과: 로컬 모델 사용 불가

2. **torch 미설치**
   - 로그: `torch not available. Korean embedding model will use fallback.`
   - 결과: 한국어 모델 사용 SNA

3. **Vertex AI 연결 실패** (로컬 환경)
   - 로그: DNS resolution failed
   - 결과: Vertex AI API 사용 불가

4. **Fallback 모드 동작**
   - 코드: `return [[0.0] * dim for _ in texts]` (line 90)
   - 결과: 모든 임베딩이 0.0으로 생성됨

### Mock 임베딩이 생성되는 곳

**파일**: `src/embedding/embedding_service.py`

```python:84:96:src/embedding/embedding_service.py
def _generate_multilingual_embeddings(self, texts: List[str]) -> List[List[float]]:
    """다국어 모델로 임베딩 생성"""
    try:
        if self.model is None:
            # Mock embedding for local development
            dim = 768
            return [[0.0] * dim for _ in texts]  # ← Mock 임베딩
        
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"다국어 임베딩 생성 중 오류 발생: {e}")
        raise
```

### 동작 흐름

1. `generate_embeddings()` 호출
2. `model_type="vertex_ai"` 지정
3. `_generate_vertex_ai_embeddings()` 시도
4. Vertex AI 연결 실패 → Exception
5. `_generate_multilingual_embeddings()` 호출 (Fallback)
6. `self.model is None` → Mock 임베딩 생성
7. 결과: `[[0.0, 0.0, ..., 0.0]]` (768차원)

## 실제 임베딩 사용을 위한 조건

### 옵션 1: sentence-transformers 설치
```bash
pip install sentence-transformers
```
- 로컬에서 실제 임베딩 생성 가능
- Vertex AI 불필요
- 메모리 사용량 증가

### 옵션 2: Vertex AI 사용
```bash
# GCP 인증 필요
gcloud auth application-default login

# 또는 서비스 계정 키 설정
export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
```
- GCP 프로젝트 설정 필요
- Vertex AI API 활성화 필요
- 네트워크 연결 필요

### 옵션 3: torch + transformers 설치
```bash
pip install torch transformers
```
- 한국어 특화 모델 사용 가능
- 대용량 메모리 필요 (보통 > 2GB)

## 현재 실행 중인 서비스

### FastAPI (uvicorn)
- URL: http://localhost:8000
- 상태: Mock 임베딩 모드
- 로그 파일: `/tmp/uvicorn_vector.log`

### Streamlit
- URL: http://localhost:8501
- 상태: 정상 실행
- 로그 파일: `/tmp/streamlit_fixed.log`

## 해결 방법

### 즉시 해결: sentence-transformers 설치
```bash
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate
pip install sentence-transformers
pkill -f uvicorn && pkill -f streamlit
# 서비스 재시작
```

### 근본 해결: Vertex AI 인증 설정
```bash
# GCP 로그인
gcloud auth application-default login

# 프로젝트 설정
gcloud config set project mk-ai-project-473000

# Vertex AI API 활성화
gcloud services enable aiplatform.googleapis.com
```

## 참고

- Mock 임베딩은 개발/테스트용
- 모든 텍스트의 임베딩이 동일함 (의미 없음)
- 검색/유사도 기능 정상 동작 불가
- 실제 사용 시 반드시 실제 모델 필요

