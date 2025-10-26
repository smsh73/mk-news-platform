#!/bin/bash

# 매일경제 신문기사 벡터임베딩 플랫폼 - 매니지드 서비스 재시작 스크립트

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

echo -e "${BLUE}🔄 매일경제 신문기사 벡터임베딩 플랫폼 - 매니지드 서비스 재시작${NC}"
echo -e "${BLUE}프로젝트: ${PROJECT_ID}${NC}"
echo -e "${BLUE}리전: ${REGION}${NC}"
echo ""

# 1. Cloud SQL 인스턴스 재시작
echo -e "${YELLOW}📋 1단계: Cloud SQL 인스턴스 재시작${NC}"

echo -e "${BLUE}🔄 Cloud SQL 인스턴스 재시작 중...${NC}"
gcloud sql instances patch mk-news-db \
    --activation-policy=ALWAYS

# 인스턴스가 완전히 시작될 때까지 대기
echo -e "${BLUE}⏳ Cloud SQL 인스턴스 시작 대기 중...${NC}"
gcloud sql instances describe mk-news-db --format="value(state)" | grep -q "RUNNABLE" || {
    echo -e "${BLUE}⏳ Cloud SQL 인스턴스가 완전히 시작될 때까지 대기 중...${NC}"
    sleep 30
}

echo -e "${GREEN}✅ Cloud SQL 인스턴스 재시작 완료${NC}"

# 2. Cloud Run 서비스 재시작
echo -e "${YELLOW}📋 2단계: Cloud Run 서비스 재시작${NC}"

# FastAPI 서비스 트래픽 복원
echo -e "${BLUE}🔄 FastAPI 서비스 트래픽 복원 중...${NC}"
gcloud run services update-traffic mk-news-api \
    --region=${REGION} \
    --to-revisions=LATEST=100

# Streamlit 서비스 트래픽 복원
echo -e "${BLUE}🔄 Streamlit 서비스 트래픽 복원 중...${NC}"
gcloud run services update-traffic mk-news-admin \
    --region=${REGION} \
    --to-revisions=LATEST=100

echo -e "${GREEN}✅ Cloud Run 서비스 재시작 완료${NC}"

# 3. Vertex AI Vector Search 재배포
echo -e "${YELLOW}📋 3단계: Vertex AI Vector Search 재배포${NC}"

# Vector Search 엔드포인트에 인덱스 재배포
echo -e "${BLUE}🔄 Vector Search 인덱스 재배포 중...${NC}"

# 인덱스 ID 가져오기
INDEX_ID=$(gcloud ai indexes list --region=${REGION} --filter="displayName:mk-news-vector-index" --format="value(name)" | head -1)
ENDPOINT_ID=$(gcloud ai index-endpoints list --region=${REGION} --filter="displayName:mk-news-vector-endpoint" --format="value(name)" | head -1)

if [ -n "$INDEX_ID" ] && [ -n "$ENDPOINT_ID" ]; then
    gcloud ai index-endpoints deploy-index ${ENDPOINT_ID} \
        --region=${REGION} \
        --deployed-index-id=mk_news_deployed_index \
        --index=${INDEX_ID} \
        --display-name="매일경제 신문기사 벡터 검색" \
        --description="매일경제 신문기사 벡터 검색 배포"
    
    echo -e "${GREEN}✅ Vertex AI Vector Search 재배포 완료${NC}"
else
    echo -e "${YELLOW}⚠️ Vector Search 인덱스 또는 엔드포인트를 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}⚠️ 전체 재배포를 위해 ./deploy_managed.sh를 실행하세요.${NC}"
fi

# 4. 서비스 상태 확인
echo -e "${YELLOW}📋 4단계: 서비스 상태 확인${NC}"

echo -e "${BLUE}📊 Cloud Run 서비스 상태:${NC}"
gcloud run services list --region=${REGION} --format="table(metadata.name,status.url,status.traffic[0].percent)"

echo ""
echo -e "${BLUE}📊 Cloud SQL 인스턴스 상태:${NC}"
gcloud sql instances describe mk-news-db --format="table(name,settings.activationPolicy,state)"

echo ""
echo -e "${BLUE}📊 Vertex AI Vector Search 상태:${NC}"
gcloud ai index-endpoints list --region=${REGION} --format="table(name,displayName,state)"

# 5. 서비스 URL 출력
echo -e "${YELLOW}📋 5단계: 서비스 접속 정보${NC}"

# 서비스 URL 가져오기
API_URL=$(gcloud run services describe mk-news-api --region=${REGION} --format="value(status.url)")
ADMIN_URL=$(gcloud run services describe mk-news-admin --region=${REGION} --format="value(status.url)")

echo ""
echo -e "${GREEN}🎉 매니지드 서비스 재시작 완료!${NC}"
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
echo -e "${GREEN}✅ 매니지드 서비스가 정상적으로 재시작되었습니다!${NC}"

