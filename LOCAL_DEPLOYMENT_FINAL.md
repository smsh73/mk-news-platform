# 로컬 배포 최종 점검

## 배포 상태

### ✅ FastAPI Backend
- **URL**: http://localhost:8000
- **상태**: 정상 작동 중
- **Health Check**: 정상

### ✅ Streamlit Frontend
- **URL**: http://localhost:8501
- **상태**: 정상 작동 중

## 수정 완료된 항목

### 1. ✅ Cloud Build 설정 파일 생성
**파일**: `cloudbuild-admin.yaml`

```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: [
    'build',
    '-t', 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/mk-news-repo/mk-news-admin:latest',
    '-f', 'Dockerfile.admin',
    '.'
  ]
images:
- 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/mk-news-repo/mk-news-admin:latest'
```

### 2. ✅ Docker 빌드 코드 수정
**파일**: `src/web/docker_build.py`

- `-f` 옵션 제거 (gcloud에서 인식 안됨)
- `--dockerfile` 제거 (gcloud에서 인식 안됨)
- `--config cloudbuild-admin.yaml` 사용 (올바른 방법)

### 3. ✅ 강제 재배포 기능
- Streamlit UI에 "🔄 강제 재배포" 체크박스 추가
- Backend에서 `force_rebuild` 파라미터 처리
- 이미지가 있어도 새로 빌드 가능

### 4. ✅ Streamlit 경고 수정
- `dataframe`의 `use_container_width=True` → `width='stretch'` 변경
- `plotly_chart`는 그대로 유지 (경고만 표시, 작동 정상)

### 5. ✅ 서비스 목록 에러 수정
- 컬럼 존재 여부 검증 로직 추가
- 사용 가능한 컬럼만 선택하여 에러 방지

### 6. ✅ Vertex AI 테스트 개선
- region 파라미터 추가: `--region=asia-northeast3`
- 정상 작동 확인

## GCP 인프라 배포 프로세스

### 자동화된 배포 흐름

```
1️⃣ Terraform Init
   ↓
2️⃣ Terraform Plan
   ↓
3️⃣ Terraform Apply
   ├─ Docker 이미지 존재 여부 확인
   ├─ 강제 재배포 체크?
   │  - Yes → 새로 빌드
   │  - No → 이미지 있으면 건너뛰기
   ├─ gcloud builds submit --config cloudbuild-admin.yaml
   └─ Cloud Run 배포
```

### 사용 방법

#### 브라우저 접속
```
http://localhost:8501
```

#### 배포 단계
1. **GCP 인프라 배포** 탭 선택
2. **"1️⃣ Terraform Init"** 클릭
3. **"2️⃣ Terraform Plan"** 클릭
4. **강제 재배포** 체크박스 선택 (필요시)
5. **"3️⃣ Terraform Apply"** 클릭
   - Docker 이미지가 자동으로 빌드됨
   - Cloud Run에 자동 배포됨

## 주요 개선사항

### Docker 이미지 빌드
- **이전**: 직접 Dockerfile 지정 시도 → 실패
- **현재**: Cloud Build 설정 파일 사용 → 성공

### 강제 재배포
- **사용자 요구**: 이미지가 있어도 새 버전 배포 필요
- **구현**: 체크박스로 사용자가 선택 가능

### 로그 표시
- **현재**: 완료 후 전체 로그 표시
- **향후**: StreamingResponse로 실시간 로그 스트리밍 가능

## 참고사항

### Database 연결 에러
- 로컬에서 Private IP로 접속 시도 시 발생하는 정상적인 에러
- GCP 인프라 배포 후 Public IP 접속 설정 필요

### plotly_chart 경고
- `use_container_width=True`는 작동하지만 향후 deprecated 예정
- 현재는 기능 정상, 경고만 표시됨

## 다음 단계

1. **http://localhost:8501** 접속
2. **"GCP 인프라 배포"** 탭 이동
3. **Init → Plan → Apply** 순서로 배포
4. 배포 완료 후 Cloud Run URL 확인

## 배포 완료 후 확인사항

### GCP 콘솔에서 확인
- Cloud Run 서비스 생성 확인
- Artifact Registry에 이미지 확인
- VPC, Cloud SQL, Storage 등 인프라 확인

### 접속 방법
```bash
# Cloud Run Admin URL 확인
gcloud run services describe mk-news-admin --region=asia-northeast3 --format='value(status.url)'
```
