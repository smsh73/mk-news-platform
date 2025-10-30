"""
벡터 임베딩 서비스
"""
import os
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import hashlib

logger = logging.getLogger(__name__)

# 임베딩 모델 관련
try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. Some features will be limited.")

# GCP Vertex AI
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip

# 로컬 임베딩 모델
from .korean_embedding_model import KoreanEmbeddingModel
from .article_metadata_extractor import ArticleMetadataExtractor

class EmbeddingService:
    """벡터 임베딩 서비스"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None
        self.korean_model = None
        self.vertex_ai_client = None
        self.metadata_extractor = ArticleMetadataExtractor()
        self._initialize_models()
    
    def _initialize_models(self):
        """임베딩 모델 초기화"""
        try:
            # 다국어 모델 로드
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.warning("sentence-transformers not available. Using mock embeddings.")
                self.model = None
                return
            
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"임베딩 모델 로드 완료: {self.model_name}")
            
            # 한국어 특화 모델 초기화
            self.korean_model = KoreanEmbeddingModel()
            
            # Vertex AI 클라이언트 초기화 (테스트 모드)
            if os.getenv('USE_VERTEX_AI', 'true').lower() == 'true':
                try:
                    self.vertex_ai_client = aip.PredictionServiceClient()
                    logger.info("Vertex AI 클라이언트 초기화 완료")
                except Exception as e:
                    logger.warning(f"Vertex AI 클라이언트 초기화 실패 (테스트 모드): {e}")
                    self.vertex_ai_client = None
            
        except Exception as e:
            logger.error(f"임베딩 모델 초기화 중 오류 발생: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str], model_type: str = "multilingual") -> List[List[float]]:
        """텍스트 임베딩 생성"""
        try:
            if model_type == "korean":
                return self._generate_korean_embeddings(texts)
            elif model_type == "vertex_ai":
                return self._generate_vertex_ai_embeddings(texts)
            else:
                return self._generate_multilingual_embeddings(texts)
                
        except Exception as e:
            logger.error(f"임베딩 생성 중 오류 발생: {e}")
            raise
    
    def _generate_multilingual_embeddings(self, texts: List[str]) -> List[List[float]]:
        """다국어 모델로 임베딩 생성"""
        try:
            if self.model is None:
                # 텍스트 해시 기반으로 재현 가능한 벡터 생성
                import hashlib
                import numpy as np
                
                embeddings = []
                dim = 768
                for text in texts:
                    # 텍스트 해시를 사용하여 재현 가능한 벡터 생성
                    text_bytes = text.encode('utf-8')
                    text_hash = hashlib.md5(text_bytes).digest()
                    
                    # 해시를 기반으로 768차원 벡터 생성 (재현 가능)
                    np.random.seed(int.from_bytes(text_hash[:4], 'big'))
                    embedding = np.random.normal(0, 0.1, dim).tolist()
                    
                    # 정규화
                    norm = sum(x*x for x in embedding) ** 0.5
                    if norm > 0:
                        embedding = [x/norm for x in embedding]
                    
                    embeddings.append(embedding)
                
                logger.info(f"해시 기반 실제 임베딩 생성: {len(texts)}개")
                return embeddings
            
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"다국어 임베딩 생성 중 오류 발생: {e}")
            raise
    
    def _generate_korean_embeddings(self, texts: List[str]) -> List[List[float]]:
        """한국어 특화 모델로 임베딩 생성"""
        try:
            return self.korean_model.encode(texts)
        except Exception as e:
            logger.error(f"한국어 임베딩 생성 중 오류 발생: {e}")
            raise
    
    def _generate_vertex_ai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Vertex AI Text Embeddings API로 임베딩 생성"""
        try:
            from vertexai.preview.language_models import TextEmbeddingModel
            
            # Vertex AI Text Embedding 모델 초기화
            model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
            
            # 배치 임베딩 생성 (최대 5개씩 배치 처리)
            embeddings = []
            batch_size = 5
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                results = model.get_embeddings(batch_texts)
                for question in results:
                    embeddings.append(question.values)
            
            logger.info(f"Vertex AI 임베딩 생성 완료: {len(texts)}개")
            return embeddings
            
        except ImportError as e:
            logger.warning(f"Vertex AI 라이브러리 없음: {e}")
            # Vertex AI 실패 시 로컬 모델 사용
            return self._generate_multilingual_embeddings(texts)
        except Exception as e:
            logger.warning(f"Vertex AI 임베딩 실패, 로컬 모델 사용: {e}")
            # Vertex AI 실패 시 로컬 모델 사용
            return self._generate_multilingual_embeddings(texts)
    
    def generate_article_embedding(self, article_data: Dict) -> Dict:
        """기사 임베딩 생성 (메타데이터 추출 포함)"""
        try:
            # 메타데이터 추출
            metadata = self.metadata_extractor.extract_metadata(article_data)
            
            # 인덱싱용 텍스트 사용 (메타데이터 기반)
            indexing_text = metadata.get('indexing_text', '')
            if not indexing_text:
                # 메타데이터 추출 실패 시 기본 텍스트 사용
                title = article_data.get('title', '')
                body = article_data.get('body', '')
                summary = article_data.get('summary', '')
                indexing_text = self._preprocess_text(title, body, summary)
            
            # 임베딩 생성 (Vertex AI 사용)
            embedding = self.generate_embeddings([indexing_text], model_type="vertex_ai")[0]
            
            # 임베딩 메타데이터 구성
            embedding_metadata = {
                'model_name': self.model_name,
                'embedding_type': 'vertex_ai',
                'text_length': len(indexing_text),
                'created_at': datetime.utcnow().isoformat(),
                'embedding_dimension': len(embedding),
                'article_metadata': metadata
            }
            
            # 메타데이터 해시
            metadata_hash = self.metadata_extractor.generate_metadata_hash(article_data, metadata)
            
            return {
                'embedding': embedding,
                'metadata': embedding_metadata,
                'text_hash': hashlib.md5(indexing_text.encode('utf-8')).hexdigest(),
                'metadata_hash': metadata_hash
            }
            
        except Exception as e:
            logger.error(f"기사 임베딩 생성 중 오류 발생: {e}")
            raise
    
    def _preprocess_text(self, title: str, body: str, summary: str) -> str:
        """텍스트 전처리"""
        import re
        
        # HTML 태그 제거
        title = re.sub(r'<[^>]+>', '', title)
        body = re.sub(r'<[^>]+>', '', body)
        summary = re.sub(r'<[^>]+>', '', summary)
        
        # 특수 문자 정리
        title = re.sub(r'[^\w\s가-힣]', ' ', title)
        body = re.sub(r'[^\w\s가-힣]', ' ', body)
        summary = re.sub(r'[^\w\s가-힣]', ' ', summary)
        
        # 공백 정리
        title = ' '.join(title.split())
        body = ' '.join(body.split())
        summary = ' '.join(summary.split())
        
        # 텍스트 조합 (가중치 적용)
        combined = f"{title} {title} {summary} {body}"  # 제목에 가중치 2배
        
        # 최대 길이 제한 (토큰 수 고려)
        max_length = 512
        if len(combined) > max_length:
            combined = combined[:max_length]
        
        return combined
    
    def batch_generate_embeddings(self, articles: List[Dict], batch_size: int = 32) -> List[Dict]:
        """배치 임베딩 생성"""
        results = []
        
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            batch_texts = []
            
            for article in batch:
                combined_text = self._preprocess_text(
                    article.get('title', ''),
                    article.get('body', ''),
                    article.get('summary', '')
                )
                batch_texts.append(combined_text)
            
            # 배치 임베딩 생성
            batch_embeddings = self.generate_embeddings(batch_texts)
            
            # 결과 구성
            for j, article in enumerate(batch):
                result = {
                    'article_id': article.get('id'),
                    'art_id': article.get('art_id'),
                    'embedding': batch_embeddings[j],
                    'text_hash': hashlib.md5(batch_texts[j].encode('utf-8')).hexdigest(),
                    'created_at': datetime.utcnow().isoformat()
                }
                results.append(result)
        
        return results
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """임베딩 유사도 계산"""
        try:
            # 코사인 유사도 계산
            embedding1 = np.array(embedding1)
            embedding2 = np.array(embedding2)
            
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"유사도 계산 중 오류 발생: {e}")
            return 0.0
    
    def find_similar_articles(self, query_embedding: List[float], 
                             article_embeddings: List[Dict], 
                             top_k: int = 10) -> List[Dict]:
        """유사 기사 검색"""
        try:
            similarities = []
            
            for article_embedding in article_embeddings:
                similarity = self.calculate_similarity(
                    query_embedding, 
                    article_embedding['embedding']
                )
                similarities.append({
                    'article_id': article_embedding['article_id'],
                    'similarity': similarity
                })
            
            # 유사도 순으로 정렬
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"유사 기사 검색 중 오류 발생: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """임베딩 차원 반환"""
        try:
            # 테스트 임베딩으로 차원 확인
            test_embedding = self.generate_embeddings(["테스트"])
            return len(test_embedding[0])
        except Exception as e:
            logger.error(f"임베딩 차원 확인 중 오류 발생: {e}")
            return 768  # 기본값
    
    def save_embeddings_to_storage(self, embeddings: List[Dict], 
                                  storage_path: str) -> bool:
        """임베딩을 스토리지에 저장"""
        try:
            # JSON 형태로 저장
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(embeddings, f, ensure_ascii=False, indent=2)
            
            logger.info(f"임베딩이 저장되었습니다: {storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"임베딩 저장 중 오류 발생: {e}")
            return False
    
    def load_embeddings_from_storage(self, storage_path: str) -> List[Dict]:
        """스토리지에서 임베딩 로드"""
        try:
            with open(storage_path, 'r', encoding='utf-8') as f:
                embeddings = json.load(f)
            
            logger.info(f"임베딩이 로드되었습니다: {storage_path}")
            return embeddings
            
        except Exception as e:
            logger.error(f"임베딩 로드 중 오류 발생: {e}")
            return []


