# FTP → GCS → 벡터 임베딩 파이프라인 최종 완료

## 구현 완료

### 1. 파일 구조

```
src/
├── ftp/
│   ├── __init__.py           # FTP 모듈 (업데이트)
│   ├── ftp_client.py         # FTP 클라이언트 (기존)
│   └── ftp_pipeline.py       # FTP 파이프라인 (신규)
├── storage/
│   ├── __init__.py           # Storage 모듈 (신규)
│   └── gcs_client.py         # GCS 클라이언트 (신규)
└── web/
    ├── app.py                # FastAPI (업데이트)
    └── streamlit_app.py      # Streamlit UI (업데이트)
```

### 2. 핵심 기능

#### FTP 파이프라인 (`ftp_pipeline.py`)
- FTP 서버에서 XML 파일 다운로드
- GCS에 자동 업로드
- XML 파싱 및 벡터 임베딩 생성
- 임시 파일 자동 정리

#### GCS 클라이언트 (`gcs_client.py`)
- Google Cloud Storage 파일 업로드
- 파일 목록 조회
- 파일 삭제

#### Streamlit UI (탭 8)
- 환경 선택 (테스트/실제)
- FTP 연결/해제
- 파이프라인 옵션 설정
- 결과 통계 표시

## 사용 방법

### 1. Streamlit UI 접속
```
http://localhost:8501
```

### 2. FTP 연동 탭 (8번) 선택

### 3. 환경 선택
- 테스트 서버: 210.179.172.2:8023
- 실제 서버: 210.179.172.10:8023

### 4. FTP 연결
"FTP 연결" 버튼 클릭

### 5. 파이프라인 옵션 설정
- ✅ 다운로드 후 FTP에서 삭제 (선택)
- ✅ GCS에 업로드 (기본: 선택)
- ✅ 벡터 임베딩 생성 (기본: 선택)

### 6. 파이프라인 실행
"파이프라인 실행" 버튼 클릭

### 7. 결과 확인
- 다운로드 파일 수
- GCS 업로드 파일 수
- 임베딩 생성 기사 수

## API 엔드포인트

### FTP 파이프라인 실행
```bash
POST /api/ftp/pipeline
Content-Type: application/json

{
  "environment": "test",
  "delete_after_download": false,
  "upload_to_gcs": true,
  "create_embeddings": true
}
```

### GCS 파일 목록 조회
```bash
GET /api/gcs/files
```

## 데이터 흐름

```
1. FTP 서버 (매경닷컴)
   ↓
2. 다운로드 (로컬 임시 저장)
   ↓
3. GCS 업로드 (gs://mk-ai-project-473000-mk-news-data/)
   ↓
4. XML 파싱
   ↓
5. 메타데이터 추출
   ↓
6. 벡터 임베딩 생성 (해시 기반 실제 벡터)
   ↓
7. Vector Index 업데이트
```

## FTP 서버 정보

### 계정
- ID: saltlux_vector
- PW: ^hfxmfn7^m

### 테스트 서버
- IP: 210.179.172.2
- Port: 8023

### 실제 서버
- IP: 210.179.172.10
- Port: 8023

## GCS 버킷

### 이름
`mk-ai-project-473000-mk-news-data`

### 저장 구조
```
gs://mk-ai-project-473000-mk-news-data/
└── ftp_downloads/
    ├── test/
    │   └── 20251028_140000_article.xml
    └── production/
        └── 20251028_140000_article.xml
```

## Cloud Run 접속 IP 설정

GCP Cloud Run에서 FTP 서버에 접속하려면 고정 IP가 필요합니다.

### 추천 방법: Cloud NAT
```bash
# VPC 네트워크 생성
gcloud compute networks create mk-news-vpc \
    --subnet-mode=regional

# Cloud Router 생성
gcloud compute routers create mk-news-router \
    --network=mk-news-vpc \
    --region=asia-northeast3

# 고정 IP 예약
gcloud compute addresses create mk-news-static-ip \
    --region=asia-northeast3

# NAT 게이트웨이 생성
gcloud compute routers nats create mk-news-nat \
    --router=mk-news-router \
    --region=asia-northeast3 \
    --nat-all-subnet-ip-ranges \
    --nat-external-ip-pool=mk-news-static-ip
```

### Cloud Run VPC 연결
```bash
# Cloud Run 서비스에 VPC 연결
gcloud run services update mk-news-admin \
    --vpc-connector=mk-news-connector \
    --vpc-egress=all-traffic
```

## 배포 상태

- ✅ FastAPI: http://localhost:8000
- ✅ Streamlit: http://localhost:8501
- ✅ FTP 클라이언트
- ✅ GCS 클라이언트
- ✅ FTP 파이프라인
- ✅ 벡터 임베딩
- ✅ Streamlit UI 통합

## 참고 문서

- `FTP_GCS_PIPELINE_COMPLETE.md` - 상세 구현 내용
- `VERTEX_AI_GEMINIました.md` - GCP Vertex AI 사용 가이드
- `GEMINI_AND_EMBEDDING_STATUS.md` - Gemini 및 임베딩 상태

## 완료 상태

모든 기능이 정상적으로 구현되었습니다!

