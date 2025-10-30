"""
TextChunker 단위 테스트
"""
import pytest
from src.embedding.text_chunker import TextChunker, get_text_chunker


def test_text_chunker_initialization():
    """TextChunker 초기화 테스트"""
    chunker = TextChunker(chunk_size=500, chunk_overlap=50, strategy="sentence")
    assert chunker.chunk_size == 500
    assert chunker.chunk_overlap == 50
    assert chunker.strategy == "sentence"


def test_chunk_by_fixed_size():
    """고정 크기 청킹 테스트"""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20, strategy="fixed_size")
    text = "a" * 250  # 250자 텍스트
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) > 0
    assert all(len(chunk.text) <= 100 for chunk in chunks)


def test_chunk_by_sentence():
    """문장 단위 청킹 테스트"""
    chunker = TextChunker(chunk_size=50, chunk_overlap=10, strategy="sentence")
    text = "첫 번째 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다."
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.text.strip() != ""


def test_get_text_chunker_singleton():
    """get_text_chunker 싱글톤 테스트"""
    chunker1 = get_text_chunker()
    chunker2 = get_text_chunker()
    assert chunker1 is chunker2


def test_chunk_with_metadata():
    """메타데이터를 포함한 청킹 테스트"""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20, strategy="fixed_size")
    text = "테스트 텍스트입니다."
    metadata = {"article_id": "123", "source": "test"}
    chunks = chunker.chunk_text(text, metadata=metadata)
    
    assert len(chunks) > 0
    assert all(chunk.metadata == metadata for chunk in chunks)

