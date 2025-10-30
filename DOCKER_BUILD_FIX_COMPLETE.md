# Docker 빌드 수정 완료

## 문제점

`gcloud builds submit` 명령어에서 `--dockerfile` 옵션을 사용할 수 없음

## 해결 방법

Cloud Build 설정 파일(`cloudbuild.yaml`)을 사용하여 Dockerfile 지정

## 수정 내역

### 1. Cloud Build 설정 파일 생성
**파일**: `cloudbuild-admin.yaml`

```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: [
    'build',
    '-t', 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/mk-news-repo/mk-news-admin:latest',
    '-f', 'Dockerfile.admin',
    '.'
  ]
images:
- 'asia-northeast3-docker.pkg.dev/$PROJECT_ID/mk-news-repo/mk-news-admin:latest'
```

### 2. Docker 빌드 코드 수정
**파일**: `src/web/docker_build.py`

**기존 코드** (잘못된 옵션):
```python
'gcloud', 'builds', 'submit',
'--tag', image_url,
'--timeout', str(timeout),
'--dockerfile', 'Dockerfile.admin',  # ❌ 인식 안됨
'.'
```

**수정된 코드**:
```python
'gcloud', 'builds', 'submit',
'--config', 'cloudbuild-admin.yaml',  # ✅ 설정 파일 사용
'--timeout', str(timeout),
'.'
```

## gcloud builds submit 옵션

- `--config`: Cloud Build 설정 파일 경로 지정
- `--tag`: 단순 빌드 시 사용 (기본 Dockerfile 사용)
- **주의**: `--dockerfile` 옵션은 존재하지 않음

## 다음 단계

1. Streamlit UI에서 "3️⃣ Terraform Apply" 다시 클릭
2. Cloud Build 설정 파일이 사용되며 올바르게 빌드 진행
3. Docker 이미지가 Artifact Registry에 푸시됨
4. Cloud Run 배포 완료
