# Docker 이미지 빌드 및 Cloud Run 배포 가이드

## 요약

**현재 상황**: 관리자 애플리케이션 Docker 이미지가 필요합니다.

**필요 작업**: Dockerfile.admin을 사용하여 이미지를 빌드하고 Cloud Run에 배포

## 실행 명령어

### 1. 환경 변수 설정
```bash
export PROJECT_ID=mk-ai-project-473000
export REGION=asia-northeast3
export REPO=mk-news-repo
export IMAGE_NAME=mk-news-admin
```

### 2. Docker 이미지 빌드 및 푸시
```bash
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"

gcloud builds submit \
  --tag asia-northeast3-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:latest \
  --timeout=1800s \
  -f Dockerfile.admin
```

**예상 시간**: 10-20분 (빌드 및 푸시)

### 3. Cloud Run 배포
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

**예상 시간**: 2-3분

### 4. 접속 URL 확인
```bash
gcloud run services describe mk-news-admin \
  --region=asia-northeast3 \
  --format='value(status.url)'
```

## Dockerfile 설명

**Dockerfile.admin** (관리자 애플리케이션)
- Base Image: `python:3.11-slim` (Python 3.13 호환성 문제 해결)
- 설치: Google Cloud SDK, 필요한 Python 패키지
- 포트: 8501 (Streamlit 기본 포트)
- 실행: Streamlit 관리자 대시보드

## 특징

1. Python 3.11 사용 (로컬 3.13 호환성 문제 해결)
2. GCP 서비스 계정 자동 인증
3. VPC Connector 연결 (Private IP 접근)
4. 헬스체크 포함
5. Cloud Run 환경 변수 자동 인식

## 배포 후 확인 사항

1. ✅ Cloud Run 서비스가 Running 상태인지 확인
2. ✅ 외부 접속 가능 여부 확인 (--allow-unauthenticated)
3. ✅ 로그에서 에러 메시지 확인
4. ✅ Terraform State에 추가 (옵션)

## 전체 프로세스 소요 시간

- Docker 빌드 및 푸시: 10-20분
- Cloud Run 배포: 2-3분
- **총 예상 시간: 15-25분**

## 다음 단계

1. `BUILD_DOCKER_IMAGE.md`에서 상세 가이드 참고
2. 위 명령어를 순서대로 실행
3. 배포 완료 후 접속 URL로 관리자 대시보드 접속
4. GCP 인프라 관리 기능 테스트

## 추가 정보

- **requirements.txt**: Python 3.11에서 정상 설치됨
- **Docker Build**: Cloud Build 서비스 사용
- **이미지 저장소**: Artifact Registry (asia-northeast3)
- **배포 서비스**: Cloud Run (fully managed)
