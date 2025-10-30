# 배포 요약

## 완료된 작업

### 1. Backend API 수정 (src/web/app.py) ✅
- Artifact Registry 이미지 확인 로직 추가
- 기존 Cloud Run 서비스 확인 로직 추가
- 배포 성공 시 URL 자동 추출 및 로그 출력

### 2. Terraform 수정 (terraform/main.tf) ✅
- Cloud Run 서비스 리소스 주석 해제
- Lifecycle 규칙 추가 (이미지 변경 무시)
- admin_service_url output 추가

### 3. 로컬 배포 완료 ✅
- Streamlit 재시작 완료
- 서비스 실행 중

## 배포 프로세스

### 자동 배포 흐름
1. **Artifact Registry 배포** - Docker 이미지 빌드 및 푸시
2. **Cloud Run 리소스 확인** - 기존 서비스 조회
3. **Cloud Run 배포** - Terraform apply
4. **외부 접속 URL 제공** - 성공 시 URL 로그 출력

### 배포 방법

#### 옵션 1: Streamlit UI 사용 (추천)
```
1. http://localhost:8501 접속
2. "☁️ GCP 인프라" 탭 선택
3. "🚀 Terraform 배포" 버튼 클릭
4. 강제 재배포 체크 (필요시)
5. 대기 (10-30분)
```

#### 옵션 2: 직접 API 호출
```bash
# 이미지 확인
curl -X POST http://localhost:8000/api/docker/check

# 강제 빌드 (필요시)
curl -X POST http://localhost:8000/api/docker/build \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": true}'

# Terraform Apply
curl -X POST http://localhost:8000/api/terraform/apply \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": false}'
```

## 접속 정보

### 로컬 환경
- Streamlit: http://localhost:8501 ✅
- FastAPI: http://localhost:8000 ✅

### GCP Cloud Run (배포 후)
- URL 형식: `https://mk-news-admin-{hash}-as.a.run.app`
- 확인 방법:
```bash
terraform output admin_service_url
```

## 현재 상태

- ✅ Dockerfile 수정 (templates 제거)
- ✅ Backend API 수정 (이미지 체크, URL 출력)
- ✅ Terraform 수정 (Cloud Run 활성화)
- ✅ 로erts Streamlit 재시작
- ⏳ GCP 배포 대기 중

## 다음 단계

1. GCP 프로젝트 인증 완료 확인
2. Terraform 배포 버튼 클릭
3. 배포 완료 후 제공되는 URL로 접속


