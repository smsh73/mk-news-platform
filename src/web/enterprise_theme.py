"""
엔터프라이즈급 UI/UX 테마 및 컴포넌트
Salesforce Lightning Design System 기반
"""
import streamlit as st
import streamlit.components.v1 as components

def apply_enterprise_theme():
    """엔터프라이즈급 테마 적용"""
    
    # Salesforce Lightning Design System CSS
    slds_css = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/design-system/2.15.3/styles/salesforce-lightning-design-system.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """
    
    # 커스텀 엔터프라이즈 CSS
    custom_css = """
    <style>
    /* Salesforce Lightning Design System 기반 커스텀 스타일 */
    
    /* 전체 레이아웃 */
    .main .block-container {
        padding: 0;
        max-width: 100%;
    }
    
    /* 헤더 스타일 */
    .enterprise-header {
        background: linear-gradient(135deg, #1B5F9E 0%, #2E7D32 100%);
        color: white;
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-bottom: 3px solid #00A1E0;
    }
    
    .enterprise-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .enterprise-header .subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: linear-gradient(180deg, #F8F9FA 0%, #E9ECEF 100%);
        border-right: 2px solid #DEE2E6;
    }
    
    .css-1d391kg .stButton > button {
        background: linear-gradient(135deg, #0070D2 0%, #0056B3 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,112,210,0.3);
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .css-1d391kg .stButton > button:hover {
        background: linear-gradient(135deg, #0056B3 0%, #004085 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,112,210,0.4);
    }
    
    /* 메인 컨텐츠 영역 */
    .main-content {
        background: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        padding: 2rem;
        margin: 1rem;
    }
    
    /* 카드 스타일 */
    .enterprise-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #E9ECEF;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .enterprise-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .enterprise-card h3 {
        color: #1B5F9E;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 2px solid #00A1E0;
        padding-bottom: 0.5rem;
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(102,126,234,0.3);
        margin-bottom: 1rem;
    }
    
    .metric-card .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* 버튼 스타일 */
    .enterprise-button {
        background: linear-gradient(135deg, #00A1E0 0%, #0070D2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,161,224,0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .enterprise-button:hover {
        background: linear-gradient(135deg, #0070D2 0%, #0056B3 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,161,224,0.4);
    }
    
    .enterprise-button.secondary {
        background: linear-gradient(135deg, #6C757D 0%, #495057 100%);
    }
    
    .enterprise-button.success {
        background: linear-gradient(135deg, #28A745 0%, #1E7E34 100%);
    }
    
    .enterprise-button.warning {
        background: linear-gradient(135deg, #FFC107 0%, #E0A800 100%);
    }
    
    .enterprise-button.danger {
        background: linear-gradient(135deg, #DC3545 0%, #C82333 100%);
    }
    
    /* 테이블 스타일 */
    .enterprise-table {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #E9ECEF;
    }
    
    .enterprise-table table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .enterprise-table th {
        background: linear-gradient(135deg, #1B5F9E 0%, #2E7D32 100%);
        color: white;
        padding: 1rem;
        font-weight: 600;
        text-align: left;
    }
    
    .enterprise-table td {
        padding: 1rem;
        border-bottom: 1px solid #E9ECEF;
    }
    
    .enterprise-table tr:hover {
        background: #F8F9FA;
    }
    
    /* 폼 스타일 */
    .enterprise-form {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #E9ECEF;
    }
    
    .enterprise-form .form-group {
        margin-bottom: 1.5rem;
    }
    
    .enterprise-form label {
        display: block;
        font-weight: 600;
        color: #1B5F9E;
        margin-bottom: 0.5rem;
    }
    
    .enterprise-form input,
    .enterprise-form select,
    .enterprise-form textarea {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #E9ECEF;
        border-radius: 8px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .enterprise-form input:focus,
    .enterprise-form select:focus,
    .enterprise-form textarea:focus {
        border-color: #00A1E0;
        box-shadow: 0 0 0 3px rgba(0,161,224,0.1);
        outline: none;
    }
    
    /* 알림 스타일 */
    .enterprise-alert {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    
    .enterprise-alert.success {
        background: #D4EDDA;
        border-color: #28A745;
        color: #155724;
    }
    
    .enterprise-alert.warning {
        background: #FFF3CD;
        border-color: #FFC107;
        color: #856404;
    }
    
    .enterprise-alert.error {
        background: #F8D7DA;
        border-color: #DC3545;
        color: #721C24;
    }
    
    .enterprise-alert.info {
        background: #D1ECF1;
        border-color: #17A2B8;
        color: #0C5460;
    }
    
    /* 탭 스타일 */
    .enterprise-tabs {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #E9ECEF;
        overflow: hidden;
    }
    
    .enterprise-tabs .tab-list {
        display: flex;
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
        border-bottom: 2px solid #DEE2E6;
    }
    
    .enterprise-tabs .tab-item {
        flex: 1;
        padding: 1rem 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border-right: 1px solid #DEE2E6;
    }
    
    .enterprise-tabs .tab-item:hover {
        background: rgba(0,161,224,0.1);
    }
    
    .enterprise-tabs .tab-item.active {
        background: linear-gradient(135deg, #00A1E0 0%, #0070D2 100%);
        color: white;
    }
    
    .enterprise-tabs .tab-content {
        padding: 2rem;
    }
    
    /* 로딩 스피너 */
    .enterprise-spinner {
        display: inline-block;
        width: 2rem;
        height: 2rem;
        border: 3px solid #E9ECEF;
        border-radius: 50%;
        border-top-color: #00A1E0;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .enterprise-header {
            padding: 1rem;
            margin: -1rem -1rem 1rem -1rem;
        }
        
        .enterprise-header h1 {
            font-size: 1.5rem;
        }
        
        .main-content {
            padding: 1rem;
            margin: 0.5rem;
        }
        
        .enterprise-tabs .tab-list {
            flex-direction: column;
        }
        
        .enterprise-tabs .tab-item {
            border-right: none;
            border-bottom: 1px solid #DEE2E6;
        }
    }
    
    /* 다크 모드 지원 */
    @media (prefers-color-scheme: dark) {
        .main-content {
            background: #1A1A1A;
            color: #FFFFFF;
        }
        
        .enterprise-card {
            background: #2D2D2D;
            border-color: #404040;
        }
        
        .enterprise-form {
            background: #2D2D2D;
            border-color: #404040;
        }
    }
    </style>
    """
    
    # CSS 적용
    components.html(f"{slds_css}{custom_css}", height=0)

def create_enterprise_header(title, subtitle=""):
    """엔터프라이즈 헤더 생성"""
    return f"""
    <div class="enterprise-header">
        <h1><i class="fas fa-newspaper"></i> {title}</h1>
        {f'<div class="subtitle">{subtitle}</div>' if subtitle else ''}
    </div>
    """

def create_metric_card(value, label, icon="fas fa-chart-line", color="primary"):
    """메트릭 카드 생성"""
    color_classes = {
        "primary": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "success": "linear-gradient(135deg, #28A745 0%, #1E7E34 100%)",
        "warning": "linear-gradient(135deg, #FFC107 0%, #E0A800 100%)",
        "danger": "linear-gradient(135deg, #DC3545 0%, #C82333 100%)",
        "info": "linear-gradient(135deg, #17A2B8 0%, #138496 100%)"
    }
    
    return f"""
    <div class="metric-card" style="background: {color_classes.get(color, color_classes['primary'])};">
        <div class="metric-value"><i class="{icon}"></i> {value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def create_enterprise_card(title, content, icon="fas fa-cog"):
    """엔터프라이즈 카드 생성"""
    return f"""
    <div class="enterprise-card">
        <h3><i class="{icon}"></i> {title}</h3>
        {content}
    </div>
    """

def create_enterprise_button(text, button_type="primary", icon="", onclick=""):
    """엔터프라이즈 버튼 생성"""
    type_classes = {
        "primary": "enterprise-button",
        "secondary": "enterprise-button secondary",
        "success": "enterprise-button success",
        "warning": "enterprise-button warning",
        "danger": "enterprise-button danger"
    }
    
    icon_html = f'<i class="{icon}"></i> ' if icon else ""
    onclick_attr = f' onclick="{onclick}"' if onclick else ""
    
    return f"""
    <button class="{type_classes.get(button_type, 'enterprise-button')}"{onclick_attr}>
        {icon_html}{text}
    </button>
    """

def create_enterprise_alert(message, alert_type="info", icon=""):
    """엔터프라이즈 알림 생성"""
    type_icons = {
        "success": "fas fa-check-circle",
        "warning": "fas fa-exclamation-triangle",
        "error": "fas fa-times-circle",
        "info": "fas fa-info-circle"
    }
    
    icon_class = icon or type_icons.get(alert_type, "fas fa-info-circle")
    
    return f"""
    <div class="enterprise-alert {alert_type}">
        <i class="{icon_class}"></i> {message}
    </div>
    """

def create_enterprise_table(headers, rows):
    """엔터프라이즈 테이블 생성"""
    header_html = "<tr>" + "".join(f"<th>{header}</th>" for header in headers) + "</tr>"
    rows_html = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    
    return f"""
    <div class="enterprise-table">
        <table>
            <thead>{header_html}</thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """

def create_enterprise_form(form_elements):
    """엔터프라이즈 폼 생성"""
    form_html = '<div class="enterprise-form">'
    for element in form_elements:
        form_html += f'<div class="form-group">{element}</div>'
    form_html += '</div>'
    return form_html

def create_loading_spinner():
    """로딩 스피너 생성"""
    return '<div class="enterprise-spinner"></div>'
