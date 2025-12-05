# backend/Dockerfile

# Build stage
FROM python:3.8-slim AS build
LABEL maintainer="Team26"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose and run
EXPOSE 8000
ENTRYPOINT ["python", "main.py"]
