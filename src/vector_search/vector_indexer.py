"""
벡터 인덱싱 서비스
"""
import os
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from .vertex_ai_client import VertexAIVectorSearchClient
from ..embedding.embedding_service import EmbeddingService
from ..database.connection import get_db
from ..database.models import Article, VectorIndex, ProcessingLog

logger = logging.getLogger(__name__)

class VectorIndexer:
    """벡터 인덱싱 서비스"""
    
    def __init__(self, project_id: str = "mk-ai-project-473000", region: str = "asia-northeast3"):
        self.project_id = project_id
        self.region = region
        self.vertex_ai_client = VertexAIVectorSearchClient(project_id, region)
        self.embedding_service = EmbeddingService()
        self.index_id = None
        self.endpoint_id = None
        self.deployed_index_id = None
    
    def create_vector_index(self, index_name: str = "mk-news-vector-index", 
                          dimensions: int = 768) -> Dict:
        """벡터 인덱스 생성"""
        try:
            # Vertex AI 인덱스 생성
            self.index_id = self.vertex_ai_client.create_index(
                index_name=index_name,
                dimensions=dimensions
            )
            
            # 데이터베이스에 인덱스 정보 저장
            self._save_index_to_db(index_name, self.index_id, dimensions)
            
            logger.info(f"벡터 인덱스 생성 완료: {self.index_id}")
            
            return {
                'status': 'success',
                'index_id': self.index_id,
                'message': '벡터 인덱스가 성공적으로 생성되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"벡터 인덱스 생성 중 오류 발생: {e}")
            return {
                'status': 'error',
                'message': f'벡터 인덱스 생성 실패: {str(e)}'
            }
    
    def create_index_endpoint(self, endpoint_name: str = "mk-news-vector-endpoint") -> Dict:
        """인덱스 엔드포인트 생성"""
        try:
            # Vertex AI 엔드포인트 생성
            self.endpoint_id = self.vertex_ai_client.create_index_endpoint(
                endpoint_name=endpoint_name
            )
            
            logger.info(f"인덱스 엔드포인트 생성 완료: {self.endpoint_id}")
            
            return {
                'status': 'success',
                'endpoint_id': self.endpoint_id,
                'message': '인덱스 엔드포인트가 성공적으로 생성되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"인덱스 엔드포인트 생성 중 오류 발생: {e}")
            return {
                'status': 'error',
                'message': f'인덱스 엔드포인트 생성 실패: {str(e)}'
            }
    
    def deploy_index(self, deployed_index_id: str = "mk_news_deployed_index") -> Dict:
        """인덱스 배포"""
        try:
            if not self.index_id or not self.endpoint_id:
                return {
                    'status': 'error',
                    'message': '인덱스 또는 엔드포인트가 생성되지 않았습니다.'
                }
            
            # 인덱스 배포
            self.deployed_index_id = self.vertex_ai_client.deploy_index(
                endpoint_id=self.endpoint_id,
                index_id=self.index_id,
                deployed_index_id=deployed_index_id
            )
            
            # 데이터베이스 업데이트
            self._update_index_deployment(deployed_index_id)
            
            logger.info(f"인덱스 배포 완료: {self.deployed_index_id}")
            
            return {
                'status': 'success',
                'deployed_index_id': self.deployed_index_id,
                'message': '인덱스가 성공적으로 배포되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"인덱스 배포 중 오류 발생: {e}")
            return {
                'status': 'error',
                'message': f'인덱스 배포 실패: {str(e)}'
            }
    
    def index_articles(self, article_ids: Optional[List[str]] = None, 
                     batch_size: int = 100) -> Dict:
        """기사 벡터 인덱싱"""
        try:
            if not self.index_id:
                return {
                    'status': 'error',
                    'message': '벡터 인덱스가 생성되지 않았습니다.'
                }
            
            # 인덱싱할 기사 조회
            articles = self._get_articles_for_indexing(article_ids)
            
            if not articles:
                return {
                    'status': 'error',
                    'message': '인덱싱할 기사가 없습니다.'
                }
            
            # 배치별로 처리
            total_articles = len(articles)
            indexed_count = 0
            error_count = 0
            
            for i in range(0, total_articles, batch_size):
                batch_articles = articles[i:i + batch_size]
                batch_result = self._index_batch(batch_articles)
                
                indexed_count += batch_result['indexed']
                error_count += batch_result['errors']
                
                logger.info(f"배치 {i//batch_size + 1} 완료: {batch_result}")
            
            # 인덱스 상태 업데이트
            self._update_index_stats(indexed_count)
            
            return {
                'status': 'success',
                'total_articles': total_articles,
                'indexed_count': indexed_count,
                'error_count': error_count,
                'message': f'{indexed_count}개 기사가 성공적으로 인덱싱되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"기사 인덱싱 중 오류 발생: {e}")
            return {
                'status': 'error',
                'message': f'기사 인덱싱 실패: {str(e)}'
            }
    
    def _get_articles_for_indexing(self, article_ids: Optional[List[str]] = None) -> List[Dict]:
        """인덱싱할 기사 조회"""
        db = next(get_db())
        try:
            query = db.query(Article).filter(
                Article.is_processed == True,
                Article.is_embedded == False
            )
            
            if article_ids:
                query = query.filter(Article.id.in_(article_ids))
            
            articles = query.limit(1000).all()  # 한 번에 최대 1000개
            
            return [
                {
                    'id': article.id,
                    'art_id': article.art_id,
                    'title': article.title,
                    'body': article.body,
                    'summary': article.summary,
                    'service_daytime': article.service_daytime
                }
                for article in articles
            ]
            
        finally:
            db.close()
    
    def _index_batch(self, articles: List[Dict]) -> Dict:
        """배치 기사 인덱싱"""
        try:
            # 임베딩 생성
            embeddings = self.embedding_service.batch_generate_embeddings(articles)
            
            # 벡터 데이터 준비
            vector_data = []
            for embedding_info in embeddings:
                vector_data.append({
                    'id': embedding_info['article_id'],
                    'embedding': embedding_info['embedding']
                })
            
            # Vertex AI에 벡터 업서트
            success = self.vertex_ai_client.upsert_vectors(self.index_id, vector_data)
            
            if success:
                # 데이터베이스 업데이트
                self._update_articles_embedded([article['id'] for article in articles])
                
                return {
                    'indexed': len(articles),
                    'errors': 0
                }
            else:
                return {
                    'indexed': 0,
                    'errors': len(articles)
                }
                
        except Exception as e:
            logger.error(f"배치 인덱싱 중 오류 발생: {e}")
            return {
                'indexed': 0,
                'errors': len(articles)
            }
    
    def search_similar_articles(self, query: str, top_k: int = 10, 
                               filter_expression: Optional[str] = None) -> List[Dict]:
        """유사 기사 검색"""
        try:
            if not self.endpoint_id:
                return []
            
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_service.generate_embeddings([query])[0]
            
            # 벡터 검색
            search_results = self.vertex_ai_client.search_vectors(
                endpoint_id=self.endpoint_id,
                query_embedding=query_embedding,
                top_k=top_k,
                filter_expression=filter_expression
            )
            
            # 기사 정보 조회
            article_ids = [result['id'] for result in search_results]
            articles = self._get_articles_by_ids(article_ids)
            
            # 결과 구성
            results = []
            for i, result in enumerate(search_results):
                article = next((a for a in articles if a['id'] == result['id']), None)
                if article:
                    results.append({
                        'article': article,
                        'similarity': result['similarity'],
                        'rank': i + 1
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"유사 기사 검색 중 오류 발생: {e}")
            return []
    
    def _get_articles_by_ids(self, article_ids: List[str]) -> List[Dict]:
        """ID로 기사 조회"""
        db = next(get_db())
        try:
            articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
            
            return [
                {
                    'id': article.id,
                    'art_id': article.art_id,
                    'title': article.title,
                    'summary': article.summary,
                    'service_daytime': article.service_daytime,
                    'article_url': article.article_url
                }
                for article in articles
            ]
            
        finally:
            db.close()
    
    def _save_index_to_db(self, index_name: str, index_id: str, dimensions: int):
        """인덱스 정보를 데이터베이스에 저장"""
        db = next(get_db())
        try:
            vector_index = VectorIndex(
                index_name=index_name,
                index_id=index_id,
                dimensions=dimensions,
                is_active=True
            )
            
            db.add(vector_index)
            db.commit()
            
        except Exception as e:
            logger.error(f"인덱스 정보 저장 중 오류 발생: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _update_index_deployment(self, deployed_index_id: str):
        """인덱스 배포 정보 업데이트"""
        db = next(get_db())
        try:
            vector_index = db.query(VectorIndex).filter(
                VectorIndex.index_id == self.index_id
            ).first()
            
            if vector_index:
                vector_index.deployed_index_id = deployed_index_id
                vector_index.is_active = True
                vector_index.updated_at = datetime.utcnow()
                db.commit()
                
        except Exception as e:
            logger.error(f"인덱스 배포 정보 업데이트 중 오류 발생: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _update_articles_embedded(self, article_ids: List[str]):
        """기사 임베딩 완료 상태 업데이트"""
        db = next(get_db())
        try:
            db.query(Article).filter(
                Article.id.in_(article_ids)
            ).update({
                'is_embedded': True,
                'embedding_created_at': datetime.utcnow()
            })
            
            db.commit()
            
        except Exception as e:
            logger.error(f"기사 임베딩 상태 업데이트 중 오류 발생: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _update_index_stats(self, indexed_count: int):
        """인덱스 통계 업데이트"""
        db = next(get_db())
        try:
            vector_index = db.query(VectorIndex).filter(
                VectorIndex.index_id == self.index_id
            ).first()
            
            if vector_index:
                vector_index.total_vectors += indexed_count
                vector_index.last_updated = datetime.utcnow()
                db.commit()
                
        except Exception as e:
            logger.error(f"인덱스 통계 업데이트 중 오류 발생: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_index_status(self) -> Dict:
        """인덱스 상태 조회"""
        try:
            if not self.index_id:
                return {'status': 'not_created'}
            
            index_status = self.vertex_ai_client.get_index_status(self.index_id)
            endpoint_status = self.vertex_ai_client.get_endpoint_status(self.endpoint_id) if self.endpoint_id else {}
            
            return {
                'index_status': index_status,
                'endpoint_status': endpoint_status,
                'deployed_index_id': self.deployed_index_id
            }
            
        except Exception as e:
            logger.error(f"인덱스 상태 조회 중 오류 발생: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def delete_index(self) -> bool:
        """인덱스 삭제"""
        try:
            if self.index_id:
                self.vertex_ai_client.delete_index(self.index_id)
            
            if self.endpoint_id:
                self.vertex_ai_client.delete_endpoint(self.endpoint_id)
            
            logger.info("벡터 인덱스 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"벡터 인덱스 삭제 중 오류 발생: {e}")
            return False
