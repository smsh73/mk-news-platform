"""
중복 감지 시스템
"""
import hashlib
import logging
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
import difflib
import re

logger = logging.getLogger(__name__)

class DuplicateDetector:
    """중복 감지기"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.content_hashes = set()
        self.title_hashes = set()
    
    def detect_duplicates(self, articles: List[Dict]) -> Dict:
        """중복 기사 감지"""
        try:
            duplicates = {
                'exact_duplicates': [],
                'similar_duplicates': [],
                'title_duplicates': [],
                'content_duplicates': []
            }
            
            # 1. 정확한 중복 감지
            exact_duplicates = self._detect_exact_duplicates(articles)
            duplicates['exact_duplicates'] = exact_duplicates
            
            # 2. 유사한 중복 감지
            similar_duplicates = self._detect_similar_duplicates(articles)
            duplicates['similar_duplicates'] = similar_duplicates
            
            # 3. 제목 중복 감지
            title_duplicates = self._detect_title_duplicates(articles)
            duplicates['title_duplicates'] = title_duplicates
            
            # 4. 콘텐츠 중복 감지
            content_duplicates = self._detect_content_duplicates(articles)
            duplicates['content_duplicates'] = content_duplicates
            
            return duplicates
            
        except Exception as e:
            logger.error(f"중복 감지 중 오류 발생: {e}")
            return {
                'exact_duplicates': [],
                'similar_duplicates': [],
                'title_duplicates': [],
                'content_duplicates': []
            }
    
    def _detect_exact_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """정확한 중복 감지"""
        try:
            exact_duplicates = []
            content_hashes = {}
            
            for article in articles:
                content_hash = self._calculate_content_hash(article)
                
                if content_hash in content_hashes:
                    # 중복 발견
                    duplicate_group = {
                        'original': content_hashes[content_hash],
                        'duplicate': article,
                        'similarity': 1.0,
                        'type': 'exact'
                    }
                    exact_duplicates.append(duplicate_group)
                else:
                    content_hashes[content_hash] = article
            
            return exact_duplicates
            
        except Exception as e:
            logger.error(f"정확한 중복 감지 중 오류 발생: {e}")
            return []
    
    def _detect_similar_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """유사한 중복 감지"""
        try:
            similar_duplicates = []
            
            for i, article1 in enumerate(articles):
                for j, article2 in enumerate(articles[i+1:], i+1):
                    similarity = self._calculate_similarity(article1, article2)
                    
                    if similarity >= self.similarity_threshold:
                        duplicate_group = {
                            'article1': article1,
                            'article2': article2,
                            'similarity': similarity,
                            'type': 'similar'
                        }
                        similar_duplicates.append(duplicate_group)
            
            return similar_duplicates
            
        except Exception as e:
            logger.error(f"유사한 중복 감지 중 오류 발생: {e}")
            return []
    
    def _detect_title_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """제목 중복 감지"""
        try:
            title_duplicates = []
            title_hashes = {}
            
            for article in articles:
                title = article.get('title', '')
                if not title:
                    continue
                
                title_hash = self._calculate_title_hash(title)
                
                if title_hash in title_hashes:
                    duplicate_group = {
                        'original': title_hashes[title_hash],
                        'duplicate': article,
                        'similarity': 1.0,
                        'type': 'title'
                    }
                    title_duplicates.append(duplicate_group)
                else:
                    title_hashes[title_hash] = article
            
            return title_duplicates
            
        except Exception as e:
            logger.error(f"제목 중복 감지 중 오류 발생: {e}")
            return []
    
    def _detect_content_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """콘텐츠 중복 감지"""
        try:
            content_duplicates = []
            
            for i, article1 in enumerate(articles):
                for j, article2 in enumerate(articles[i+1:], i+1):
                    content_similarity = self._calculate_content_similarity(
                        article1.get('body', ''),
                        article2.get('body', '')
                    )
                    
                    if content_similarity >= self.similarity_threshold:
                        duplicate_group = {
                            'article1': article1,
                            'article2': article2,
                            'similarity': content_similarity,
                            'type': 'content'
                        }
                        content_duplicates.append(duplicate_group)
            
            return content_duplicates
            
        except Exception as e:
            logger.error(f"콘텐츠 중복 감지 중 오류 발생: {e}")
            return []
    
    def _calculate_content_hash(self, article: Dict) -> str:
        """콘텐츠 해시 계산"""
        try:
            title = article.get('title', '')
            body = article.get('body', '')
            summary = article.get('summary', '')
            
            # 콘텐츠 정규화
            content = f"{title} {body} {summary}"
            content = self._normalize_text(content)
            
            # 해시 계산
            return hashlib.md5(content.encode('utf-8')).hexdigest()
            
        except Exception as e:
            logger.error(f"콘텐츠 해시 계산 중 오류 발생: {e}")
            return ""
    
    def _calculate_title_hash(self, title: str) -> str:
        """제목 해시 계산"""
        try:
            normalized_title = self._normalize_text(title)
            return hashlib.md5(normalized_title.encode('utf-8')).hexdigest()
            
        except Exception as e:
            logger.error(f"제목 해시 계산 중 오류 발생: {e}")
            return ""
    
    def _calculate_similarity(self, article1: Dict, article2: Dict) -> float:
        """기사 유사도 계산"""
        try:
            # 제목 유사도
            title_similarity = self._calculate_text_similarity(
                article1.get('title', ''),
                article2.get('title', '')
            )
            
            # 요약 유사도
            summary_similarity = self._calculate_text_similarity(
                article1.get('summary', ''),
                article2.get('summary', '')
            )
            
            # 본문 유사도
            body_similarity = self._calculate_content_similarity(
                article1.get('body', ''),
                article2.get('body', '')
            )
            
            # 가중 평균 계산
            weights = {'title': 0.4, 'summary': 0.3, 'body': 0.3}
            total_similarity = (
                title_similarity * weights['title'] +
                summary_similarity * weights['summary'] +
                body_similarity * weights['body']
            )
            
            return total_similarity
            
        except Exception as e:
            logger.error(f"유사도 계산 중 오류 발생: {e}")
            return 0.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        try:
            if not text1 or not text2:
                return 0.0
            
            # 텍스트 정규화
            text1 = self._normalize_text(text1)
            text2 = self._normalize_text(text2)
            
            # SequenceMatcher 사용
            similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
            
            return similarity
            
        except Exception as e:
            logger.error(f"텍스트 유사도 계산 중 오류 발생: {e}")
            return 0.0
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """콘텐츠 유사도 계산"""
        try:
            if not content1 or not content2:
                return 0.0
            
            # 콘텐츠 정규화
            content1 = self._normalize_text(content1)
            content2 = self._normalize_text(content2)
            
            # 긴 텍스트의 경우 청크 단위로 비교
            if len(content1) > 1000 or len(content2) > 1000:
                return self._calculate_chunk_similarity(content1, content2)
            else:
                return difflib.SequenceMatcher(None, content1, content2).ratio()
                
        except Exception as e:
            logger.error(f"콘텐츠 유사도 계산 중 오류 발생: {e}")
            return 0.0
    
    def _calculate_chunk_similarity(self, content1: str, content2: str) -> float:
        """청크 단위 유사도 계산"""
        try:
            chunk_size = 500
            max_similarity = 0.0
            
            # 첫 번째 텍스트를 청크로 분할
            chunks1 = [content1[i:i+chunk_size] for i in range(0, len(content1), chunk_size)]
            
            # 두 번째 텍스트를 청크로 분할
            chunks2 = [content2[i:i+chunk_size] for i in range(0, len(content2), chunk_size)]
            
            # 각 청크 쌍의 유사도 계산
            for chunk1 in chunks1:
                for chunk2 in chunks2:
                    similarity = difflib.SequenceMatcher(None, chunk1, chunk2).ratio()
                    max_similarity = max(max_similarity, similarity)
            
            return max_similarity
            
        except Exception as e:
            logger.error(f"청크 유사도 계산 중 오류 발생: {e}")
            return 0.0
    
    def _normalize_text(self, text: str) -> str:
        """텍스트 정규화"""
        try:
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', text)
            
            # 특수 문자 제거
            text = re.sub(r'[^\w\s가-힣]', ' ', text)
            
            # 공백 정리
            text = re.sub(r'\s+', ' ', text)
            
            # 소문자 변환
            text = text.lower()
            
            # 앞뒤 공백 제거
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"텍스트 정규화 중 오류 발생: {e}")
            return text
    
    def filter_duplicates(self, articles: List[Dict], 
                         keep_strategy: str = 'latest') -> List[Dict]:
        """중복 필터링"""
        try:
            # 중복 감지
            duplicates = self.detect_duplicates(articles)
            
            # 유지할 기사 결정
            keep_articles = set()
            remove_articles = set()
            
            # 정확한 중복 처리
            for duplicate in duplicates['exact_duplicates']:
                original = duplicate['original']
                duplicate_article = duplicate['duplicate']
                
                if keep_strategy == 'latest':
                    if original.get('created_at', '') < duplicate_article.get('created_at', ''):
                        keep_articles.add(duplicate_article['id'])
                        remove_articles.add(original['id'])
                    else:
                        keep_articles.add(original['id'])
                        remove_articles.add(duplicate_article['id'])
                else:  # 'first'
                    keep_articles.add(original['id'])
                    remove_articles.add(duplicate_article['id'])
            
            # 유사한 중복 처리
            for duplicate in duplicates['similar_duplicates']:
                article1 = duplicate['article1']
                article2 = duplicate['article2']
                
                if keep_strategy == 'latest':
                    if article1.get('created_at', '') < article2.get('created_at', ''):
                        keep_articles.add(article2['id'])
                        remove_articles.add(article1['id'])
                    else:
                        keep_articles.add(article1['id'])
                        remove_articles.add(article2['id'])
                else:  # 'first'
                    keep_articles.add(article1['id'])
                    remove_articles.add(article2['id'])
            
            # 필터링된 기사 반환
            filtered_articles = [
                article for article in articles 
                if article['id'] not in remove_articles
            ]
            
            return filtered_articles
            
        except Exception as e:
            logger.error(f"중복 필터링 중 오류 발생: {e}")
            return articles
    
    def get_duplicate_statistics(self, articles: List[Dict]) -> Dict:
        """중복 통계 조회"""
        try:
            duplicates = self.detect_duplicates(articles)
            
            stats = {
                'total_articles': len(articles),
                'exact_duplicates': len(duplicates['exact_duplicates']),
                'similar_duplicates': len(duplicates['similar_duplicates']),
                'title_duplicates': len(duplicates['title_duplicates']),
                'content_duplicates': len(duplicates['content_duplicates']),
                'unique_articles': len(articles) - len(duplicates['exact_duplicates']),
                'duplicate_rate': len(duplicates['exact_duplicates']) / len(articles) if articles else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"중복 통계 조회 중 오류 발생: {e}")
            return {
                'total_articles': 0,
                'exact_duplicates': 0,
                'similar_duplicates': 0,
                'title_duplicates': 0,
                'content_duplicates': 0,
                'unique_articles': 0,
                'duplicate_rate': 0
            }


