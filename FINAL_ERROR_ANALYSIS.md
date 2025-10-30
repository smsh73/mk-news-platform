# Terraform Apply 최종 오류 분석

## 발생한 오류 2가지

### 1. Vertex AI Index 오류
```
Error: dimensions is required but missing from Index metadata
```

**원인**: 
- Vertex AI Index의 `metadata` 블록이 불완전함
- Terraform의 `google_vertex_ai_index` 리소스는 복잡한 metadata 설정을 요구함

**해결**: 
- Vertex AI Index를 주석 처리하여 나중에 수동으로 생성
- 또는 올바른 metadata 스키마를 구성해야 함

### 2. Cloud Run 이미지 오류  
```
Error: Image 'asia-northeast3-docker.pkg.dev/.../mk-news-api:latest' not found
```

**원인**: 
- Artifact Registry에 Docker 이미지가 없음
- Cloud Run은 이미지가 있어야만 배포 가능

**해결**: 
- Cloud Run 배포를 주석 처리하거나
- 이미지 빌드 후 배포

## 현재 상태

✅ **성공적으로 배포됨**:
- Cloud SQL 인스턴스 및 데이터베이스 (16분 소요)
- Vertex AI Index Endpoint

❌ **실패**:
- Vertex AI Index (metadata 설정 문제)
- Cloud Run 서비스 2개 (이미지 없음)

## 다음 단계

### 권장 사항: 단계별 배포

1. **이미 배포된 인프라 활용**:
   - Cloud SQL: 사용 가능
   - Storage Buckets: 사용 가능
   - VPC, Connector: 사용 가능

2. **Vertex AI Index**:
   - Cloud Console에서 수동 생성
   - 또는 올바른 Terraform 설정으로 재시도

3. **Cloud Run**:
   - Docker 이미지 빌드 및 배포
   - `gcloud builds submit` 명령어로 이미지 생성
   - 이미지 존재 확인 후 Cloud Run 배포

## 결론

**핵심 인프라는 배포 완료**되었습니다:
- Database
- Storage
- Networking
- AI Platform Endpoint

애플리케이션 레벨 리소스(Index, Cloud Run)는 추가 설정이 필요합니다.
