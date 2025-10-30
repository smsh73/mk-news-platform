# GCP 배포 가이드

## 현재 상태

✅ 준비 완료:
- GCP 프로젝트: mk-ai-project-473000 (설정됨)
- Terraform 설정 파일: terraform/main.tf
- Docker 이미지: Dockerfile.admin
- Streamlit 대시보드: http://localhost:8501

❌ 배포 필요:
- Vertex AI Indexes
- Cloud Run 서비스
- Cloud SQL 인스턴스
- Artifact Registry 저장소

## 배포 방법 (선택지 2가지)

### 방법 1: Streamlit UI에서 배포 (권장)

1. **Streamlit 대시보드 접속**
   ```
   http://localhost:8501
   ```

2. **GCP 인프라 탭 선택**
   - 상단 탭 메뉴에서 "GCP 인프라" 클릭

3. **Terraform 배포 버튼 클릭**
   - "인프라 배포" 섹션으로 스크롤
   - "Terraform 배포" 버튼 클릭
   - Init → Plan → Apply가 자동으로 실행됩니다

4. **배포 완료 대기**
   - 예상 시간: 10-30분
   - 로그를 확인하며 진행 상황 모니터링

5. **배포 확인**
   - "관리자 앱 상태 확인" 버튼으로 URL 확인

### 방법 2: 터미널에서 직접 배포

```bash
cd terraform

# 1. Terraform 초기화
terraform init

# 2. 배포 계획 확인
terraform plan

# 3. 배포 실행
terraform apply

# 4. 배포 후 URL 확인
terraform output admin_service_url
```

## 배포 후 생성될 리소스

1. **Cloud Run**: mk-news-admin 서비스
   - Streamlit 관리자 대시보드
   - URL: https://mk-news-admin-xxx.asia-northeast3.run.app

2. **Vertex AI**:
   - Vector Index
   - Index Endpoint

3. **Cloud SQL**:
   - PostgreSQL 인스턴스
   - 데이터베이스: mk_news_db

4. **Artifact Registry**:
   - Docker 이미지 저장소
   - Region: asia-northeast3

5. **Cloud Storage**:
   - 데이터 버킷
   - XML 파일 저장용

## 주의사항

- 배포 전 GCP 인증 완료 필요
- 비용 발생 가능 (Cloud Run, Vertex AI 등)
- 배포에는 10-30분 소요

## 다음 단계

Streamlit 대시보드의 "Terraform 배포" 버튼을 클릭하여 배포를 시작하세요.


