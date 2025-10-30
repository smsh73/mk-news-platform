# Terraform Plan 오류 수정

## 오류 내용

```
Error: Reference to undeclared input variable

on main.tf line 299, in resource "google_vertex_ai_index" "mk_news_vector_index":
299:     environment = var.environment

An input variable with the name "environment" has not been declared.
```

## 원인

`var.environment` 변수를 사용하고 있었지만 변수 선언이 없었습니다.

## 수정 내용

### 1. `environment` 변수 추가 (terraform/main.tf line 33-37)

```terraform
variable "environment" {
  description = "환경 이름"
  type        = string
  default     = "production"
}
```

### 2. Secret Manager replication 설정 수정 (line 330-335)

**이전**:
```terraform
replication {
  automatic = true
}
```

**수정 후**:
```terraform
replication {
  user_managed {
    replicas {
      location = var.region
    }
  }
}
```

## 사용 위치

`environment` 변수는 다음 리소스의 라벨로 사용됩니다:

1. **Vertex AI Index** (line 299)
2. **Secret Manager Secret** (line 339)

## 다음 단계

이제 Streamlit에서 "2️⃣ Terraform Plan" 버튼을 다시 클릭하면 정상 작동할 것입니다.
