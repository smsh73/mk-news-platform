# 로컬 배포 가이드

## 개요

로컬 환경에서 관리자 애플리케이션을 실행하고, GCP에 Terraform을 통해 인프라를 배포하는 가이드입니다.

## 사전 준비

### 1. 필수 도구 설치

```bash
# Python 3.11+ 설치 확인
python3 --version

# Google Cloud SDK 설치 확인
gcloud --version

# Terraform 설치 확인
terraform --version
```

### 2. 의존성 설치

```bash
# 가상 환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# .env 파일 생성
cp env.example .env

# .env 파일 편집
nano .env
```

`.env` 파일 내용:
```bash
# GCP 설정
GCP_PROJECT_ID=godwind2015
GCP_REGION=asia-northeast3

# 데이터베이스 설정 (로컬)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mk_news
DB_USER=postgres
DB_PASSWORD=your_password

# Gemini API 설정
GEMINI_API_KEY=your_gemini_api_key

# 애플리케이션 설정
USE_MANAGED_SERVICES=false
PORT=8000
```

## 로컬 배포 및 실행

### 1단계: 관리자 애플리케이션 실행

터미널 1: Streamlit 관리자 대시보드
```bash
streamlit run src/web/streamlit_app.py
```

터미널 2: FastAPI 백엔드 (선택사항)
```bash
uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

브라우저에서 접속:
- 관리자 대시보드: http://localhost:8501
- API 서버: http://localhost:8000

### 2단계: GCP 로그인

관리자 대시보드에서:
1. "☁️ GCP 인프라" 탭 선택
2. "gcloud CLI" 선택
3. "🔑 gcloud 로그인" 버튼 클릭
4. 브라우저에서 인증 완료

### 3단계: GCP 프로젝트 설정

관리자 대시보드에서:
1. "📋 프로젝트 목록 조회" 버튼 클릭
2. 프로젝트 선택
3. "✅ 프로젝트 설정" 버튼 클릭

### 4단계: Terraform 배포

관리자 대시보드에서:
1. "🏗️ 인프라 배포" 섹션으로 스크롤
2. "🚀 Terraform 배포" 버튼 클릭
3. 배포 계획 확인
4. "✅ 배포 실행" 버튼 클릭
5. **실시간 로그 확인** (구현됨)

## 배포 프로세스

### 실시간 로깅 및 모니터링

관리자 대시보드에서 Terraform 배포를 실행하면:

1. **배포 단계 표시**
   - Terraform 초기화
   - Plan 실행
   - Apply 실행
   - 각 단계별 진행률 표시

2. **실시간 로그 스트림**
   - 배포 프로세스의 모든 출력
   - 에러 메시지 즉시 표시
   - 성공/실패 상태 표시

3. **리소스 생성 확인**
   - VPC 네트워크
   - Cloud SQL
   - Cloud Storage
   - Artifact Registry
   - Vertex AI Vector Search
   - Cloud Run 서비스

### 배포 후 확인

관리자 대시보드에서:
1. "🧪 인프라 테스트" 섹션으로 이동
2. "🔍 연결 테스트" 버튼 클릭
3. 리소스 상태 확인

또는 터미널에서:
```bash
# 배포된 서비스 URL 확인
cd terraform
terraform output admin_service_url
terraform output api_service_url
```

## 문제 해결

### Terraform 배포 실패

1. **GCP 로그인 확인**
   ```bash
   gcloud auth list
   gcloud config get-value project
   ```

2. **권한 확인**
   ```bash
   gcloud projects get-iam-policy PROJECT_ID
   ```

3. **필수 API 활성화 확인**
   ```bash
   gcloud services list --enabled
   ```

### 로컬 애플리케이션 실행 오류

1. **포트 충돌**
   ```bash
   # 포트 사용 확인
   lsof -i :8501
   lsof -i :8000
   
   # 프로세스 종료
   kill -9 PID
   ```

2. **의존성 문제**
   ```bash
   # 가상 환경 재생성
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 다음 단계

배포 완료 후:
1. XML 파일 업로드
2. 벡터 임베딩 처리
3. 메타데이터 추출
4. Gemini API로 해설 생성
5. 연관기사 검색

자세한 내용은 `GCP_DEPLOYMENT_GUIDE.md` 참조
