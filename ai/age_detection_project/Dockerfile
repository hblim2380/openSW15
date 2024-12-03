# 베이스 이미지로 Python 3.9 이미지를 사용합니다.
FROM python:3.9-slim

# 컨테이너의 작업 디렉토리를 설정
WORKDIR /app

# 호스트 시스템에서 필요한 파일들을 컨테이너로 복사
COPY requirements.txt /app/
COPY main.py /app/
COPY models /app/models/

# 시스템의 종속성을 설치
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지들을 설치
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너가 실행될 때 main.py를 실행
CMD ["python", "main.py"]
