"""
Vertex AI Vector Search 클라이언트
"""
import os
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
from google.cloud.aiplatform.matching_engine import MatchingEngineIndex
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint

logger = logging.getLogger(__name__)

class VertexAIVectorSearchClient:
    """Vertex AI Vector Search 클라이언트"""
    
    def __init__(self, project_id: str = "mk-ai-project-473000", region: str = "asia-northeast3"):
        self.project_id = project_id
        self.region = region
        self.client = None
        self.index_endpoint = None
        self._initialize_client()
    
    def _initialize_client(self):
        """클라이언트 초기화"""
        try:
            # 환경 변수에서 인증 정보 확인
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path and os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            # Vertex AI 초기화
            aiplatform.init(
                project=self.project_id, 
                location=self.region,
                staging_bucket=f"gs://{self.project_id}-vertex-ai-staging"
            )
            
            # Vector Search 클라이언트 초기화
            self.client = aip.PredictionServiceClient()
            
            logger.info(f"Vertex AI Vector Search 클라이언트 초기화 완료: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Vertex AI 클라이언트 초기화 중 오류 발생: {e}")
            # 관리형 서비스에서는 인증 실패 시에도 계속 진행
            if os.getenv('USE_MANAGED_SERVICES', 'false').lower() == 'true':
                logger.warning("관리형 서비스 모드: Vertex AI 클라이언트 초기화 실패하지만 계속 진행")
                self.client = None
            else:
                raise
    
    def create_index(self, index_name: str, dimensions: int = 768, 
                    description: str = "매일경제 신문기사 벡터 인덱스") -> str:
        """벡터 인덱스 생성"""
        try:
            # 인덱스 설정
            index_config = {
                "display_name": index_name,
                "description": description,
                "metadata": {
                    "contents_delta_uri": f"gs://mk-news-storage-{self.project_id}/embeddings",
                    "config": {
                        "dimensions": dimensions,
                        "approximate_neighbors_count": 150,
                        "distance_measure_type": "DOT_PRODUCT_DISTANCE",
                        "algorithm_config": {
                            "tree_ah_config": {
                                "leaf_node_embedding_count": 500,
                                "leaf_nodes_to_search_percent": 7
                            }
                        }
                    }
                },
                "index_update_method": "BATCH_UPDATE"
            }
            
            # 인덱스 생성 요청
            parent = f"projects/{self.project_id}/locations/{self.region}"
            
            operation = self.client.create_index(
                parent=parent,
                index=index_config
            )
            
            # 작업 완료 대기
            result = operation.result()
            index_id = result.name.split('/')[-1]
            
            logger.info(f"벡터 인덱스 생성 완료: {index_id}")
            return index_id
            
        except Exception as e:
            logger.error(f"벡터 인덱스 생성 중 오류 발생: {e}")
            raise
    
    def create_index_endpoint(self, endpoint_name: str, 
                             description: str = "매일경제 신문기사 벡터 검색 엔드포인트") -> str:
        """인덱스 엔드포인트 생성"""
        try:
            # 엔드포인트 설정
            endpoint_config = {
                "display_name": endpoint_name,
                "description": description,
                "network": f"projects/{self.project_id}/global/networks/mk-news-vpc"
            }
            
            # 엔드포인트 생성 요청
            parent = f"projects/{self.project_id}/locations/{self.region}"
            
            operation = self.client.create_index_endpoint(
                parent=parent,
                index_endpoint=endpoint_config
            )
            
            # 작업 완료 대기
            result = operation.result()
            endpoint_id = result.name.split('/')[-1]
            
            logger.info(f"인덱스 엔드포인트 생성 완료: {endpoint_id}")
            return endpoint_id
            
        except Exception as e:
            logger.error(f"인덱스 엔드포인트 생성 중 오류 발생: {e}")
            raise
    
    def deploy_index(self, endpoint_id: str, index_id: str, 
                    deployed_index_id: str = "mk_news_deployed_index") -> str:
        """인덱스를 엔드포인트에 배포"""
        try:
            # 배포 설정
            deployed_index_config = {
                "id": deployed_index_id,
                "index": f"projects/{self.project_id}/locations/{self.region}/indexes/{index_id}",
                "display_name": "매일경제 신문기사 벡터 검색",
                "description": "매일경제 신문기사 벡터 검색 배포",
                "enable_restricted_image_search": False,
                "dedicated_resources": {
                    "machine_spec": {
                        "machine_type": "e2-standard-2"
                    },
                    "min_replica_count": 1,
                    "max_replica_count": 3
                }
            }
            
            # 배포 요청
            endpoint_name = f"projects/{self.project_id}/locations/{self.region}/indexEndpoints/{endpoint_id}"
            
            operation = self.client.deploy_index(
                index_endpoint=endpoint_name,
                deployed_index=deployed_index_config
            )
            
            # 작업 완료 대기
            result = operation.result()
            deployed_index_name = result.name.split('/')[-1]
            
            logger.info(f"인덱스 배포 완료: {deployed_index_name}")
            return deployed_index_name
            
        except Exception as e:
            logger.error(f"인덱스 배포 중 오류 발생: {e}")
            raise
    
    def upsert_vectors(self, index_id: str, vectors: List[Dict]) -> bool:
        """벡터 데이터 업서트"""
        try:
            # 벡터 데이터 준비
            vector_data = []
            for vector_info in vectors:
                vector_data.append({
                    "id": vector_info['id'],
                    "embedding": vector_info['embedding']
                })
            
            # 업서트 요청
            index_name = f"projects/{self.project_id}/locations/{self.region}/indexes/{index_id}"
            
            # 실제 구현에서는 Vertex AI의 업서트 API 사용
            # 여기서는 로컬 저장으로 대체
            self._save_vectors_locally(vector_data)
            
            logger.info(f"벡터 데이터 업서트 완료: {len(vector_data)}개")
            return True
            
        except Exception as e:
            logger.error(f"벡터 데이터 업서트 중 오류 발생: {e}")
            return False
    
    def _save_vectors_locally(self, vector_data: List[Dict]):
        """벡터 데이터 로컬 저장 (개발용)"""
        try:
            os.makedirs("data/vectors", exist_ok=True)
            
            with open("data/vectors/vector_data.json", "w", encoding="utf-8") as f:
                json.dump(vector_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"벡터 데이터 로컬 저장 중 오류 발생: {e}")
    
    def search_vectors(self, endpoint_id: str, query_embedding: List[float], 
                      top_k: int = 10, filter_expression: Optional[str] = None) -> List[Dict]:
        """벡터 검색"""
        try:
            # 검색 요청 구성
            search_request = {
                "deployed_index_id": "mk_news_deployed_index",
                "queries": [{
                    "embedding": query_embedding,
                    "top_k": top_k
                }]
            }
            
            if filter_expression:
                search_request["filter"] = filter_expression
            
            # 검색 실행
            endpoint_name = f"projects/{self.project_id}/locations/{self.region}/indexEndpoints/{endpoint_id}"
            
            # 실제 구현에서는 Vertex AI의 검색 API 사용
            # 여기서는 로컬 검색으로 대체
            results = self._search_vectors_locally(query_embedding, top_k)
            
            logger.info(f"벡터 검색 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"벡터 검색 중 오류 발생: {e}")
            return []
    
    def _search_vectors_locally(self, query_embedding: List[float], top_k: int) -> List[Dict]:
        """로컬 벡터 검색 (개발용)"""
        try:
            # 로컬 벡터 데이터 로드
            if not os.path.exists("data/vectors/vector_data.json"):
                return []
            
            with open("data/vectors/vector_data.json", "r", encoding="utf-8") as f:
                vector_data = json.load(f)
            
            # 유사도 계산
            similarities = []
            for vector_info in vector_data:
                similarity = self._calculate_cosine_similarity(
                    query_embedding, 
                    vector_info['embedding']
                )
                similarities.append({
                    'id': vector_info['id'],
                    'similarity': similarity
                })
            
            # 유사도 순으로 정렬
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"로컬 벡터 검색 중 오류 발생: {e}")
            return []
    
    def _calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """코사인 유사도 계산"""
        try:
            import numpy as np
            
            embedding1 = np.array(embedding1)
            embedding2 = np.array(embedding2)
            
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"유사도 계산 중 오류 발생: {e}")
            return 0.0
    
    def get_index_status(self, index_id: str) -> Dict:
        """인덱스 상태 조회"""
        try:
            index_name = f"projects/{self.project_id}/locations/{self.region}/indexes/{index_id}"
            
            # 인덱스 정보 조회
            index_info = self.client.get_index(name=index_name)
            
            return {
                'name': index_info.name,
                'display_name': index_info.display_name,
                'state': index_info.state.name,
                'create_time': index_info.create_time,
                'update_time': index_info.update_time
            }
            
        except Exception as e:
            logger.error(f"인덱스 상태 조회 중 오류 발생: {e}")
            return {}
    
    def get_endpoint_status(self, endpoint_id: str) -> Dict:
        """엔드포인트 상태 조회"""
        try:
            endpoint_name = f"projects/{self.project_id}/locations/{self.region}/indexEndpoints/{endpoint_id}"
            
            # 엔드포인트 정보 조회
            endpoint_info = self.client.get_index_endpoint(name=endpoint_name)
            
            return {
                'name': endpoint_info.name,
                'display_name': endpoint_info.display_name,
                'state': endpoint_info.state.name,
                'create_time': endpoint_info.create_time,
                'update_time': endpoint_info.update_time
            }
            
        except Exception as e:
            logger.error(f"엔드포인트 상태 조회 중 오류 발생: {e}")
            return {}
    
    def delete_index(self, index_id: str) -> bool:
        """인덱스 삭제"""
        try:
            index_name = f"projects/{self.project_id}/locations/{self.region}/indexes/{index_id}"
            
            operation = self.client.delete_index(name=index_name)
            operation.result()
            
            logger.info(f"인덱스 삭제 완료: {index_id}")
            return True
            
        except Exception as e:
            logger.error(f"인덱스 삭제 중 오류 발생: {e}")
            return False
    
    def delete_endpoint(self, endpoint_id: str) -> bool:
        """엔드포인트 삭제"""
        try:
            endpoint_name = f"projects/{self.project_id}/locations/{self.region}/indexEndpoints/{endpoint_id}"
            
            operation = self.client.delete_index_endpoint(name=endpoint_name)
            operation.result()
            
            logger.info(f"엔드포인트 삭제 완료: {endpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"엔드포인트 삭제 중 오류 발생: {e}")
            return False
