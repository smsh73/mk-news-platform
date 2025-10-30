# CI/CD 설정 진행 단계

## 1단계: Cloud Source Repositories API 활성화 (수동) - 진행 중

현재 API 활성화 권한이 CLI에서는 제한되어 있습니다. 브라우저에서 직접 활성화해주세요:

**방법 1: 직접 링크**
https://console.developers.google.com/apis/api/sourcerepo.googleapis.com/overview?project=mk-ai-project-473000

**방법 2: GCP 콘솔에서**
1. https://console.cloud.google.com 접속
2. 프로젝트: mk-ai-project-473000 선택
3. "API 및 서비스" > "라이브러리" 메뉴
4. "Cloud Source Repositories API" 검색 후 활성화

활성화 후 2-3분 기다린 다음 다음 단계 진행하세요.

## 2단계: Git 저장소 초기화 (완료)

✅ Git 저장소 초기화 완료
✅ 변경사항 커밋 완료
✅ Git 인증 설정 완료

## 3단계: Cloud Source Repository 생성 (API 활성화 대기 중)

API가 활성화되면 다음 명령어를 실행하세요:

```bash
# Cloud Source Repository 생성
gcloud source repos create mk-news-platform --project=mk-ai-project-473000

# 원격 저장소 추가
git remote add google https://source.developers.google.com/p/mk-ai-project-473000/r/mk-news-platform

# 코드 푸시
git push google main
```

## 4단계: Cloud Build 트리거 설정

API 활성화 후 다음 명령어를 실행하세요:

```bash
# Cloud Build 트리거 생성
gcloud builds triggers create cloud-source-repositories \
  --name="auto-deploy-mk-news-admin" \
  --repo="mk-news-platform" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild-admin.yaml" \
  --project=mk-ai-project-473000
```

## 현재 상태

- ✅ 로컬 Git 저장소 준비 완료
- ⏳ Cloud Source Repositories API 활성화 대기 중
- ⏳ Cloud Source Repository 생성 대기 중
- ⏳ Cloud Build 트리거 설정 대기 중

## 대안: GitHub 사용

API 활성화가 어려운 경우 GitHub를 사용할 수 있습니다:

1. GitHub에서 새 저장소 생성: `mk-news-platform`
2. 로컬에서 GitHub 원격 저장소 추가:
   ```bash
   git remote add origin https://github.com/your-username/mk-news-platform.git
   git push -u origin main
   ```
3. GitHub Actions 워크플로 설정 (`.github/workflows/deploy.yml`)

어떤 방법을 선택하시겠습니까?