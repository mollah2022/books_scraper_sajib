# Base image — Python 3.12 slim for smaller image size
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install setuptools first — required by scrapyd pkg_resources
RUN pip install --no-cache-dir setuptools==69.5.1

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . .
# Explicitly copy scrapyd config to ensure it's loaded
COPY scrapyd.cfg /etc/scrapyd/scrapyd.cfg

# Create necessary directories
RUN mkdir -p output logs database eggs dbs

# Expose Scrapyd port
EXPOSE 6800

# Copy and set entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Default command — start Scrapyd server
ENTRYPOINT ["/entrypoint.sh"]