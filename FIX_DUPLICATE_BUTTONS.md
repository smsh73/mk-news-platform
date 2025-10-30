# 중복 버튼 오류 수정

## 문제
이모지 제거 과정에서 버튼 텍스트가 모두 같은 공백 "  "로 되어 key가 중복됨

## 해결
Git에서 원본 파일로 복원 완료

## 다음 단계
casting 재시작 필요
`pkill -f streamlit && streamlit run src/web/streamlit_app.py`

## 참고
이모지 제거는 선택적 기능이므로 현재 상태로 사용 가능


