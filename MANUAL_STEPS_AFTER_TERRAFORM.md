# Terraform 배포 후 수동 설정 안내

## 개요

Terraform으로 배포 후 다음 설정들을 수동으로 진행해야 합니다.

## 1. 서비스 계정 IAM 권한 부여

서비스 계정: `mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com`

Cloud Console에서 다음 역할 부여:
1. IAM & Admin → IAM
2. "mk-news-platform" 서비스 계정 찾기
3. 다음 역할 추가:
   - `roles/aiplatform.user`
   - `roles/storage.admin`
   - `roles/cloudsql.client`
   - `roles/secretmanager.secretAccessor`
   - `roles/ml.developer`

## 2. Gemini API 키 추가

1. Cloud Console → Secret Manager
2. "gemini-api-key" Secret 찾기
3. "Add Version" 클릭
4. API 키 값 입력
5. "Add" 클릭

## 3. (옵션) Private IP로 전환

현재는 Public IP로 배포되었습니다. Private IP로 전환하려면:

1. Cloud Console → VPC Network → VPC Peering
2. "Create Peering Connection" 클릭
3. Network: `mk-news-vpc` 선택
4. Peered Network: Service Networking 선택
5. "Create" 클릭
6. Cloud SQL 인스턴스 재시작 (Private IP 활성화)

## 4. (옵션) Vertex AI Index Endpoint Private 설정

현재는 Public으로 배포되었습니다. Private으로 전환하려면:

1. Terraform에서 주석 제거
2. `terraform apply` 재실행

## 참고

- 현재 설정은 **테스트 환경**을 위한 것입니다
- **프로덕션 환경**에서는 모든 리소스를 Private으로 설정해야 합니다
