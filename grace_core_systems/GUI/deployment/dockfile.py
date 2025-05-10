# Grace Core – Dockerfile v2 (with Lightning, NLP, and FastAPI)

FROM python:3.10-slim

WORKDIR /app

COPY . /app

# Ensure pip is up-to-date and dependencies install cleanly
RUN pip install --upgrade pip \
 && pip install -r requirements.txt || true \
 && pip install fastapi uvicorn[standard] python-multipart networkx

EXPOSE 8000

# Launch public API entrypoint with sandboxed interface
CMD ["uvicorn", "central_intelligence.public_api_launcher:app", "--app-dir", "grace_core_systems", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
