"""
FastAPI 웹 애플리케이션 - 매일경제 신문기사 벡터임베딩 플랫폼
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uvicorn

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..database.connection import get_db, init_database
from ..database.models import Article, VectorIndex, ProcessingLog
from ..xml_processor import XMLProcessor
from ..vector_search.vector_indexer import VectorIndexer
from ..rag.hybrid_rag_system import HybridRAGSystem
from ..incremental.incremental_processor import IncrementalProcessor
from ..embedding.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

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
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
@app.get("/")
async def root():
    """메인 페이지"""
    return {"message": "매일경제 신문기사 벡터임베딩 플랫폼에 오신 것을 환영합니다!"}

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
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
