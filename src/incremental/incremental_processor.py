"""
증분형 벡터 임베딩 및 중복 필터링 시스템
"""
import os
import logging
import hashlib
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..database.connection import get_db
from ..database.models import Article, ProcessingLog, VectorIndex
from ..embedding.embedding_service import EmbeddingService
from ..vector_search.vector_indexer import VectorIndexer
from .duplicate_detector import DuplicateDetector
from .content_hasher import ContentHasher

logger = logging.getLogger(__name__)

class IncrementalProcessor:
    """증분형 처리기"""
    
    def __init__(self, project_id: str = "mk-ai-project-473000", region: str = "asia-northeast3"):
        self.project_id = project_id
        self.region = region
        self.embedding_service = EmbeddingService()
        self.vector_indexer = VectorIndexer(project_id, region)
        self.duplicate_detector = DuplicateDetector()
        self.content_hasher = ContentHasher()
        self.batch_size = 50
        self.max_workers = 4
    
    def process_incremental_articles(self, xml_directory: str, 
                                   last_processed_time: Optional[datetime] = None) -> Dict:
        """증분형 기사 처리"""
        try:
            start_time = datetime.utcnow()
            
            # 1. 새로운 XML 파일 감지
            new_files = self._detect_new_files(xml_directory, last_processed_time)
            
            if not new_files:
                return {
                    'status': 'success',
                    'message': '처리할 새로운 파일이 없습니다.',
                    'processed_count': 0,
                    'duplicate_count': 0,
                    'error_count': 0
                }
            
            # 2. 중복 파일 필터링
            unique_files = self._filter_duplicate_files(new_files)
            
            # 3. 배치 처리
            results = self._process_batch_files(unique_files)
            
            # 4. 벡터 임베딩 생성
            embedding_results = self._process_embeddings(results['processed_articles'])
            
            # 5. 벡터 인덱스 업데이트
            index_results = self._update_vector_index(embedding_results)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'status': 'success',
                'message': '증분형 처리 완료',
                'total_files': len(new_files),
                'unique_files': len(unique_files),
                'processed_count': results['processed_count'],
                'duplicate_count': results['duplicate_count'],
                'error_count': results['error_count'],
                'embedded_count': embedding_results['embedded_count'],
                'indexed_count': index_results['indexed_count'],
                'processing_time': processing_time,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"증분형 처리 중 오류 발생: {e}")
            return {
                'status': 'error',
                'message': f'증분형 처리 실패: {str(e)}',
                'processed_count': 0,
                'duplicate_count': 0,
                'error_count': 0
            }
    
    def _detect_new_files(self, xml_directory: str, 
                         last_processed_time: Optional[datetime]) -> List[str]:
        """새로운 파일 감지"""
        try:
            from pathlib import Path
            
            xml_path = Path(xml_directory)
            if not xml_path.exists():
                return []
            
            # 모든 XML 파일 조회
            all_files = list(xml_path.glob("*.xml"))
            
            if not last_processed_time:
                return [str(f) for f in all_files]
            
            # 마지막 처리 시간 이후 파일만 필터링
            new_files = []
            for file_path in all_files:
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime > last_processed_time:
                    new_files.append(str(file_path))
            
            logger.info(f"새로운 파일 {len(new_files)}개 감지")
            return new_files
            
        except Exception as e:
            logger.error(f"새로운 파일 감지 중 오류 발생: {e}")
            return []
    
    def _filter_duplicate_files(self, file_paths: List[str]) -> List[str]:
        """중복 파일 필터링"""
        try:
            unique_files = []
            processed_hashes = set()
            
            for file_path in file_paths:
                # 파일 해시 계산
                file_hash = self.content_hasher.calculate_file_hash(file_path)
                
                if file_hash not in processed_hashes:
                    processed_hashes.add(file_hash)
                    unique_files.append(file_path)
                else:
                    logger.info(f"중복 파일 제외: {file_path}")
            
            logger.info(f"중복 제거 후 {len(unique_files)}개 파일")
            return unique_files
            
        except Exception as e:
            logger.error(f"중복 파일 필터링 중 오류 발생: {e}")
            return file_paths
    
    def _process_batch_files(self, file_paths: List[str]) -> Dict:
        """배치 파일 처리"""
        try:
            results = {
                'processed_count': 0,
                'duplicate_count': 0,
                'error_count': 0,
                'processed_articles': []
            }
            
            # 멀티스레딩으로 병렬 처리
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {
                    executor.submit(self._process_single_file, file_path): file_path 
                    for file_path in file_paths
                }
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        
                        if result['status'] == 'success':
                            results['processed_count'] += 1
                            results['processed_articles'].append(result['article'])
                        elif result['status'] == 'duplicate':
                            results['duplicate_count'] += 1
                        else:
                            results['error_count'] += 1
                            
                    except Exception as e:
                        logger.error(f"파일 처리 중 오류 발생: {file_path}, {e}")
                        results['error_count'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"배치 파일 처리 중 오류 발생: {e}")
            return {
                'processed_count': 0,
                'duplicate_count': 0,
                'error_count': 0,
                'processed_articles': []
            }
    
    def _process_single_file(self, file_path: str) -> Dict:
        """단일 파일 처리"""
        try:
            from ..xml_parser import XMLParser
            from ..xml_processor import XMLProcessor
            
            # XML 파싱
            parser = XMLParser()
            parsed_data = parser.parse_xml_file(file_path)
            
            if not parsed_data:
                return {
                    'status': 'error',
                    'message': 'XML 파싱 실패'
                }
            
            # 중복 체크
            content_hash = parsed_data['content_hash']
            is_duplicate = self._check_content_duplicate(content_hash)
            
            if is_duplicate:
                return {
                    'status': 'duplicate',
                    'message': '중복 콘텐츠'
                }
            
            # 데이터베이스 저장
            processor = XMLProcessor()
            save_result = processor._save_to_database(parsed_data)
            
            if save_result['status'] == 'success':
                return {
                    'status': 'success',
                    'message': '처리 완료',
                    'article': {
                        'id': save_result['article_id'],
                        'art_id': parsed_data['article_data']['art_id'],
                        'title': parsed_data['article_data']['title'],
                        'content_hash': content_hash
                    }
                }
            else:
                return {
                    'status': 'error',
                    'message': save_result['message']
                }
                
        except Exception as e:
            logger.error(f"단일 파일 처리 중 오류 발생: {file_path}, {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _check_content_duplicate(self, content_hash: str) -> bool:
        """콘텐츠 중복 체크"""
        try:
            db = next(get_db())
            try:
                existing_article = db.query(Article).filter(
                    Article.content_hash == content_hash
                ).first()
                
                return existing_article is not None
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"콘텐츠 중복 체크 중 오류 발생: {e}")
            return False
    
    def _process_embeddings(self, articles: List[Dict]) -> Dict:
        """임베딩 처리"""
        try:
            if not articles:
                return {
                    'embedded_count': 0,
                    'embeddings': []
                }
            
            # 배치별로 임베딩 생성
            embeddings = []
            embedded_count = 0
            
            for i in range(0, len(articles), self.batch_size):
                batch_articles = articles[i:i + self.batch_size]
                
                # 기사 정보 조회
                article_data = self._get_articles_data(batch_articles)
                
                # 임베딩 생성
                batch_embeddings = self.embedding_service.batch_generate_embeddings(article_data)
                
                # 데이터베이스 업데이트
                for embedding_info in batch_embeddings:
                    self._update_article_embedding(embedding_info)
                    embeddings.append(embedding_info)
                    embedded_count += 1
            
            return {
                'embedded_count': embedded_count,
                'embeddings': embeddings
            }
            
        except Exception as e:
            logger.error(f"임베딩 처리 중 오류 발생: {e}")
            return {
                'embedded_count': 0,
                'embeddings': []
            }
    
    def _get_articles_data(self, articles: List[Dict]) -> List[Dict]:
        """기사 데이터 조회"""
        try:
            db = next(get_db())
            try:
                article_ids = [article['id'] for article in articles]
                db_articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
                
                return [
                    {
                        'id': article.id,
                        'art_id': article.art_id,
                        'title': article.title,
                        'body': article.body,
                        'summary': article.summary
                    }
                    for article in db_articles
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"기사 데이터 조회 중 오류 발생: {e}")
            return []
    
    def _update_article_embedding(self, embedding_info: Dict):
        """기사 임베딩 정보 업데이트"""
        try:
            db = next(get_db())
            try:
                article = db.query(Article).filter(
                    Article.id == embedding_info['article_id']
                ).first()
                
                if article:
                    article.embedding_vector = embedding_info['embedding']
                    article.embedding_model = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
                    article.embedding_created_at = datetime.utcnow()
                    article.is_embedded = True
                    
                    db.commit()
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"기사 임베딩 정보 업데이트 중 오류 발생: {e}")
    
    def _update_vector_index(self, embeddings: List[Dict]) -> Dict:
        """벡터 인덱스 업데이트"""
        try:
            if not embeddings:
                return {
                    'indexed_count': 0
                }
            
            # 벡터 데이터 준비
            vector_data = []
            for embedding_info in embeddings:
                vector_data.append({
                    'id': embedding_info['article_id'],
                    'embedding': embedding_info['embedding']
                })
            
            # Vertex AI 인덱스 업데이트
            success = self.vector_indexer.vertex_ai_client.upsert_vectors(
                self.vector_indexer.index_id, vector_data
            )
            
            if success:
                # 데이터베이스 통계 업데이트
                self._update_index_stats(len(embeddings))
                
                return {
                    'indexed_count': len(embeddings)
                }
            else:
                return {
                    'indexed_count': 0
                }
                
        except Exception as e:
            logger.error(f"벡터 인덱스 업데이트 중 오류 발생: {e}")
            return {
                'indexed_count': 0
            }
    
    def _update_index_stats(self, indexed_count: int):
        """인덱스 통계 업데이트"""
        try:
            db = next(get_db())
            try:
                vector_index = db.query(VectorIndex).filter(
                    VectorIndex.is_active == True
                ).first()
                
                if vector_index:
                    vector_index.total_vectors += indexed_count
                    vector_index.last_updated = datetime.utcnow()
                    db.commit()
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"인덱스 통계 업데이트 중 오류 발생: {e}")
    
    def get_processing_status(self) -> Dict:
        """처리 상태 조회"""
        try:
            db = next(get_db())
            try:
                stats = {
                    'total_articles': db.query(Article).count(),
                    'processed_articles': db.query(Article).filter(Article.is_processed == True).count(),
                    'embedded_articles': db.query(Article).filter(Article.is_embedded == True).count(),
                    'recent_articles': db.query(Article).filter(
                        Article.created_at >= datetime.utcnow() - timedelta(days=1)
                    ).count(),
                    'error_articles': db.query(Article).filter(
                        Article.processing_error.isnot(None)
                    ).count()
                }
                
                return stats
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"처리 상태 조회 중 오류 발생: {e}")
            return {}
    
    def cleanup_duplicates(self) -> Dict:
        """중복 기사 정리"""
        try:
            db = next(get_db())
            try:
                # 중복 콘텐츠 해시 찾기
                duplicate_hashes = db.query(Article.content_hash).filter(
                    Article.content_hash.isnot(None)
                ).group_by(Article.content_hash).having(
                    db.func.count(Article.id) > 1
                ).all()
                
                duplicate_count = 0
                for hash_tuple in duplicate_hashes:
                    content_hash = hash_tuple[0]
                    
                    # 중복 기사들 조회 (첫 번째 제외)
                    duplicate_articles = db.query(Article).filter(
                        Article.content_hash == content_hash
                    ).order_by(Article.created_at).all()
                    
                    # 첫 번째를 제외한 나머지 삭제
                    for article in duplicate_articles[1:]:
                        db.delete(article)
                        duplicate_count += 1
                
                db.commit()
                
                return {
                    'status': 'success',
                    'duplicate_count': duplicate_count,
                    'message': f'{duplicate_count}개의 중복 기사가 정리되었습니다.'
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"중복 기사 정리 중 오류 발생: {e}")
            return {
                'status': 'error',
                'message': f'중복 기사 정리 실패: {str(e)}'
            }
    
    def get_last_processed_time(self) -> Optional[datetime]:
        """마지막 처리 시간 조회"""
        try:
            db = next(get_db())
            try:
                last_article = db.query(Article).filter(
                    Article.is_processed == True
                ).order_by(Article.created_at.desc()).first()
                
                return last_article.created_at if last_article else None
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"마지막 처리 시간 조회 중 오류 발생: {e}")
            return None
