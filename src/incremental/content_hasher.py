"""
콘텐츠 해싱 시스템
"""
import hashlib
import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import re
import os

logger = logging.getLogger(__name__)

class ContentHasher:
    """콘텐츠 해싱 시스템"""
    
    def __init__(self):
        self.hash_algorithms = ['md5', 'sha1', 'sha256']
        self.normalization_rules = [
            self._remove_html_tags,
            self._normalize_whitespace,
            self._remove_special_characters,
            self._normalize_case,
            self._remove_punctuation
        ]
    
    def calculate_file_hash(self, file_path: str) -> str:
        """파일 해시 계산"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                return hashlib.md5(file_content).hexdigest()
                
        except Exception as e:
            logger.error(f"파일 해시 계산 중 오류 발생: {file_path}, {e}")
            return ""
    
    def calculate_content_hash(self, content: str, algorithm: str = 'md5') -> str:
        """콘텐츠 해시 계산"""
        try:
            # 콘텐츠 정규화
            normalized_content = self._normalize_content(content)
            
            # 해시 계산
            if algorithm == 'md5':
                return hashlib.md5(normalized_content.encode('utf-8')).hexdigest()
            elif algorithm == 'sha1':
                return hashlib.sha1(normalized_content.encode('utf-8')).hexdigest()
            elif algorithm == 'sha256':
                return hashlib.sha256(normalized_content.encode('utf-8')).hexdigest()
            else:
                return hashlib.md5(normalized_content.encode('utf-8')).hexdigest()
                
        except Exception as e:
            logger.error(f"콘텐츠 해시 계산 중 오류 발생: {e}")
            return ""
    
    def calculate_article_hash(self, article: Dict) -> Dict:
        """기사 해시 계산"""
        try:
            hashes = {}
            
            # 전체 콘텐츠 해시
            full_content = f"{article.get('title', '')} {article.get('body', '')} {article.get('summary', '')}"
            hashes['full_content'] = self.calculate_content_hash(full_content)
            
            # 제목 해시
            title = article.get('title', '')
            hashes['title'] = self.calculate_content_hash(title)
            
            # 본문 해시
            body = article.get('body', '')
            hashes['body'] = self.calculate_content_hash(body)
            
            # 요약 해시
            summary = article.get('summary', '')
            hashes['summary'] = self.calculate_content_hash(summary)
            
            # 메타데이터 해시
            metadata = f"{article.get('art_id', '')}{article.get('writers', '')}{article.get('service_daytime', '')}"
            hashes['metadata'] = self.calculate_content_hash(metadata)
            
            return hashes
            
        except Exception as e:
            logger.error(f"기사 해시 계산 중 오류 발생: {e}")
            return {}
    
    def calculate_multiple_hashes(self, content: str) -> Dict[str, str]:
        """다중 해시 계산"""
        try:
            normalized_content = self._normalize_content(content)
            hashes = {}
            
            for algorithm in self.hash_algorithms:
                if algorithm == 'md5':
                    hashes[algorithm] = hashlib.md5(normalized_content.encode('utf-8')).hexdigest()
                elif algorithm == 'sha1':
                    hashes[algorithm] = hashlib.sha1(normalized_content.encode('utf-8')).hexdigest()
                elif algorithm == 'sha256':
                    hashes[algorithm] = hashlib.sha256(normalized_content.encode('utf-8')).hexdigest()
            
            return hashes
            
        except Exception as e:
            logger.error(f"다중 해시 계산 중 오류 발생: {e}")
            return {}
    
    def _normalize_content(self, content: str) -> str:
        """콘텐츠 정규화"""
        try:
            normalized = content
            
            # 정규화 규칙 적용
            for rule in self.normalization_rules:
                normalized = rule(normalized)
            
            return normalized
            
        except Exception as e:
            logger.error(f"콘텐츠 정규화 중 오류 발생: {e}")
            return content
    
    def _remove_html_tags(self, text: str) -> str:
        """HTML 태그 제거"""
        try:
            return re.sub(r'<[^>]+>', '', text)
        except Exception:
            return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """공백 정규화"""
        try:
            # 연속된 공백을 하나로 변환
            text = re.sub(r'\s+', ' ', text)
            # 앞뒤 공백 제거
            return text.strip()
        except Exception:
            return text
    
    def _remove_special_characters(self, text: str) -> str:
        """특수 문자 제거"""
        try:
            # 한글, 영문, 숫자, 공백만 유지
            return re.sub(r'[^\w\s가-힣]', '', text)
        except Exception:
            return text
    
    def _normalize_case(self, text: str) -> str:
        """대소문자 정규화"""
        try:
            return text.lower()
        except Exception:
            return text
    
    def _remove_punctuation(self, text: str) -> str:
        """구두점 제거"""
        try:
            return re.sub(r'[^\w\s가-힣]', ' ', text)
        except Exception:
            return text
    
    def compare_hashes(self, hash1: str, hash2: str) -> bool:
        """해시 비교"""
        try:
            return hash1 == hash2
        except Exception as e:
            logger.error(f"해시 비교 중 오류 발생: {e}")
            return False
    
    def find_similar_hashes(self, target_hash: str, hash_list: List[str], 
                           threshold: float = 0.8) -> List[Tuple[str, float]]:
        """유사한 해시 찾기"""
        try:
            similar_hashes = []
            
            for hash_value in hash_list:
                similarity = self._calculate_hash_similarity(target_hash, hash_value)
                if similarity >= threshold:
                    similar_hashes.append((hash_value, similarity))
            
            # 유사도 순으로 정렬
            similar_hashes.sort(key=lambda x: x[1], reverse=True)
            
            return similar_hashes
            
        except Exception as e:
            logger.error(f"유사한 해시 찾기 중 오류 발생: {e}")
            return []
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """해시 유사도 계산"""
        try:
            if len(hash1) != len(hash2):
                return 0.0
            
            # 해시 문자열의 문자별 유사도 계산
            matches = sum(1 for c1, c2 in zip(hash1, hash2) if c1 == c2)
            similarity = matches / len(hash1)
            
            return similarity
            
        except Exception as e:
            logger.error(f"해시 유사도 계산 중 오류 발생: {e}")
            return 0.0
    
    def create_hash_fingerprint(self, article: Dict) -> str:
        """기사 해시 지문 생성"""
        try:
            # 핵심 정보 추출
            title = article.get('title', '')
            body = article.get('body', '')
            summary = article.get('summary', '')
            
            # 핵심 키워드 추출
            keywords = self._extract_keywords(f"{title} {body} {summary}")
            
            # 키워드 기반 지문 생성
            fingerprint = ' '.join(keywords[:10])  # 상위 10개 키워드
            fingerprint = self._normalize_content(fingerprint)
            
            return self.calculate_content_hash(fingerprint)
            
        except Exception as e:
            logger.error(f"해시 지문 생성 중 오류 발생: {e}")
            return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        try:
            # 불용어 제거
            stop_words = {
                '이', '가', '을', '를', '에', '의', '로', '으로', '와', '과', '는', '은', '도', '만',
                '것', '거', '게', '걸', '있다', '없다', '되다', '하다', '이다', '아니다'
            }
            
            # 단어 분리
            words = re.findall(r'[가-힣\w]+', text.lower())
            
            # 불용어 제거 및 길이 필터링
            keywords = [word for word in words if word not in stop_words and len(word) >= 2]
            
            # 빈도수 계산
            from collections import Counter
            word_counts = Counter(keywords)
            
            # 상위 키워드 반환
            return [word for word, count in word_counts.most_common(20)]
            
        except Exception as e:
            logger.error(f"키워드 추출 중 오류 발생: {e}")
            return []
    
    def get_hash_statistics(self, hashes: List[str]) -> Dict:
        """해시 통계 조회"""
        try:
            if not hashes:
                return {
                    'total_hashes': 0,
                    'unique_hashes': 0,
                    'duplicate_hashes': 0,
                    'duplicate_rate': 0.0
                }
            
            unique_hashes = set(hashes)
            duplicate_count = len(hashes) - len(unique_hashes)
            
            return {
                'total_hashes': len(hashes),
                'unique_hashes': len(unique_hashes),
                'duplicate_hashes': duplicate_count,
                'duplicate_rate': duplicate_count / len(hashes) if hashes else 0.0
            }
            
        except Exception as e:
            logger.error(f"해시 통계 조회 중 오류 발생: {e}")
            return {
                'total_hashes': 0,
                'unique_hashes': 0,
                'duplicate_hashes': 0,
                'duplicate_rate': 0.0
            }
    
    def validate_hash(self, hash_value: str, algorithm: str = 'md5') -> bool:
        """해시 유효성 검증"""
        try:
            if algorithm == 'md5':
                return len(hash_value) == 32 and all(c in '0123456789abcdef' for c in hash_value)
            elif algorithm == 'sha1':
                return len(hash_value) == 40 and all(c in '0123456789abcdef' for c in hash_value)
            elif algorithm == 'sha256':
                return len(hash_value) == 64 and all(c in '0123456789abcdef' for c in hash_value)
            else:
                return False
                
        except Exception as e:
            logger.error(f"해시 유효성 검증 중 오류 발생: {e}")
            return False


