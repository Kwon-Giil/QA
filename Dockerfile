# 기존 v1.49.0에서 v1.64.0으로 변경
FROM mcr.microsoft.com/playwright/python:v1.64.0-noble
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV CI=true

CMD ["pytest", "-vs"]