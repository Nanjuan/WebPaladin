# WebPaladin Web Interface Scanner

## Overview

The WebPaladin Web Interface Scanner provides a modern, web-based interface for the WebPaladin security scanner. This allows users to perform web server security scans through an intuitive browser interface instead of command-line tools.

## Table of Contents

- [Architecture](#architecture)
- [Dockerfile.web Breakdown](#dockerfileweb-breakdown)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Development](#development)

## Architecture

The web interface consists of several components working together:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │───▶│  Flask Web App  │───▶│  WebPaladin     │
│   (Port 8080)   │    │  (Port 8080)    │    │  Scanner        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Scan Results   │
                       │  Directory      │
                       └─────────────────┘
```

### Component Structure

- **Frontend**: Modern HTML5/CSS3/JavaScript interface
- **Backend**: Flask-based REST API
- **Scanner**: WebPaladin Python scanner integration
- **Storage**: File-based scan results storage

## Dockerfile.web Breakdown

### Base Image and Environment

```dockerfile
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web_interface/app.py
ENV FLASK_ENV=production
```

**Purpose:**
- Uses Python 3.11 slim for optimal size/performance balance
- Sets Flask environment variables for production deployment
- Enables unbuffered Python output for real-time logging

### System Dependencies

```dockerfile
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*
```

**Purpose:**
- `curl`: Required for health checks and HTTP requests
- `wget`: Alternative download utility for file operations
- Package cache cleanup reduces image size

### Application Setup

```dockerfile
WORKDIR /app
COPY requirements.web.txt /tmp/requirements.web.txt
RUN pip install --no-cache-dir -r /tmp/requirements.web.txt
```

**Dependencies (requirements.web.txt):**
- `Flask==2.3.3`: Web framework
- `Flask-CORS==4.0.0`: Cross-origin resource sharing
- `Werkzeug==2.3.7`: WSGI utilities
- `Jinja2==3.1.2`: Template engine
- Additional security and utility packages

### File Structure

```dockerfile
COPY web_interface/ /app/web_interface/
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY web_server_scan.py /app/
COPY check_dependencies.py /app/
COPY launcher.py /app/
COPY requirements.txt /app/
```

**File Organization:**
- `web_interface/`: Flask application code
- `templates/`: HTML templates for web interface
- `static/`: CSS, JavaScript, and static assets
- Scanner files: Core WebPaladin functionality

### Security Configuration

```dockerfile
RUN useradd -m -s /bin/bash webuser && \
    chown -R webuser:webuser /app
USER webuser
```

**Security Features:**
- Non-root user execution
- Proper file permissions
- Container isolation

### Health Monitoring

```dockerfile
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

**Health Check Details:**
- Checks every 30 seconds
- 10-second timeout
- 5-second startup grace period
- 3 retry attempts before marking unhealthy

## Installation & Setup

### Prerequisites

- Docker installed and running
- At least 512MB RAM available
- Port 8080 available

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd WebPaladin

# Build the web interface image
docker build -f Dockerfile.web -t webpaladin-web .

# Run the web interface
docker run -d -p 8080:8080 --name webpaladin-web webpaladin-web

# Access the interface
open http://localhost:8080
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  webpaladin-web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "8080:8080"
    volumes:
      - ./scan_results:/app/scan_results
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

```bash
# Start with Docker Compose
docker-compose up -d webpaladin-web
```

### Production Deployment

```bash
# Build for production
docker build -f Dockerfile.web -t webpaladin-web:latest .

# Run with resource limits
docker run -d \
  --name webpaladin-web \
  -p 8080:8080 \
  --memory=1g \
  --cpus=1.0 \
  --restart=unless-stopped \
  webpaladin-web:latest
```

## Usage Guide

### Web Interface Features

#### 1. Scan Configuration
- **Target Domain**: Enter the domain to scan (e.g., `example.com`)
- **Port**: Specify the port (default: 443)
- **Scan Type**: Choose from available scan types

#### 2. Scan Types Available
- **All Scans**: Comprehensive security assessment
- **NMap Web Server Scan**: Port and service enumeration
- **SSL/TLS Scan**: Certificate and encryption analysis
- **Vulnerability Scan**: Security vulnerability assessment

#### 3. Real-time Monitoring
- Progress bar showing scan completion
- Status messages with detailed information
- Live updates every 2 seconds

#### 4. Results Management
- View all scan results
- Download individual result files
- File size and modification date information

### Step-by-Step Usage

1. **Access the Interface**
   ```
   http://localhost:8080
   ```

2. **Configure Scan**
   - Enter target domain
   - Set port (optional, default 443)
   - Select scan type

3. **Start Scan**
   - Click "Start Scan" button
   - Monitor progress in real-time
   - Wait for completion

4. **View Results**
   - Click "Refresh Results" to see new files
   - Download results using "Download" buttons
   - Review scan findings

## API Reference

### Endpoints

#### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-26T03:00:00.000000"
}
```

#### Start Scan
```http
POST /api/scan
Content-Type: application/json

{
  "domain": "example.com",
  "port": "443",
  "scan_type": "all"
}
```
**Response:**
```json
{
  "message": "Scan started",
  "scan_id": "2025-06-26T03:00:00.000000"
}
```

#### Get Scan Status
```http
GET /api/scan/status
```
**Response:**
```json
{
  "running": true,
  "current_scan": {
    "domain": "example.com",
    "port": "443",
    "scan_type": "all",
    "start_time": "2025-06-26T03:00:00.000000"
  },
  "progress": 75,
  "message": "Scan in progress..."
}
```

#### List Results
```http
GET /api/results
```
**Response:**
```json
{
  "results": [
    {
      "name": "20250626_nmap-web-server.xml",
      "size": 1024,
      "modified": "2025-06-26T03:00:00.000000",
      "type": ".xml"
    }
  ]
}
```

#### Download Result
```http
GET /api/results/{filename}
```
**Response:** File download

### Error Handling

All API endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing parameters)
- `404`: Not Found (file not found)
- `500`: Internal Server Error

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check container logs
docker logs webpaladin-web

# Verify port availability
netstat -an | grep 8080
```

#### 2. Health Check Failing
```bash
# Test health endpoint manually
curl -f http://localhost:8080/health

# Check if Flask app is running
docker exec webpaladin-web ps aux | grep python
```

#### 3. Template Not Found
```bash
# Verify template files exist
docker exec webpaladin-web ls -la /app/templates/

# Check Flask app configuration
docker exec webpaladin-web cat /app/web_interface/app.py | grep template_folder
```

#### 4. Scan Not Starting
```bash
# Check scanner files exist
docker exec webpaladin-web ls -la /app/web_server_scan.py

# Verify permissions
docker exec webpaladin-web ls -la /app/
```

### Debug Mode

Enable debug mode for development:
```bash
# Run with debug environment
docker run -d -p 8080:8080 \
  -e FLASK_ENV=development \
  -e FLASK_DEBUG=1 \
  webpaladin-web
```

### Log Analysis

```bash
# View real-time logs
docker logs -f webpaladin-web

# Check specific error patterns
docker logs webpaladin-web | grep ERROR

# Monitor resource usage
docker stats webpaladin-web
```

## Security Considerations

### Container Security

1. **Non-root User**: Container runs as `webuser` instead of root
2. **File Permissions**: Proper ownership and permissions set
3. **Network Isolation**: Containerized network stack
4. **Resource Limits**: Configurable memory and CPU limits

### Web Application Security

1. **Input Validation**: All user inputs are validated
2. **CORS Configuration**: Proper cross-origin settings
3. **Error Handling**: No sensitive information in error messages
4. **File Access**: Restricted to scan results directory

### Network Security

1. **Port Exposure**: Only necessary port (8080) exposed
2. **Health Checks**: Regular health monitoring
3. **Restart Policy**: Automatic restart on failure

### Best Practices

```bash
# Use secrets management for production
docker run -d \
  --secret db_password \
  -e DB_PASSWORD_FILE=/run/secrets/db_password \
  webpaladin-web

# Implement reverse proxy
# Use HTTPS in production
# Regular security updates
```

## Development

### Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd WebPaladin

# Install development dependencies
pip install -r requirements.web.txt

# Run Flask app locally
export FLASK_APP=web_interface/app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8080
```

### File Structure for Development

```
WebPaladin/
├── web_interface/
│   └── app.py              # Flask application
├── templates/
│   └── index.html          # Main web interface
├── static/
│   └── style.css           # Additional styles
├── Dockerfile.web          # Web interface Dockerfile
├── requirements.web.txt    # Web dependencies
└── web_server_scan.py      # Core scanner
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## Performance Optimization

### Container Optimization

```dockerfile
# Multi-stage build for smaller images
FROM python:3.11-slim as builder
COPY requirements.web.txt .
RUN pip install --user -r requirements.web.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

### Resource Management

```bash
# Set appropriate resource limits
docker run -d \
  --memory=1g \
  --cpus=1.0 \
  --pids-limit=100 \
  webpaladin-web
```

### Caching Strategies

- Template caching enabled
- Static file caching
- Database connection pooling (if applicable)

## Monitoring and Logging

### Health Monitoring

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"

# Monitor resource usage
docker stats webpaladin-web
```

### Log Management

```bash
# Configure log rotation
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  webpaladin-web
```

### Metrics Collection

- Response time monitoring
- Error rate tracking
- Resource utilization metrics
- Scan completion statistics

## Conclusion

The WebPaladin Web Interface Scanner provides a powerful, user-friendly way to perform security scans through a modern web interface. The Dockerfile.web creates a production-ready container with proper security, monitoring, and scalability features.

For additional support or questions, refer to the main WebPaladin documentation or contact the development team.

---

**Author**: Nestor Torres (@n3stortorres)  
**Version**: 1.0  
**Last Updated**: June 2025 