# 최종 CI/CD 설정 단계

## ✅ 완료된 작업

1. ✅ GitHub 저장소 생성: https://github.com/smsh73/mk-news-platform
2. ✅ 로컬 코드 푸시 완료
3. ✅ GitHub Actions 워크플로 파일 생성 및 수정 완료

## 🔧 남은 작업

### 1단계: 서비스 계정 키 준비

서비스 계정 키가 이미 있으면 (`~/mk-news-key.json`) 이 단계를 스킵하세요.

```bash
# 서비스 계정 키 생성
gcloud iam service-accounts keys create ~/mk-news-key.json \
  --iam-account=mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com \
  --project=mk-ai-project-473000

# 키를 Base64로 인코딩
base64 -i ~/mk-news-key.json
```

### 2단계: GitHub Secrets 설정

1. **GitHub 저장소로 이동**: https://github.com/smsh73/mk-news-platform/settings/secrets/actions

2. **"New repository secret" 클릭하여 다음 Secret 추가**:

   **Secret 1:**
   - Name: `GCP_SERVICE_ACCOUNT_KEY`
   - Value: 1단계에서 복사한 Base64 인코딩된 전체 내용 (한 줄)

   **Secret 2:**
   - Name: `GCP_PROJECT_ID`
   - Value: `mk-ai-project-473000`

### 3단계: 테스트 배포

GitHub Actions가 자동으로 실행되는지 확인:

1. 코드에 작은 변경사항 추가:
   ```bash
   echo "# CI/CD Test" >> README.md
   git add README.md
   git commit -m "Test CI/CD"
   git push origin main
   ```

2. GitHub 저장소의 "Actions" 탭에서 빌드 상태 확인:
   https://github.com/smsh73/mk-news-platform/actions

## 📋 작업 흐름 (설정 완료 후)

1. **Cursor에서 코드 수정**
2. **커밋 및 푸시**:
   ```bash
   git add .
   git commit -m "변경사항 설명"
   git push origin main
   ```
3. **자동 배포**: GitHub Actions가 자동으로 감지하여 빌드 및 배포 수행

## 🔍 확인 방법

- **GitHub Actions 로그**: https://github.com/smsh73/mk-news-platform/actions
- **Cloud Build 로그**: 
  ```bash
  gcloud builds list --limit=5 --project=mk-ai-project-473000
  ```
- **Cloud Run 배포 확인**:
  ```bash
  gcloud run services list --project=mk-ai-project-473000
  ```

## ⚠️ 보안 참고사항

- Personal Access Token을 공개 저장소에 커밋하지 마세요
- 서비스 계정 키는 GitHub Secrets에만 저장하세요
- `.gitignore`에 키 파일이 포함되어 있는지 확인하세요

## 🎯 다음 단계

위의 "1단계: 서비스 계정 키 준비"부터 진행하세요!
