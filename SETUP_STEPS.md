# CI/CD 설정 진행 단계

## 1단계: Cloud Source Repositories API 활성화 (수동)

현재 API 활성화 권한이 CLI에서는 제한되어 있습니다. 브라우저에서 직접 활성화해주세요:

**방법 1: 직접 링크**
https://console.developers.google.com/apis/api/sourcerepo.googleapis.com/overview?project=mk-ai-project-473000

**방법 2: GCP 콘솔에서**
1. https://console.cloud.google.com 접속
2. 프로젝트: mk-ai-project-473000 선택
3. "API 및 서비스" > "라이브덱릭리" 메뉴
4. "Cloud Source Repositories API" 검색 후 활성화

활성화 후 2-3분 기다린 다음 다음 단계 진행하세요.

## 2단계: Git 저장소 초기화 (진행 중)

아래 명령어들을 순서대로 실행하세요.
