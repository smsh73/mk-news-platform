"""
쿼리 처리 및 분석 시스템
"""
import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import jieba
import nltk
from collections import Counter

logger = logging.getLogger(__name__)

class QueryProcessor:
    """쿼리 처리기"""
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
        self.entity_patterns = self._load_entity_patterns()
        self._initialize_nltk()
    
    def _initialize_nltk(self):
        """NLTK 초기화"""
        try:
            # 필요한 NLTK 데이터 다운로드
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            logger.warning(f"NLTK 초기화 중 오류 발생: {e}")
    
    def _load_stop_words(self) -> set:
        """불용어 로드"""
        korean_stop_words = {
            '이', '가', '을', '를', '에', '의', '로', '으로', '와', '과', '는', '은', '도', '만', '부터', '까지',
            '에서', '에게', '한테', '께', '보다', '처럼', '같이', '만큼', '쯤', '정도', '뿐', '뿐만', '아니라',
            '그리고', '또한', '또', '그런데', '하지만', '그러나', '따라서', '그러므로', '그래서', '왜냐하면',
            '때문에', '위해', '대해', '관해', '대한', '관한', '위한', '대한', '관한', '위한',
            '것', '거', '게', '걸', '거야', '거예요', '거죠', '거지', '거네', '거다',
            '있다', '없다', '되다', '하다', '이다', '아니다', '그렇다', '아니다',
            '이것', '그것', '저것', '이런', '그런', '저런', '이렇게', '그렇게', '저렇게',
            '여기', '거기', '저기', '어디', '언제', '왜', '어떻게', '무엇', '누구', '어느'
        }
        return korean_stop_words
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """엔티티 패턴 로드"""
        return {
            'person': [
                r'[가-힣]{2,4}(?=\s*씨|\s*님|\s*기자|\s*대표|\s*사장|\s*회장|\s*총재)',
                r'[가-힣]{2,4}(?=\s*씨|\s*님|\s*기자|\s*대표|\s*사장|\s*회장|\s*총재)',
            ],
            'company': [
                r'[가-힣\w\s]+(?:주식회사|유한회사|㈜|\(주\)|\(유\)|그룹|홀딩스)',
                r'[가-힣\w\s]+(?:은행|증권|보험|카드|금융)',
                r'[가-힣\w\s]+(?:기업|회사|법인|단체)'
            ],
            'location': [
                r'[가-힣]+(?:시|도|구|군|동|읍|면)',
                r'[가-힣]+(?:서울|부산|대구|인천|광주|대전|울산|세종)',
                r'[가-힣]+(?:강남|강북|서초|송파|마포|용산|영등포)'
            ],
            'date': [
                r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',
                r'\d{4}-\d{2}-\d{2}',
                r'\d{2}/\d{2}/\d{4}',
                r'\d{4}\.\d{2}\.\d{2}',
                r'(?:오늘|어제|내일|이번주|다음주|이번달|다음달|올해|작년|내년)'
            ],
            'number': [
                r'\d+조\s*\d+억\s*\d+만',
                r'\d+억\s*\d+만',
                r'\d+만\s*원',
                r'\d+%',
                r'\d+\.\d+%',
                r'\d+원',
                r'\d+개',
                r'\d+명',
                r'\d+건'
            ]
        }
    
    def analyze_query(self, query: str) -> Dict:
        """쿼리 분석"""
        try:
            # 기본 정보
            processed_query = {
                'original_query': query,
                'processed_text': self._preprocess_text(query),
                'keywords': [],
                'entities': {},
                'intent': '',
                'filters': {},
                'complexity': 'simple'
            }
            
            # 텍스트 전처리
            processed_text = processed_query['processed_text']
            
            # 키워드 추출
            keywords = self._extract_keywords(processed_text)
            processed_query['keywords'] = keywords
            
            # 엔티티 추출
            entities = self._extract_entities(processed_text)
            processed_query['entities'] = entities
            
            # 의도 분석
            intent = self._analyze_intent(processed_text)
            processed_query['intent'] = intent
            
            # 필터 추출
            filters = self._extract_filters(processed_text)
            processed_query['filters'] = filters
            
            # 복잡도 분석
            complexity = self._analyze_complexity(processed_text, keywords, entities)
            processed_query['complexity'] = complexity
            
            return processed_query
            
        except Exception as e:
            logger.error(f"쿼리 분석 중 오류 발생: {e}")
            return {
                'original_query': query,
                'processed_text': query,
                'keywords': [],
                'entities': {},
                'intent': 'unknown',
                'filters': {},
                'complexity': 'simple',
                'error': str(e)
            }
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        try:
            # 소문자 변환
            text = text.lower()
            
            # 특수 문자 정리
            text = re.sub(r'[^\w\s가-힣]', ' ', text)
            
            # 연속된 공백 정리
            text = re.sub(r'\s+', ' ', text)
            
            # 앞뒤 공백 제거
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"텍스트 전처리 중 오류 발생: {e}")
            return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        try:
            # 단어 분리
            words = text.split()
            
            # 불용어 제거
            filtered_words = [word for word in words if word not in self.stop_words]
            
            # 길이 필터링 (2글자 이상)
            keywords = [word for word in filtered_words if len(word) >= 2]
            
            # 빈도수 기반 키워드 선택
            word_counts = Counter(keywords)
            top_keywords = [word for word, count in word_counts.most_common(10)]
            
            return top_keywords
            
        except Exception as e:
            logger.error(f"키워드 추출 중 오류 발생: {e}")
            return []
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """엔티티 추출"""
        try:
            entities = {}
            
            for entity_type, patterns in self.entity_patterns.items():
                matches = []
                for pattern in patterns:
                    found = re.findall(pattern, text)
                    matches.extend(found)
                
                # 중복 제거 및 정리
                entities[entity_type] = list(set(matches))
            
            return entities
            
        except Exception as e:
            logger.error(f"엔티티 추출 중 오류 발생: {e}")
            return {}
    
    def _analyze_intent(self, text: str) -> str:
        """의도 분석"""
        try:
            # 질문 의도 패턴
            question_patterns = [
                r'무엇|뭐|어떤|어느',
                r'언제|몇시|몇일',
                r'어디|어느곳|어느지역',
                r'왜|어떻게|어떤이유',
                r'누구|누가|어느사람',
                r'얼마|몇|어느정도'
            ]
            
            # 정보 요청 의도
            if any(re.search(pattern, text) for pattern in question_patterns):
                return 'question'
            
            # 검색 의도
            search_keywords = ['찾다', '검색', '조회', '확인', '알다', '정보']
            if any(keyword in text for keyword in search_keywords):
                return 'search'
            
            # 비교 의도
            comparison_keywords = ['비교', '차이', 'vs', '대비', '대조']
            if any(keyword in text for keyword in comparison_keywords):
                return 'comparison'
            
            # 분석 의도
            analysis_keywords = ['분석', '평가', '판단', '의견', '견해']
            if any(keyword in text for keyword in analysis_keywords):
                return 'analysis'
            
            # 기본값
            return 'general'
            
        except Exception as e:
            logger.error(f"의도 분석 중 오류 발생: {e}")
            return 'unknown'
    
    def _extract_filters(self, text: str) -> Dict:
        """필터 추출"""
        try:
            filters = {}
            
            # 날짜 필터
            date_filters = self._extract_date_filters(text)
            if date_filters:
                filters.update(date_filters)
            
            # 카테고리 필터
            category_filters = self._extract_category_filters(text)
            if category_filters:
                filters.update(category_filters)
            
            # 기타 필터
            other_filters = self._extract_other_filters(text)
            if other_filters:
                filters.update(other_filters)
            
            return filters
            
        except Exception as e:
            logger.error(f"필터 추출 중 오류 발생: {e}")
            return {}
    
    def _extract_date_filters(self, text: str) -> Dict:
        """날짜 필터 추출"""
        try:
            filters = {}
            
            # 상대적 날짜
            if '오늘' in text:
                filters['start_date'] = datetime.now().date()
                filters['end_date'] = datetime.now().date()
            elif '어제' in text:
                yesterday = datetime.now() - timedelta(days=1)
                filters['start_date'] = yesterday.date()
                filters['end_date'] = yesterday.date()
            elif '이번주' in text:
                start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
                filters['start_date'] = start_of_week.date()
                filters['end_date'] = datetime.now().date()
            elif '이번달' in text:
                start_of_month = datetime.now().replace(day=1)
                filters['start_date'] = start_of_month.date()
                filters['end_date'] = datetime.now().date()
            elif '올해' in text:
                start_of_year = datetime.now().replace(month=1, day=1)
                filters['start_date'] = start_of_year.date()
                filters['end_date'] = datetime.now().date()
            
            # 절대적 날짜
            date_patterns = [
                r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',
                r'(\d{4})-(\d{2})-(\d{2})',
                r'(\d{2})/(\d{2})/(\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        if pattern == date_patterns[0]:  # YYYY년 MM월 DD일
                            year, month, day = match.groups()
                        elif pattern == date_patterns[1]:  # YYYY-MM-DD
                            year, month, day = match.groups()
                        else:  # MM/DD/YYYY
                            month, day, year = match.groups()
                        
                        date_obj = datetime(int(year), int(month), int(day))
                        filters['start_date'] = date_obj.date()
                        filters['end_date'] = date_obj.date()
                        break
                    except ValueError:
                        continue
            
            return filters
            
        except Exception as e:
            logger.error(f"날짜 필터 추출 중 오류 발생: {e}")
            return {}
    
    def _extract_category_filters(self, text: str) -> Dict:
        """카테고리 필터 추출"""
        try:
            filters = {}
            
            # 뉴스 카테고리 키워드
            category_keywords = {
                '정치': ['정치', '정부', '국회', '선거', '정당'],
                '경제': ['경제', '금융', '주식', '부동산', '기업'],
                '사회': ['사회', '사건', '사고', '범죄', '사고'],
                '국제': ['국제', '외교', '해외', '국제뉴스'],
                '문화': ['문화', '연예', '스포츠', '영화', '음악'],
                '기술': ['기술', 'IT', '과학', '디지털', '인공지능']
            }
            
            found_categories = []
            for category, keywords in category_keywords.items():
                if any(keyword in text for keyword in keywords):
                    found_categories.append(category)
            
            if found_categories:
                filters['categories'] = found_categories
            
            return filters
            
        except Exception as e:
            logger.error(f"카테고리 필터 추출 중 오류 발생: {e}")
            return {}
    
    def _extract_other_filters(self, text: str) -> Dict:
        """기타 필터 추출"""
        try:
            filters = {}
            
            # 기자 필터
            if '기자' in text:
                # 기자명 추출 시도
                writer_pattern = r'([가-힣]{2,4})\s*기자'
                writer_match = re.search(writer_pattern, text)
                if writer_match:
                    filters['writers'] = [writer_match.group(1)]
            
            # 키워드 필터
            if '키워드' in text or '주제' in text:
                # 키워드 추출 로직
                import re
                keyword_pattern = r'키워드[:\s]+([^\n]+)|주제[:\s]+([^\n]+)'
                matches = re.findall(keyword_pattern, text, re.IGNORECASE)
                if matches:
                    keywords = []
                    for match in matches:
                        keywords.extend([k.strip() for k in (match[0] or match[1]).split(',') if k.strip()])
                    if keywords:
                        filters['keywords'] = keywords
            
            return filters
            
        except Exception as e:
            logger.error(f"기타 필터 추출 중 오류 발생: {e}")
            return {}
    
    def _analyze_complexity(self, text: str, keywords: List[str], entities: Dict) -> str:
        """복잡도 분석"""
        try:
            complexity_score = 0
            
            # 텍스트 길이
            if len(text) > 50:
                complexity_score += 1
            if len(text) > 100:
                complexity_score += 1
            
            # 키워드 수
            if len(keywords) > 3:
                complexity_score += 1
            if len(keywords) > 6:
                complexity_score += 1
            
            # 엔티티 수
            total_entities = sum(len(entity_list) for entity_list in entities.values())
            if total_entities > 2:
                complexity_score += 1
            if total_entities > 5:
                complexity_score += 1
            
            # 복잡도 분류
            if complexity_score <= 1:
                return 'simple'
            elif complexity_score <= 3:
                return 'medium'
            else:
                return 'complex'
                
        except Exception as e:
            logger.error(f"복잡도 분석 중 오류 발생: {e}")
            return 'simple'
    
    def expand_query(self, processed_query: Dict) -> Dict:
        """쿼리 확장"""
        try:
            expanded_query = processed_query.copy()
            
            # 동의어 확장
            synonyms = self._get_synonyms(processed_query['keywords'])
            if synonyms:
                expanded_query['expanded_keywords'] = synonyms
            
            # 관련 키워드 추가
            related_keywords = self._get_related_keywords(processed_query['keywords'])
            if related_keywords:
                expanded_query['related_keywords'] = related_keywords
            
            return expanded_query
            
        except Exception as e:
            logger.error(f"쿼리 확장 중 오류 발생: {e}")
            return processed_query
    
    def _get_synonyms(self, keywords: List[str]) -> List[str]:
        """동의어 추출"""
        try:
            # 간단한 동의어 사전 (실제로는 더 포괄적인 사전 필요)
            synonym_dict = {
                '경제': ['금융', '재정', '경영'],
                '정치': ['정부', '국정', '정책'],
                '기업': ['회사', '법인', '기업체'],
                '주식': ['증권', '투자', '자본'],
                '부동산': ['부동산', '아파트', '건물']
            }
            
            synonyms = []
            for keyword in keywords:
                if keyword in synonym_dict:
                    synonyms.extend(synonym_dict[keyword])
            
            return list(set(synonyms))
            
        except Exception as e:
            logger.error(f"동의어 추출 중 오류 발생: {e}")
            return []
    
    def _get_related_keywords(self, keywords: List[str]) -> List[str]:
        """관련 키워드 추출"""
        try:
            # 간단한 관련 키워드 사전
            related_dict = {
                '경제': ['GDP', '인플레이션', '금리', '환율'],
                '정치': ['선거', '국회', '정당', '정책'],
                '기업': ['매출', '영업이익', '주가', '시장'],
                '주식': ['코스피', '코스닥', '증시', '투자']
            }
            
            related = []
            for keyword in keywords:
                if keyword in related_dict:
                    related.extend(related_dict[keyword])
            
            return list(set(related))
            
        except Exception as e:
            logger.error(f"관련 키워드 추출 중 오류 발생: {e}")
            return []


