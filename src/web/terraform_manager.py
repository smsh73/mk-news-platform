"""
Terraform 실행 및 실시간 로그 모니터링 관리자
"""
import os
import subprocess
import threading
import time
from typing import Dict, Callable, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class TerraformManager:
    """Terraform 실행 및 로그 모니터링"""
    
    def __init__(self, terraform_dir: str = "terraform"):
        self.terraform_dir = Path(terraform_dir)
        self.logs = []
        self.status = "idle"  # idle, running, success, error
        self.current_step = None
        self.error_message = None
        self._callback = None
        self._process = None
        self._thread = None
        
    def execute_with_logging(
        self,
        command: list,
        on_log: Optional[Callable] = None,
        timeout: int = 3600
    ) -> tuple[bool, list]:
        """
        Terraform 명령어 실행 및 실시간 로그 수집
        
        Args:
            command: 실행할 terraform 명령어 리스트 (예: ['terraform', 'init'])
            on_log: 로그 수신 시 호출할 콜백 함수
            timeout: 타임아웃 시간 (초)
            
        Returns:
            (성공여부, 로그 리스트)
        """
        self.logs = []
        self.status = "running"
        self.error_message = None
        self._callback = on_log
        
        try:
            # 프로세스 시작
            self._process = subprocess.Popen(
                command,
                cwd=str(self.terraform_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 실시간 로그 읽기
            while True:
                line = self._process.stdout.readline()
                if not line:
                    break
                    
                line = line.rstrip()
                if line:
                    self.logs.append(line)
                    if self._callback:
                        self._callback(line)
                        
            # 프로세스 종료 대기
            return_code = self._process.wait(timeout=timeout)
            
            if return_code == 0:
                self.status = "success"
                return True, self.logs
            else:
                self.status = "error"
                self.error_message = f"Terraform 명령어 실패 (코드: {return_code})"
                return False, self.logs
                
        except subprocess.TimeoutExpired:
            self._process.kill()
            self.status = "error"
            self.error_message = f"타임아웃 발생 (>{timeout}초)"
            return False, self.logs
            
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            logger.error(f"Terraform 실행 오류: {e}")
            return False, self.logs
    
    def init(self, on_log: Optional[Callable] = None) -> tuple[bool, list]:
        """Terraform 초기화"""
        self.current_step = "init"
        return self.execute_with_logging(
            ['terraform', 'init'],
            on_log=on_log,
            timeout=120
        )
    
    def plan(self, on_log: Optional[Callable] = None) -> tuple[bool, list]:
        """Terraform Plan"""
        self.current_step = "plan"
        return self.execute_with_logging(
            ['terraform', 'plan', '-out=tfplan'],
            on_log=on_log,
            timeout=300
        )
    
    def apply(self, on_log: Optional[Callable] = None) -> tuple[bool, list]:
        """Terraform Apply"""
        self.current_step = "apply"
        return self.execute_with_logging(
            ['terraform', 'apply', '-auto-approve'],
            on_log=on_log,
            timeout=1800  # 30분
        )
    
    def get_outputs(self) -> Dict[str, str]:
        """Terraform 출력값 조회"""
        try:
            result = subprocess.run(
                ['terraform', 'output', '-json'],
                cwd=str(self.terraform_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {}
        except Exception as e:
            logger.error(f"Terraform 출력 조회 오류: {e}")
            return {}
    
    def get_workspace_info(self) -> Dict:
        """Terraform 워크스페이스 정보 조회"""
        return {
            "terraform_dir": str(self.terraform_dir),
            "exists": self.terraform_dir.exists(),
            "has_main_tf": (self.terraform_dir / "main.tf").exists(),
            "status": self.status,
            "current_step": self.current_step,
            "error": self.error_message
        }


# 전역 인스턴스
_terraform_manager = None


def get_terraform_manager() -> TerraformManager:
    """Terraform Manager 싱글톤"""
    global _terraform_manager
    if _terraform_manager is None:
        _terraform_manager = TerraformManager()
    return _terraform_manager
