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

# 임베딩 모델 관련
from sentence_transformers import SentenceTransformer
import torch

# GCP Vertex AI
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip

# 로컬 임베딩 모델
from .korean_embedding_model import KoreanEmbeddingModel

logger = logging.getLogger(__name__)

class EmbeddingService:
    """벡터 임베딩 서비스"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None
        self.korean_model = None
        self.vertex_ai_client = None
        self._initialize_models()
    
    def _initialize_models(self):
        """임베딩 모델 초기화"""
        try:
            # 다국어 모델 로드
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
        """Vertex AI로 임베딩 생성"""
        try:
            if not self.vertex_ai_client:
                raise Exception("Vertex AI 클라이언트가 초기화되지 않았습니다.")
            
            # Vertex AI 임베딩 API 호출
            # 실제 구현에서는 Vertex AI의 임베딩 API를 사용
            # 여기서는 다국어 모델을 대신 사용
            return self._generate_multilingual_embeddings(texts)
            
        except Exception as e:
            logger.error(f"Vertex AI 임베딩 생성 중 오류 발생: {e}")
            raise
    
    def generate_article_embedding(self, article_data: Dict) -> Dict:
        """기사 임베딩 생성"""
        try:
            # 임베딩할 텍스트 구성
            title = article_data.get('title', '')
            body = article_data.get('body', '')
            summary = article_data.get('summary', '')
            
            # 텍스트 전처리
            combined_text = self._preprocess_text(title, body, summary)
            
            # 임베딩 생성
            embedding = self.generate_embeddings([combined_text])[0]
            
            # 메타데이터 구성
            embedding_metadata = {
                'model_name': self.model_name,
                'text_length': len(combined_text),
                'title_length': len(title),
                'body_length': len(body),
                'summary_length': len(summary),
                'created_at': datetime.utcnow().isoformat(),
                'embedding_dimension': len(embedding)
            }
            
            return {
                'embedding': embedding,
                'metadata': embedding_metadata,
                'text_hash': hashlib.md5(combined_text.encode('utf-8')).hexdigest()
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


