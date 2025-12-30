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

# Download and extract TDLib pre-built binaries
RUN wget -q https://github.com/tdlib/td/releases/download/v1.8.31/tdlib-1.8.31-linux-x86_64.tar.gz && \
    tar -xzf tdlib-1.8.31-linux-x86_64.tar.gz && \
    mkdir -p tdlibs/td-agent-ping tdlibs/td-agent-speed && \
    cp -r td/lib tdlibs/td-agent-ping/ && \
    cp -r td/lib tdlibs/td-agent-speed/ && \
    rm -rf tdlib-1.8.31-linux-x86_64.tar.gz td

# Run the application
CMD ["python", "run.py"]
