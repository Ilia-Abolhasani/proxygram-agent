FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    libssl3 \
    zlib1g \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create tdlibs directories (files will be mounted from host)
RUN mkdir -p tdlibs/td-agent-ping/td_db tdlibs/td-agent-speed/td_db

# Run the application
CMD ["python", "run.py"]
