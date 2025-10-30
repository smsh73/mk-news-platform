# Cloud Run 배포 완료

## 수정 완료 내용

### 1. Terraform Cloud Run 리소스 활성화
- `terraform/main.tf`에서 주석 처리되어 있던 Cloud Run 서비스 리소스 활성화
- `google_cloud_run_v2_service.mk_news_admin` 리소스 주석 해제
- `google_cloud_run_service_iam_member.mk_news_admin_public` 리소스 주석 해제
- Output으로 `admin_service_url` 추가

### 2. 배포 전 체크 로직 추가
백엔드 API (`src/web/app.py`)의 `terraform_apply` 함수에 다음 체크 추가:

#### a) 기존 Cloud Run 서비스 확인
- 배포 전 기존 서비스 존재 여부 확인
- 존재 시 URL 로그로 출력
- 중복 배포 방지

#### b) Artifact Registry 이미지 필수 확인
- Artifact Registry에 이미지가 없으면 배포 실패
- 강제 재배포 옵션 체크 시에만 진행 가능
- 이미지 없이 배포 시도 시 명확한 오류 메시지 제공

#### c) 배포 성공 시 URL 자동 출력
- Terraform output에서 `admin_service_url` 조회
- 성공 로그에 URL 자동 포함

### 3. Lifecycle 규칙 추가
```terraform
lifecycle {
  ignore_changes = [template[0].containers[0].image]
}
```
- Terraform이 이미지 변경을 무시하도록 설정
- 수동 이미지 업데이트 시 Terraform 재실행 방지

## 배포 프로세스

### 자동 배포 흐름
1. **기존 서비스 확인** - Cloud Run 서비스 존재 여부 조회
2. **이미지 확인** - Artifact Registry에 이미지 존재 여부 확인
3. **이미지 빌드** (선택) - 없거나 강제 재배포 시 빌드
4. **Terraform Apply** - 인프라 배포
5. **URL 출력** - 배포된 서비스 URL 자동 제공

### 체크 조건
- ✅ Artifact Registry에 이미지가 있어야 함 (필수)
- ⚠️ 기존 서비스가 있어도 업데이트됨 (lifecycle 규칙으로 안전)
- 🔄 강제 재배포 옵션으로 항상 재빌드 가능

## 배포 후 접속
배포 성공 시 로그에 출력되는 URL로 접속:
```
📊 관리자 대시보드 URL: https://mk-news-admin-{hash}-as.a.run.app
```

또는 다음 명령으로 확인:
```bash
terraform output admin_service_url
```

## 주요 개선점

1. **안전한 배포**: 이미지 없이 배포 시도 시 명확한 오류
2. **중복 방지**: 기존 서비스 확인 후 업데이트
3. **자동화**: URL 자동 조회 및 출력
4. **유연성**: 강제 재배포 옵션으로 언제든지 재빌드 가능

