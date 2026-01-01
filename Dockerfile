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

# Create tdlibs directories and placeholder files for volume mounts
RUN mkdir -p tdlibs/td-agent-ping tdlibs/td-agent-speed && \
    touch tdlibs/td-agent-ping/libtdjson.so.1.8.59 && \
    touch tdlibs/td-agent-speed/libtdjson.so.1.8.59 && \
    ln -s /app/tdlibs/td-agent-ping/libtdjson.so.1.8.59 /app/tdlibs/td-agent-ping/libtdjson.so && \
    ln -s /app/tdlibs/td-agent-speed/libtdjson.so.1.8.59 /app/tdlibs/td-agent-speed/libtdjson.so && \
    mkdir -p tdlibs/td-agent-ping/td_db tdlibs/td-agent-speed/td_db

# Run the application
CMD ["python", "run.py"]
