# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Explicitly add grace_core_systems to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/grace_core_systems"

# Expose the app port
EXPOSE 8000

# Set logging behavior and run the app
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
