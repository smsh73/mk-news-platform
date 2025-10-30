"""
Google Cloud Storage 클라이언트
"""
import os
import logging
from typing import Optional, List
from pathlib import Path
from datetime import datetime

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    logger.warning("google-cloud-storage not available")

logger = logging.getLogger(__name__)

class GCSClient:
    """Google Cloud Storage 클라이언트"""
    
    def __init__(self, bucket_name: str = None, project_id: str = None):
        """
        Args:
            bucket_name: GCS 버킷 이름
            project_id: GCP 프로젝트 ID
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'mk-ai-project-473000')
        self.bucket_name = bucket_name or f"{self.project_id}-mk-news-data"
        self.client = None
        self.bucket = None
        
        if GCS_AVAILABLE:
            self._initialize_client()
    
    def _initialize_client(self):
        """GCS 클라이언트 초기화"""
        try:
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"GCS 클라이언트 초기화 완료 (버킷: {self.bucket_name})")
            
        except Exception as e:
            logger.info(f"GCS 클라이언트 초기화 실패 (테스트 모드): {e}")
            self.client = None
            self.bucket = None
    
    def upload_file(self, local_file_path: str, remote_file_path: str) -> dict:
        """
        파일을 GCS에 업로드
        
        Args:
            local_file_path: 로컬 파일 경로
            remote_file_path: GCS에 저장할 경로
            
        Returns:
            {"success": bool, "gs_url": str, "error": str}
        """
        if not self.bucket:
            return {
                "success": False,
                "gs_url": "",
                "error": "GCS 클라이언트가 초기화되지 않았습니다"
            }
        
        try:
            logger.info(f"GCS 업로드 시작: {local_file_path} -> {remote_file_path}")
            
            blob = self.bucket.blob(remote_file_path)
            blob.upload_from_filename(local_file_path)
            
            gs_url = f"gs://{self.bucket_name}/{remote_file_path}"
            
            logger.info(f"GCS 업로드 완료: {gs_url}")
            
            return {
                "success": True,
                "gs_url": gs_url,
                "bucket": self.bucket_name,
                "path": remote_file_path,
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"GCS 업로드 실패: {e}")
            return {
                "success": False,
                "gs_url": "",
                "error": str(e)
            }
    
    def upload_directory(self, local_dir: str, remote_prefix: str = "ftp_downloads") -> List[dict]:
        """
        디렉토리 전체를 GCS에 업로드
        
        Args:
            local_dir: 로컬 디렉토리 경로
            remote_prefix: GCS 경로 prefix
            
        Returns:
            업로드 결과 리스트
        """
        results = []
        local_path = Path(local_dir)
        
        if not local_path.exists():
            logger.error(f"로컬 디렉토리가 존재하지 않습니다: {local_dir}")
            return results
        
        # XML 파일만 필터링
        for file_path in local_path.glob("*.xml"):
            rel_path = file_path.relative_to(local_path)
            remote_path = f"{remote_prefix}/{rel_path}"
            
            result = self.upload_file(str(file_path), remote_path)
            results.append(result)
        
        logger.info(f"GCS 디렉토리 업로드 완료: {len(results)}개 파일")
        return results
    
    def list_files(self, prefix: str = "") -> List[dict]:
        """
        GCS 버킷의 파일 목록 조회
        
        Args:
            prefix: 경로 prefix
            
        Returns:
            파일 정보 리스트
        """
        if not self.bucket:
            return []
        
        try:
            files = []
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            for blob in blobs:
                files.append({
                    "name": blob.name,
                    "size": blob.size,
                    "created": blob.time_created.isoformat() if blob.time_created else "",
                    "updated": blob.updated.isoformat() if blob.updated else "",
                    "url": f"gs://{self.bucket_name}/{blob.name}"
                })
            
            return files
            
        except Exception as e:
            logger.error(f"GCS 파일 목록 조회 실패: {e}")
            return []
    
    def delete_file(self, remote_file_path: str) -> dict:
        """
        GCS에서 파일 삭제
        
        Args:
            remote_file_path: GCS 파일 경로
            
        Returns:
            {"success": bool, "error": str}
        """
        if not self.bucket:
            return {
                "success": False,
                "error": "GCS 클라이언트가 초기화되지 않았습니다"
            }
        
        try:
            blob = self.bucket.blob(remote_file_path)
            blob.delete()
            
            logger.info(f"GCS 파일 삭제 완료: {remote_file_path}")
            
            return {
                "success": True,
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"GCS 파일 삭제 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_bucket_info(self) -> dict:
        """버킷 정보 조회"""
        return {
            "bucket_name": self.bucket_name,
            "project_id": self.project_id,
            "initialized": self.bucket is not None
        }

