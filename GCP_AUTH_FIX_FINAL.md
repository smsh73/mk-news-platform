# GCP 인증 상태 확인 수정

## 문제
인증을 완료했는데도 "인증되지 않음"으로 표시됨

## 원인
`default()` 함수는 Application Default Credentials (ADC)를 확인하는데, `gcloud auth login`은 사용자 자격 증명만 설정하고 ADC는 설정하지 않음

## 해결
`gcloud auth list` 명령으로 실제 인증된 계정을 확인하도록 변경:

### 수정 전
```python
credentials, project = default(scopes=SCOPES)
if credentials and credentials.valid:
    return True, project
```

### 수정 후
```python
# gcloud auth list로 인증된 계정 확인
result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=json'], ...)
accounts = json.loads(result.stdout)
if accounts and len(accounts) > 0:
    # 활성 계정이 있으면 프로젝트 ID 가져오기
    project_id = subprocess.run(['gcloud', 'config', 'get-value', 'project'], ...)
    return True, project_id
```

## 적용 완료
- ✅ 파일 수정 완료
- ✅ 문법 검증 성공
- ✅ Streamlit 자동 리로드

## 사용 방법
1. "🔑 gcloud 로그인" 버튼으로 인증
2. 인증 완료 후 "🔄 인증 상태 새로고침" 버튼 클릭
3. 인증 상태가 "✅ 인증됨"으로 표시됨

이제 `gcloud auth login`만으로도 인증 상태가 정상적으로 표시됩니다.


