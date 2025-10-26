"""
Google Cloud Platform 스타일 테마 함수들
Material Design 3 기반의 GCP 디자인 시스템
"""

def create_gcp_header(title, subtitle, icon="cloud"):
    """GCP 스타일 헤더 생성"""
    return f"""
    <div class="gcp-header">
        <div class="gcp-header-content">
            <div>
                <h1 class="gcp-header-title">
                    <i class="fas fa-{icon}" style="font-size: 2rem;"></i>
                    {title}
                </h1>
                <p class="gcp-header-subtitle">{subtitle}</p>
            </div>
            <div class="gcp-header-actions">
                <button class="gcp-btn gcp-btn-outline" onclick="toggleTheme()">
                    <i class="fas fa-moon"></i>
                    다크모드
                </button>
                <button class="gcp-btn gcp-btn-primary" onclick="refreshPage()">
                    <i class="fas fa-sync-alt"></i>
                    새로고침
                </button>
            </div>
        </div>
    </div>
    <script>
        function toggleTheme() {{
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }}
        
        function refreshPage() {{
            window.location.reload();
        }}
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
    """

def create_gcp_navigation(active_tab=0):
    """GCP 스타일 네비게이션 생성"""
    tabs = [
        ("대시보드", "tachometer-alt", 0),
        ("기사 관리", "newspaper", 1),
        ("RAG 검색", "search", 2),
        ("통계 분석", "chart-line", 3),
        ("시스템 설정", "cog", 4),
        ("GCP 인프라", "cloud", 5),
        ("벡터 처리", "vector-square", 6),
        ("AI 해설", "robot", 7)
    ]
    
    nav_items = ""
    for name, icon, tab_id in tabs:
        active_class = "active" if tab_id == active_tab else ""
        nav_items += f"""
        <li class="gcp-nav-item">
            <a href="#" class="gcp-nav-link {active_class}" onclick="switchTab({tab_id})">
                <i class="fas fa-{icon} gcp-sidebar-icon"></i>
                {name}
            </a>
        </li>
        """
    
    return f"""
    <nav class="gcp-nav">
        <div class="gcp-nav-content">
            <a href="#" class="gcp-nav-brand">
                <i class="fas fa-cloud" style="color: var(--gcp-primary);"></i>
                MK AI Platform
            </a>
            <ul class="gcp-nav-menu">
                {nav_items}
            </ul>
        </div>
    </nav>
    <script>
        function switchTab(tabId) {{
            // Streamlit session state 업데이트
            const event = new CustomEvent('switchTab', {{ detail: {{ tabId: tabId }} }});
            window.dispatchEvent(event);
        }}
    </script>
    """

def create_gcp_sidebar():
    """GCP 스타일 사이드바 생성"""
    return """
    <div class="gcp-sidebar" id="sidebar">
        <div class="gcp-sidebar-header">
            <h2 class="gcp-sidebar-title">메뉴</h2>
        </div>
        <div class="gcp-sidebar-content">
            <div class="gcp-sidebar-section">
                <h3 class="gcp-sidebar-section-title">주요 기능</h3>
                <ul class="gcp-sidebar-menu">
                    <li class="gcp-sidebar-item">
                        <a href="#" class="gcp-sidebar-link active">
                            <i class="fas fa-tachometer-alt gcp-sidebar-icon"></i>
                            대시보드
                        </a>
                    </li>
                    <li class="gcp-sidebar-item">
                        <a href="#" class="gcp-sidebar-link">
                            <i class="fas fa-newspaper gcp-sidebar-icon"></i>
                            기사 관리
                        </a>
                    </li>
                    <li class="gcp-sidebar-item">
                        <a href="#" class="gcp-sidebar-link">
                            <i class="fas fa-search gcp-sidebar-icon"></i>
                            RAG 검색
                        </a>
                    </li>
                    <li class="gcp-sidebar-item">
                        <a href="#" class="gcp-sidebar-link">
                            <i class="fas fa-chart-line gcp-sidebar-icon"></i>
                            통계 분석
                        </a>
                    </li>
                </ul>
            </div>
            <div class="gcp-sidebar-section">
                <h3 class="gcp-sidebar-section-title">시스템</h3>
                <ul class="gcp-sidebar-menu">
                    <li class="gcp-sidebar-item">
                        <a href="#" class="gcp-sidebar-link">
                            <i class="fas fa-cog gcp-sidebar-icon"></i>
                            설정
                        </a>
                    </li>
                    <li class="gcp-sidebar-item">
                        <a href="#" class="gcp-sidebar-link">
                            <i class="fas fa-cloud gcp-sidebar-icon"></i>
                            GCP 인프라
                        </a>
                    </li>
                    <li class="gcp-sidebar-item">
                        <a href="#" class="gcp-sidebar-link">
                            <i class="fas fa-vector-square gcp-sidebar-icon"></i>
                            벡터 처리
                        </a>
                    </li>
                    <li class="gcp-sidebar-item">
                        <a href="#" class="gcp-sidebar-link">
                            <i class="fas fa-robot gcp-sidebar-icon"></i>
                            AI 해설
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </div>
    """

def create_gcp_card(title, content, icon=None, actions=None):
    """GCP 스타일 카드 생성"""
    icon_html = f'<i class="fas fa-{icon}" style="color: var(--gcp-primary);"></i>' if icon else ""
    actions_html = ""
    
    if actions:
        actions_html = f"""
        <div class="gcp-card-footer">
            {actions}
        </div>
        """
    
    return f"""
    <div class="gcp-card">
        <div class="gcp-card-header">
            <h3 class="gcp-card-title">
                {icon_html}
                {title}
            </h3>
        </div>
        <div class="gcp-card-body">
            {content}
        </div>
        {actions_html}
    </div>
    """

def create_gcp_metric_card(title, value, change=None, change_type="neutral", icon=None):
    """GCP 스타일 메트릭 카드 생성"""
    icon_html = f'<i class="fas fa-{icon}" style="color: var(--gcp-primary);"></i>' if icon else ""
    change_html = ""
    
    if change is not None:
        change_class = "positive" if change_type == "positive" else "negative" if change_type == "negative" else "neutral"
        change_icon = "fa-arrow-up" if change_type == "positive" else "fa-arrow-down" if change_type == "negative" else "fa-minus"
        change_html = f"""
        <div class="gcp-metric-change {change_class}">
            <i class="fas {change_icon}"></i>
            {change}
        </div>
        """
    
    return f"""
    <div class="gcp-metric-card">
        <div class="gcp-metric-header">
            <h4 class="gcp-metric-title">{title}</h4>
            {icon_html}
        </div>
        <div class="gcp-metric-value">{value}</div>
        {change_html}
    </div>
    """

def create_gcp_button(text, variant="primary", size="md", icon=None, onclick=None):
    """GCP 스타일 버튼 생성"""
    icon_html = f'<i class="fas fa-{icon}"></i>' if icon else ""
    onclick_attr = f'onclick="{onclick}"' if onclick else ""
    
    return f"""
    <button class="gcp-btn gcp-btn-{variant} gcp-btn-{size}" {onclick_attr}>
        {icon_html}
        {text}
    </button>
    """

def create_gcp_alert(message, type="info", icon=None, dismissible=True):
    """GCP 스타일 알림 생성"""
    icons = {
        "success": "check-circle",
        "warning": "exclamation-triangle", 
        "error": "times-circle",
        "info": "info-circle"
    }
    
    icon_name = icon or icons.get(type, "info-circle")
    dismiss_html = """
    <button class="gcp-btn gcp-btn-ghost gcp-btn-sm" onclick="this.parentElement.style.display='none'">
        <i class="fas fa-times"></i>
    </button>
    """ if dismissible else ""
    
    return f"""
    <div class="gcp-alert gcp-alert-{type}">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-{icon_name}" style="font-size: 1.25rem;"></i>
                <span>{message}</span>
            </div>
            {dismiss_html}
        </div>
    </div>
    """

def create_gcp_status_indicator(text, status="info"):
    """GCP 스타일 상태 표시기 생성"""
    return f"""
    <span class="gcp-status gcp-status-{status}">
        <span class="gcp-status-dot"></span>
        {text}
    </span>
    """

def create_gcp_progress_bar(percentage, label=None):
    """GCP 스타일 진행률 표시바 생성"""
    label_html = f'<div style="margin-bottom: 0.5rem; font-size: 0.875rem; color: var(--gcp-text-secondary);">{label}</div>' if label else ""
    
    return f"""
    <div>
        {label_html}
        <div class="gcp-progress">
            <div class="gcp-progress-bar" style="width: {percentage}%"></div>
        </div>
    </div>
    """

def create_gcp_loading_spinner(text="로딩 중..."):
    """GCP 스타일 로딩 스피너 생성"""
    return f"""
    <div class="gcp-loading-content">
        <div class="gcp-loading-spinner"></div>
        <p class="gcp-loading-text">{text}</p>
    </div>
    """

def create_gcp_empty_state(title, description, icon="inbox", action=None):
    """GCP 스타일 빈 상태 표시 생성"""
    action_html = f"""
    <div style="margin-top: 1rem;">
        {action}
    </div>
    """ if action else ""
    
    return f"""
    <div class="gcp-empty-state">
        <div class="gcp-empty-state-icon">
            <i class="fas fa-{icon}" style="font-size: 4rem; color: var(--gcp-text-tertiary);"></i>
        </div>
        <h3 class="gcp-empty-state-title">{title}</h3>
        <p class="gcp-empty-state-description">{description}</p>
        {action_html}
    </div>
    """

def create_gcp_table(headers, rows, striped=True, hover=True):
    """GCP 스타일 테이블 생성"""
    striped_class = "gcp-table-striped" if striped else ""
    hover_class = "gcp-table-hover" if hover else ""
    
    header_html = "".join([f"<th>{header}</th>" for header in headers])
    rows_html = ""
    
    for row in rows:
        rows_html += "<tr>"
        for cell in row:
            rows_html += f"<td>{cell}</td>"
        rows_html += "</tr>"
    
    return f"""
    <div class="gcp-table-container" style="overflow-x: auto;">
        <table class="gcp-table {striped_class} {hover_class}">
            <thead>
                <tr>{header_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

def create_gcp_form_group(label, input_html, help_text=None, error_text=None):
    """GCP 스타일 폼 그룹 생성"""
    help_html = f'<div class="gcp-form-help">{help_text}</div>' if help_text else ""
    error_html = f'<div class="gcp-form-error">{error_text}</div>' if error_text else ""
    
    return f"""
    <div class="gcp-form-group">
        <label class="gcp-form-label">{label}</label>
        {input_html}
        {help_html}
        {error_html}
    </div>
    """

def create_gcp_modal(title, content, actions=None, size="md"):
    """GCP 스타일 모달 생성"""
    size_class = f"gcp-modal-{size}" if size != "md" else ""
    actions_html = f"""
    <div class="gcp-modal-footer">
        {actions}
    </div>
    """ if actions else ""
    
    return f"""
    <div class="gcp-modal-overlay" id="modal-overlay">
        <div class="gcp-modal {size_class}">
            <div class="gcp-modal-header">
                <h2 class="gcp-modal-title">{title}</h2>
                <button class="gcp-modal-close" onclick="closeModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="gcp-modal-body">
                {content}
            </div>
            {actions_html}
        </div>
    </div>
    <script>
        function closeModal() {{
            document.getElementById('modal-overlay').style.display = 'none';
        }}
    </script>
    """

def create_gcp_dashboard_grid(items):
    """GCP 스타일 대시보드 그리드 생성"""
    items_html = "".join([f'<div class="gcp-dashboard-item">{item}</div>' for item in items])
    
    return f"""
    <div class="gcp-dashboard">
        {items_html}
    </div>
    """

def create_gcp_chart_container(title, chart_html, actions=None):
    """GCP 스타일 차트 컨테이너 생성"""
    actions_html = f"""
    <div class="gcp-chart-actions">
        {actions}
    </div>
    """ if actions else ""
    
    return f"""
    <div class="gcp-chart">
        <div class="gcp-chart-header">
            <h3 class="gcp-chart-title">{title}</h3>
            {actions_html}
        </div>
        <div class="gcp-chart-body">
            {chart_html}
        </div>
    </div>
    """

def apply_gcp_theme():
    """GCP 테마 적용"""
    return """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="/static/css/gcp_theme.css">
    <link rel="stylesheet" href="/static/css/gcp_components.css">
    <style>
        /* Streamlit 기본 스타일 오버라이드 */
        .main .block-container {
            padding-top: 0;
            padding-bottom: 0;
        }
        
        .stApp {
            background-color: var(--gcp-bg-primary);
        }
        
        .stButton > button {
            background-color: var(--gcp-primary);
            color: var(--gcp-text-inverse);
            border: none;
            border-radius: var(--gcp-radius-md);
            padding: var(--gcp-space-3) var(--gcp-space-4);
            font-weight: var(--gcp-font-medium);
            transition: all var(--gcp-transition-fast);
        }
        
        .stButton > button:hover {
            background-color: var(--gcp-primary-hover);
            box-shadow: var(--gcp-shadow-2);
        }
        
        .stSelectbox > div > div {
            background-color: var(--gcp-bg-primary);
            border: 1px solid var(--gcp-border-medium);
            border-radius: var(--gcp-radius-md);
        }
        
        .stTextInput > div > div > input {
            background-color: var(--gcp-bg-primary);
            border: 1px solid var(--gcp-border-medium);
            border-radius: var(--gcp-radius-md);
            color: var(--gcp-text-primary);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--gcp-primary);
            box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1);
        }
        
        .stTextArea > div > div > textarea {
            background-color: var(--gcp-bg-primary);
            border: 1px solid var(--gcp-border-medium);
            border-radius: var(--gcp-radius-md);
            color: var(--gcp-text-primary);
        }
        
        .stDataFrame {
            border: 1px solid var(--gcp-border-light);
            border-radius: var(--gcp-radius-lg);
            overflow: hidden;
        }
        
        .stAlert {
            border-radius: var(--gcp-radius-md);
            border: none;
        }
        
        .stSuccess {
            background-color: var(--gcp-green-50);
            color: var(--gcp-green-800);
            border-left: 4px solid var(--gcp-success);
        }
        
        .stError {
            background-color: var(--gcp-red-50);
            color: var(--gcp-red-800);
            border-left: 4px solid var(--gcp-error);
        }
        
        .stWarning {
            background-color: var(--gcp-yellow-50);
            color: var(--gcp-yellow-800);
            border-left: 4px solid var(--gcp-warning);
        }
        
        .stInfo {
            background-color: var(--gcp-blue-50);
            color: var(--gcp-blue-800);
            border-left: 4px solid var(--gcp-info);
        }
        
        /* 다크모드 스타일 */
        [data-theme="dark"] .stApp {
            background-color: var(--gcp-bg-primary);
        }
        
        [data-theme="dark"] .stSelectbox > div > div {
            background-color: var(--gcp-grey-800);
            border-color: var(--gcp-grey-600);
        }
        
        [data-theme="dark"] .stTextInput > div > div > input {
            background-color: var(--gcp-grey-800);
            border-color: var(--gcp-grey-600);
            color: var(--gcp-text-primary);
        }
        
        [data-theme="dark"] .stTextArea > div > div > textarea {
            background-color: var(--gcp-grey-800);
            border-color: var(--gcp-grey-600);
            color: var(--gcp-text-primary);
        }
    </style>
    """
