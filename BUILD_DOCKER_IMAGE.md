# Docker 이미지 빌드 및 Cloud Run 배포 가이드

## 현재 상황

- ✅ GCP 인프라 배포 완료 (26개 리소스)
- ❌ Cloud Run 서비스 없음 (Docker 이미지 필요)

## Docker 이미지 빌드 방법

### 1. 사전 준비

#### GCP 인증 설정
```bash
# GCP 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project mk-ai-project-473000

# Artifact Registry 인증 설정
gcloud auth configure-docker asia-northeast3-docker.pkg.dev
```

### 2. 관리자 애플리케이션 이미지 빌드

#### 로컬에서 빌드 및 푸시
```bash
# 프로젝트 디렉토리로 이동
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"

# Artifact Registry 주소 설정
export PROJECT_ID=mk-ai-project-473000
export REGION=asia-northeast3
export REPO=mk-news-repo
export IMAGE_NAME=mk-news-admin

# Docker 이미지 빌드 및 푸시
gcloud builds submit --tag asia-northeast3-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:latest \
  --timeout=1800s \
  -f Dockerfile.admin
```

#### 또는 Cloud Build 사용
```bash
# Cloud Build로 빌드 및 푸시
gcloud builds submit --config=cloudbuild.yaml
```

### 3. FastAPI 이미지 빌드 (선택사항)

```bash
export IMAGE_NAME_API=mk-news-api

gcloud builds submit --tag asia-northeast3-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME_API}:latest \
  --timeout=1800s \
  -f Dockerfile.api
```

## Cloud Run 배포

### 관리자 애플리케이션 배포

```bash
gcloud run deploy mk-news-admin \
  --image asia-northeast3-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 3600s \
  --max-instances 5 \
  --min-instances 0 \
  --port 8501 \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_REGION=${REGION},USE_MANAGED_SERVICES=true" \
  --service-account=mk-news-platform@${PROJECT_ID}.iam.gserviceaccount.com \
  --vpc-connector=mk-news-connector \
  --vpc-egress=private-ranges-only
```

### FastAPI 배포 (선택사항)

```bash
gcloud run deploy mk-news-api \
  --image asia-northeast3-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME_API}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600s \
  --max-instances 10 \
  --min-instances 0 \
  --port 8000 \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_REGION=${REGION},USE_MANAGED_SERVICES=true" \
  --set-env-vars="DB_CONNECTION_NAME=${PROJECT_ID}:${REGION}:mk-news-db" \
  --set-env-vars="STORAGE_BUCKET=mk-ai-project-473000-mk-news-data" \
  --set-env-vars="VECTOR_STORAGE_BUCKET=mk-ai-project-473000-vector-index" \
  --service-account=mk-news-platform@${PROJECT_ID}.iam.gserviceaccount.com \
  --vpc-connector=mk-news-connector \
  --vpc-egress=private-ranges-only
```

## 접속 확인

배포 완료 후 접속 URL 확인:

```bash
# 서비스 목록 조회
gcloud run services list --region=asia-northeast3

# 특정 서비스 URL 확인
gcloud run services describe mk-news-admin --region=asia-northeast3 --format='value(status.url)'
```

## Terraform State에 추가

배포 완료 후 Terraform State에 추가하여 관리:

```bash
cd terraform

# Cloud Run Admin State 추가
terraform import google_cloud_run_v2_service.mk_news_admin \
  projects/mk-ai-project-473000/locations/asia-northeast3/services/mk-news-admin

# IAM 설정도 추가 (필요시)
terraform import google_cloud_run_service_iam_member.mk_news_admin_public \
  projects/mk-ai-project-473000/locations/asia-n рheast3/services/mk-news-admin/roles/run.invoker/allUsers
```

## 트러블슈팅

### 이미지 빌드 실패
- Python 3.13 호환성 문제: Dockerfile에서 3.11 사용 확인
- 메모리 부족: `--memory` 옵션 확인

### 배포 실패
- 서비스 계정 권한: IAM 역할 확인
- VPC Connector: `mk-news-connector` 존재 확인

### 접속 불가
- IAM 설정: `--allow-unauthenticated` 확인
- 방화벽: VPC 방화벽 규칙 확인

## 권장 순서

1. **먼저 관리자 애플리케이션만 배포**
2. **접속 확인 및 기능 테스트**
3. **이후 API 서비스 배포 (필요시)**
4. **Terraform State에 추가하여 관리**
