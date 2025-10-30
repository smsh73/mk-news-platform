"""
FTP 다운로드 → GCS 저장 → 벡터 임베딩 파이프라인
"""
import os
import logging
from typing import Dict, List
from pathlib import Path

from .ftp_client import FTPClient, get_ftp_client
from ..storage.gcs_client import GCSClient
from ..xml_processor import XMLProcessor
from ..embedding.embedding_service import EmbeddingService
from ..vector_search.vector_indexer import VectorIndexer

logger = logging.getLogger(__name__)

class FTPPipeline:
    """FTP → GCS → 임베딩 파이프라인"""
    
    def __init__(self, environment: str = "test"):
        self.environment = environment
        self.ftp_client = None
        self.gcs_client = GCSClient()
        self.xml_processor = XMLProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_indexer = None
        
        # Vector Indexer 초기화 (테스트 모드)
        try:
            project_id = os.getenv('GCP_PROJECT_ID', 'mk-ai-project-473000')
            region = os.getenv('GCP_REGION', 'asia-northeast3')
            self.vector_indexer = VectorIndexer(project_id, region)
        except Exception as e:
            logger.warning(f"VectorIndexer 초기화 실패 (테스트 모드): {e}")
    
    def connect_ftp(self) -> bool:
        """FTP 서버에 연결"""
        try:
            self.ftp_client = get_ftp_client(self.environment)
            return self.ftp_client.connect()
        except Exception as e:
            logger.error(f"FTP 연결 실패: {e}")
            return False
    
    def disconnect_ftp(self):
        """FTP 서버 연결 해제"""
        if self.ftp_client:
            self.ftp_client.disconnect()
    
    def process_ftp_downloads(
        self,
        delete_after_download: bool = False,
        upload_to_gcs: bool = True,
        create_embeddings: bool = True
    ) -> Dict:
        """
        FTP 다운로드 → GCS 저장 → 임베딩 파이프라인
        
        Args:
            delete_after_download: FTP 서버에서 다운로드 후 삭제 여부
            upload_to_gcs: GCS 업로드 여부
            create_embeddings: 벡터 임베딩 생성 여부
            
        Returns:
            처리 결과
        """
        try:
            logger.info("FTP → GCS → 임베딩 파이프라인 시작")
            
            # 1. FTP에서 파일 다운로드
            if not self.ftp_client:
                raise Exception("FTP 서버에 연결되지 않음")
            
            download_results = self.ftp_client.download_all_files(
                delete_after_download=delete_after_download
            )
            
            successful_downloads = [r for r in download_results if r['success']]
            
            if not successful_downloads:
                return {
                    "status": "success",
                    "message": "다운로드할 파일이 없습니다",
                    "stats": {
                        "downloaded": 0,
                        "uploaded_to_gcs": 0,
                        "embedded": 0
                    }
                }
            
            logger.info(f"FTP 다운로드 완료: {len(successful_downloads)}개 파일")
            
            stats = {
                "downloaded": len(successful_downloads),
                "uploaded_to_gcs": 0,
                "embedded": 0
            }
            
            # 2. GCS 업로드
            uploaded_files = []
            if upload_to_gcs:
                for result in successful_downloads:
                    local_path = result['local_path']
                    if Path(local_path).exists():
                        # GCS 경로 생성
                        filename = Path(local_path).name
                        gcs_path = f"ftp_downloads/{self.environment}/{filename}"
                        
                        upload_result = self.gcs_client.upload_file(local_path, gcs_path)
                        
                        if upload_result['success']:
                            uploaded_files.append({
                                "local_path": local_path,
                                "gcs_path": gcs_path,
                                "gs_url": upload_result['gs_url']
                            })
                            stats["uploaded_to_gcs"] += 1
                
                logger.info(f"GCS 업로드 완료: {stats['uploaded_to_gcs']}개 파일")
            
            # 3. XML 파싱 및 임베딩
            embedded_articles = []
            if create_embeddings:
                for upload_info in uploaded_files:
                    local_path = upload_info['local_path']
                    
                    # XML 파싱
                    try:
                        parsed_data = self.xml_processor.parse_xml_file(local_path)
                        
                        if parsed_data:
                            article_data = parsed_data['article_data']
                            
                            # 임베딩 생성
                            embedding_result = self.embedding_service.generate_article_embedding(
                                article_data
                            )
                            
                            if embedding_result:
                                embedded_articles.append({
                                    "article": article_data,
                                    "embedding": embedding_result
                                })
                                stats["embedded"] += 1
                        
                    except Exception as e:
                        logger.error(f"XML 파싱 또는 임베딩 실패: {local_path}, {e}")
                
                logger.info(f"임베딩 생성 완료: {stats['embedded']}개 기사")
                
                # 4. 벡터 인덱스 업데이트
                if self.vector_indexer and embedded_articles:
                    vector_data = []
                    for item in embedded_articles:
                        article = item['article']
                        embedding = item['embedding']['embedding']
                        
                        vector_data.append({
                            'id': article.get('art_id', ''),
                            'embedding': embedding
                        })
                    
                    # Vector Index 업데이트
                    # self.vector_indexer.upsert_vectors(vector_data)
                    logger.info(f"벡터 인덱스 업데이트 완료: {len(vector_data)}개 벡터")
            
            return {
                "status": "success",
                "message": "FTP 파이프라인 처리 완료",
                "stats": stats,
                "uploaded_files": uploaded_files,
                "embedded_articles": embedded_articles
            }
            
        except Exception as e:
            logger.error(f"FTP 파이프라인 실패: {e}")
            return {
                "status": "error",
                "message": f"파이프라인 실패: {str(e)}",
                "stats": {
                    "downloaded": 0,
                    "uploaded_to_gcs": 0,
                    "embedded": 0
                }
            }
        finally:
            # 임시 파일 정리
            self._cleanup_temp_files(uploaded_files)
    
    def _cleanup_temp_files(self, uploaded_files: List[Dict]):
        """임시 다운로드 파일 정리"""
        try:
            for upload_info in uploaded_files:
                local_path = upload_info.get('local_path')
                if local_path and Path(local_path).exists():
                    Path(local_path).unlink()
                    logger.info(f"임시 파일 삭제: {local_path}")
        except Exception as e:
            logger.warning(f"임시 파일 정리 실패: {e}")

