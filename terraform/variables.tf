# Terraform 변수 정의
variable "project_id" {
  description = "MK AI Project"
  type        = string
  default     = "godwind2015"
}

variable "region" {
  description = "GCP 리전"
  type        = string
  default     = "asia-northeast3"
}

variable "zone" {
  description = "GCP 존"
  type        = string
  default     = "asia-northeast3-a"
}

variable "environment" {
  description = "환경명"
  type        = string
  default     = "prod"
}

variable "machine_type" {
  description = "Compute Engine 머신 타입"
  type        = string
  default     = "e2-standard-4"
}

variable "database_tier" {
  description = "Cloud SQL 인스턴스 티어"
  type        = string
  default     = "db-f1-micro"
}

variable "vector_dimensions" {
  description = "벡터 임베딩 차원"
  type        = number
  default     = 768
}
