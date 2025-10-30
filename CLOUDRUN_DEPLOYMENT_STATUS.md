# Cloud Run 배포 현황 및 재생성 방법

## 현재 상황

### ✅ **GCP 리소스 배포 상태**

1. **VPC Network**: 정상 작동
2. **Cloud SQL**: 정상 작동 (Public IP: 34.64.172.232)
3. **Storage Buckets**: 3개 모두 정상
4. **Artifact Registry**: DOCKER 저장소 준비 완료
5. **Vertex AI Endpoint**: 정상 작동
6. **Service Account**: 생성 완료
7. **VPC Connector**: 정상 작동

### ❌ **Cloud Run**: 삭제됨

Terraform Plan 결과: "Listed 0 items" (Cloud Run 서비스 없음)

## Terraform의 리소스 관리 원리

### 중복 생성 방지
- **No**: Terraform은 State 파일로 리소스 상태를 추적
- 이미 존재하는 리소스는 "No changes"로 표시
- **중복 생성 안 됨**

### 임의 삭제된 리소스 재생성
- **reload**: `terraform refresh`가 실제 GCP 상태를 확인
- **plan**: State와 실제 상태를 비교
- **결과**: State에는 있지만 실제로는 삭제된 리소스 → 재생성 계획

### 리소스 상태 확인
- **apply 전**: `terraform plan`으로 변경사항 확인
- **apply 후**: 모든 리소스가 State와 실제 상태 일치

## Cloud Run을 재생성하려면

### 옵션 1: Terraform으로 재생성 (권장)
현재 Cloud Run 리소스가 주석 처리되어 있어서 재생성 안 됨

**주석 해제 필요**: `terraform/main.tf` line 385-548
- `google_cloud_run_v2_service.mk_news_api` 주석 해제
- `google_cloud_run_v2_service.mk_news_admin` 주석 해제
- IAM 리소스도 함께 주석 해제

**주의사항**: Docker 이미지가 없으면 실패

### 옵션 2: 수동 배포 (현실적)
Cloud Run은 Docker 이미지가 필수이므로, 현재는 수동 배포가 더 적합함

```bash
# 1. Docker 이미지 빌드
gcloud builds submit --tag asia-northeast3-docker.pkg.dev/mk-ai-project-473000/mk-news-repo/mk-news-api:latest

# 2. Cloud Run 배포
gcloud run deploy mk-news-api \
  --image asia-northeast3-docker.pkg.dev/mk-ai-project-473000/mk-news-repo/mk-news-api:latest \
  --region asia-northeast3 \
  --allow-unauthenticated
```

## 요구사항 처리 방법

### 1. 임의 삭제된 리소스 재생성
**현재**: Cloud Run 주석 처리됨 → 재생성 안 됨
**해결**: 주석 해제 후 `terraform apply`

### 2. 기존 리소스 재확인
**자동**: `terraform plan`과 `terraform apply`가 모든 리소스 상태 확인
**결과**: "No changes" 표시되면 정상

### 3. 중복 생성 방지
**자동**: Terraform State로 관리
**확인**: `terraform state list`로 관리되는 리소스 확인

## 권장사항

1. **Cloud Run은 수동 배포**: Docker 이미지가 필수이므로 gcloud 명령어로 배포
2. **Terraform은 주석 유지**: 이미지 빌드 후 주석 해제
3. **기존 리소스**: Terraform이 자동으로 상태 확인 및 유지
