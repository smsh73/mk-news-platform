"""
한국어 특화 임베딩 모델
"""
import os
import logging
import numpy as np
from typing import List, Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModel
import re

logger = logging.getLogger(__name__)

class KoreanEmbeddingModel:
    """한국어 특화 임베딩 모델"""
    
    def __init__(self, model_name: str = "jhgan/ko-sbert-nli"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """모델 초기화"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.eval()
            
            logger.info(f"한국어 임베딩 모델 로드 완료: {self.model_name}")
            
        except Exception as e:
            logger.error(f"한국어 임베딩 모델 초기화 중 오류 발생: {e}")
            # 대체 모델 사용
            self._initialize_fallback_model()
    
    def _initialize_fallback_model(self):
        """대체 모델 초기화"""
        try:
            # 기본 다국어 모델 사용
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.tokenizer = None  # SentenceTransformer는 내장 토크나이저 사용
            
            logger.info("대체 임베딩 모델 로드 완료")
            
        except Exception as e:
            logger.error(f"대체 모델 초기화 중 오류 발생: {e}")
            raise
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """텍스트 임베딩 생성"""
        try:
            if self.tokenizer is None:
                # SentenceTransformer 사용
                return self.model.encode(texts, convert_to_tensor=False).tolist()
            
            # 한국어 특화 모델 사용
            return self._encode_with_korean_model(texts)
            
        except Exception as e:
            logger.error(f"한국어 임베딩 생성 중 오류 발생: {e}")
            raise
    
    def _encode_with_korean_model(self, texts: List[str]) -> List[List[float]]:
        """한국어 모델로 임베딩 생성"""
        try:
            embeddings = []
            
            for text in texts:
                # 텍스트 전처리
                processed_text = self._preprocess_korean_text(text)
                
                # 토크나이징
                inputs = self.tokenizer(
                    processed_text,
                    return_tensors='pt',
                    padding=True,
                    truncation=True,
                    max_length=512
                )
                
                # 임베딩 생성
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # CLS 토큰의 임베딩 사용
                    embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
                    embeddings.append(embedding.tolist())
            
            return embeddings
            
        except Exception as e:
            logger.error(f"한국어 모델 임베딩 생성 중 오류 발생: {e}")
            raise
    
    def _preprocess_korean_text(self, text: str) -> str:
        """한국어 텍스트 전처리"""
        try:
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', text)
            
            # 특수 문자 정리
            text = re.sub(r'[^\w\s가-힣]', ' ', text)
            
            # 공백 정리
            text = ' '.join(text.split())
            
            # 최대 길이 제한
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            return text
            
        except Exception as e:
            logger.error(f"한국어 텍스트 전처리 중 오류 발생: {e}")
            return text
    
    def get_embedding_dimension(self) -> int:
        """임베딩 차원 반환"""
        try:
            if self.model is None:
                return 768  # 기본값
            
            # 모델의 출력 차원 확인
            if hasattr(self.model, 'config'):
                return self.model.config.hidden_size
            else:
                # 테스트 임베딩으로 차원 확인
                test_embedding = self.encode(["테스트"])
                return len(test_embedding[0])
                
        except Exception as e:
            logger.error(f"임베딩 차원 확인 중 오류 발생: {e}")
            return 768
    
    def encode_single(self, text: str) -> List[float]:
        """단일 텍스트 임베딩 생성"""
        try:
            embeddings = self.encode([text])
            return embeddings[0]
            
        except Exception as e:
            logger.error(f"단일 텍스트 임베딩 생성 중 오류 발생: {e}")
            raise
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """임베딩 유사도 계산 (코사인 유사도)"""
        try:
            embedding1 = np.array(embedding1)
            embedding2 = np.array(embedding2)
            
            # 정규화
            embedding1 = embedding1 / np.linalg.norm(embedding1)
            embedding2 = embedding2 / np.linalg.norm(embedding2)
            
            # 코사인 유사도 계산
            similarity = np.dot(embedding1, embedding2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"유사도 계산 중 오류 발생: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]], 
                         top_k: int = 5) -> List[Dict]:
        """가장 유사한 임베딩 찾기"""
        try:
            similarities = []
            
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate_embedding)
                similarities.append({
                    'index': i,
                    'similarity': similarity
                })
            
            # 유사도 순으로 정렬
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"유사 임베딩 검색 중 오류 발생: {e}")
            return []


