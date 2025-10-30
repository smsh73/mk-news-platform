# Terraform 배포 상태 및 모니터링 가이드

## 현재 배포 상태

### 완료된 리소스 ✅
다음 리소스들이 이미 생성되어 있습니다:
- `google_artifact_registry_repository.mk_news_repo` - Artifact Registry
- `google_compute_network.mk_news_vpc` - VPC 네트워크
- `google_compute_subnetwork.mk_news_subnet` - 서브넷
- `google_project_service.*` - API 서비스 활성화
  - Cloud Run
  - Cloud SQL
  - Cloud Storage
  - Cloud Build
  - Compute Engine
  - Logging

### 아직 생성되지 않은 리소스 ❌
- Cloud Run 서비스 (mk-news-admin)
- admin_service_url 출력값

## 왜 로그가 안 보이는가?

### 문제 원인
Streamlit UI 코드에서 버튼이 spinner 안에 중첩되어 있어서 제대로 작동하지 않습니다.

**문제 코드** (src/web/streamlit_app.py:1472-1496):
```python
if st.button("🚀 Terraform 배포"):
    with st.spinner("배포 중..."):
        # init, plan 실행
        ...
        if st.button("✅ 배포 실행"):  # ❌ 중첩된 버튼은 작동 안 함
            result = subprocess.run(['terraform', 'apply', ...])
```

## 진행 상태 확인 방법

### 1. 터미널에서 직접 확인 (가장 확실함)

```bash
# Terraform 적용 실행
cd terraform
terraform apply -auto-approve

# 또는 단계별로
terraform init
terraform plan
terraform apply
```

### 2. 실시간 로그 확인

```bash
# Terraform 출력 보기
cd terraform
terraform apply -auto-approve 2>&1 | tee terraform.log

# Cloud Run 배포 진행 상황 확인
watch -n 5 'gcloud run services list --region=asia-northeast3'
```

### 3. FastAPI 로그 확인

```bash
# API 로그 실시간 확인
tail -f /tmp/uvicorn_fixed.log
```

### 4. GCP 콘솔에서 확인

1. **Cloud Run**: https://console.cloud.google.com/run?project=mk-ai-project-473000
2. **Cloud Build**: https://console.cloud.google.com/cloud-build?project=mk-ai-project-473000
3. **Artifact Registry**: https://console.cloud.google.com/artifacts?project=mk-ai-project-473000

## 배포 완료 한 후 확인

### URL 확인

```bash
terraform output admin_service_url
```

### 서비스 상태 확인

```bash
# Cloud Run 서비스 목록
gcloud run services list --region=asia-northeast3

# 특정 서비스 상세 정보
gcloud run services describe mk-news-admin --region=asia-northeast3 --format=json

# 서비스 로그
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mk-news-admin" --limit 50
```

## 해결 권장 사항

### 즉시 배포하기

터미널에서 직접 배포를 실행하는 것이 가장 확실합니다:

```bash
cd terraform

# 배포 실행 (약 10-30분 소요)
terraform apply -auto-approve

# 완료 후 URL 확인
terraform output admin_service_url
```

### 배포가 완료되면
1. Cloud Run URL 확인
2. 관리자 대시보드 접속
3. "관리자 앱 상태 확인" 버튼으로 URL 표시

## 현재 상태 요약

- Terraform 리소스: ✅ 부분적으로 생성됨
- Cloud Run: ❌ 아직 생성 안 됨
- URL: ❌ 아직 없음
- **다음 단계**: `terraform apply` 실행 필요
