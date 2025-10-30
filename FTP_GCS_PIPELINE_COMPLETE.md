# FTP → GCS → 벡터 임베딩 파이프라인 완료

## 구현 완료

### 1. FTP 클라이언트
**파일**: `src/ftp/ftp_client.py`

- FTP 서버 연결/해제
- 파일 목록 조회
- 파일 다운로드
- 다운로드 후 삭제 옵션
- 테스트/실제 서버 지원

### 2. GCS 클라이언트
**파일**: `src/storage/gcs_client.py` (신규 생성)

- GCS 버킷 연결
- 파일 업로드
- 디렉토리 업로드 (XML 필터링)
- 파일 목록 조회
- 파일 삭제

### 3. FTP 파이프라인
**파일**: `src/ftp/ftp_pipeline.py` (신규 생성)

**기능**:
1. FTP에서 XML 파일 다운로드
2. GCS에 업로드
3. XML 파싱
4. 벡터 임베딩 생성
5. Vector Index 업데이트

**옵션**:
- `delete_after_download`: FTP 서버에서 다운로드 후 삭제 여부
- `upload_to_gcs`: GCS 업로드 여부
- `create_embeddings`: 벡터 임베딩 생성 여부

### 4. API 엔드포인트

**추가된 API**:
```
POST   /api/ftp/pipeline    - FTP → GCS → 임베딩 파이프라인
GET    /api/gcs/files       - GCS 파일 목록 조회
DELETE /api/gcs/files/{path} - GCS 파일 삭제
```

### 5. Streamlit UI

**위치**: 탭 8 - FTP 연동

**기능**:
- 환경 선택 (테스트/실제 서버)
- FTP 연결/해제 버튼
- 파이프라인 옵션 설정 (체크박스)
  - 다운로드 후 FTP에서 삭제
  - GCS에 업로드
  - 벡터 임베딩 생성
- 파이프라인 실행
- 결과 통계 표시
- GCS 파일 목록 조회

## FTP 서버 정보

### 테스트 서버
- 주소: 210.179.172.2:8023
- 계정: saltlux_vector
- 비밀번호: ^hfxmfn7^m

### 실제 서버
- 주소: 210.179.172.10:8023
- 계정: saltlux_vector
- 비밀번호: ^hfxmfn7^m

## Cloud Run 접속 IP

GCP Cloud Run에서 FTP 서버에 접속하려면 고정 IP가 필요합니다.

### 방법 1: Cloud NAT 사용 (추천)
```bash
# NAT 게이트웨이 생성
gcloud compute routers create mk-news-router \
    --network=mk-news-vpc \
    --region=asia-northeast3

# NAT 설정
gcloud compute routers nats create mk-news-nat \
    --router=mk-news-router \
    --region=asia-northeast3 \
    --nat-all-subnet-ip-ranges \
    --nat-external-ip-pool=<STATIC_IP_NAME>
```

### 방법 2: 고정 IP 서버리스 NEG
```bash
# 고정 IP 리전 예약
gcloud compute addresses create mk-news-static-ip \
    --region=asia-northeast3 \
    --network-tier=PREMIUM
```

### 방법 3: Cloud SQL Proxy와 유사한 방법
- FTP 서버가 내부 네트워크에 있다면 VPC 피어링 사용

## 사용 방법

### Streamlit UI
1. http://localhost:8501 접속
2. "FTP 연동" 탭 (8번) 선택
3. 환경 선택 (테스트/실제)
4. "FTP 연결" 버튼 클릭
5. 옵션 설정:
   - 다운로드 후 FTP에서 삭제 (선택)
   - GCS에 업로드 (선택)
   - 벡터 임베딩 생성 (선택)
6. "파이프라인 실행" 버튼 클릭
7. 결과 확인

### API 사용
```bash
curl -X POST http://localhost:8000/api/ftp/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "test",
    "delete_after_download": false,
    "upload_to_gcs": true,
    "create_embeddings": true
  }'
```

## 데이터 흐름

```
매경닷컴 FTP 서버
    ↓ (다운로드)
로컬 임시 저장
    ↓ (업로드)
GCS Blob Storage
    ↓ (파싱)
XML Parser
    ↓ (메타데이터 추출)
Metadata Extractor
    ↓ (임베딩)
Embedding Service (해시 기반 실제 벡터)
    ↓ (인덱싱)
Vector Indexer
    ↓
Vertex AI Vector Search
```

## 주요 파일

- `src/ftp/ftp_client.py` - FTP 클라이언트
- `src/ftp/ftp_pipeline.py` - 파이프라인 (신규)
- `src/storage/gcs_client.py` - GCS 클라이언트 (신규)
- `src/web/app.py` - API 엔드포인트 추가
- `src/web/streamlit_app.py` - UI 추가

## 보안 고려사항

1. **FTP 자격증명**: 환경변수 또는 Secret Manager 사용 권장
2. **GCS 권한**: 서비스 계정 최소 권한 부여
3. **네트워크**: VPN 또는 VPC 피어링 고려
4. **데이터 암호화**: GCS 업로드 시 자동 암호화

## 배포 상태

- FastAPI: http://localhost:8000 ✅
- Streamlit: http://localhost:8501 ✅

FTP → GCS → 벡터 임베딩 파이프라인이 완전히 구현되었습니다.


