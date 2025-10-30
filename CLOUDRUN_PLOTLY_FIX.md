# Cloud Run Plotly 모듈 오류 수정

## 문제
Cloud Run에 배포된 관리자 앱에서 `ModuleNotFoundError: No module named 'plotly'` 에러 발생

## 원인
requirements.txt에 plotly가 포함되지 않았음

## 해결 방법

### 1. requirements.txt 업데이트
```bash
# 추가된 패키지
plotly>=5.17.0
openpyxl>=3.1.0
```

### 2. Docker 이미지 재빌드 및 배포
```bash
# 1. Docker 이미지 강제 재빌드
gcloud builds submit --config cloudbuild-admin.yaml \
  --substitutions=_FORCE_REBUILD=true

# 또는 Streamlit 대시보드에서
# "GCP 인프라" 탭 → "강제 이미지 재배포" 체크 → 배포
```

### 3. Cloud Run 재배포
```bash
# Terraform으로 재배포
cd terraform
terraform apply
```

## Streamlit 대시보드에서 배포

1. http://localhost:8501 접속
2. "GCP 인프라" 탭 선택
3. "강제 이미지 재배포 (Force Rebuild)" 체크박스 선택
4. "인프라 배포" 버튼 클릭

## 확인

배포 후 다음 URL에서 확인:
```
https://mk-news-admin-43vp3ey7fa-du.a.run.app
```

## 상태

- ✅ requirements.txt 업데이트 완료
- ⏳ Docker 이미지 재빌드 필요
- ⏳ Cloud Run 재배포 필요



