FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8505

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8505/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8505", "--server.address=0.0.0.0"]
