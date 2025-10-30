# Vertex AI 연결 오류 수정

## 발생한 오류
```
ERROR: (gcloud.ai.models.list) Error parsing [region]. 
The [region] resource is not properly specified. 
Failed to find attribute [region].
```

## 원인
`gcloud ai models list` 명령어에 `--region` 파라미터가 누락됨

## 수정 내용

### 파일: `src/web/streamlit_app.py`
**위치**: 인프라 테스트 섹션

#### 수정 전:
```python
result = subprocess.run(['gcloud', 'ai', 'models', 'list'], 
                      capture_output=True, text=True, timeout=30)
```

#### 수정 후:
```python
result = subprocess.run(['gcloud', 'ai', 'models', 'list', '--region=asia-northeast3'], 
                      capture_output=True, text=True, timeout=30)
```

## 수정 완료

✅ Streamlit 재배포 완료
- URL: http://localhost:8501
- 상태: 정상 실행 중 (200 OK)

## 테스트 방법

1. Streamlit에 접속: http://localhost:8501
2. "GCP 인프라" 탭 선택
3. "인프라 테스트" 섹션으로 이동
4. "연결 테스트" 버튼 클릭
5. Vertex AI 연결 결과 확인

## 참고사항

Region 파라미터는 Vertex AI 명령어에서 필수입니다:
- 기본 region이 설정되지 않은 경우 명시적으로 지정 필요
- 프로젝트의 region: `asia-northeast3` (서울)
- 다른 region 사용 시: `--region=<region-name>`
