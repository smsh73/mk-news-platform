#!/bin/bash

# 매일경제 신문기사 벡터임베딩 플랫폼 배포 스크립트

set -e

echo "🚀 매일경제 신문기사 벡터임베딩 플랫폼 배포 시작..."

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

# 환경 확인
check_environment() {
    log_info "환경 확인 중..."
    
    # Python 버전 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되지 않았습니다."
        exit 1
    fi
    
    # pip 확인
    if ! command -v pip &> /dev/null; then
        log_error "pip가 설치되지 않았습니다."
        exit 1
    fi
    
    # gcloud 확인
    if ! command -v gcloud &> /dev/null; then
        log_warning "gcloud CLI가 설치되지 않았습니다. GCP 서비스를 사용할 수 없습니다."
        log_info "gcloud CLI 설치: https://cloud.google.com/sdk/docs/install"
        log_info "인증 설정: gcloud auth login godwind2015@gmail.com"
    fi
    
    # terraform 확인
    if ! command -v terraform &> /dev/null; then
        log_warning "terraform이 설치되지 않았습니다. 인프라 배포를 건너뜁니다."
    fi
    
    log_success "환경 확인 완료"
}

# 가상환경 설정
setup_virtual_environment() {
    log_info "가상환경 설정 중..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "가상환경 생성 완료"
    fi
    
    source venv/bin/activate
    log_success "가상환경 활성화 완료"
}

# 의존성 설치
install_dependencies() {
    log_info "의존성 설치 중..."
    
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "의존성 설치 완료"
}

# 환경 변수 설정
setup_environment() {
    log_info "환경 변수 설정 중..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            log_warning "env.example을 .env로 복사했습니다. 필요한 값들을 수정해주세요."
        else
            log_error "환경 변수 파일이 없습니다. env.example 파일을 생성해주세요."
            exit 1
        fi
    fi
    
    # 환경 변수 로드
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    log_success "환경 변수 설정 완료"
}

# GCP 인프라 배포
deploy_infrastructure() {
    log_info "GCP 인프라 배포 중..."
    
    if [ -d "terraform" ]; then
        cd terraform
        
        # Terraform 초기화
        if [ ! -d ".terraform" ]; then
            terraform init
        fi
        
        # Terraform 계획 확인
        terraform plan
        
        # 사용자 확인
        read -p "인프라를 배포하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            terraform apply -auto-approve
            log_success "GCP 인프라 배포 완료"
        else
            log_warning "인프라 배포를 건너뜁니다."
        fi
        
        cd ..
    else
        log_warning "terraform 디렉토리가 없습니다. 인프라 배포를 건너뜁니다."
    fi
}

# 데이터베이스 초기화
initialize_database() {
    log_info "데이터베이스 초기화 중..."
    
    python src/main.py --mode init
    
    log_success "데이터베이스 초기화 완료"
}

# 시스템 테스트
test_system() {
    log_info "시스템 테스트 중..."
    
    # 헬스 체크
    python -c "
import requests
import time
import sys

# FastAPI 서버 시작 (백그라운드)
import subprocess
import os

# 서버 시작
server_process = subprocess.Popen([
    'uvicorn', 'src.web.app:app', 
    '--host', '0.0.0.0', 
    '--port', '8000'
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 서버 시작 대기
time.sleep(10)

try:
    response = requests.get('http://localhost:8000/health', timeout=10)
    if response.status_code == 200:
        print('✅ FastAPI 서버 정상 동작')
    else:
        print('❌ FastAPI 서버 응답 오류')
        sys.exit(1)
except Exception as e:
    print(f'❌ FastAPI 서버 테스트 실패: {e}')
    sys.exit(1)
finally:
    server_process.terminate()
"
    
    log_success "시스템 테스트 완료"
}

# XML 파일 처리 (선택사항)
process_xml_files() {
    log_info "XML 파일 처리 옵션"
    
    read -p "XML 파일을 처리하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "XML 파일 디렉토리 경로를 입력하세요: " xml_dir
        
        if [ -d "$xml_dir" ]; then
            log_info "XML 파일 처리 중..."
            python src/main.py --mode process --xml-directory "$xml_dir"
            log_success "XML 파일 처리 완료"
        else
            log_error "XML 디렉토리를 찾을 수 없습니다: $xml_dir"
        fi
    fi
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    # FastAPI 서버 시작 (백그라운드)
    nohup uvicorn src.web.app:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &
    echo $! > fastapi.pid
    
    # Streamlit 대시보드 시작 (백그라운드)
    nohup streamlit run src/web/streamlit_app.py --server.port 8501 --server.headless true > streamlit.log 2>&1 &
    echo $! > streamlit.pid
    
    log_success "서비스 시작 완료"
    log_info "FastAPI 서버: http://localhost:8000"
    log_info "Streamlit 대시보드: http://localhost:8501"
    log_info "관리자 대시보드: http://localhost:8000/admin"
}

# 배포 완료 메시지
deployment_complete() {
    log_success "🎉 매일경제 신문기사 벡터임베딩 플랫폼 배포 완료!"
    
    echo ""
    echo "📋 배포 정보:"
    echo "  - FastAPI 서버: http://localhost:8000"
    echo "  - Streamlit 대시보드: http://localhost:8501"
    echo "  - 관리자 대시보드: http://localhost:8000/admin"
    echo "  - API 문서: http://localhost:8000/docs"
    echo ""
    echo "📁 로그 파일:"
    echo "  - 시스템 로그: mk_news_platform.log"
    echo "  - FastAPI 로그: fastapi.log"
    echo "  - Streamlit 로그: streamlit.log"
    echo ""
    echo "🔧 관리 명령어:"
    echo "  - 서비스 중지: ./stop.sh"
    echo "  - 로그 확인: tail -f mk_news_platform.log"
    echo "  - 시스템 상태: python src/main.py --mode status"
    echo ""
}

# 메인 실행
main() {
    log_info "매일경제 신문기사 벡터임베딩 플랫폼 배포 시작"
    
    check_environment
    setup_virtual_environment
    install_dependencies
    setup_environment
    deploy_infrastructure
    initialize_database
    test_system
    process_xml_files
    start_services
    deployment_complete
}

# 스크립트 실행
main "$@"
