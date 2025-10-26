#!/bin/bash

# GCP 설정 스크립트 - MK AI Project (godwind2015@gmail.com)

set -e

echo "🔧 GCP 설정 시작 - MK AI Project"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# GCP 계정 및 프로젝트 설정
setup_gcp_account() {
    log_info "GCP 계정 및 프로젝트 설정 중..."
    
    # GCP 계정 로그인
    log_info "GCP 계정 로그인: godwind2015@gmail.com"
    gcloud auth login godwind2015@gmail.com
    
    # 프로젝트 설정
    log_info "프로젝트 설정: godwind2015"
    gcloud config set project godwind2015
    
    # 리전 설정
    log_info "리전 설정: asia-northeast3"
    gcloud config set compute/region asia-northeast3
    gcloud config set compute/zone asia-northeast3-a
    
    # 현재 설정 확인
    log_info "현재 GCP 설정:"
    gcloud config list
    
    log_success "GCP 계정 및 프로젝트 설정 완료"
}

# 필요한 API 활성화
enable_apis() {
    log_info "필요한 GCP API 활성화 중..."
    
    # 필요한 API 목록
    apis=(
        "aiplatform.googleapis.com"
        "compute.googleapis.com"
        "sqladmin.googleapis.com"
        "storage.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "servicenetworking.googleapis.com"
        "cloudsql.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        log_info "API 활성화: $api"
        gcloud services enable "$api"
    done
    
    log_success "모든 필요한 API 활성화 완료"
}

# 서비스 계정 생성 및 권한 설정
setup_service_account() {
    log_info "서비스 계정 생성 및 권한 설정 중..."
    
    # 서비스 계정 생성
    service_account_name="mk-news-platform-sa"
    service_account_email="${service_account_name}@godwind2015.iam.gserviceaccount.com"
    
    # 서비스 계정이 존재하는지 확인
    if gcloud iam service-accounts describe "$service_account_email" &>/dev/null; then
        log_info "서비스 계정이 이미 존재합니다: $service_account_email"
    else
        log_info "서비스 계정 생성: $service_account_email"
        gcloud iam service-accounts create "$service_account_name" \
            --display-name="매일경제 신문기사 벡터임베딩 플랫폼 서비스 계정" \
            --description="매일경제 신문기사 벡터임베딩 플랫폼용 서비스 계정"
    fi
    
    # 필요한 권한 부여
    roles=(
        "roles/aiplatform.user"
        "roles/storage.admin"
        "roles/cloudsql.client"
        "roles/compute.instanceAdmin"
        "roles/iam.serviceAccountUser"
    )
    
    for role in "${roles[@]}"; do
        log_info "권한 부여: $role"
        gcloud projects add-iam-policy-binding godwind2015 \
            --member="serviceAccount:$service_account_email" \
            --role="$role"
    done
    
    # 서비스 계정 키 생성
    log_info "서비스 계정 키 생성 중..."
    gcloud iam service-accounts keys create service-account-key.json \
        --iam-account="$service_account_email"
    
    # 환경 변수 설정
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account-key.json"
    echo "export GOOGLE_APPLICATION_CREDENTIALS=\"$(pwd)/service-account-key.json\"" >> ~/.bashrc
    
    log_success "서비스 계정 설정 완료"
}

# Cloud SQL 인스턴스 생성
create_cloud_sql() {
    log_info "Cloud SQL 인스턴스 생성 중..."
    
    instance_name="mk-news-db"
    
    # 인스턴스가 존재하는지 확인
    if gcloud sql instances describe "$instance_name" &>/dev/null; then
        log_info "Cloud SQL 인스턴스가 이미 존재합니다: $instance_name"
    else
        log_info "Cloud SQL 인스턴스 생성: $instance_name"
        gcloud sql instances create "$instance_name" \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=asia-northeast3 \
            --storage-type=SSD \
            --storage-size=10GB \
            --backup \
            --enable-bin-log
    fi
    
    # 데이터베이스 생성
    log_info "데이터베이스 생성: mk_news"
    gcloud sql databases create mk_news --instance="$instance_name" || true
    
    # 사용자 생성
    log_info "데이터베이스 사용자 생성"
    gcloud sql users create postgres \
        --instance="$instance_name" \
        --password="mk_news_secure_password_2024" || true
    
    log_success "Cloud SQL 설정 완료"
}

# Cloud Storage 버킷 생성
create_storage_bucket() {
    log_info "Cloud Storage 버킷 생성 중..."
    
    bucket_name="mk-news-storage-godwind2015"
    
    # 버킷이 존재하는지 확인
    if gsutil ls -b "gs://$bucket_name" &>/dev/null; then
        log_info "Cloud Storage 버킷이 이미 존재합니다: $bucket_name"
    else
        log_info "Cloud Storage 버킷 생성: $bucket_name"
        gsutil mb -l asia-northeast3 "gs://$bucket_name"
        
        # 버킷 설정
        gsutil versioning set on "gs://$bucket_name"
        gsutil lifecycle set - "gs://$bucket_name" <<EOF
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 30}
    }
  ]
}
EOF
    fi
    
    log_success "Cloud Storage 버킷 설정 완료"
}

# Vertex AI 설정
setup_vertex_ai() {
    log_info "Vertex AI 설정 중..."
    
    # Vertex AI API 활성화 확인
    if gcloud services list --enabled --filter="name:aiplatform.googleapis.com" | grep -q "aiplatform.googleapis.com"; then
        log_info "Vertex AI API가 이미 활성화되어 있습니다."
    else
        log_info "Vertex AI API 활성화 중..."
        gcloud services enable aiplatform.googleapis.com
    fi
    
    log_success "Vertex AI 설정 완료"
}

# 환경 변수 파일 생성
create_env_file() {
    log_info "환경 변수 파일 생성 중..."
    
    cat > .env <<EOF
APPDATA=C:\Users\godwind2015\AppData\Roaming
# GCP 설정
GCP_PROJECT_ID=godwind2015
GCP_REGION=asia-northeast3
GCP_ZONE=asia-northeast3-a

# 데이터베이스 설정
USE_CLOUD_SQL=true
DB_INSTANCE_NAME=mk-news-db
DB_NAME=mk_news
DB_USER=postgres
DB_PASSWORD=mk_news_secure_password_2024

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Vertex AI 설정
USE_VERTEX_AI=true
GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/service-account-key.json

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=mk_news_platform.log

# 애플리케이션 설정
APP_HOST=0.0.0.0
APP_PORT=8000
STREAMLIT_PORT=8501

# XML 파일 경로
XML_DIRECTORY=$(pwd)/xml_files

# 배치 처리 설정
BATCH_SIZE=100
MAX_WORKERS=4

# 임베딩 설정
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSIONS=768

# 벡터 검색 설정
VECTOR_INDEX_NAME=mk-news-vector-index
VECTOR_ENDPOINT_NAME=mk-news-vector-endpoint
SIMILARITY_THRESHOLD=0.7

# RAG 시스템 설정
MAX_RETRIEVED_DOCS=20
MAX_CONTEXT_LENGTH=4000
TOP_K_RESULTS=10

# 중복 감지 설정
DUPLICATE_SIMILARITY_THRESHOLD=0.8
CONTENT_HASH_ALGORITHM=md5

# 모니터링 설정
ENABLE_METRICS=true
METRICS_PORT=9090
EOF
    
    log_success "환경 변수 파일 생성 완료: .env"
}

# 설정 확인
verify_setup() {
    log_info "GCP 설정 확인 중..."
    
    # 현재 프로젝트 확인
    current_project=$(gcloud config get-value project)
    if [ "$current_project" = "godwind2015" ]; then
        log_success "프로젝트 설정 확인: $current_project"
    else
        log_error "프로젝트 설정 오류: $current_project (예상: godwind2015)"
    fi
    
    # API 활성화 확인
    log_info "활성화된 API 확인:"
    gcloud services list --enabled --filter="name:(aiplatform OR compute OR sqladmin OR storage)"
    
    # 서비스 계정 확인
    if [ -f "service-account-key.json" ]; then
        log_success "서비스 계정 키 파일 확인"
    else
        log_error "서비스 계정 키 파일이 없습니다."
    fi
    
    log_success "GCP 설정 확인 완료"
}

# 메인 실행
main() {
    log_info "GCP 설정 시작 - MK AI Project (godwind2015@gmail.com)"
    
    setup_gcp_account
    enable_apis
    setup_service_account
    create_cloud_sql
    create_storage_bucket
    setup_vertex_ai
    create_env_file
    verify_setup
    
    log_success "🎉 GCP 설정 완료!"
    
    echo ""
    echo "📋 설정 완료 정보:"
    echo "  - 프로젝트: MK AI Project (godwind2015)"
    echo "  - 계정: godwind2015@gmail.com"
    echo "  - 리전: asia-northeast3"
    echo "  - 서비스 계정: mk-news-platform-sa@godwind2015.iam.gserviceaccount.com"
    echo "  - Cloud SQL: mk-news-db"
    echo "  - Storage: mk-news-storage-godwind2015"
    echo ""
    echo "🔧 다음 단계:"
    echo "  1. Gemini API 키 설정: .env 파일에서 GEMINI_API_KEY 수정"
    echo "  2. 인프라 배포: ./deploy.sh"
    echo "  3. XML 파일 처리: python src/main.py --mode process --xml-directory /path/to/xml"
    echo ""
}

# 스크립트 실행
main "$@"