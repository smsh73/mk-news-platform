# Cloud Run 재배포 가이드

## 문제
Cloud Run 앱에서 plotly 모듈 누락 오류 발생

## 현재 상태
- ✅ requirements.txt에 plotly 추가 완료
- ⏳ Docker 이미지 재빌드 필요
- ⏳ Cloud Run 재배포 필요

## 재배포 방법

### 방법 1: Streamlit 대시보드에서 배포 (추천)

1. **로컬 대시보드 접속**
   ```
   http://localhost:8501
   ```

2. **GCP 인프라 탭으로 이동**
   - 상단 네비게이션에서 "GCP 인프라" 선택

3. **강제 재배포 설정**
   - "강제 이미지 재배포 (Force Rebuild)" 체크박스 체크
   - Docker 이미지를 새로 빌드합니다

4. **배포 시작**
   - "인프라 배포" 버튼 클릭
   - Init → Plan → Apply 단계 진행

5. **완료 확인**
   - Apply 성공 후 메인페이지 상단의 Cloud Run URL 확인
   - URL에 접속하여 오류 해결 확인

### 방법 2: 명령어로 배포

```bash
# 1. 프로젝트로 이동
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"

# 2. 가상환경 활성화
source venv/bin/activate

# 3. Docker 이미지 빌드 및 푸시
python src/web/docker_build.py --rebuild --push

# 4. Terraform으로 Cloud Run 재배포
cd terraform
terraform apply
```

### 방법 3: gcloud 명령어로 배포

```bash
# 1. Docker 이미지 강제 빌드
gcloud builds submit \
  --config cloudbuild-admin.yaml \
  --substitutions=_FORCE_REBUILD=true

# 2. Cloud Run 서비스 업데이트
gcloud run services update mk-news-admin \
  --region=asia-northeast3 \
  --image=asia-northeast3-docker.pkg.dev/mk-ai-project-473000/mk-news-repo/admin:latest
```

## 주의사항

- 재배포 중에는 일시적으로 서비스가 중단될 수 있습니다
- 배포는 약 5-10분 소요됩니다
- 배포 후 Cloud Run URL이 변경될 수 있습니다

## 확인 방법

배포 완료 후:
1. 메인페이지 상단의 Cloud Run URL 클릭
2. 페이지가 정상적으로 로드되는지 확인
3. chart/graph가 표시되는지 확인 (plotly 사용)

## 현재 상태

- **로컬 환경**: 정상 작동 ✅
- **Cloud Run**: plotly 오류 ❌ → 재배포 필요 ⏳



