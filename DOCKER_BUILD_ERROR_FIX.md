# Docker 빌드 에러 수정

## 에러 원인

```bash
ERROR: (gcloud.builds.submit) unrecognized arguments:
  -f
```

`gcloud builds submit` 명령어에서 `-f` 옵션이 인식되지 않습니다.

## 수정 내용

### 기존 코드 (잘못된 형식)
```python
result = subprocess.run([
    'gcloud', 'builds', 'submit',
    '--tag', image_url,
    '--timeout', str(timeout),
    '-f', 'Dockerfile.admin',  # ❌ 잘못된 옵션
    '.'
])
```

### 수정된 코드
```python
result = subprocess.run([
    'gcloud', 'builds', 'submit',
    '--tag', image_url,
    '--timeout', str(timeout),
    '--dockerfile', 'Dockerfile.admin',  # ✅ 올바른 옵션
    '.'
])
```

## gcloud builds submit 옵션

- `-f` → `--dockerfile`: Dockerfile 경로 지정
- `-f`는 `docker build` 명령어에서 사용하는 옵션
- `gcloud builds submit`에서는 `--dockerfile` 옵션 사용

## 다음 단계

1. Streamlit UI에서 다시 "3️⃣ Terraform Apply" 클릭
2. Docker 이미지 빌드가 정상적으로 진행됨
3. Cloud Run 배포 완료
