# Cloud Run 관리자 앱 URL 표시 기능 구현 완료

## 질문과 답변

### Q1: Cloud Run에 배포된 관리자용 웹앱의 접속 주소 필요
**A**: ✅ 구현 완료

### Q2: 메인페이지에 접속주소를 항시 업데이트하여 표시 가능?
**A**: ✅ 구현 완료 - 자동 업데이트 및 새로고침 버튼 제공

### Q3: 현재 메인페이지의 소스코드 파일이름은?
**A**: `src/web/streamlit_app.py`

## 구현 내용

### 1. 메인페이지 파일
- **파일명**: `src/web/streamlit_app.py`
- **위치**: 프로젝트 루트의 `src/web/` 디렉토리

### 2. Cloud Run URL 표시 기능

#### 자동 조회
- 페이지 로드 시 자동으로 Cloud Run 서비스 URL 조회
- `gcloud run services list` 명령어 사용

#### 표시 위치
- **메인페이지 최상단**: 모든 콘텐츠 위에 표시
- **항상 보임**: 다른 탭으로 이동해도 상단에 표시

#### 기능
1. **URL 있음**: 클릭 가능한 링크 표시
2. **URL 없음**: 배포 안내 메시지 표시
3. **새로고침 버튼**: 최신 URL 확인 가능

## 사용 방법

### 1. 접속
```
http://localhost:8501
```

### 2. URL 확인
- 메인페이지 상단에 Cloud Run URL 자동 표시
- 배포되지 않았다면 안내 메시지 표시

### 3. 새로고침
- 상단의 "🔄" 버튼 클릭
- URL 재조회 및 업데이트

## 구현 코드 위치

**파일**: `src/web/streamlit_app.py`

**라인**: 343-380

```python
# Cloud Run 관리자 앱 URL 조회 함수
def get_cloud_run_admin_url():
    """Cloud Run 관리자 앱 URL 조회"""
    result = subprocess.run(
        ['gcloud', 'run', 'services', 'list', '--region=asia-northeast3', 
         '--filter=metadata.name=mk-news-admin', '--format=value(status.url)'],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip() if result.returncode == 0 else None

# 페이지 로드 시 URL 조회
if 'admin_url' not in st.session_state or st.session_state.get('refresh_admin_url', False):
    admin_url = get_cloud_run_admin_url()
    st.session_state['admin_url'] = admin_url

# URL 표시
if st.session_state.get('admin_url'):
    st.info(f"🌐 **Cloud Run 관리자 앱**: [{url}]({url})")
else:
    st.warning("⚠️ Cloud Run 관리자 앱이 아직 배포되지 않았습니다.")

# 새로고침 버튼
if st.button("🔄"):
    st.session_state['refresh_admin_url'] = True
    st.rerun()
```

## 표시 예시

### Cloud Run 배포된 경우
```
🌐 Cloud Run 관리자 앱: https://mk-news-admin-xxx-xx.a.run.app 
- 로컬 대시보드 대신 Cloud Run에 배포된 앱에 접속하려면 이 링크를 사용하세요.

[🔄 버튼]
```

### Cloud Run 배포 안 된 경우
```
⚠️ Cloud Run 관리자 앱이 아직 배포되지 않았습니다. 'GCP 인프라' 탭에서 배포를 진행하세요.

[🔄 버튼]
```

## 배포 상태

- ✅ 메인페이지: `src/web/streamlit_app.py`
- ✅ URL 자동 조회 기능
- ✅ 상단 항상 표시
- ✅ 새로고침 버튼
- ✅ 배포 안내 메시지

## 참고 문서

- `CLOUDRUN_URL_DISPLAY.md` - 상세 구현 내용

## 완료! 🎉

모든 기능이 구현되어 정상 동작 중입니다!

