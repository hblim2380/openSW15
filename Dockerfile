# PostgreSQL 기본 이미지 사용
FROM postgres:latest

# 환경 변수 설정 (사용자 이름, 비밀번호, 데이터베이스 이름)
ENV POSTGRES_USER=team15
ENV POSTGRES_PASSWORD=team15
ENV POSTGRES_DB=kiosk

# 초기화 SQL 파일 복사
COPY init.sql /docker-entrypoint-initdb.d/
