# GCP 인프라 구성 - 매일경제 신문기사 벡터임베딩 플랫폼
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# 변수 정의
variable "project_id" {
  description = "MK AI Project"
  type        = string
  default     = "mk-ai-project-473000"
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

# VPC 네트워크 구성
resource "google_compute_network" "mk_news_vpc" {
  name                    = "mk-news-vpc"
  auto_create_subnetworks = false
  description             = "매일경제 신문기사 벡터임베딩 플랫폼 VPC"
}

resource "google_compute_subnetwork" "mk_news_subnet" {
  name          = "mk-news-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.mk_news_vpc.id
  description   = "매일경제 신문기사 플랫폼 서브넷"
}

# 방화벽 규칙
resource "google_compute_firewall" "mk_news_firewall" {
  name    = "mk-news-firewall"
  network = google_compute_network.mk_news_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "8080", "8000"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["mk-news-server"]
}

# Vertex AI 서비스 활성화
resource "google_project_service" "vertex_ai" {
  service = "aiplatform.googleapis.com"
}

resource "google_project_service" "vertex_ai_vector_search" {
  service = "aiplatform.googleapis.com"
}

resource "google_project_service" "compute_engine" {
  service = "compute.googleapis.com"
}

resource "google_project_service" "cloud_sql" {
  service = "sqladmin.googleapis.com"
}

resource "google_project_service" "cloud_storage" {
  service = "storage.googleapis.com"
}

resource "google_project_service" "cloud_run" {
  service = "run.googleapis.com"
}

resource "google_project_service" "vpc_access" {
  service = "vpcaccess.googleapis.com"
}

resource "google_project_service" "servicenetworking" {
  service = "servicenetworking.googleapis.com"
}

resource "google_project_service" "container_registry" {
  service = "containerregistry.googleapis.com"
}

resource "google_project_service" "artifact_registry" {
  service = "artifactregistry.googleapis.com"
}

# Cloud SQL 인스턴스 (메타데이터 저장용) - Private IP
resource "google_sql_database_instance" "mk_news_db" {
  name             = "mk-news-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-standard-2"
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.mk_news_vpc.id
      require_ssl     = true
    }
    
    database_flags {
      name  = "log_statement"
      value = "all"
    }
    
    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"
    }
  }

  deletion_protection = false
  depends_on = [google_service_networking_connection.mk_news_private_connection]
}

# Cloud SQL 데이터베이스
resource "google_sql_database" "mk_news_database" {
  name     = "mk_news"
  instance = google_sql_database_instance.mk_news_db.name
}

# Cloud Storage 버킷 (XML 파일 및 임베딩 저장용)
resource "google_storage_bucket" "mk_news_storage" {
  name          = "mk-news-storage-godwind2015"
  location      = "ASIA-NORTHEAST3"
  force_destroy = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Vertex AI Vector Search 인덱스
resource "google_vertex_ai_index" "mk_news_vector_index" {
  display_name = "mk-news-vector-index"
  description  = "매일경제 신문기사 벡터 임베딩 인덱스"
  region       = var.region

    metadata {
      contents_delta_uri = "gs://mk-news-storage-godwind2015/embeddings"
    config {
      dimensions                  = 768
      approximate_neighbors_count = 150
      distance_measure_type       = "DOT_PRODUCT_DISTANCE"
      algorithm_config {
        tree_ah_config {
          leaf_node_embedding_count    = 500
          leaf_nodes_to_search_percent  = 7
        }
      }
    }
  }

  index_update_method = "BATCH_UPDATE"
}

# Vertex AI Vector Search 엔드포인트
resource "google_vertex_ai_index_endpoint" "mk_news_vector_endpoint" {
  display_name = "mk-news-vector-endpoint"
  description  = "매일경제 신문기사 벡터 검색 엔드포인트"
  region       = var.region
}

# Vertex AI Vector Search 인덱스 배포
resource "google_vertex_ai_index_endpoint_deployed_index" "mk_news_deployed_index" {
  index_endpoint = google_vertex_ai_index_endpoint.mk_news_vector_endpoint.id
  deployed_index_id = "mk_news_deployed_index"
  index = google_vertex_ai_index.mk_news_vector_index.id
  display_name = "매일경제 신문기사 벡터 검색"
  description = "매일경제 신문기사 벡터 검색 배포"
}

# Cloud Run 서비스 (FastAPI 애플리케이션)
resource "google_cloud_run_v2_service" "mk_news_api" {
  name     = "mk-news-api"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/mk-news-api:latest"
      
      ports {
        container_port = 8000
      }
      
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "DB_HOST"
        value = google_sql_database_instance.mk_news_db.private_ip_address
      }
      
      env {
        name  = "DB_NAME"
        value = google_sql_database.mk_news_database.name
      }
      
      env {
        name  = "STORAGE_BUCKET"
        value = google_storage_bucket.mk_news_storage.name
      }
      
      env {
        name  = "VECTOR_INDEX_ID"
        value = google_vertex_ai_index.mk_news_vector_index.id
      }
      
      env {
        name  = "VECTOR_ENDPOINT_ID"
        value = google_vertex_ai_index_endpoint.mk_news_vector_endpoint.id
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }
    }
    
    service_account = google_service_account.mk_news_sa.email
    
    vpc_access {
      connector = google_vpc_access_connector.mk_news_connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Cloud Run 서비스 (Streamlit 관리자 대시보드)
resource "google_cloud_run_v2_service" "mk_news_admin" {
  name     = "mk-news-admin"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/mk-news-admin:latest"
      
      ports {
        container_port = 8501
      }
      
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "API_URL"
        value = google_cloud_run_v2_service.mk_news_api.uri
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
      }
    }
    
    service_account = google_service_account.mk_news_sa.email
    
    vpc_access {
      connector = google_vpc_access_connector.mk_news_connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Private Service Connection (Cloud SQL용)
resource "google_compute_global_address" "mk_news_private_ip" {
  name          = "mk-news-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.mk_news_vpc.id
}

resource "google_service_networking_connection" "mk_news_private_connection" {
  network                 = google_compute_network.mk_news_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.mk_news_private_ip.name]
}

# VPC Access Connector (Private 서비스 연결용)
resource "google_vpc_access_connector" "mk_news_connector" {
  name          = "mk-news-connector"
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.mk_news_vpc.name
  region        = var.region
}

# Artifact Registry (컨테이너 이미지 저장소)
resource "google_artifact_registry_repository" "mk_news_repo" {
  location      = var.region
  repository_id = "mk-news-repo"
  description   = "매일경제 신문기사 플랫폼 컨테이너 이미지 저장소"
  format        = "DOCKER"
}

# Cloud Run IAM (API 서비스)
resource "google_cloud_run_service_iam_member" "mk_news_api_public" {
  location = google_cloud_run_v2_service.mk_news_api.location
  service  = google_cloud_run_v2_service.mk_news_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Run IAM (관리자 대시보드)
resource "google_cloud_run_service_iam_member" "mk_news_admin_public" {
  location = google_cloud_run_v2_service.mk_news_admin.location
  service  = google_cloud_run_v2_service.mk_news_admin.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 서비스 계정
resource "google_service_account" "mk_news_sa" {
  account_id   = "mk-news-sa"
  display_name = "매일경제 신문기사 플랫폼 서비스 계정"
  description  = "매일경제 신문기사 벡터임베딩 플랫폼용 서비스 계정"
}

# 서비스 계정 권한
resource "google_project_iam_member" "mk_news_sa_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.mk_news_sa.email}"
}

resource "google_project_iam_member" "mk_news_sa_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.mk_news_sa.email}"
}

resource "google_project_iam_member" "mk_news_sa_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.mk_news_sa.email}"
}

# 출력값
output "vpc_network" {
  value = google_compute_network.mk_news_vpc.name
}

output "subnet" {
  value = google_compute_subnetwork.mk_news_subnet.name
}

output "database_instance" {
  value = google_sql_database_instance.mk_news_db.name
}

output "database_private_ip" {
  value = google_sql_database_instance.mk_news_db.private_ip_address
}

output "storage_bucket" {
  value = google_storage_bucket.mk_news_storage.name
}

output "vector_index" {
  value = google_vertex_ai_index.mk_news_vector_index.name
}

output "vector_endpoint" {
  value = google_vertex_ai_index_endpoint.mk_news_vector_endpoint.name
}

output "api_service_url" {
  value = google_cloud_run_v2_service.mk_news_api.uri
}

output "admin_service_url" {
  value = google_cloud_run_v2_service.mk_news_admin.uri
}

output "artifact_registry" {
  value = google_artifact_registry_repository.mk_news_repo.name
}

output "vpc_connector" {
  value = google_vpc_access_connector.mk_news_connector.name
}

