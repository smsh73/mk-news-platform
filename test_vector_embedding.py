"""
Vertex AI Vector Embedding 테스트 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.embedding.embedding_service import EmbeddingService
from src.embedding.article_metadata_extractor import ArticleMetadataExtractor
import logging

logging.basicConfig(level=logging.INFO)

def test_metadata_extraction():
    """메타데이터 추출 테스트"""
    print("\n=== 메타데이터 추출 테스트 ===")
    
    extractor = ArticleMetadataExtractor()
    
    article_data = {
        'title': '삼성전자 주가 급등, 반도체 수요 회복 기대',
        'body': '삼성전자(005930) 주가가 급등했다. 반도체 수요 회복 기대감이 높아지고 있다. 주요 증권사는 삼성전자 목표주가를 상향 조정했다.',
        'summary': '삼성전자 주가 급등, 반도체 수요 회복 기대',
        'service_daytime': '2024-03-15T10:30:00Z',
        'categories': [
            {'code_nm': '증권'},
            {'code_nm': 'IT'}
        ],
        'keywords': [
            {'keyword': '삼성전자'},
            {'keyword': '반도체'}
        ],
        'stock_codes': [
            {'stock_code': '005930'}
        ]
    }
    
    metadata = extractor.extract_metadata(article_data)
    
    print(f"제목 길이: {metadata.get('title_length')}")
    print(f"본문 길이: {metadata.get('body_length')}")
    print(f"단어 수: {metadata.get('word_count')}")
    print(f"\n엔티티:")
    for entity_type, entities in metadata.get('entities', {}).items():
        if entities:
            print(f"  {entity_type}: {entities}")
    print(f"\n카테고리: {metadata.get('categories')}")
    print(f"키워드: {metadata.get('keywords')}")
    print(f"주식 코드: {metadata.get('stock_codes')}")
    print(f"기사 타입: {metadata.get('article_type')}")
    print(f"중요도 점수: {metadata.get('importance_score')}")
    print(f"\n인덱싱용 텍스트 (일부):")
    indexing_text = metadata.get('indexing_text', '')
    print(f"  {indexing_text[:100]}...")
    
    return True

def test_embedding_generation():
    """임베딩 생성 테스트"""
    print("\n=== 임베딩 생성 테스트 ===")
    
    try:
        embedding_service = EmbeddingService()
        
        # 테스트 텍스트
        test_texts = [
            "삼성전자 주가 급등",
            "반도체 수요 회복 기대",
            "AI 기술 발전"
        ]
        
        print(f"Vertex AI 임베딩 생성 시도...")
        embeddings = embedding_service.generate_embeddings(test_texts, model_type="vertex_ai")
        
        print(f"✅ 임베딩 생성 성공!")
        print(f"  생성된 임베딩 수: {len(embeddings)}")
        print(f"  임베딩 차원: {len(embeddings[0])}")
        print(f"  첫 번째 임베딩 일부: {embeddings[0][:5]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Vertex AI 임베딩 실패: {e}")
        print(f"  Fallback 모델 사용 시도...")
        
        # Fallback 테스트
        try:
            embeddings = embedding_service.generate_embeddings(test_texts, model_type="multilingual")
            print(f"✅ Fallback 임베딩 생성 성공!")
            print(f"  생성된 임베딩 수: {len(embeddings)}")
            print(f"  임베딩 차원: {len(embeddings[0])}")
            return True
        except Exception as e2:
            print(f"❌ Fallback 임베딩도 실패: {e2}")
            return False

def test_article_embedding():
    """기사 임베딩 생성 테스트"""
    print("\n=== 기사 임베딩 생성 테스트 ===")
    
    try:
        embedding_service = EmbeddingService()
        
        article_data = {
            'title': '삼성전자 주가 급등, 반도체 수요 회복 기대',
            'body': '삼성전자(005930) 주가가 급등했다. 반도체 수요 회복 기대감이 높아지고 있다. 주요 증권사는 삼성전자 목표주가를 상향 조정했다.',
            'summary': '삼성전자 주가 급등, 반도체 수요 회복 기대',
            'categories': [
                {'code_nm': '증권'},
                {'code_nm': 'IT'}
            ],
            'keywords': [
                {'keyword': '삼성전자'},
                {'keyword': '반도체'}
            ],
            'stock_codes': [
                {'stock_code': '005930'}
            ]
        }
        
        result = embedding_service.generate_article_embedding(article_data)
        
        print(f"✅ 기사 임베딩 생성 성공!")
        print(f"  임베딩 차원: {len(result['embedding'])}")
        print(f"  메타데이터: {result['metadata']}")
        print(f"  텍스트 해시: {result['text_hash']}")
        print(f"  메타데이터 해시: {result.get('metadata_hash', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 기사 임베딩 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트"""
    print("=" * 60)
    print("Vertex AI Vector Embedding 테스트 시작")
    print("=" * 60)
    
    results = []
    
    # 1. 메타데이터 추출 테스트
    results.append(("메타데이터 추출", test_metadata_extraction()))
    
    # 2. 기본 임베딩 생성 테스트
    results.append(("기본 임베딩 생성", test_embedding_generation()))
    
    # 3. 기사 임베딩 생성 테스트
    results.append(("기사 임베딩 생성", test_article_embedding()))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n전체: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n⚠️ 일부 테스트 실패 (Vertex AI 인증 또는 의존성 확인 필요)")

if __name__ == "__main__":
    main()

