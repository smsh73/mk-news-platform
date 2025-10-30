# IAM 수동 설정 가이드

## 현재 상태

✅ **Terraform Apply 완료!**
- Cloud Run 서비스가 성공적으로 배포되었습니다
- IAM 정책 설정만 권한 문제로 실패

## IAM 설정 방법

### 방법 1: GCP 콘솔에서 설정 (가장 쉬움)

1. **Cloud Run 콘솔 접속**
   - https://console.cloud.google.com/run?project=mk-ai-project-473000

2. **서비스 선택**
   - `mk-崑ews-admin` 서비스 클릭

3. **권한 설정**
   - "권한" 탭 선택
   - "주 구성원 추가" 버튼 클릭
   - 새 구성원: `allUsers`
   - 역할: `Cloud Run 호출자`
   - 저장

### 방법 2: 명령어로 설정

```bash
# 프로젝트 소유자 권한이 필요
gcloud run services add-iam-policy-binding mk-news-admin \
  --region=asia-northeast3 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=mk-ai-project-473000
```

### 방법 3: 프로젝트 소유자에게 요청

현재 계정 `godwind2015@gmail.com`이 프로젝트 소유자가 아닌 경우:

1. 프로젝트 소유자에게 요청
2. IAM 관리자 역할 부여 또는
3. 소유자가 직접 위 명령어 실행

## 배포 완료 확인

Cloud Run 서비스는 이미 생성되었습니다:

```bash
# 서비스 확인
gcloud run services list --region=asia-northeast3

# URL 확인
gcloud run services describe mk-news-admin --region=asia-northeast3 --format="value(status.url)"
```

## IAM 설정 후 접속

IAM 설정이 완료되면 다음과 같이 접속:

```
https://mk-news-admin-XXX.asia-northeast3.run.app
```

## 현재 계정 권한

계정: `godwind2015@gmail.com`
권한: `run.services.setIamPolicy` 없음

필요한 역할:
- Cloud Run Admin 또는
- Security Admin

## 다음 단계

1. **GCP 콘솔에서 IAM 설정** (권장)
2. URL 확인
3. 대시보드 접속 테스트


