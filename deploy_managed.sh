#!/bin/bash

# 매일경제 신문기사 벡터임베딩 플랫폼 - 매니지드 서비스 배포 스크립트
# GCP Cloud Run + Cloud SQL + Vertex AI 기반 매니지드 아키텍처

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 설정
PROJECT_ID="godwind2015"
REGION="asia-northeast3"
ZONE="asia-northeast3-a"

echo -e "${BLUE}🚀 매일경제 신문기사 벡터임베딩 플랫폼 - 매니지드 서비스 배포${NC}"
echo -e "${BLUE}프로젝트: ${PROJECT_ID}${NC}"
echo -e "${BLUE}리전: ${REGION}${NC}"
echo ""

# 1. GCP 인증 및 프로젝트 설정
echo -e "${YELLOW}📋 1단계: GCP 인증 및 프로젝트 설정${NC}"
gcloud auth login --account=godwind2015@gmail.com
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud config set compute/zone ${ZONE}

echo -e "${GREEN}✅ GCP 인증 완료${NC}"

# 2. 필수 서비스 활성화
echo -e "${YELLOW}📋 2단계: 필수 GCP 서비스 활성화${NC}"
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

echo -e "${GREEN}✅ GCP 서비스 활성화 완료${NC}"

# 2.1. Vertex AI 서비스 계정 생성 및 권한 설정
echo -e "${YELLOW}📋 2.1단계: Vertex AI 서비스 계정 설정${NC}"
SERVICE_ACCOUNT_NAME="vertex-ai-service-account"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# 서비스 계정 생성 (이미 존재하면 무시)
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="Vertex AI Service Account" \
    --description="Service account for Vertex AI operations" \
    2>/dev/null || echo "서비스 계정이 이미 존재합니다."

# 필요한 권한 부여
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/aiplatform.serviceAgent"

echo -e "${GREEN}✅ Vertex AI 서비스 계정 설정 완료${NC}"

# 3. Terraform 인프라 배포
echo -e "${YELLOW}📋 3단계: Terraform 인프라 배포${NC}"
cd terraform

# Terraform 초기화
terraform init

# Terraform 플랜 확인
echo -e "${BLUE}📊 Terraform 배포 계획 확인 중...${NC}"
terraform plan

# 사용자 확인
read -p "위의 계획으로 인프라를 배포하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 배포가 취소되었습니다.${NC}"
    exit 1
fi

# Terraform 적용
echo -e "${BLUE}🏗️ 인프라 배포 중...${NC}"
terraform apply -auto-approve

echo -e "${GREEN}✅ Terraform 인프라 배포 완료${NC}"

# 4. Artifact Registry 설정
echo -e "${YELLOW}📋 4단계: Artifact Registry 설정${NC}"
cd ..

# Docker 인증 설정
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# 5. 컨테이너 이미지 빌드 및 푸시
echo -e "${YELLOW}📋 5단계: 컨테이너 이미지 빌드 및 푸시${NC}"

# FastAPI 이미지 빌드 및 푸시
echo -e "${BLUE}🔨 FastAPI 이미지 빌드 중...${NC}"
docker build -f Dockerfile.api -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/mk-news-repo/mk-news-api:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/mk-news-repo/mk-news-api:latest

# Streamlit 이미지 빌드 및 푸시
echo -e "${BLUE}🔨 Streamlit 이미지 빌드 중...${NC}"
docker build -f Dockerfile.admin -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/mk-news-repo/mk-news-admin:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/mk-news-repo/mk-news-admin:latest

echo -e "${GREEN}✅ 컨테이너 이미지 빌드 및 푸시 완료${NC}"

# 6. Cloud Run 서비스 배포
echo -e "${YELLOW}📋 6단계: Cloud Run 서비스 배포${NC}"

# Terraform 출력값 가져오기
API_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/mk-news-repo/mk-news-api:latest"
ADMIN_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/mk-news-repo/mk-news-admin:latest"

# Cloud Run 서비스 이미지 업데이트
echo -e "${BLUE}🔄 Cloud Run 서비스 이미지 업데이트 중...${NC}"

# FastAPI 서비스 업데이트
gcloud run services update mk-news-api \
    --region=${REGION} \
    --image=${API_IMAGE} \
    --platform=managed

# Streamlit 서비스 업데이트
gcloud run services update mk-news-admin \
    --region=${REGION} \
    --image=${ADMIN_IMAGE} \
    --platform=managed

echo -e "${GREEN}✅ Cloud Run 서비스 배포 완료${NC}"

# 7. 서비스 URL 출력
echo -e "${YELLOW}📋 7단계: 배포 결과 확인${NC}"

# 서비스 URL 가져오기
API_URL=$(gcloud run services describe mk-news-api --region=${REGION} --format="value(status.url)")
ADMIN_URL=$(gcloud run services describe mk-news-admin --region=${REGION} --format="value(status.url)")

echo ""
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo ""
echo -e "${BLUE}📊 서비스 정보:${NC}"
echo -e "  • FastAPI 서비스: ${API_URL}"
echo -e "  • 관리자 대시보드: ${ADMIN_URL}"
echo ""
echo -e "${BLUE}🔧 관리 명령어:${NC}"
echo -e "  • 서비스 중지: ./stop_managed.sh"
echo -e "  • 로그 확인: gcloud run logs tail mk-news-api --region=${REGION}"
echo -e "  • 서비스 상태: gcloud run services list --region=${REGION}"
echo ""
echo -e "${GREEN}✅ 매니지드 서비스 배포가 완료되었습니다!${NC}"

