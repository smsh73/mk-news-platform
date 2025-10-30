# Cloud Run 관리자 페이지 URL 안내

## 현재 상황

Terraform 파일을 확인한 결과, Cloud Run 서비스가 주석 처리되어 있어 아직 GCP에 배포되지 않은 상태입니다.

```terraform
# resource "google_cloud_run_v2 тervice" "mk_news_admin" {
#   ...
# }
```

## 관리자 페이지 접속 방법

### 1. 로컬 환경 (현재 사용 가능)

Streamlit 관리자 대시보드가 로컬에서 실행 중입니다:

```
http://localhost:8501
```

### 2. GCP Cloud Run 배포 후 (배포 필요)

Cloud Run 서비스가 배포되면 다음 URL 형식으로 접속 가능합니다:

```
https://mk-news-admin-{hash}-{region}.a.run.app
```

정확한 URL은 Terraform apply 완료 후 다음 명령으로 확인할 수 있습니다:

```bash
# Terraform output 확인
terraform output admin_service_url

# 또는 gcloud 명령어로 확인
gcloud run services describe mk-news-admin --region=asia-northeast3 --format='value(status.url)'
```

## 배포 방법

### 현재 로컬 배포

1. Streamlit 대시보드: http://localhost:8501 ✅ (실행 중)
2. FastAPI 서비스: http://localhost:8000 ✅ (실행 중)

### GCP 배포 진행 방법

1. Streamlit 대시보드 접속: http://localhost:8501
2. "☁️ GCP 인프라" 탭 선택
3. "🚀 Terraform 배포 실행" 버튼 클릭
4. Init → Plan → Apply가 자동으로 실행됩니다
5. 완료 후 제공되는 URL로 접속

## 참고사항

- Terraform의 admin 서비스가 주석 처리되어 있어 배포하려면 주석을 해제해야 합니다
- Docker 이미지가 성공적으로 빌드되어야 Cloud Run 배포가 가능합니다
- 배포 시간: 약 10-30분 소요 예상

## 빠른 확인 명령

```bash
# 현재 실행 중인 로컬 서비스
curl http://localhost:8501  # Streamlit
curl http://localhost:8000/docs  # FastAPI

# GCP 배포 상태 확인
gcloud run services list --region=asia-northeast3
```

