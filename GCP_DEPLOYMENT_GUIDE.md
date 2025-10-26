# 🚀 GCP 관리형 서비스 배포 가이드

## 📋 개요
매일경제 신문기사 벡터임베딩 플랫폼을 GCP 관리형 서비스로 배포하는 가이드입니다.

## 🏗️ 아키텍처
- **Cloud Run**: FastAPI 백엔드 + Streamlit 관리자 앱
- **Cloud SQL**: PostgreSQL 데이터베이스 (Private IP)
- **Vertex AI**: 벡터 검색 및 임베딩 서비스
- **Cloud Storage**: XML 파일 및 모델 저장
- **VPC**: Private 네트워크 구성
- **Artifact Registry**: Docker 이미지 저장

## 🔧 사전 준비사항

### 1. GCP 계정 및 프로젝트 설정
```bash
# GCP 로그인
gcloud auth login --account=godwind2015@gmail.com

# 프로젝트 설정
gcloud config set project godwind2015
gcloud config set compute/region asia-northeast3
```

### 2. 필수 도구 설치
```bash
# Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Terraform
brew install terraform  # macOS
# 또는 https://www.terraform.io/downloads.html

# Docker
# https://docs.docker.com/get-docker/
```

## 🚀 배포 단계

### 1단계: 자동 배포 (권장)
```bash
# 전체 배포 스크립트 실행
chmod +x deploy_managed.sh
./deploy_managed.sh
```

### 2단계: 수동 배포

#### 2.1. GCP 서비스 활성화
```bash
gcloud services enable \
    compute.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    run.googleapis.com \
    vpcaccess.googleapis.com \
    servicenetworking.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com
```

#### 2.2. 서비스 계정 생성
```bash
# Vertex AI 서비스 계정
gcloud iam service-accounts create vertex-ai-service-account \
    --display-name="Vertex AI Service Account"

# 권한 부여
gcloud projects add-iam-policy-binding godwind2015 \
    --member="serviceAccount:vertex-ai-service-account@godwind2015.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding godwind2015 \
    --member="serviceAccount:vertex-ai-service-account@godwind2015.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

#### 2.3. Terraform 인프라 배포
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

#### 2.4. Docker 이미지 빌드 및 배포
```bash
# API 서비스
docker build -f Dockerfile.api -t gcr.io/godwind2015/mk-news-api .
docker push gcr.io/godwind2015/mk-news-api

# 관리자 앱
docker build -f Dockerfile.admin -t gcr.io/godwind2015/mk-news-admin .
docker push gcr.io/godwind2015/mk-news-admin
```

#### 2.5. Cloud Run 서비스 배포
```bash
# API 서비스 배포
gcloud run deploy mk-news-api \
    --image gcr.io/godwind2015/mk-news-api \
    --platform managed \
    --region asia-northeast3 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 10 \
    --vpc-connector mk-news-connector \
    --set-env-vars="GCP_PROJECT_ID=godwind2015,GCP_REGION=asia-northeast3,USE_MANAGED_SERVICES=true"

# 관리자 앱 배포
gcloud run deploy mk-news-admin \
    --image gcr.io/godwind2015/mk-news-admin \
    --platform managed \
    --region asia-northeast3 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --vpc-connector mk-news-connector \
    --set-env-vars="GCP_PROJECT_ID=godwind2015,GCP_REGION=asia-northeast3,USE_MANAGED_SERVICES=true"
```

## 🔐 인증 설정

### 1. 서비스 계정 키 생성
```bash
# 서비스 계정 키 생성
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=vertex-ai-service-account@godwind2015.iam.gserviceaccount.com

# Cloud Run에 시크릿으로 업로드
gcloud secrets create vertex-ai-key --data-file=service-account-key.json
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
cp env.example .env

# 필요한 값들 수정
nano .env
```

## 📊 모니터링 및 로깅

### 1. Cloud Monitoring 설정
- Cloud Run 메트릭 자동 수집
- 커스텀 메트릭 설정 가능
- 알림 정책 구성

### 2. Cloud Logging 설정
- 애플리케이션 로그 자동 수집
- 로그 기반 메트릭 생성
- 로그 보존 정책 설정

## 🔧 문제 해결

### 1. 일반적인 문제들

#### Cloud SQL 연결 실패
```bash
# Private IP 확인
gcloud sql instances describe mk-news-db --format="value(ipAddresses[0].ipAddress)"

# VPC 커넥터 상태 확인
gcloud compute networks vpc-access connectors describe mk-news-connector --region=asia-northeast3
```

#### Vertex AI 인증 실패
```bash
# 서비스 계정 권한 확인
gcloud projects get-iam-policy godwind2015

# Application Default Credentials 설정
gcloud auth application-default login
```

#### Cloud Run 배포 실패
```bash
# 로그 확인
gcloud run services logs read mk-news-api --region=asia-northeast3

# 서비스 상태 확인
gcloud run services describe mk-news-api --region=asia-northeast3
```

### 2. 성능 최적화

#### Cloud Run 설정
- CPU: 2 vCPU (API), 1 vCPU (Admin)
- Memory: 4Gi (API), 2Gi (Admin)
- Concurrency: 80
- Min instances: 0 (비용 절약)
- Max instances: 10 (API), 5 (Admin)

#### Cloud SQL 설정
- Private IP 사용
- SSL 연결 필수
- Connection pooling 활성화

## 💰 비용 최적화

### 1. Cloud Run
- Min instances를 0으로 설정하여 유휴 시간 비용 절약
- CPU 할당을 요청 시에만 설정
- 적절한 메모리 할당

### 2. Cloud SQL
- 개발 환경에서는 Shared-core 인스턴스 사용
- 자동 백업 설정으로 스토리지 비용 관리

### 3. Vertex AI
- 벡터 인덱스는 필요할 때만 생성
- 임베딩 모델은 캐싱 활용

## 🔄 업데이트 및 유지보수

### 1. 코드 업데이트
```bash
# 새 이미지 빌드 및 배포
docker build -f Dockerfile.api -t gcr.io/godwind2015/mk-news-api:latest .
docker push gcr.io/godwind2015/mk-news-api:latest

# Cloud Run 서비스 업데이트
gcloud run services update mk-news-api \
    --image gcr.io/godwind2015/mk-news-api:latest \
    --region asia-northeast3
```

### 2. 데이터베이스 마이그레이션
```bash
# 마이그레이션 실행
gcloud run jobs create db-migration \
    --image gcr.io/godwind2015/mk-news-api \
    --region asia-northeast3 \
    --command="python" \
    --args="src/database/migrate.py"
```

## 📞 지원 및 문의

- **프로젝트**: godwind2015
- **리전**: asia-northeast3
- **이메일**: godwind2015@gmail.com

## 📚 추가 자료

- [GCP Cloud Run 문서](https://cloud.google.com/run/docs)
- [Vertex AI 문서](https://cloud.google.com/vertex-ai/docs)
- [Cloud SQL 문서](https://cloud.google.com/sql/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
