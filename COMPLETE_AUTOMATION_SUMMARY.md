# GCP Cloud Run 완전 자동 배포 시스템

## 구현 완료

### 목표
로컬에 배포된 관리자 애플리케이션에서 Docker 이미지를 미리 빌드하여 Container Registry에 배포한 후, Terraform Apply로 GCP Cloud Run을 생성하는 과정을 완전 자동화

### 구현된 기능

#### 1. Docker 빌드 모듈 (`src/web/docker_build.py`)
- Artifact Registry 이미지 존재 확인
- Cloud Build를 통한 자동 빌드 및 푸시
- Python 3.11 기반 이미지 빌드 (로컬 3.13 호환성 문제 해결)

#### 2. Backend API 확장 (`src/web/app.py`)
```python
POST /api/docker/build       # 이미지 수동 빌드
POST /api/docker/check       # 이미지 존재 확인
POST /api/terraform/apply    # 자동 빌드 + Apply
```

#### 3. Terraform Apply 자동화
- 이미지 없으면 자동 빌드 (10-20분)
- 이미지 있으면 바로 Apply (2-3분)
- 통합 로그 표시

### 사용 방법

#### Streamlit UI에서 (권장)
1. "1️⃣ Terraform Init" 클릭
2. "2️⃣ Terraform Plan" 클릭
3. "3️⃣ Terra self Apply" 클릭
   - 자동으로 이미지 확인 및 빌드
   - 완료 후 Terraform으로 Cloud Run 생성

#### 백엔드 API 직접 호출
```bash
# 이미지 빌드
curl -X POST http://localhost:8000/api/docker/build

# 이미지 확인
curl -X POST http://localhost:8000/api/docker/check

# Apply (자동 빌드 포함)
curl -X POST http://localhost:8000/api/terraform/apply
```

### 자동화 프로세스

```
사용자: "Terraform Apply" 클릭
    ↓
Backend: 이미지 확인 (/api/docker/check)
    ↓
이미지 없음? → Cloud Build로 빌드 → Container Registry 푸시
이미지 있음? → 바로 다음 단계
    ↓
Terraform Apply 실행
    ↓
Cloud Run 생성 (이미지 사용)
    ↓
완료!
```

### 장점

1. **완전 자동화**: 사용자 개입 없이 전체 프로세스 실행
2. **스마트 빌드**: 이미지가 있으면 재빌드 안 함
3. **통합 로그**: 빌드 + Terraform 로그 한 번에 확인
4. **에러 처리**: 빌드 실패 시 Terraform 실행 안 됨
5. **표준 워크플로우**: Docker 빌드 → 푸시 → 배포

### 예상 소요 시간

- **첫 배포** (이미지 빌드 포함): 15-25분
- **재배포** (이미지 재사용): 2-3분

### 다음 단계

1. Streamlit UI 실행: `streamlit run src/web/streamlit_app.py`
2. "GCP 인프라 배포" 탭에서 3단계 순서대로 클릭
3. 배포 완료 후 Cloud Run URL 확인

### 참고 문서
- `DOCKER_BUILD_GUIDE.md`: Docker 빌드 상세 가이드
- `CLOUDRUN_DOCKER_DEPLOYMENT.md`: Cloud Run 배포 전략
- `DEPLOYMENT_AUTOMATION_GUIDE.md`: 자동화 구현 상세
