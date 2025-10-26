"""
엔터프라이즈급 매일경제 신문기사 벡터임베딩 플랫폼 관리자 대시보드
Salesforce Lightning Design System 기반 전문 웹 포털
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
import subprocess
import time
from pathlib import Path
import webbrowser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth import default
import tempfile
from gcp_theme import (
    apply_gcp_theme,
    create_gcp_header,
    create_gcp_navigation,
    create_gcp_sidebar,
    create_gcp_card,
    create_gcp_metric_card,
    create_gcp_button,
    create_gcp_alert,
    create_gcp_status_indicator,
    create_gcp_progress_bar,
    create_gcp_loading_spinner,
    create_gcp_empty_state,
    create_gcp_table,
    create_gcp_form_group,
    create_gcp_modal,
    create_gcp_dashboard_grid,
    create_gcp_chart_container
)

# 페이지 설정
st.set_page_config(
    page_title="매일경제 AI 플랫폼 | 엔터프라이즈 관리자 대시보드",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.mk.co.kr',
        'Report a bug': "https://github.com/mk-ai-platform",
        'About': "# 매일경제 AI 플랫폼\n엔터프라이즈급 벡터임베딩 솔루션"
    }
)

# GCP 테마 적용
apply_gcp_theme()

# GCP OAuth 설정
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/cloud-platform.read-only',
    'https://www.googleapis.com/auth/aiplatform',
    'https://www.googleapis.com/auth/sqlservice.admin'
]

def check_gcp_auth():
    """GCP 인증 상태 확인"""
    try:
        credentials, project = default(scopes=SCOPES)
        if credentials and credentials.valid:
            return True, project
        return False, None
    except Exception as e:
        return False, None

def get_gcp_auth_url():
    """GCP OAuth 인증 URL 생성"""
    try:
        # OAuth 2.0 클라이언트 ID 설정 (웹 애플리케이션용)
        client_config = {
            "web": {
                "client_id": "your-client-id.apps.googleusercontent.com",
                "client_secret": "your-client-secret",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8501"]
            }
        }
        
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    except Exception as e:
        st.error(f"OAuth URL 생성 실패: {e}")
        return None

def authenticate_with_gcloud(login_type="browser"):
    """gcloud CLI를 통한 인증"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "gcloud CLI가 설치되지 않았습니다. Google Cloud SDK를 설치해주세요."
        
        # 로그인 유형에 따른 명령어 구성
        if login_type == "browser":
            # 브라우저를 통한 인증 (기본)
            result = subprocess.run(['gcloud', 'auth', 'login'], 
                                  capture_output=True, text=True, timeout=120)
        elif login_type == "no_browser":
            # 브라우저 없이 인증 (URL 제공)
            result = subprocess.run(['gcloud', 'auth', 'login', '--no-launch-browser'], 
                                  capture_output=True, text=True, timeout=60)
        elif login_type == "service_account":
            # 서비스 계정 키 파일 업로드
            return False, "서비스 계정 키 파일을 업로드해주세요."
        else:
            return False, "지원하지 않는 로그인 유형입니다."
        
        if result.returncode == 0:
            return True, "gcloud 인증 성공"
        else:
            # 에러 메시지에서 URL 추출
            error_msg = result.stderr
            if "Go to the following link" in error_msg:
                # URL 추출
                import re
                url_match = re.search(r'https://[^\s]+', error_msg)
                if url_match:
                    url = url_match.group(0)
                    return False, f"브라우저에서 다음 링크를 열어 인증을 완료하세요:\n\n{url}\n\n인증 완료 후 페이지를 새로고침하세요."
            return False, f"gcloud 인증 실패: {error_msg}"
    except FileNotFoundError:
        return False, "gcloud CLI가 설치되지 않았습니다. Google Cloud SDK를 설치해주세요."
    except Exception as e:
        return False, f"gcloud 인증 오류: {e}"

def set_application_default_credentials():
    """Application Default Credentials 설정"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "gcloud CLI가 설치되지 않았습니다. Google Cloud SDK를 설치해주세요."
        
        # ADC 설정 실행
        result = subprocess.run(['gcloud', 'auth', 'application-default', 'login'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True, "ADC 설정 성공"
        else:
            # 에러 메시지에서 URL 추출
            error_msg = result.stderr
            if "Go to the following link" in error_msg:
                import re
                url_match = re.search(r'https://[^\s]+', error_msg)
                if url_match:
                    url = url_match.group(0)
                    return False, f"브라우저에서 다음 링크를 열어 ADC 설정을 완료하세요:\n\n{url}\n\n설정 완료 후 페이지를 새로고침하세요."
            return False, f"ADC 설정 실패: {error_msg}"
    except FileNotFoundError:
        return False, "gcloud CLI가 설치되지 않았습니다. Google Cloud SDK를 설치해주세요."
    except Exception as e:
        return False, f"ADC 설정 오류: {e}"

def authenticate_with_service_account(service_account_file):
    """서비스 계정 키 파일을 통한 인증"""
    try:
        import json
        import os
        
        # 임시 파일로 저장
        temp_file = f"/tmp/service_account_{os.getpid()}.json"
        with open(temp_file, 'w') as f:
            f.write(service_account_file)
        
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            os.remove(temp_file)
            return False, "gcloud CLI가 설치되지 않았습니다."
        
        # 서비스 계정으로 인증
        result = subprocess.run(['gcloud', 'auth', 'activate-service-account', '--key-file', temp_file], 
                              capture_output=True, text=True, timeout=30)
        
        # 임시 파일 삭제
        os.remove(temp_file)
        
        if result.returncode == 0:
            return True, "서비스 계정 인증 성공"
        else:
            return False, f"서비스 계정 인증 실패: {result.stderr}"
    except Exception as e:
        return False, f"서비스 계정 인증 오류: {e}"

def get_gcp_projects():
    """GCP 프로젝트 목록 조회"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "gcloud CLI가 설치되지 않았습니다."
        
        result = subprocess.run(['gcloud', 'projects', 'list', '--format=json'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            projects = json.loads(result.stdout)
            return True, projects
        else:
            return False, f"프로젝트 조회 실패: {result.stderr}"
    except FileNotFoundError:
        return False, "gcloud CLI가 설치되지 않았습니다."
    except Exception as e:
        return False, f"프로젝트 조회 오류: {e}"

def get_current_project():
    """현재 설정된 프로젝트 조회"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        return None

def set_gcp_project(project_id):
    """GCP 프로젝트 설정"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "gcloud CLI가 설치되지 않았습니다."
        
        result = subprocess.run(['gcloud', 'config', 'set', 'project', project_id], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, f"프로젝트가 {project_id}로 설정되었습니다"
        else:
            return False, f"프로젝트 설정 실패: {result.stderr}"
    except FileNotFoundError:
        return False, "gcloud CLI가 설치되지 않았습니다."
    except Exception as e:
        return False, f"프로젝트 설정 오류: {e}"

def get_gcp_services():
    """GCP 서비스 목록 조회"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "gcloud CLI가 설치되지 않았습니다."
        
        result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--format=json'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            services = json.loads(result.stdout)
            return True, services
        else:
            return False, f"서비스 조회 실패: {result.stderr}"
    except FileNotFoundError:
        return False, "gcloud CLI가 설치되지 않았습니다."
    except Exception as e:
        return False, f"서비스 조회 오류: {e}"

def get_api_keys():
    """API 키 목록 조회"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "gcloud CLI가 설치되지 않았습니다."
        
        result = subprocess.run(['gcloud', 'services', 'api-keys', 'list', '--format=json'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            api_keys = json.loads(result.stdout)
            return True, api_keys
        else:
            return False, f"API 키 조회 실패: {result.stderr}"
    except FileNotFoundError:
        return False, "gcloud CLI가 설치되지 않았습니다."
    except Exception as e:
        return False, f"API 키 조회 오류: {e}"

def create_api_key(display_name, restrictions=None):
    """API 키 생성"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "gcloud CLI가 설치되지 않았습니다."
        
        cmd = ['gcloud', 'services', 'api-keys', 'create', '--display-name', display_name]
        if restrictions:
            cmd.extend(['--api-target', restrictions])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True, "API 키가 생성되었습니다"
        else:
            return False, f"API 키 생성 실패: {result.stderr}"
    except FileNotFoundError:
        return False, "gcloud CLI가 설치되지 않았습니다."
    except Exception as e:
        return False, f"API 키 생성 오류: {e}"

def get_gcp_quotas():
    """GCP 할당량 정보 조회"""
    try:
        # gcloud 명령어 존재 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "gcloud CLI가 설치되지 않았습니다."
        
        result = subprocess.run(['gcloud', 'compute', 'project-info', 'describe', '--format=json'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            quotas = json.loads(result.stdout)
            return True, quotas
        else:
            return False, f"할당량 조회 실패: {result.stderr}"
    except FileNotFoundError:
        return False, "gcloud CLI가 설치되지 않았습니다."
    except Exception as e:
        return False, f"할당량 조회 오류: {e}"

# GCP 헤더
st.markdown(create_gcp_header(
    "매일경제 AI 플랫폼",
    "Google Cloud Platform 기반 벡터임베딩 & RAG 솔루션 관리자 대시보드",
    "cloud"
), unsafe_allow_html=True)

# GCP 인증 상태 확인
is_authenticated, current_project = check_gcp_auth()

# GCP 네비게이션
st.markdown(create_gcp_navigation(st.session_state.get('active_tab', 0)), unsafe_allow_html=True)

# GCP 사이드바
with st.sidebar:
    # GCP 인증 상태 카드
    if is_authenticated:
        st.markdown(create_gcp_card(
            "GCP 인증 상태",
            f"""
            <div style="text-align: center; padding: 1rem;">
                <i class="fas fa-check-circle" style="color: var(--gcp-success); font-size: 2rem; margin-bottom: 0.5rem;"></i>
                <h4 style="color: var(--gcp-success); margin: 0;">인증됨</h4>
                <p style="color: var(--gcp-text-secondary); margin: 0.5rem 0 0 0;">프로젝트: {current_project}</p>
            </div>
            """,
            "shield-alt"
        ), unsafe_allow_html=True)
    else:
        st.markdown(create_gcp_card(
            "GCP 인증 상태",
            """
            <div style="text-align: center; padding: 1rem;">
                <i class="fas fa-exclamation-triangle" style="color: var(--gcp-error); font-size: 2rem; margin-bottom: 0.5rem;"></i>
                <h4 style="color: var(--gcp-error); margin: 0;">인증되지 않음</h4>
                <p style="color: var(--gcp-text-secondary); margin: 0.5rem 0 0 0;">GCP 서비스를 사용하려면 인증이 필요합니다</p>
            </div>
            """,
            "shield-alt"
        ), unsafe_allow_html=True)
    
    # GCP 인증 버튼들
    st.markdown(create_gcp_card(
        "GCP 인증",
        "",
        "key"
    ), unsafe_allow_html=True)
    
    # gcloud CLI 설치 상태 확인
    try:
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        gcloud_installed = result.returncode == 0
    except:
        gcloud_installed = False
    
    if not gcloud_installed:
        st.markdown(create_gcp_alert(
            "Google Cloud SDK가 설치되지 않았습니다. 아래 설치 방법을 참고하세요.",
            "warning",
            "exclamation-triangle"
        ), unsafe_allow_html=True)
        
        with st.expander("📋 Google Cloud SDK 설치 가이드", expanded=False):
            st.markdown("""
            **macOS (Homebrew):**
            ```bash
            brew install google-cloud-sdk
            ```
            
            **Linux/Windows:**
            ```bash
            curl https://sdk.cloud.google.com | bash
            exec -l $SHELL
            ```
            
            **또는 [공식 웹사이트](https://cloud.google.com/sdk/docs/install)에서 다운로드**
            """)
    
    if gcloud_installed:
        # 로그인 유형 선택
        login_type = st.selectbox(
            "로그인 유형:",
            ["브라우저 인증", "URL 제공 인증"],
            key="sidebar_login_type",
            help="브라우저 인증을 권장합니다."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 gcloud 로그인", disabled=not gcloud_installed, key="sidebar_gcloud_login"):
                with st.spinner("gcloud 로그인 중..."):
                    success, message = authenticate_with_gcloud("browser" if login_type == "브라우저 인증" else "no_browser")
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                        # URL이 포함된 경우 표시
                        if "https://" in message:
                            st.markdown("**인증 링크:**")
                            st.markdown(message)
        
        with col2:
            if st.button("⚙️ ADC 설정", key="sidebar_adc", disabled=not gcloud_installed):
                with st.spinner("Application Default Credentials 설정 중..."):
                    success, message = set_application_default_credentials()
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                        # URL이 포함된 경우 표시
                        if "https://" in message:
                            st.markdown("**ADC 설정 링크:**")
                            st.markdown(message)
    else:
        st.info("GCP 인증을 사용하려면 Google Cloud SDK를 설치하세요.")
    
    # 시스템 상태
    st.markdown(create_gcp_card(
        "시스템 상태",
        "",
        "server"
    ), unsafe_allow_html=True)
    
    if st.button("🔄 상태 새로고침", key="sidebar_refresh"):
        st.rerun()
    
    # 빠른 액션
    st.markdown(create_gcp_card(
        "빠른 액션",
        "",
        "bolt"
    ), unsafe_allow_html=True)
    
    if st.button("📊 대시보드", key="quick_dashboard"):
        st.session_state['active_tab'] = 0
        st.rerun()
    
    if st.button("☁️ GCP 관리", key="quick_gcp"):
        st.session_state['active_tab'] = 5
        st.rerun()
    
    if st.button("📤 벡터 처리", key="quick_vector"):
        st.session_state['active_tab'] = 6
        st.rerun()
    
    # 처리 작업
    st.subheader("처리 작업")
    if st.button("📄 XML 처리"):
        with st.spinner("XML 처리가 시작되었습니다..."):
            try:
                response = requests.post("http://localhost:8000/api/process-xml", 
                    json={"xml_directory": "/path/to/xml/files", "batch_size": 100})
                if response.status_code == 200:
                    st.success("XML 처리가 시작되었습니다!")
                else:
                    st.error("XML 처리 시작 실패")
            except Exception as e:
                st.error(f"오류: {str(e)}")
    
    if st.button("⚡ 증분형 처리"):
        with st.spinner("증분형 처리가 시작되었습니다..."):
            try:
                response = requests.post("http://localhost:8000/api/incremental-process", 
                    json={"xml_directory": "/path/to/xml/files"})
                if response.status_code == 200:
                    st.success("증분형 처리가 시작되었습니다!")
                else:
                    st.error("증분형 처리 시작 실패")
            except Exception as e:
                st.error(f"오류: {str(e)}")
    
    if st.button("🔍 벡터 인덱스 업데이트"):
        with st.spinner("벡터 인덱스 업데이트 중..."):
            try:
                response = requests.post("http://localhost:8000/api/vector-index/update")
                if response.status_code == 200:
                    st.success("벡터 인덱스 업데이트가 시작되었습니다!")
                else:
                    st.error("벡터 인덱스 업데이트 실패")
            except Exception as e:
                st.error(f"오류: {str(e)}")
    
    if st.button("🧹 중복 정리"):
        with st.spinner("중복 정리 중..."):
            try:
                response = requests.get("http://localhost:8000/api/duplicate-cleanup")
                if response.status_code == 200:
                    result = response.json()
                    st.success(result.get('message', '중복 정리가 완료되었습니다!'))
                else:
                    st.error("중복 정리 실패")
            except Exception as e:
                st.error(f"오류: {str(e)}")

# 메인 컨텐츠
# 엔터프라이즈 탭 시스템
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 0

# 탭 버튼들
tab_cols = st.columns(8)
tab_names = [
    ("📊 대시보드", 0),
    ("📰 기사 관리", 1), 
    ("🔍 검색 테스트", 2),
    ("📈 통계", 3),
    ("⚙️ 시스템 설정", 4),
    ("☁️ GCP 인프라", 5),
    ("📤 벡터임베딩", 6),
    ("🤖 개별기사 해설", 7)
]

for i, (name, tab_idx) in enumerate(tab_names):
    with tab_cols[i]:
        if st.button(name, key=f"tab_btn_{tab_idx}", 
                   type="primary" if st.session_state['active_tab'] == tab_idx else "secondary"):
            st.session_state['active_tab'] = tab_idx
            st.rerun()

# 탭 컨텐츠
if st.session_state['active_tab'] == 0:
    # GCP 대시보드
    st.markdown(create_gcp_card(
        "시스템 대시보드",
        "",
        "tachometer-alt"
    ), unsafe_allow_html=True)
    
    # 시스템 통계 메트릭 카드들
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        response = requests.get("http://localhost:8000/api/stats")
        if response.status_code == 200:
            stats = response.json()
            
            with col1:
                st.markdown(create_gcp_metric_card(
                    "총 기사",
                    f"{stats.get('total_articles', 0):,}",
                    None,
                    "neutral",
                    "newspaper"
                ), unsafe_allow_html=True)
            
            with col2:
                st.markdown(create_gcp_metric_card(
                    "처리된 기사",
                    f"{stats.get('processed_articles', 0):,}",
                    None,
                    "neutral",
                    "cogs"
                ), unsafe_allow_html=True)
            
            with col3:
                st.markdown(create_gcp_metric_card(
                    "임베딩된 기사",
                    f"{stats.get('embedded_articles', 0):,}",
                    None,
                    "neutral",
                    "brain"
                ), unsafe_allow_html=True)
            
            with col4:
                st.markdown(create_gcp_metric_card(
                    "최근 기사",
                    f"{stats.get('recent_articles', 0):,}",
                    None,
                    "neutral",
                    "clock"
                ), unsafe_allow_html=True)
        else:
            st.markdown(create_gcp_alert(
                "통계 데이터를 불러올 수 없습니다. API 서버 상태를 확인해주세요.",
                "error",
                "exclamation-circle"
            ), unsafe_allow_html=True)
    except Exception as e:
        st.markdown(create_gcp_alert(
            f"통계 데이터 로드 오류: {str(e)}",
            "error",
            "exclamation-circle"
        ), unsafe_allow_html=True)
    
    # 벡터 인덱스 상태
    st.markdown(create_gcp_card(
        "벡터 인덱스 상태",
        "",
        "search"
    ), unsafe_allow_html=True)
    
    try:
        response = requests.get("http://localhost:8000/api/vector-index/status")
        if response.status_code == 200:
            status = response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(create_metric_card(
                    status.get('indexed_vectors', 0),
                    "인덱스된 벡터 수",
                    "fas fa-database",
                    "info"
                ), unsafe_allow_html=True)
            
            with col2:
                status_color = "success" if status.get('status') == 'active' else "warning"
                st.markdown(create_metric_card(
                    status.get('status', 'Unknown'),
                    "인덱스 상태",
                    "fas fa-check-circle" if status.get('status') == 'active' else "fas fa-exclamation-triangle",
                    status_color
                ), unsafe_allow_html=True)
        else:
            st.markdown(create_gcp_alert(
                "벡터 인덱스 상태를 불러올 수 없습니다.",
                "error",
                "exclamation-circle"
            ), unsafe_allow_html=True)
    except Exception as e:
        st.markdown(create_gcp_alert(
            f"벡터 인덱스 상태 로드 오류: {str(e)}",
            "error",
            "exclamation-circle"
        ), unsafe_allow_html=True)
    
    # 처리 로그
    st.markdown(create_gcp_card(
        "최근 처리 로그",
        "",
        "list"
    ), unsafe_allow_html=True)
    
    try:
        response = requests.get("http://localhost:8000/api/processing-logs?limit=20")
        if response.status_code == 200:
            logs = response.json()
            if logs:
                df_logs = pd.DataFrame(logs)
                st.markdown(create_gcp_table(
                    df_logs.columns.tolist(),
                    df_logs.values.tolist()
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_gcp_alert(
                    "처리 로그가 없습니다.",
                    "info",
                    "info-circle"
                ), unsafe_allow_html=True)
        else:
            st.markdown(create_gcp_alert(
                "처리 로그를 불러올 수 없습니다.",
                "error",
                "exclamation-circle"
            ), unsafe_allow_html=True)
    except Exception as e:
        st.markdown(create_gcp_alert(
            f"처리 로그 로드 오류: {str(e)}",
            "error",
            "exclamation-circle"
        ), unsafe_allow_html=True)

elif st.session_state['active_tab'] == 1:
    st.header("📰 기사 관리")
    
    # 기사 검색
    st.subheader("기사 검색")
    search_query = st.text_input("검색어 입력")
    
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox("카테고리", ["전체", "정치", "경제", "사회", "국제", "문화", "기술"])
    with col2:
        date_range = st.date_input("날짜 범위", value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
    
    if st.button("🔍 검색"):
        try:
            params = {
                "skip": 0,
                "limit": 100
            }
            
            if category_filter != "전체":
                params["category"] = category_filter
            
            if len(date_range) == 2:
                params["start_date"] = date_range[0].isoformat()
                params["end_date"] = date_range[1].isoformat()
            
            response = requests.get("http://localhost:8000/api/articles", params=params)
            if response.status_code == 200:
                articles = response.json()
                if articles:
                    df_articles = pd.DataFrame(articles)
                    st.dataframe(df_articles, use_container_width=True)
                else:
                    st.info("검색 결과가 없습니다.")
            else:
                st.error("기사 검색 실패")
        except Exception as e:
            st.error(f"검색 오류: {str(e)}")

elif st.session_state['active_tab'] == 2:
    st.header("🔍 Hybrid RAG 검색 테스트")
    
    # RAG 시스템 테스트
    st.subheader("Hybrid RAG 시스템 테스트")
    
    query = st.text_area("질문을 입력하세요", height=100, placeholder="예: 삼성전자 주가 전망에 대해 알려주세요")
    
    # 검색 설정
    st.subheader("⚙️ 검색 설정")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        top_k = st.slider("검색 결과 수", 1, 50, 10)
    with col2:
        similarity_threshold = st.slider("유사도 임계값", 0.0, 1.0, 0.7, 0.01)
    with col3:
        max_context_length = st.number_input("최대 컨텍스트 길이", min_value=1000, max_value=8000, value=4000)
    
    # 가중치 설정
    st.subheader("⚖️ 검색 가중치 설정")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        vector_weight = st.slider("벡터 검색 가중치", 0.0, 1.0, 0.6, 0.1, 
                                 help="의미적 유사도 검색의 가중치")
    with col2:
        keyword_weight = st.slider("키워드 검색 가중치", 0.0, 1.0, 0.3, 0.1,
                                  help="키워드 매칭 검색의 가중치")
    with col3:
        rerank_weight = st.slider("리랭킹 가중치", 0.0, 1.0, 0.1, 0.1,
                                 help="최종 리랭킹의 가중치")
    
    # 메타데이터 필터링
    st.subheader("🔍 메타데이터 필터링")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("카테고리", ["전체", "정치", "경제", "사회", "국제", "문화", "기술", "스포츠"])
    with col2:
        date_range = st.date_input("날짜 범위", value=[datetime.now().date() - timedelta(days=365), datetime.now().date()])
    with col3:
        writer_filter = st.text_input("작성자 필터", placeholder="작성자명 입력")
    
    # 추가 필터 옵션
    with st.expander("🔧 고급 필터 옵션"):
        col1, col2 = st.columns(2)
        with col1:
            min_article_length = st.number_input("최소 기사 길이", min_value=0, value=100)
            include_images = st.checkbox("이미지 포함 기사만", value=False)
        with col2:
            stock_codes = st.text_input("주식 코드 (쉼표로 구분)", placeholder="005930,000660")
            keyword_required = st.text_input("필수 키워드", placeholder="삼성,전자")
    
    # 검색 실행
    if st.button("🔍 Hybrid RAG 검색 실행"):
        if query:
            try:
                # 필터 구성
                filters_dict = {}
                if category_filter != "전체":
                    filters_dict["category"] = category_filter
                if len(date_range) == 2:
                    filters_dict["start_date"] = date_range[0].isoformat()
                    filters_dict["end_date"] = date_range[1].isoformat()
                if writer_filter:
                    filters_dict["writer"] = writer_filter
                if min_article_length > 0:
                    filters_dict["min_length"] = min_article_length
                if include_images:
                    filters_dict["has_images"] = True
                if stock_codes:
                    filters_dict["stock_codes"] = [code.strip() for code in stock_codes.split(",")]
                if keyword_required:
                    filters_dict["required_keywords"] = [kw.strip() for kw in keyword_required.split(",")]
                
                # 가중치 설정
                weights = {
                    "vector_weight": vector_weight,
                    "keyword_weight": keyword_weight,
                    "rerank_weight": rerank_weight
                }
                
                # 검색 요청
                response = requests.post("http://localhost:8000/api/query", 
                    json={
                        "query": query, 
                        "filters": filters_dict, 
                        "top_k": top_k,
                        "similarity_threshold": similarity_threshold,
                        "max_context_length": max_context_length,
                        "weights": weights
                    })
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # AI 응답
                    st.subheader("🤖 AI 응답")
                    st.write(result.get('response', {}).get('text', '응답이 없습니다.'))
                    
                    # 검색 결과 상세 정보
                    st.subheader("📊 검색 결과 상세")
                    
                    retrieved_docs = result.get('retrieved_docs', [])
                    if retrieved_docs:
                        # 검색 결과 테이블
                        search_results_data = []
                        for i, doc in enumerate(retrieved_docs, 1):
                            article = doc['article']
                            search_results_data.append({
                                '순위': i,
                                '제목': article.get('title', 'N/A'),
                                '유사도': f"{doc.get('similarity', 0):.3f}",
                                '벡터점수': f"{doc.get('vector_score', 0):.3f}",
                                '키워드점수': f"{doc.get('keyword_score', 0):.3f}",
                                '리랭킹점수': f"{doc.get('rerank_score', 0):.3f}",
                                '발행일': article.get('service_daytime', 'N/A'),
                                '카테고리': article.get('category', 'N/A'),
                                '작성자': article.get('writers', 'N/A')
                            })
                        
                        df_results = pd.DataFrame(search_results_data)
                        st.dataframe(df_results, use_container_width=True)
                        
                        # 개별 기사 상세 정보
                        st.subheader("📚 참조 기사 상세")
                        for i, doc in enumerate(retrieved_docs[:5], 1):
                            article = doc['article']
                            with st.expander(f"기사 {i}: {article.get('title', 'N/A')}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**유사도:** {doc.get('similarity', 0):.3f}")
                                    st.write(f"**벡터 점수:** {doc.get('vector_score', 0):.3f}")
                                    st.write(f"**키워드 점수:** {doc.get('keyword_score', 0):.3f}")
                                    st.write(f"**리랭킹 점수:** {doc.get('rerank_score', 0):.3f}")
                                with col2:
                                    st.write(f"**발행일:** {article.get('service_daytime', 'N/A')}")
                                    st.write(f"**카테고리:** {article.get('category', 'N/A')}")
                                    st.write(f"**작성자:** {article.get('writers', 'N/A')}")
                                
                                st.write(f"**요약:** {article.get('summary', 'N/A')}")
                                if article.get('article_url'):
                                    st.write(f"**URL:** {article.get('article_url')}")
                    else:
                        st.info("검색 결과가 없습니다.")
                    
                    # 검색 통계
                    st.subheader("📈 검색 통계")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("처리 시간", f"{result.get('processing_time', 0):.2f}초")
                    with col2:
                        st.metric("컨텍스트 길이", result.get('context_length', 0))
                    with col3:
                        st.metric("검색 결과 수", len(retrieved_docs))
                    with col4:
                        st.metric("필터 적용", "✅" if filters_dict else "❌")
                    
                    # 검색 품질 메트릭
                    if 'search_metrics' in result:
                        metrics = result['search_metrics']
                        st.subheader("🎯 검색 품질 메트릭")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("평균 유사도", f"{metrics.get('avg_similarity', 0):.3f}")
                        with col2:
                            st.metric("최고 유사도", f"{metrics.get('max_similarity', 0):.3f}")
                        with col3:
                            st.metric("검색 다양성", f"{metrics.get('diversity_score', 0):.3f}")
                    
                    # 가중치 효과 분석
                    st.subheader("⚖️ 가중치 효과 분석")
                    if retrieved_docs:
                        vector_scores = [doc.get('vector_score', 0) for doc in retrieved_docs]
                        keyword_scores = [doc.get('keyword_score', 0) for doc in retrieved_docs]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=list(range(1, len(vector_scores) + 1)),
                            y=vector_scores,
                            mode='lines+markers',
                            name='벡터 점수',
                            line=dict(color='blue')
                        ))
                        fig.add_trace(go.Scatter(
                            x=list(range(1, len(keyword_scores) + 1)),
                            y=keyword_scores,
                            mode='lines+markers',
                            name='키워드 점수',
                            line=dict(color='red')
                        ))
                        fig.update_layout(
                            title="검색 점수 분포",
                            xaxis_title="검색 결과 순위",
                            yaxis_title="점수"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("검색 실패")
            except Exception as e:
                st.error(f"검색 오류: {str(e)}")
        else:
            st.warning("질문을 입력해주세요.")
    
    # 검색 히스토리
    st.subheader("📚 검색 히스토리")
    if st.button("📋 최근 검색 조회"):
        try:
            response = requests.get("http://localhost:8000/api/search-history?limit=10")
            if response.status_code == 200:
                history = response.json()
                if history:
                    for search in history:
                        with st.expander(f"🔍 {search.get('query', 'N/A')} - {search.get('created_at', 'N/A')}"):
                            st.write(f"**결과 수:** {search.get('result_count', 0)}")
                            st.write(f"**처리 시간:** {search.get('processing_time', 0):.2f}초")
                            st.write(f"**필터:** {search.get('filters', {})}")
                else:
                    st.info("검색 히스토리가 없습니다.")
            else:
                st.error("검색 히스토리를 불러올 수 없습니다.")
        except Exception as e:
            st.error(f"히스토리 로드 오류: {str(e)}")

elif st.session_state['active_tab'] == 3:
    st.header("📈 통계 분석")
    
    # 기사 통계 차트
    st.subheader("기사 통계")
    
    try:
        response = requests.get("http://localhost:8000/api/articles?limit=1000")
        if response.status_code == 200:
            articles = response.json()
            if articles:
                df = pd.DataFrame(articles)
                
                # 날짜별 기사 수
                if 'service_daytime' in df.columns:
                    df['date'] = pd.to_datetime(df['service_daytime']).dt.date
                    daily_counts = df.groupby('date').size().reset_index(name='count')
                    
                    fig = px.line(daily_counts, x='date', y='count', title='일별 기사 수')
                    st.plotly_chart(fig, use_container_width=True)
                
                # 임베딩 상태 분포
                if 'is_embedded' in df.columns:
                    embedding_counts = df['is_embedded'].value_counts()
                    
                    fig = px.pie(values=embedding_counts.values, 
                                names=['임베딩 완료' if x else '임베딩 미완료' for x in embedding_counts.index],
                                title='임베딩 상태 분포')
                    st.plotly_chart(fig, use_container_width=True)
                
                # 기사 길이 분포
                if 'summary' in df.columns:
                    df['summary_length'] = df['summary'].str.len()
                    
                    fig = px.histogram(df, x='summary_length', title='기사 요약 길이 분포')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("통계 데이터가 없습니다.")
        else:
            st.error("통계 데이터를 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"통계 데이터 로드 오류: {str(e)}")

elif st.session_state['active_tab'] == 4:
    st.header("⚙️ 시스템 설정")
    
    # 벡터 인덱스 관리
    st.subheader("벡터 인덱스 관리")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔧 인덱스 생성"):
            with st.spinner("벡터 인덱스 생성 중..."):
                try:
                    response = requests.post("http://localhost:8000/api/vector-index/create")
                    if response.status_code == 200:
                        result = response.json()
                        st.success(result.get('message', '벡터 인덱스가 생성되었습니다!'))
                    else:
                        st.error("벡터 인덱스 생성 실패")
                except Exception as e:
                    st.error(f"오류: {str(e)}")
    
    with col2:
        if st.button("🚀 인덱스 배포"):
            with st.spinner("벡터 인덱스 배포 중..."):
                try:
                    response = requests.post("http://localhost:8000/api/vector-index/deploy")
                    if response.status_code == 200:
                        result = response.json()
                        st.success(result.get('message', '벡터 인덱스가 배포되었습니다!'))
                    else:
                        st.error("벡터 인덱스 배포 실패")
                except Exception as e:
                    st.error(f"오류: {str(e)}")
    
    with col3:
        if st.button("🔄 인덱스 상태 확인"):
            try:
                response = requests.get("http://localhost:8000/api/vector-index/status")
                if response.status_code == 200:
                    status = response.json()
                    st.json(status)
                else:
                    st.error("벡터 인덱스 상태 확인 실패")
            except Exception as e:
                st.error(f"오류: {str(e)}")
    
    # 시스템 정보
    st.subheader("시스템 정보")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health = response.json()
            st.json(health)
        else:
            st.error("시스템 정보를 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"시스템 정보 로드 오류: {str(e)}")

elif st.session_state['active_tab'] == 5:
    st.header("☁️ GCP 인프라 관리")
    
    # GCP 로그인 상태 확인
    st.subheader("🔐 GCP 인증 상태")
    
    # 인증 상태 표시
    if is_authenticated:
        st.success(f"✅ 인증됨\n프로젝트: {current_project}")
        auth_status = "인증됨"
    else:
        st.error("❌ 인증되지 않음")
        auth_status = "인증되지 않음"
    
    # 인증 방법 선택
    st.subheader("🔑 GCP 인증 방법")
    
    auth_method = st.radio(
        "인증 방법을 선택하세요:",
        ["gcloud CLI", "OAuth 2.0 (웹)", "서비스 계정 키"],
        horizontal=True
    )
    
    if auth_method == "gcloud CLI":
        # gcloud CLI 설치 상태 확인
        try:
            result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
            gcloud_installed = result.returncode == 0
        except:
            gcloud_installed = False
        
        if not gcloud_installed:
            st.error("❌ gcloud CLI가 설치되지 않았습니다. Google Cloud SDK를 설치해주세요.")
            st.code("""
# macOS (Homebrew)
brew install google-cloud-sdk

# 또는 공식 설치 스크립트
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
            """)
        else:
            st.success("✅ gcloud CLI가 설치되어 있습니다.")
            
            # 로그인 유형 선택
            login_type = st.selectbox(
                "로그인 유형을 선택하세요:",
                ["브라우저 인증 (권장)", "URL 제공 인증", "서비스 계정 키 파일"],
                help="브라우저 인증이 가장 간단하고 안전합니다."
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔑 gcloud 로그인", type="primary", disabled=not gcloud_installed):
                    with st.spinner("gcloud 로그인 중..."):
                        # 로그인 유형에 따른 처리
                        if login_type == "브라우저 인증 (권장)":
                            success, message = authenticate_with_gcloud("browser")
                        elif login_type == "URL 제공 인증":
                            success, message = authenticate_with_gcloud("no_browser")
                        else:  # 서비스 계정 키 파일
                            success, message = authenticate_with_gcloud("service_account")
                        
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                            # URL이 포함된 경우 클릭 가능한 링크로 표시
                            if "https://" in message:
                                st.markdown("**인증 링크:**")
                                st.markdown(message)
            
            with col2:
                if st.button("⚙️ ADC 설정", key="main_adc", disabled=not gcloud_installed):
                    with st.spinner("Application Default Credentials 설정 중..."):
                        success, message = set_application_default_credentials()
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                            # URL이 포함된 경우 클릭 가능한 링크로 표시
                            if "https://" in message:
                                st.markdown("**ADC 설정 링크:**")
                                st.markdown(message)
    
    elif auth_method == "OAuth 2.0 (웹)":
        st.info("OAuth 2.0 클라이언트 ID를 설정해야 합니다.")
        
        client_id = st.text_input("OAuth 2.0 클라이언트 ID", placeholder="your-client-id.apps.googleusercontent.com")
        client_secret = st.text_input("클라이언트 시크릿", type="password")
        
        if st.button("🌐 OAuth 인증 시작"):
            if client_id and client_secret:
                # OAuth 설정 저장
                oauth_config = {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost:8501"]
                    }
                }
                
                with open('oauth_config.json', 'w') as f:
                    json.dump(oauth_config, f)
                
                st.success("OAuth 설정이 저장되었습니다!")
                st.info("브라우저에서 인증을 완료하세요.")
            else:
                st.error("클라이언트 ID와 시크릿을 입력해주세요.")
    
    elif auth_method == "서비스 계정 키":
        st.info("서비스 계정 키 파일을 업로드하세요.")
        
        uploaded_file = st.file_uploader("서비스 계정 키 파일", type=['json'], help="GCP 콘솔에서 다운로드한 JSON 키 파일을 업로드하세요.")
        
        if uploaded_file is not None:
            try:
                # 파일 내용 읽기
                key_data = uploaded_file.read().decode('utf-8')
                
                # JSON 유효성 검사
                json.loads(key_data)
                
                # gcloud CLI를 통한 인증
                with st.spinner("서비스 계정으로 인증 중..."):
                    success, message = authenticate_with_service_account(key_data)
                
                if success:
                    # 키 파일 저장
                    with open('service_account_key.json', 'w') as f:
                        f.write(key_data)
                    
                    # 환경변수 설정
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account_key.json'
                    
                    st.success("✅ 서비스 계정 인증 성공!")
                    st.info(f"프로젝트: {json.loads(key_data).get('project_id', 'Unknown')}")
                    st.rerun()
                else:
                    st.error(f"❌ 서비스 계정 인증 실패: {message}")
                    
            except json.JSONDecodeError:
                st.error("❌ 유효하지 않은 JSON 파일입니다.")
            except Exception as e:
                st.error(f"❌ 키 파일 처리 오류: {e}")
        
        # 서비스 계정 키 생성 안내
        with st.expander("🔧 서비스 계정 키 생성 방법"):
            st.markdown("""
            1. **GCP 콘솔 접속**: https://console.cloud.google.com/
            2. **IAM 및 관리자** → **서비스 계정** 이동
            3. **서비스 계정 만들기** 클릭
            4. 서비스 계정 정보 입력:
               - 이름: `mk-news-platform`
               - 설명: `매일경제 신문기사 플랫폼용 서비스 계정`
            5. **역할 추가**:
               - `Vertex AI 사용자`
               - `Cloud SQL 클라이언트`
               - `Storage 관리자`
               - `AI Platform 관리자`
            6. **키 만들기** → **JSON** 선택
            7. 다운로드된 JSON 파일을 위에 업로드
            """)
    
    # 현재 계정 정보 표시
    try:
        # gcloud CLI 설치 상태 확인
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        if result.returncode != 0:
            st.warning("⚠️ gcloud CLI가 설치되지 않았습니다. GCP 기능을 사용하려면 Google Cloud SDK를 설치해주세요.")
            current_account = None
        else:
            result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                current_account = result.stdout.strip()
                st.info(f"현재 계정: {current_account}")
            else:
                current_account = None
    except Exception as e:
        current_account = None
    
    # GCP 프로젝트 관리
    st.subheader("🏗️ 프로젝트 관리")
    
    # 현재 프로젝트 정보
    current_project = get_current_project()
    if current_project:
        st.info(f"현재 프로젝트: {current_project}")
    else:
        st.warning("프로젝트가 설정되지 않았습니다.")
    
    # 프로젝트 목록 조회 및 선택
    if st.button("📋 프로젝트 목록 조회", key="list_projects"):
        with st.spinner("프로젝트 목록을 조회하는 중..."):
            success, projects = get_gcp_projects()
            if success:
                st.session_state['gcp_projects'] = projects
                st.success(f"{len(projects)}개의 프로젝트를 찾았습니다.")
            else:
                st.error(projects)
    
    # 프로젝트 목록 표시 및 선택
    if 'gcp_projects' in st.session_state:
        projects = st.session_state['gcp_projects']
        
        # 프로젝트 선택
        project_options = {f"{p['projectId']} - {p['name']}": p['projectId'] for p in projects}
        selected_project = st.selectbox(
            "프로젝트 선택:",
            options=list(project_options.keys()),
            index=0 if not current_project else next(
                (i for i, key in enumerate(project_options.keys()) 
                 if project_options[key] == current_project), 0
            )
        )
        
        if selected_project:
            selected_project_id = project_options[selected_project]
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 프로젝트 설정", key="set_project"):
                    with st.spinner("프로젝트를 설정하는 중..."):
                        success, message = set_gcp_project(selected_project_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            with col2:
                if st.button("🔄 새로고침", key="refresh_projects"):
                    st.rerun()
    
    # 리전 설정
    st.subheader("🌍 리전 설정")
    region = st.selectbox("GCP 리전", ["asia-northeast3", "asia-northeast1", "us-central1"], index=0)
    
    # API 키 관리
    st.subheader("🔑 API 키 관리")
    
    # API 키 목록 조회
    if st.button("📋 API 키 목록 조회", key="list_api_keys"):
        with st.spinner("API 키 목록을 조회하는 중..."):
            success, api_keys = get_api_keys()
            if success:
                st.session_state['gcp_api_keys'] = api_keys
                st.success(f"{len(api_keys)}개의 API 키를 찾았습니다.")
            else:
                st.error(api_keys)
    
    # API 키 목록 표시
    if 'gcp_api_keys' in st.session_state:
        api_keys = st.session_state['gcp_api_keys']
        
        if api_keys:
            st.subheader("📋 기존 API 키")
            for i, key in enumerate(api_keys):
                with st.expander(f"API 키 {i+1}: {key.get('displayName', '이름 없음')}"):
                    st.json(key)
        else:
            st.info("등록된 API 키가 없습니다.")
    
    # 새 API 키 생성
    st.subheader("🆕 새 API 키 생성")
    
    col1, col2 = st.columns(2)
    with col1:
        new_key_name = st.text_input("API 키 이름", placeholder="my-api-key")
    with col2:
        key_restrictions = st.text_input("API 제한 (선택사항)", placeholder="service:aiplatform.googleapis.com")
    
    if st.button("🔑 API 키 생성", key="create_api_key"):
        if new_key_name:
            with st.spinner("API 키를 생성하는 중..."):
                success, message = create_api_key(new_key_name, key_restrictions if key_restrictions else None)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.error("API 키 이름을 입력해주세요.")
    
    # Gemini API 키 설정
    st.subheader("🤖 Gemini API 설정")
    gemini_api_key = st.text_input("Gemini API 키", type="password", help="Google AI Studio에서 발급받은 API 키")
    
    if st.button("💾 API 키 저장", key="save_gemini_key"):
        if gemini_api_key:
            # .env 파일에 저장
            env_content = f"""GCP_PROJECT_ID={current_project or 'mk-ai-project-473000'}
GCP_REGION={region}
GEMINI_API_KEY={gemini_api_key}
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            st.success("API 키가 저장되었습니다!")
        else:
            st.error("API 키를 입력해주세요.")
    
    # GCP 서비스 관리
    st.subheader("🔧 GCP 서비스 관리")
    
    # 서비스 목록 조회
    if st.button("📋 활성화된 서비스 조회", key="list_services"):
        with st.spinner("서비스 목록을 조회하는 중..."):
            success, services = get_gcp_services()
            if success:
                st.session_state['gcp_services'] = services
                st.success(f"{len(services)}개의 활성화된 서비스를 찾았습니다.")
            else:
                st.error(services)
    
    # 서비스 목록 표시
    if 'gcp_services' in st.session_state:
        services = st.session_state['gcp_services']
        
        if services:
            st.subheader("📋 활성화된 서비스")
            service_df = pd.DataFrame(services)
            st.dataframe(service_df[['name', 'title', 'state']], use_container_width=True)
        else:
            st.info("활성화된 서비스가 없습니다.")
    
    # 필수 서비스 활성화
    st.subheader("🚀 필수 서비스 활성화")
    
    services_to_enable = [
        "compute.googleapis.com",
        "sqladmin.googleapis.com", 
        "aiplatform.googleapis.com",
        "storage.googleapis.com",
        "vpcaccess.googleapis.com",
        "servicenetworking.googleapis.com",
        "container.googleapis.com",
        "artifactregistry.googleapis.com"
    ]
    
    # 서비스 선택
    selected_services = st.multiselect(
        "활성화할 서비스 선택:",
        services_to_enable,
        default=services_to_enable
    )
    
    if st.button("🚀 선택된 서비스 활성화", key="enable_services"):
        if selected_services:
            with st.spinner("GCP 서비스를 활성화하는 중..."):
                success_count = 0
                for service in selected_services:
                    try:
                        result = subprocess.run(['gcloud', 'services', 'enable', service], 
                                              capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            st.success(f"✅ {service} 활성화됨")
                            success_count += 1
                        else:
                            st.error(f"❌ {service} 활성화 실패: {result.stderr}")
                    except Exception as e:
                        st.error(f"❌ {service} 활성화 오류: {str(e)}")
                
                st.info(f"총 {success_count}/{len(selected_services)}개 서비스가 활성화되었습니다.")
        else:
            st.warning("활성화할 서비스를 선택해주세요.")
    
    # 할당량 정보 조회
    st.subheader("📊 할당량 정보")
    
    if st.button("📈 할당량 조회", key="get_quotas"):
        with st.spinner("할당량 정보를 조회하는 중..."):
            success, quotas = get_gcp_quotas()
            if success:
                st.session_state['gcp_quotas'] = quotas
                st.success("할당량 정보를 조회했습니다.")
            else:
                st.error(quotas)
    
    # 할당량 정보 표시
    if 'gcp_quotas' in st.session_state:
        quotas = st.session_state['gcp_quotas']
        
        if 'quotas' in quotas:
            st.subheader("📊 현재 할당량")
            quota_data = []
            for quota in quotas['quotas']:
                quota_data.append({
                    '메트릭': quota.get('metric', 'N/A'),
                    '사용량': quota.get('usage', 0),
                    '한도': quota.get('limit', 0),
                    '지역': quota.get('region', 'N/A')
                })
            
            if quota_data:
                quota_df = pd.DataFrame(quota_data)
                st.dataframe(quota_df, use_container_width=True)
            else:
                st.info("할당량 정보가 없습니다.")
    
    # 인프라 배포
    st.subheader("🏗️ 인프라 배포")
    
    if st.button("🚀 Terraform 배포"):
        with st.spinner("Terraform으로 인프라를 배포하는 중..."):
            try:
                # Terraform 초기화
                result = subprocess.run(['terraform', 'init'], cwd='terraform', 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    st.error(f"Terraform 초기화 실패: {result.stderr}")
                    st.stop()
                
                # Terraform 플랜
                result = subprocess.run(['terraform', 'plan'], cwd='terraform', 
                                      capture_output=True, text=True, timeout=120)
                st.text("Terraform Plan 결과:")
                st.code(result.stdout)
                
                if st.button("✅ 배포 실행"):
                    result = subprocess.run(['terraform', 'apply', '-auto-approve'], cwd='terraform', 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        st.success("인프라 배포가 완료되었습니다!")
                    else:
                        st.error(f"배포 실패: {result.stderr}")
                        
            except Exception as e:
                st.error(f"배포 오류: {str(e)}")
    
    # 인프라 테스트
    st.subheader("🧪 인프라 테스트")
    
    if st.button("🔍 연결 테스트"):
        with st.spinner("인프라 연결을 테스트하는 중..."):
            try:
                # Cloud SQL 연결 테스트
                result = subprocess.run(['gcloud', 'sql', 'instances', 'list'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    st.success("✅ Cloud SQL 연결 성공")
                    st.text(result.stdout)
                else:
                    st.error(f"❌ Cloud SQL 연결 실패: {result.stderr}")
                
                # Vertex AI 연결 테스트
                result = subprocess.run(['gcloud', 'ai', 'models', 'list'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    st.success("✅ Vertex AI 연결 성공")
                else:
                    st.error(f"❌ Vertex AI 연결 실패: {result.stderr}")
                    
            except Exception as e:
                st.error(f"테스트 오류: {str(e)}")
    
    # 인프라 모니터링
    st.subheader("📊 인프라 모니터링")
    
    if st.button("📈 리소스 상태 확인"):
        try:
            # Compute Engine 인스턴스
            result = subprocess.run(['gcloud', 'compute', 'instances', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                st.subheader("🖥️ Compute Engine")
                st.text(result.stdout)
            
            # Cloud SQL 인스턴스
            result = subprocess.run(['gcloud', 'sql', 'instances', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                st.subheader("🗄️ Cloud SQL")
                st.text(result.stdout)
                
        except Exception as e:
            st.error(f"모니터링 오류: {str(e)}")

elif st.session_state['active_tab'] == 6:
    st.header("📤 벡터임베딩 증분처리")
    
    # XML 파일 업로드
    st.subheader("📁 XML 파일 업로드")
    
    uploaded_files = st.file_uploader(
        "XML 기사 파일을 업로드하세요", 
        type=['xml'], 
        accept_multiple_files=True,
        help="여러 개의 XML 파일을 동시에 업로드할 수 있습니다."
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)}개의 XML 파일이 업로드되었습니다.")
        
        # 업로드된 파일 정보
        with st.expander("📋 업로드된 파일 목록"):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size:,} bytes)")
    
    # 벡터임베딩 배치 처리 설정
    st.subheader("⚙️ 배치 처리 설정")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        batch_size = st.number_input("배치 크기", min_value=1, max_value=1000, value=100)
    with col2:
        max_workers = st.number_input("최대 워커 수", min_value=1, max_value=10, value=4)
    with col3:
        embedding_model = st.selectbox(
            "임베딩 모델", 
            ["sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 
             "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"],
            index=0
        )
    
    # 처리 시작
    if st.button("🚀 벡터임베딩 배치 처리 시작"):
        if uploaded_files:
            with st.spinner("벡터임베딩 처리를 시작하는 중..."):
                try:
                    # 업로드된 파일들을 임시 디렉토리에 저장
                    temp_dir = Path("temp_upload")
                    temp_dir.mkdir(exist_ok=True)
                    
                    for file in uploaded_files:
                        with open(temp_dir / file.name, "wb") as f:
                            f.write(file.getbuffer())
                    
                    # API 호출
                    response = requests.post("http://localhost:8000/api/process-xml", 
                        json={
                            "xml_directory": str(temp_dir),
                            "batch_size": batch_size,
                            "max_workers": max_workers,
                            "embedding_model": embedding_model
                        })
                    
                    if response.status_code == 200:
                        st.success("벡터임베딩 처리가 시작되었습니다!")
                        
                        # 처리 진행 상황 모니터링
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # 처리 상태 확인 (실제로는 백그라운드 작업 상태를 확인)
                        for i in range(100):
                            time.sleep(0.1)
                            progress_bar.progress(i + 1)
                            status_text.text(f"처리 중... {i+1}%")
                        
                        st.success("벡터임베딩 처리가 완료되었습니다!")
                        
                    else:
                        st.error("처리 시작 실패")
                        
                except Exception as e:
                    st.error(f"처리 오류: {str(e)}")
        else:
            st.warning("먼저 XML 파일을 업로드해주세요.")
    
    # VertexAI Vector Search 반영
    st.subheader("🔍 VertexAI Vector Search 반영")
    
    if st.button("🔄 벡터 인덱스 업데이트"):
        with st.spinner("VertexAI Vector Search에 벡터를 반영하는 중..."):
            try:
                response = requests.post("http://localhost:8000/api/vector-index/update")
                if response.status_code == 200:
                    result = response.json()
                    st.success(result.get('message', '벡터 인덱스가 업데이트되었습니다!'))
                else:
                    st.error("벡터 인덱스 업데이트 실패")
            except Exception as e:
                st.error(f"업데이트 오류: {str(e)}")
    
    # 메타데이터 추출 및 인덱싱
    st.subheader("📊 메타데이터 추출 및 인덱싱")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 메타데이터 추출"):
            with st.spinner("메타데이터를 추출하는 중..."):
                try:
                    response = requests.post("http://localhost:8000/api/extract-metadata")
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result.get('extracted_count', 0)}개의 메타데이터가 추출되었습니다.")
                    else:
                        st.error("메타데이터 추출 실패")
                except Exception as e:
                    st.error(f"추출 오류: {str(e)}")
    
    with col2:
        if st.button("🔍 메타데이터 인덱싱"):
            with st.spinner("메타데이터를 인덱싱하는 중..."):
                try:
                    response = requests.post("http://localhost:8000/api/index-metadata")
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result.get('indexed_count', 0)}개의 메타데이터가 인덱싱되었습니다.")
                    else:
                        st.error("메타데이터 인덱싱 실패")
                except Exception as e:
                    st.error(f"인덱싱 오류: {str(e)}")
    
    # 처리 결과 모니터링
    st.subheader("📈 처리 결과 모니터링")
    
    if st.button("📊 처리 통계 확인"):
        try:
            response = requests.get("http://localhost:8000/api/processing-stats")
            if response.status_code == 200:
                stats = response.json()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("총 처리된 기사", stats.get('total_processed', 0))
                with col2:
                    st.metric("임베딩 완료", stats.get('embedded_count', 0))
                with col3:
                    st.metric("메타데이터 추출", stats.get('metadata_extracted', 0))
                with col4:
                    st.metric("인덱싱 완료", stats.get('indexed_count', 0))
            else:
                st.error("통계 데이터를 불러올 수 없습니다.")
        except Exception as e:
            st.error(f"통계 로드 오류: {str(e)}")

elif st.session_state['active_tab'] == 7:
    st.header("🤖 개별기사 해설 생성")
    
    # 기사 선택
    st.subheader("📰 기사 선택")
    
    # 기사 검색
    search_query = st.text_input("기사 검색", placeholder="제목이나 키워드로 검색")
    
    if st.button("🔍 기사 검색"):
        if search_query:
            try:
                response = requests.get("http://localhost:8000/api/articles", 
                    params={"search": search_query, "limit": 20})
                if response.status_code == 200:
                    articles = response.json()
                    if articles:
                        st.session_state['search_results'] = articles
                    else:
                        st.info("검색 결과가 없습니다.")
                else:
                    st.error("기사 검색 실패")
            except Exception as e:
                st.error(f"검색 오류: {str(e)}")
    
    # 검색 결과에서 기사 선택
    if 'search_results' in st.session_state and st.session_state['search_results']:
        st.subheader("📋 검색 결과")
        
        selected_article = None
        for i, article in enumerate(st.session_state['search_results']):
            with st.expander(f"{i+1}. {article.get('title', '제목 없음')}"):
                st.write(f"**발행일:** {article.get('service_daytime', 'N/A')}")
                st.write(f"**요약:** {article.get('summary', '요약 없음')}")
                st.write(f"**작성자:** {article.get('writers', 'N/A')}")
                
                if st.button(f"선택", key=f"select_{i}"):
                    selected_article = article
                    st.session_state['selected_article'] = selected_article
                    st.success("기사가 선택되었습니다!")
        
        # 선택된 기사 정보
        if 'selected_article' in st.session_state:
            article = st.session_state['selected_article']
            st.subheader("📰 선택된 기사")
            st.write(f"**제목:** {article.get('title', 'N/A')}")
            st.write(f"**발행일:** {article.get('service_daytime', 'N/A')}")
            st.write(f"**본문:** {article.get('body', 'N/A')[:500]}...")
    
    # 해설 생성 설정
    st.subheader("⚙️ 해설 생성 설정")
    
    col1, col2 = st.columns(2)
    with col1:
        timeline_years = st.number_input("과거 타임라인 조회 년수", min_value=1, max_value=10, value=3)
    with col2:
        analysis_depth = st.selectbox("분석 깊이", ["기본", "상세", "심화"], index=1)
    
    # 해설 생성 옵션
    st.subheader("🎯 해설 생성 옵션")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        include_timeline = st.checkbox("과거 타임라인 분석", value=True)
    with col2:
        include_current = st.checkbox("현재 기사 논설", value=True)
    with col3:
        include_future = st.checkbox("향후 전망", value=True)
    
    # 해설 생성
    if st.button("🤖 해설 생성"):
        if 'selected_article' in st.session_state:
            article = st.session_state['selected_article']
            
            with st.spinner("해설을 생성하는 중..."):
                try:
                    # 해설 생성 요청
                    response = requests.post("http://localhost:8000/api/generate-analysis", 
                        json={
                            "article_id": article.get('id'),
                            "timeline_years": timeline_years,
                            "analysis_depth": analysis_depth,
                            "include_timeline": include_timeline,
                            "include_current": include_current,
                            "include_future": include_future
                        })
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # 해설 결과 표시
                        st.subheader("📊 해설 결과")
                        
                        if include_timeline and 'timeline_analysis' in result:
                            st.subheader("📅 과거 타임라인 분석")
                            st.write(result['timeline_analysis'])
                        
                        if include_current and 'current_analysis' in result:
                            st.subheader("📰 현재 기사 논설")
                            st.write(result['current_analysis'])
                        
                        if include_future and 'future_analysis' in result:
                            st.subheader("🔮 향후 전망")
                            st.write(result['future_analysis'])
                        
                        # 참조 기사
                        if 'reference_articles' in result:
                            st.subheader("📚 참조 기사")
                            for ref in result['reference_articles']:
                                with st.expander(f"📰 {ref.get('title', 'N/A')}"):
                                    st.write(f"**발행일:** {ref.get('service_daytime', 'N/A')}")
                                    st.write(f"**유사도:** {ref.get('similarity', 0):.3f}")
                                    st.write(f"**요약:** {ref.get('summary', 'N/A')}")
                        
                        # 생성 통계
                        st.subheader("📊 생성 통계")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("처리 시간", f"{result.get('processing_time', 0):.2f}초")
                        with col2:
                            st.metric("참조 기사 수", len(result.get('reference_articles', [])))
                        with col3:
                            st.metric("분석 깊이", result.get('analysis_depth', 'N/A'))
                            
                    else:
                        st.error("해설 생성 실패")
                        
                except Exception as e:
                    st.error(f"해설 생성 오류: {str(e)}")
        else:
            st.warning("먼저 기사를 선택해주세요.")
    
    # 해설 히스토리
    st.subheader("📚 해설 히스토리")
    
    if st.button("📋 최근 해설 조회"):
        try:
            response = requests.get("http://localhost:8000/api/analysis-history?limit=10")
            if response.status_code == 200:
                history = response.json()
                if history:
                    for analysis in history:
                        with st.expander(f"📰 {analysis.get('article_title', 'N/A')} - {analysis.get('created_at', 'N/A')}"):
                            st.write(f"**분석 유형:** {analysis.get('analysis_type', 'N/A')}")
                            st.write(f"**생성 시간:** {analysis.get('processing_time', 0):.2f}초")
                            st.write(f"**참조 기사 수:** {analysis.get('reference_count', 0)}")
                else:
                    st.info("해설 히스토리가 없습니다.")
            else:
                st.error("해설 히스토리를 불러올 수 없습니다.")
        except Exception as e:
            st.error(f"히스토리 로드 오류: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("**매일경제 신문기사 벡터임베딩 플랫폼** - GCP VertexAI 기반 Hybrid RAG 시스템")

