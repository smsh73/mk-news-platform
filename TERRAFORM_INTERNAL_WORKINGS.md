# Terraform 동작 원리 및 리소스 관리

## 요구사항 분석

사용자 요청:
1. Cloud Run 임의 삭제 시 재생성되도록
2. 기존 리소스 상태 확인 및 문제 검증
3. 중복 생성 방지

## Terraform의 기본 동작 원리

### 1. State 파일 관리
```
State 파일 (terraform.tfstate) = 실제 GCP 리소스 상태의 스냅샷
```

**동작 방식**:
- Apply 시 State 파일 업데이트
- Plan 시 State와 실제 GCP 상태 비교
- 차이점 발견 시 변경 계획 수립

### 2. 리소스 상태 확인 프로세스

#### Step 1: Refresh
```bash
terraform refresh
```
- 실제 GCP 리소스 상태를 조회
- State 파일을 실제 상태와 동기화

#### Step 2: Plan
```bash
terraform plan
```
- State와 실제 상태 비교
- 변경사항 계산
- 예상 결과 표시

#### Step 3: Apply
```bash
terraform apply
```
- 변경사항 적용
- State 파일 업데이트

### 3. 삭제된 리소스 처리

**시나리오**: Cloud Run을 콘솔에서 수동 삭제

**State 파일 상태**:
```json
{
  "resources": [
    {
      "type": "google_cloud_run_v2_service",
      "name": "mk_news_api",
      "instances": [{ "id": "projects/.../services/mk-news-api" }]
    }
  ]
}
```

**Refresh 후**:
- 실제 GCP에 `mk-news-api`가 없음
- State는 그대로 유지 (리소스가 있다고 기록)

**Plan 결과**:
```
# google_cloud_run_v2_service.mk_news_api will be created
# (because it exists in state but not in GCP)
```

**Apply 결과**:
- Cloud Run이 재생성됨

## 현재 Cloud Run 주석 처리 문제

### 문제점
- Cloud Run 리소스가 주석 처리되어 있음
- Terraform이 이 리소스를 관리하지 않음
- 삭제되어도 재생성 안 됨

### 해결 방법

#### 방법 1: 주석 해제
```terraform
resource "google_cloud_run_v2_service" "mk_news_api" {
  name     = "mk-news-api"
  location = var.region
  ...
}
```

**장점**:
- Terraform이 완전히 관리
- 삭제 시 자동 재생성

**단점**:
- Docker 이미지 필요
- 이미지 없으면 Apply 실패

#### 방법 2: 수동 배포 유지
```bash
gcloud run deploy mk-news-api --image ...
```

**장점**:
- 이미지 빌드/배포 자유
- Terraform과 독립적

**단점**:
- Terraform State에 없음
- 삭제되어도 재생성 안 됨

## 권장 해결 방안

### 단계별 접근

1. **현재**: Cloud Run 주석 유지 (이미지 없음)
2. **다음**: Docker 이미지 빌드 및 수동 배포
3. **최종**: 배포 후 Terraform State에 추가

### State에 추가하는 방법

```bash
# Cloud Run을 수동으로 배포한 후
terraform import google_cloud_run_v2_service.mk_news_api \
  projects/mk-ai-project-473000/locations/asia-northeast3-countries/kr/services/mk-news-api
```

**결과**:
- Terraform이 Cloud Run을 인식
- 이후 Terraform으로 관리 가능
- 삭제 시 재생성됨

## 기존 리소스 상태 확인

### 모든 리소스 점검
```bash
terraform plan
```

**결과 분석**:
```
No changes → 모든 리소스 정상
Plan: X to add → X개 리소스 없음 (재생성 계획)
Plan: X to change → X개 리소스 변경 필요
```

### 개별 리소스 확인
```bash
# State에 있는 리소스
terraform state list

# 실제 GCP 리소스
gcloud sql instances list
gcloud compute networks list
gcloud storage buckets list
```

## 결론

### 현재 상태
✅ 핵심 인프라 (VPC, SQL, Storage): Terraform 완전 관리
❌ Cloud Run: 주석 처리되어 관리 안 됨

### 권장 조치
1. **즉시**: 수동 배포로 Cloud Run 생성
2. **배포 후**: `terraform import`로 State 추가
3. **이후**: Terraform으로 완전 관리

이렇게 하면:
- ✅ 삭제 시 재생성됨
- ✅ 기존 리소스 상태 확인됨
- ✅ 중복 생성 방지됨
