# Cloud Run 고정 IP 주소 설정 가이드

## 개요

Cloud Run은 기본적으로 동적 IP 주소를 사용합니다. FTP 서버에서 IP 화이트리스트에 등록하기 위해 고정 IP가 필요한 경우, **Cloud NAT**를 설정하거나 **Cloud Run with VPC egress**를 사용해야 합니다.

## 중요: Cloud Run의 NAT Gateway 제한사항

### 1. Cloud Run의 아키텍처 특성
- Cloud Run은 완전 관리형 서버리스 플랫폼입니다
- 각 요청은 별도의 컨테이너 인스턴스로 처리됩니다
- 기본적으로 동적 IP 주소를 사용합니다

### 2. 고정 IP를 위한 옵션

#### 옵션 1: Cloud NAT + VPC Egress (권장)
**장점**: 
- Cloud Run에서 외부로의 아웃바운드 트래픽이 고정 IP를 통해 나감
- FTP 서버 화이트리스트 등록 가능

**단점**:
- VPC 접속 필요
- NAT Gateway 비용 발생

#### 옵션 2: Cloud Load Balancer (비권장)
- Cloud Run의 프론트엔드용으로는 적합하지만
- FTP 클라이언트 아웃바운드 IP는 여전히 동적

#### 옵션 3: 전용 VM + Cloud NAT (가장 안정적)
- VM을 중계 서버로 사용
- VM에 고정 IP 부여
- VM에서 FTP 클라이언트 실행

## 현재 Terraform 구성 분석

### 현재 상태
```terraform
# VPC Access Connector (있음)
resource "google_vpc_access_connector" "mk_news_connector" {
  name          = "mk-news-connector"
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.mk_news_vpc.name
  region        = var.region
  # ...
}
```

### 부족한 부분
1. NAT Gateway 리소스 없음
2. Cloud Router 없음
3. Cloud Run의 VPC egress 설정 없음

## 권장 해결방안

### 방안 1: Cloud NAT 구성 (Terraform 추가 필요)

```hcl
# Cloud Router 생성
resource "google_compute_router" "mk_news_router" {
  name    = "mk-news-router"
  region  = var.region
  network = google_compute_network.mk_news_vpc.id
}

# NAT Gateway 생성
resource "google_compute_router_nat" "mk_news_nat" {
  name   = "mk-news-nat"
  router = google_compute_router.mk_news_router.name
  region = var.region

  nat_ip_allocate_option = "MANUAL_ONLY"
  nat_ips                = [google_compute_address.mk_news_static_ip.id]

  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# 고정 IP 주소
resource "google_compute_address" "mk_news_static_ip" {
  name         = "mk-news-static-ip"
  address_type = "EXTERNAL"
  region       = var.region
}
```

### 방안 2: 수동 설정

#### GCP 콘솔에서 설정
1. **Cloud Router 생성**
   - 네비게이션: VPC network > Cloud Routers
   - 새 라우터 생성
   - 이름: `mk-news-router`
   - 네트워크: `mk-news-vpc`
   - 리전: `asia-northeast3`

2. **고정 IP 주소 예약**
   - 네비게이션: VPC network > External IP addresses
   - 예약
   - 이름: `mk-news-static-ip`
   - 유형: Static
   - 리전: `asia-northeast3`

3. **NAT Gateway 생성**
   - Cloud Router 내에서 NAT 생성
   - 이름: `mk-news-nat`
   - NAT IP: `mk-news-static-ip` 선택
   - 소스 서브넷: 모든 서브넷

4. **Cloud Run 서비스 업데이트**
   ```bash
   gcloud run services update mk-news-admin \
     --region=asia-northeast3 \
     --vpc-egress=private-ranges-only \
     --vpc-connector=mk-news-connector
   ```

## FTP 서버 화이트리스트 등록 절차

### 1. 고정 IP 확인
```bash
# 고정 IP 주소 확인
gcloud compute addresses describe mk-news-static-ip \
  --region=asia-northeast3 \
  --format='value(address)'
```

### 2. FTP 서버 관리자에게 제공할 정보
```
IP 주소: <고정 IP>
리전: asia-northeast3
프로젝트: mk-ai-project-473000
서비스: Cloud Run (mk-news-admin)
목적: 뉴스 기사 FTP 다운로드
```

## 비용 고려사항

### Cloud NAT 비용 (예상)
- NAT Gateway: 시간당 약 $0.045 (약 3,300원/월)
- 데이터 처리: GB당 $0.045
- 최소 요금: 약 $32/월 (최소 비용)

### 대안 비용 비교
| 방법 | 월 비용 | 안정성 |
|------|---------|--------|
| Cloud NAT | ~$32 | 중 |
| 전용 VM (e2-small) | ~$13 | 높음 |
| Cloud Run (동적 IP) | $0 | 낮음 (FTP 화이트리스트 불가) |

## 권장사항

### 단기 해결책
1. FTP 서버 관리자에게 **프로젝트 ID**와 **서비스 계정**을 알려주고
2. **IP 범위** 화이트리스트 요청
3. Cloud Run의 IP 범위는 정확히 알기 어려움

### 중장기 해결책
1. **전용 VM (e2-small)** 생성
2. VM에 고정 IP 부여
3. VM에서 FTP 클라이언트 실행
4. VM에서 Cloud Storage로 업로드
5. Cloud Run에서 Cloud Storage에서 처리

### 가장 실용적인 방법
FTP 서버 관리자에게 다음을 요청:
- **GCP 프로젝트 번호**: 268150188947
- **서비스 계정 이메일**: mk-news-platform@mk-ai-project-473000.iam.gserviceaccount.com
- **인증 정보 제공** (OAuth나 Service Account Key)

IP 기반 화이트리스트 대신 **인증 기반 접근**을 사용하는 것이 더 안전하고 관리하기 쉽습니다.

## 다음 단계

1. FTP 클라이언트 기능 구현 완료 (완료)
2. Streamlit UI에 FTP 모니터링 페이지 추가
3. 고정 IP 필요 여부 재확인
4. 필요한 경우 Cloud NAT 구성
5. FTP 서버 관리자와 협의하여 인증 방식 확인

## 참고 자료
- [Cloud NAT 문서](https://cloud.google.com/nat/docs/overview)
- [Cloud Run VPC egress](https://cloud.google.com/run/docs/configuring/connecting-vpc)
- [Cloud Router 문서](https://cloud.google.com/router/docs)

