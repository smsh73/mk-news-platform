"""
Gemini API 클라이언트
"""
import os
import logging
from typing import List, Dict, Optional, Any
import json
import re

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None
    HarmCategory = None
    HarmBlockThreshold = None

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini API 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.use_vertex_ai = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Gemini 클라이언트 초기화"""
        try:
            if not genai:
                logger.warning("google-generativeai 패키지가 설치되지 않았습니다.")
                return
            
            # API 키 확인 (환경변수 또는 직접 전달)
            if not self.api_key:
                self.api_key = os.getenv('GEMINI_API_KEY')
                if not self.api_key:
                    logger.warning("Gemini API 키가 설정되지 않았습니다.")
                    return
            
            # Gemini API 설정
            genai.configure(api_key=self.api_key)
            
            # 모델 초기화 (관리형 서비스에서는 안정적인 모델 사용)
            model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
            self.model = genai.GenerativeModel(model_name)
            
            logger.info(f"Gemini API 클라이언트 초기화 완료 (모델: {model_name})")
            
        except Exception as e:
            logger.error(f"Gemini 클라이언트 초기화 중 오류 발생: {e}")
            # 관리형 서비스에서는 API 키 없이도 계속 진행
            if os.getenv('USE_MANAGED_SERVICES', 'false').lower() == 'true':
                logger.warning("관리형 서비스 모드: Gemini API 초기화 실패하지만 계속 진행")
                self.model = None
    
    def generate_response(self, query: str, context: str, 
                         retrieved_docs: List[Dict]) -> Dict:
        """Gemini API로 응답 생성"""
        try:
            if not self.model:
                return self._fallback_response(query, context, retrieved_docs)
            
            # 프롬프트 구성
            prompt = self._build_prompt(query, context, retrieved_docs)
            
            # 안전 설정
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # 생성 설정
            generation_config = {
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
            
            # 응답 생성
            response = self.model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            # 응답 처리
            if response.text:
                return self._process_response(response.text, retrieved_docs)
            else:
                return self._fallback_response(query, context, retrieved_docs)
                
        except Exception as e:
            logger.error(f"Gemini API 응답 생성 중 오류 발생: {e}")
            return self._fallback_response(query, context, retrieved_docs)
    
    def _build_prompt(self, query: str, context: str, retrieved_docs: List[Dict]) -> str:
        """프롬프트 구성"""
        prompt = f"""
당신은 매일경제 신문의 AI 어시스턴트입니다. 제공된 기사 정보를 바탕으로 사용자의 질문에 정확하고 유용한 답변을 제공해주세요.

사용자 질문: {query}

관련 기사 정보:
{context}

답변 가이드라인:
1. 제공된 기사 정보를 바탕으로 정확한 답변을 제공하세요.
2. 답변에 출처가 되는 기사를 명시하세요.
3. 기사 정보가 부족한 경우, 그 한계를 명확히 설명하세요.
4. 객관적이고 중립적인 관점을 유지하세요.
5. 답변은 한국어로 작성하세요.
6. 답변은 500자 이내로 간결하게 작성하세요.

답변:
"""
        return prompt
    
    def _process_response(self, response_text: str, retrieved_docs: List[Dict]) -> Dict:
        """응답 처리"""
        try:
            # 응답 텍스트 정리
            cleaned_response = self._clean_response_text(response_text)
            
            # 참조 기사 정보 추출
            references = self._extract_references(cleaned_response, retrieved_docs)
            
            # 신뢰도 점수 계산
            confidence_score = self._calculate_confidence_score(cleaned_response, retrieved_docs)
            
            return {
                'text': cleaned_response,
                'references': references,
                'confidence_score': confidence_score,
                'source': 'gemini',
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"응답 처리 중 오류 발생: {e}")
            return {
                'text': response_text,
                'references': [],
                'confidence_score': 0.5,
                'source': 'gemini',
                'timestamp': self._get_current_timestamp()
            }
    
    def _clean_response_text(self, text: str) -> str:
        """응답 텍스트 정리"""
        try:
            # 불필요한 접두사 제거
            prefixes_to_remove = [
                "답변:",
                "답변",
                "AI 어시스턴트:",
                "매일경제 AI:",
                "매일경제 신문 AI 어시스턴트:"
            ]
            
            for prefix in prefixes_to_remove:
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()
            
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', text)
            
            # 연속된 공백 정리
            text = re.sub(r'\s+', ' ', text)
            
            # 앞뒤 공백 제거
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"응답 텍스트 정리 중 오류 발생: {e}")
            return text
    
    def _extract_references(self, response_text: str, retrieved_docs: List[Dict]) -> List[Dict]:
        """참조 기사 정보 추출"""
        try:
            references = []
            
            # 응답 텍스트에서 기사 제목이나 키워드 매칭
            for doc in retrieved_docs[:3]:  # 상위 3개만
                article = doc['article']
                title = article.get('title', '')
                
                # 제목이 응답에 언급되었는지 확인
                if title and any(word in response_text for word in title.split()[:3]):
                    references.append({
                        'title': title,
                        'url': article.get('article_url', ''),
                        'similarity': doc.get('similarity', 0)
                    })
            
            return references
            
        except Exception as e:
            logger.error(f"참조 기사 정보 추출 중 오류 발생: {e}")
            return []
    
    def _calculate_confidence_score(self, response_text: str, retrieved_docs: List[Dict]) -> float:
        """신뢰도 점수 계산"""
        try:
            score = 0.5  # 기본 점수
            
            # 검색된 문서 수에 따른 점수
            if len(retrieved_docs) >= 3:
                score += 0.2
            elif len(retrieved_docs) >= 1:
                score += 0.1
            
            # 응답 길이에 따른 점수
            if len(response_text) > 100:
                score += 0.1
            
            # 참조 정보가 있는 경우 점수
            if any(doc.get('article', {}).get('article_url') for doc in retrieved_docs):
                score += 0.1
            
            # 최대 1.0으로 제한
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"신뢰도 점수 계산 중 오류 발생: {e}")
            return 0.5
    
    def _fallback_response(self, query: str, context: str, retrieved_docs: List[Dict]) -> Dict:
        """대체 응답 생성 (Gemini API 사용 불가 시)"""
        try:
            if not retrieved_docs:
                return {
                    'text': '죄송합니다. 관련 기사를 찾을 수 없습니다.',
                    'references': [],
                    'confidence_score': 0.0,
                    'source': 'fallback',
                    'timestamp': self._get_current_timestamp()
                }
            
            # 간단한 템플릿 기반 응답
            response_parts = []
            
            # 질문에 대한 간단한 답변
            response_parts.append(f"'{query}'에 대한 관련 기사 정보를 찾았습니다.")
            
            # 관련 기사 요약
            for i, doc in enumerate(retrieved_docs[:3], 1):
                article = doc['article']
                response_parts.append(f"{i}. {article.get('title', '')}")
                if article.get('summary'):
                    summary = article['summary'][:100] + '...' if len(article['summary']) > 100 else article['summary']
                    response_parts.append(f"   {summary}")
            
            return {
                'text': '\n'.join(response_parts),
                'references': [
                    {
                        'title': doc['article'].get('title', ''),
                        'url': doc['article'].get('article_url', ''),
                        'similarity': doc.get('similarity', 0)
                    }
                    for doc in retrieved_docs[:3]
                ],
                'confidence_score': 0.6,
                'source': 'fallback',
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"대체 응답 생성 중 오류 발생: {e}")
            return {
                'text': '죄송합니다. 응답을 생성할 수 없습니다.',
                'references': [],
                'confidence_score': 0.0,
                'source': 'error',
                'timestamp': self._get_current_timestamp()
            }
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def test_connection(self) -> Dict:
        """Gemini API 연결 테스트"""
        try:
            if not self.model:
                return {
                    'status': 'error',
                    'message': 'Gemini 모델이 초기화되지 않았습니다.'
                }
            
            # 간단한 테스트 쿼리
            test_response = self.model.generate_content("안녕하세요")
            
            if test_response.text:
                return {
                    'status': 'success',
                    'message': 'Gemini API 연결이 정상입니다.',
                    'test_response': test_response.text[:100]
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Gemini API 응답을 받을 수 없습니다.'
                }
                
        except Exception as e:
            logger.error(f"Gemini API 연결 테스트 중 오류 발생: {e}")
            return {
                'status': 'error',
                'message': f'Gemini API 연결 테스트 실패: {str(e)}'
            }
    
    def get_model_info(self) -> Dict:
        """모델 정보 조회"""
        try:
            if not self.model:
                return {
                    'model_name': 'Not initialized',
                    'api_key_configured': bool(self.api_key),
                    'status': 'not_initialized'
                }
            
            return {
                'model_name': 'gemini-1.5-pro',
                'api_key_configured': bool(self.api_key),
                'status': 'initialized'
            }
            
        except Exception as e:
            logger.error(f"모델 정보 조회 중 오류 발생: {e}")
            return {
                'model_name': 'Unknown',
                'api_key_configured': False,
                'status': 'error'
            }


