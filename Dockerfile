# 베이스 이미지 설정
FROM python:3.9

# WORKDIR : working directory 작업경로
WORKDIR /backend

# 필요한 파일 복사
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install django-redis

# 소스 코드 복사
COPY . ./

# 프로젝트 실행 명령어
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
