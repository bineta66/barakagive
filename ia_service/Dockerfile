FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Retry slow or interrupted package downloads instead of failing on pip's short
# default read timeout.
RUN python -m pip install --no-cache-dir --default-timeout=120 --retries=10 -r requirements.txt

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
