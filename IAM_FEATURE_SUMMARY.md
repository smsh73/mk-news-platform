# Cloud Run IAM 설정 기능 구현 완료

## 구현 일시
2025-10-28 13:54

## 구현 항목

### 1. 자동 IAM 설정 (Terraform Apply 후)
- **위치**: Terraform 배포 완료 후 자동 실행
- **기능**:
  - 현재 활성 계정 자동 확인
  - Cloud Run 서비스에 공개 접근 권한 자동 설정
  - 상세 로그 출력 (활성 계정, Return Code, Output, Error)
  - 실패 시 수동 설정 안내

### 2. 수동 IAM 설정 UI
**위치**: Streamlit → GCP 인프라 탭 → Cloud Run IAM 설정

#### 기능 세부사항:

##### A. 전체 공개 설정
- 버튼: "전체 공개 설정"
- 기능: 모든 사용자에게 Cloud Run 접근 권한 부여
- 결과: 로그 자동 표시 Icon 접근 Tk

##### B. 특정 계정 권한 부여
- 입력: 이메일 주소
- 버튼: "권한 부여"
- 기능: 특정 이메일 계정에 접근 권한 부여
- 검증: 이메일 형식 검증
- 결과: 로그 자동 표시

##### C. 현재 IAM 정책 확인
- 버튼: "현재 IAM 정책 확인"
- 기능: 
  - JSON 형식의 상세 정책 조회
  - 역할별 구성원 목록 표시
  - 사용자 친화적 UI로 정보 제공

### 3. 로그 시스템
모든 IAM 작업에 대해:
- **실행 명령어**: gcloud 전체 명령어
- **Return Code**: 성공(0)/실패(1)
- **Output**: 표준 출력 내용
- **Error**: 오류 메시지
- **형식**: Expander로 접기/펼치기 가능

## 화면 구성

```
┌────────────────────────────────────────────────────────┐
│ GCP 인프라                                             │
├────────────────────────────────────────────────────────┤
│                                                        │
│ 🔒 Cloud Run IAM 설정                                 │
│                                                        │
│ ┌──────────────────┐  ┌─────────────────────────┐    │
│ │ 공개 접근 설정   │  │ 특정 계정 권한 부여    │    │
│ │                  │  │ 이메일: [____@____]    │    │
│ │ [전체 공개 설정] │  │ [권한 부여]           │    │
│ │                  │  │                       │    │
│ └──────────────────┘  └─────────────────────────┘    │
│                                                        │
│        [현재 IAM 정책 확인]                           │
│                                                        │
│ ┌─ IAM 자동 설정 로그 ────────────────────────────┐ │
│ │ ▼ 현재 활성 계정: user@example.com              │ │
│ │ Return code: 0                                   │ │
│ │ Output:                                          │ │
│ │ Updated IAM policy for service [mk-news-admin]   │ │
│ └──────────────────────────────────────────────────┘ │
│                                                        │
│ 🎉 현재 IAM 설정 완료:                               │
│ - allUsers: Cloud Run 호출자 권한                    │
│ - admin@example.com: Cloud Run 호출자 권한           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## 사용 시나리오

### 시나리오 1: Terraform 배포 후 자동 설정
1. Terraform Apply 실행
2. 배포 완료 후 자동으로 IAM 정책 설정 시도
3. 성공 시: "공개 접근 허용 자동 설정 완료" 메시지
4. 실패 시: "수동 설정 안내" 메시지

### 시나리오 2: 다른 계정으로 수동 설정
1. 터미널에서 관리자 계정 로그인
   ```bash
   gcloud auth login admin@example.com
   ```
2. Streamlit 페이지 새로고침
3. "전체 공개 설정" 버튼 클릭
4. 로그 확인

### 시나리오 3: 특정 사용자 권한 부여
1. "특정 계정 권한 부여" 섹션으로 이동
2. 이메일 입력 (예: user@example.com)
3. "권한 부여" 버튼 클릭
4. 성공 메시지 확인

### 시나리오 4: 현재 설정 확인
1. "현재 IAM 정책 확인" 버튼 클릭
2. JSON 형식의 정책 내용 확인
3. 역할별 구성원 목록 확인

## 개선 사항

### 기존 문제
- ❌ 수동 설정만 가능
- ❌ 다른 계정 설정 시 터미널 사용 필요
- ❌ 로그 확인 불편

### 개선 결과
- ✅ Terraform 배포 후 자동 설정 시도
- ✅ UI에서 이메일 입력 후 다른 계정으로 설정 가능
- ✅ 모든 작업 로그 자동 표시
- ✅ 현재 정책 상태 확인 기능 추가
- ✅ 사용자 친화적 UI 제공

## 기술 구현

### gcloud 명령어
```bash
# 공개 접근 설정
gcloud run services add-iam-policy-binding mk-news-admin \
  --region=asia-northeast3 \
  --member=allUsers \
  --role=roles/run.invoker

# 특정 계정 권한 부여
gcloud run services add-iam-policy-binding mk-news-admin \
  --region=asia-northeast3 \
  --member=user:email@example.com \
  --role=roles/run.invoker

# 현재 IAM 정책 확인
gcloud run services get-ras-policy mk-news-admin \
  --region=asia-northeast3 \
  --format=json
```

### Python subprocess
```python
result = subprocess.run([
    'gcloud', 'run', 'services', 'add-iam-policy-binding', 'mk-news-admin',
    '--region=asia-northeast3',
    '--member=allUsers',
    '--role=roles/run.invoker'
], capture_output=True, text=True, timeout=60)
```

## 실행 상태

✅ Streamlit 정상 실행
- URL: http://localhost:8501
- 로그 파일: /tmp/streamlit_iam.log

## 접근 방법

1. 브라우저에서 http://localhost:8501 접속
2. "GCP 인프라" 탭 선택
3. "Cloud Run IAM 설정" 섹션으로 스크롤
4. 원하는 기능 사용

## 파일 목록

- `src/web/streamlit_app.py` - IAM 설정 UI 구현
- `IAM_SETUP_GUIDE.md` - 사용 가이드
- `IAM_FEATURE_SUMMARY.md` - 이 파일 (기능 요약)

## 다음 단계

1. GCP Console에서 Owner 권한이 있는 계정 확인
2. 해당 계정으로 로그인: `gcloud auth login admin@example.com`
3. Streamlit에서 "전체 공개 설정" 버튼 클릭
4. IAM 정책 확인: "현재 IAM 정책 확인" 버튼 클릭

