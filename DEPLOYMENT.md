# Streamlit Community Cloud 배포 설정

## 환경 변수 설정

Streamlit Community Cloud에서 다음 환경 변수들을 설정해야 합니다:

### 필수 환경 변수
```bash
GCP_PROJECT_ID=mk-ai-project-473000
GCP_REGION=asia-northeast3
GEMINI_API_KEY=your_gemini_api_key_here
```

### 선택적 환경 변수
```bash
DB_INSTANCE_NAME=mk-news-db
DB_NAME=mk_news
DB_USER=postgres
DB_PASSWORD=your_password_here
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

## 배포 설정

### Repository 설정
- **Repository**: `YOUR_USERNAME/mk-ai-platform`
- **Branch**: `main`
- **Main file path**: `src/web/streamlit_app.py`

### 고급 설정
- **Python version**: 3.11
- **Dependencies**: `requirements.txt` 자동 감지
- **Streamlit version**: 1.28.1

## 보안 고려사항

1. **API 키 보안**: Gemini API 키는 Streamlit Cloud의 Secrets에서 설정
2. **GCP 인증**: 서비스 계정 키 파일은 환경 변수로 설정
3. **데이터베이스**: Cloud SQL 프록시 사용 권장

## 배포 후 확인사항

1. 앱이 정상적으로 로드되는지 확인
2. GCP 인증 기능 테스트
3. 다크모드 토글 작동 확인
4. 각 탭의 기능 동작 테스트
5. 반응형 디자인 확인

## 문제 해결

### 일반적인 문제
- **모듈 임포트 오류**: `requirements.txt`에 누락된 패키지 추가
- **환경 변수 오류**: Streamlit Cloud의 Secrets 설정 확인
- **GCP 인증 오류**: 서비스 계정 권한 및 키 파일 확인

### 로그 확인
Streamlit Cloud의 로그 탭에서 상세한 오류 메시지 확인 가능
