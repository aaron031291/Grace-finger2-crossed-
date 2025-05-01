FROM python:3.11-slim

WORKDIR /app

RUN pip install "fastapi[all]" redis python-jose[cryptography] passlib python-multipart

COPY . .

CMD ["uvicorn", "dashboard_api:app", "--host", "0.0.0.0", "--port", "8000"]