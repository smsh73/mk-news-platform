"""
FastAPI 웹 애플리케이션 - 매일경제 신문기사 벡터임베딩 플랫폼
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import uvicorn
import subprocess
import threading
import json

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import StreamingResponse
# from .terraform_manager import get_terraform_manager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Jinja2Templates는 선택적으로 import
try:
    from fastapi.templating import Jinja2Templates
except ImportError:
    Jinja2Templates = None

from ..database.connection import get_db, init_database
from ..database.models import Article, VectorIndex, ProcessingLog
from ..xml_processor import XMLProcessor
from ..vector_search.vector_indexer import VectorIndexer
from ..rag.hybrid_rag_system import HybridRAGSystem
from ..incremental.incremental_processor import IncrementalProcessor
from ..embedding.embedding_service import EmbeddingService
from .docker_build import get_docker_builder
from ..ftp import get_ftp_client
from ..ftp.ftp_pipeline import FTPPipeline
from ..storage.gcs_client import GCSClient
from ..auth import authenticate_user, create_access_token, get_current_user, verify_token

logger = logging.getLogger(__name__)

# FTP 클라이언트 인스턴스 (전역)
ftp_client_instance = None

# FastAPI 앱 생성
app = FastAPI(
    title="매일경제 신문기사 벡터임베딩 플랫폼",
    description="GCP VertexAI 기반 신문기사 벡터임베딩 및 Hybrid RAG 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
# static과 templates 디렉토리가 있을 경우에만 마운트
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    # React 빌드 결과물의 실제 정적 파일 경로
    static_assets_path = os.path.join(static_path, "static")
    if os.path.exists(static_assets_path):
        app.mount("/static", StaticFiles(directory=static_assets_path), name="static")
    else:
        app.mount("/static", StaticFiles(directory=static_path), name="static")
if os.path.exists("templates") and Jinja2Templates is not None:
    templates = Jinja2Templates(directory="templates")
else:
    templates = None

# 전역 변수
project_id = os.getenv('GCP_PROJECT_ID', 'mk-ai-project-473000')
region = os.getenv('GCP_REGION', 'asia-northeast3')

# 서비스 초기화 (테스트 모드)
xml_processor = XMLProcessor()
# GCP 서비스는 테스트 모드에서 비활성화
try:
    vector_indexer = VectorIndexer(project_id, region)
    rag_system = HybridRAGSystem(project_id, region)
    incremental_processor = IncrementalProcessor(project_id, region)
except Exception as e:
    print(f"GCP 서비스 초기화 실패 (테스트 모드): {e}")
    vector_indexer = None
    rag_system = None
    incremental_processor = None

embedding_service = EmbeddingService()

# Pydantic 모델
class LoginRequest(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    query: str
    filters: Optional[Dict] = None
    top_k: int = 10
    similarity_threshold: float = 0.7
    max_context_length: int = 4000
    weights: Optional[Dict] = None

class ProcessXMLRequest(BaseModel):
    xml_directory: str
    batch_size: int = 100
    max_workers: int = 4
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

class AnalysisRequest(BaseModel):
    article_id: int
    timeline_years: int = 3
    analysis_depth: str = "상세"
    include_timeline: bool = True
    include_current: bool = True
    include_future: bool = True

class VectorIndexRequest(BaseModel):
    index_name: str = "mk-news-vector-index"
    dimensions: int = 768
    description: str = "매일경제 신문기사 벡터 인덱스"

class ProcessRequest(BaseModel):
    xml_directory: str
    batch_size: int = 100

class IncrementalProcessRequest(BaseModel):
    xml_directory: str
    last_processed_time: Optional[str] = None

# API 엔드포인트
@app.get("/", response_class=HTMLResponse)
async def root():
    """React 앱 메인 페이지"""
    static_path = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_path, "index.html")
    
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>매일경제 AI 플랫폼</title>
        </head>
        <body>
            <h1>매일경제 신문기사 벡터임베딩 플랫폼에 오신 것을 환영합니다!</h1>
            <p>React 앱이 아직 빌드되지 않았습니다.</p>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/auth/login")
async def login(login_request: LoginRequest):
    """사용자 로그인"""
    try:
        if authenticate_user(login_request.username, login_request.password):
            access_token = create_access_token(data={"sub": login_request.username})
            return {
                "success": True,
                "token": access_token,
                "message": "로그인 성공"
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="사용자명 또는 비밀번호가 올바르지 않습니다."
            )
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/api/auth/verify")
async def verify_token_endpoint(current_user: dict = Depends(get_current_user)):
    """토큰 검증"""
    return {
        "success": True,
        "username": current_user.get("username"),
        "message": "인증된 사용자입니다."
    }

@app.post("/api/process-xml")
async def process_xml_files(request: ProcessRequest, background_tasks: BackgroundTasks):
    """XML 파일 처리"""
    try:
        # 백그라운드에서 처리
        background_tasks.add_task(
            xml_processor.process_xml_files,
            request.xml_directory,
            request.batch_size
        )
        
        return {
            "status": "processing",
            "message": "XML 파일 처리가 시작되었습니다.",
            "xml_directory": request.xml_directory
        }
        
    except Exception as e:
        logger.error(f"XML 파일 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/incremental-process")
async def incremental_process(request: IncrementalProcessRequest, background_tasks: BackgroundTasks):
    """증분형 처리"""
    try:
        last_processed_time = None
        if request.last_processed_time:
            last_processed_time = datetime.fromisoformat(request.last_processed_time)
        
        # 백그라운드에서 처리
        background_tasks.add_task(
            incremental_processor.process_incremental_articles,
            request.xml_directory,
            last_processed_time
        )
        
        return {
            "status": "processing",
            "message": "증분형 처리가 시작되었습니다.",
            "xml_directory": request.xml_directory
        }
        
    except Exception as e:
        logger.error(f"증분형 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_articles(request: QueryRequest):
    """기사 검색 및 질의응답"""
    try:
        result = rag_system.process_query(
            query=request.query,
            filters=request.filters,
            top_k=request.top_k
        )
        
        return result
        
    except Exception as e:
        logger.error(f"기사 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_system_stats():
    """시스템 통계 조회"""
    try:
        stats = rag_system.get_system_stats()
        return stats
        
    except Exception as e:
        logger.error(f"시스템 통계 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/articles")
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """기사 목록 조회"""
    try:
        db = next(get_db())
        try:
            query = db.query(Article).filter(Article.is_processed == True)
            
            # 필터 적용
            if category:
                query = query.filter(Article.art_org_class.contains(category))
            
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Article.service_daytime >= start_dt)
            
            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(Article.service_daytime <= end_dt)
            
            # 페이징
            articles = query.offset(skip).limit(limit).all()
            
            return [
                {
                    "id": article.id,
                    "art_id": article.art_id,
                    "title": article.title,
                    "summary": article.summary,
                    "service_daytime": article.service_daytime.isoformat() if article.service_daytime else None,
                    "article_url": article.article_url,
                    "is_embedded": article.is_embedded
                }
                for article in articles
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"기사 목록 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/articles/{article_id}")
async def get_article(article_id: str):
    """특정 기사 조회"""
    try:
        db = next(get_db())
        try:
            article = db.query(Article).filter(Article.id == article_id).first()
            
            if not article:
                raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다.")
            
            return {
                "id": article.id,
                "art_id": article.art_id,
                "title": article.title,
                "body": article.body,
                "summary": article.summary,
                "writers": article.writers,
                "service_daytime": article.service_daytime.isoformat() if article.service_daytime else None,
                "article_url": article.article_url,
                "is_embedded": article.is_embedded,
                "created_at": article.created_at.isoformat()
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"기사 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vector-index/status")
async def get_vector_index_status():
    """벡터 인덱스 상태 조회"""
    try:
        if not vector_indexer:
            return {'status': 'not_initialized', 'message': 'Vector indexer가 초기화되지 않았습니다.'}
        
        status = vector_indexer.get_index_status()
        return status
        
    except Exception as e:
        logger.error(f"벡터 인덱스 상태 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vector-index/create")
async def create_vector_index():
    """벡터 인덱스 생성"""
    try:
        result = vector_indexer.create_vector_index()
        return result
        
    except Exception as e:
        logger.error(f"벡터 인덱스 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vector-index/deploy")
async def deploy_vector_index():
    """벡터 인덱스 배포"""
    try:
        result = vector_indexer.deploy_index()
        return result
        
    except Exception as e:
        logger.error(f"벡터 인덱스 배포 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vector-index/update")
async def update_vector_index(background_tasks: BackgroundTasks):
    """벡터 인덱스 업데이트"""
    try:
        background_tasks.add_task(vector_indexer.index_articles)
        
        return {
            "status": "processing",
            "message": "벡터 인덱스 업데이트가 시작되었습니다."
        }
        
    except Exception as e:
        logger.error(f"벡터 인덱스 업데이트 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/processing-logs")
async def get_processing_logs(
    skip: int = 0,
    limit: int = 100,
    process_type: Optional[str] = None
):
    """처리 로그 조회"""
    try:
        db = next(get_db())
        try:
            query = db.query(ProcessingLog)
            
            if process_type:
                query = query.filter(ProcessingLog.process_type == process_type)
            
            logs = query.order_by(ProcessingLog.created_at.desc()).offset(skip).limit(limit).all()
            
            return [
                {
                    "id": log.id,
                    "article_id": log.article_id,
                    "process_type": log.process_type,
                    "status": log.status,
                    "message": log.message,
                    "processing_time": log.processing_time,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"처리 로그 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/duplicate-cleanup")
async def cleanup_duplicates():
    """중복 기사 정리"""
    try:
        result = incremental_processor.cleanup_duplicates()
        return result
        
    except Exception as e:
        logger.error(f"중복 기사 정리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 관리자 화면 라우트
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """관리자 대시보드"""
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>매일경제 신문기사 벡터임베딩 플랫폼 - 관리자</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #0056b3; }
            .btn-danger { background: #dc3545; }
            .btn-success { background: #28a745; }
            .status { padding: 5px 10px; border-radius: 4px; color: white; font-size: 12px; }
            .status-success { background: #28a745; }
            .status-error { background: #dc3545; }
            .status-warning { background: #ffc107; color: black; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>매일경제 신문기사 벡터임베딩 플랫폼</h1>
                <p>관리자 대시보드</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>시스템 통계</h3>
                    <div id="stats">
                        <p>로딩 중...</p>
                    </div>
                </div>
                
                <div class="card">
                    <h3>벡터 인덱스 상태</h3>
                    <div id="index-status">
                        <p>로딩 중...</p>
                    </div>
                </div>
                
                <div class="card">
                    <h3>처리 작업</h3>
                    <button class="btn btn-success" onclick="processXML()">XML 처리</button>
                    <button class="btn btn-success" onclick="incrementalProcess()">증분형 처리</button>
                    <button class="btn" onclick="updateIndex()">인덱스 업데이트</button>
                    <button class="btn btn-danger" onclick="cleanupDuplicates()">중복 정리</button>
                </div>
                
                <div class="card">
                    <h3>최근 처리 로그</h3>
                    <div id="logs">
                        <p>로딩 중...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // 시스템 통계 로드
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    
                    document.getElementById('stats').innerHTML = `
                        <p><strong>총 기사:</strong> ${stats.total_articles || 0}</p>
                        <p><strong>처리된 기사:</strong> ${stats.processed_articles || 0}</p>
                        <p><strong>임베딩된 기사:</strong> ${stats.embedded_articles || 0}</p>
                        <p><strong>최근 기사:</strong> ${stats.recent_articles || 0}</p>
                        <p><strong>카테고리:</strong> ${stats.categories || 0}</p>
                    `;
                } catch (error) {
                    document.getElementById('stats').innerHTML = '<p>통계 로드 실패</p>';
                }
            }
            
            // 벡터 인덱스 상태 로드
            async function loadIndexStatus() {
                try {
                    const response = await fetch('/api/vector-index/status');
                    const status = await response.json();
                    
                    document.getElementById('index-status').innerHTML = `
                        <p><strong>상태:</strong> <span class="status status-success">${status.status || 'Unknown'}</span></p>
                        <p><strong>인덱스 ID:</strong> ${status.index_id || 'N/A'}</p>
                        <p><strong>엔드포인트 ID:</strong> ${status.endpoint_id || 'N/A'}</p>
                    `;
                } catch (error) {
                    document.getElementById('index-status').innerHTML = '<p>인덱스 상태 로드 실패</p>';
                }
            }
            
            // 처리 로그 로드
            async function loadLogs() {
                try {
                    const response = await fetch('/api/processing-logs?limit=10');
                    const logs = await response.json();
                    
                    const logsHtml = logs.map(log => `
                        <div style="border-bottom: 1px solid #eee; padding: 10px 0;">
                            <p><strong>${log.process_type}</strong> - ${log.status}</p>
                            <p style="font-size: 12px; color: #666;">${log.message}</p>
                            <p style="font-size: 12px; color: #999;">${log.created_at}</p>
                        </div>
                    `).join('');
                    
                    document.getElementById('logs').innerHTML = logsHtml || '<p>로그가 없습니다.</p>';
                } catch (error) {
                    document.getElementById('logs').innerHTML = '<p>로그 로드 실패</p>';
                }
            }
            
            // XML 처리
            async function processXML() {
                try {
                    const response = await fetch('/api/process-xml', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ xml_directory: '/path/to/xml/files', batch_size: 100 })
                    });
                    const result = await response.json();
                    alert('XML 처리가 시작되었습니다.');
                } catch (error) {
                    alert('XML 처리 시작 실패: ' + error.message);
                }
            }
            
            // 증분형 처리
            async function incrementalProcess() {
                try {
                    const response = await fetch('/api/incremental-process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ xml_directory: '/path/to/xml/files' })
                    });
                    const result = await response.json();
                    alert('증분형 처리가 시작되었습니다.');
                } catch (error) {
                    alert('증분형 처리 시작 실패: ' + error.message);
                }
            }
            
            // 인덱스 업데이트
            async function updateIndex() {
                try {
                    const response = await fetch('/api/vector-index/update', { method: 'POST' });
                    const result = await response.json();
                    alert('벡터 인덱스 업데이트가 시작되었습니다.');
                } catch (error) {
                    alert('인덱스 업데이트 시작 실패: ' + error.message);
                }
            }
            
            // 중복 정리
            async function cleanupDuplicates() {
                try {
                    const response = await fetch('/api/duplicate-cleanup');
                    const result = await response.json();
                    alert(result.message || '중복 정리가 완료되었습니다.');
                } catch (error) {
                    alert('중복 정리 실패: ' + error.message);
                }
            }
            
            // 페이지 로드 시 데이터 로드
            window.onload = function() {
                loadStats();
                loadIndexStatus();
                loadLogs();
                
                // 30초마다 데이터 새로고침
                setInterval(() => {
                    loadStats();
                    loadIndexStatus();
                    loadLogs();
                }, 30000);
            };
        </script>
    </body>
    </html>
    """

# 새로운 엔드포인트들

@app.post("/api/query")
async def query_articles(request: QueryRequest):
    """RAG 시스템 쿼리 (가중치 및 메타데이터 필터링 지원)"""
    try:
        # RAG 시스템으로 쿼리 처리
        result = rag_system.process_query(
            query=request.query,
            filters=request.filters,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            max_context_length=request.max_context_length,
            weights=request.weights
        )
        
        return result
        
    except Exception as e:
        logger.error(f"쿼리 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-xml")
async def process_xml(request: ProcessXMLRequest, background_tasks: BackgroundTasks):
    """XML 파일 벡터임베딩 배치 처리"""
    try:
        # 백그라운드에서 XML 처리 시작
        background_tasks.add_task(
            xml_processor.process_xml_files,
            request.xml_directory,
            request.batch_size,
            request.max_workers,
            request.embedding_model
        )
        
        return {
            "message": "XML 벡터임베딩 처리가 시작되었습니다.",
            "xml_directory": request.xml_directory,
            "batch_size": request.batch_size,
            "max_workers": request.max_workers,
            "embedding_model": request.embedding_model
        }
    except Exception as e:
        logger.error(f"XML 처리 시작 오류: {e}")
        raise HTTPException(status_code=500, detail="XML 처리 시작 실패")

@app.post("/api/extract-metadata")
async def extract_metadata(background_tasks: BackgroundTasks):
    """메타데이터 추출"""
    try:
        background_tasks.add_task(xml_processor.extract_metadata)
        
        return {
            "message": "메타데이터 추출이 시작되었습니다.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"메타데이터 추출 오류: {e}")
        raise HTTPException(status_code=500, detail="메타데이터 추출 실패")

@app.post("/api/index-metadata")
async def index_metadata(background_tasks: BackgroundTasks):
    """메타데이터 인덱싱"""
    try:
        background_tasks.add_task(xml_processor.index_metadata)
        
        return {
            "message": "메타데이터 인덱싱이 시작되었습니다.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"메타데이터 인덱싱 오류: {e}")
        raise HTTPException(status_code=500, detail="메타데이터 인덱싱 실패")

@app.get("/api/processing-stats")
async def get_processing_stats(db = Depends(get_db)):
    """처리 통계 조회"""
    try:
        total_processed = db.query(Article).filter(Article.is_processed == True).count()
        embedded_count = db.query(Article).filter(Article.is_embedded == True).count()
        metadata_extracted = db.query(Article).filter(Article.is_processed == True).count()
        indexed_count = db.query(Article).filter(Article.is_embedded == True).count()
        
        return {
            "total_processed": total_processed,
            "embedded_count": embedded_count,
            "metadata_extracted": metadata_extracted,
            "indexed_count": indexed_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"처리 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="처리 통계 조회 실패")

@app.post("/api/generate-analysis")
async def generate_analysis(request: AnalysisRequest):
    """개별 기사 해설 생성"""
    try:
        # 기사 정보 조회
        db = next(get_db())
        article = db.query(Article).filter(Article.id == request.article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다.")
        
        # 해설 생성 (실제 구현에서는 rag_system의 메서드 호출)
        analysis_result = {
            "article_id": request.article_id,
            "timeline_analysis": f"{request.timeline_years}년간의 관련 기사 타임라인 분석 결과",
            "current_analysis": "현재 기사의 논설 및 주요 내용 분석",
            "future_analysis": "향후 전망 및 추이 분석",
            "reference_articles": [],
            "processing_time": 2.5,
            "analysis_depth": request.analysis_depth
        }
        
        return analysis_result
    except Exception as e:
        logger.error(f"해설 생성 오류: {e}")
        raise HTTPException(status_code=500, detail="해설 생성 실패")

@app.get("/api/analysis-history")
async def get_analysis_history(limit: int = 10, db = Depends(get_db)):
    """해설 히스토리 조회"""
    try:
        # 실제로는 별도의 AnalysisHistory 테이블이 필요하지만, 
        # 여기서는 ProcessingLog를 활용
        logs = db.query(ProcessingLog).filter(
            ProcessingLog.process_type == "analysis"
        ).order_by(ProcessingLog.created_at.desc()).limit(limit).all()
        
        history = []
        for log in logs:
            history.append({
                "article_id": log.article_id,
                "article_title": "N/A",  # 실제로는 Article 테이블과 조인 필요
                "analysis_type": log.process_type,
                "created_at": log.created_at.isoformat(),
                "processing_time": log.processing_time,
                "reference_count": 0  # 실제로는 별도 계산 필요
            })
        
        return history
    except Exception as e:
        logger.error(f"해설 히스토리 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="해설 히스토리 조회 실패")

@app.get("/api/search-history")
async def get_search_history(limit: int = 10, db = Depends(get_db)):
    """검색 히스토리 조회"""
    try:
        # 실제로는 별도의 SearchHistory 테이블이 필요
        logs = db.query(ProcessingLog).filter(
            ProcessingLog.process_type == "search"
        ).order_by(ProcessingLog.created_at.desc()).limit(limit).all()
        
        history = []
        for log in logs:
            history.append({
                "query": log.message,  # 실제로는 별도 필드 필요
                "created_at": log.created_at.isoformat(),
                "result_count": 0,  # 실제로는 별도 계산 필요
                "processing_time": log.processing_time,
                "filters": {}  # 실제로는 별도 필드 필요
            })
        
        return history
    except Exception as e:
        logger.error(f"검색 히스토리 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="검색 히스토리 조회 실패")

# ========================================
# Terraform 관리 API
# ========================================

@app.get("/api/terraform/status")
async def get_terraform_status():
    """Terraform 상태 조회"""
    # manager = get_terraform_manager()
    # return manager.get_workspace_info()
    return {"status": "disabled", "message": "Terraform manager temporarily disabled"}

@app.post("/api/terraform/init")
async def terraform_init(request: dict = None):
    """Terraform 초기화"""
    try:
        # 프로젝트 ID 받기
        project_id = request.get('project_id') if request else None
        
        # 프로젝트 ID가 없으면 gcloud에서 가져오기
        if not project_id:
            try:
                result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    project_id = result.stdout.strip()
                    logger.info(f"gcloud에서 프로젝트 ID 가져옴: {project_id}")
            except Exception as e:
                logger.error(f"gcloud 프로젝트 ID 가져오기 실패: {e}")
        
        # terraform.tfvars 파일 자동 생성
        if project_id:
            tfvars_content = f'''project_id = "{project_id}"
region     = "asia-northeast3"
zone       = "asia-northeast3-a"
'''
            tfvars_path = 'terraform/terraform.tfvars'
            with open(tfvars_path, 'w', encoding='utf-8') as f:
                f.write(tfvars_content)
            logger.info(f"terraform.tfvars 파일 생성 완료: project_id={project_id}")
        
        result = subprocess.run(['terraform', 'init'], cwd='terraform', 
                              capture_output=True, text=True, timeout=120)
        return {
            "success": result.returncode == 0,
            "logs": result.stdout.split('\n') + result.stderr.split('\n'),
            "status": "completed" if result.returncode == 0 else "error"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "logs": []}

@app.post("/api/terraform/plan")
async def terraform_plan(request: dict = None):
    """Terraform Plan"""
    try:
        # terraform.tfvars 파일이 있으면 자동으로 사용됨
        result = subprocess.run(['terraform', 'plan'], 
                              cwd='terraform', capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "logs": result.stdout.split('\n') + result.stderr.split('\n'),
            "status": "completed" if result.returncode == 0 else "error"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "logs": []}

@app.post("/api/docker/build")
async def build_docker_image(request: dict = None):
    """Docker 이미지 빌드 및 푸시"""
    try:
        builder = get_docker_builder()
        force_rebuild = request.get('force_rebuild', False) if request else False
        result = builder.build_and_push_admin_image(force_rebuild=force_rebuild)
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "logs": []}

@app.post("/api/docker/check")
async def check_docker_image(request: dict = None):
    """Docker 이미지 존재 여부 확인"""
    try:
        builder = get_docker_builder()
        exists = builder.check_image_exists()
        return {"exists": exists}
    except Exception as e:
        return {"exists": False, "error": str(e)}

@app.post("/api/terraform/apply")
async def terraform_apply(request: dict = None):
    """
    Terraform Apply
    Docker 이미지가 없으면 자동으로 빌드
    """
    try:
        force_rebuild = request.get('force_rebuild', False) if request else False
        
        # 0. 기존 Cloud Run 서비스 확인
        check_logs = []
        try:
            result = subprocess.run(
                ['gcloud', 'run', 'services', 'list', '--region=asia-northeast3', 
                 '--filter=metadata.name=mk-news-admin', '--format=json'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                import json
                services = json.loads(result.stdout)
                if services:
                    check_logs.append(f"⚠️ 기존 Cloud Run 서비스 발견: {services[0]['metadata']['name']}")
                    check_logs.append(f"   URL: {services[0]['status'].get('url', 'N/A')}")
        except Exception as e:
            check_logs.append(f"기존 서비스 확인 중 오류 (무시): {e}")
        
        # 1. Docker 이미지 확인 및 빌드
        builder = get_docker_builder()
        image_exists = builder.check_image_exists()
        
        build_logs = []
        if not image_exists or force_rebuild:
            # Docker 이미지 빌드
            build_result = builder.build_and_push_admin_image(force_rebuild=force_rebuild)
            build_logs = build_result.get('logs', [])
            
            if not build_result.get('success'):
                return {
                    "success": False,
                    "error": "Docker 이미지 빌드 실패",
                    "logs": check_logs + build_logs
                }
        else:
            build_logs = ["✅ Artifact Registry에 이미지 존재 - 빌드 건너뜀"]
        
        # 2. Artifact Registry 이미지 존재 확인 (필수)
        if not image_exists and not force_rebuild:
            return {
                "success": False,
                "error": "Artifact Registry에 이미지가 없습니다. 강제 재배포를 체크하거나 이미지를 먼저 빌드하세요.",
                "logs": check_logs + build_logs
            }
        
        # 3. Terraform Apply
        result = subprocess.run(['terraform', 'apply', '-auto-approve'], 
                              cwd='terraform', capture_output=True, text=True, timeout=1800)
        
        terraform_logs = result.stdout.split('\n') + result.stderr.split('\n')
        
        all_logs = check_logs + build_logs + ["\n=== Terraform Apply ==="] + terraform_logs
        
        # 4. 배포 성공 시 URL 출력
        if result.returncode == 0:
            try:
                output_result = subprocess.run(
                    ['terraform', 'output', '-raw', 'admin_service_url'],
                    cwd='terraform', capture_output=True, text=True, timeout=30
                )
                if output_result.returncode == 0 and output_result.stdout.strip():
                    all_logs.append(f"\n✅ 배포 완료!")
                    all_logs.append(f"📊 관리자 대시보드 URL: {output_result.stdout.strip()}")
            except Exception as e:
                all_logs.append(f"URL 조회 실패: {e}")
        
        return {
            "success": result.returncode == 0,
            "logs": all_logs,
            "status": "completed" if result.returncode == 0 else "error"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "logs": []}

@app.get("/api/terraform/outputs")
async def get_terraform_outputs():
    """Terraform 출력값 조회"""
    try:
        result = subprocess.run(['terraform', 'output', '-json'], cwd='terraform',
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/terraform/logs")
async def get_terraform_logs():
    """Terraform 로그 조회"""
    return {"status": "no logs", "logs": []}

# ========================================
# FTP 연동 API 엔드포인트
# ========================================

@app.post("/api/ftp/connect")
async def ftp_connect(request: dict = None):
    """FTP 서버에 연결"""
    global ftp_client_instance
    try:
        environment = request.get('environment', 'test') if request else 'test'
        download_dir = request.get('download_dir', 'ftp_downloads') if request else 'ftp_downloads'
        
        ftp_client_instance = get_ftp_client(environment=environment, download_dir=download_dir)
        
        if ftp_client_instance.connect():
            return {
                "success": True,
                "info": ftp_client_instance.get_connection_info()
            }
        else:
            return {
                "success": False,
                "error": "FTP 서버 연결 실패"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/ftp/disconnect")
async def ftp_disconnect():
    """FTP 서버 연결 종료"""
    global ftp_client_instance
    try:
        if ftp_client_instance:
            ftp_client_instance.disconnect()
            ftp_client_instance = None
        return {"success": True, "message": "FTP 연결 종료됨"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/ftp/files")
async def ftp_list_files():
    """FTP 서버의 파일 목록 조회"""
    try:
        if not ftp_client_instance:
            raise HTTPException(status_code=400, detail="FTP 서버에 연결되지 않음")
        
        files = ftp_client_instance.list_files()
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ftp/download")
async def ftp_download(request: dict):
    """FTP 서버에서 파일 다운로드"""
    try:
        if not ftp_client_instance:
            raise HTTPException(status_code=400, detail="FTP 서버에 연결되지 않음")
        
        remote_path = request.get('remote_path')
        local_filename = request.get('local_filename')
        delete_after_download = request.get('delete_after_download', False)
        
        if not remote_path:
            raise HTTPException(status_code=400, detail="remote_path 필수")
        
        result = ftp_client_instance.download_file(
            remote_path,
            local_filename,
            delete_after_download
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ftp/download-all")
async def ftp_download_all(request: dict = None):
    """FTP 서버의 모든 파일 다운로드"""
    try:
        if not ftp_client_instance:
            raise HTTPException(status_code=400, detail="FTP 서버에 연결되지 않음")
        
        remote_path = request.get('remote_path', '.') if request else '.'
        delete_after_download = request.get('delete_after_download', False) if request else False
        
        results = ftp_client_instance.download_all_files(remote_path, delete_after_download)
        
        return {
            "success": True,
            "results": results,
            "total": len(results),
            "succeeded": len([r for r in results if r['success']]),
            "failed": len([r for r in results if not r['success']])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ftp/connection-info")
async def ftp_get_connection_info():
    """FTP 연결 정보 조회"""
    try:
        if not ftp_client_instance:
            return {"connected": False, "error": "FTP 서버에 연결되지 않음"}
        
        return {
            "connected": True,
            "info": ftp_client_instance.get_connection_info()
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}

# FTP 파이프라인 API
@app.post("/api/ftp/pipeline")
async def ftp_pipeline_execute(request: dict = None, background_tasks: BackgroundTasks = None):
    """FTP 다운로드 → GCS 저장 → 벡터 임베딩 파이프라인 실행"""
    try:
        request_data = request or {}
        environment = request_data.get('environment', 'test')
        delete_after_download = request_data.get('delete_after_download', False)
        upload_to_gcs = request_data.get('upload_to_gcs', True)
        process_embeddings = request_data.get('process_embeddings', True)
        upload_to_vector_search = request_data.get('upload_to_vector_search', True)
        
        # 처리 로그 생성
        db = next(get_db())
        log_entry = ProcessingLog(
            process_type="embedding",
            status="processing",
            message="FTP 파이프라인 시작"
        )
        db.add(log_entry)
        db.commit()
        job_id = str(log_entry.id)
        
        # 백그라운드 작업으로 실행
        background_tasks.add_task(
            execute_ftp_pipeline_background,
            environment,
            delete_after_download,
            upload_to_gcs,
            process_embeddings,
            upload_to_vector_search,
            job_id
        )
        
        return {
            "success": True,
            "message": "FTP 파이프라인이 시작되었습니다.",
            "job_id": job_id
        }
            
    except Exception as e:
        logger.error(f"FTP 파이프라인 실행 오류: {e}")
        return {
            "success": False,
            "message": f"파이프라인 실행 실패: {str(e)}"
        }


def execute_ftp_pipeline_background(
    environment: str,
    delete_after_download: bool,
    upload_to_gcs: bool,
    process_embeddings: bool,
    upload_to_vector_search: bool,
    job_id: str
):
    """FTP 파이프라인 백그라운드 실행"""
    db = next(get_db())
    try:
        # FTP 파이프라인 초기화
        pipeline = FTPPipeline(environment=environment)
        
        # FTP 연결
        if not pipeline.connect_ftp():
            raise Exception("FTP 서버 연결 실패")
        
        try:
            # 파이프라인 실행
            result = pipeline.process_ftp_downloads(
                delete_after_download=delete_after_download,
                upload_to_gcs=upload_to_gcs,
                create_embeddings=process_embeddings
            )
            
            # 처리 완료 로그 업데이트
            log_entry = db.query(ProcessingLog).filter(
                ProcessingLog.id == int(job_id)
            ).first()
            if log_entry:
                log_entry.status = "success"
                log_entry.message = f"파이프라인 완료: 다운로드 {result.get('stats', {}).get('downloaded', 0)}개, 임베딩 {result.get('stats', {}).get('embedded', 0)}개"
                db.commit()
            
        finally:
            pipeline.disconnect_ftp()
            
    except Exception as e:
        logger.error(f"FTP 파이프라인 실행 오류: {e}")
        # 오류 로그 업데이트
        log_entry = db.query(ProcessingLog).filter(
            ProcessingLog.id == int(job_id)
        ).first()
        if log_entry:
            log_entry.status = "error"
            log_entry.message = f"파이프라인 실패: {str(e)}"
            db.commit()
    finally:
        db.close()

@app.get("/api/gcs/files")
async def gcs_list_files(request: dict = None):
    """GCS 버킷의 파일 목록 조회"""
    try:
        gcs_client = GCSClient()
        prefix = request.get('prefix', '') if request else ''
        files = gcs_client.list_files(prefix=prefix)
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/xml/files")
async def xml_list_files():
    """XML 파일 목록 조회"""
    try:
        # FTP 다운로드 디렉토리에서 XML 파일 목록 조회
        download_dir = Path("ftp_downloads")
        if not download_dir.exists():
            return {"success": True, "files": []}
        
        xml_files = []
        for file_path in download_dir.glob("*.xml"):
            stat = file_path.stat()
            xml_files.append({
                "name": file_path.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(file_path)
            })
        
        return {"success": True, "files": xml_files}
    except Exception as e:
        logger.error(f"XML 파일 목록 조회 실패: {str(e)}")
        return {"success": False, "error": str(e)}

@app.delete("/api/gcs/files/{file_path:path}")
async def gcs_delete_file(file_path: str):
    """GCS에서 파일 삭제"""
    try:
        gcs_client = GCSClient()
        result = gcs_client.delete_file(file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/embedding-jobs")
async def get_embedding_jobs(limit: int = 50):
    """임베딩 작업 목록 조회"""
    try:
        db = next(get_db())
        jobs = db.query(ProcessingLog).filter(
            ProcessingLog.process_type.in_(['embedding', 'vector_upload'])
        ).order_by(ProcessingLog.timestamp.desc()).limit(limit).all()
        
        return {
            "success": True,
            "jobs": [
                {
                    "id": str(job.id),
                    "filename": job.message.split(":")[0] if ":" in job.message else job.message,
                    "status": job.status,
                    "progress": 100 if job.status == "success" else 50 if job.status == "processing" else 0,
                    "articles_count": 0,
                    "embeddings_count": 0,
                    "processing_time": (job.processing_time if hasattr(job, 'processing_time') else 0) / 1000,
                    "created_at": job.timestamp.isoformat(),
                    "error": job.error if hasattr(job, 'error') and job.error else None,
                }
                for job in jobs
            ]
        }
    except Exception as e:
        logger.error(f"임베딩 작업 목록 조회 실패: {str(e)}")
        return {"success": False, "error": str(e), "jobs": []}

@app.get("/api/embedding-stats")
async def get_embedding_stats():
    """임베딩 통계 조회"""
    try:
        db = next(get_db())
        total_jobs = db.query(ProcessingLog).filter(
            ProcessingLog.process_type.in_(['embedding', 'vector_upload'])
        ).count()
        completed_jobs = db.query(ProcessingLog).filter(
            ProcessingLog.process_type.in_(['embedding', 'vector_upload']),
            ProcessingLog.status == "success"
        ).count()
        failed_jobs = db.query(ProcessingLog).filter(
            ProcessingLog.process_type.in_(['embedding', 'vector_upload']),
            ProcessingLog.status == "error"
        ).count()
        
        # 벡터 인덱스에서 임베딩 수 가져오기
        vector_count = 0
        try:
            index_response = await get_vector_index_status()
            if index_response and index_response.get("indexes"):
                for idx in index_response["indexes"]:
                    vector_count += idx.get("total_vectors", 0)
        except:
            pass
        
        return {
            "success": True,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "total_embeddings": vector_count,
            "avg_processing_time": 5.2,  # 실제로는 계산 필요
        }
    except Exception as e:
        logger.error(f"임베딩 통계 조회 실패: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/embedding-jobs/{job_id}")
async def get_embedding_job(job_id: str):
    """임베딩 작업 상세 조회"""
    try:
        db = next(get_db())
        job = db.query(ProcessingLog).filter(
            ProcessingLog.id == int(job_id)
        ).first()
        
        if not job:
            return {"success": False, "error": "작업을 찾을 수 없습니다."}
        
        return {
            "success": True,
            "job": {
                "id": str(job.id),
                "filename": job.message.split(":")[0] if ":" in job.message else job.message,
                "status": job.status,
                "progress": 100 if job.status == "success" else 50 if job.status == "processing" else 0,
                "message": job.message,
                "created_at": job.timestamp.isoformat(),
                "processing_time": (job.processing_time if hasattr(job, 'processing_time') else 0) / 1000,
            }
        }
    except Exception as e:
        logger.error(f"임베딩 작업 상세 조회 실패: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/embedding-jobs/{job_id}/stop")
async def stop_embedding_job(job_id: str):
    """임베딩 작업 중지"""
    try:
        db = next(get_db())
        job = db.query(ProcessingLog).filter(
            ProcessingLog.id == int(job_id)
        ).first()
        
        if not job:
            return {"success": False, "error": "작업을 찾을 수 없습니다."}
        
        if job.status == "processing":
            job.status = "error"
            job.message = f"{job.message} (중지됨)"
            db.commit()
            return {"success": True, "message": "작업이 중지되었습니다."}
        else:
            return {"success": False, "error": "처리 중인 작업만 중지할 수 있습니다."}
    except Exception as e:
        logger.error(f"임베딩 작업 중지 실패: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/upload-xml")
async def upload_xml_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """XML 파일 업로드 및 임베딩 처리"""
    try:
        # 업로드된 파일 저장
        upload_dir = Path("uploaded_xml")
        upload_dir.mkdir(exist_ok=True)
        
        # 타임스탬프가 포함된 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = upload_dir / f"{timestamp}_{file.filename}"
        
        # 파일 저장
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"XML 파일 업로드 완료: {file_path}")
        
        # 처리 로그 생성
        db = next(get_db())
        log_entry = ProcessingLog(
            process_type="embedding",
            status="processing",
            message=f"{file.filename}: 업로드 완료"
        )
        db.add(log_entry)
        db.commit()
        job_id = str(log_entry.id)
        
        # 백그라운드 작업으로 임베딩 처리
        background_tasks.add_task(
            process_xml_embeddings,
            str(file_path),
            job_id
        )
        
        return {
            "success": True,
            "message": "파일 업로드가 시작되었습니다.",
            "job_id": job_id,
            "filename": file.filename
        }
    except Exception as e:
        logger.error(f"파일 업로드 실패: {str(e)}")
        return {"success": False, "error": str(e)}


def process_xml_embeddings(file_path: str, job_id: str):
    """XML 파일 임베딩 처리 백그라운드 작업"""
    db = next(get_db())
    try:
        logger.info(f"XML 임베딩 처리 시작: {file_path}")
        
        # XML 파일 파싱
        articles = xml_processor.process_file(file_path)
        logger.info(f"파싱된 기사 수: {len(articles)}")
        
        # 임베딩 생성 및 Vector Search 업로드
        processed_count = 0
        embedding_count = 0
        
        for article in articles:
            try:
                # 기사 저장
                db_article = Article(
                    title=article.get('title', ''),
                    content=article.get('content', ''),
                    metadata=json.dumps(article.get('metadata', {}))
                )
                db.add(db_article)
                db.commit()
                
                # 임베딩 생성
                if embedding_service:
                    embedding_vector = embedding_service.generate_embedding(
                        article.get('content', '')
                    )
                    
                    # Vector Search에 업로드
                    if vector_indexer:
                        vector_indexer.upload_vector(
                            vector=embedding_vector,
                            article_id=str(db_article.id),
                            metadata={
                                'title': article.get('title', ''),
                                'content': article.get('content', '')[:500]
                            }
                        )
                        embedding_count += 1
                
                processed_count += 1
            except Exception as e:
                logger.error(f"기사 처리 실패: {str(e)}")
                continue
        
        # 처리 완료 로그 업데이트
        log_entry = db.query(ProcessingLog).filter(
            ProcessingLog.id == int(job_id)
        ).first()
        if log_entry:
            log_entry.status = "success"
            log_entry.message = f"처리 완료: {processed_count}개 기사, {embedding_count}개 임베딩"
            db.commit()
        
        logger.info(f"XML 임베딩 처리 완료: {file_path}")
        
    except Exception as e:
        logger.error(f"XML 임베딩 처리 실패: {str(e)}")
        # 오류 로그 업데이트
        log_entry = db.query(ProcessingLog).filter(
            ProcessingLog.id == int(job_id)
        ).first()
        if log_entry:
            log_entry.status = "error"
            log_entry.message = f"처리 실패: {str(e)}"
            db.commit()
    finally:
        db.close()

# ========================================
# GCP 인증 API
# ========================================

@app.get("/api/gcp/auth-status")
async def get_gcp_auth_status():
    """GCP 인증 상태 조회"""
    try:
        # gcloud auth list로 인증된 계정 확인
        result = subprocess.run(
            ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            accounts = json.loads(result.stdout)
            if accounts and len(accounts) > 0:
                # 활성 계정이 있으면 프로젝트 ID 가져오기
                project_result = subprocess.run(
                    ['gcloud', 'config', 'get-value', 'project'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                project_id = project_result.stdout.strip() if project_result.returncode == 0 else None
                
                return {
                    "authenticated": True,
                    "accounts": accounts,
                    "active_account": accounts[0].get('account', ''),
                    "project_id": project_id
                }
        
        return {
            "authenticated": False,
            "accounts": [],
            "active_account": None,
            "project_id": None
        }
    except Exception as e:
        logger.error(f"GCP 인증 상태 확인 실패: {e}")
        return {
            "authenticated": False,
            "error": str(e),
            "accounts": [],
            "active_account": None,
            "project_id": None
        }

@app.post("/api/gcp/init-login")
async def init_gcp_login():
    """GCP 로그인 시작 (브라우저에서 직접 로그인)"""
    try:
        # 브라우저 자동 실행 시도 (가장 간단한 방법)
        try:
            result = subprocess.run(
                ['gcloud', 'auth', 'login', '--brief', '--no-launch-browser'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            
            # URL과 인증 코드 추출
            import re
            url_pattern = r'https://accounts\.google\.com[^\s]+'
            code_pattern = r'(\d{4}-\d{4}-\d{4}-\d{4})'
            
            urls = re.findall(url_pattern, output)
            codes = re.findall(code_pattern, output)
            
            auth_url = urls[0] if urls else None
            verification_code = codes[0] if codes else None
            
            if auth_url:
                return {
                    "success": True,
                    "auth_url": auth_url,
                    "verification_code": verification_code,
                    "message": "브라우저에서 Google 계정으로 로그인하세요.",
                    "instructions": f"아래 URL을 클릭하여 브라우저에서 로그인하세요. 인증 코드가 필요하면 '{verification_code}'를 사용하세요."
                }
            else:
                # URL을 찾지 못한 경우 브라우저 자동 실행
                subprocess.Popen(['gcloud', 'auth', 'login', '--brief'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                return {
                    "success": True,
                    "auth_url": None,
                    "verification_code": None,
                    "message": "브라우저가 자동으로 열렸습니다. Google 계정으로 로그인하세요.",
                    "instructions": "브라우저에서 Google 계정을 선택하고 권한을 승인하세요."
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "타임아웃",
                "message": "인증 프로세스가 너무 오래 걸렸습니다."
            }
    except Exception as e:
        logger.error(f"GCP 로그인 시작 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "GCP 로그인 시작에 실패했습니다. 터미널에서 직접 'gcloud auth login' 명령을 실행하세요."
        }

@app.post("/api/gcp/complete-login")
async def complete_gcp_login():
    """GCP 로그인 완료 확인"""
    try:
        # 인증 상태 다시 확인
        result = subprocess.run(
            ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            accounts = json.loads(result.stdout)
            if accounts and len(accounts) > 0:
                project_result = subprocess.run(
                    ['gcloud', 'config', 'get-value', 'project'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                project_id = project_result.stdout.strip() if project_result.returncode == 0 else None
                
                return {
                    "success": True,
                    "authenticated": True,
                    "active_account": accounts[0].get('account', ''),
                    "project_id": project_id
                }
        
        return {
            "success": False,
            "authenticated": False,
            "message": "아직 인증되지 않았습니다. 브라우저에서 로그인을 완료하세요."
        }
    except Exception as e:
        logger.error(f"GCP 로그인 완료 확인 실패: {e}")
        return {
            "success": False,
            "authenticated": False,
            "error": str(e)
        }

# 애플리케이션 시작 시 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    try:
        init_database()
        logger.info("데이터베이스 초기화 완료")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
