# 1. 파이썬 3.10 슬림 버전 (가볍고 안정적) 사용
FROM python:3.10-slim

# 2. 로그가 버퍼링 없이 즉시 출력되도록 설정 (로그 확인용)
ENV PYTHONUNBUFFERED=1

# 3. 컨테이너 내부의 작업 폴더를 /app으로 설정
WORKDIR /app

# 4. 시스템 업데이트 및 필수 패키지 설치
# (Pillow 등 이미지 처리 라이브러리가 필요로 하는 기본 도구들)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. 라이브러리 목록 파일 먼저 복사
COPY requirements.txt .

# 6. 파이썬 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 7. 나머지 모든 소스 코드 복사
COPY . .

# 8. 봇 실행 명령어
CMD ["python", "main.py"]