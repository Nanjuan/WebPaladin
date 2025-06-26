#!/bin/bash

# WebPaladin Docker Runner Script
# Convenience script for running WebPaladin in Docker containers
#
# Author: Nestor Torres (@n3stortorres)
# For questions or support, contact me on X (Twitter) @n3stortorres
# or open an issue on GitHub.

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

# Function to show usage
show_usage() {
    echo "WebPaladin Docker Runner Script"
    echo "Usage: $0 [OPTIONS] [DOMAIN] [PORT]"
    echo
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -b, --build         Build the Docker image"
    echo "  -r, --rebuild       Rebuild the Docker image (no cache)"
    echo "  -i, --interactive   Run in interactive mode"
    echo "  -d, --detached      Run in detached mode"
    echo "  -c, --clean         Clean up containers and images"
    echo "  -l, --logs          Show container logs"
    echo "  -s, --shell         Open shell in container"
    echo "  -w, --web           Start with web interface"
    echo
    echo "Examples:"
    echo "  $0 example.com              # Run scan on example.com"
    echo "  $0 example.com 8443         # Run scan on example.com:8443"
    echo "  $0 -b                       # Build image"
    echo "  $0 -i                       # Interactive mode"
    echo "  $0 -s                       # Open shell"
    echo "  $0 -w                       # Start with web interface"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    docker-compose build
    print_success "Docker image built successfully!"
}

# Function to rebuild Docker image
rebuild_image() {
    print_status "Rebuilding Docker image (no cache)..."
    docker-compose build --no-cache
    print_success "Docker image rebuilt successfully!"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and images..."
    docker-compose down --rmi all --volumes --remove-orphans
    docker system prune -f
    print_success "Cleanup completed!"
}

# Function to show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose logs -f webpaladin
}

# Function to open shell
open_shell() {
    print_status "Opening shell in container..."
    docker-compose exec webpaladin /bin/bash
}

# Function to run scan
run_scan() {
    local domain=$1
    local port=${2:-443}
    
    if [ -z "$domain" ]; then
        print_error "Domain is required"
        show_usage
        exit 1
    fi
    
    print_status "Running scan on $domain:$port..."
    docker-compose run --rm webpaladin python3 /app/web_server_scan.py "$domain" "$port"
}

# Function to run interactive
run_interactive() {
    print_status "Starting interactive mode..."
    docker-compose run --rm -it webpaladin python3 /app/launcher.py
}

# Function to run detached
run_detached() {
    print_status "Starting detached mode..."
    docker-compose up -d webpaladin
    print_success "Container started in detached mode"
    print_status "Use '$0 -l' to view logs"
    print_status "Use '$0 -s' to open shell"
}

# Function to start web interface
start_web_interface() {
    print_status "Starting web interface..."
    docker-compose --profile web-interface up -d
    print_success "Web interface started at http://localhost:8080"
}

# Main function
main() {
    # Check if Docker is running
    check_docker
    
    # Parse command line arguments
    local build=false
    local rebuild=false
    local interactive=false
    local detached=false
    local clean=false
    local logs=false
    local shell=false
    local web=false
    local domain=""
    local port=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -b|--build)
                build=true
                shift
                ;;
            -r|--rebuild)
                rebuild=true
                shift
                ;;
            -i|--interactive)
                interactive=true
                shift
                ;;
            -d|--detached)
                detached=true
                shift
                ;;
            -c|--clean)
                clean=true
                shift
                ;;
            -l|--logs)
                logs=true
                shift
                ;;
            -s|--shell)
                shell=true
                shift
                ;;
            -w|--web)
                web=true
                shift
                ;;
            -*)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [ -z "$domain" ]; then
                    domain="$1"
                elif [ -z "$port" ]; then
                    port="$1"
                else
                    print_error "Too many arguments"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Execute actions
    if [ "$clean" = true ]; then
        cleanup
        exit 0  # Exit after cleanup
    fi
    
    if [ "$rebuild" = true ]; then
        rebuild_image
    elif [ "$build" = true ]; then
        build_image
    fi
    
    if [ "$logs" = true ]; then
        show_logs
    elif [ "$shell" = true ]; then
        open_shell
    elif [ "$web" = true ]; then
        start_web_interface
    elif [ "$interactive" = true ]; then
        run_interactive
    elif [ "$detached" = true ]; then
        run_detached
    elif [ -n "$domain" ]; then
        run_scan "$domain" "$port"
    else
        # Default to interactive mode
        run_interactive
    fi
}

# Run main function
main "$@" 