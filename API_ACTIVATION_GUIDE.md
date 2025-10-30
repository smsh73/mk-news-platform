# Cloud Source Repositories API 활성화 가이드

## 현재 상황
CLI에서 API 활성화 권한이 제한되어 있어 브라우저에서 직접 활성화해야 합니다.

## 활성화 방법

### 방법 1: 직접 링크 (가장 빠름)
아래 링크를 클릭하여 바로 활성화하세요:

**🔗 [Cloud Source Repositories API 활성화](https://console.developers.google.com/apis/api/sourcerepo.googleapis.com/overview?project=mk-ai-project-473000)**

### 방법 2: GCP 콘솔에서 수동 활성화
1. **GCP 콘솔 접속**: https://console.cloud.google.com
2. **프로젝트 선택**: `mk-ai-project-473000` 선택
3. **API 및 서비스 메뉴**: 왼쪽 메뉴에서 "API 및 서비스" > "라이브러리" 클릭
4. **API 검색**: "Cloud Source Repositories" 검색
5. **API 활성화**: "사용 설정" 버튼 클릭

## 활성화 확인
활성화 후 아래 명령어로 확인할 수 있습니다:

```bash
gcloud services list --enabled --project=mk-ai-project-473000 | grep sourcerepo
```

## 다음 단계
API 활성화가 완료되면 자동으로 다음 단계를 진행합니다:
1. Cloud Source Repository 생성
2. Git 원격 저장소 설정
3. 코드 푸시
4. Cloud Build 트리거 설정

## 예상 소요 시간
- API 활성화: 1-2분
- 설정 완료: 5-10분

**활성화가 완료되면 "완료"라고 알려주세요.**
