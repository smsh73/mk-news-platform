# 매일경제 AI 플랫폼

Google Cloud Platform 기반 벡터임베딩 & RAG 솔루션 관리자 대시보드

## 🚀 주요 기능

- **GCP 통합**: Google Cloud Platform 서비스와 완전 통합
- **벡터 임베딩**: Vertex AI를 활용한 고성능 벡터 임베딩
- **RAG 시스템**: 하이브리드 검색 및 생성 시스템
- **실시간 대시보드**: GCP Material Design 기반 현대적 UI
- **자동화 처리**: 증분형 데이터 처리 및 모니터링

## 🛠 기술 스택

- **Frontend**: Streamlit, GCP Material Design
- **Backend**: FastAPI, Python
- **Database**: Cloud SQL (PostgreSQL)
- **AI/ML**: Vertex AI, Gemini API, Vector Search
- **Infrastructure**: Terraform, Cloud Run, Cloud Storage

## 📋 요구사항

- Python 3.11+
- Google Cloud SDK
- Docker (선택사항)

## 🔧 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/mk-ai-platform.git
cd mk-ai-platform
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 GCP 프로젝트 정보 입력
```

### 4. GCP 인증
```bash
gcloud auth login
gcloud auth application-default login
```

### 5. 애플리케이션 실행
```bash
# Streamlit 대시보드
streamlit run src/web/streamlit_app.py

# FastAPI 백엔드
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 배포

### Streamlit Community Cloud
1. GitHub 저장소에 코드 푸시
2. [Streamlit Community Cloud](https://share.streamlit.io/)에서 배포
3. 저장소 URL과 메인 파일 경로 설정: `src/web/streamlit_app.py`

### Google Cloud Platform
```bash
# Terraform으로 인프라 배포
cd terraform
terraform init
terraform plan
terraform apply
```

## 📁 프로젝트 구조

```
mk-ai-platform/
├── src/
│   ├── web/                 # 웹 애플리케이션
│   │   ├── app.py          # FastAPI 백엔드
│   │   ├── streamlit_app.py # Streamlit 대시보드
│   │   ├── gcp_theme.py    # GCP 테마 시스템
│   │   └── static/         # 정적 파일
│   ├── database/           # 데이터베이스 연결
│   ├── vector_search/      # 벡터 검색
│   ├── rag/               # RAG 시스템
│   └── incremental/       # 증분 처리
├── terraform/             # 인프라 코드
├── requirements.txt       # Python 의존성
└── README.md             # 프로젝트 문서
```

## 🔐 환경 변수

```bash
# GCP 설정
GCP_PROJECT_ID=your-project-id
GCP_REGION=asia-northeast3

# 데이터베이스
DB_INSTANCE_NAME=mk-news-db
DB_NAME=mk_news
DB_USER=postgres
DB_PASSWORD=your-password

# API 키
GEMINI_API_KEY=your-gemini-api-key
```

## 📊 대시보드 기능

- **시스템 모니터링**: 실시간 상태 및 메트릭
- **기사 관리**: 뉴스 기사 검색 및 관리
- **RAG 검색**: 하이브리드 검색 시스템
- **통계 분석**: 데이터 분석 및 시각화
- **GCP 인프라**: 클라우드 리소스 관리
- **벡터 처리**: 임베딩 및 인덱싱 관리
- **AI 해설**: Gemini API 기반 자동 해설

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 있거나 질문이 있으시면 [Issues](https://github.com/your-username/mk-ai-platform/issues)를 통해 문의해주세요.

## 🙏 감사의 말

- Google Cloud Platform
- Streamlit Community
- 매일경제신문# CI/CD Test - Thu Oct 30 20:42:00 KST 2025
