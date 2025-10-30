# Cloud Run 자동 배포 전략

## 문제점
- Cloud Run 배포 시 Docker 이미지 필요
- 이미지가 없으면 Terraform Apply 실패

## 해결 방법: 두 가지 옵션

### 옵션 1: Docker 이미지 먼저 빌드 (권장)
- 사용자가 명시적으로 Docker 이미지 빌드 후 Apply
- 장점: 명확한 프로세스, 디버깅 쉬움
- 단점: 수동 단계 필요

### 옵션 2: Terraform Apply 자동화
- Apply 시 Docker 이미지 없으면 자동 빌드
- 장점: 자동화
- 단점: 복잡도 증가, 시간 소요

## 권장 절차

### Step 1: Docker 이미지 빌드 (한 번만)
```bash
gcloud builds submit \
  --tag asia-northeast3-docker.pkg.dev/mk-ai-project-473000/mk-news-repo/mk-news-admin:latest \
  --timeout=1800s \
  -f Dockerfile.admin
```

### Step 2: Terraform Apply로 Cloud Run 생성
- Streamlit UI에서 "Terraform Apply" 클릭
- Terraform이 이미지를 사용하여 Cloud Run 생성

## 구현 방법

### 방법 A: Backend에서 이미지 존재 확인
```python
# src/web/app.py의 terraform_apply 함수
def check_and_build_image():
    # Artifact Registry에서 이미지 확인
    # 없으면 gcloud builds submit 실행
    # 있으면 바로 Terraform Apply
```

### 방법 B: Streamlit UI에 빌드 버튼 추가
```python
# src/web/streamlit_app.py
# "Docker 이미지 빌드" 탭 추가
# 빌드 완료 후 "Terraform Apply" 활성화
```

## 최종 권장 사항

**사용자 가이드에 명확한 순서 제시:**
1. Docker 이미지 빌드 (명령어 제공)
2. Terraform Apply (Streamlit UI에서)
3. Cloud Run 접속 URL 확인

**이유:**
- 명확성: 사용자가 각 단계를 이해
- 디버깅: 문제 발생 시 단계별 확인 가능
- 유연성: 필요 시 수동 조작 가능
