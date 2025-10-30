# GitHub + Cloud Build CI/CD 설정 가이드

## 상황 설명
Cloud Source Repositories는 2024년 6월 17일부터 신규 고객에게 제공되지 않으므로, GitHub를 사용하여 CI/CD를 설정합니다.

## 설정 단계

### 1단계: GitHub 저장소 생성 (수동)

1. GitHub (https://github.com) 접속 및 로그인
2. 우측 상단 "+" 버튼 > "New repository" 클릭
3. 저장소 정보 입력:
   - Repository name: `mk-news-platform`
   - Description: "매일경제 신문기사 벡터임베딩 플랫폼"
   - Public 또는 Private 선택
   - **"Add a README file" 체크하지 않기** (이미 로컬에 코드가 있으므로)
   - "Create repository" 클릭

### 2단계: 로컬 Git과 GitHub 연결

GitHub 저장소 생성 후, 저장소 URL을 복사한 다음 아래 명령어를 실행하세요:

```bash
# 저장소 URL 예시: https://github.com/YOUR_USERNAME/mk-news-platform.git
# YOUR_USERNAME을 실제 GitHub 사용자명으로 변경하세요

cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"

# GitHub 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/mk-news-platform.git

# 코드 푸시
git push -u origin main
```

### 3단계: GitHub OIDC 인증 설정 (보안 강화)

GitHub Actions에서 GCP에 인증하기 위한 OIDC 설정:

```bash
# 워크로드 ID 풀 생성
gcloud iam workload-identity-pools create github-pool \
  --project="mk-ai-project-473000" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# 워크로드 ID 공급자 생성 (YOUR_USERNAME을 실제 사용자명으로 변경)
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project="mk-ai-project-473000" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 워크로드 ID 풀 이름 가져오기
gcloud iam workload-identity-pools providers describe github-provider \
  --project="mk-ai-project-473000" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"

# 서비스 계정 권한 부여 (YOUR_USERNAME을 실제 사용자명으로 변경)
gcloud iam service-accounts add-iam-policy-binding \
  mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com \
  --project="mk-ai-project-473000" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/mk-ai-project-473000/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_USERNAME/mk-news-platform"
```

### 4단계: GitHub Secrets 설정

1. GitHub 저장소 페이지로 이동
2. "Settings" > "Secrets and variables" > "Actions" 클릭
3. "New repository secret" 클릭하여 다음 두 개의 Secret 추가:

**Secret 1:**
- Name: `WIF_PROVIDER`
- Value: 워크로드 ID 풀 공급자 전체 경로 (3단계에서 출력된 값)
  예시: `projects/mk-ai-project-473000/locations/global/workloadIdentityPools/github-pool/providers/github-provider`

**Secret 2:**
- Name: `GCP_SERVICE_ACCOUNT`
- Value: `mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com`

### 5단계: Cloud Build 트리거 설정 (선택사항)

GitHub Actions 대신 Cloud Build 트리거를 사용하려면:

```bash
# GitHub 연결 (처음만, 브라우저에서 인증 필요)
gcloud builds triggers create github \
  --name="github-auto-deploy-admin" \
  --repo-name="mk-news-platform" \
  --repo-owner="YOUR_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild-admin.yaml" \
  --project=mk-ai-project-473000
```

## 작업 흐름

### CI/CD 적용 후
1. **Cursor에서 코드 수정**
2. **Git 커밋 및 푸시**:
   ```bash
   git add .
   git commit -m "변경사항 설명"
   git push origin main
   ```
3. **자동 배포**: GitHub Actions 또는 Cloud Build가 자동으로 감지하여 빌드 및 배포 수행

## 장점

- ✅ GitHub UI로 코드 관리
- ✅ GitHub Actions로 자동 배포
- ✅ OIDC 인증으로 보안 강화
- ✅ Pull Request 리뷰 가능
- ✅ 이슈 및 프로젝트 관리 가능

## 문제 해결

### Git 인증 오류
```bash
# GitHub Personal Access Token 사용
git config credential.helper store
# 또는 SSH 키 사용
git remote set-url origin git@github.com:YOUR_USERNAME/mk-news-platform.git
```

### Cloud Build 권한 오류
```bash
gcloud projects add-iam-policy-binding mk-ai-project-473000 \
  --member="serviceAccount:mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"
```