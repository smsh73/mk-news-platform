# React Frontend Dockerfile
FROM node:18-alpine as build

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 package-lock.json 복사
COPY frontend/package*.json ./

# 의존성 설치
RUN npm ci --only=production

# 소스 코드 복사
COPY frontend/ .

# 프로덕션 빌드
RUN npm run build

# Nginx를 사용한 정적 파일 서빙
FROM nginx:alpine

# 빌드된 파일을 nginx 디렉토리로 복사
COPY --from=build /app/build /usr/share/nginx/html

# nginx 설정 파일 복사
COPY frontend/nginx.conf /etc/nginx/nginx.conf

# 포트 노출
EXPOSE 80

# nginx 시작
CMD ["nginx", "-g", "daemon off;"]
