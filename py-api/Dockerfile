# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
# Note: .env file is optional - Railway will use environment variables instead
# COPY .env .env

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the application
# Railway will set PORT environment variable, default to 8000 if not set
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
