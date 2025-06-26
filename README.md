# WebPaladin

A comprehensive web server security scanning toolkit with support for multiple operating systems and modular scanning options.

## Author

**Nestor Torres** ([@n3stortorres](https://twitter.com/n3stortorres))

For questions, support, or contributions:
- **X (Twitter)**: [@n3stortorres](https://twitter.com/n3stortorres)
- **GitHub Issues**: Open an issue on this repository

## Overview

This project provides three different implementations of a web server scanner:

1. **Shell Script Version** (`web_server_scan.sh`) - Cross-platform bash script
2. **Python Version** (`web_server_scan.py`) - Cross-platform Python script
3. **Docker Version** - Containerized environment with all tools pre-installed
4. **Dependency Checker** (`check_dependencies.py`) - Standalone tool to verify and install dependencies

## Features

- **Modular Scanning**: Choose which scans to run individually
- **Cross-Platform Support**: Works on Linux, macOS, and Windows
- **Docker Support**: Complete containerized environment
- **Automatic Dependency Management**: Checks and installs required tools
- **Comprehensive Scanning**: Includes multiple security testing tools
- **User-Friendly Interface**: Interactive menu system
- **Detailed Reporting**: Generates HTML and text reports

## Available Scans

1. **NMap Web Server Scan** - Comprehensive web server enumeration
2. **NMap SSL Scan** - SSL/TLS cipher enumeration
3. **NMap Vulners Scan** - Vulnerability scanning using Vulners database
4. **Extended Port Scan** - Full port range scanning
5. **SSLScan** - SSL/TLS configuration analysis
6. **SSLyze** - Advanced SSL/TLS testing
7. **Heartbleed Test** - Heartbleed vulnerability detection
8. **DNS Enumeration** - DNS record analysis and subdomain enumeration
9. **Nikto** - Web server vulnerability scanner

## Prerequisites

The scanner requires the following tools to be installed:

- **nmap** - Network mapper for port scanning
- **sslscan** - SSL/TLS scanner
- **nikto** - Web server scanner
- **python3** - Python 3 interpreter
- **java** - Java Runtime Environment (for XML to HTML conversion)
- **dig** - DNS lookup utility
- **sslyze** - SSL/TLS scanner (Python package)

## Installation

### Option 1: Docker (Recommended)

The easiest way to run the scanner is using Docker, which includes all dependencies:

```bash
# Build the Docker image
./docker-run.sh -b

# Run in interactive mode
./docker-run.sh -i

# Run a specific scan
./docker-run.sh example.com

# Run with custom port
./docker-run.sh example.com 8443
```

For detailed Docker documentation, see [DOCKER.md](DOCKER.md).

### Option 2: Local Installation

#### Quick Start

1. **Check Dependencies**:
   ```bash
   python3 check_dependencies.py
   ```

2. **Run the Scanner**:
   ```bash
   # Shell version
   chmod +x web_server_scan.sh
   ./web_server_scan.sh example.com
   
   # Python version
   python3 web_server_scan.py example.com
   ```

#### Manual Installation

##### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install nmap sslscan nikto python3 python3-pip openjdk-11-jdk dnsutils
pip3 install sslyze
```

##### Linux (CentOS/RHEL/Fedora)
```bash
sudo yum install nmap sslscan nikto python3 python3-pip java-11-openjdk bind-utils
# or for Fedora
sudo dnf install nmap sslscan nikto python3 python3-pip java-11-openjdk bind-utils
pip3 install sslyze
```

##### macOS
```bash
# Install Homebrew first if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install nmap sslscan nikto python3 openjdk bind
pip3 install sslyze
```

##### Windows
For Windows, you'll need to manually install the tools:

1. **NMap**: Download from https://nmap.org/
2. **SSLScan**: Download from https://github.com/rbsec/sslscan
3. **Nikto**: Download from https://github.com/sullo/nikto
4. **Python**: Download from https://python.org/
5. **Java**: Download from https://adoptium.net/

## Usage

### Docker Usage

```bash
# Interactive mode (recommended)
./docker-run.sh -i

# Direct scan
./docker-run.sh example.com
./docker-run.sh example.com 8443

# Shell access
./docker-run.sh -s

# View logs
./docker-run.sh -l

# Clean up
./docker-run.sh -c
```

### Local Usage

#### Dependency Checker

The dependency checker can verify and install all required tools:

```bash
# Check dependencies
python3 check_dependencies.py

# Show installation guide
python3 check_dependencies.py --guide
```

#### Shell Script Version

```bash
# Make executable
chmod +x web_server_scan.sh

# Run with domain
./web_server_scan.sh example.com

# Run with domain and port
./web_server_scan.sh example.com 8443

# Run interactively
./web_server_scan.sh
```

#### Python Version

```bash
# Run with domain
python3 web_server_scan.py example.com

# Run with domain and port
python3 web_server_scan.py example.com 8443

# Run interactively
python3 web_server_scan.py
```

### Interactive Menu

Both versions provide an interactive menu:

```
==============================================
           WebPaladin Menu
==============================================
Domain: example.com
Port: 443
==============================================
1.  NMap Web Server Scan
2.  NMap SSL Scan
3.  NMap Vulners Scan
4.  Extended Port Scan
5.  SSLScan
6.  SSLyze
7.  Heartbleed Test
8.  DNS Enumeration
9.  Nikto
10. Run All Scans
11. Change Domain/Port
12. Check Dependencies
0.  Exit
==============================================
```

## Output Files

All scan results are saved in the `scan_results/` directory:

- **NMap scans**: XML and HTML files
- **SSLScan**: Text files
- **SSLyze**: Text files
- **Nikto**: HTML files
- **DNS enumeration**: Text files

## File Structure

```
WebServerScan/
├── web_server_scan.sh          # Shell script version
├── web_server_scan.py          # Python version
├── check_dependencies.py       # Dependency checker
├── launcher.py                 # Universal launcher
├── install.sh                  # Installation script
├── web_server_scan.bat         # Original Windows batch file
├── Nmap-reports-files/         # NMap XSL and Xalan files
│   ├── nmap.xsl
│   └── xalan.jar
├── scan_results/               # Generated scan results
├── Dockerfile                  # Docker container image
├── Dockerfile.web             # Web interface Docker image
├── docker-compose.yml         # Docker Compose configuration
├── docker-compose.override.yml # Development overrides
├── docker-compose.prod.yml    # Production settings
├── docker-compose.test.yml    # Testing environment
├── docker-run.sh              # Docker convenience script
├── .dockerignore              # Docker build exclusions
├── requirements.txt           # Python dependencies
├── requirements.web.txt       # Web interface dependencies
├── DOCKER.md                  # Docker documentation
└── README.md                  # This file
```

## Security Considerations

⚠️ **Important**: This tool is designed for security testing and should only be used:

- On systems you own or have explicit permission to test
- In controlled environments
- For educational or authorized security assessments

**Never use this tool against systems without proper authorization.**

## Troubleshooting

### Docker Issues

```bash
# Check Docker is running
docker --version
docker-compose --version

# Build issues
./docker-run.sh -c  # Clean up
./docker-run.sh -r  # Rebuild

# Permission issues
chmod +x docker-run.sh
```

### Local Installation Issues

1. **Permission Denied**:
   ```bash
   chmod +x web_server_scan.sh
   ```

2. **Java not found**:
   - Install Java Runtime Environment
   - Ensure JAVA_HOME is set correctly

3. **NMap scripts not found**:
   - Update NMap to the latest version
   - Install additional NMap scripts if needed

4. **SSLScan/SSLyze errors**:
   - Ensure Python 3 and pip are installed
   - Reinstall sslyze: `pip3 install --upgrade sslyze`

### Getting Help

1. Run the dependency checker first: `python3 check_dependencies.py`
2. Check the installation guide: `python3 check_dependencies.py --guide`
3. For Docker issues, see [DOCKER.md](DOCKER.md)
4. Ensure all tools are in your PATH
5. Check file permissions on the script files

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## Contact & Support

**Nestor Torres** ([@n3stortorres](https://twitter.com/n3stortorres))

For questions, support, bug reports, or feature requests:

- **X (Twitter)**: [@n3stortorres](https://twitter.com/n3stortorres)
- **GitHub Issues**: Open an issue on this repository
- **Documentation**: Check this README and [DOCKER.md](DOCKER.md)

## License

This project is provided as-is for educational and authorized security testing purposes.

## Acknowledgments

- Original batch script by the project creator
- NMap project for the network scanning capabilities
- All the open-source security tools used in this scanner 