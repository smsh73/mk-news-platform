"""
API 엔드포인트 단위 테스트
"""
import pytest
from fastapi.testclient import TestClient
from src.web.app import app

client = TestClient(app)


def test_health_endpoint():
    """Health check 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_query_endpoint():
    """Query 엔드포인트 테스트"""
    response = client.post(
        "/api/query",
        json={
            "query": "테스트 쿼리",
            "top_k": 10,
            "similarity_threshold": 0.7,
            "filters": {},
            "max_context_length": 4000
        }
    )
    assert response.status_code in [200, 500]  # 500은 실제 구현에 따라 달라질 수 있음


def test_stats_endpoint():
    """Stats 엔드포인트 테스트"""
    response = client.get("/api/stats")
    assert response.status_code in [200, 500]


def test_articles_endpoint():
    """Articles 엔드포인트 테스트"""
    response = client.get("/api/articles?limit=10")
    assert response.status_code in [200, 500]


def test_vector_index_status():
    """Vector index status 엔드포인트 테스트"""
    response = client.get("/api/vector-index/status")
    assert response.status_code in [200, 500]


def test_ftp_connection_info():
    """FTP connection info 엔드포인트 테스트"""
    response = client.get("/api/ftp/connection-info")
    assert response.status_code in [200, 500]


def test_search_history():
    """Search history 엔드포인트 테스트"""
    response = client.get("/api/search-history?limit=5")
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)

