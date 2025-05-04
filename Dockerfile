# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app source code
COPY . .

# Add grace_core_systems to Python path so modules can be found
ENV PYTHONPATH="${PYTHONPATH}:/app/grace_core_systems"

# Expose the app port
EXPOSE 8000

# Set unbuffered logging and run the app
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
