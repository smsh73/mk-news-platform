"""
XML 파일 파싱 및 메타정보 추출 시스템
"""
import xml.etree.ElementTree as ET
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class XMLParser:
    """XML 파일 파서"""
    
    def __init__(self):
        self.namespaces = {
            'saltlux': 'http://www.saltlux.com/schema'
        }
    
    def parse_xml_file(self, xml_file_path: str) -> Optional[Dict]:
        """XML 파일 파싱"""
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # 기사 정보 추출
            article_data = self._extract_article_data(root)
            if not article_data:
                logger.warning(f"기사 데이터를 추출할 수 없습니다: {xml_file_path}")
                return None
            
            # 메타정보 추출
            metadata = self._extract_metadata(article_data)
            
            # 중복 체크용 해시 생성
            content_hash = self._generate_content_hash(article_data)
            
            return {
                'article_data': article_data,
                'metadata': metadata,
                'content_hash': content_hash,
                'file_path': xml_file_path,
                'parsed_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"XML 파싱 중 오류 발생: {xml_file_path}, {e}")
            return None
    
    def _extract_article_data(self, root) -> Optional[Dict]:
        """기사 데이터 추출"""
        try:
            article = root.find('article')
            if article is None:
                return None
            
            wms_article = article.find('wms_article')
            wms_article_body = article.find('wms_article_body')
            wms_article_summary = article.find('wms_article_summary')
            wms_code_classes = article.find('wms_code_classes')
            wms_article_images = article.find('wms_article_images')
            stock_codes = article.find('stock_codes')
            wms_article_keywords = article.find('wms_article_keywords')
            
            article_data = {
                'action': self._get_text(article, 'action'),
                'art_id': self._get_text(wms_article, 'art_id'),
                'art_year': self._get_int(wms_article, 'art_year'),
                'art_no': self._get_text(wms_article, 'art_no'),
                'gubun': self._get_text(wms_article, 'gubun'),
                'service_daytime': self._get_datetime(wms_article, 'service_daytime'),
                'title': self._get_cdata_text(wms_article, 'title'),
                'sub_title': self._get_cdata_text(wms_article, 'sub_title'),
                'media_code': self._get_text(wms_article, 'media_code'),
                'writers': self._get_cdata_text(wms_article, 'writers'),
                'free_type': self._get_text(wms_article, 'free_type'),
                'pub_div': self._get_text(wms_article, 'pub_div'),
                'pub_date': self._get_text(wms_article, 'pub_date'),
                'pub_edition': self._get_text(wms_article, 'pub_edition'),
                'pub_section': self._get_text(wms_article, 'pub_section'),
                'pub_page': self._get_text(wms_article, 'pub_page'),
                'reg_dt': self._get_datetime(wms_article, 'reg_dt'),
                'mod_dt': self._get_datetime(wms_article, 'mod_dt'),
                'art_org_class': self._get_text(wms_article, 'art_org_class'),
                'body': self._get_cdata_text(wms_article_body, 'body') if wms_article_body is not None else None,
                'summary': self._get_cdata_text(wms_article_summary, 'summary') if wms_article_summary is not None else None,
                'article_url': self._get_cdata_text(article, 'article_url'),
                'categories': self._extract_categories(wms_code_classes),
                'images': self._extract_images(wms_article_images),
                'stock_codes': self._extract_stock_codes(stock_codes),
                'keywords': self._extract_keywords(wms_article_keywords)
            }
            
            return article_data
            
        except Exception as e:
            logger.error(f"기사 데이터 추출 중 오류 발생: {e}")
            return None
    
    def _extract_metadata(self, article_data: Dict) -> Dict:
        """메타정보 추출"""
        metadata = {
            'extracted_entities': self._extract_entities(article_data),
            'content_length': len(article_data.get('body', '')),
            'word_count': len(article_data.get('body', '').split()),
            'has_images': len(article_data.get('images', [])) > 0,
            'has_stock_codes': len(article_data.get('stock_codes', [])) > 0,
            'category_info': self._analyze_categories(article_data.get('categories', [])),
            'time_info': self._analyze_time_info(article_data),
            'content_type': self._determine_content_type(article_data)
        }
        
        return metadata
    
    def _extract_entities(self, article_data: Dict) -> Dict:
        """엔티티 추출 (기본적인 패턴 매칭)"""
        text = f"{article_data.get('title', '')} {article_data.get('body', '')}"
        
        entities = {
            'persons': self._extract_persons(text),
            'companies': self._extract_companies(text),
            'locations': self._extract_locations(text),
            'dates': self._extract_dates(text),
            'numbers': self._extract_numbers(text)
        }
        
        return entities
    
    def _extract_persons(self, text: str) -> List[str]:
        """인물명 추출"""
        # 한국어 인명 패턴 (성 + 이름)
        korean_name_pattern = r'[가-힣]{2,4}(?=\s|,|\.|이다|라고|씨|님)'
        names = re.findall(korean_name_pattern, text)
        
        # 기자명 추출
        writer_pattern = r'([가-힣]{2,4})\s*기자'
        writers = re.findall(writer_pattern, text)
        
        return list(set(names + writers))
    
    def _extract_companies(self, text: str) -> List[str]:
        """기업명 추출"""
        # 주식회사, 유한회사 등 패턴
        company_patterns = [
            r'([가-힣\w\s]+(?:주식회사|유한회사|㈜|\(주\)|\(유\)))',
            r'([가-힣\w\s]+(?:그룹|그룹사|홀딩스|인베스트먼트))',
            r'([가-힣\w\s]+(?:은행|증권|보험|카드))'
        ]
        
        companies = []
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            companies.extend(matches)
        
        return list(set(companies))
    
    def _extract_locations(self, text: str) -> List[str]:
        """지역명 추출"""
        # 한국 지역명 패턴
        location_patterns = [
            r'([가-힣]+(?:시|도|구|군|동|읍|면))',
            r'([가-힣]+(?:서울|부산|대구|인천|광주|대전|울산|세종))',
            r'([가-힣]+(?:강남|강북|서초|송파|마포|용산|영등포))'
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            locations.extend(matches)
        
        return list(set(locations))
    
    def _extract_dates(self, text: str) -> List[str]:
        """날짜 추출"""
        date_patterns = [
            r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{4}\.\d{2}\.\d{2}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return list(set(dates))
    
    def _extract_numbers(self, text: str) -> List[str]:
        """숫자 추출"""
        number_patterns = [
            r'\d+조\s*\d+억\s*\d+만',
            r'\d+억\s*\d+만',
            r'\d+만\s*원',
            r'\d+%',
            r'\d+\.\d+%'
        ]
        
        numbers = []
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            numbers.extend(matches)
        
        return list(set(numbers))
    
    def _analyze_categories(self, categories: List[Dict]) -> Dict:
        """분류 정보 분석"""
        if not categories:
            return {}
        
        category = categories[0]  # 첫 번째 분류 사용
        
        return {
            'large_category': category.get('large_code_nm'),
            'middle_category': category.get('middle_code_nm'),
            'small_category': category.get('small_code_nm'),
            'category_code': category.get('code_id')
        }
    
    def _analyze_time_info(self, article_data: Dict) -> Dict:
        """시간 정보 분석"""
        service_time = article_data.get('service_daytime')
        reg_time = article_data.get('reg_dt')
        
        return {
            'service_time': service_time,
            'registration_time': reg_time,
            'is_recent': self._is_recent_article(service_time),
            'time_category': self._categorize_time(service_time)
        }
    
    def _determine_content_type(self, article_data: Dict) -> str:
        """콘텐츠 타입 결정"""
        title = article_data.get('title', '').lower()
        body = article_data.get('body', '').lower()
        
        if any(keyword in title for keyword in ['오피니언', '칼럼', '사설']):
            return 'opinion'
        elif any(keyword in title for keyword in ['기업', '회사', '경영']):
            return 'business'
        elif any(keyword in title for keyword in ['정치', '정부', '국회']):
            return 'politics'
        elif any(keyword in title for keyword in ['경제', '금융', '주식']):
            return 'economy'
        else:
            return 'general'
    
    def _is_recent_article(self, service_time: Optional[datetime]) -> bool:
        """최근 기사 여부 확인"""
        if not service_time:
            return False
        
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        return service_time > (now - timedelta(days=30))
    
    def _categorize_time(self, service_time: Optional[datetime]) -> str:
        """시간대 분류"""
        if not service_time:
            return 'unknown'
        
        hour = service_time.hour
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 24:
            return 'evening'
        else:
            return 'night'
    
    def _generate_content_hash(self, article_data: Dict) -> str:
        """콘텐츠 해시 생성 (중복 체크용)"""
        content = f"{article_data.get('title', '')}{article_data.get('body', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _get_text(self, element, tag: str) -> Optional[str]:
        """XML 요소에서 텍스트 추출"""
        if element is None:
            return None
        child = element.find(tag)
        return child.text if child is not None else None
    
    def _get_cdata_text(self, element, tag: str) -> Optional[str]:
        """CDATA 섹션에서 텍스트 추출"""
        if element is None:
            return None
        child = element.find(tag)
        if child is None:
            return None
        
        # CDATA 섹션 처리
        text = child.text or ''
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
    
    def _get_int(self, element, tag: str) -> Optional[int]:
        """XML 요소에서 정수 추출"""
        text = self._get_text(element, tag)
        try:
            return int(text) if text else None
        except ValueError:
            return None
    
    def _get_datetime(self, element, tag: str) -> Optional[datetime]:
        """XML 요소에서 날짜시간 추출"""
        text = self._get_text(element, tag)
        if not text:
            return None
        
        try:
            # 다양한 날짜 형식 처리
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%Y%m%d%H%M%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None
    
    def _extract_categories(self, wms_code_classes) -> List[Dict]:
        """분류 정보 추출"""
        if wms_code_classes is None:
            return []
        
        categories = []
        for code_class in wms_code_classes.findall('wms_code_class'):
            category = {
                'code_id': self._get_cdata_text(code_class, 'code_id'),
                'code_nm': self._get_cdata_text(code_class, 'code_nm'),
                'large_code_id': self._get_cdata_text(code_class, 'large_code_id'),
                'large_code_nm': self._get_cdata_text(code_class, 'large_code_nm'),
                'middle_code_id': self._get_cdata_text(code_class, 'middle_code_id'),
                'middle_code_nm': self._get_cdata_text(code_class, 'middle_code_nm'),
                'small_code_id': self._get_cdata_text(code_class, 'small_code_id'),
                'small_code_nm': self._get_cdata_text(code_class, 'small_code_nm')
            }
            categories.append(category)
        
        return categories
    
    def _extract_images(self, wms_article_images) -> List[Dict]:
        """이미지 정보 추출"""
        if wms_article_images is None:
            return []
        
        images = []
        for image in wms_article_images.findall('wms_article_image'):
            img_data = {
                'image_url': self._get_cdata_text(image, 'image_url'),
                'image_caption': self._get_cdata_text(image, 'image_caption')
            }
            images.append(img_data)
        
        return images
    
    def _extract_stock_codes(self, stock_codes) -> List[str]:
        """주식 코드 추출"""
        if stock_codes is None or not stock_codes.text:
            return []
        
        # 주식 코드는 보통 쉼표로 구분
        codes = [code.strip() for code in stock_codes.text.split(',') if code.strip()]
        return codes
    
    def _extract_keywords(self, wms_article_keywords) -> List[str]:
        """키워드 추출"""
        if wms_article_keywords is None or not wms_article_keywords.text:
            return []
        
        # 키워드는 보통 쉼표로 구분
        keywords = [keyword.strip() for keyword in wms_article_keywords.text.split(',') if keyword.strip()]
        return keywords


