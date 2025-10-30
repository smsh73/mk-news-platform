# Streamlit Terraform 실시간 로깅 UI 구현 가이드

## 구현된 기능

### 1. 백엔드 API 추가
- `/api/terraform/init` - Terraform 초기화
- `/api/terraform/plan` - Terraform Plan
- `/api/terraform/apply` - Terraform Apply  
- `/api/terraform/status` - 상태 조회
- `/api/terraform/logs` - 로그 조회
- `/api/terraform/outputs` - 출력값 조회

### 2. Terraform Manager 모듈
`src/web/terraform_manager.py`에 구현:
- 실시간 로그 수집
- subprocess 기반 비동기 실행
- 콜백을 통한 실시간 로그 전달
- 에러 처리 및 타임아웃 관리

### 3. Streamlit UI 업데이트

`src/web/streamlit_app.py`에 다음 코드를 추가하여 실시간 로깅 기능을 구현:

```python
elif st.session_state['active_tab'] == 5:  # GCP 인프라 탭
    st.header("☁️ GCP 인프라 관리")
    
    # ... 기존 GCP 로그인 코드 ...
    
    # 실시간 Terraform 배포 섹션 추가
    st.subheader("🚀 Terraform 실시간 배포")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("1️⃣ Init", type="primary"):
            with st.spinner("Terraform 초기화 중..."):
                response = requests.post("http://localhost:8000/api/terraform/init")
                if response.status_code == 200:
                    result = response.json()
                    st.json(result)
    
    with col2:
        if st.button("2️⃣ Plan", type="primary"):
            log_container = st.empty()
            with st.spinner("Terraform Plan 실행 중..."):
                response = requests.post("http://localhost:8000/api/terraform/plan")
                if response.status_code == 200:
                    result = response.json()
                    # 실시간 로그 표시
                    for log_line in result.get('logs', []):
                        log_container.code(log_line)
    
    with col3:
        if st.button("3️⃣ Apply", type="primary"):
            # 로그를 실시간으로 표시하는 컨테이너
            log_container = st.container()
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with log_container:
                with st.spinner("Terraform Apply 실행 중..."):
                    response = requests.post("http://localhost:8000/api/terraform/apply")
                    if response.status_code == 200:
                        result = response.json()
                        
                        # 로그 표시
                        st.subheader("📋 배포 로그")
                        with st.expander("전체 로그 보기", expanded=True):
                            st.code('\n'.join(result.get('logs', [])))
                        
                        # 상태 표시
                        if result.get('success'):
                            st.success("✅ 배포 성공!")
                            st.balloons()
                        else:
                            st.error(f"❌ 배포 실패: {result.get('error', 'Unknown error')}")
```

## 사용 방법

### 1. 백엔드 실행
```bash
uvicorn src.web.app:app --host 0.0.0.0 --port 8000
```

### 2. Streamlit 실행
```bash
streamlit run src/web/streamlit_app.py
```

### 3. 배포 실행
1. 브라우저에서 http://localhost:8501 접속
2. "☁️ GCP 인프라" 탭 선택
3. GCP 로그인 완료
4. "1️⃣ Init" → "2️⃣ Plan" → "3️⃣ Apply" 순서로 클릭
5. 실시간 로그 확인

## 향후 개선 사항

### 실시간 로그 스트리밍 (Server-Sent Events)
```python
@app.get("/api/terraform/stream")
async def stream_terraform_logs():
    """실시간 로그 스트리밍"""
    def generate():
        manager = get_terraform_manager()
        for log_line in manager.logs:
            yield f"data: {json.dumps({'log': log_line})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

Streamlit에서:
```python
# 실시간 로그 업데이트
if 'last_log_count' not in st.session_state:
    st.session_state.last_log_count = 0

# 주기적으로 로그 확인
time.sleep(1)
response = requests.get("http://localhost:8000/api/terraform/logs")
logs = response.json().get('logs', [])

if len(logs) > st.session_state.last_log_count:
    new_logs = logs[st.session_state.last_log_count:]
    for log_line in new_logs:
        st.code(log_line)
    st.session_state.last_log_count = len(logs)
    st.rerun()
```

## 현재 구현 상태

✅ 완료:
- Terraform Manager 모듈
- 백엔드 API 엔드포인트
- 기본 로그 수집 및 반환

⏳ 진행 필요:
- Streamlit UI에 통합
- 실시간 로그 표시 (polling 방식)
- 진행률 표시
- 단계별 상태 표시

**다음 단계**: Streamlit UI를 업데이트하여 실시간 로깅 기능을 완성하세요.
