# CI/CD 문제 해결 다음 단계

## 현재 상황

여전히 Cloud Build 버킷 접근 권한 오류가 발생하고 있습니다.

## 추가로 시도할 방법

### 방법 1: 서비스 계정에 Editor 권한 부여 (임시 해결책)

```bash
gcloud projects add-iam-policy-binding mk-ai-project-473000 \
  --member="serviceAccount:mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com" \
  --role="roles/editor"
```

주의: Editor 권한은 매우 광범위한 권한입니다. 프로덕션 환경에서는 최소 권한 원칙에 따라 더 세밀한 권한 설정을 권장합니다.

### 방법 2: GitHub Actions에서 직접 Docker 빌드 및 배포

Cloud Build를 거치지 않고 GitHub Actions에서 직접:
1. Docker 이미지 빌드
2. Artifact Registry에 푸시
3. Cloud Run 배포

### 방법 3: Cloud Build 트리거 사용

GitHub 저장소를 Cloud Build에 연결하고 트리거를 사용하는 방법.

### 방법 4: 버킷 정책 확인

조직 정책이나 버킷 레벨 정책에서 서비스 계정 접근을 제한하고 있는지 확인:
```bash
gcloud organizations list
gsutil iam get gs://mk-ai-project-473000_cloudbuild
```

## 최신 실행 확인

최신 실행의 상세 로그를 확인하여 정확한 오류 메시지를 파악해야 합니다:
https://github.com/smsh73/mk-news-platform/actions

## 권장 사항

1. **먼저 Editor 권한으로 테스트** - 문제가 해결되면, 점진적으로 권한을 줄여나가면서 최소 권한을 찾습니다.

2. **로그 직접 확인** - GitHub Actions 페이지에서 실패한 워크플로의 "Deploy to Cloud Run" 단계 로그를 확인하여 정확한 오류 메시지를 확인합니다.

3. **로컬 테스트** - 서비스 계정 키로 로컬에서 Cloud Build가 정상 작동하는지 확인:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/mk-news-key.json
gcloud builds submit --config=cloudbuild-api.yaml --project=mk-ai-project-473000
```

## 현재 설정된 권한 요약

✅ `roles/cloudbuild.builds.builder`
✅ `roles/artifactregistry.writer`
✅ `roles/serviceusage.serviceUsageConsumer`
✅ `roles/storage.admin`
✅ `roles/run.admin`
✅ 버킷 레벨: `storage.objectCreator`, `storage.objectViewer`

이론적으로는 충분한 권한이지만, 여전히 버킷 접근이 거부되고 있습니다.
