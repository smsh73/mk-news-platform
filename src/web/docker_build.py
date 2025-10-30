"""
Docker 이미지 빌드 및 관리 모듈
"""
import os
import subprocess
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DockerBuilder:
    """Docker 이미지 빌드 및 Container Registry 푸시"""
    
    def __init__(self, project_id: str, region: str, repo: str):
        self.project_id = project_id
        self.region = region
        self.repo = repo
        
    def build_and_push_admin_image(self, timeout: int = 1800, force_rebuild: bool = False) -> Dict:
        """
        관리자 애플리케이션 Docker 이미지 빌드 및 푸시
        
        Args:
            timeout: 빌드 타임아웃 (초)
            force_rebuild: 강제 재빌드 여부 (이미지가 있어도 다시 빌드)
        
        Returns:
            Dict: {"success": bool, "logs": List[str], "image_url": str}
        """
        image_name = "mk-news-admin"
        image_url = f"{self.region}-docker.pkg.dev/{self.project_id}/{self.repo}/{image_name}:latest"
        
        try:
            logger.info(f"Docker 이미지 빌드 시작: {image_url}")
            
            result = subprocess.run(
                [
                    'gcloud', 'builds', 'submit',
                    '--config', 'cloudbuild-admin.yaml',
                    '--timeout', str(timeout),
                    '.'
                ],
                cwd='.',  # 프로젝트 루트 디렉토리
                capture_output=True,
                text=True,
                timeout=timeout + 60  # 여유 시간 추가
            )
            
            logs = result.stdout.split('\n') + result.stderr.split('\n')
            
            if result.returncode == 0:
                logger.info("Docker 이미지 빌드 성공")
                return {
                    "success": True,
                    "logs": logs,
                    "image_url": image_url
                }
            else:
                logger.error(f"Docker 이미지 빌드 실패: {result.stderr}")
                return {
                    "success": False,
                    "logs": logs,
                    "image_url": image_url,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Docker 빌드 타임아웃")
            return {
                "success": False,
                "logs": ["빌드 타임아웃"],
                "image_url": image_url,
                "error": "타임아웃"
            }
        except Exception as e:
            logger.error(f"Docker 빌드 예외: {e}")
            return {
                "success": False,
                "logs": [str(e)],
                "image_url": image_url,
                "error": str(e)
            }
    
    def check_image_exists(self) -> bool:
        """
        Artifact Registry에 이미지가 이미 존재하는지 확인
        
        Returns:
            bool: 이미지 존재 여부
        """
        image_name = "mk-news-admin"
        image_url = f"{self.region}-docker.pkg.dev/{self.project_id}/{self.repo}/{image_name}:latest"
        
        try:
            result = subprocess.run(
                [
                    'gcloud', 'artifacts', 'docker', 'images', 'list',
                    f'{self.region}-docker.pkg.dev/{self.project_id}/{self.repo}',
                    '--format=json'
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # JSON 결과에서 이미지 존재 여부 확인
                import json
                images = json.loads(result.stdout)
                return any(image.get('package', '').endswith(f'/{image_name}') for image in images)
            
            return False
        except Exception as e:
            logger.error(f"이미지 존재 확인 실패: {e}")
            return False


def get_docker_builder() -> DockerBuilder:
    """Docker 빌더 인스턴스 생성"""
    project_id = os.getenv('GCP_PROJECT_ID', 'mk-ai-project-473000')
    region = os.getenv('GCP_REGION', 'asia-northeast3')
    repo = os.getenv('ARTIFACT_REGISTRY_REPO', 'mk-news-repo')
    
    return DockerBuilder(project_id, region, repo)
