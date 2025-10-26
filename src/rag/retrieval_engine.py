"""
검색 엔진
"""
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import re
from collections import defaultdict

from ..database.connection import get_db
from ..database.models import Article, ArticleKeyword, ArticleCategory, ArticleStockCode

logger = logging.getLogger(__name__)

class RetrievalEngine:
    """검색 엔진"""
    
    def __init__(self):
        self.search_weights = {
            'title': 3.0,
            'summary': 2.0,
            'body': 1.0,
            'keywords': 2.5,
            'categories': 1.5
        }
    
    def search_articles(self, query: str, filters: Optional[Dict] = None, 
                       top_k: int = 10) -> List[Dict]:
        """기사 검색"""
        try:
            # 1. 키워드 검색
            keyword_results = self._keyword_search(query, filters, top_k)
            
            # 2. 카테고리 검색
            category_results = self._category_search(query, filters, top_k)
            
            # 3. 메타데이터 검색
            metadata_results = self._metadata_search(query, filters, top_k)
            
            # 4. 결과 통합 및 점수 계산
            combined_results = self._combine_search_results(
                keyword_results, category_results, metadata_results
            )
            
            # 5. 재순위화
            reranked_results = self._rerank_results(combined_results, query)
            
            return reranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"기사 검색 중 오류 발생: {e}")
            return []
    
    def _keyword_search(self, query: str, filters: Optional[Dict], top_k: int) -> List[Dict]:
        """키워드 기반 검색"""
        try:
            db = next(get_db())
            try:
                # 쿼리 키워드 추출
                keywords = self._extract_search_keywords(query)
                
                if not keywords:
                    return []
                
                # 키워드 매칭 검색
                keyword_articles = db.query(Article).join(ArticleKeyword).filter(
                    ArticleKeyword.keyword.in_(keywords)
                ).distinct().all()
                
                # 제목/본문 텍스트 검색
                text_articles = db.query(Article).filter(
                    Article.title.contains(query) | 
                    Article.body.contains(query) |
                    Article.summary.contains(query)
                ).all()
                
                # 결과 통합
                all_articles = list(set(keyword_articles + text_articles))
                
                # 점수 계산
                results = []
                for article in all_articles:
                    score = self._calculate_keyword_score(article, query, keywords)
                    results.append({
                        'article': self._format_article(article),
                        'score': score,
                        'search_type': 'keyword'
                    })
                
                return results
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"키워드 검색 중 오류 발생: {e}")
            return []
    
    def _category_search(self, query: str, filters: Optional[Dict], top_k: int) -> List[Dict]:
        """카테고리 기반 검색"""
        try:
            db = next(get_db())
            try:
                # 쿼리에서 카테고리 키워드 추출
                category_keywords = self._extract_category_keywords(query)
                
                if not category_keywords:
                    return []
                
                # 카테고리 매칭 검색
                category_articles = db.query(Article).join(ArticleCategory).filter(
                    ArticleCategory.large_code_nm.in_(category_keywords) |
                    ArticleCategory.middle_code_nm.in_(category_keywords) |
                    ArticleCategory.small_code_nm.in_(category_keywords)
                ).distinct().all()
                
                # 점수 계산
                results = []
                for article in all_articles:
                    score = self._calculate_category_score(article, category_keywords)
                    results.append({
                        'article': self._format_article(article),
                        'score': score,
                        'search_type': 'category'
                    })
                
                return results
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"카테고리 검색 중 오류 발생: {e}")
            return []
    
    def _metadata_search(self, query: str, filters: Optional[Dict], top_k: int) -> List[Dict]:
        """메타데이터 기반 검색"""
        try:
            db = next(get_db())
            try:
                query_builder = db.query(Article).filter(Article.is_processed == True)
                
                # 날짜 필터
                if filters and 'start_date' in filters:
                    query_builder = query_builder.filter(Article.service_daytime >= filters['start_date'])
                
                if filters and 'end_date' in filters:
                    query_builder = query_builder.filter(Article.service_daytime <= filters['end_date'])
                
                # 기자 필터
                if filters and 'writers' in filters:
                    query_builder = query_builder.filter(Article.writers.in_(filters['writers']))
                
                # 카테고리 필터
                if filters and 'categories' in filters:
                    query_builder = query_builder.join(ArticleCategory).filter(
                        ArticleCategory.large_code_nm.in_(filters['categories'])
                    )
                
                articles = query_builder.limit(top_k * 2).all()
                
                # 점수 계산
                results = []
                for article in articles:
                    score = self._calculate_metadata_score(article, query, filters)
                    results.append({
                        'article': self._format_article(article),
                        'score': score,
                        'search_type': 'metadata'
                    })
                
                return results
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"메타데이터 검색 중 오류 발생: {e}")
            return []
    
    def _extract_search_keywords(self, query: str) -> List[str]:
        """검색 키워드 추출"""
        try:
            # 불용어 제거
            stop_words = {'이', '가', '을', '를', '에', '의', '로', '으로', '와', '과', '는', '은', '도', '만'}
            
            # 단어 분리
            words = re.findall(r'[가-힣\w]+', query.lower())
            
            # 불용어 제거 및 길이 필터링
            keywords = [word for word in words if word not in stop_words and len(word) >= 2]
            
            return keywords
            
        except Exception as e:
            logger.error(f"검색 키워드 추출 중 오류 발생: {e}")
            return []
    
    def _extract_category_keywords(self, query: str) -> List[str]:
        """카테고리 키워드 추출"""
        try:
            category_keywords = {
                '정치': ['정치', '정부', '국회', '선거', '정당'],
                '경제': ['경제', '금융', '주식', '부동산', '기업'],
                '사회': ['사회', '사건', '사고', '범죄'],
                '국제': ['국제', '외교', '해외'],
                '문화': ['문화', '연예', '스포츠', '영화'],
                '기술': ['기술', 'IT', '과학', '디지털']
            }
            
            found_categories = []
            for category, keywords in category_keywords.items():
                if any(keyword in query for keyword in keywords):
                    found_categories.append(category)
            
            return found_categories
            
        except Exception as e:
            logger.error(f"카테고리 키워드 추출 중 오류 발생: {e}")
            return []
    
    def _calculate_keyword_score(self, article: Article, query: str, keywords: List[str]) -> float:
        """키워드 점수 계산"""
        try:
            score = 0.0
            
            # 제목 매칭 점수
            title_matches = sum(1 for keyword in keywords if keyword in article.title.lower())
            score += title_matches * self.search_weights['title']
            
            # 요약 매칭 점수
            if article.summary:
                summary_matches = sum(1 for keyword in keywords if keyword in article.summary.lower())
                score += summary_matches * self.search_weights['summary']
            
            # 본문 매칭 점수
            if article.body:
                body_matches = sum(1 for keyword in keywords if keyword in article.body.lower())
                score += body_matches * self.search_weights['body']
            
            # 키워드 테이블 매칭 점수
            db = next(get_db())
            try:
                keyword_count = db.query(ArticleKeyword).filter(
                    ArticleKeyword.article_id == article.id,
                    ArticleKeyword.keyword.in_(keywords)
                ).count()
                score += keyword_count * self.search_weights['keywords']
            finally:
                db.close()
            
            return score
            
        except Exception as e:
            logger.error(f"키워드 점수 계산 중 오류 발생: {e}")
            return 0.0
    
    def _calculate_category_score(self, article: Article, category_keywords: List[str]) -> float:
        """카테고리 점수 계산"""
        try:
            score = 0.0
            
            db = next(get_db())
            try:
                # 카테고리 매칭 점수
                category_count = db.query(ArticleCategory).filter(
                    ArticleCategory.article_id == article.id,
                    ArticleCategory.large_code_nm.in_(category_keywords)
                ).count()
                score += category_count * self.search_weights['categories']
            finally:
                db.close()
            
            return score
            
        except Exception as e:
            logger.error(f"카테고리 점수 계산 중 오류 발생: {e}")
            return 0.0
    
    def _calculate_metadata_score(self, article: Article, query: str, filters: Optional[Dict]) -> float:
        """메타데이터 점수 계산"""
        try:
            score = 0.0
            
            # 최신성 점수
            if article.service_daytime:
                days_ago = (datetime.utcnow() - article.service_daytime).days
                if days_ago < 7:  # 최근 1주일
                    score += 2.0
                elif days_ago < 30:  # 최근 1개월
                    score += 1.0
                elif days_ago < 365:  # 최근 1년
                    score += 0.5
            
            # 필터 매칭 점수
            if filters:
                if 'start_date' in filters and article.service_daytime:
                    if article.service_daytime.date() >= filters['start_date']:
                        score += 1.0
                
                if 'end_date' in filters and article.service_daytime:
                    if article.service_daytime.date() <= filters['end_date']:
                        score += 1.0
            
            return score
            
        except Exception as e:
            logger.error(f"메타데이터 점수 계산 중 오류 발생: {e}")
            return 0.0
    
    def _combine_search_results(self, keyword_results: List[Dict], 
                              category_results: List[Dict], 
                              metadata_results: List[Dict]) -> List[Dict]:
        """검색 결과 통합"""
        try:
            # 결과 통합을 위한 딕셔너리
            combined_dict = {}
            
            # 키워드 검색 결과 추가
            for result in keyword_results:
                article_id = result['article']['id']
                if article_id not in combined_dict:
                    combined_dict[article_id] = result
                else:
                    # 기존 결과와 점수 합산
                    combined_dict[article_id]['score'] += result['score']
                    combined_dict[article_id]['search_types'] = combined_dict[article_id].get('search_types', []) + ['keyword']
            
            # 카테고리 검색 결과 추가
            for result in category_results:
                article_id = result['article']['id']
                if article_id not in combined_dict:
                    combined_dict[article_id] = result
                else:
                    combined_dict[article_id]['score'] += result['score']
                    combined_dict[article_id]['search_types'] = combined_dict[article_id].get('search_types', []) + ['category']
            
            # 메타데이터 검색 결과 추가
            for result in metadata_results:
                article_id = result['article']['id']
                if article_id not in combined_dict:
                    combined_dict[article_id] = result
                else:
                    combined_dict[article_id]['score'] += result['score']
                    combined_dict[article_id]['search_types'] = combined_dict[article_id].get('search_types', []) + ['metadata']
            
            return list(combined_dict.values())
            
        except Exception as e:
            logger.error(f"검색 결과 통합 중 오류 발생: {e}")
            return keyword_results + category_results + metadata_results
    
    def _rerank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """결과 재순위화"""
        try:
            # 점수 기반 정렬
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # 추가 보너스 점수 적용
            for i, result in enumerate(results):
                # 순위 보너스
                rank_bonus = max(0, (len(results) - i) * 0.1)
                result['final_score'] = result['score'] + rank_bonus
                
                # 검색 타입 다양성 보너스
                search_types = result.get('search_types', [])
                if len(set(search_types)) > 1:
                    result['final_score'] += 0.5
            
            # 최종 점수로 재정렬
            results.sort(key=lambda x: x['final_score'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"결과 재순위화 중 오류 발생: {e}")
            return results
    
    def _format_article(self, article: Article) -> Dict:
        """기사 정보 포맷팅"""
        try:
            return {
                'id': article.id,
                'art_id': article.art_id,
                'title': article.title,
                'summary': article.summary,
                'service_daytime': article.service_daytime,
                'article_url': article.article_url,
                'writers': article.writers,
                'is_embedded': article.is_embedded
            }
            
        except Exception as e:
            logger.error(f"기사 정보 포맷팅 중 오류 발생: {e}")
            return {
                'id': article.id,
                'art_id': article.art_id,
                'title': article.title,
                'summary': '',
                'service_daytime': None,
                'article_url': '',
                'writers': '',
                'is_embedded': False
            }
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """검색 제안"""
        try:
            db = next(get_db())
            try:
                # 제목에서 유사한 키워드 검색
                suggestions = db.query(Article.title).filter(
                    Article.title.contains(query),
                    Article.is_processed == True
                ).distinct().limit(limit).all()
                
                return [suggestion[0] for suggestion in suggestions]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"검색 제안 중 오류 발생: {e}")
            return []
    
    def get_popular_keywords(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """인기 키워드 조회"""
        try:
            db = next(get_db())
            try:
                # 최근 기사들의 키워드 통계
                start_date = datetime.utcnow() - timedelta(days=days)
                
                keyword_stats = db.query(
                    ArticleKeyword.keyword,
                    ArticleKeyword.keyword_type,
                    db.func.count(ArticleKeyword.id).label('count')
                ).join(Article).filter(
                    Article.service_daytime >= start_date,
                    Article.is_processed == True
                ).group_by(
                    ArticleKeyword.keyword,
                    ArticleKeyword.keyword_type
                ).order_by(
                    db.func.count(ArticleKeyword.id).desc()
                ).limit(limit).all()
                
                return [
                    {
                        'keyword': stat.keyword,
                        'type': stat.keyword_type,
                        'count': stat.count
                    }
                    for stat in keyword_stats
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"인기 키워드 조회 중 오류 발생: {e}")
            return []


