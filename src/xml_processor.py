"""
XML 파일 처리 및 데이터베이스 저장 시스템
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from .xml_parser import XMLParser
from .database.connection import get_db, init_database
from .database.models import (
    Article, ArticleCategory, ArticleImage, ArticleKeyword, 
    ArticleStockCode, ProcessingLog
)

logger = logging.getLogger(__name__)

class XMLProcessor:
    """XML 파일 처리기"""
    
    def __init__(self, max_workers: int = 4):
        self.xml_parser = XMLParser()
        self.max_workers = max_workers
        self.processed_count = 0
        self.error_count = 0
        self.duplicate_count = 0
    
    def process_xml_files(self, xml_directory: str, batch_size: int = 100) -> Dict:
        """XML 파일들을 배치로 처리"""
        xml_files = self._get_xml_files(xml_directory)
        total_files = len(xml_files)
        
        logger.info(f"총 {total_files}개의 XML 파일을 처리합니다.")
        
        results = {
            'total_files': total_files,
            'processed': 0,
            'errors': 0,
            'duplicates': 0,
            'start_time': datetime.utcnow(),
            'end_time': None
        }
        
        # 배치별로 처리
        for i in range(0, total_files, batch_size):
            batch_files = xml_files[i:i + batch_size]
            batch_results = self._process_batch(batch_files)
            
            # 결과 누적
            results['processed'] += batch_results['processed']
            results['errors'] += batch_results['errors']
            results['duplicates'] += batch_results['duplicates']
            
            logger.info(f"배치 {i//batch_size + 1} 완료: {batch_results}")
        
        results['end_time'] = datetime.utcnow()
        results['processing_time'] = (results['end_time'] - results['start_time']).total_seconds()
        
        logger.info(f"XML 처리 완료: {results}")
        return results
    
    def _get_xml_files(self, xml_directory: str) -> List[str]:
        """XML 파일 목록 가져오기"""
        xml_path = Path(xml_directory)
        if not xml_path.exists():
            raise FileNotFoundError(f"XML 디렉토리를 찾을 수 없습니다: {xml_directory}")
        
        xml_files = list(xml_path.glob("*.xml"))
        return [str(f) for f in xml_files]
    
    def _process_batch(self, xml_files: List[str]) -> Dict:
        """배치 파일 처리"""
        batch_results = {
            'processed': 0,
            'errors': 0,
            'duplicates': 0
        }
        
        # 멀티스레딩으로 병렬 처리
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_xml, xml_file): xml_file 
                for xml_file in xml_files
            }
            
            for future in as_completed(future_to_file):
                xml_file = future_to_file[future]
                try:
                    result = future.result()
                    if result['status'] == 'success':
                        batch_results['processed'] += 1
                    elif result['status'] == 'duplicate':
                        batch_results['duplicates'] += 1
                    else:
                        batch_results['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"파일 처리 중 오류 발생: {xml_file}, {e}")
                    batch_results['errors'] += 1
        
        return batch_results
    
    def _process_single_xml(self, xml_file: str) -> Dict:
        """단일 XML 파일 처리"""
        start_time = datetime.utcnow()
        
        try:
            # XML 파싱
            parsed_data = self.xml_parser.parse_xml_file(xml_file)
            if not parsed_data:
                return {
                    'status': 'error',
                    'message': 'XML 파싱 실패',
                    'processing_time': 0
                }
            
            # 데이터베이스에 저장
            result = self._save_to_database(parsed_data)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # 처리 로그 저장
            self._log_processing(
                parsed_data['article_data'].get('art_id'),
                'xml_parse',
                result['status'],
                result.get('message', ''),
                processing_time
            )
            
            return {
                'status': result['status'],
                'message': result.get('message', ''),
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"XML 파일 처리 중 오류 발생: {xml_file}, {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': 0
            }
    
    def _save_to_database(self, parsed_data: Dict) -> Dict:
        """파싱된 데이터를 데이터베이스에 저장"""
        db = next(get_db())
        
        try:
            article_data = parsed_data['article_data']
            metadata = parsed_data['metadata']
            content_hash = parsed_data['content_hash']
            
            # 중복 체크
            existing_article = db.query(Article).filter(
                Article.content_hash == content_hash
            ).first()
            
            if existing_article:
                return {
                    'status': 'duplicate',
                    'message': '이미 존재하는 기사입니다.'
                }
            
            # 기사 정보 저장
            article = Article(
                art_id=article_data['art_id'],
                art_year=article_data['art_year'],
                art_no=article_data['art_no'],
                title=article_data['title'],
                sub_title=article_data['sub_title'],
                writers=article_data['writers'],
                service_daytime=article_data['service_daytime'],
                reg_dt=article_data['reg_dt'],
                mod_dt=article_data['mod_dt'],
                article_url=article_data['article_url'],
                media_code=article_data['media_code'],
                gubun=article_data['gubun'],
                free_type=article_data['free_type'],
                pub_div=article_data['pub_div'],
                art_org_class=article_data['art_org_class'],
                body=article_data['body'],
                summary=article_data['summary'],
                content_hash=content_hash,
                is_processed=True
            )
            
            db.add(article)
            db.flush()  # ID 생성
            
            # 분류 정보 저장
            for category_data in article_data.get('categories', []):
                category = ArticleCategory(
                    article_id=article.id,
                    code_id=category_data.get('code_id'),
                    code_nm=category_data.get('code_nm'),
                    large_code_id=category_data.get('large_code_id'),
                    large_code_nm=category_data.get('large_code_nm'),
                    middle_code_id=category_data.get('middle_code_id'),
                    middle_code_nm=category_data.get('middle_code_nm'),
                    small_code_id=category_data.get('small_code_id'),
                    small_code_nm=category_data.get('small_code_nm')
                )
                db.add(category)
            
            # 이미지 정보 저장
            for image_data in article_data.get('images', []):
                image = ArticleImage(
                    article_id=article.id,
                    image_url=image_data.get('image_url'),
                    image_caption=image_data.get('image_caption')
                )
                db.add(image)
            
            # 키워드 저장
            for keyword in article_data.get('keywords', []):
                keyword_obj = ArticleKeyword(
                    article_id=article.id,
                    keyword=keyword,
                    keyword_type='general'
                )
                db.add(keyword_obj)
            
            # 추출된 엔티티를 키워드로 저장
            entities = metadata.get('extracted_entities', {})
            for entity_type, entities_list in entities.items():
                for entity in entities_list:
                    keyword_obj = ArticleKeyword(
                        article_id=article.id,
                        keyword=entity,
                        keyword_type=entity_type
                    )
                    db.add(keyword_obj)
            
            # 주식 코드 저장
            for stock_code in article_data.get('stock_codes', []):
                stock_obj = ArticleStockCode(
                    article_id=article.id,
                    stock_code=stock_code
                )
                db.add(stock_obj)
            
            db.commit()
            
            return {
                'status': 'success',
                'message': '기사가 성공적으로 저장되었습니다.',
                'article_id': article.id
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"데이터베이스 저장 중 오류 발생: {e}")
            return {
                'status': 'error',
                'message': f'데이터베이스 저장 실패: {str(e)}'
            }
        finally:
            db.close()
    
    def _log_processing(self, art_id: str, process_type: str, status: str, 
                       message: str, processing_time: float):
        """처리 로그 저장"""
        db = next(get_db())
        try:
            log = ProcessingLog(
                article_id=art_id or 'unknown',
                process_type=process_type,
                status=status,
                message=message,
                processing_time=processing_time
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"처리 로그 저장 중 오류 발생: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_processing_stats(self) -> Dict:
        """처리 통계 조회"""
        db = next(get_db())
        try:
            stats = {
                'total_articles': db.query(Article).count(),
                'processed_articles': db.query(Article).filter(Article.is_processed == True).count(),
                'embedded_articles': db.query(Article).filter(Article.is_embedded == True).count(),
                'error_articles': db.query(Article).filter(Article.processing_error.isnot(None)).count(),
                'recent_articles': db.query(Article).filter(
                    Article.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count()
            }
            return stats
        finally:
            db.close()
    
    def get_articles_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """날짜 범위별 기사 조회"""
        db = next(get_db())
        try:
            articles = db.query(Article).filter(
                Article.service_daytime >= start_date,
                Article.service_daytime <= end_date
            ).all()
            
            return [
                {
                    'id': article.id,
                    'art_id': article.art_id,
                    'title': article.title,
                    'service_daytime': article.service_daytime,
                    'is_processed': article.is_processed,
                    'is_embedded': article.is_embedded
                }
                for article in articles
            ]
        finally:
            db.close()
    
    def get_unprocessed_articles(self, limit: int = 100) -> List[Dict]:
        """미처리 기사 조회"""
        db = next(get_db())
        try:
            articles = db.query(Article).filter(
                Article.is_processed == False
            ).limit(limit).all()
            
            return [
                {
                    'id': article.id,
                    'art_id': article.art_id,
                    'title': article.title,
                    'service_daytime': article.service_daytime
                }
                for article in articles
            ]
        finally:
            db.close()


