# 로컬 배포 수정 가이드

## 수정된 내용

### 1. Dockerfile.admin, Dockerfile.api 수정
- 존재하지 않는 `templates/` 디렉토리 복사 명령 제거
- 존재하지 않는 `static/` 디렉토리 복사 명령 제거
- Streamlit 앱은 `src/` 디렉토리만 복사

### 2. src/web/app.py 수정
- static과 templates 디렉토리가 없어도 정상 작동하도록 조건부 마운트 추가
- Jinja2Templates를 선택적으로 import

## 로컬 배포 방법

### 방법 1: 현재 실행 중인 서비스 확인 (권장)

현재 로컬에서 Streamlit과 FastAPI가 이미 실행 중입니다.

1. Streamlit 대시보드 확인
   - 브라우저에서 http://localhost:8501 접속
   - 변경사항이 자동으로 반영되는지 확인

2. FastAPI 서비스 확인
   - 터미널에서 실행 중인 uvicorn 프로세스 확인
   - http://localhost:8000/docs 접속하여 API 동작 확인

### 방법 2: 서비스 재시작이 필요한 경우

만약 변경사항이 반영되지 않는다면 다음 명령으로 재시작:

```bash
# 현재 프로세스 중지
pkill -f streamlit
pkill -f uvicorn

# Streamlit 재시작
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate
streamlit run src/web/streamlit_app.py --server.port 8501 --server.headless true > /tmp/streamlit.log 2>&1 &

# FastAPI 재시작
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate
python -m uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload > /tmp/uvicorn.log 2>&1 &
```

### 방법 3: 변경사항 확인

수정된 파일들:
- Dockerfile.admin
- Dockerfile.api
- src/web/app.py

이 파일들이 정상적으로 작동하는지 확인:
```bash
# Python 문법 확인
python -m py_compile src/web/app.py

# Dockerfile 문법 확인 (선택사항)
docker build -f Dockerfile.admin -t test-admin .
```

## 기대 효과

1. Docker 빌드 성공
   - GCP Cloud Build에서 Dockerfile.admin 사용 시 빌드 성공
   - templates 디렉토리 오류 해결

2. 로컬 환경 안정성 향상
   - static/templates 디렉토리 의존성 제거
   - 개발 환경 구축이 더 간편해짐

3. GCP 배포 성공
   - Terraform apply 단계에서 Docker 빌드 성공
   - Cloud Run 서비스 배포 완료 예상

## 다음 단계

1. 로컬에서 앱이 정상 작동하는지 확인
2. 필요시 Terraform apply를 다시 실행하여 GCP 배포
3. Cloud Run 서비스가 정상적으로 배포되는지 확인

