#!/bin/bash

# 매일경제 신문기사 벡터임베딩 플랫폼 서비스 중지 스크립트

set -e

echo "🛑 매일경제 신문기사 벡터임베딩 플랫폼 서비스 중지 중..."

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

# FastAPI 서버 중지
stop_fastapi() {
    log_info "FastAPI 서버 중지 중..."
    
    if [ -f "fastapi.pid" ]; then
        pid=$(cat fastapi.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log_success "FastAPI 서버 중지 완료 (PID: $pid)"
        else
            log_warning "FastAPI 서버가 이미 중지되었습니다."
        fi
        rm -f fastapi.pid
    else
        log_warning "FastAPI PID 파일을 찾을 수 없습니다."
        
        # 프로세스 이름으로 찾아서 중지
        pids=$(pgrep -f "uvicorn src.web.app:app")
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill
            log_success "FastAPI 서버 중지 완료"
        else
            log_warning "실행 중인 FastAPI 서버를 찾을 수 없습니다."
        fi
    fi
}

# Streamlit 서버 중지
stop_streamlit() {
    log_info "Streamlit 서버 중지 중..."
    
    if [ -f "streamlit.pid" ]; then
        pid=$(cat streamlit.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log_success "Streamlit 서버 중지 완료 (PID: $pid)"
        else
            log_warning "Streamlit 서버가 이미 중지되었습니다."
        fi
        rm -f streamlit.pid
    else
        log_warning "Streamlit PID 파일을 찾을 수 없습니다."
        
        # 프로세스 이름으로 찾아서 중지
        pids=$(pgrep -f "streamlit run src.web.streamlit_app")
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill
            log_success "Streamlit 서버 중지 완료"
        else
            log_warning "실행 중인 Streamlit 서버를 찾을 수 없습니다."
        fi
    fi
}

# 관련 프로세스 정리
cleanup_processes() {
    log_info "관련 프로세스 정리 중..."
    
    # Python 프로세스 중지 (플랫폼 관련)
    pids=$(pgrep -f "python.*src/main.py")
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill
        log_success "메인 프로세스 중지 완료"
    fi
    
    # 포트 사용 프로세스 확인 및 중지
    ports=(8000 8501)
    for port in "${ports[@]}"; do
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pid" ]; then
            kill "$pid" 2>/dev/null || true
            log_info "포트 $port 사용 프로세스 중지 완료"
        fi
    done
}

# 로그 파일 정리
cleanup_logs() {
    log_info "로그 파일 정리 중..."
    
    # 로그 파일 압축
    if [ -f "fastapi.log" ]; then
        gzip -f fastapi.log
        log_info "FastAPI 로그 파일 압축 완료"
    fi
    
    if [ -f "streamlit.log" ]; then
        gzip -f streamlit.log
        log_info "Streamlit 로그 파일 압축 완료"
    fi
    
    # 오래된 로그 파일 정리 (30일 이상)
    find . -name "*.log.gz" -mtime +30 -delete 2>/dev/null || true
    log_info "오래된 로그 파일 정리 완료"
}

# 서비스 상태 확인
check_status() {
    log_info "서비스 상태 확인 중..."
    
    # 포트 사용 확인
    ports=(8000 8501)
    for port in "${ports[@]}"; do
        if lsof -ti:$port >/dev/null 2>&1; then
            log_warning "포트 $port가 여전히 사용 중입니다."
        else
            log_success "포트 $port 사용 중지 확인"
        fi
    done
    
    # 프로세스 확인
    fastapi_pids=$(pgrep -f "uvicorn src.web.app:app" || true)
    streamlit_pids=$(pgrep -f "streamlit run src.web.streamlit_app" || true)
    
    if [ -n "$fastapi_pids" ]; then
        log_warning "FastAPI 프로세스가 여전히 실행 중입니다: $fastapi_pids"
    fi
    
    if [ -n "$streamlit_pids" ]; then
        log_warning "Streamlit 프로세스가 여전히 실행 중입니다: $streamlit_pids"
    fi
    
    if [ -z "$fastapi_pids" ] && [ -z "$streamlit_pids" ]; then
        log_success "모든 서비스가 정상적으로 중지되었습니다."
    fi
}

# 메인 실행
main() {
    log_info "매일경제 신문기사 벡터임베딩 플랫폼 서비스 중지 시작"
    
    stop_fastapi
    stop_streamlit
    cleanup_processes
    cleanup_logs
    check_status
    
    log_success "🎉 모든 서비스 중지 완료!"
    
    echo ""
    echo "📋 중지된 서비스:"
    echo "  - FastAPI 서버 (포트 8000)"
    echo "  - Streamlit 대시보드 (포트 8501)"
    echo ""
    echo "🔧 재시작 명령어:"
    echo "  - 서비스 시작: ./deploy.sh"
    echo "  - 개별 시작: uvicorn src.web.app:app --host 0.0.0.0 --port 8000"
    echo "  - 대시보드 시작: streamlit run src/web/streamlit_app.py --server.port 8501"
    echo ""
}

# 스크립트 실행
main "$@"


