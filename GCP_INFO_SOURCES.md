# GCP 정보 표시 원리

## 질문
GCP 인프라 탭을 클릭하면 project ID, region, account 정보가 화면에 표시되는데, 이 데이터들은 어떻게 오류 없이 가져오는 것일까?

## 답변

화면에 표시되는 GCP 정보는 **두 가지 방법**으로 가져옵니다:

### 1. 왼쪽 사이드바 (초기 로드 시)

**함수**: `check_gcp_auth()` (line 63-71)
```python
def check_gcp_auth():
    """GCP 인증 상태 확인"""
    try:
        credentials, project = default(scopes=SCOPES)
        if credentials and credentials.valid:
            return True, project
        return False, None
    except Exception as e:
        return False, None
```

**방법**: 
- Google의 **Application Default Credentials (ADC)** 사용
- `google.auth.default()` 함수로 로컬 인증 정보 확인
- 이미 `gcloud auth application-default login`으로 인증되어 있으면 자동으로 프로젝트 ID를 가져옴

**표시 위치**: 사이드바의 "GCP 인증 상태" 카드

### 2. GCP 인프라 탭 내 (탭 클릭 시)

**함수**: `get_current_project()` (line 214-228)
```python
def get_current_project():
    """현재 설정된 프로젝트 조회"""
    try:
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
```

**방법**:
- **gcloud CLI 명령어** 직접 실행
- `gcloud config get-value project` 명령어로 현재 설정된 프로젝트 ID 가져오기
- gcloud가 설치되어 있고 로그인되어 있어야 작동

**표시 위치**: "현재 프로젝트 정보" 섹션 (line 1260-1265)

### 3. Region 정보

**방법**: 
- 하드코딩된 기본값 사용 (line 1314-1315)
```python
region = st.selectbox("GCP 리전", ["asia-northeast3", "asia-northeast1", "us-central1"], index=0)
```

## 왜 오류 없이 작동할까?

두 가지 방법이 **독립적으로 작동**하기 때문에:

1. **ADC 방법**: `gcloud auth application-default login`로 인증되어 있으면
   - ✅ 사이드바에서 프로젝트 ID 표시
   - ✅ 초기 로드 시 session_state에 저장 (line 342-343)

2. **gcloud CLI 방법**: `gcloud auth login`으로 로그인되어 있으면
   - ✅ GCP 인프라 탭에서 프로젝트 ID 표시
   - ✅ Terraform에서 자동으로 사용 가능

### 백엔드의 자동 감지

**Terraform Init 버튼 클릭 시** (src/web/app.py line 746-762):
```python
# 프로젝트 ID가 없으면 gcloud에서 가져오기
if not project_id:
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            project_id = result.stdout.strip()
            logger.info(f"gcloud에서 프로젝트 ID 가져옴: {project_id}")
    except Exception as e:
        logger.error(f"gcloud 프로젝트 ID 가져오기 실패: {e}")
```

## 요약

| 정보 | 방법 | 함수/위치 |
|------|------|-----------|
| 프로젝트 ID (사이드바) | ADC | `check_gcp_auth()` |
| 프로젝트 ID (탭 내) | gcloud CLI | `get_current_project()` |
| Region | 하드코딩 | `st.selectbox()` |
| Account | ADC/gcloud | 인증 시 자동 |

**핵심**: 두 방법이 모두 지원되므로 어느 한 방법이라도 작동하면 정보가 표시됩니다.
