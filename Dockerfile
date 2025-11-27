# Modern GPA Docker Container
FROM nvidia/cuda:11.4-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=all

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    python3-dev \
    wget \
    curl \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install \
    numpy \
    pyyaml \
    pytest \
    dataclasses-json \
    typing-extensions

# Set working directory
WORKDIR /workspace

# Clone GPA repository with submodules
RUN git clone --recursive https://github.com/Jokeren/GPA.git .

# Copy configuration (optional - can be overridden at runtime)
COPY config.yaml config.yaml

# Install GPA using modern installer
RUN python3 install.py /opt/gpa

# Add GPA to PATH
ENV PATH="/opt/gpa/bin:/opt/gpa/hpctoolkit/bin:${PATH}"
ENV GPA_ROOT="/opt/gpa"

# Create workspace directory for benchmarks
RUN mkdir -p /workspace/results

# Default command - can be overridden
CMD ["python3", "run_benchmarks.py", "--help"]

# Labels for metadata
LABEL maintainer="GPA Development Team"
LABEL description="GPU Performance Advisor Container"
LABEL version="2.0"
LABEL cuda.version="11.4"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD nvidia-smi || exit 1
