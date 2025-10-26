#!/bin/bash

# 매일경제 신문기사 벡터임베딩 플랫폼 - 매니지드 서비스 중지 스크립트

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

echo -e "${BLUE}🛑 매일경제 신문기사 벡터임베딩 플랫폼 - 매니지드 서비스 중지${NC}"
echo -e "${BLUE}프로젝트: ${PROJECT_ID}${NC}"
echo -e "${BLUE}리전: ${REGION}${NC}"
echo ""

# 사용자 확인
read -p "모든 매니지드 서비스를 중지하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 중지가 취소되었습니다.${NC}"
    exit 1
fi

# 1. Cloud Run 서비스 중지
echo -e "${YELLOW}📋 1단계: Cloud Run 서비스 중지${NC}"

# FastAPI 서비스 트래픽 0%로 설정
echo -e "${BLUE}🔄 FastAPI 서비스 트래픽 중지 중...${NC}"
gcloud run services update-traffic mk-news-api \
    --region=${REGION} \
    --to-revisions=LATEST=0

# Streamlit 서비스 트래픽 0%로 설정
echo -e "${BLUE}🔄 Streamlit 서비스 트래픽 중지 중...${NC}"
gcloud run services update-traffic mk-news-admin \
    --region=${REGION} \
    --to-revisions=LATEST=0

echo -e "${GREEN}✅ Cloud Run 서비스 트래픽 중지 완료${NC}"

# 2. Cloud SQL 인스턴스 중지
echo -e "${YELLOW}📋 2단계: Cloud SQL 인스턴스 중지${NC}"

echo -e "${BLUE}🔄 Cloud SQL 인스턴스 중지 중...${NC}"
gcloud sql instances patch mk-news-db \
    --activation-policy=NEVER

echo -e "${GREEN}✅ Cloud SQL 인스턴스 중지 완료${NC}"

# 3. Vertex AI 리소스 정리
echo -e "${YELLOW}📋 3단계: Vertex AI 리소스 정리${NC}"

# Vector Search 엔드포인트에서 인덱스 제거
echo -e "${BLUE}🔄 Vector Search 인덱스 제거 중...${NC}"
gcloud ai index-endpoints undeploy-index mk-news-vector-endpoint \
    --region=${REGION} \
    --deployed-index-id=mk_news_deployed_index \
    --quiet || echo "인덱스가 이미 제거되었거나 존재하지 않습니다."

echo -e "${GREEN}✅ Vertex AI 리소스 정리 완료${NC}"

# 4. 서비스 상태 확인
echo -e "${YELLOW}📋 4단계: 서비스 상태 확인${NC}"

echo -e "${BLUE}📊 Cloud Run 서비스 상태:${NC}"
gcloud run services list --region=${REGION} --format="table(metadata.name,status.url,status.traffic[0].percent)"

echo ""
echo -e "${BLUE}📊 Cloud SQL 인스턴스 상태:${NC}"
gcloud sql instances describe mk-news-db --format="table(name,settings.activationPolicy,state)"

echo ""
echo -e "${GREEN}✅ 매니지드 서비스 중지가 완료되었습니다!${NC}"
echo ""
echo -e "${BLUE}🔧 재시작 명령어:${NC}"
echo -e "  • 서비스 재시작: ./restart_managed.sh"
echo -e "  • 전체 재배포: ./deploy_managed.sh"
echo ""
echo -e "${YELLOW}⚠️ 주의: Cloud SQL 인스턴스는 중지되었지만 데이터는 보존됩니다.${NC}"
echo -e "${YELLOW}⚠️ 주의: Vertex AI Vector Search 인덱스는 제거되었습니다.${NC}"

