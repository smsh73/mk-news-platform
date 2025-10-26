"""
데이터베이스 연결 및 세션 관리
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
# from google.cloud.sql.connector import Connector  # 테스트용으로 주석 처리
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """데이터베이스 연결 관리자"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_connection()
    
    def _setup_connection(self):
        """데이터베이스 연결 설정"""
        try:
            # Cloud SQL 연결 설정
            if os.getenv('USE_CLOUD_SQL', 'true').lower() == 'true':
                self._setup_cloud_sql_connection()
            else:
                self._setup_local_connection()
            
            # 세션 팩토리 생성
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("데이터베이스 연결이 성공적으로 설정되었습니다.")
            
        except Exception as e:
            logger.error(f"데이터베이스 연결 설정 중 오류 발생: {e}")
            raise
    
    def _setup_cloud_sql_connection(self):
        """Cloud SQL 연결 설정"""
        project_id = os.getenv('GCP_PROJECT_ID', 'mk-ai-project-473000')
        region = os.getenv('GCP_REGION', 'asia-northeast3')
        instance_name = os.getenv('DB_INSTANCE_NAME', 'mk-news-db')
        database_name = os.getenv('DB_NAME', 'mk_news')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', 'your_password')
        
        # Cloud SQL Private IP 연결
        if os.getenv('DB_PRIVATE_IP', 'true').lower() == 'true':
            # Private IP 연결
            host = f"{instance_name}.{region}.c.{project_id}.internal"
            port = 5432
        else:
            # Public IP 연결 (개발용)
            host = f"{instance_name}.{region}.c.{project_id}.internal"
            port = 5432
        
        # SSL 설정
        ssl_mode = os.getenv('DB_SSL_MODE', 'require')
        
        # 데이터베이스 URL 구성
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{database_name}?sslmode={ssl_mode}"
        
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "sslmode": ssl_mode,
                "sslcert": os.getenv('DB_SSL_CERT', ''),
                "sslkey": os.getenv('DB_SSL_KEY', ''),
                "sslrootcert": os.getenv('DB_SSL_ROOT_CERT', '')
            }
        )
    
    def _setup_local_connection(self):
        """로컬 데이터베이스 연결 설정 (개발용)"""
        database_url = os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:password@localhost:5432/mk_news'
        )
        
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    def get_session(self):
        """데이터베이스 세션 반환"""
        if not self.SessionLocal:
            raise Exception("데이터베이스 연결이 설정되지 않았습니다.")
        return self.SessionLocal()
    
    def create_tables(self):
        """테이블 생성"""
        try:
            from .models import Base
            Base.metadata.create_all(bind=self.engine)
            logger.info("데이터베이스 테이블이 성공적으로 생성되었습니다.")
        except Exception as e:
            logger.error(f"테이블 생성 중 오류 발생: {e}")
            raise
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()
            logger.info("데이터베이스 연결이 종료되었습니다.")

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()

def get_db():
    """의존성 주입을 위한 데이터베이스 세션 생성기"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """데이터베이스 초기화"""
    db_manager.create_tables()
