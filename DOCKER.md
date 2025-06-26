# Docker Setup for WebPaladin

This document explains how to use Docker to run WebPaladin in a containerized environment.

## Author

**Nestor Torres** ([@n3stortorres](https://twitter.com/n3stortorres))

For questions, support, or contributions:
- **X (Twitter)**: [@n3stortorres](https://twitter.com/n3stortorres)
- **GitHub Issues**: Open an issue on this repository

## Overview

The Docker setup provides:
- **Isolated Environment**: All tools and dependencies in one container
- **Cross-Platform**: Works on any system with Docker
- **Consistent Results**: Same environment across different machines
- **Easy Deployment**: No need to install tools locally
- **Security**: Isolated scanning environment

## Prerequisites

- **Docker**: Install Docker Desktop or Docker Engine
- **Docker Compose**: Usually included with Docker Desktop
- **Git**: To clone the repository

## Quick Start

### 1. Build the Docker Image

```bash
# Build the image
./docker-run.sh -b

# Or using docker-compose directly
docker-compose build
```

### 2. Run the Scanner

```bash
# Interactive mode (recommended)
./docker-run.sh -i

# Run a specific scan
./docker-run.sh example.com

# Run with custom port
./docker-run.sh example.com 8443
```

## Docker Files Structure

```
WebServerScan/
├── Dockerfile                 # Main container image
├── Dockerfile.web            # Web interface image
├── docker-compose.yml        # Main compose file
├── docker-compose.override.yml # Development overrides
├── docker-compose.prod.yml   # Production settings
├── docker-compose.test.yml   # Testing environment
├── docker-run.sh             # Convenient runner script
├── .dockerignore             # Files to exclude from build
├── requirements.txt          # Python dependencies
├── requirements.web.txt      # Web interface dependencies
└── DOCKER.md                 # This file
```

## Usage Options

### Interactive Mode
```bash
./docker-run.sh -i
```
Opens the interactive menu where you can choose which scans to run.

### Direct Scan
```bash
./docker-run.sh example.com
./docker-run.sh example.com 8443
```
Runs a scan directly on the specified domain and port.

### Detached Mode
```bash
./docker-run.sh -d
```
Runs the container in the background.

### Shell Access
```bash
./docker-run.sh -s
```
Opens a bash shell inside the container for manual operations.

### View Logs
```bash
./docker-run.sh -l
```
Shows container logs in real-time.

### Web Interface
```bash
./docker-run.sh -w
```
Starts the web interface (if implemented) at http://localhost:8080.

## Docker Compose Commands

### Basic Operations

```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec webpaladin python3 /app/web_server_scan.py example.com
```

### Development Mode

```bash
# Use development overrides
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

### Production Mode

```bash
# Use production settings
docker-compose -f docker-compose.prod.yml up -d
```

### Testing Mode

```bash
# Run tests
docker-compose -f docker-compose.test.yml up --build
```

## Volume Mounts

The Docker setup mounts several directories:

- **`./scan_results:/app/scan_results`**: Scan results are saved here
- **`./Nmap-reports-files:/app/Nmap-reports-files`**: NMap XSL and Xalan files
- **`./wordlists:/app/wordlists:ro`**: Read-only wordlists (optional)
- **`./logs:/app/logs`**: Application logs (production)

## Environment Variables

### Main Container
- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered
- `TERM=xterm-256color`: Enables colored output
- `DEBUG=1`: Enables debug mode (development)
- `PRODUCTION=1`: Production mode settings

### Web Interface
- `FLASK_APP=app.py`: Flask application entry point
- `FLASK_ENV=production`: Flask environment

## Security Considerations

### Container Security
- **Non-root user**: Container runs as `scanner` user, not root
- **Privileged mode**: Required for network scanning capabilities
- **Network capabilities**: Added `NET_ADMIN` and `NET_RAW` capabilities
- **Read-only mounts**: Wordlists mounted as read-only

### Network Security
⚠️ **Important**: The container runs in privileged mode to allow network scanning. This is necessary for tools like NMap but should be used carefully.

### Data Persistence
- Scan results are persisted in the `./scan_results` directory
- Logs can be persisted in the `./logs` directory
- NMap files are mounted read-only for security

## Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Make scripts executable
chmod +x docker-run.sh
chmod +x web_server_scan.sh
```

#### 2. Docker Not Running
```bash
# Start Docker Desktop or Docker daemon
sudo systemctl start docker  # Linux
# Or start Docker Desktop on macOS/Windows
```

#### 3. Port Already in Use
```bash
# Check what's using the port
lsof -i :8080

# Stop conflicting services
docker-compose down
```

#### 4. Build Failures
```bash
# Clean and rebuild
./docker-run.sh -c
./docker-run.sh -r
```

#### 5. Network Scanning Issues
```bash
# Ensure container has proper capabilities
docker-compose down
docker-compose up --build
```

### Debug Mode

```bash
# Run with debug output
docker-compose run --rm webpaladin python3 -u /app/web_server_scan.py example.com

# Check container logs
docker-compose logs webpaladin
```

### Resource Issues

```bash
# Check container resource usage
docker stats webpaladin

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

## Performance Optimization

### Production Settings
- **Resource limits**: Set memory and CPU limits
- **Log rotation**: Configure log file rotation
- **Health checks**: Monitor container health
- **Restart policies**: Automatic restart on failure

### Development Settings
- **Volume mounts**: Mount source code for development
- **Debug mode**: Enable debug output
- **Interactive mode**: Enable interactive shell

## Customization

### Adding Custom Tools
1. Modify `Dockerfile` to install additional tools
2. Update `requirements.txt` for Python packages
3. Rebuild the image: `./docker-run.sh -r`

### Custom Wordlists
1. Create a `wordlists/` directory
2. Add your wordlist files
3. The directory is automatically mounted as read-only

### Custom NMap Scripts
1. Add scripts to `Nmap-reports-files/`
2. Update the scanner code to use them
3. Rebuild the image

## Monitoring and Logging

### Health Checks
The container includes health checks that verify:
- Python interpreter availability
- Basic functionality

### Logging
- **Application logs**: Written to stdout/stderr
- **Scan results**: Saved to `./scan_results/`
- **Docker logs**: Available via `docker-compose logs`

### Monitoring
```bash
# Check container status
docker-compose ps

# Monitor resource usage
docker stats

# View health check status
docker inspect webpaladin | grep Health -A 10
```

## Backup and Recovery

### Backup Scan Results
```bash
# Create backup of scan results
tar -czf scan_results_backup_$(date +%Y%m%d).tar.gz scan_results/
```

### Restore from Backup
```bash
# Extract backup
tar -xzf scan_results_backup_YYYYMMDD.tar.gz

# Start container
docker-compose up -d
```

## Advanced Usage

### Multi-Container Setup
```bash
# Start with web interface
docker-compose --profile web-interface up -d

# Start with database
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d
```

### Custom Networks
```bash
# Create custom network
docker network create scanner-network

# Use custom network in docker-compose.yml
networks:
  default:
    external:
      name: scanner-network
```

### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml scanner-stack
```

## Support

For issues with the Docker setup:
1. Check the troubleshooting section
2. Review Docker logs: `docker-compose logs`
3. Verify Docker installation: `docker --version`
4. Check system resources: `docker system df`

## Contributing

To contribute to the Docker setup:
1. Test changes in development mode
2. Update documentation
3. Ensure security best practices
4. Test on multiple platforms 