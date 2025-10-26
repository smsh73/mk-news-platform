# 매일경제 신문기사 벡터임베딩 플랫폼 - 프로젝트 요약

## 📋 프로젝트 정보

- **프로젝트 명**: MK AI Project
- **GCP 프로젝트 ID**: godwind2015
- **계정 이메일**: godwind2015@gmail.com
- **리전**: asia-northeast3 (서울)
- **목적**: 60년치 매일경제 신문기사 데이터의 벡터 임베딩 및 Hybrid RAG 시스템 구축

## 🎯 프로젝트 목표

1. **기사 데이터 처리**: 60년치 XML 기사 파일을 구조화된 데이터로 변환
2. **벡터 임베딩**: VertexAI 기반 의미적 검색을 위한 벡터 임베딩 생성
3. **Hybrid RAG 시스템**: 벡터 검색과 키워드 검색을 결합한 하이브리드 검색
4. **증분형 처리**: 새로운 기사 파일 자동 감지 및 처리
5. **중복 필터링**: 자동 중복 기사 감지 및 제거
6. **실시간 모니터링**: 시스템 상태 및 통계 실시간 추적

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     사용자 인터페이스                         │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │ Streamlit        │          │ FastAPI Admin    │        │
│  │ Dashboard        │          │ Dashboard        │        │
│  └──────────────────┘          └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                          │
│  - /api/query: RAG 질의응답                                 │
│  - /api/process-xml: XML 파일 처리                         │
│  - /api/articles: 기사 검색 및 조회                         │
│  - /api/stats: 시스템 통계                                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐  ┌─────────────────┐
│   XML Files  │    │  PostgreSQL DB   │  │  Vertex AI      │
│              │    │                  │  │  Vector Search  │
│  - 파싱       │───▶│  - Articles      │  │                 │
│  - 메타추출   │    │  - Categories    │◀─│  - Embeddings   │
│  - 중복필터   │    │  - Keywords      │  │  - Index        │
│              │    │  - Images        │  │                 │
└──────────────┘    └──────────────────┘  └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Gemini API      │
                    │  (RAG System)    │
                    └──────────────────┘
```

## 📦 주요 구성 요소

### 1. 데이터 처리 계층
- **XML Parser**: 기사 XML 파일 파싱
- **Metadata Extractor**: 제목, 본문, 요약, 분류 정보 추출
- **Entity Extractor**: 인물, 기업, 지역, 날짜 등 엔티티 추출
- **Content Hasher**: 중복 콘텐츠 감지

### 2. 벡터 임베딩 계층
- **Embedding Service**: 다국어 및 한국어 임베딩 모델
- **Vector Indexer**: VertexAI Vector Search 관리
- **Korean Embedding Model**: 한국어 특화 임베딩

### 3. 검색 및 RAG 계층
- **Hybrid RAG System**: 벡터 + 키워드 하이브리드 검색
- **Query Processor**: 자연어 쿼리 분석
- **Retrieval Engine**: 다중 검색 전략
- **Gemini Client**: Google Gemini API 연동

### 4. 증분형 처리 계층
- **Incremental Processor**: 신규 파일 자동 감지 및 처리
- **Duplicate Detector**: 콘텐츠 유사도 기반 중복 감지
- **Content Hasher**: 해시 기반 중복 필터링

### 5. 웹 인터페이스 계층
- **FastAPI**: REST API 서버
- **Streamlit**: 관리자 대시보드
- **Admin Dashboard**: HTML 기반 관리 화면

## 🗄️ 데이터베이스 스키마

### Articles (기사)
- id, art_id, art_year, art_no
- title, sub_title, body, summary
- writers, service_daytime, article_url
- embedding_vector, content_hash
- is_processed, is_embedded

### ArticleCategory (분류)
- article_id, code_id, code_nm
- large/middle/small_category

### ArticleKeyword (키워드)
- article_id, keyword, keyword_type

### ArticleImage (이미지)
- article_id, image_url, image_caption

### ArticleStockCode (주식코드)
- article_id, stock_code, stock_name

### VectorIndex (벡터 인덱스)
- index_name, index_id, endpoint_id
- dimensions, total_vectors, is_active

### ProcessingLog (처리 로그)
- article_id, process_type, status
- message, processing_time

## 🔧 기술 스택

### Backend
- Python 3.8+
- FastAPI: 웹 API 프레임워크
- SQLAlchemy: ORM
- PostgreSQL: 관계형 데이터베이스

### AI/ML
- Sentence Transformers: 벡터 임베딩
- Vertex AI: GCP AI 플랫폼
- Gemini API: 생성형 AI
- Transformers: 한국어 NLP

### Infrastructure
- GCP: Cloud Platform
- Terraform: IaC
- Docker: 컨테이너화

### Frontend
- Streamlit: 관리 대시보드
- HTML/CSS/JavaScript: 관리자 UI
- Plotly: 데이터 시각화

## 📂 프로젝트 구조

```
saltlux_xml/
├── terraform/              # GCP 인프라 설정
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── src/                   # 소스 코드
│   ├── __init__.py
│   ├── main.py            # 메인 실행 파일
│   ├── xml_parser.py      # XML 파싱
│   ├── xml_processor.py   # XML 처리 파이프라인
│   ├── database/          # 데이터베이스
│   │   ├── models.py
│   │   └── connection.py
│   ├── embedding/         # 벡터 임베딩
│   │   ├── embedding_service.py
│   │   └── korean_embedding_model.py
│   ├── vector_search/     # 벡터 검색
│   │   ├── vertex_ai_client.py
│   │   └── vector_indexer.py
│   ├── rag/               # RAG 시스템
│   │   ├── hybrid_rag_system.py
│   │   ├── gemini_client.py
│   │   ├── query_processor.py
│   │   └── retrieval_engine.py
│   ├── incremental/       # 증분형 처리
│   │   ├── incremental_processor.py
│   │   ├── duplicate_detector.py
│   │   └── content_hasher.py
│   └── web/               # 웹 애플리케이션
│       ├── app.py
│       └── streamlit_app.py
├── requirements.txt       # Python 의존성
├── deploy.sh             # 자동 배포
├── stop.sh               # 서비스 중지
├── gcp_setup.sh          # GCP 설정
├── env.example           # 환경 변수 예제
├── README.md             # 프로젝트 문서
└── PROJECT_SUMMARY.md    # 프로젝트 요약

```

## 🚀 빠른 시작

### 1. GCP 설정
```bash
# GCP 로그인 및 프로젝트 설정
./gcp_setup.sh

# 또는 수동 설정
gcloud auth login godwind2015@gmail.com
gcloud config set project godwind2015
```

### 2. 환경 변수 설정
```bash
cp env.example .env
# .env 파일 편집하여 API 키 설정
```

### 3. 의존성 설치
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 데이터베이스 초기화
```bash
python src/main.py --mode init
```

### 5. XML 파일 처리
```bash
python src/main.py --mode process --xml-directory xml_files
```

### 6. 서비스 실행
```bash
# 자동 배포
./deploy.sh

# 또는 수동 실행
uvicorn src.web.app:app --host 0.0.0.0 --port 8000
streamlit run src/web/streamlit_app.py --server.port 8501
```

## 🔍 주요 기능

### 1. XML 파싱 및 메타정보 추출
- 기사 제목, 본문, 요약 추출
- 분류 정보 (정치, 경제, 사회 등)
- 엔티티 추출 (인물, 기업, 지역, 날짜)
- 이미지 및 주식 코드 정보

### 2. 벡터 임베딩
- 다국어 모델: paraphrase-multilingual-MiniLM-L12-v2
- 한국어 특화 모델
- VertexAI Vector Search 통합
- 배치 처리 및 병렬 처리

### 3. Hybrid RAG 시스템 (고급 기능)
- **벡터 검색**: 의미적 유사도 기반
- **키워드 검색**: 정확한 매칭
- **가중치 설정**: 벡터/키워드/리랭킹 가중치 조정
- **메타데이터 필터링**: 날짜, 카테고리, 작성자, 주식코드 등
- **검색 품질 메트릭**: 평균 유사도, 최고 유사도, 검색 다양성
- **Gemini API 기반 자연어 응답**

### 4. 증분형 처리
- 새로운 XML 파일 자동 감지
- 마지막 처리 시간 기반 증분 처리
- 중복 콘텐츠 자동 필터링
- 백그라운드 처리 지원

### 5. 개별 기사 해설 생성
- **과거 타임라인 분석**: 관련 기사 히스토리 추적
- **현재 기사 논설**: 주요 논점 및 핵심 키워드 분석
- **향후 전망**: 예상 추이 및 영향 요인 분석
- **참조 기사**: 관련 기사 자동 검색 및 연결

### 6. GCP 인프라 관리
- **인터랙티브 인프라 구성**: Terraform 기반 자동 배포
- **Gemini API 키 설정**: 관리자 화면에서 직접 설정
- **인프라 테스트**: 연결 상태 및 서비스 상태 확인
- **인프라 모니터링**: 리소스 사용량 및 성능 추적

### 7. 실시간 모니터링
- 시스템 통계 대시보드
- 벡터 인덱스 상태 모니터링
- 처리 로그 및 성능 메트릭
- 기사 통계 시각화

## 📊 처리 성능

- **XML 파싱**: 배치 처리 (100개/배치)
- **임베딩 생성**: 배치 처리 (50개/배치)
- **벡터 검색**: <100ms
- **RAG 응답**: <2초

## 🔐 보안 및 권한

- GCP 서비스 계정 기반 인증
- Cloud SQL Private IP 연결
- VPC 네트워크 격리
- API 키 환경 변수 관리

## 📈 확장성

- 수평 확장: 다중 인스턴스 지원
- 수직 확장: 인스턴스 타입 조정
- 데이터베이스: Read Replica 지원
- 벡터 인덱스: 자동 스케일링

## 🐛 문제 해결

### 일반적인 문제
1. **GCP 인증 오류**: `gcloud auth login` 실행
2. **데이터베이스 연결 오류**: Cloud SQL 인스턴스 상태 확인
3. **벡터 인덱스 오류**: VertexAI API 활성화 확인
4. **임베딩 생성 오류**: 모델 다운로드 및 메모리 확인

### 로그 확인
```bash
tail -f mk_news_platform.log
grep "ERROR" mk_news_platform.log
```

## 📞 지원 및 문의

- **이메일**: godwind2015@gmail.com
- **프로젝트**: MK AI Project (godwind2015)
- **문서**: README.md 참조

---

**매일경제 신문기사 벡터임베딩 플랫폼**  
GCP VertexAI 기반 Hybrid RAG 시스템  
MK AI Project - godwind2015@gmail.com
