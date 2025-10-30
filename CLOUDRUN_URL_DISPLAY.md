# Cloud Run 관리자 앱 URL 표시 기능

## 구현 내용

### 메인페이지에 Cloud Run URL 항상 표시

**파일**: `src/web/streamlit_app.py`

### 주요 기능

1. **자동 URL 조회**: 페이지 로드 시 gcloud 명령어로 Cloud Run 서비스 URL 조회
2. **상단 항상 표시**: 다른 모든 콘텐츠 위에 URL 표시
3. **새로고침 버튼**: URL을 다시 조회할 수 있는 버튼 제공
4. **링크 클릭 가능**: URL을 클릭하면 관리자 앱으로 이동

### 구현 코드

```python
def get_cloud_run_admin_url():
    """Cloud Run 관리자 앱 URL 조회"""
    try:
        result = subprocess.run(
            ['gcloud', 'run', 'services', 'list', '--region=asia-northeast3', 
             '--filter=metadata.name=mk-news-admin', '--format=value(status.url)'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        return None
    except Exception:
        return None

# 페이지 로드 시 URL 조회
if 'admin_url' not in st.session_state or st.session_state.get('refresh_admin_url', False):
    admin_url = get_cloud_run_admin_url()
    st.session_state['admin_url'] = admin_url
    st.session_state['refresh_admin_url'] = False

# URL 표시
if st.session_state.get('admin_url'):
    st.info(f"🌐 **Cloud Run 관리자 앱**: [{st.session_state['admin_url']}]({st.session_state['admin_url']})")
else:
    st.warning("⚠️ Cloud Run 관리자 앱이 아직 배포되지 않았습니다.")

# 새로고침 버튼
if st.button("🔄"):
    st.session_state['refresh_admin_url'] = True
    st.rerun()
```

## 표시 위치

- **위치**: 메인페이지 최상단
- **순서**: 네비게이션 바로 위
- **항상 표시**: 모든 탭에서 보임

## 동작 방식

1. **페이지 로드**: Cloud Run 서비스에서 URL 자동 조회
2. **URL 있음**: 링크로 표시
3. **URL 없음**: 배포 안내 메시지 표시
4. **새로고침**: 버튼 클릭 시 URL 재조회

## 주요 명령어

```bash
# Cloud Run 서비스 URL 조회
gcloud run services list \
  --region=asia-northeast3 \
  --filter=metadata.name=mk-news-admin \
  --format=value(status.url)
```

## 사용자 경험

- **항상 접근 가능**: 메인페이지에서 바로 Cloud Run 앱으로 이동
- **현재 상태 확인**: 배포 여부를 즉시 확인
- **간편한 새로고침**: 버튼 하나로 최신 URL 확인

## 완료 상태

- ✅ URL 자동 조회
- ✅ 상단 항상 표시
- ✅ 새로고حو 버튼
- ✅ 배포 없을 때 안내 메시지

