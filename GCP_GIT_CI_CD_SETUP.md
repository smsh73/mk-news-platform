# GCP Git 연동 및 CI/CD 자동화 설정 가이드

## 개요

소스코드를 GCP의 Git 저장소로 옮기고, Cursor에서 작업 후 커밋→Push→배포가 자동으로 이루어지도록 설정합니다.

## 방법 선택

### 옵션 1: Cloud Source Repositories (GCP 네이티브) - 추천
- GCP 프로젝트 내에서 모든 것이 관리됨
- Cloud Build와 완벽 통합
- 별도 계정 관리 불필요

### 옵션 2: GitHub + Cloud Build 연동
- GitHub UI 사용 가능
- 더 많은 기능과 생태계
- OIDC 인증으로 보안 강화

## 옵션 1: Cloud Source Repositories 설정 (추천)

### 1단계: Cloud Source Repository 생성

```bash
# Cloud Source Repositories API 활성화 (처음 사용 시)
gcloud services enable sourcerepo.googleapis.com --project=mk-ai-project-473000

# Cloud Source Repository 생성
gcloud source repos create mk-news-platform \
  --project=mk-ai-project-473000

# 리포지토리 URL 확인
gcloud source repos describe mk-news-platform \
  --project=mk-ai-project-473000 \
  --format="value(url)"
```

### 2단계: 로컬 Git 저장소 초기화 및 푸시

```bash
# 프로젝트 디렉토리로 이동
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"

# Git 초기화 (이미 있으면 스킵)
git init

# .gitignore 파일이 없으면 생성 (이미 생성됨)

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: 매일경제 신문기사 벡터임베딩 플랫폼"

# Cloud Source Repository에 푸시
git remote add google \
  https://source.developers.google.com/p/mk-ai-project-473000/r/mk-news-platform

# 인증 설정 (GCP 로그인 필요)
git config credential.helper gcloud.sh

# 푸시 (main 브랜치가 없으면 생성)
git branch -M main 2>/dev/null || git checkout -b main
git push google main
```

### 3단계: Cloud Build 트리거 생성

```bash
# Cloud Build 트리거 생성 (cloudbuild-admin.yaml 사용)
gcloud builds triggers create cloud-source-repositories \
  --name="auto-deploy-mk-news-admin" \
  --repo="mk-news-platform" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild-admin.yaml" \
  --project=mk-ai-project-473000
```

### 4단계: Cursor에서 작업 흐름

1. **코드 수정** (Cursor에서)
2. **커밋 및 푸시**:
   ```bash
   git add .
   git commit -m "변경사항 설명"
   git push google main
   ```
3. **자동 배포**: Cloud Build가 자동으로 감지하여 빌드 및 배포 수행

## 옵션 2: GitHub + Cloud Build 연동

### 1단계: GitHub 저장소 생성

1. GitHub에서 새 저장소 생성: `mk-news-platform`
2. 저장소 URL 확인 (예: `https://github.com/your-username/mk-news-platform.git`)

### 2단계: 로컬 Git 설정 및 GitHub 푸시

```bash
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"

# Git 초기화
git init

# GitHub 원격 저장소 추가
git remote add origin https://github.com/your-username/mk-news-platform.git

# 커밋 및 푸시
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main
```

### 3단계: GitHub OIDC 인증 설정 (보안 강화)

```bash
# 워크로드 ID 풀 생성
gcloud iam workload-identity-pools create github-pool \
  --project="mk-ai-project-473000" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# 워크로드 ID 공급자 생성
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project="mk-ai-project-473000" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 서비스 계정 권한 부여 (your-username을 실제 사용자명으로 변경)
gcloud iam service-accounts add-iam-policy-binding \
  mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com \
  --project="mk-ai-project-473000" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/mk-ai-project-473000/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-username/mk-news-platform"
```

### 4단계: GitHub Actions 워크플로 생성

`.github/workflows/deploy.yml` 파일 생성:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: amount
      id-token: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/mk-ai-project-473000/locations/global/workloadIdentityPools/github-pool/providers/github-provider
          service_account: mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Deploy to Cloud Run
        run: |
          gcloud builds submit --config=cloudbuild-admin.yaml \
            --project=mk-ai-project-473000
```

### 5단계: Cloud Build 트리거 생성 (GitHub용)

```bash
# GitHub 연결 (처음만)
gcloud builds triggers create github \
  --name="github-auto-deploy" \
  --repo-name="mk-news-platform" \
  --repo-owner="your-username" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild-admin.yaml" \
  --project=mk-ai-project-473000
```

## 작업 흐름 비교

### 현재 (로컬)
1. Cursor에서 코드 수정
2. 터미널에서 Docker 빌드 → Push → 배포 (수동, 오래 걸림)

### CI/CD 적용 후
1. Cursor에서 코드 수정
lit 2. Git 커밋 및 푸시培训 3. **자동으로** Cloud Build가 빌드 및 배포 수행

## 장점

### 시간 절약
- 로컬 빌드: 20-30분
- Cloud Build: 10-15분 (GCP 인프라 활용)

### 편의성
- 커밋만으로 자동 배포
- 빌드 로그 자동 저장
- 배포 이력 관리

### 보안
- 서비스 계정 키 불필요
- OIDC 인증 사용
- 권한 관리 용이

## 다음 단계

1. **Git 저장소 선택**: Cloud Source Repositories 또는 GitHub
2. **저장소 초기화**: 위 가이드 따라 진행
3. **트리거 설정**: 자동 배포 활성화
4. **테스트**: 간단한 변경사항 푸시하여 자동 배포 확인

## 문제 해결

### Git 인증 오류
```bash
git config credential.helper gcloud.sh
```

### Cloud Build 권한 오류
```bash
gcloud projects add-iam-policy-binding mk-ai-project-473000 \
  --member="serviceAccount:mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"
```

### 배포 실패 시
- Cloud Build 로그 확인:
  ```bash
  gcloud builds list --limit=5 --project=mk-ai-project-473000
  ```
