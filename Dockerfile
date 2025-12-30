FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for TDLib
RUN apt-get update && apt-get install -y \
    wget \
    git \
    build-essential \
    cmake \
    gperf \
    libssl-dev \
    zlib1g-dev \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build TDLib from source
RUN git clone https://github.com/tdlib/td.git /tmp/td && \
    cd /tmp/td && \
    git checkout master && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=/usr/local .. && \
    cmake --build . --target install -j$(nproc) && \
    mkdir -p /app/tdlibs/td-agent-ping /app/tdlibs/td-agent-speed && \
    cp /usr/local/lib/libtdjson.so* /app/tdlibs/td-agent-ping/ && \
    cp /usr/local/lib/libtdjson.so* /app/tdlibs/td-agent-speed/ && \
    mkdir -p /app/tdlibs/td-agent-ping/td_db /app/tdlibs/td-agent-speed/td_db && \
    cd / && rm -rf /tmp/td

# Run the application
CMD ["python", "run.py"]
