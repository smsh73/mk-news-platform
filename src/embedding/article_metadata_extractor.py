"""
기사 메타데이터 추출 및 인덱싱 시스템
"""
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class ArticleMetadataExtractor:
    """기사 메타데이터 추출기"""
    
    def __init__(self):
        self.entity_patterns = {
            'company': [
                r'([가-힣]+(?:그룹|기업|컨소시엄|회사|증권|은행|보험|생명))',
                r'([A-Z]+)주'
            ],
            'person': [
                r'([가-힣]{2,4})\s*(?:회장|사장|대표รวม|이사|임원|부장|팀장)',
                r'([가-힣]{2,4})\s*(?:씨|님)'
            ],
            'location': [
                r'([가-힣]+(?:시|도|구|군|동|읍|면))',
            ],
            'date': [
                r'(\d{4}년\s?\d{1,2}월\s?\d{1,2}일)',
                r'(\d{4}-\d{2}-\d{2})',
            ],
            'number': [
                r'(\d{1,3}(?:,\d{3})*(?:원|달러|억원|만원|조원|%|배))',
            ]
        }
    
    def extract_metadata(self, article_data: Dict) -> Dict:
        """기사에서 메타데이터 추출"""
        try:
            title = article_data.get('title', '')
            body = article_data.get('body', '')
            summary = article_data.get('summary', '')
            
            # 기본 메타데이터
            metadata = {
                'title_length': len(title),
                'body_length': len(body),
                'summary_length': len(summary),
                'total_length': len(title) + len(body) + len(summary),
                'word_count': len(body.split()),
                'has_summary': bool(summary),
            }
            
            # 엔티티 추출
            entities = self._extract_entities(title + ' ' + body)
            metadata['entities'] = entities
            
            # 분류 정보
            categories = article_data.get('categories', [])
            metadata['categories'] = self._normalize_categories(categories)
            
            # 키워드
            keywords = article_data.get('keywords', [])
            metadata['keywords'] = [kw.get('keyword') for kw in keywords if kw]
            
            # 주식 코드
            stock_codes = article_data.get('stock_codes', [])
            metadata['stock_codes'] = [sc.get('stock_code') for sc in stock_codes if sc]
            
            # 시간 정보
            service_daytime = article_data.get('service_daytime')
            if service_daytime:
                if isinstance(service_daytime, str):
                    try:
                        service_daytime = datetime.fromisoformat(service_daytime.replace('Z', '+00:00'))
                    except:
                        service_daytime = None
                
                if service_daytime:
                    metadata['year'] = service_daytime.year
                    metadata['month'] = service_daytime.month
                    metadata['day'] = service_daytime.day
                    metadata['weekday'] = service_daytime.strftime('%A')
                    metadata['hour'] = service_daytime.hour
            
            # 기사 타입 추론
            metadata['article_type'] = self._infer_article_type(title, body)
            
            # 중요도 점수
            metadata['importance_score'] = self._calculate_importance_score(metadata)
            
            # 인덱싱용 텍스트 생성
            metadata['indexing_text'] = self._generate_indexing_text(article_data, metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"메타데이터 추출 중 오류 발생: {e}")
            return {}
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """엔티티 추출"""
        entities = {
            'company': [],
            'person': [],
            'location': [],
            'date': [],
            'number': []
        }
        
        for entity_type, patterns in self.entity_patterns.items():
            extracted = set()
            for pattern in patterns:
                matches = re.findall(pattern, text)
                extracted.update(matches)
            entities[entity_type] = list(extracted)
        
        return entities
    
    def _normalize_categories(self, categories: List[Dict]) -> List[str]:
        """카테고리 정규화"""
        normalized = []
        for cat in categories:
            code_nm = cat.get('code_nm', '')
            if code_nm:
                normalized.append(code_nm)
        return normalized
    
    def _infer_article_type(self, title: str, body: str) -> str:
        """기사 타입 추론"""
        title_lower = title.lower()
        body_lower = body.lower()
        
        if any(keyword in title_lower or keyword in body_lower for keyword in ['배당', '주가', '증시', '상장']):
            return 'financial'
        elif any(keyword in title_lower or keyword in body_lower for keyword in ['인수', '합병', 'M&A', '투자']):
            return 'mna'
        elif any(keyword in title_lower or keyword in body_lower for keyword in ['연봉', '채용', '인사']):
            return 'people'
        elif any(keyword in title_lower or keyword in body_lower for keyword in ['정책', '법안', '규제']):
            return 'policy'
        elif any(keyword in title_lower or keyword in body_lower for keyword in ['기술', 'AI', '디지털', '스마트']):
            return 'technology'
        else:
            return 'general'
    
    def _calculate_importance_score(self, metadata: Dict) -> float:
        """중요도 점수 계산"""
        score = 0.0
        
        # 키워드 개수
        score += len(metadata.get('keywords', [])) * 0.5
        
        # 주식 코드 존재
        if metadata.get('stock_codes'):
            score += 2.0
        
        # 엔티티 존재
        total_entities = sum(len(entities) for entities in metadata.get('entities', {}).values())
        score += total_entities * 0.3
        
        # 본문 길이
        body_length = metadata.get('body_length', 0)
        if body_length > 1000:
            score += 1.0
        elif body_length > 500:
            score += 0.5
        
        return round(score, 2)
    
    def _generate_indexing_text(self, article_data: Dict, metadata: Dict) -> str:
        """인덱싱용 텍스트 생성"""
        parts = []
        
        # 제목 (가중치 높음)
        title = article_data.get('title', '')
        if title:
            parts.append(title)
            parts.append(title)  # 제목 반복으로 가중치 증가
        
        # 요약
        summary = article_data.get('summary', '')
        if summary:
            parts.append(summary)
        
        # 카테고리
        categories = metadata.get('categories', [])
        if categories:
            parts.extend(categories)
        
        # 키워드
        keywords = metadata.get('keywords', [])
        if keywords:
            parts.extend(keywords)
        
        # 엔티티
        entities = metadata.get('entities', {})
        for entity_list in entities.values():
            parts.extend(entity_list)
        
        return ' '.join(parts)
    
    def generate_metadata_hash(self, article_data: Dict, metadata: Dict) -> str:
        """메타데이터 해시 생성"""
        # 해시에 포함할 필드들
        hash_fields = [
            article_data.get('art_id', ''),
            article_data.get('title', ''),
            metadata.get('categories', []),
            metadata.get('keywords', []),
        ]
        
        hash_string = '|'.join(str(field) for field in hash_fields)
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()

