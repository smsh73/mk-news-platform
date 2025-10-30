# GitHub Secrets 설정 안내

## 현재 상태
✅ GitHub 저장소에 코드 푸시 완료
✅ GitHub Actions 워크플로 파일 업로드 완료
oin GitHub Secrets 설정 필요

## GitHub Secrets 설정 방법

### 1단계: GitHub 저장소 Settings로 이동

다음 링크로 이동하세요:
**https://github.com/smsh73/mk-news-platform/settings/secrets/actions**

### 2단계: Secret 추가

"New repository secret" 버튼을 클릭하여 다음 두 개의 Secret을 추가하세요:

#### Secret 1: GCP_SERVICE_ACCOUNT_KEY

- **Name**: `GCP_SERVICE_ACCOUNT_KEY`
- **Value**: 아래 명령어로 생성된 Base64 인코딩된 키 (전체 내용을 한 줄로 복사)
  ```bash
  base64 -i ~/mk-news-key.json
  ```
  또는 터미널에서:
  ```bash
  cat ~/mk-news-key.json | base64 | tr -d '\n'
  ```
  전체 출력을 복사하여 Value에 붙여넣으세요.

#### Secret 2: GCP_PROJECT_ID

- **Name**: `GCP_PROJECT_ID`
- **Value**: `mk-ai-project-473000`

## 확인

설정 완료 후:
1. GitHub 저장소의 Secrets 페이지에서 두 Secret이 표시되는지 확인
2. "Actions" 탭에서 워크플로가 보이는지 확인

## 테스트

Secrets 설정 후, 코드에 작은 변경사항을 추가하여 CI/CD가 작동하는지 테스트:

```bash
echo "# CI/CD Test - $(date)" >> README.md
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main
```

그 다음 GitHub Actions 페이지에서 배포 진행 상황을 확인하세요:
**https://github.com/smsh73/mk-news-platform/actions**

## 서비스 계정 키 Base64 인코딩

터미널에서 다음 명령어 실행:

```bash
base64 -i ~/mk-news-key.json | tr -d '\n'
```

출력된 전체 텍스트를 복사하여 `GCP_SERVICE_ACCOUNT_KEY` Secret의 Value로 사용하세요.

