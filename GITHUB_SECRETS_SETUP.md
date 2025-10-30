# GitHub Secrets 설정 가이드

## 현재 상황
워크로드 ID 풀 생성 권한이 제한되어 있어, 서비스 계정 키를 사용하는 방법으로 진행합니다.

## 방법 선택

### 방법 1: 서비스 계정 키 사용 (간단, 권장)
OIDC 권한이 없는 경우 이 방법을 사용합니다.

### 방법 2: Cloud Build 트리거 사용
GitHub Actions 대신 Cloud Build 트리거를 사용합니다.

## 방법 1: 서비스 계정 키 사용

### 1단계: 서비스 계정 키 생성

```bash
# 서비스 계정 키 다운로드 (기존 키가 있다면 스킵)
gcloud iam service-accounts keys create ~/mk-news-key.json \
  --iam-account=mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com \
  --project=mk-ai-project-473000

# 키 파일을 Base64로 인코딩 (GitHub Secret에 저장하기 위해)
base64 -i ~/mk-news-key.json | pbcopy
```

### 2단계: GitHub Secrets 설정

1. GitHub 저장소 페이지: https://github.com/smsh73/mk-news-platform
2. "Settings" > "Secrets and variables" > "Actions" 클릭
3. "New repository secret" 클릭하여 다음 Secret 추가:

**Secret 1: GCP_SERVICE_ACCOUNT_KEY**
- Name: `GCP_SERVICE_ACCOUNT_KEY`
- Value: 위에서 복사한 Base64 인코딩된 키 내용

**Secret 2: GCP_PROJECT_ID**
- Name: `GCP_PROJECT_ID`
- Value: `mk-ai-project-473000`

### 3단계: GitHub Actions 워크플로 수정

`.github/workflows/deploy-admin.yml` 파일을 수정하여 서비스 계정 키를 사용하도록 변경합니다.

## 방법 2: Cloud Build 트리거 사용

GitHub Actions 대신 Cloud Build 트리거를 사용하면 인증 설정이 더 간단합니다.

### 1단계: GitHub 연결

```bash
# GitHub 연결 (브라우저에서 인증 필요)
gcloud builds triggers create github \
  --name="github-auto-deploy-admin" \
  --repo-name="mk-news-platform" \
  --repo-owner="smsh73" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild-admin.yaml" \
  --project=mk-ai-project-473000
```

## 권장 방법

**방법 2 (Cloud Build 트리거)를 권장**합니다:
- 인증 설정이 간단함
- GitHub Secrets 설정 불필요
- GCP 네이티브 서비스로 통합 관리 용이
- 기존 Cloud Build 설정 파일 그대로 사용 가능

어떤 방법을 선택하시겠습니까?
