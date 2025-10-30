# Vertex AI Vector Search 구현 완료

## 구현 내용

### 1. Vertex AI Text Embeddings API 통합

#### `src/embedding/embedding_service.py`
- **Vertex AI Text Embedding 모델 사용**: `textembedding-gecko@003`
- **배치 처리**: 최대 5개씩 배치로 처리하여 API 효율성 향상
- **Fallback 처리**: Vertex AI 실패 시 로컬 모델(sentence-transformers) 사용

```python
def _generate_vertex_ai_embeddings(self, texts: List[str]) -> List[List[float]]:
    from vertexai.preview.language_models import TextEmbeddingModel
    
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
    
    # 배치 처리 (최대 5개)
    embeddings = []
    batch_size = 5
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        results = model.get_embeddings(batch_texts)
        for question in results:
            embeddings.append(question.values)
    
    return embeddings
```

### 2. 기사 메타데이터 추출 시스템

#### `src/embedding/article_metadata_extractor.py` (신규 생성)
- **엔티티 추출**: 회사명, 인물, 지역, 날짜, 숫자 추출
- **카테고리 정규화**: 기사 분류 정보 추출
- **키워드 추출**: 주식 코드, 키워드 추출
- **기사 타입 추론**: 금융, 인수합병, 인사, 정책, 기술, 일반
- **중요도 점수 계산**: 메타데이터 기반 중요도 평가
- **인덱싱용 텍스트 생성**: 제목, 요약, 카테고리, 키워드, 엔티티 조합

#### 주요 메소드:
```python
def extract_metadata(article_data: Dict) -> Dict:
    """기사에서 메타데이터 추출"""
    - 엔티티 추출 (회사, 인물, 지역, 날짜, 숫자)
    - 카테고리 정규화
    - 키워드 추출
    - 주식 코드 추출
    - 시간 정보 추출
    - 기사 타입 추론
    - 중요도 점수 계산
    - 인덱싱용 텍스트 생성
```

### 3. 통합 임베딩 파이프라인

#### `src/embedding/embedding_service.py` 수정
- **메타데이터 추출 통합**: `ArticleMetadataExtractor` 활용
- **Vertex AI 임베딩 기본 사용**: `model_type="vertex_ai"` 설정
- **강화된 인덱싱 텍스트**: 메타데이터 기반 텍스트 사용
- **메타데이터 해시**: 중복 감지 및 추적용

```python
def generate_article_embedding(self, article_data: Dict) -> Dict:
    # 메타데이터 추출
    metadata = self.metadata_extractor.extract_metadata(article_data)
    
    # 인덱싱용 텍스트 사용 (메타데이터 기반)
    indexing_text = metadata.get('indexing_text', '')
    
    # Vertex AI 임베딩 생성
    embedding = self.generate_embeddings([indexing_text], model_type="vertex_ai")[0]
    
    return {
        'embedding': embedding,
        'metadata': embedding_metadata,
        'text_hash': hashlib.md5(indexing_text.encode('utf-8')).hexdigest(),
        'metadata_hash': metadata_hash
    }
```

### 4. Vertex AI Vector Search 인덱싱

#### `src/vector_search/vector_indexer.py`
- **배치 인덱싱**: 100개씩 배치로 처리
- **임베딩 생성**: `EmbeddingService` 활용
- **Vertex AI 업서트**: `upsert_vectors` 호출
- **상태 관리**: 데이터베이스에 인덱싱 상태 저장

```python
def _index_batch(self, articles: List[Dict]) -> Dict:
    # 임베딩 생성
    embeddings = self.embedding_service.batch_generate_embeddings(articles)
    
    # Vertex AI에 벡터 업서트
    vector_data = [{
        'id': embedding_info['article_id'],
        'embedding': embedding_info['embedding']
    } for embedding_info in embeddings]
    
    success = self.vertex_ai_client.upsert_vectors(self.index_id, vector_data)
```

### 5. 의존성 관리

#### `requirements.txt`
- **sentence-transformers**: 로컬 fallback 모델
- **Vertex AI SDK**: google-cloud-aiplatform (이미 포함)

## 동작 방식

### 전체 프로세스:

1. **기사 메타데이터 추출**
   - 제목, 본문, 요약에서 엔티티 추출
   - 카테고리, 키워드, 주식 코드 추출
   - 기사 타입 및 중요도 계산

2. **인덱싱용 텍스트 생성**
   - 제목 (가중치 2배)
   - 요약
   - 카테고리
   - 키워드
   - 엔티티

3. **Vertex AI 임베딩 생성**
   - textembedding-gecko@003 사용
   - 768차원 벡터 생성
   - 배치 처리 (5개씩)

4. **Vertex AI Vector Search 인덱싱**
   - 벡터를 인덱스에 업서트
   - 메타데이터와 함께 저장
   - 배치 처리 (100개씩)

## 사용 방법

### 1. 임베딩 생성
```python
from src.embedding.embedding_service import EmbeddingService

embedding_service = EmbeddingService()

article_data = {
    'title': '삼성전자 주가 상승',
    'body': '...',
    'summary': '...',
    'categories': [...],
    'keywords': [...]
}

result = embedding_service.generate_article_embedding(article_data)
# result['embedding']: 벡터 임베딩
# result['metadata']: 메타데이터
# result['metadata_hash']: 메타데이터 해시
```

### 2. 배치 인덱싱
```python
from src.vector_search.vector_indexer import VectorIndexer

indexer = VectorIndexer()

result = indexer.index_articles(batch_size=100 settings)
# 기사들을 배치로 처리하여 Vertex AI 인덱스에 추가
```

### 3. 검색
```python
results = indexer.search_similar_articles(
    query="금융 뉴스",
    top_k=10
)
```

## 특징

### 장점
1. **Vertex AI 통합**: Google의 강력한 임베딩 모델 사용
2. **메타데이터 강화**: 엔티티, 키워드 등 풍부한 메타데이터
3. **효율적 처리**: 배치 처리로 API 효율성 향상
4. **Fallback 지원**: Vertex AI 실패 시 로컬 모델 사용
5. **확장 가능**: 증분 인덱싱, 업데이트 지원

### 주의사항
1. **Vertex AI 인증 필요**: GCP 프로젝트 인증 필요
2. **API 비용**: Vertex AI API 사용량에 따른 비용 발생
3. **처리 시간**: 대량 데이터 처리 시 시간 소요

## 향후 개선
1. **캐싱**: 동일 텍스트 임베딩 캐싱
2. **병렬 처리**: 멀티스레딩으로 성능 향상
3. **스트리밍**: 대용량 데이터 스트리밍 처리
4. **모니터링**: 임베딩 품질 및 성능 모니터링

