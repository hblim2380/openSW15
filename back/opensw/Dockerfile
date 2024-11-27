# 빌드 단계
FROM --platform=linux/arm64 eclipse-temurin:17-jdk AS builder

# 작업 디렉토리 설정
WORKDIR /app

# Gradle Wrapper와 설정 파일 복사
COPY ./gradlew /app/gradlew
COPY ./gradle /app/gradle
COPY ./build.gradle /app/build.gradle
COPY ./settings.gradle /app/settings.gradle

# 의존성 미리 다운로드
RUN ./gradlew dependencies --no-daemon

# 소스 코드 복사
COPY ./src /app/src

# 애플리케이션 빌드
RUN ./gradlew clean build --no-daemon

# 실행 단계
FROM --platform=linux/arm64 eclipse-temurin:17-jre

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 결과물 복사
COPY --from=builder /app/build/libs/*.jar app.jar

# 컨테이너에서 실행할 포트 정의
EXPOSE 8080

# 애플리케이션 실행
ENTRYPOINT ["java", "-jar", "app.jar"]
