# 로컬 실행 가이드 - 현재 상태

## 서비스 실행 상태

### ✅ 관리자 대시보드 (Streamlit)
- **URL**: http://localhost:8501
- **상태**: 실행 중
- **접속**: 브라우저에서 바로 접속 가능

### 요구사항
모든 필수 패키지가 설치되었습니다:
- ✅ streamlit
- ✅ fastapi
- ✅ google-auth
- ✅ google-auth-oauthlib
- ✅ google-auth-httplib2

## 사용 방법

### 1. 관리자 대시보드 접속

브라우저에서 다음 주소로 접속:
```
http://localhost:8501
```

### 2. GCP 로그인

관리자 대시보드에서:
1. 좌측 사이드바 또는 상단 탭에서 "☁️ GCP 인프라" 선택
2. "gcloud CLI" 선택
3. "🔑 gcloud 로그인" 버튼 클릭
4. 브라우저 팝업에서 인증 완료

### 3. 프로젝트 설정

1. "📋 프로젝트 목록 조회" 버튼 클릭
2. 프로젝트 선택: godwind2015
3. "✅ 프로젝트 설정" 버튼 클릭

### 4. Terraform 배포

"🏗️ 인프라 배포" 섹션으로 이동:

#### Terraform 배포 단계
아래 버튼을 순서대로 클릭:

**1️⃣ Terraform Init**
- 초기화 실행 (1-2분)
- 성공 메시지 확인
- 로그는 Expander에서 확인

**2️⃣ Terraform Plan**
- 배포 계획 생성 (2-5분)
- 생성될 리소스 목록 확인
- 로그 확장하여 전체 내용 확인

**3️⃣ Terraform Apply**
- 실제 인프라 배포 (10-30분)
- 경고: 소요 시간이 길 수 있음
- 성공 시 축하 애니메이션 표시
- 배포 결과 출력값 자동 표시

### 5. 배포 확인

배포 완료 후:
- 배포된 서비스 URL 확인
- 리소스 상태 확인
- 연결 테스트 수행

## 구현된 기능

### 실시간 로깅
- ✅ 각 단계별 로그 실시간 표시
- ✅ 성공/실패 상태 즉시 확인
- ✅ 전체 로그 확인 가능 (Expander)
- ✅ 에러 발생 시 상세 로그

### Terraform 관리
- ✅ 3단계 배포 프로세스
- ✅ 자동화된 배포
- ✅ 배포 결과 자동 추출
- ✅ 리소스 URL 자동 표시

### GCP 연동
- ✅ 인증 통합
- ✅ 프로젝트 관리
- ✅ 리전 설정
- ✅ 서비스 활성화

## 주요 탭 기능

### 📊 대시보드
- 시스템 통계
- 벡터 인덱스 상태
- 최근 처리 로그

### ☁️ GCP 인프라
- GCP 로그인
- 프로젝트 설정
- Terraform 배포
- 리소스 관리

### 📤 벡터임베딩
- XML 파일 업로드
- 배치 처리
- Vertex AI 반영
- 메타데이터 추출

### 🤖 개별기사 해설
- Gemini API 연동
- 3단 논법 해설 생성
- 연관기사 검색
- 타임라인 구성

## 문제 해결

### 대시보드 접속 안됨
```bash
# 포트 확인
lsof -i :8501

# 프로세스 확인
ps aux | grep streamlit
```

### GCP 로그인 오류
```bash
# gcloud CLI 확인
gcloud --version

# 로그인 상태 확인
gcloud auth list

# 로그인
gcloud auth login
```

### Terraform 실행 오류
```bash
# Terraform 확인
cd terraform
terraform version

# 수동 실행 가능
terraform init
terraform plan
terraform apply
```

## 다음 단계

배포 완료 후:
1. XML 파일 업로드
2. 벡터 임베딩 처리
3. 메타데이터 추출
4. Gemini API 해설 생성
5. 연관기사 검색

자세한 내용은 `GCP_DEPLOYMENT_GUIDE.md` 참조
