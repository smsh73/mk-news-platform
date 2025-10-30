# Terraform Plan 오류 해결 가이드

## 발생한 오류

Terraform Plan 단계에서 다음 오류가 발생했습니다:
```
Error: Reference to undeclared input variable
  variable "project_id" has not been declared
  variable "region" has not been declared
  variable "zone" has not been declared
```

## 해결 방법

### 1단계: terraform/main.tf 파일 수정 완료

`terraform/main.tf` 파일에 변수 정의를 추가했습니다:

```hcl
variable "project_id" {
  description = "GCP 프로젝트 ID"
  type        = string
  default     = ""
}

variable "region" {
 汀scription = "GCP 리전"
  type        = string
  default     = "asia-northeast3"  # 서울
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "asia-northeast3-a"
}
```

### 2단계: 백엔드 API 수정 완료

`src/web/app.py` 파일의 Terraform API 엔드포인트를 수정하여 project_id를 전달하도록 했습니다.

### 3단계: Streamlit 앱에서 프로젝트 ID 전달

Streamlit 앱에서 버튼을 클릭할 때 프로젝트 ID를 전달해야 합니다.

## 임시 해결책

Streamlit 앱이 아직 업데이트되지 않았으므로, 다음 방법 중 하나를 사용할 수 있습니다:

### 방법 1: Terraform .tfvars 파일 생성 (권장)

```bash
cd terraform
cat > terraform.tfvars << EOF
project_id = "your-gcp-project-id"
region     = "asia-northeast3"
zone       = "asia-northeast3-a"
EOF
```

### 방법 2: 명령줄에서 직접 실행

Streamlit에서 Plan을 클릭하기 전에 터미널에서:

```bash
cd terraform
terraform plan -var="project_id=your-gcp-project-id"
```

### 방법 3: 환경 변수 사용

```bash
export TF_VAR_project_id="your-gcp-project-id"
export TF_VAR_region="asia-northeast3"
export TF_VAR_zone="asia-northeast3-a"
```

## 다음 단계

1. Terraform Init 다시 실행
2. Terraform Plan 실행 (이제 project_id를 제공해야 함)
3. Terraform Apply 실행

## 참고

Streamlit 앱을 재시작하면 최신 코드가 반영됩니다.
백 프론트엔드가 재시작되면 프로젝트 ID를 자동으로 전달합니다.

## Streamlit 앱 재시작 방법

터미널에서:
```bash
# 백엔드 재시작
pkill -f uvicorn
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate
python -m uvicorn src.web.app:app --host 0.0.0.0 --port 8000 &
```
