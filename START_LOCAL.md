# 로컬 배포 및 실행 가이드

## 빠른 시작

### 1단계: 가상 환경 활성화

```bash
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate
```

### 2단계: 패키지 설치 확인

필수 패키지가 설치되어 있는지 확인:
```bash
pip list | grep -E "streamlit|fastapi|uvicorn|requests"
```

필요시 재설치:
```bash
pip install streamlit fastapi uvicorn requests python-dotenv plotly
```

### 3단계: 서비스 실행 (2개 터미널 필요)

#### 터미널 1: 백엔드 API 서버
```bash
uvicorn src.web.app:app --host 0.0.0.0 --port 8000
```

#### 터미널 2: 관리자 대시보드
```bash
streamlit run src/web/streamlit_app.py
```

### 4단계: 브라우저 접속

- 관리자 대시보드: http://localhost:8501
- API 서버: http://localhost:8000

## 관리자 대시보드 사용

### 1. GCP 로그인
1. "☁️ GCP 인프라" 탭 선택
2. "gcloud CLI" 선택
3. "🔑 gcloud 로그인" 버튼 클릭
4. 브라우저에서 인증 완료

### 2. 프로젝트 설정
1. "📋 프로젝트 목록 조회" 클릭
2. 프로젝트 선택
3. "✅ 프로젝트 설정" 클릭

### 3. Terraform 배포
1. "Terraform 배포 단계" 섹션으로 이동
2. 순서대로 클릭:
   - **1️⃣ Init** → 초기화 완료
   - **2️⃣ Plan** → 배포 계획 확인
   - **3️⃣ Apply** → 인프라 배포 (10-30분 소요)
3. 실시간 로그 확인
4. 배포 완료 후 결과 확인

## 문제 해결

### 포트 충돌
```bash
# 8501 포트 사용 중인 프로세스 확인
lsof -i :8501

# 프로세스 종료
kill -9 [PID]
```

### 패키지 설치 오류
```bash
# 가상 환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install streamlit fastapi uvicorn requests python-dotenv plotly
```

### Streamlit 실행 오류
```bash
# 로그 확인
streamlit run src/web/streamlit_app.py --logger.level=debug
```

## 다음 단계

배포 완료 후:
1. XML 파일 업로드
2. 벡터 임베딩 처리
3. 메타데이터 추출
4. Gemini API로 해설 생성

자세한 내용은 `GCP_DEPLOYMENT_GUIDE.md` 참조
