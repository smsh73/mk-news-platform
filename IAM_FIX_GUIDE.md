# Cloud Run IAM 권한 문제 해결

## 문제

```
Error 403: Permission 'run.services.setIamPolicy' denied
```

IAM 권한 설정이 거부됨

## 해결 방법

### 임시 해결 (현재 적용됨)

IAM 설정을 주석 처리하여 Cloud Run 서비스만 먼저 배포

### 배포 후 IAM 수동 설정

배포가 완료되면 다음 명령으로 공개 접근 허용:

```bash
# Cloud Run 서비스에 public 접근 허용
gcloud run services add-iam-policy-binding mk-news-admin \
  --region=asia-northeast3 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### 영구적 해결

필요한 권한을 프로젝트에 부여:

```bash
# 프로젝트에 Cloud Run Admin 역할 부여
gcloud projects add-iam-policy-binding mk-ai-project-473000 \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/run.admin"
```

## 현재 상태

- ✅ Terraform 파일 수정 완료
- ✅ IAM 설정 주석 처리
- ✅ Cloud Run 서비스만 배포 가능

## 다음 단계

1. Terraform apply 재실행
2. 배포 완료 후 IAM 설정 명령 실행
3. URL로 접속 테스트


