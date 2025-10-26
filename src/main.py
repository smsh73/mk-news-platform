"""
매일경제 신문기사 벡터임베딩 플랫폼 메인 실행 파일
"""
import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.connection import init_database
from xml_processor import XMLProcessor
from vector_search.vector_indexer import VectorIndexer
from rag.hybrid_rag_system import HybridRAGSystem
from incremental.incremental_processor import IncrementalProcessor
from embedding.embedding_service import EmbeddingService

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mk_news_platform.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MKNewsPlatform:
    """매일경제 신문기사 벡터임베딩 플랫폼"""
    
    def __init__(self, project_id: str = "mk-ai-project-473000", region: str = "asia-northeast3"):
        self.project_id = project_id
        self.region = region
        
        # 서비스 초기화
        self.xml_processor = XMLProcessor()
        self.vector_indexer = VectorIndexer(project_id, region)
        self.rag_system = HybridRAGSystem(project_id, region)
        self.incremental_processor = IncrementalProcessor(project_id, region)
        self.embedding_service = EmbeddingService()
        
        logger.info("매일경제 신문기사 벡터임베딩 플랫폼 초기화 완료")
    
    def initialize_system(self):
        """시스템 초기화"""
        try:
            logger.info("시스템 초기화 시작...")
            
            # 데이터베이스 초기화
            init_database()
            logger.info("데이터베이스 초기화 완료")
            
            # 벡터 인덱스 생성
            self.create_vector_index()
            
            logger.info("시스템 초기화 완료")
            
        except Exception as e:
            logger.error(f"시스템 초기화 실패: {e}")
            raise
    
    def create_vector_index(self):
        """벡터 인덱스 생성"""
        try:
            logger.info("벡터 인덱스 생성 시작...")
            
            # 인덱스 생성
            result = self.vector_indexer.create_vector_index()
            if result['status'] == 'success':
                logger.info(f"벡터 인덱스 생성 완료: {result['index_id']}")
                
                # 엔드포인트 생성
                endpoint_result = self.vector_indexer.create_index_endpoint()
                if endpoint_result['status'] == 'success':
                    logger.info(f"인덱스 엔드포인트 생성 완료: {endpoint_result['endpoint_id']}")
                    
                    # 인덱스 배포
                    deploy_result = self.vector_indexer.deploy_index()
                    if deploy_result['status'] == 'success':
                        logger.info(f"인덱스 배포 완료: {deploy_result['deployed_index_id']}")
                    else:
                        logger.error(f"인덱스 배포 실패: {deploy_result['message']}")
                else:
                    logger.error(f"엔드포인트 생성 실패: {endpoint_result['message']}")
            else:
                logger.error(f"벡터 인덱스 생성 실패: {result['message']}")
                
        except Exception as e:
            logger.error(f"벡터 인덱스 생성 중 오류 발생: {e}")
    
    def process_xml_files(self, xml_directory: str, batch_size: int = 100):
        """XML 파일 처리"""
        try:
            logger.info(f"XML 파일 처리 시작: {xml_directory}")
            
            result = self.xml_processor.process_xml_files(xml_directory, batch_size)
            
            logger.info(f"XML 파일 처리 완료: {result}")
            
            # 처리된 기사들에 대한 임베딩 생성
            self.generate_embeddings_for_processed_articles()
            
            return result
            
        except Exception as e:
            logger.error(f"XML 파일 처리 중 오류 발생: {e}")
            raise
    
    def generate_embeddings_for_processed_articles(self):
        """처리된 기사들에 대한 임베딩 생성"""
        try:
            logger.info("임베딩 생성 시작...")
            
            # 미처리 기사 조회
            unprocessed_articles = self.xml_processor.get_unprocessed_articles(limit=1000)
            
            if unprocessed_articles:
                # 임베딩 생성
                embedding_results = self.embedding_service.batch_generate_embeddings(unprocessed_articles)
                
                # 벡터 인덱스 업데이트
                vector_data = []
                for embedding_info in embedding_results:
                    vector_data.append({
                        'id': embedding_info['article_id'],
                        'embedding': embedding_info['embedding']
                    })
                
                # Vertex AI 인덱스 업데이트
                success = self.vector_indexer.vertex_ai_client.upsert_vectors(
                    self.vector_indexer.index_id, vector_data
                )
                
                if success:
                    logger.info(f"임베딩 생성 및 인덱스 업데이트 완료: {len(embedding_results)}개")
                else:
                    logger.error("벡터 인덱스 업데이트 실패")
            else:
                logger.info("임베딩할 새로운 기사가 없습니다.")
                
        except Exception as e:
            logger.error(f"임베딩 생성 중 오류 발생: {e}")
    
    def incremental_process(self, xml_directory: str):
        """증분형 처리"""
        try:
            logger.info(f"증분형 처리 시작: {xml_directory}")
            
            # 마지막 처리 시간 조회
            last_processed_time = self.incremental_processor.get_last_processed_time()
            
            result = self.incremental_processor.process_incremental_articles(
                xml_directory, last_processed_time
            )
            
            logger.info(f"증분형 처리 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"증분형 처리 중 오류 발생: {e}")
            raise
    
    def test_rag_system(self, query: str):
        """RAG 시스템 테스트"""
        try:
            logger.info(f"RAG 시스템 테스트: {query}")
            
            result = self.rag_system.process_query(query)
            
            logger.info(f"RAG 시스템 테스트 완료")
            return result
            
        except Exception as e:
            logger.error(f"RAG 시스템 테스트 중 오류 발생: {e}")
            raise
    
    def get_system_status(self):
        """시스템 상태 조회"""
        try:
            status = {
                'timestamp': datetime.utcnow().isoformat(),
                'system_stats': self.rag_system.get_system_stats(),
                'vector_index_status': self.vector_indexer.get_index_status(),
                'processing_stats': self.incremental_processor.get_processing_status()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"시스템 상태 조회 중 오류 발생: {e}")
            return {}

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="매일경제 신문기사 벡터임베딩 플랫폼")
    parser.add_argument("--project-id", default="mk-ai-project-473000", help="MK AI Project")
    parser.add_argument("--region", default="asia-northeast3", help="GCP 리전")
    parser.add_argument("--xml-directory", help="XML 파일 디렉토리")
    parser.add_argument("--batch-size", type=int, default=100, help="배치 크기")
    parser.add_argument("--mode", choices=["init", "process", "incremental", "test", "status"], 
                       default="status", help="실행 모드")
    parser.add_argument("--query", help="테스트 쿼리")
    
    args = parser.parse_args()
    
    try:
        # 플랫폼 초기화
        platform = MKNewsPlatform(args.project_id, args.region)
        
        if args.mode == "init":
            # 시스템 초기화
            platform.initialize_system()
            
        elif args.mode == "process":
            # XML 파일 처리
            if not args.xml_directory:
                logger.error("XML 디렉토리를 지정해주세요.")
                return
            
            platform.process_xml_files(args.xml_directory, args.batch_size)
            
        elif args.mode == "incremental":
            # 증분형 처리
            if not args.xml_directory:
                logger.error("XML 디렉토리를 지정해주세요.")
                return
            
            platform.incremental_process(args.xml_directory)
            
        elif args.mode == "test":
            # RAG 시스템 테스트
            if not args.query:
                logger.error("테스트 쿼리를 지정해주세요.")
                return
            
            result = platform.test_rag_system(args.query)
            print(f"테스트 결과: {result}")
            
        elif args.mode == "status":
            # 시스템 상태 조회
            status = platform.get_system_status()
            print(f"시스템 상태: {status}")
            
    except Exception as e:
        logger.error(f"메인 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
