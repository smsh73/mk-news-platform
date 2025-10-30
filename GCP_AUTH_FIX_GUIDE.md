# GCP 인증 상태 새로고침 버튼 추가 필요

## 문제
GCP 인증 상태가 "인증되지 않음"으로 표시됨

## 원인
캐시된 인증 정보가 업데이트되지 않음

## 해결 방법

### 사이드바에 새로고침 버튼 추가
`src/web/streamlit_app.py` 394번 줄 다음에 추가:

```python
# GCP 인증 상태 카드 다음에 추가
if st.button("🔄 인증 상태 새로고침", key="refresh_auth_sidebar"):
    st.session_state['force_gcp_auth_refresh'] = True
    st.rerun()
```

### 또는 캐시 제거
다음 명령으로 Streamlit 재시작:
```bash
pkill -f streamlit
streamlit run src/web/streamlit_app.py --server.port 8501 &
```

### 인증 방법
"☁️ GCP 인프라" 탭 → "🔑 gcloud 로그인" 버튼 클릭


