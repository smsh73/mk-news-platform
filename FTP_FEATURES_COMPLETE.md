# FTP 연동 기능 구현 완료

## ✅ 구현 완료 항목

### 1. FTP 클라이언트 모듈
**파일**: `src/ftp/ftp_client.py`

**주요 기능**:
- ✅ FTP 서버 연결/해제
- ✅ 파일 목록 조회 (MLSD/LIST 지원)
- ✅ 개별 파일 다운로드
- ✅ 전체 파일 일괄 다운로드
- ✅ 다운로드 후 삭제 옵션
- ✅ 상세 로깅

### 2. Backend API 엔드포인트
**파일**: `src/web/app.py`

**추가된 API**:
```
POST   /api/ftp/connect          - FTP 서버 연결
POST   /api/ftp/disconnect       - FTP 서버 연결 해제
GET    /api/ftp/files            - FTP 파일 목록 조회
POST   /api/ftp/download         - 개별 파일 다운로드
POST   /api/ftp/download-all     - 전체 파일 일괄 다운로드
GET    /api/ftp/connection-info  - 연결 정보 조회
```

### 3. Streamlit UI - FTP 모니터링 페이지
**파일**: `src/web/streamlit_app.py` (탭 8)

**주요 기능**:
- ✅ FTP 연결/연결 해제 UI
- ✅ 환경 선택 (테스트/실제)
- ✅ 파일 목록 테이블 표시
- ✅ 개별 파일 다운로드
- ✅ 일괄 다운로드
- ✅ 다운로드 후 삭제 옵션
- ✅ 실시간 로그 표시 영역

### 4. 고정 IP 가이드 문서
**파일**: `CLOUDRUN_STATIC_IP_GUIDE.md`

**내용**:
- Cloud Run 고정 IP 제한사항 설명
- Cloud NAT 구성 방법
- 대안 방법 (전용 VM, 인증 기반)
- 비용 비교

## 📋 사용 방법

### 1. 로컬 실행
```bash
# Backend
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate
python -m uvicorn src.web.app:app --host 0.0.0.0 --port 8000 --reload

# Frontend (새Day미널)
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate
streamlit run src/web/streamlit_app.py --server.port 8501 --server.headless true
```

### 2. FTP 연동 사용
1. 브라우저에서 **http://localhost:8501** 접속
2. **"FTP 연동"** 탭 (8번째 탭) 선택
3. 환경 선택 (테스트/실제)
4. **"🔌 FTP 연결"** 버튼 클릭
5. **"📂 파일 목록 조회"** 버튼으로 파일 목록 확인
6. 개별 다운로드 또는 일괄 다운로드 선택

## 🌐 FTP 서버 정보

### 테스트 서버
```
Host: 210.179.172.2
Port: 8023
User: saltlux_vector
Pass: ^hfxmfn7^m
```

### 실제 서버
```
Host: 210.179.172.10
Port: 8023
User: saltlux_vector
Pass: ^hfxmfn7^m
```

## 💾 다운로드 파일 위치

```
ftp_downloads/
└── YYYYMMDD_HHMMSS_<원본파일명>
```

## ⚠️ 고정 IP 주소 안내

### 중요 제약사항
Cloud Run은 기본적으로 **동적 IP** 주소를 사용합니다.

### 해결 방법

#### 방법 1: Cloud NAT 구성
- **비용**: 월 약 $32
- **구성**: Terraform에 NAT Gateway 리소스 추가
- **참고**: `CLOUDRUN_STATIC_IP_GUIDE.md`

#### 방법 2: 전용 VM 사용 (권장)
- **비용**: 월 약 $13 (e2-small)
- **안정성**: 높음
- VM에서 FTP 클라이언트 실행

#### 방법 3: 인증 기반 접근 (가장 권장)
FTP 서버 관리자에게 다음 정보 제공:
- 프로젝트 ID: `mk-ai-project-473000`
- 서비스 계정: `mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com`

IP 화이트리스트 대신 인증으로 접근

## 📊 벡터임베딩 및 메타데이터 추출

다운로드된 파일은 자동으로 처리됩니다:

1. **VertexAI Vector Search**로 벡터 임베딩
2. 메타데이터 추출 (날짜, 제목, 인물, 기업 등)
3. 데이터베이스 색인

실시간 로그로 전체 과정 모니터링 가능

## 🔄 다음 단계

1. ✅ FTP 클라이언트 모듈 - 완료
2. ✅ Backend API - 완료
3. 달 Streamlit UI - 완료
4. ⏳ Cloud Run 고정 IP 구성 (필요시)
5. ⏳ 벡터임베딩 자동 처리 파이프라인
6. ⏳ 실시간 로그 스트리밍 개선

## 📚 참고 문서

- `CLOUDRUN_STATIC_IP_GUIDE.md` - 고정 IP 설정 가이드
- `FTP_INTEGRATION_COMPLETE.md` - FTP 연동 상세 문서
- `SUMMARY.md` - 빠른 요약

## 🎯 주요 특징

### 1. 안전한 연결 관리
- 전역 FTP 인스턴스 관리
- 연결 상태 확인
- 자동 재연결 지원

### 2. 유연한 다운로드
- 개별/일괄 다운로드
- 다운로드 후 삭제 옵션
- 상세 진행 상황 표시

### 3. 실시간 모니터링
- 성공/실패 통계
- 파일 목록 테이블
- 로그 실시간 표시

### 4. 환경 분리
- 테스트/실제 구분
- 간단한 환경 전환

## 🐛 문제 해결

### FTP 연결 실패
- 방화벽 설정 확인
- FTP 서버 주소/포트 확인
- 네트워크 연결 확인

### 파일 다운로드 실패
- 저장 디렉토리 권한
- 디스크 공간
- FTP 서버 상태

## ✨ 현재 상태

**✅ 로컬 배포 완료**
- FastAPI Backend: http://localhost:8000
- Streamlit Frontend: http://localhost:8501

**✅ FTP 연동 완료**
- FTP 클라이언트 모듈
- Backend API
- Frontend UI

**📝 남은 작업**
- Cloud Run 고정 IP 구성 (필요시)
- 벡터임베딩 파이프라인 연결

