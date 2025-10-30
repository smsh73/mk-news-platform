"""
Hybrid RAG 시스템
"""
import os
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import re

from ..database.connection import get_db
from ..database.models import Article, ArticleKeyword, ArticleCategory, ArticleImage, ArticleStockCode
from ..embedding.embedding_service import EmbeddingService
from ..vector_search.vector_indexer import VectorIndexer
from .gemini_client import GeminiClient
from .query_processor import QueryProcessor
from .retrieval_engine import RetrievalEngine

logger = logging.getLogger(__name__)

class HybridRAGSystem:
    """Hybrid RAG 시스템"""
    
    def __init__(self, project_id: str = "mk-ai-project-473000", region: str = "asia-northeast3"):
        self.project_id = project_id
        self.region = region
        
        # 컴포넌트 초기화 (테스트 모드)
        self.embedding_service = EmbeddingService()
        
        # GCP 서비스는 테스트 모드에서 비활성화
        try:
            self.vector_indexer = VectorIndexer(project_id, region)
        except Exception as e:
            logger.warning(f"VectorIndexer 초기화 실패 (테스트 모드): {e}")
            self.vector_indexer = None
            
        try:
            self.gemini_client = GeminiClient()
        except Exception as e:
            logger.warning(f"GeminiClient 초기화 실패 (테스트 모드): {e}")
            self.gemini_client = None
            
        self.query_processor = QueryProcessor()
        self.retrieval_engine = RetrievalEngine()
        
        # 설정
        self.max_retrieved_docs = 20
        self.max_context_length = 4000
        self.similarity_threshold = 0.7
    
    def process_query(self, query: str, filters: Optional[Dict] = None, 
                     top_k: int = 10, similarity_threshold: float = 0.7,
                     max_context_length: int = 4000, weights: Optional[Dict] = None) -> Dict:
        """쿼리 처리 및 응답 생성"""
        try:
            start_time = datetime.utcnow()
            
            # 1. 쿼리 전처리 및 분석
            processed_query = self.query_processor.analyze_query(query)
            
            # 2. 하이브리드 검색 수행 (가중치 및 필터 적용)
            search_results = self._hybrid_search(
                processed_query, filters, top_k, similarity_threshold, weights
            )
            
            # 3. 검색 결과 후처리
            retrieved_docs = self._postprocess_results(search_results)
            
            # 4. 컨텍스트 구성
            context = self._build_context(retrieved_docs, processed_query)
            
            # 5. Gemini API로 응답 생성
            response = self.gemini_client.generate_response(
                query=query,
                context=context,
                retrieved_docs=retrieved_docs
            )
            
            # 6. 응답 후처리
            final_response = self._postprocess_response(response, retrieved_docs)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'query': query,
                'response': final_response,
                'retrieved_docs': retrieved_docs,
                'context_length': len(context),
                'processing_time': processing_time,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"쿼리 처리 중 오류 발생: {e}")
            return {
                'query': query,
                'response': f'죄송합니다. 쿼리 처리 중 오류가 발생했습니다: {str(e)}',
                'retrieved_docs': [],
                'context_length': 0,
                'processing_time': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _hybrid_search(self, processed_query: Dict, filters: Optional[Dict], 
                      top_k: int) -> List[Dict]:
        """하이브리드 검색 수행"""
        try:
            # 1. 벡터 검색 (의미적 유사도)
            vector_results = self._vector_search(processed_query, top_k)
            
            # 2. 키워드 검색 (정확한 매칭)
            keyword_results = self._keyword_search(processed_query, top_k)
            
            # 3. 메타데이터 필터링
            filtered_results = self._apply_metadata_filters(
                vector_results + keyword_results, filters
            )
            
            # 4. 결과 통합 및 중복 제거
            combined_results = self._combine_search_results(
                vector_results, keyword_results, filtered_results
            )
            
            # 5. 재순위화
            reranked_results = self._rerank_results(combined_results, processed_query)
            
            return reranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"하이브리드 검색 중 오류 발생: {e}")
            return []
    
    def _vector_search(self, processed_query: Dict, top_k: int) -> List[Dict]:
        """벡터 검색"""
        try:
            query_text = processed_query['processed_text']
            
            # 벡터 검색 수행
            search_results = self.vector_indexer.search_similar_articles(
                query=query_text,
                top_k=top_k * 2  # 더 많은 결과를 가져와서 후처리
            )
            
            # 결과 변환
            vector_results = []
            for result in search_results:
                vector_results.append({
                    'article': result['article'],
                    'similarity': result['similarity'],
                    'search_type': 'vector',
                    'rank': result['rank']
                })
            
            return vector_results
            
        except Exception as e:
            logger.error(f"벡터 검색 중 오류 발생: {e}")
            return []
    
    def _keyword_search(self, processed_query: Dict, top_k: int) -> List[Dict]:
        """키워드 검색"""
        try:
            keywords = processed_query.get('keywords', [])
            entities = processed_query.get('entities', {})
            
            if not keywords and not any(entities.values()):
                return []
            
            # 데이터베이스에서 키워드 검색
            db = next(get_db())
            try:
                # 키워드 매칭 쿼리
                keyword_articles = db.query(Article).join(ArticleKeyword).filter(
                    ArticleKeyword.keyword.in_(keywords)
                ).distinct().limit(top_k * 2).all()
                
                # 엔티티 매칭 쿼리
                entity_articles = []
                for entity_type, entity_list in entities.items():
                    if entity_list:
                        articles = db.query(Article).join(ArticleKeyword).filter(
                            ArticleKeyword.keyword.in_(entity_list),
                            ArticleKeyword.keyword_type == entity_type
                        ).distinct().limit(top_k).all()
                        entity_articles.extend(articles)
                
                # 결과 통합
                all_articles = list(set(keyword_articles + entity_articles))
                
                keyword_results = []
                for i, article in enumerate(all_articles):
                    keyword_results.append({
                        'article': {
                            'id': article.id,
                            'art_id': article.art_id,
                            'title': article.title,
                            'summary': article.summary,
                            'service_daytime': article.service_daytime,
                            'article_url': article.article_url
                        },
                        'similarity': 1.0,  # 키워드 매칭은 완전 일치
                        'search_type': 'keyword',
                        'rank': i + 1
                    })
                
                return keyword_results
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"키워드 검색 중 오류 발생: {e}")
            return []
    
    def _apply_metadata_filters(self, results: List[Dict], 
                              filters: Optional[Dict]) -> List[Dict]:
        """메타데이터 필터 적용"""
        if not filters:
            return results
        
        try:
            filtered_results = []
            
            for result in results:
                article = result['article']
                
                # 날짜 필터
                if 'start_date' in filters and article.get('service_daytime'):
                    if article['service_daytime'] < filters['start_date']:
                        continue
                
                if 'end_date' in filters and article.get('service_daytime'):
                    if article['service_daytime'] > filters['end_date']:
                        continue
                
                # 카테고리 필터
                if 'categories' in filters:
                    # 카테고리 정보 조회
                    article_categories = article.get('art_org_class', '')
                    if article_categories:
                        categories_list = article_categories.split(',') if isinstance(article_categories, str) else article_categories
                        filter_categories = filters['categories']
                        if not any(cat in categories_list for cat in filter_categories):
                            continue
                
                # 기자 필터
                if 'writers' in filters:
                    # 기자 정보 매칭
                    article_writer = article.get('writer', '') or article.get('author', '')
                    if article_writer:
                        filter_writers = filters['writers']
                        if not any(writer.lower() in article_writer.lower() for writer in filter_writers):
                            continue
                
                filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"메타데이터 필터 적용 중 오류 발생: {e}")
            return results
    
    def _combine_search_results(self, vector_results: List[Dict], 
                              keyword_results: List[Dict], 
                              filtered_results: List[Dict]) -> List[Dict]:
        """검색 결과 통합"""
        try:
            # 중복 제거를 위한 딕셔너리
            combined_dict = {}
            
            # 벡터 검색 결과 추가
            for result in vector_results:
                article_id = result['article']['id']
                combined_dict[article_id] = result
            
            # 키워드 검색 결과 추가 (벡터 검색 결과와 중복되지 않는 경우)
            for result in keyword_results:
                article_id = result['article']['id']
                if article_id not in combined_dict:
                    combined_dict[article_id] = result
                else:
                    # 기존 결과와 통합 (유사도 점수 조합)
                    existing = combined_dict[article_id]
                    combined_dict[article_id] = {
                        **existing,
                        'similarity': max(existing['similarity'], result['similarity']),
                        'search_types': ['vector', 'keyword']
                    }
            
            return list(combined_dict.values())
            
        except Exception as e:
            logger.error(f"검색 결과 통합 중 오류 발생: {e}")
            return vector_results + keyword_results
    
    def _rerank_results(self, results: List[Dict], processed_query: Dict) -> List[Dict]:
        """결과 재순위화"""
        try:
            # 다양한 요소를 고려한 재순위화
            for result in results:
                score = result['similarity']
                
                # 최신성 보너스
                if result['article'].get('service_daytime'):
                    days_ago = (datetime.utcnow() - result['article']['service_daytime']).days
                    if days_ago < 30:  # 최근 30일 이내
                        score += 0.1
                    elif days_ago < 365:  # 최근 1년 이내
                        score += 0.05
                
                # 검색 타입 보너스
                if 'search_types' in result and 'keyword' in result['search_types']:
                    score += 0.05
                
                # 제목 매칭 보너스
                title = result['article'].get('title', '').lower()
                query_text = processed_query['processed_text'].lower()
                if any(word in title for word in query_text.split()):
                    score += 0.1
                
                result['final_score'] = score
            
            # 최종 점수로 정렬
            results.sort(key=lambda x: x['final_score'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"결과 재순위화 중 오류 발생: {e}")
            return results
    
    def _postprocess_results(self, results: List[Dict]) -> List[Dict]:
        """검색 결과 후처리"""
        try:
            processed_results = []
            
            for result in results:
                article = result['article']
                
                # 기사 내용 요약 (너무 긴 경우)
                if len(article.get('summary', '')) > 500:
                    article['summary'] = article['summary'][:500] + '...'
                
                # 메타데이터 추가
                processed_result = {
                    'article': article,
                    'similarity': result['similarity'],
                    'search_type': result.get('search_type', 'unknown'),
                    'rank': result.get('rank', 0),
                    'final_score': result.get('final_score', result['similarity'])
                }
                
                processed_results.append(processed_result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"검색 결과 후처리 중 오류 발생: {e}")
            return results
    
    def _build_context(self, retrieved_docs: List[Dict], processed_query: Dict) -> str:
        """컨텍스트 구성"""
        try:
            context_parts = []
            current_length = 0
            
            for i, doc in enumerate(retrieved_docs):
                article = doc['article']
                
                # 기사 정보 구성
                article_info = f"""
기사 {i+1}:
제목: {article.get('title', '')}
요약: {article.get('summary', '')}
발행일: {article.get('service_daytime', '').strftime('%Y-%m-%d') if article.get('service_daytime') else ''}
URL: {article.get('article_url', '')}
"""
                
                # 길이 체크
                if current_length + len(article_info) > self.max_context_length:
                    break
                
                context_parts.append(article_info)
                current_length += len(article_info)
            
            return '\n'.join(context_parts)
            
        except Exception as e:
            logger.error(f"컨텍스트 구성 중 오류 발생: {e}")
            return ""
    
    def _postprocess_response(self, response: Dict, retrieved_docs: List[Dict]) -> Dict:
        """응답 후처리"""
        try:
            # 응답에 참조 기사 정보 추가
            if retrieved_docs:
                response['references'] = [
                    {
                        'title': doc['article']['title'],
                        'url': doc['article']['article_url'],
                        'similarity': doc['similarity']
                    }
                    for doc in retrieved_docs[:5]  # 상위 5개만
                ]
            
            return response
            
        except Exception as e:
            logger.error(f"응답 후처리 중 오류 발생: {e}")
            return response
    
    def get_system_stats(self) -> Dict:
        """시스템 통계 조회"""
        try:
            db = next(get_db())
            try:
                stats = {
                    'total_articles': db.query(Article).count(),
                    'processed_articles': db.query(Article).filter(Article.is_processed == True).count(),
                    'embedded_articles': db.query(Article).filter(Article.is_embedded == True).count(),
                    'recent_articles': db.query(Article).filter(
                        Article.service_daytime >= datetime.utcnow() - timedelta(days=30)
                    ).count(),
                    'categories': db.query(ArticleCategory).distinct(ArticleCategory.large_code_nm).count()
                }
                
                return stats
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"시스템 통계 조회 중 오류 발생: {e}")
            return {}
    
    def search_by_filters(self, filters: Dict, top_k: int = 10) -> List[Dict]:
        """필터 기반 검색"""
        try:
            db = next(get_db())
            try:
                query = db.query(Article).filter(Article.is_processed == True)
                
                # 날짜 필터
                if 'start_date' in filters:
                    query = query.filter(Article.service_daytime >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(Article.service_daytime <= filters['end_date'])
                
                # 카테고리 필터
                if 'categories' in filters:
                    query = query.join(ArticleCategory).filter(
                        ArticleCategory.large_code_nm.in_(filters['categories'])
                    )
                
                # 키워드 필터
                if 'keywords' in filters:
                    query = query.join(ArticleKeyword).filter(
                        ArticleKeyword.keyword.in_(filters['keywords'])
                    )
                
                articles = query.limit(top_k).all()
                
                return [
                    {
                        'id': article.id,
                        'art_id': article.art_id,
                        'title': article.title,
                        'summary': article.summary,
                        'service_daytime': article.service_daytime,
                        'article_url': article.article_url
                    }
                    for article in articles
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"필터 기반 검색 중 오류 발생: {e}")
            return []
    
    def _vector_search_with_filters(self, query: str, top_k: int, 
                                  filters: Optional[Dict] = None, 
                                  similarity_threshold: float = 0.7) -> List[Dict]:
        """메타데이터 필터가 적용된 벡터 검색"""
        try:
            # 기본 벡터 검색 수행
            search_results = self.vector_indexer.search_similar_articles(
                query=query,
                top_k=top_k * 2,  # 필터링 후 결과가 부족할 수 있으므로 더 많이 가져옴
                similarity_threshold=similarity_threshold
            )
            
            # 메타데이터 필터 적용
            if filters:
                filtered_results = self._apply_metadata_filters(search_results, filters)
            else:
                filtered_results = search_results
            
            # 결과 변환
            vector_results = []
            for result in filtered_results:
                vector_results.append({
                    'article': result['article'],
                    'similarity': result['similarity'],
                    'vector_score': result['similarity'],
                    'search_type': 'vector',
                    'rank': result.get('rank', 0)
                })
            
            return vector_results[:top_k]
            
        except Exception as e:
            logger.error(f"필터 적용 벡터 검색 중 오류 발생: {e}")
            return []
    
    def _keyword_search_with_filters(self, query: str, top_k: int, 
                                   filters: Optional[Dict] = None) -> List[Dict]:
        """메타데이터 필터가 적용된 키워드 검색"""
        try:
            db = next(get_db())
            try:
                # 기본 키워드 검색 쿼리
                search_query = db.query(Article).filter(
                    Article.is_processed == True,
                    Article.title.contains(query) | Article.summary.contains(query)
                )
                
                # 메타데이터 필터 적용
                if filters:
                    search_query = self._apply_database_filters(search_query, filters)
                
                articles = search_query.limit(top_k * 2).all()
                
                # 키워드 매칭 점수 계산
                keyword_results = []
                for article in articles:
                    keyword_score = self._calculate_keyword_score(query, article)
                    if keyword_score > 0:
                        keyword_results.append({
                            'article': {
                                'id': article.id,
                                'title': article.title,
                                'summary': article.summary,
                                'service_daytime': article.service_daytime,
                                'article_url': article.article_url
                            },
                            'keyword_score': keyword_score,
                            'search_type': 'keyword'
                        })
                
                return keyword_results[:top_k]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"필터 적용 키워드 검색 중 오류 발생: {e}")
            return []
    
    def _apply_database_filters(self, query, filters: Dict):
        """데이터베이스 쿼리에 필터 적용"""
        try:
            # 카테고리 필터
            if 'category' in filters:
                query = query.join(ArticleCategory).filter(
                    ArticleCategory.large_code_nm == filters['category']
                )
            
            # 날짜 범위 필터
            if 'start_date' in filters:
                from datetime import datetime
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(Article.service_daytime >= start_date)
            
            if 'end_date' in filters:
                from datetime import datetime
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(Article.service_daytime <= end_date)
            
            # 작성자 필터
            if 'writer' in filters:
                query = query.filter(Article.writers.contains(filters['writer']))
            
            # 최소 기사 길이 필터
            if 'min_length' in filters:
                query = query.filter(Article.body.length() >= filters['min_length'])
            
            # 이미지 포함 필터
            if 'has_images' in filters and filters['has_images']:
                query = query.join(ArticleImage).filter(ArticleImage.image_url.isnot(None))
            
            # 주식 코드 필터
            if 'stock_codes' in filters:
                query = query.join(ArticleStockCode).filter(
                    ArticleStockCode.stock_code.in_(filters['stock_codes'])
                )
            
            # 필수 키워드 필터
            if 'required_keywords' in filters:
                for keyword in filters['required_keywords']:
                    query = query.filter(
                        Article.title.contains(keyword) | Article.summary.contains(keyword)
                    )
            
            return query
            
        except Exception as e:
            logger.error(f"데이터베이스 필터 적용 중 오류 발생: {e}")
            return query
    
    def _calculate_keyword_score(self, query: str, article) -> float:
        """키워드 매칭 점수 계산"""
        try:
            query_words = set(query.lower().split())
            title_words = set(article.title.lower().split())
            summary_words = set(article.summary.lower().split())
            
            # 제목 매칭 점수 (가중치 높음)
            title_matches = len(query_words.intersection(title_words))
            title_score = title_matches / len(query_words) if query_words else 0
            
            # 요약 매칭 점수
            summary_matches = len(query_words.intersection(summary_words))
            summary_score = summary_matches / len(query_words) if query_words else 0
            
            # 가중 평균
            keyword_score = (title_score * 0.7) + (summary_score * 0.3)
            
            return keyword_score
            
        except Exception as e:
            logger.error(f"키워드 점수 계산 중 오류 발생: {e}")
            return 0.0
    
    def _combine_and_rerank_with_weights(self, vector_results: List[Dict], 
                                        keyword_results: List[Dict], 
                                        top_k: int, weights: Dict) -> List[Dict]:
        """가중치를 적용한 결과 통합 및 리랭킹"""
        try:
            # 결과 통합
            combined_results = {}
            
            # 벡터 검색 결과 추가
            for result in vector_results:
                article_id = result['article']['id']
                if article_id not in combined_results:
                    combined_results[article_id] = {
                        'article': result['article'],
                        'vector_score': result.get('vector_score', 0),
                        'keyword_score': 0,
                        'rerank_score': 0
                    }
                else:
                    combined_results[article_id]['vector_score'] = result.get('vector_score', 0)
            
            # 키워드 검색 결과 추가
            for result in keyword_results:
                article_id = result['article']['id']
                if article_id not in combined_results:
                    combined_results[article_id] = {
                        'article': result['article'],
                        'vector_score': 0,
                        'keyword_score': result.get('keyword_score', 0),
                        'rerank_score': 0
                    }
                else:
                    combined_results[article_id]['keyword_score'] = result.get('keyword_score', 0)
            
            # 가중치 적용 최종 점수 계산
            final_results = []
            for article_id, scores in combined_results.items():
                final_score = (
                    scores['vector_score'] * weights['vector_weight'] +
                    scores['keyword_score'] * weights['keyword_weight'] +
                    scores['rerank_score'] * weights['rerank_weight']
                )
                
                final_results.append({
                    'article': scores['article'],
                    'similarity': final_score,
                    'vector_score': scores['vector_score'],
                    'keyword_score': scores['keyword_score'],
                    'rerank_score': scores['rerank_score'],
                    'final_score': final_score
                })
            
            # 최종 점수로 정렬
            final_results.sort(key=lambda x: x['final_score'], reverse=True)
            
            return final_results[:top_k]
            
        except Exception as e:
            logger.error(f"가중치 적용 리랭킹 중 오류 발생: {e}")
            return []
    
    def generate_article_analysis(self, article, timeline_years: int = 3,
                                analysis_depth: str = "상세", 
                                include_timeline: bool = True,
                                include_current: bool = True,
                                include_future: bool = True) -> Dict:
        """개별 기사 해설 생성"""
        try:
            analysis_result = {
                "article_id": article.id,
                "timeline_analysis": "",
                "current_analysis": "",
                "future_analysis": "",
                "reference_articles": [],
                "processing_time": 0,
                "analysis_depth": analysis_depth
            }
            
            # 과거 타임라인 분석
            if include_timeline:
                timeline_analysis = self._generate_timeline_analysis(
                    article, timeline_years
                )
                analysis_result["timeline_analysis"] = timeline_analysis
            
            # 현재 기사 논설
            if include_current:
                current_analysis = self._generate_current_analysis(article)
                analysis_result["current_analysis"] = current_analysis
            
            # 향후 전망
            if include_future:
                future_analysis = self._generate_future_analysis(article)
                analysis_result["future_analysis"] = future_analysis
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"기사 해설 생성 중 오류 발생: {e}")
            return {
                "article_id": article.id,
                "timeline_analysis": "분석 중 오류가 발생했습니다.",
                "current_analysis": "분석 중 오류가 발생했습니다.",
                "future_analysis": "분석 중 오류가 발생했습니다.",
                "reference_articles": [],
                "processing_time": 0,
                "analysis_depth": analysis_depth
            }
    
    def _generate_timeline_analysis(self, article, timeline_years: int) -> str:
        """과거 타임라인 분석 생성"""
        try:
            # 관련 기사 검색
            related_articles = self._search_related_articles(article, timeline_years)
            
            # 타임라인 분석 생성
            timeline_text = f"지난 {timeline_years}년간의 관련 기사 분석:\n\n"
            
            for related_article in related_articles[:5]:  # 상위 5개 기사만
                timeline_text += f"- {related_article['service_daytime']}: {related_article['title']}\n"
            
            return timeline_text
            
        except Exception as e:
            logger.error(f"타임라인 분석 생성 중 오류 발생: {e}")
            return "타임라인 분석을 생성할 수 없습니다."
    
    def _generate_current_analysis(self, article) -> str:
        """현재 기사 논설 생성"""
        try:
            # 기사 내용 분석
            analysis = f"현재 기사 분석:\n\n"
            analysis += f"제목: {article.title}\n"
            analysis += f"요약: {article.summary}\n"
            analysis += f"주요 논점: [AI가 분석한 주요 논점]\n"
            analysis += f"핵심 키워드: [추출된 핵심 키워드]\n"
            
            return analysis
            
        except Exception as e:
            logger.error(f"현재 기사 분석 생성 중 오류 발생: {e}")
            return "현재 기사 분석을 생성할 수 없습니다."
    
    def _generate_future_analysis(self, article) -> str:
        """향후 전망 분석 생성"""
        try:
            future_analysis = f"향후 전망 분석:\n\n"
            future_analysis += f"기사 주제: {article.title}\n"
            future_analysis += f"예상 추이: [AI가 분석한 향후 전망]\n"
            future_analysis += f"관련 이슈: [관련된 향후 이슈들]\n"
            future_analysis += f"영향 요인: [영향을 미칠 수 있는 요인들]\n"
            
            return future_analysis
            
        except Exception as e:
            logger.error(f"향후 전망 분석 생성 중 오류 발생: {e}")
            return "향후 전망 분석을 생성할 수 없습니다."
    
    def _search_related_articles(self, article, timeline_years: int) -> List[Dict]:
        """관련 기사 검색"""
        try:
            # 기사 제목과 요약을 이용한 관련 기사 검색
            search_query = f"{article.title} {article.summary}"
            
            # 벡터 검색으로 관련 기사 찾기
            related_articles = self.vector_indexer.search_similar_articles(
                query=search_query,
                top_k=10
            )
            
            # 날짜 필터링 (지정된 년수 이내)
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=timeline_years * 365)
            
            filtered_articles = []
            for result in related_articles:
                article_date = result['article'].get('service_daytime')
                if article_date and article_date >= cutoff_date:
                    filtered_articles.append(result['article'])
            
            return filtered_articles
            
        except Exception as e:
            logger.error(f"관련 기사 검색 중 오류 발생: {e}")
            return []
