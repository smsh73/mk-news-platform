# CI/CD 동작 확인 가이드

## 테스트 커밋 완료

코드가 푸시되었습니다. 이제 GitHub Actions가 자동으로 트리거되어야 합니다.

## 확인 방법

### 1. GitHub Actions 페이지에서 확인

다음 링크로 이동하여 워크플로 실행 상태를 확인하세요:
**https://github.com/smsh73/mk-news-platform/actions**

### 2. 예상되는 동작

1. **워크플로 트리거**: `main` 브랜치에 푸시되면 자동으로 시작
2. **빌드 단계**:
   - Checkout code
   - Authenticate to Google Cloud
   - Set up Cloud SDK
   - Deploy to Cloud Run (Admin)

### 3. 상태 확인

- **노란색 동그라미 (진행 중)**: 워크플로가 현재 실행 중
- **초록색 체크 (성공)**: 배포 성공
- **빨간색 X (실패)**: 오류 발생 - 로그 확인 필요

### 4. 로그 확인

워크플로 실행 항목을 클릭하여 각 단계의 상세 로그를 확인할 수 있습니다.

## 예상 소요 시간

- GitHub Actions 실행: 5-10분
- Cloud Build 빌드: 10-15분
- Cloud Run 배포: 5-10분
- **총 소요 시간: 약 20-35분**

## 문제 해결

### 워크플로가 보이지 않는 경우
- Secrets 설정이 완료되었는지 확인
- `.github/workflows/deploy-admin.yml` 파일이 존재하는지 확인

### 인증 오류가 발생하는 경우
- `GCP_SERVICE_ACCOUNT_KEY` Secret이 올바르게 설정되었는지 확인
- Base64 인코딩이 올바른지 확인

### 배포 오류가 발생하는 경우
- Cloud Build 로그 확인:
  ```bash
  gcloud builds list --limit=5 --project=mk-ai-project-473000
  ```

## 다음 단계

워크플로가 성공적으로 완료되면:
1. Cloud Run 서비스 확인
2. 애플리케이션 접속 테스트
3. 추가 변경사항 푸시하여 자동 배포 확인

