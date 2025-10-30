# CI/CD 문제 해결 진행 상황

## 수행한 작업

### 1. 버킷 레벨 권한 추가
```bash
gsutil iam ch serviceAccount:mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com:roles/storage.objectCreator,roles/storage.objectViewer gs://mk-ai-project-473000_cloudbuild
```
- Cloud Build 버킷에 서비스 계정이 직접 접근할 수 있도록 권한 추가

### 2. Cloud Run 배포 권한 추가
```bash
gcloud projects add-iam-policy-binding mk-ai-project-473000 \
  --member="serviceAccount:mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```
- Cloud Run에 배포할 수 있도록 권한 추가

### 3. cloudbuild-api.yaml 파일 개선
- Cloud Run 배포 단계 추가 (기존에는 이미지 빌드만 수행)
- Artifact Registry 푸시 단계 추가
- BUILD_ID 태그를 사용한 이미지 버전 관리

## 현재 서비스 계정 권한 목록

1. `roles/cloudbuild.builds.builder` - Cloud Build 실행
2. `roles/artifactregistry.writer` - Artifact Registry 쓰기
3. `roles/serviceusage.serviceUsageConsumer` - 서비스 사용
4. `roles/storage.admin` - Cloud Storage 전체 관리
5. `roles/run.admin` - Cloud Run 관리

## 버킷 권한

- `roles/storage.objectCreator` - 버킷에 객체 생성
- `roles/storage.objectViewer` - 버킷 객체 조회

## 예상 결과

이제 GitHub Actions에서:
1. ✅ Cloud Build 버킷에 소스 코드 업로드 가능
2. ✅ Docker 이미지 빌드 가능
3. ✅ Artifact Registry에 이미지 푸시 가능
4. ✅ Cloud Run에 자동 배포 가능

## 다음 확인 사항

워크플로가 성공적으로 실행되는지 확인:
- https://github.com/smsh73/mk-news-platform/actions

성공 시:
- API 서비스: Cloud Run에 `mk-news-api` 배大人
- Admin 서비스: Cloud Run에 `mk-news-admin` 배포
