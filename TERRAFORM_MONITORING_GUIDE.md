# Terraform 배포 모니터링 가이드

## 현재 상태

✅ **Terraform은 정상적으로 실행되었습니다!**

확인된 리소스:
- google_artifact_registry_repository.mk_news_repo
- google_compute_network.mk_news_vpc
- google_compute_subnetwork.mk_news_subnet
- google_project_service.* (Cloud Run, Cloud SQL, Storage 등)
- 기타 인프라 리소스

## 진행 상태 확인 방법

### 1. Streamlit 대시보드에서 확인

**현재 코드 문제**: Streamlit UI에서 apply 후 로그가 표시되지 않음

**해결 방법**:
- API 응답을 확인: FastAPI는 정상적으로 로그 반환
- Streamlit 페이지를 새로고침하여 상태 확인

### 2. 터미널에서 실시간 모니터링

```bash
# Terraform 출력 확인
cd terraform
terraform output -json

# Cloud Run 서비스 확인
gcloud run services list --region=asia-northeast3

# 배포 진행 상황 확인
gcloud run services describe mk-news-admin --region=asia-northeast3 --format=json

# 로그 확인
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mk-news-admin" --limit 50
```

### 3. Streamlit 로그 확인

```bash
# FastAPI 로그
tail -f /tmp/uvicorn_fixed.log

# Streamlit 로그
tail -f /tmp/streamlit_clean.log
```

### 4. Terraform 상태 확인

```bash
# Terraform 리소스 목록
cd terraform
terraform state list

# 특정 리소스 확인
terraform state show google_cloud_run_v2_service.mk_news_admin

# 배포 결과 확인
terraform output admin_service_url
```

### 5. GCP 콘솔에서 확인

1. **Cloud Run**: https://console.cloud.google.com/run
2. **Artifact Registry**: https://console.cloud.google.com/artifacts
3. **Vertex AI**: https://console.cloud.google.com/vertex-ai
4. **Terraform**: https://console.cloud.google.com/cloud-build

## 현재 문제

### Streamlit UI에서 로그가 표시되지 않는 이유

**코드 분석** (src/web/streamlit_app.py:1487):
```python
if st.button("✅ 배포 실행"):  # 이 버튼이 중첩되어 있어서 작동 안 함
    result = subprocess.run(['terraform', 'apply', ...])
```

**문제점**:
- 버튼이 spinner 안에 중첩됨
- Streamlit은 동일 컨텍스트에서 버튼이 제대로 작동하지 않음

## 해결 방법

### 임시 해결 (터미널 사용)

```bash
# 직접 배포 실행
cd terraform
terraform apply -auto-approve

# 또는 강제 재배포
terraform apply -auto-approve -refresh
```

### UI 개선 방법

Streamlit 코드를 수정하여 단계별로 진행하도록 변경 필요

## 배포 확인

### URL 확인

```bash
# 관리자 대시보드 URL
terraform output admin_service_url
```

### 서비스 상태 확인

```bash
# Cloud Run 서비스 상태
gcloud run services list --region=asia-northeast3

# Cloud Run 서비스 상세 정보
gcloud run services describe mk-news-admin --region=asia-northeast3
```

## EFTER 배포

배포가 완료되면:
1. Cloud Run URL 확인
2. 서비스 접속 테스트
3. 관리자 대시보드 기능 테스트


