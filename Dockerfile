FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 데이터베이스 디렉토리 생성
RUN mkdir -p /app/data

# 환경변수 설정
ENV PYTHONUNBUFFERED=1

# 봇 실행
CMD ["python", "bot.py"]