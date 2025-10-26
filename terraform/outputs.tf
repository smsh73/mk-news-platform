# Terraform 출력값 정의
output "project_id" {
  description = "GCP 프로젝트 ID"
  value       = var.project_id
}

output "region" {
  description = "GCP 리전"
  value       = var.region
}

output "vpc_network_name" {
  description = "VPC 네트워크 이름"
  value       = google_compute_network.mk_news_vpc.name
}

output "subnet_name" {
  description = "서브넷 이름"
  value       = google_compute_subnetwork.mk_news_subnet.name
}

output "database_instance_name" {
  description = "Cloud SQL 인스턴스 이름"
  value       = google_sql_database_instance.mk_news_db.name
}

output "database_connection_name" {
  description = "Cloud SQL 연결 이름"
  value       = google_sql_database_instance.mk_news_db.connection_name
}

output "storage_bucket_name" {
  description = "Cloud Storage 버킷 이름"
  value       = google_storage_bucket.mk_news_storage.name
}

output "vector_index_name" {
  description = "Vertex AI Vector Search 인덱스 이름"
  value       = google_vertex_ai_index.mk_news_vector_index.name
}

output "vector_endpoint_name" {
  description = "Vertex AI Vector Search 엔드포인트 이름"
  value       = google_vertex_ai_index_endpoint.mk_news_vector_endpoint.name
}

output "server_external_ip" {
  description = "서버 외부 IP 주소"
  value       = google_compute_instance.mk_news_server.network_interface[0].access_config[0].nat_ip
}

output "server_internal_ip" {
  description = "서버 내부 IP 주소"
  value       = google_compute_instance.mk_news_server.network_interface[0].network_ip
}

output "service_account_email" {
  description = "서비스 계정 이메일"
  value       = google_service_account.mk_news_sa.email
}

