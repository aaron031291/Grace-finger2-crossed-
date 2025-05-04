# syntax=docker/dockerfile:1

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "grace_core_systems.GUI.dashboard.backend:app", "--host", "0.0.0.0", "--port", "7860", "--reload"]
