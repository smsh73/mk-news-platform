# 개선된 배포 시스템

## 구현된 개선사항

### 1. 강제 재배포 기능
**문제**: 이미지가 Artifact Registry에 있어도 새 버전을 배포해야 하는 경우
**해결**: "🔄 강제 재배포" 체크박스 추가

**사용법**:
1. Streamlit UI에서 "3️⃣ Terraform Apply" 버튼 위
2. "🔄 강제 재배포 (기존 이미지 재빌드)" 체크박스 선택
3. Apply 클릭 → 이미지가 있어도 새로 빌드

**Backend 로직**:
```python
force_rebuild = request.get('force_rebuild', False)

if not image_exists or force_rebuild:
    # Docker 이미지 빌드 (기존 이미지 있어도 재빌드)
    build_result = builder.build_and_push_admin_image(force_rebuild=force_rebuild)
```

### 2. 실시간 로그 스트리밍 (제한적)
**현재 상태**: 
- Backend는 `capture_output=True`로 완료 후 로그 반환
- 완전한 실시간 스트리밍은 StreamingResponse 필요

**현재 구현**:
- 작업 완료 후 전체 로그 표시
- Expander에서 로그 확인 가능

**개선 방법** (향후):
- FastAPI StreamingResponse 사용
- Generator로 로그 yield
- Streamlit에서 실시간 업데이트

### 3. Streamlit 에러 수정
**문제**: `service_df[['name', 'title', 'state']]`에서 컬럼이 없을 때 에러
**해결**: 사용 가능한 컬럼만

```python
# 기존 코드 (에러 발생)
st.dataframe(service_df[['name', 'title', 'state']])

# 수정된 코드
available_columns = [col for col in ['name', 'title', 'state'] if col in service_df.columns]
if available_columns:
    st.dataframe(service_df[available_columns])
else:
    st.dataframe(service_df)
```

## 사용 방법

### 강제 재배포
1. "3️⃣ Terraform Apply" 버튼 섹션으로 스크롤
2. "🔄 강제 재배포" 체크박스 선택
3. Apply 클릭
4. 새 이미지 빌드 및 Cloud Run 배포

### 로그 확인
1. Apply 완료 후
2. "📋 전체 배포 로그" Expander 클릭
3. 빌드 + Terraform 로그 확인

## 장점

1. **유연성**: 필요시에만 재빌드
2. **시간 절약**: 기본적으로 이미지 있으면 재사용
3. **명확성**: 사용자가 재빌드 여부 선택
4. **안정성**: 에러 방지를 위한 컬럼 검증

## 향후 개선

### 완전한 실시간 로그 (StreamingResponse 구현)
```python
@app.post("/api/terraform/apply/stream")
async def terraform_apply_stream(request: dict = None):
    async def log_generator():
        # subprocess를 PIPE로 열어 실시간 읽기
        process = subprocess.Popen([...], stdout=subprocess.PIPE, ...)
        for line in iter(process.stdout.readline, b''):
            yield line.decode()
    
    return StreamingResponse(log_generator())
```

### Progress Bar 통합
- 진행률 계산
- 단계별 진행 표시
- 예상 완료 시간
