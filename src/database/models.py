"""
매일경제 신문기사 데이터베이스 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Article(Base):
    """기사 메인 테이블"""
    __tablename__ = 'articles'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    art_id = Column(String, unique=True, nullable=False, index=True)  # XML의 art_id
    art_year = Column(Integer, nullable=False, index=True)
    art_no = Column(String, nullable=True)
    title = Column(Text, nullable=False)
    sub_title = Column(Text, nullable=True)
    writers = Column(Text, nullable=True)
    service_daytime = Column(DateTime, nullable=True, index=True)
    reg_dt = Column(DateTime, nullable=True)
    mod_dt = Column(DateTime, nullable=True)
    article_url = Column(Text, nullable=True)
    
    # 기사 분류 정보
    media_code = Column(String, nullable=True)
    gubun = Column(String, nullable=True)
    free_type = Column(String, nullable=True)
    pub_div = Column(String, nullable=True)
    art_org_class = Column(String, nullable=True)
    
    # 본문 및 요약
    body = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    
    # 벡터 임베딩 관련
    embedding_vector = Column(JSON, nullable=True)  # 벡터 임베딩 저장
    embedding_model = Column(String, nullable=True)  # 사용된 임베딩 모델
    embedding_created_at = Column(DateTime, nullable=True)
    
    # 중복 체크용 해시
    content_hash = Column(String, nullable=True, index=True)
    
    # 처리 상태
    is_processed = Column(Boolean, default=False)
    is_embedded = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ArticleCategory(Base):
    """기사 분류 정보"""
    __tablename__ = 'article_categories'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, nullable=False, index=True)
    code_id = Column(String, nullable=True)
    code_nm = Column(String, nullable=True)
    large_code_id = Column(String, nullable=True)
    large_code_nm = Column(String, nullable=True)
    middle_code_id = Column(String, nullable=True)
    middle_code_nm = Column(String, nullable=True)
    small_code_id = Column(String, nullable=True)
    small_code_nm = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ArticleImage(Base):
    """기사 이미지 정보"""
    __tablename__ = 'article_images'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, nullable=False, index=True)
    image_url = Column(Text, nullable=True)
    image_caption = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ArticleKeyword(Base):
    """기사 키워드"""
    __tablename__ = 'article_keywords'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, nullable=False, index=True)
    keyword = Column(String, nullable=False, index=True)
    keyword_type = Column(String, nullable=True)  # person, place, company, event, issue 등
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ArticleStockCode(Base):
    """기사 관련 주식 코드"""
    __tablename__ = 'article_stock_codes'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, nullable=False, index=True)
    stock_code = Column(String, nullable=False, index=True)
    stock_name = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ProcessingLog(Base):
    """처리 로그"""
    __tablename__ = 'processing_logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, nullable=False, index=True)
    process_type = Column(String, nullable=False)  # xml_parse, embedding, indexing 등
    status = Column(String, nullable=False)  # success, error, processing
    message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)  # 처리 시간 (초)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class VectorIndex(Base):
    """벡터 인덱스 관리"""
    __tablename__ = 'vector_indexes'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    index_name = Column(String, nullable=False, unique=True)
    index_id = Column(String, nullable=True)  # Vertex AI 인덱스 ID
    endpoint_id = Column(String, nullable=True)  # Vertex AI 엔드포인트 ID
    deployed_index_id = Column(String, nullable=True)  # 배포된 인덱스 ID
    
    # 인덱스 설정
    dimensions = Column(Integer, nullable=False, default=768)
    approximate_neighbors_count = Column(Integer, nullable=False, default=150)
    distance_measure_type = Column(String, nullable=False, default="DOT_PRODUCT_DISTANCE")
    
    # 상태
    is_active = Column(Boolean, default=False)
    total_vectors = Column(Integer, default=0)
    last_updated = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmbeddingModel(Base):
    """임베딩 모델 관리"""
    __tablename__ = 'embedding_models'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String, nullable=False, unique=True)
    model_type = Column(String, nullable=False)  # sentence-transformers, vertex-ai 등
    model_path = Column(String, nullable=True)
    dimensions = Column(Integer, nullable=False)
    max_sequence_length = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


