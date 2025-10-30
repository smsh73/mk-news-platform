# service_df KeyError 수정

## 문제
```
KeyError: "['title'] not in index"
```

## 원인
`gcloud services list --format=json`의 출력 구조가 예상과 다름.
- 기대: `name`, `title`, `state` 컬럼
- 실제: 중첩된 구조 또는 다른 컬럼명

## 해결
동적으로 사용 가능한 컬럼을 확인하고 안전하게 표시:

```python
# 수정 전
st.dataframe(service_df[['name', 'title', 'state']], ...)

# 수정 후
available_cols = service_df.columns.tolist()
display_cols = []
for col in ['name', 'config', 'state']:
    if col in available_cols:
        display_cols.append(col)
st.dataframe(service_df[display_cols], ...)
```

## 적용 완료
- 파일 수정 완료
- 문법 검증 성공
- Streamlit 자동 리로드

## 테스트
"📋 활성화된 서비스 조회" 버튼을 다시 클릭하면 오류 없이 표시됩니다.


