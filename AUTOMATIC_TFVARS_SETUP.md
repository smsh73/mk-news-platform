# 자동 terraform.tfvars 설정 완료

## 수정 사항

Terraform Init 단계에서 프로젝트 ID를 자동으로 받아서 `terraform.tfvars` 파일을 생성하도록 수정했습니다.

### 백엔드 API 변경사항

**`src/web/app.py`** - `terraform_init` 함수:
- 프로젝트 ID를 받아서 `terraform.tfvars` 파일을 자동 생성
- Plan과 Apply 단계에서는 생성된 tfvars 파일을 자동으로 사용

```python
@app.post("/api/terraform/init")
async def terraform_init(request: dict = None):
    """Terraform 초기화"""
    try:
        # 프로젝트 ID 받기
        project_id = request.get('project_id') if request else None
        
        # terraform.tfvars 파일 자동 생성
        if project_id:
            tfvars_content = f'''project_id = "{project_id}"
region     = "asia-northeast3"
zone       = "asia-northeast3-a"
'''
            tfvars_path = 'terraform/terraform.tfvars'
            with open(tfvars_path, 'w', encoding='utf-8') as f:
                f.write(tfvars_content)
            logger.info(f"terraform.tfvars 파일 생성 완료: project_id={project_id}")
        
        # ... rest of init logic
```

### Streamlit 앱 변경사항

**`src/web/streamlit_app.py`** - Terraform Init 버튼:
- 프로젝트 ID를 session_state에서 가져와서 API에 전달

```python
# GCP 프로젝트 ID 가져오기
project_id = repr.session_state.get('project_id', '')
if not project_id:
    st.error("먼저 GCP 프로젝트 ID를 입력하세요")
    st.stop()

response = requests.post("http://localhost:8000/api/terraform/init", 
                       json={"project_id": project_id}, timeout=180)
```

## 사용 방법

### 1단계: GCP 프로젝트 ID 입력
Streamlit 앱에서 먼저 GCP 프로젝트 ID를 입력합니다.
(이미 입력되어 있다면 그대로 사용)

### 2단계: Terraform Init 버튼 클릭
"1️⃣ Terraform Init" 버튼을 클릭하면:
- 프로젝트 ID가 자동으로 감지됨
- `terraform/terraform.tfvars` 파일이 자동 생성됨
- Terraform 초기화 진행

### 3단계: Plan과 Apply 실행
Plan과 Apply 버튼을 클릭하면:
- 생성된 tfvars 파일을 자동으로 사용
- 별도로 프로젝트 ID를 입력할 필요 없음

## 생성되는 파일

**`terraform/terraform.tfvars`**:
```hcl
project_id = "your-gcp-project-id"
region     = "asia-northeast3"
zone       = "asia-northeast3-a"
```

## 주의사항

- terraform.tfvars 파일은 Init 시에만 생성됩니다
- 프로젝트 ID를 변경하려면 Init을 다시 실행하거나 tfvars 파일을 수정하세요
- .gitignore에 tfvars 파일이 포함되어 있는지 확인하세요 (민감 정보 포함 가능)

## 백엔드 재시작 필요

코드 변경사항을 적용하려면 백엔드를 재시작해야 합니다:

```bash
pkill -f uvicorn
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate
python -m uvicorn src.web.app:app --host 0.0.0.0 --port 8000
```
