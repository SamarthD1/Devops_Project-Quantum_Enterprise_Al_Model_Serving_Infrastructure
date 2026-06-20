# Use official, stable python slim image (supports x86 and arm64 architectures)
FROM python:3.11-slim

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout/stderr streams for real-time log ingestion
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies (curl is needed for the Docker healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install python dependencies without saving pip cache to keep the image slim
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY main.py model_loader.py ./
COPY schemas/ ./schemas/
COPY utils/ ./utils/
COPY models/ ./models/

# Create logs directory
RUN mkdir -p logs

# Create a non-root system user and group for enhanced security compliance
RUN groupadd -g 10001 quantum && \
    useradd -u 10001 -g quantum -s /bin/bash -m quantumuser

# Change ownership of /app directory to the non-root user
RUN chown -R quantumuser:quantum /app

# Switch to the non-root user
USER quantumuser:quantum

# Expose backend API port
EXPOSE 8000

# Docker container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the uvicorn API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
