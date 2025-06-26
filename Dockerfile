# WebPaladin Docker Image
# Based on Ubuntu 22.04 LTS
#
# Author: Nestor Torres (@n3stortorres)
# For questions or support, contact me on X (Twitter) @n3stortorres
# or open an issue on GitHub.

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    nmap \
    sslscan \
    nikto \
    openjdk-11-jdk \
    dnsutils \
    curl \
    wget \
    git \
    vim \
    nano \
    xsltproc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Create app directory
WORKDIR /app

# Copy application files
COPY web_server_scan.py /app/
COPY check_dependencies.py /app/
COPY launcher.py /app/
COPY requirements.txt /app/

# Create scan results directory
RUN mkdir -p /app/scan_results

# Copy Nmap files if they exist
COPY Nmap-reports-files/ /app/Nmap-reports-files/

# Set permissions
RUN chmod +x /app/web_server_scan.py
RUN chmod +x /app/check_dependencies.py
RUN chmod +x /app/launcher.py

# Create a non-root user for security
RUN useradd -m -s /bin/bash scanner && \
    chown -R scanner:scanner /app

# Switch to non-root user
USER scanner

# Set default command
CMD ["python3", "/app/launcher.py"] 