# Terraform Apply 오류 분석

## 발생한 오류 2가지

### 1. Vertex AI Index 오류
```
Error: dimensions is required but missing from Index metadata
```

**원인**: 
- Vertex AI Index 생성 시 metadata에 필수 필드가 누락됨
- `dimensions` 또는 관련 필드가 필요

**해결**: 
- `metadata` 블록에 필요한 필드를 추가 (위치 정보 포함)

### 2. Cloud Run 이미지 오류
```
Error: Image 'asia-northeast3-docker.pkg.dev/.../mk-news-api:latest' not found
```

**원인**: 
- Artifact Registry에 Docker 이미지가 아직 배포되지 않음
- Cloud Run은 이미지가 있어야 실행 가능

**해결책**:
1. Cloud Run 배포 전에 이미지가 필요하므로 순서 변경 필요
2. 또는 더미 이미지 사용 (실제로는 컨테이너 이미지를 먼저 빌드)

## 다음 단계

### 옵션 1: Cloud Run 배포 제거 (권장)
테스트 환경에서는 Cloud Run 배포를 제외하고:
1. Cloud SQL
2. Vertex AI Index
3. Storage Buckets

만 먼저 배포하고, 이미지 빌드 후 수동으로 Cloud Run 배포

### 옵션 2: 더미 이미지 사용
이미 존재하는 이미지로 테스트 (예: `hello-world`)

### 옵션 3: 이미지 빌드 스크립트 추가
Terraform 외부에서 이미지를 먼저 빌드하고 배포

## 권장사항

**현재 상황**: Cloud SQL과 Storage는 이미 배포 완료

**다음 작업**:
1. Vertex AI Index 수정 후 재배포
2. Cloud Run은 이미지 빌드 후 별도로 배포
3. 또는 Cloud Run 설정을 주석 처리하여 Core 인프라만 배포
