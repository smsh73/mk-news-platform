# Cloud Run IAM 자동 설정 가이드

## 구현 완료

### 1. 자동 IAM 설정
- Terraform Apply 완료 후 자동으로 IAM 정책 설정 시도
- 현재 활성 계정 확인 및 로그 출력
- 실패 시 수동 설정 안내

### 2. 수동 IAM 설정 UI
**위치**: Streamlit 대시보드 → GCP 인프라 탭 → Cloud Run IAM 설정

#### 제공 기능:

##### 공개 접근 설정
- 버튼 클릭으로 전체 공개 설정
- 실행 로그 자동 표시

##### 특정 계정 권한 부여
- 이메일 주소 입력
- 특정 사용자에게 권한 부여
- 실행 로그 자동 표시

##### 현재 IAM 정책 확인
- 현재 설정된 권한 조회
- JSON 형식으로 상세 정보 표시
- 역할별 구성원 목록 표시

## 사용 방법

### 방법 1: 자동 설정 (Terraform Apply 후)
1. Terraform 배포 진행
2. Apply 완료 후 자동으로 IAM 설정 시도
3. 로그 확인 후 실패 시 수동 설정

### 방법 2: 수동 설정 (공개 접근)
1. GCP 인프라 탭 선택
2. "Cloud Run IAM 설정" 섹션으로 이동
3. "전체 공개 설정" 버튼 클릭
4. 로그 확인

### 방법 3: 특정 계정 권한 부여
1. GCP 인프라 탭 선택
2. "Cloud Run IAM 설정" 섹션으로 이동
3. "특정 계정 권한 부여" 섹션에서 이메일 입력
4. "권한 부여" 버튼 클릭
5. 로그 확인

### 방법 4: 다른 계정으로 설정
1. 터미널에서 다른 계정으로 로그인:
   ```bash
   gcloud auth login another@example.com
   ```
2. Streamlit 페이지 새로고침 (인증 상태 자동 업데이트)
3. "전체 공개 설정" 또는 "특정 계정 권한 부여" 버튼 클릭

## 권한 오류 해결

### 현재 오류
```
PERMISSION_DENIED: Permission 'run.services.setIamPolicy' denied
```

### 해결 방법

#### 1. Owner 또는 Editor Epic
프로젝트 IAM 설정에서 다음 역할 중 하나를 가진 계정 사용:
- **Owner** (`roles/owner`)
- **Editor** (`roles/editor`)
- **Cloud Run Admin** (`roles/run.admin`)

#### 2. 필요한 최소 권한
다음 중 하나의 IAM 역할:
```bash
# Owner
roles/owner

# Editor
roles/editor

# Cloud Run Admin (최소 권한)
roles/run.admin
```

#### 3. 권한 부여 방법
1. GCP Console 접속: https://console.cloud.google.com/iam-admin/iam?project=mk-ai-project-473000
2. "주 구성원 추가" 클릭
3. 이메일 주소 입력
4. 역할 선택: `Owner` 또는 `Editor`
5. "저장" 클릭

#### 4. 다른 계정으로 설정
```bash
# 계정 로그인
gcloud auth login another@example.com

# 프로젝트 설정
gcloud config set project mk-ai-project-473000

# 권한 확인
gcloud projects get-iam-policy mk-ai-project-473000 \
  --flatten="bindings[].members" \
  --filter="bindings.members:another@example.com" \
  --format="table(bindings.role)"
```

## UI 구성

### Cloud Run IAM 설정 섹션
```
┌─────────────────────────────────────────────────────────┐
│ 🔒 Cloud Run IAM 설정                                   │
│                                                         │
│ ┌───────────────────┐  ┌─────────────────────────┐   │
│ │ 공개 접근 설정    │  │ 특정 계정 권한 부여     │   │
│ │ [전체 공개 설정]  │  │ 이메일: [          ]    │   │
│ │                   │  │        [권한 부여]      │   │
│ └───────────────────┘  └─────────────────────────┘   │
│                                                         │
│          [현재 IAM 정책 확인]                           │
│                                                         │
│ ┌─ IAM 정책 상세 ─────────────────────────────────────┐│
│ │                                                     ││
│ │ - JSON 형식의 상세 정책                             ││
│ │ - 역할별 Reheving원 목록                             ││
│ │                                                     ││
│ └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## 로그 표시

모든 IAM 설정 작업은 다음과 같은 로그를 표시합니다:

1. **실행 명령어**: gcloud 명령어 전체
2. **Return Code**: 실행 결과 코드
3. **Output**: 성공 시 출력 내용
4. **Error**: 실패 시 오류 메시지

### 로그 예시

#### 성공 시:
```
현재 활성 계정: admin@example.com
Return code: 0
Output:
Updated IAM policy for service [mk-news-admin].
bindings:
- members:
  - allUsers
  role: roles/run.invoker
etag: BwWV...
version: 1
```

#### 실패 시:
```
현재 활성 계정: user@example.com
Return code: 1
Error:
ERROR: (gcloud.run.services.add-iam-policy-binding) PERMISSION_DENIED
```

## 주의사항

1. **보안**: `allUsers` 권한은 인터넷상 누구나 접근 가능
2. **권한**: IAM 정책 설정은 Owner/Editor 권한 필요
3. **계정**: 여러 계정이 등록된 경우 활성 계정 확인 필요
4. **로그**: 모든 작업 로그는 expander로 표시됨

## 명령어 참고

### 수동 실행 (터미널)
```bash
# 공개 접(U는 설정
gcloud run services add-iam-policy-binding mk-news-admin \
  --region=asia-northeast3 \
  --member=allUsers \
  --role=roles/run.invoker

# 특정 계정 권한 부여
gcloud run services add-iam-policy-binding mk-news-admin \
  --region=asia-northeast3 \
  --member=user:user@example.com \
  --role=roles/run.invoker

# 현재 IAM 정책 확인
gcloud run services get-iam-policy mk-news-admin \
  --region=asia-northeast3 \
  --format=json

# 다른 계정으로 로그인
gcloud auth login admin@example.com
```

## 자주 묻는 질문

### Q1: 자동 설정이 실패하면?
A: 하단의 "Cloud Run IAM 설정" 섹션에서 수동으로 설정하거나 Owner 권한을 가진 다른 계정으로 설정하세요.

### Q2: 다른 계정으로 설정하려면?
A: 터미널에서 `gcloud auth login` 명령어로 다른 계정으로 로그인 후 Streamlit 페이지를 새로고침하세요.

### Q3: 로그는 어디서 확인?
A: 각 버튼 실행 후 나타나는 expander에서 "IAM 설정 로그" 또는 "IAM 정책 상세"를 클릭하세요.

### Q4: 권한 오류는 어떻게 해결?
A: 프로젝트 Owner 권한을 가진 계정으로 로그인하거나, GCP Console에서 직접 권한을 부여받으세요.

