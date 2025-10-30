# FTP 연동 배포 상태 확인

## ✅ 현재 배포 상태

### 1. 로컬 서비스 실행 중

#### FastAPI Backend
- **URL**: http://localhost:8000
- **상태**: ✅ 정상 실행 중
- **Health Check**: ✅ 통과
- **모듈 로드**: ✅ FTP 모듈 정상 import

#### Streamlit Frontend
- **URL**: http://localhost:8501
- **상태**: ✅ 정상 실행 중
- **FTP 탭**: ✅ 탭 8번 위치

### 2. FTP 기능 구현 완료

#### FTP 클라이언트 모듈
**파일**: `src/ftp/ftp_client.py`
- ✅ FTP 서버 연결/해제
- ✅ 파일 목록 조회 (MLSD/LIST 지원)
- ✅ 개별 파일 다운로드
- ✅ 전체 파일 일괄 다운로드
- ✅ 다운로드 후 삭제 옵션
- ✅ 상세 로깅

#### Backend API
**파일**: `src/web/app.py`
- ✅ `POST /api/ftp/connect` - FTP 서버 연결
- ✅ `POST /api/ftp/disconnect` - FTP 서버 연결 해제
- ✅ `GET /api/ftp/files` - FTP 파일 목록 조회
- ✅ `POST /api/ftp/download` - 개별 파일 다운로드
- ✅ `POST /api/ftp/download-all` - 전체 파일 일괄 다운로드
- ✅ `GET /api/ftp/connection-info` - 연결 정보 조회

#### Streamlit UI
**파일**: `src/web/streamlit_app.py` (탭 8)
- ✅ FTP 연결/연결 해제 UI
- ✅ 환경 선택 (테스트/실제)
- ✅ 파일 목록 테이블 표시
- ✅ 개별 파일 다운로드
- ✅ 일괄 다운로드
- ✅ 다운로드 후 삭제 옵션
- ✅ 실시간 로그 표시 영역

### 3. 고정 IP 가이드 문서
**파일**: `CLOUDRUN_STATIC_IP_GUIDE.md`
- ✅ Cloud Run 고정 IP 제한사항 설명
- ✅ Cloud NAT 구성 방법
- ✅ 대안 방법 (전용 VM, 인증 기반)
- ✅ 비용 비교

## 🎯 사용 방법

### 1. FTP 연동 사용하기

#### 단계 1: 브라우저 접속
```
http://localhost:8501
```

#### 단계 2: FTP 탭 선택
- 왼쪽 메뉴에서 **"FTP 연동"** 탭 (8번째) 클릭

#### 단계 3: FTP 서버 연결
1. **환경 선택**: 테스트 또는 실제
   - 테스트: `210.179.172.2:8023`
   - 실제: `210.179.172.10:8023`

2. **🔌 FTP 연결** 버튼 클릭

#### 단계 4: 파일 목록 조회
1. **📂 파일 목록 조회** 버튼 클릭
2. 파일 목록이 테이블로 표시됨

#### 단계 5: 파일 다운로드
**개별 다운로드**:
1. 파일 선택 드롭다운에서 파일 선택
2. "다운로드 후 FTP에서 삭제" 체크박스 선택 (선택사항)
3. **⬇️ 선택 파일 다운로드** 버튼 클릭

**일괄 다운로드**:
1. "다운로드 후 FTP에서 삭제" 체크박스 선택 (선택사항)
2. **⬇️ 전체 파일 일괄 다운로드** 버튼 클릭

#### 단계 6: 다운로드 로그 확인
- 화면 하단의 **"📋 다운로드 및 처리 로그"** 영역에서 실시간 로그 확인

### 2. 다운로드 파일 위치

```
ftp_downloads/
└── YYYYMMDD_HHMMSS_<원본파일명>
```

**예시**:
```
ftp_downloads/
├── 20250227_143022_news001.xml
├── 20250227_143045_news002.xml
└── 20250227_143102_news003.xml
```

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

## ⚠️ 중요한 제약사항

### 1. Cloud Run 고정 IP
**현재 상태**: ❌ 고정 IP 없음

Cloud Run은 기본적으로 **동적 IP** 주소를 사용합니다.
FTP 서버에 IP 화이트리스트를 등록하려면 고정 IP가 필요합니다.

#### 해결 방법

**방법 1: Cloud NAT 구성** (권장하지 않음)
- **비용**: 월 약 $32
- Terraform에 NAT Gateway 리소스 추가
- 참고: `CLOUDRUN_STATIC_IP_GUIDE.md`

**방법 2: 전용 VM 사용** (더 좋은 대안)
- **비용**: 월 약 $13 (e2-small)
- **안정성**: 높음
- VM에서 FTP 클라이언트 실행

**방법 3: 인증 기반 접근** (가장 권장)
FTP 서버 관리자에게 다음 정보 제공:
```
프로젝트 ID: mk-ai-project-473000
서비스 계정: mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com
```
IP 화이트리스트 대신 인증으로 접근

### 2. 로컬 테스트
로컬에서 FTP 연동 기능을 **테스트할 수 있습니다**.
FTP 서버에서 로컬 IP 주소를 허용하는 경우:
1. 로컬에서 Streamlit 접속
2. FTP 탭에서 연결
3. 파일 다운로드 테스트

## 🔄 다음 단계

### 즉시 가능한 작업
1. ✅ FTP 파일 다운로드 - **완료**
2. ⏳ 다운로드된 파일 자동 처리 - **대기**
3. ⏳ 벡터임베딩 자동 실행 - **대기**
4. ⏳ 메타데이터 추출 및 색인 - **대기**
5. ⏳ 실시간 로그 스트리밍 - **대기**

### 벡터임베딩 파이프라인 연결
다운로드된 XML 파일을 자동으로:
1. VertexAI Vector Search로 벡터 임베딩
2. 메타데이터 추출 (날짜, 제목, 인물, 기업 등)
3. 데이터베이스 색인

### Cloud Run 고정 IP 구성 (필요시)
1. FTP 서버 관리자와 협의
2. 인증 기반 접근 또는 IP 화이트리스트 확인
3. 필요시 Cloud NAT 또는 VM 구성

## 🐛 문제 해결

### FTP 연결 실패
- **원인**: 방화벽 차단, 네트워크 문제
- **해결**: 네트워크 설정 확인, FTP 서버 상태 확인

### 파일 다운로드 실패
- **원인**: 저장 디렉토리 권한, 디스크 공간 부족
- **해결**: 디렉토리 권한 확인, 디스크 공간 확인

### 모듈 import 오류
- **원인**: 의존성 누락
- **해결**: `pip install ftputil` (참고: 이미 `requirements.txt`에 추가됨)

## 📊 현재 상태 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| 로컬 Backend | ✅ 실행 중 | http://localhost:8000 |
| 로컬 Frontend | ✅ 실행 중 | http://localhost:8501 |
| FTP 클라이언트 | ✅ 구현 완료 | 다운로드, 삭제 옵션, 로깅 |
| Backend API | ✅ 구현 완료 | 6개 엔드포인트 |
| Streamlit UI | ✅ 구현 완료 | 탭 8번 위치 |
| 고정 IP 문서 | ✅ 작성 완료 | Cloud NAT 가이드 |
| 벡터임베딩 연결 | ⏳ 대기 | 다음 단계 |
| Cloud Run 배포 | ⏳ 대기 | 고정 IP 구성 후 |

## 🎉 완료된 작업

1. ✅ FTP 클라이언트 모듈 구현
2. ✅ Backend API 엔드포인트 추가
3. ✅ Streamlit UI에 FTP 모니터링 페이지 추가
4. ✅ 고정 IP 가이드 문서 작성
5. ✅ 로컬 배포 확인
6. ✅ Health Check 통과

## 📝 사용 예시

```bash
# 로컬 배포 상태 확인
curl http://localhost:8000/health

# FTP 연결 상태 확인
curl http://localhost:8000/api/ftp/connection-info

# 브라우저에서 접속
open http://localhost:8501
```

## 🔗 관련 문서

- `FTP_INTEGRATION_COMPLETE.md` - FTP 연동 상세 문서
- `FTP_FEATURES_COMPLETE.md` - FTP 기능 완료 문서
- `CLOUDRUN_STATIC_IP_GUIDE.md` - Cloud Run 고정 IP 가이드
- `SUMMARY.md` - 빠른 요약

---

**마지막 업데이트**: 2025-01-27
**현재 상태**: 로컬 배포 완료, FTP 연동 기능 준비 완료
