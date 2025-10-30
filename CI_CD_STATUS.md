# CI/CD 설정 현황

## 완료된 작업

✅ **GitHub 저장소 연결**
- 저장소: https://github.com/smsh73/mk-news-platform
- GitHub Actions 워크플로 파일 설정 완료

✅ **서비스 계정 설정**
- 서비스 계정: `mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com`
- GitHub Secrets에 서비스 계정 키 설정 완료

✅ **IAM 권한 설정**
서비스 계정에 다음 권한이 부여되었습니다:
- `roles/cloudbuild.builds.builder` - Cloud Build 실행 권한
- `roles/artifactregistry.writer` - Artifact Registry 쓰기 권한
- `roles/serviceusage.serviceUsageConsumer` - 서비스 사용 권한
- `roles/storage.admin` - Cloud Storage 버킷 접근 권한

✅ **API 활성화**
- Cloud Build API
- Cloud Storage API
- Artifact Registry API

## 현재 문제

**오류 메시지:**
```
ERROR: (gcloud.builds.submit) The user is forbidden from accessing the bucket [mk-ai-project-473000_cloudbuild]. 
Please check your сайте's policy or if the user has the "serviceusage.services.use" permission.
```

**해결 시도:**
1. ✅ `roles/serviceusage.serviceUsageConsumer` 권한 추가
2. ✅ `roles/storage.admin` 권한 추가

**권한 확인:**
```bash
gcloud projects get-iam-policy mk-ai-project-473000 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

## 가능한 원인

1. **IAM 권한 전파 지연**
   - IAM 권한 변경이 완전히 전파되는 데 최대 10분 정도 걸릴 수 있습니다.
   - 권한 추가 후 몇 분 기다린 후 다시 테스트해보세요.

2. **조직 정책 (Organization Policy)**
   - GCP whitelist 정책이나 리소스 접근 제한이 있을 수 있습니다.
   - GCP 콘솔에서 조직 정책을 확인해보세요.

3. **버킷 레벨 권한**
   - 프로젝트 레벨 권한 외에 버킷 자체에 대한 특별한 권한이 필요할 수 있습니다.
   - 다음 명령어로 버킷 IAM 정책 확인:
   ```bash
   gsutil iam get gs://mk-ai-project-473000_cloudbuild
   ```

## 다음 단계

1. **권한 전파 대기**
   - 권한 추가 후 5-10분 기다린 후 다시 테스트

2. **버킷 IAM 확인**
   - Cloud Storage 버킷에 대한 직접 권한 확인

3. **조직 정책 확인**
   - GCP 콘솔에서 조직 정책 확인

4. **로컬 테스트**
   - 서비스 계정 키로 로컬에서 Cloud Build 실행 테스트:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=~/mk-news-key.json
   gcloud builds submit --config=cloudbuild-api.yaml --project=mk-ai-project-473000
   ```

## 워크플로 파일 위치

- `.github/workflows/deploy-api.yml` - API 배포 워크플로
- `.github/workflows/deploy-admin.yml` - Admin 배포 워크플로

## 테스트 방법

GitHub에 푸시하면 자동으로 워크플로가 실행됩니다:
```bash
git add .
git commit -m "Test: CI/CD"
git push origin main
```

워크플로 상태 확인:
https://github.com/smsh73/mk-news-platform/actions
