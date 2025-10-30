# GCP CLI 브라우저 로그인 가이드

## 방법 1: 기본 브라우저 로그인 (권장)

터미널에서 다음 명령어를 실행하세요:

```bash
gcloud auth login
```

**실행 결과:**
1. 브라우저가 자동으로 열리거나, 터미널에 URL이 표시됩니다
2. 브라우저에서 GCP 계정으로 로그인
3. 권한 승인
4. 로그인 완료 후 터미널로 돌아옵니다

## 방법 2: 브라우저 수동 실행

브라우저가 자동으로 열리지 않는 경우:

```bash
gcloud auth login --no-launch-browser
```

**실행 결과:**
1. 터미널에 URL과 인증 코드가 표시됩니다
2. 브라우저를 직접 열고 제공된 URL로 이동
3. 인증 코드를 복사하여 입력
4. 로그인 완료

## 방법 3: Application Default Credentials 설정

애플리케이션에서 사용할 인증 정보 설정:

```bash
gcloud auth application-default login
```

이 방법은 애플리케이션 코드에서 사용하는 인증 정보를 설정합니다.

## 현재 인증 상태 확인

```bash
gcloud auth list
```

현재 활성화된 계정 목록을 확인할 수 있습니다.

## 특정 계정 선택

여러 계정이 있는 경우:

```bash
gcloud config set account YOUR_EMAIL@gmail.com
```

## 프로젝트 설정 확인

```bash
gcloud config list
```

현재 프로젝트 및 계정 설정을 확인할 수 있습니다.

## 문제 해결

### 인증 코드를 복사할 수 없는 경우
- 터미널에서 직접 복사하거나
- Service Account Key 파일 사용 (이미 설정됨: `~/mk-news-key.json`)

### Service Account 사용
이미 생성된 Service Account 키를 사용하려면:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/mk-news-key.json
gcloud auth activate-service-account mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com --key-file=~/mk-news-key.json
```

## 브라우저 접근 시

브라우저에서 Cloud Run 서비스에 접근할 때:
- GCP 콘솔을 통해 접근하면 자동으로 인증됩니다
- 직접 URL 접근 시: GCP 계정으로 로그인하라는 메시지가 표시됩니다
- 로그인하면 해당 계정의 권한에 따라 접근 가능합니다

