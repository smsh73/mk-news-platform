# 브라우저에서 Cloud Run 서비스 접근 방법

## ✅ 권한 설정 완료

다음 계정에 접근 권한이 부여되었습니다:
- **계정**: godwind2015@gmail.com
- **API 서비스**: 접근 가능
- **Admin 서비스**: 접근 가능

## 🌐 브라우저 접근 방법

### 방법 1: GCP 콘솔을 통한 접근 (가장 쉬움)

1. GCP 콘솔 접속: https://console.cloud.google.com
2. 로그인: godwind2015@gmail.com 계정으로 로그인
3. Cloud Run 서비스 페이지로 이동
4. 서비스 선택:
   - **mk-news-admin**: 관리자 대시보드
   - **mk-news-api**: API 서비스

### 방법 2: 직접 URL 접근

브라우저에서 다음 URL로 접근:

**Admin 대시보드:**
```
https://mk-news-admin-268150188947.asia-northeast3.run.app
```

**API 서비스:**
```
https://mk-news-api-268150188947.asia-northeast3.run.app
```

**접근 시:**
1. 브라우저에서 GCP 로그인 화면이 나타납니다
2. **godwind2015@gmail.com** 계정으로 로그인
3. 권한 승인 클릭
4. 서비스에 접근할 수 있습니다

## 🔑 로그인이 안 되는 경우

### 다음 명령어로 토큰 새로고침:
```bash
gcloud auth application-default login
```

### 또는 다시 로그인:
```bash
gcloud auth login
```

## 📝 참고사항

- 이미 계정에 접근 권한이 부여되어 있으므로, GCP 계정으로 로그인하면 바로 접근 가능합니다
- 브라우저에서 "Error: Forbidden"이 나타나면, GCP 계정으로 로그인하세요
- 첫 접근 시 권한 승인을 요청할 수 있습니다

