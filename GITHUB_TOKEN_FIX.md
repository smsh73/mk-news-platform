# GitHub Personal Access Token 권한 수정

## 현재 문제
Personal Access Token에 `workflow` 권한이 없어서 `.github/workflows/` 파일을 푸시할 수 없습니다.

## 해결 방법

### 방법 1: 기존 토큰에 권한 추가 (불가능)
GitHub Personal Access Token은 생성 후 권한을 변경할 수 없습니다. 새 토큰을 생성해야 합니다.

### 방법 2: 새 Personal Access Token 생성 (권장)

1. **GitHub에서 토큰 생성**:
   - https://github.com/settings/tokens/new 접속
   - Note: "mk-news-platform CI/CD with workflow"
   - Expiration: "No expiration" 또는 적절한 기간 선택
   - **Scopes**: 다음 권한들을 체크하세요:
     - ✅ `repo` (전체 저장소 접근)
     - ✅ `workflow` (GitHub Actions 워크플로 업데이트) **← 필수!**
   - "Generate token" 클릭
   - **새 토큰을 복사하여 안전한 곳에 저장**

2. **로컬 Git 원격 URL 업데이트**:
   ```bash
   # 새 토큰으로 원격 URL 업데이트
   git remote set-url origin https://NEW_TOKEN@github.com/smsh73/mk-news-platform.git
   
   # NEW_TOKEN을 실제 새 토큰으로 변경하세요
   ```

3. **다시 푸시**:
   ```bash
   git push origin main
   ```

## 즉시 해결 명령어

새 토큰을 받으시면 아래 명령어를 실행하세요:

```bash
# 1. 원격 URL 업데이트 (NEW_TOKEN을 실제 토큰으로 변경)
git remote set-url origin https://NEW_TOKEN@github.com/smsh73/mk-news-platform.git

# 2. 푸시
git push origin main
```

## 보안 참고사항

- 새 토큰 생성 후 기존 토큰은 삭제하거나 더 이상 사용하지 마세요
- 토큰을 공개 저장소나 코드에 커밋하지 마세요
- 토큰은 `.gitignore`에 명시되어 있지만, 확인하세요

**새 토큰을 생성하셨으면 토큰 값을 알려주세요. 제가 자동으로 설정해드리겠습니다.**
