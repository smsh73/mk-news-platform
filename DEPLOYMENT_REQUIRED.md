# 배포 필요 안내

## 현재 상황

모든 GCP 리소스가 아직 배포되지 않았습니다:
- Cloud Run 서비스 없음
- Vertex AI Indexes 없음
- Cloud SQL 인스턴스 없음
- Artifact Registry 저장소 없음

## 해결 방법

### 1. Streamlit UI에서 배포

1. 대시보드 접속: http://localhost:8501
2. "GCP 인프라" 탭 선택
3. "Terraform 배포" 버튼 클릭
4. 다음 단계가 자동 실행됩니다:
   - Init (초기화)
   - Plan (계획 수립)
   - Apply (배포 실행)

### 2. 배포 예상 시간

- Init: 1-2분
- Plan: 2-5분
- Apply: 10-30분 (이미지 빌드 포함)

### 3. 배포 후 확인할 리소스

배포가 완료되면 다음 리소스들이 생성됩니다:

```
Cloud Run: mk-news-admin 서비스
Vertex AI: Index 및 Index Endpoint
Cloud SQL: PostgreSQL 인스턴스
Artifact Registry: Docker 이미지 저장소
Cloud Storage: 데이터 버킷
```

## 주의사항

- 배포 전 GCP 인증 완료 필요
- 프로젝트 ID 설정 필요 (mk-ai-project-473000)
- 필수 API 활성화 필요

## 현재 상태

- 로컬 환경: ✅ 정상 작동
- GCP 배포: ⏳ 대기 중

## 다음 단계

Streamlit 대시보드에서 "Terraform 배포" 버튼을 클릭하여 배포를 시작하세요.


