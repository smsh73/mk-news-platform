# GitHub Actions 인증 오류 해결

## 문제
`google-github-actions/auth`에서 `workload_identity_provider`와 `credentials_json` 중 정확히 하나만 지정해야 한다는 오류가 발생했습니다.

## 해결 완료
✅ `deploy-api.yml` 파일을 `credentials_json` 방식으로 수정 완료

## 추가 확인 사항

### 1. GitHub Secrets 확인

GitHub 저장소의 Secrets 설정을 확인하세요:
**https://github.com/smsh73/mk-news-platform/settings/secrets/actions**

다음 Secret이 설정되어 있어야 합니다:
- ✅ `GCP_SERVICE_ACCOUNT_KEY` - 서비스 계정 키 (JSON 파일 내용)
- ✅ `GCP_PROJECT_ID` - 프로젝트 ID: `mk-ai-project-473000`

### 2. GCP_SERVICE_ACCOUNT_KEY 형식

`GCP_SERVICE_ACCOUNT_KEY` Secret은 다음 중 하나의 형식이어야 합니다:

**방법 1: JSON 파일 내용 그대로 (권장)**
```json
{
  "type": "service_account",
  "project_id": "mk-ai-project-473000",
  ...
}
```
- `~/mk-news-key.json` 파일의 내용을 그대로 복사하여 Secret에 붙여넣기

**방법 2: Base64 인코딩**
- Base64로 인코딩된 경우, 워크플로에서 디코딩 필요 (현재는 방법 1 권장)

### 3. Secret 설정 확인 명령어

터미널에서 다음 명령어로 키 파일 내용 확인:
```bash
cat ~/mk-news-key.json
```

이 내용 전체를 복사하여 `GCP_SERVICE_ACCOUNT_KEY` Secret에 붙여넣으세요.

## 수정된 워크플로 파일

두 워크플로 파일 모두 `credentials_json` 방식으로 통일되었습니다:
- ✅ `.github/workflows/deploy-admin.yml`
- ✅ `.github/workflows/deploy-api.yml`

## 다음 단계

1. Secret이 올바르게 설정되었는지 확인
2. 수정된 워크플로 파일을 커밋하고 푸시
3. 다시 테스트

키 파일 내용을 확인하여 Secret에 올바르게 설정되었는지 확인해주세요.

