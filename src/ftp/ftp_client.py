"""
FTP 클라이언트 모듈
매일경제 FTP 서버에서 뉴스 기사 파일을 다운로드
"""
import os
import ftplib
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FTPClient:
    """FTP 클라이언트 클래스"""
    
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        download_dir: str = "ftp_downloads"
    ):
        """
        Args:
            host: FTP 서버 주소
            port: FTP 서버 포트
            username: FTP 사용자명
            password: FTP 비밀번호
            download_dir: 다운로드할 로컬 디렉토리
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # FTP 연결 객체
        self.ftp: Optional[ftplib.FTP] = None
    
    def connect(self) -> bool:
        """FTP 서버에 연결"""
        try:
            logger.info(f"FTP 서버 연결 중: {self.host}:{self.port}")
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.host, self.port, timeout=30)
            self.ftp.login(self.username, self.password)
            logger.info("FTP 서버 연결 성공")
            return True
        except Exception as e:
            logger.error(f"FTP 서버 연결 실패: {str(e)}")
            return False
    
    def disconnect(self):
        """FTP 서버 연결 종료"""
        if self.ftp:
            try:
                self.ftp.quit()
                logger.info("FTP 서버 연결 종료")
            except Exception as e:
                logger.error(f"FTP 서버 연결 종료 실패: {str(e)}")
            finally:
                self.ftp = None
    
    def list_files(self, remote_path: str = ".") -> List[Dict]:
        """
        FTP 서버의 파일 목록 조회
        
        Args:
            remote_path: 원격 디렉토리 경로
            
        Returns:
            파일 정보 리스트 [{"name": str, "size": int, "modified": str}]
        """
        if not self.ftp:
            logger.error("FTP 서버에 연결되어 있지 않습니다")
            return []
        
        try:
            files = []
            logger.info(f"파일 목록 조회 중: {remote_path}")
            
            # 파일 목록 조회 (MLSD 명령 사용 시도)
            try:
                for item in self.ftp.mlsd(remote_path):
                    name, facts = item
                    if facts.get("type") == "file":
                        files.append({
                            "name": name,
                            "size": int(facts.get("size", 0)),
                            "modified": facts.get("modify", ""),
                            "path": f"{remote_path}/{name}".replace("//", "/")
                        })
            except (ftplib.error_perm, AttributeError):
                # MLSD가 지원되지 않으면 LIST 사용
                logger.info("MLSD 미지원, LIST 명령 사용")
                self.ftp.cwd(remote_path)
                lines = []
                self.ftp.retrlines("LIST", lines.append)
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 9:
                        size = int(parts[4])
                        name = " ".join(parts[8:])
                        files.append({
                            "name": name,
                            "size": size,
                            "modified": "",
                            "path": f"{remote_path}/{name}".replace("//", "/")
                        })
            
            logger.info(f"파일 {len(files)}개 발견")
            return files
            
        except Exception as e:
            logger.error(f"파일 목록 조회 실패: {str(e)}")
            return []
    
    def download_file(
        self,
        remote_path: str,
        local_filename: Optional[str] = None,
        delete_after_download: bool = False
    ) -> Dict:
        """
        FTP 서버에서 파일 다운로드
        
        Args:
            remote_path: 원격 파일 경로
            local_filename: 로컬 파일명 (None이면 원격 파일명 사용)
            delete_after_download: 다운로드 후 삭제 여부
            
        Returns:
            {"success": bool, "local_path": str, "size": int, "error": str}
        """
        if not self.ftp:
            logger.error("FTP 서버에 연결되어 있지 않습니다")
            return {
                "success": False,
                "local_path": "",
                "size": 0,
                "error": "FTP 서버에 연결되지 않음"
            }
        
        try:
            # 로컬 파일 경로 결정
            remote_filename = os.path.basename(remote_path)
            if not local_filename:
                # 타임스탬프 추가하여 중복 방지
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                local_filename = f"{timestamp}_{remote_filename}"
            
            local_path = self.download_dir / local_filename
            
            logger.info(f"파일 다운로드 시작: {remote_path} -> {local_path}")
            
            # 다운로드 진행
            total_size = 0
            
            def callback(data: bytes):
                nonlocal total_size
                total_size += len(data)
                f.write(data)
            
            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f"RETR {remote_path}", callback)
            
            logger.info(f"파일 다운로드 완료: {local_path} ({total_size} bytes)")
            
            # 다운로드 후 삭제 옵션
            if delete_after_download:
                try:
                    self.ftp.delete(remote_path)
                    logger.info(f"원격 파일 삭제 완료: {remote_path}")
                except Exception as e:
                    logger.warning(f"원격 파일 삭제 실패: {str(e)}")
                    # 삭제 실패해도 다운로드는 성공으로 간주
            
            return {
                "success": True,
                "local_path": str(local_path),
                "size": total_size,
                "remote_path": remote_path,
                "deleted": delete_after_download,
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"파일 다운로드 실패: {str(e)}")
            return {
                "success": False,
                "local_path": "",
                "size": 0,
                "error": str(e)
            }
    
    def download_all_files(
        self,
        remote_path: str = ".",
        delete_after_download: bool = False
    ) -> List[Dict]:
        """
        FTP 서버의 모든 파일 다운로드
        
        Args:
            remote_path: 원격 디렉토리 경로
            delete_after_download: 다운로드 후 삭제 여부
            
        Returns:
            다운로드 결과 리스트
        """
        results = []
        files = self.list_files(remote_path)
        
        logger.info(f"총 {len(files)}개 파일 다운로드 시작")
        
        for file_info in files:
            result = self.download_file(
                file_info["path"],
                delete_after_download=delete_after_download
            )
            result["remote_filename"] = file_info["name"]
            result["remote_size"] = file_info["size"]
            results.append(result)
        
        logger.info(f"다운로드 완료: {len([r for r in results if r['success']])}/{len(files)}개 성공")
        
        return results
    
    def get_connection_info(self) -> Dict:
        """FTP 연결 정보 반환"""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "downloaded_dir": str(self.download_dir),
            "connected": self.ftp is not None
        }


def get_ftp_client(
    environment: str = "test",
    download_dir: str = "ftp_downloads"
) -> FTPClient:
    """
    환경에 따른 FTP 클라이언트 생성
    
    Args:
        environment: "test" 또는 "production"
        download_dir: 다운로드 디렉토리
        
    Returns:
        FTPClient 인스턴스
    """
    if environment == "production":
        # 실제 FTP 서버
        return FTPClient(
            host="210.179.172.10",
            port=8023,
            username="saltlux_vector",
            password="^hfxmfn7^m",
            download_dir=download_dir
        )
    else:
        # 테스트 FTP 서버
        return FTPClient(
            host="210.179.172.2",
            port=8023,
            username="saltlux_vector",
            password="^hfxmfn7^m",
            download_dir=download_dir
        )

