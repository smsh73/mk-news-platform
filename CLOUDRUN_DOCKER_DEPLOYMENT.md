# Cloud Run Docker 이미지 배포 전략

## 문제 상황
Cloud Run 배포 시 Docker 이미지가 필요한데, 현재는 이미지가 없어서 Terraform Apply가 실패할 수 있습니다.

## 해결 방법: 두 가지 접근

### 방법 A: Cloud Build 사용 (권장)
Dockerfile.admin을 사용하여 이미지를 빌드하고 Artifact Registry에 푸시한 후, Terraform에서 Cloud Run 배포

**장점:**
- GCP 네이티브 서비스 활용
- 이미지 버전 관리 용이
- 빌드 로그 자동 저장

**단계:**
1. Docker 이미지 빌드 및 푸시 (클라우드에서)
2. Terraform Apply로 Cloud Run 생성

### 방법 B: Streamlit UI에 빌드 기능 추가
사용자가 Streamlit 대시보드에서 직접 이미지 빌드를 트리거

**장점:**
- 원클릭 배포 가능
- UI 통합

**단점:**
- 빌드 시간이 길어지면 타임아웃 위험
- 복잡한 에러 처리 필요

## 추천 절차

### 1단계: Docker 이미지 수동 빌드 (한 번만)
```bash
gcloud builds submit \
  --tag asia-northeast3-docker.pkg.dev/mk-ai-project-473000/mk-news-repo/mk-news-admin:latest \
  --timeout=1800s \
  -f Dockerfile.admin \
  .
```

**예상 시간:** 10-20분

### 2단계: Terraform Apply로 Cloud Run 생성
Streamlit UI에서 "Terraform Apply" 클릭

**Terraform이 수행하는 작업:**
- Artifact Registry에서 이미지 참조
- Cloud Run 서비스 생성
- 환경 변수 설정
- VPC Connector 연결
- IAM 권한 설정

**예상 시간:** 2-3분

### 3단계: Cloud Run 접속
```bash
gcloud run services list --region=asia-northeast3
gcloud run services describe mk-news-admin --region=asia-northeast3 --format='value(status.url)'
```

## 왜 이 방법인가?

1. **명확한 책임 분리**
   - Docker 빌드: gcloud CLI로 명시적 실행
   - Cloud Run 생성: Terraform으로 인프라 관리

2. **디버깅 용이**
   - 빌드 실패 시 Cloud Build 로그 확인
   - Terraform 실패 시 Plan 결과 확인

3. **재사용 가능**
   - 이미지 한 번 빌드 후 재사용
   - Cloud Run은 Terraform으로 수정

4. **표준 워크플로우**
   - Docker 빌드 → 푸시 → 배포
   - GCP 모범 사례 준수

## 자동화 고려사항

향후 자동화가 필요하다면:

```python
# src/web/app.py에 추가
@app.post("/api/docker/build")
async def build_docker_image():
    """Docker 이미지 빌드"""
    result = subprocess.run([
        'gcloud', 'builds', 'submit',
        '--tag', 'asia-northeast3-docker.pkg.dev/...',
        '-f', 'Dockerfile.admin'
    ], capture_output=True, text=True, timeout=1800)
    
    return {"success": result.returncode == 0, "logs": result.stdout}
```

하지만 현재는 수동 빌드가 더 안정적입니다.

## 체크리스트

배포 전 확인:
- [ ] GCP 인증 완료 (`gcloud auth login`)
- [ ] Artifact Registry 인증 설정 (`gcloud auth configure-docker`)
- [ ] Terraform 상태 확인 (`terraform plan`)
- [ ] Dockerfile.admin 존재 확인
- [ ] requirements.txt 준비 완료

배포 후 확인:
- [ ] Cloud Run 서비스 Running 상태
- [ ] 외부 접속 가능
- [ ] 로그에서 에러 없음
- [ ] Terraform State에 추가됨
