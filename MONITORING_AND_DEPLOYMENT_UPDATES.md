# 모니터링 및 배포 로그 개선 가이드

## 요청 사항

1. 인프라 모니터링에 모든 리소스 추가
2. Terraform 배포 시 자세한 로그 화면 표시

## 수정 필요 부분

### 1. 인프라 모니터링 리소스 추가

현재 위치: `src/web/streamlit_app.py` 라인 1527-1544

추가할 리소스:
- Cloud Run 서비스
- Vertex AI Index Endpoints  
- Vertex AI Indexes
- Artifact Registry
- Cloud Storage

### 2. Terraform 배포 로그 개선

현재 위치: `src/web/streamlit_app.py` 라인 1471-1496

개선 사항:
- Step별 진행 상황 표시
- 각 단계 로그 출력
- Apply 로그 전체 표시
- 배포 완료 후 URL 자동 표시

## 수동 수정 가이드

Terraform 파일 복원 후 수동으로 수정해야 합니다.

### 인프라 모니터링 섹션에 추가할 코드

```python
# Cloud Run 서비스
result = subprocess.run(['gcloud', 'run', 'services', 'list', '--region=asia-northeast3'], 
                      capture_output=True, text=True, timeout=30)
if result.returncode == 0:
    st.subheader("☁️ Cloud Run")
    st.code(result.stdout)

# Vertex AI Index Endpoints
result = subprocess.run(['gcloud', 'ai', 'index-endpoints', 'list', '--region=asia-northeast3'], 
                      capture_output=True, text=True, timeout=30)
# ... 나머지 리소스들
```

### Terraform 배포 개선 코드

```python
if st.button("🚀 Terraform 배포"):
    try:
        # Step 1: Init
        st.info("🔧 Step 1/3: Terraform 초기화 중...")
        # 로그 표시
        
        # Step 2: Plan  
        st.info("🔍 Step 2/3: Terraform Plan 실행 중...")
        # 로그 표시
        
        # Step 3: Apply
        if st.button("✅ 배포 실행"):
            st.info("🚀 Step 3/3: Terraform Apply 실행 중...")
            # 로그 표시
```

## 현재 상태

- 파일 복원 완료
- 수동 수정 필요


