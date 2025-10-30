"""
텍스트 청킹 서비스
긴 문서를 의미 단위로 분할하여 임베딩 및 검색 성능 최적화
"""
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """텍스트 청크 데이터 클래스"""
    text: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Optional[Dict] = None


class TextChunker:
    """텍스트 청킹 클래스"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: str = "fixed"
    ):
        """
        초기화
        
        Args:
            chunk_size: 청크 크기 (문자 수)
            chunk_overlap: 청크 간 겹치는 문자 수
            strategy: 청킹 전략 ('fixed', 'sentence', 'paragraph', 'semantic')
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
    
    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """
        텍스트를 청크로 분할
        
        Args:
            text: 분할할 텍스트
            metadata: 메타데이터 (원본 문서 정보 등)
            
        Returns:
            TextChunk 리스트
        """
        if not text or len(text.strip()) == 0:
            return []
        
        try:
            if self.strategy == "fixed":
                return self._chunk_fixed_size(text, metadata)
            elif self.strategy == "sentence":
                return self._chunk_by_sentence(text, metadata)
            elif self.strategy == "paragraph":
                return self._chunk_by_paragraph(text, metadata)
            elif self.strategy == "semantic":
                return self._chunk_semantic(text, metadata)
            else:
                logger.warning(f"알 수 없는 청킹 전략: {self.strategy}, fixed 전략 사용")
                return self._chunk_fixed_size(text, metadata)
        except Exception as e:
            logger.error(f"텍스트 청킹 중 오류 발생: {e}")
            return [TextChunk(
                text=text,
                chunk_index=0,
                start_char=0,
                end_char=len(text),
                metadata=metadata
            )]
    
    def _chunk_fixed_size(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """고정 크기 청킹"""
        chunks = []
        text = text.strip()
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # 청크 텍스트 추출
            chunk_text = text[start:end]
            
            # 다음 청크 시작 위치 계산 (오버랩 고려)
            if end < len(text):
                # 오버랩 영역에서 적절한 경계 찾기 (공백이나 문장 끝)
                overlap_start = max(start, end - self.chunk_overlap)
                next_start = self._find_split_point(text, overlap_start, end)
                start = next_start if next_start > start else end
            else:
                start = end
            
            chunks.append(TextChunk(
                text=chunk_text.strip(),
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                metadata=metadata
            ))
            chunk_index += 1
        
        return chunks
    
    def _chunk_by_sentence(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """문장 단위 청킹"""
        # 한국어 문장 구분자: . ! ? \n
        sentence_pattern = r'([^.!?\n]+[.!?\n]+)'
        sentences = re.findall(sentence_pattern, text)
        
        if not sentences:
            return [TextChunk(
                text=text,
                chunk_index=0,
                start_char=0,
                end_char=len(text),
                metadata=metadata
            )]
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        start_char = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # 현재 청크 저장
                chunks.append(TextChunk(
                    text=current_chunk.strip(),
                    chunk_index=chunk_index,
                    start_char=start_char,
                    end_char=start_char + len(current_chunk),
                    metadata=metadata
                ))
                chunk_index += 1
                
                # 오버랩 처리: 마지막 문장을 다음 청크에 포함
                if self.chunk_overlap > 0:
                    overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                    current_chunk = overlap_text + sentence
                    start_char = start_char + len(current_chunk) - len(sentence) - len(overlap_text)
                else:
                    current_chunk = sentence
                    start_char += len(current_chunk)
            else:
                current_chunk += sentence
        
        # 마지막 청크 추가
        if current_chunk.strip():
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                chunk_index=chunk_index,
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                metadata=metadata
            ))
        
        return chunks
    
    def _chunk_by_paragraph(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """문단 단위 청킹"""
        # 문단 구분: 두 개 이상의 연속된 줄바꿈
        paragraphs = re.split(r'\n\s*\n+', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not paragraphs:
            return [TextChunk(
                text=text,
                chunk_index=0,
                start_char=0,
                end_char=len(text),
                metadata=metadata
            )]
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        char_offset = 0
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 > self.chunk_size and current_chunk:
                # 현재 청크 저장
                chunks.append(TextChunk(
                    text=current_chunk.strip(),
                    chunk_index=chunk_index,
                    start_char=char_offset - len(current_chunk),
                    end_char=char_offset,
                    metadata=metadata
                ))
                chunk_index += 1
                
                # 오버랩 처리
                if self.chunk_overlap > 0:
                    overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                    current_chunk = overlap_text + "\n\n" + paragraph
                    char_offset += len(paragraph) + 2 - len(overlap_text)
                else:
                    current_chunk = paragraph
                    char_offset += len(paragraph) + 2
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                    char_offset += len(paragraph) + 2
                else:
                    current_chunk = paragraph
                    char_offset += len(paragraph) + 2
        
        # 마지막 청크 추가
        if current_chunk.strip():
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                chunk_index=chunk_index,
                start_char=char_offset - len(current_chunk),
                end_char=char_offset,
                metadata=metadata
            ))
        
        return chunks
    
    def _chunk_semantic(self, text: str, metadata: Optional[Dict] = None) -> List[TextChunk]:
        """
        의미 단위 청킹 (현재는 문장 단위로 구현, 향후 개선 가능)
        실제 의미 분석을 위해서는 NLP 모델이 필요하지만,
        현재는 문장 단위 + 키워드 기반으로 구현
        """
        # 의미 단위 청킹은 복잡하므로, 현재는 문장 단위로 구현
        # 향후 개선: 토픽 모델링, 코사인 유사도 기반 분할 등
        return self._chunk_by_sentence(text, metadata)
    
    def _find_split_point(self, text: str, start: int, end: int) -> int:
        """적절한 분할 지점 찾기 (공백, 줄바꿈, 문장 끝)"""
        # 역순으로 검색하여 가장 가까운 적절한 분할 지점 찾기
        for i in range(end - 1, start - 1, -1):
            if text[i] in ['\n', '\r', '.', '!', '?', ' ']:
                # 다음 문자 확인 (공백이나 줄바꿈이면 그대로 사용)
                if i + 1 < len(text) and text[i + 1] in ['\n', '\r', ' ']:
                    return i + 2
                return i + 1
        return end
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """오버랩 텍스트 추출 (문장 단위로 정리)"""
        if len(text) <= overlap_size:
            return text
        
        overlap = text[-overlap_size:]
        # 첫 번째 문장 시작점 찾기
        sentence_start = re.search(r'[.!?\n]', overlap)
        if sentence_start:
            return overlap[sentence_start.end():]
        return overlap


# 전역 청커 인스턴스
_default_chunker = None


def get_text_chunker(
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    strategy: str = "fixed"
) -> TextChunker:
    """
    TextChunker 싱글톤 인스턴스 반환
    
    Args:
        chunk_size: 청크 크기
        chunk_overlap: 오버랩 크기
        strategy: 청킹 전략
        
    Returns:
        TextChunker 인스턴스
    """
    global _default_chunker
    if _default_chunker is None or _default_chunker.chunk_size != chunk_size or \
       _default_chunker.chunk_overlap != chunk_overlap or _default_chunker.strategy != strategy:
        _default_chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy
        )
    return _default_chunker

