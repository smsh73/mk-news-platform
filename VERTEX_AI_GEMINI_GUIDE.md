# Vertex AI를 통한 Gemini 사용 가이드

## 개요

현재 프로젝트는 GCP Vertex AI를 통해 Gemini 모델을 사용할 수 있도록 구현되어 있습니다. 이것은 별도의 Gemini API 키 없이 GCP 프로젝트 인증만으로 사용 가능합니다.

## 구현 내용

### Vertex AI Gemini 통합

**파일**: `src/rag/gemini_client.py`

#### 초기화 순서:

1. **1순위: Vertex AI Gemini** (권장)
   - GCP 프로젝트 인증 사용
   - 별도 API 키 불필요
   - 비용은 GCP 프로젝트에 청구

2. **2순위: 직접 API 키**
   - `GEMINI_API_KEY` 환경변수
   - Google AI Studio에서 발급

### 코드 구현

```python
def _initialize_client(self):
    # 1순위: Vertex AI를 통한 Gemini 사용
    try:
        from vertexai.preview.generative_models import GenerativeModel
        from google.cloud import aiplatform
        
        # Vertex AI 초기화
        project_id = os.getenv('GCP_PROJECT_ID', 'mk-ai-project-473000')
        region = os.getenv('GCP_REGION', 'asia-northeast3')
        
        aiplatform.init(project=project_id, location=region)
        
        # Vertex AI를 통한 Gemini 모델 사용
        model_name = 'gemini-1.5-pro'
        self.model = GenerativeModel(model_name)
        
        self.use_vertex_ai = True
        logger.info("Vertex AI Gemini 모델 초기화 완료")
        return
        
    except Exception as e:
        logger.debug(f"Vertex AI 초기화 실패: {e}, API 키 방식 시도")
        # API 키 방식 fallback
```

## 사용 방법

### 방법 1: Vertex AI 사용 (권장)

#### 필요 조건:
- GCP 프로젝트 설정
- Application Default Credentials (ADC)
- Vertex AI API 활성화

#### 설정:
```bash
# GCP 인증
gcloud auth application-default login

# 프로젝트 설정
export GCP_PROJECT_ID=mk-ai-project-473000
export GCP_REGION=asia-northeast3

# Vertex AI API 활성화
gcloud services enable aiplatform.googleapis.com
```

#### 장점:
- API 키 불필요
- GCP 관리형 서비스와 통합
- 자동 인증 관리
- 프로젝트별 쿼터 및 제한 관리

### 방법 2: 직접 API 키 사용

#### 필요 조건:
- Google AI Studio API 키

#### 설정:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

#### 장점:
- 간단한 설정
- Google AI Studio에서 직접 관리

## 모델 정보

### 사용 가능한 모델:

#### Vertex AI:
- `gemini-1.5-pro` (기본값)
- `gemini-1.5-flash`
- `gemini-pro`

#### 직접 API:
- `gemini-1.5-pro` (기본값)
- `gemini-1.5-flash`

### 모델 변경:

환경변수로 모델 지정:
```bash
export GEMINI_MODEL=gemini-1.5-flash
```

## 비용

### Vertex AI:
- GCP 프로젝트에 청구
- 프로젝트별 쿼터 및 제한
- 사용량 기반 과금

### 직접 API:
- 무료 쿼터: 월 15 RPM
- 유료 플랜: 사용량 기반

## 테스트

### Vertex AI Gemini 테스트:
```bash
cd "/Users/seungminlee/Downloads/기사 XML 2/saltlux_xml"
source venv/bin/activate

python -c "
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import aiplatform

aiplatform.init(project='mk-ai-project-473000', location='asia-northeast3')
model = GenerativeModel('gemini-1.5-pro')
response = model.generate_content('안녕하세요')
print(response.text)
"
```

## 자동 Fallback

현재 구현은 다음과 같이 자동 Fallback됩니다:

1. Vertex AI 시도
   - 성공: Vertex AI Gemini 사용
   - 실패: 다음으로 진행

2. 직접 API 키 시도
   - 키 있음: 직접 API 사용
   - 키 없음: Fallback 응답

3. Fallback 응답
   - 간단한 템플릿 기반 응답
   - 검색된 기사 정보만 제공

## 현재 상태 확인

```bash
# Vertex AI 사용 가능 여부
gcloud auth application-default print-access-token

# Vertex AI API 활성화 여부
gcloud services list --enabled | grep aiplatform

# 프로젝트 설정
gcloud config get-value project
```

## 참고

- Vertex AI 사용 시 `aiplatform.init()`만 호출하면 GCP 인증이 자동으로 처리됩니다
- Application Default Credentials (ADC)를 사용하므로 별도 인증 파일 불필요
- 현재 로그인한 gcloud 계정의 권한을 사용합니다


