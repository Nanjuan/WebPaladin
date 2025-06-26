#!/bin/bash

# Web Server Scanner Installation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies based on OS
install_dependencies() {
    local os=$(detect_os)
    
    print_status "Installing dependencies for $os..."
    
    case $os in
        "linux")
            if command_exists apt-get; then
                print_status "Using apt-get package manager..."
                sudo apt-get update
                sudo apt-get install -y nmap sslscan nikto python3 python3-pip openjdk-11-jdk dnsutils
                pip3 install sslyze
            elif command_exists yum; then
                print_status "Using yum package manager..."
                sudo yum install -y nmap sslscan nikto python3 python3-pip java-11-openjdk bind-utils
                pip3 install sslyze
            elif command_exists dnf; then
                print_status "Using dnf package manager..."
                sudo dnf install -y nmap sslscan nikto python3 python3-pip java-11-openjdk bind-utils
                pip3 install sslyze
            else
                print_error "No supported package manager found"
                return 1
            fi
            ;;
        "macos")
            if command_exists brew; then
                print_status "Using Homebrew package manager..."
                brew install nmap sslscan nikto python3 openjdk bind
                pip3 install sslyze
            else
                print_error "Homebrew not found. Please install Homebrew first:"
                print_error "https://brew.sh/"
                return 1
            fi
            ;;
        "windows")
            print_warning "Windows installation not automated"
            print_warning "Please install tools manually:"
            print_warning "- NMap: https://nmap.org/"
            print_warning "- SSLScan: https://github.com/rbsec/sslscan"
            print_warning "- Nikto: https://github.com/sullo/nikto"
            print_warning "- Python: https://python.org/"
            print_warning "- Java: https://adoptium.net/"
            return 1
            ;;
        *)
            print_error "Unsupported OS: $os"
            return 1
            ;;
    esac
    
    print_success "Dependencies installed successfully!"
}

# Function to make scripts executable
make_executable() {
    print_status "Making scripts executable..."
    
    if [[ -f "web_server_scan.sh" ]]; then
        chmod +x web_server_scan.sh
        print_success "Made web_server_scan.sh executable"
    fi
    
    if [[ -f "install.sh" ]]; then
        chmod +x install.sh
        print_success "Made install.sh executable"
    fi
}

# Function to create scan results directory
create_directories() {
    print_status "Creating directories..."
    
    mkdir -p scan_results
    print_success "Created scan_results directory"
}

# Function to run dependency check
run_dependency_check() {
    print_status "Running dependency check..."
    
    if command_exists python3; then
        if [[ -f "check_dependencies.py" ]]; then
            python3 check_dependencies.py
        else
            print_warning "check_dependencies.py not found"
        fi
    else
        print_warning "Python3 not found, skipping dependency check"
    fi
}

# Main installation function
main() {
    echo "=============================================="
    echo "        Web Server Scanner Installation"
    echo "=============================================="
    
    # Detect OS
    local os=$(detect_os)
    print_status "Detected OS: $os"
    
    # Ask user if they want to install dependencies
    echo
    read -p "Do you want to install dependencies automatically? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
    else
        print_warning "Skipping automatic dependency installation"
    fi
    
    # Make scripts executable
    make_executable
    
    # Create directories
    create_directories
    
    # Run dependency check
    run_dependency_check
    
    echo
    print_success "Installation completed!"
    echo
    echo "Next steps:"
    echo "1. Run the launcher: python3 launcher.py"
    echo "2. Or run directly:"
    echo "   - Shell version: ./web_server_scan.sh"
    echo "   - Python version: python3 web_server_scan.py"
    echo "3. Check dependencies: python3 check_dependencies.py"
}

# Run main function
main 