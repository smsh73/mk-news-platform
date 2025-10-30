# GitHub 인증 설정 가이드

## 현재 상황
GitHub 푸시 시 권한 오류가 발생했습니다. 인증 설정이 필요합니다.

## 해결 방법

### 방법 1: Personal Access Token 사용 (권장)

1. **GitHub에서 Personal Access Token 생성**:
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - "Generate new token (classic)" 클릭
   - Note: "mk-news-platform CI/CD"
   - Expiration: "No expiration" 또는 적절한 기간 선택
   - Scopes: `repo` (전체 저장소 접근) 체크
   - "Generate token" 클릭
   - **토큰을 복사하여 안전한 곳에 저장**

2. **Git 인증 설정**:
   ```bash
   # Personal Access Token으로 인증
   git config --global credential.helper store
   
   # 푸시 시도 (사용자명: smsh73, 비밀번호: Personal Access Token)
   git push -u origin main
   ```

### 방법 2: SSH 키 사용

1. **SSH 키 생성** (이미 있다면 스킵):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Enter를 눌러 기본 경로 사용
   # 비밀번호 설정 (선택사항)
   ```

2. **SSH 키를 GitHub에 추가**:
   ```bash
   # 공개 키 복사
   cat ~/.ssh/id_ed25519.pub
   ```
   - GitHub → Settings → SSH and GPG keys → New SSH key
   - 복사한 공개 키 붙여넣기

3. **원격 저장소 URL을 SSH로 변경**:
   ```bash
   git remote set-url origin git@github.com:smsh73/mk-news-platform.git
   git push -u origin main
   ```

## 추천 방법

**Personal Access Token 방법을 추천**합니다. 이유:
- 설정이 간단함
- HTTPS를 사용하여 방화벽 문제 없음
- 토큰으로 세밀한 권한 제어 가능

## 다음 단계

인증 설정 후:
1. 코드 푸시 완료
2. OIDC 인증 설정
3. GitHub Secrets 설정
4. CI/CD 테스트

어떤 방법을 선택하시겠습니까?
