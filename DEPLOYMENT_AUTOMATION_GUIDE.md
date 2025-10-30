# GCP Cloud Run 자동 배포 가이드

## 구현 완료: Docker 이미지 자동 빌드 및 Cloud Run 배포

### 구현 내용

1. **Docker 이미지 빌드 모듈** (`src/web/docker_build.py`)
   - 이미지 존재 여부 확인
   - 이미지 자동 빌드 및 Container Registry 푸시

2. **Backend API 확장** (`src/web/app.py`)
   - `/api/docker/build`: 이미지 수동 빌드
   - `/api/docker/check`: 이미지 존재 확인
   - `/api/terraform/apply`: 이미지 자동 확인 및 빌드 → Terraform Apply

### 작동 방식

#### Terraform Apply 클릭 시:

```
1. Docker 이미지 확인 (Artifact Registry)
   ├─ 이미지 있음 → 바로 Terraform Apply
   └─ 이미지 없음 → 이미지 빌드 → Terraform Apply

2. Terraform Apply 실행
   └─ Cloud Run 생성 (이미지 사용)
```

### 사용 방법

#### Streamlit UI에서:

1. **1️⃣ Terraform Init** 클릭
2. **2️⃣ Terraform Plan** 클릭
3. **3️⃣ Terraform Apply** 클릭
   - 이미지가 없으면 자동으로 빌드 (10-20분)
   - 이미지가 있으면 바로 Apply (2-3분)

#### 수동 빌드가 필요한 경우:

```bash
# 터미널에서 실행
curl -X POST http://localhost:8000/api/docker/build
```

### 장점

1. **완전 자동화**: 사용자가 별도 명령어 입력 불필요
2. **스마트 인식**: 이미지가 있으면 재빌드 안 함
3. **통합 로그**: 빌드 + Terraform 로그 한번에 확인
4. **에러 핸들링**: 빌드 실패 시 Terraform 실행 안 됨

### 예상 시간

- **이미지 첫 빌드**: 15-25분 (빌드 + Apply)
- **이미지 재사용**: 2-3분 (Apply만)
