# 매니지드 서비스 아키텍처 가이드

## 🏗️ 개요

매일경제 신문기사 벡터임베딩 플랫폼을 GCP 매니지드 서비스로 구축하여 서버리스 아키텍처를 구현합니다. 맥북에서 개발하고 GCP에서 완전 매니지드 서비스로 운영합니다.

## 🎯 아키텍처 목표

### 1. **서버리스 운영**
- Cloud Run 기반 자동 스케일링
- 서버 관리 불필요
- 사용량 기반 과금

### 2. **매니지드 데이터베이스**
- Cloud SQL PostgreSQL
- 자동 백업 및 고가용성
- Private IP 연결

### 3. **AI/ML 서비스 통합**
- Vertex AI Vector Search
- Gemini API 연동
- 매니지드 임베딩 서비스

### 4. **보안 강화**
- VPC 네트워크 격리
- Private 서비스 간 통신
- IAM 기반 접근 제어

## 🏛️ 아키텍처 구성

### 1. **Cloud Run (애플리케이션 서버)**
```
┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │ Streamlit Admin │
│   (Port 8000)   │    │   (Port 8501)   │
│                 │    │                 │
│ • REST API      │    │ • 관리자 대시보드│
│ • 벡터 검색      │    │ • 모니터링      │
│ • XML 처리      │    │ • 설정 관리      │
└─────────────────┘    └─────────────────┘
```

**특징:**
- 자동 스케일링 (0-1000 인스턴스)
- 서버리스 운영
- HTTPS 자동 제공
- 컨테이너 기반 배포

### 2. **Cloud SQL (데이터베이스)**
```
┌─────────────────────────────────┐
│        Cloud SQL PostgreSQL     │
│                                 │
│ • Private IP 연결               │
│ • 자동 백업 (30일 보관)          │
│ • SSL 암호화                    │
│ • 고가용성                      │
└─────────────────────────────────┘
```

**특징:**
- Private IP (10.0.1.0/24)
- 자동 백업 및 복구
- SSL/TLS 암호화
- 모니터링 및 알림

### 3. **Vertex AI (AI/ML 서비스)**
```
┌─────────────────────────────────┐
│        Vertex AI Platform       │
│                                 │
│ • Vector Search                 │
│ • Embedding API                  │
│ • Gemini API                    │
│ • 매니지드 인덱스               │
└─────────────────────────────────┘
```

**특징:**
- 매니지드 벡터 검색
- 자동 인덱스 관리
- 고성능 검색 엔진
- 실시간 업데이트

### 4. **Cloud Storage (데이터 저장)**
```
┌─────────────────────────────────┐
│        Cloud Storage             │
│                                 │
│ • XML 파일 저장                 │
│ • 임베딩 벡터 캐시               │
│ • 로그 및 아티팩트              │
│ • 버전 관리                      │
└─────────────────────────────────┘
```

**특징:**
- 글로벌 분산 저장
- 자동 버전 관리
- 생명주기 정책
- 접근 제어

### 5. **VPC 네트워크 (보안)**
```
┌─────────────────────────────────┐
│           VPC Network            │
│                                 │
│ • Private 서비스 통신           │
│ • 방화벽 규칙                    │
│ • NAT Gateway                   │
│ • VPC Connector                  │
└─────────────────────────────────┘
```

**특징:**
- Private IP 통신
- 네트워크 격리
- 보안 강화
- 트래픽 제어

## 🚀 배포 프로세스

### 1. **인프라 배포**
```bash
# Terraform으로 GCP 리소스 생성
cd terraform
terraform init
terraform plan
terraform apply
```

**생성되는 리소스:**
- VPC 네트워크 및 서브넷
- Cloud SQL 인스턴스 (Private IP)
- Cloud Storage 버킷
- Vertex AI Vector Search
- VPC Access Connector
- Artifact Registry

### 2. **컨테이너 이미지 빌드**
```bash
# FastAPI 이미지
docker build -f Dockerfile.api -t mk-news-api:latest .
docker tag mk-news-api:latest asia-northeast3-docker.pkg.dev/godwind2015/mk-news-repo/mk-news-api:latest
docker push asia-northeast3-docker.pkg.dev/godwind2015/mk-news-repo/mk-news-api:latest

# Streamlit 이미지
docker build -f Dockerfile.admin -t mk-news-admin:latest .
docker tag mk-news-admin:latest asia-northeast3-docker.pkg.dev/godwind2015/mk-news-repo/mk-news-admin:latest
docker push asia-northeast3-docker.pkg.dev/godwind2015/mk-news-repo/mk-news-admin:latest
```

### 3. **Cloud Run 서비스 배포**
```bash
# FastAPI 서비스
gcloud run deploy mk-news-api \
    --image=asia-northeast3-docker.pkg.dev/godwind2015/mk-news-repo/mk-news-api:latest \
    --region=asia-northeast3 \
    --platform=managed \
    --allow-unauthenticated

# Streamlit 서비스
gcloud run deploy mk-news-admin \
    --image=asia-northeast3-docker.pkg.dev/godwind2015/mk-news-repo/mk-news-admin:latest \
    --region=asia-northeast3 \
    --platform=managed \
    --allow-unauthenticated
```

## 📊 서비스 구성

### 1. **FastAPI 서비스 (mk-news-api)**
- **CPU**: 2 vCPU
- **메모리**: 4GB
- **포트**: 8000
- **환경변수**:
  - `GCP_PROJECT_ID`: godwind2015
  - `DB_HOST`: Cloud SQL Private IP
  - `DB_NAME`: mk_news
  - `STORAGE_BUCKET`: mk-news-storage-godwind2015
  - `VECTOR_INDEX_ID`: Vector Search 인덱스 ID
  - `VECTOR_ENDPOINT_ID`: Vector Search 엔드포인트 ID

### 2. **Streamlit 서비스 (mk-news-admin)**
- **CPU**: 1 vCPU
- **메모리**: 2GB
- **포트**: 8501
- **환경변수**:
  - `GCP_PROJECT_ID`: godwind2015
  - `API_URL`: FastAPI 서비스 URL

### 3. **Cloud SQL 인스턴스 (mk-news-db)**
- **엔진**: PostgreSQL 15
- **인스턴스 클래스**: db-standard-2
- **스토리지**: SSD
- **백업**: 30일 보관
- **네트워크**: Private IP (VPC 내부)

### 4. **Vertex AI Vector Search**
- **인덱스**: mk-news-vector-index
- **차원**: 768
- **거리 측정**: DOT_PRODUCT_DISTANCE
- **알고리즘**: Tree-AH
- **업데이트 방식**: BATCH_UPDATE

## 🔧 운영 관리

### 1. **자동 스케일링**
- **최소 인스턴스**: 0 (서버리스)
- **최대 인스턴스**: 1000
- **스케일링 트리거**: CPU 사용률, 요청 수
- **콜드 스타트**: ~2-3초

### 2. **모니터링**
- **Cloud Logging**: 애플리케이션 로그
- **Cloud Monitoring**: 성능 메트릭
- **Cloud Trace**: 분산 추적
- **알림**: 오류 및 성능 임계값

### 3. **보안**
- **IAM**: 서비스 계정 기반 권한
- **VPC**: Private 네트워크 격리
- **SSL/TLS**: 모든 통신 암호화
- **방화벽**: 네트워크 레벨 보안

## 💰 비용 최적화

### 1. **서버리스 비용**
- **Cloud Run**: 요청 수 및 실행 시간 기반
- **Cloud SQL**: 인스턴스 크기 기반
- **Vertex AI**: API 호출 수 기반
- **Cloud Storage**: 저장 용량 기반

### 2. **비용 절약 전략**
- **자동 스케일링**: 사용량에 따른 자동 조정
- **리전 선택**: asia-northeast3 (서울)
- **스토리지 클래스**: Standard → Nearline → Coldline
- **백업 정책**: 30일 → 7일로 조정 가능

## 🚀 배포 스크립트

### 1. **전체 배포**
```bash
./deploy_managed.sh
```

### 2. **서비스 중지**
```bash
./stop_managed.sh
```

### 3. **서비스 재시작**
```bash
./restart_managed.sh
```

## 📈 성능 특성

### 1. **응답 시간**
- **API 응답**: 평균 200-500ms
- **벡터 검색**: 평균 100-300ms
- **데이터베이스 쿼리**: 평균 50-150ms
- **콜드 스타트**: 2-3초

### 2. **처리량**
- **동시 요청**: 1000+ RPS
- **벡터 검색**: 100+ QPS
- **XML 처리**: 100+ 파일/분
- **임베딩 생성**: 50+ 문서/분

### 3. **가용성**
- **SLA**: 99.9%
- **다중 리전**: 자동 장애 조치
- **백업**: 자동 복구
- **모니터링**: 실시간 알림

## 🔍 트러블슈팅

### 1. **일반적인 문제**
- **콜드 스타트 지연**: 첫 요청 시 2-3초 지연
- **메모리 부족**: 배치 크기 조정 필요
- **데이터베이스 연결**: Private IP 설정 확인
- **권한 오류**: 서비스 계정 권한 확인

### 2. **모니터링 명령어**
```bash
# 서비스 상태 확인
gcloud run services list --region=asia-northeast3

# 로그 확인
gcloud run logs tail mk-news-api --region=asia-northeast3

# 데이터베이스 상태
gcloud sql instances describe mk-news-db

# Vertex AI 상태
gcloud ai index-endpoints list --region=asia-northeast3
```

## 📚 참고 자료

- [Cloud Run 문서](https://cloud.google.com/run/docs)
- [Cloud SQL 문서](https://cloud.google.com/sql/docs)
- [Vertex AI 문서](https://cloud.google.com/vertex-ai/docs)
- [VPC 문서](https://cloud.google.com/vpc/docs)

---

**매일경제 신문기사 벡터임베딩 플랫폼**  
GCP 매니지드 서비스 아키텍처  
MK AI Project - godwind2015@gmail.com

