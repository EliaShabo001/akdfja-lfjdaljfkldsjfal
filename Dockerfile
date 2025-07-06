# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run will set PORT environment variable)
EXPOSE 8080

# Support both webhook and polling + keep-alive modes
CMD if [ "$DEPLOYMENT_MODE" = "polling_keepalive" ]; then \
      python TelegramBot.py; \
    else \
      exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 TelegramBot:app; \
    fi
