#!/bin/bash

# WebPaladin - Shell Script Version
# Enhanced version with modular scanning options and dependency checking
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

# Global variables
DOMAIN=""
PORT="443"
SCAN_DIR="scan_results"
TOOLS_DIR="tools"

# Function to print colored output
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
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

# Function to install tools based on OS
install_tool() {
    local tool=$1
    local os=$(detect_os)
    
    print_status "Installing $tool..."
    
    case $os in
        "linux")
            case $tool in
                "nmap")
                    if command_exists apt-get; then
                        sudo apt-get update && sudo apt-get install -y nmap
                    elif command_exists yum; then
                        sudo yum install -y nmap
                    elif command_exists dnf; then
                        sudo dnf install -y nmap
                    else
                        print_error "Package manager not supported. Please install nmap manually."
                        return 1
                    fi
                    ;;
                "sslscan")
                    if command_exists apt-get; then
                        sudo apt-get install -y sslscan
                    elif command_exists yum; then
                        sudo yum install -y sslscan
                    else
                        print_error "Please install sslscan manually."
                        return 1
                    fi
                    ;;
                "nikto")
                    if command_exists apt-get; then
                        sudo apt-get install -y nikto
                    elif command_exists yum; then
                        sudo yum install -y nikto
                    else
                        print_error "Please install nikto manually."
                        return 1
                    fi
                    ;;
                "python3")
                    if command_exists apt-get; then
                        sudo apt-get install -y python3 python3-pip
                    elif command_exists yum; then
                        sudo yum install -y python3 python3-pip
                    else
                        print_error "Please install python3 manually."
                        return 1
                    fi
                    ;;
                "sslyze")
                    pip3 install sslyze
                    ;;
                *)
                    print_error "Unknown tool: $tool"
                    return 1
                    ;;
            esac
            ;;
        "macos")
            if command_exists brew; then
                case $tool in
                    "nmap")
                        brew install nmap
                        ;;
                    "sslscan")
                        brew install sslscan
                        ;;
                    "nikto")
                        brew install nikto
                        ;;
                    "python3")
                        brew install python3
                        ;;
                    "sslyze")
                        pip3 install sslyze
                        ;;
                    *)
                        print_error "Unknown tool: $tool"
                        return 1
                        ;;
                esac
            else
                print_error "Homebrew not found. Please install Homebrew first: https://brew.sh/"
                return 1
            fi
            ;;
        "windows")
            print_warning "Windows installation not automated. Please install $tool manually."
            return 1
            ;;
        *)
            print_error "Unsupported OS: $os"
            return 1
            ;;
    esac
    
    print_success "$tool installed successfully!"
}

# Function to check and install dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    local missing_tools=()
    local tools=("nmap" "sslscan" "nikto" "python3" "dig" "java")
    
    for tool in "${tools[@]}"; do
        if ! command_exists "$tool"; then
            missing_tools+=("$tool")
        else
            print_success "$tool is installed"
        fi
    done
    
    # Check for sslyze specifically
    if ! python3 -c "import sslyze" 2>/dev/null; then
        missing_tools+=("sslyze")
    else
        print_success "sslyze is installed"
    fi
    
    if [ ${#missing_tools[@]} -eq 0 ]; then
        print_success "All dependencies are installed!"
        return 0
    else
        print_warning "Missing tools: ${missing_tools[*]}"
        echo
        read -p "Would you like to install missing tools? (y/n): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for tool in "${missing_tools[@]}"; do
                echo
                read -p "Install $tool? (y/n): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    install_tool "$tool"
                fi
            done
        else
            print_error "Some tools are missing. Please install them manually."
            return 1
        fi
    fi
}

# Function to create scan directory
setup_scan_directory() {
    if [ ! -d "$SCAN_DIR" ]; then
        mkdir -p "$SCAN_DIR"
        print_success "Created scan directory: $SCAN_DIR"
    fi
    
    cd "$SCAN_DIR"
}

# Function to run nmap web server scan
run_nmap_web_scan() {
    print_status "Starting NMap Web Server scan..."
    local output_file="${DOMAIN}-nmap-web-server"
    
    nmap -sC -sV -O -v1 --script=banner,http-headers -oX "${output_file}.xml" --stylesheet="../Nmap-reports-files/nmap.xsl" "$DOMAIN"
    
    if command_exists java; then
        java -jar "../Nmap-reports-files/xalan.jar" -IN "${output_file}.xml" -OUT "${output_file}.html"
        print_success "NMap web scan completed: ${output_file}.html"
    else
        print_warning "Java not found. XML file created: ${output_file}.xml"
    fi
}

# Function to run nmap SSL scan
run_nmap_ssl_scan() {
    print_status "Starting NMap SSL scan..."
    local output_file="${DOMAIN}-nmap-ssl"
    
    nmap -v1 -p "$PORT" --script=ssl-enum-ciphers -oX "${output_file}.xml" --stylesheet="../Nmap-reports-files/nmap.xsl" "$DOMAIN"
    
    if command_exists java; then
        java -jar "../Nmap-reports-files/xalan.jar" -IN "${output_file}.xml" -OUT "${output_file}.html"
        print_success "NMap SSL scan completed: ${output_file}.html"
    else
        print_warning "Java not found. XML file created: ${output_file}.xml"
    fi
}

# Function to run nmap vulners scan
run_nmap_vulners_scan() {
    print_status "Starting NMap Vulners scan..."
    local output_file="${DOMAIN}-nmap-vulners"
    
    nmap -sV -sS -O -v1 --script=vulners.nse -oX "${output_file}.xml" --stylesheet="../Nmap-reports-files/nmap.xsl" "$DOMAIN"
    
    if command_exists java; then
        java -jar "../Nmap-reports-files/xalan.jar" -IN "${output_file}.xml" -OUT "${output_file}.html"
        print_success "NMap Vulners scan completed: ${output_file}.html"
    else
        print_warning "Java not found. XML file created: ${output_file}.xml"
    fi
}

# Function to run extended port scan
run_extended_port_scan() {
    print_status "Starting extended port scan..."
    local output_file="nmap-extended-ports-${DOMAIN}"
    
    nmap -Pn -p- -vv -oX "${output_file}.xml" --stylesheet="../Nmap-reports-files/nmap.xsl" "$DOMAIN"
    
    if command_exists java; then
        java -jar "../Nmap-reports-files/xalan.jar" -IN "${output_file}.xml" -OUT "${output_file}.html"
        print_success "Extended port scan completed: ${output_file}.html"
    else
        print_warning "Java not found. XML file created: ${output_file}.xml"
    fi
}

# Function to run SSLScan
run_sslscan() {
    print_status "Starting SSLScan..."
    local output_file="sslscan-${DOMAIN}.txt"
    
    sslscan --no-failed "$DOMAIN" > "$output_file"
    print_success "SSLScan completed: $output_file"
}

# Function to run SSLyze
run_sslyze() {
    print_status "Starting SSLyze..."
    local output_file="sslyze-${DOMAIN}.txt"
    
    python3 -m sslyze --regular "$DOMAIN" > "$output_file"
    print_success "SSLyze completed: $output_file"
}

# Function to run Heartbleed test
run_heartbleed_test() {
    print_status "Starting Heartbleed test..."
    local output_file="nmap-ssl-heartbleed-${DOMAIN}.txt"
    
    echo "If vulnerable, you will see 'State: VULNERABLE' in the scan results" > "$output_file"
    echo "----------------------------------------------------------" >> "$output_file"
    nmap -p 443 --script ssl-heartbleed "$DOMAIN" >> "$output_file"
    print_success "Heartbleed test completed: $output_file"
}

# Function to run DNS enumeration
run_dns_enumeration() {
    print_status "Starting DNS enumeration..."
    
    # Dig record types
    local output_file="dig-record-types-${DOMAIN}.txt"
    echo "View all the record types (A, MX, NS, etc.)" > "$output_file"
    echo "------------------------------------------------------" >> "$output_file"
    dig "$DOMAIN" -t any >> "$output_file"
    print_success "DNS record types completed: $output_file"
    
    # Zone transfer test
    local zone_file="dig-zone-transfer-${DOMAIN}.txt"
    echo "Request to get a copy of the zone transfer from the primary server" > "$zone_file"
    echo "(Transfer failed. means the application PASS the test)" >> "$zone_file"
    echo "-----------------------------------------------------" >> "$zone_file"
    dig "$DOMAIN" -t axfr >> "$zone_file"
    print_success "Zone transfer test completed: $zone_file"
    
    # DNS brute force
    local brute_file="nmap-DNS-brute-${DOMAIN}.txt"
    echo "Nmap brute force subdomain enumeration" > "$brute_file"
    echo "------------------------------------------------------" >> "$brute_file"
    nmap --script dns-brute "$DOMAIN" >> "$brute_file"
    print_success "DNS brute force completed: $brute_file"
}

# Function to run Nikto
run_nikto() {
    print_status "Starting Nikto..."
    local output_file="nikto-${DOMAIN}.html"
    
    nikto -C all -ssl "$PORT" -Format HTML -output "$output_file" -Save niktosave -host "$DOMAIN"
    print_success "Nikto completed: $output_file"
}

# Function to show menu
show_menu() {
    echo
    echo "=============================================="
    echo "           Web Server Scanner Menu"
    echo "=============================================="
    echo "Domain: $DOMAIN"
    echo "Port: $PORT"
    echo "=============================================="
    echo "1.  NMap Web Server Scan"
    echo "2.  NMap SSL Scan"
    echo "3.  NMap Vulners Scan"
    echo "4.  Extended Port Scan"
    echo "5.  SSLScan"
    echo "6.  SSLyze"
    echo "7.  Heartbleed Test"
    echo "8.  DNS Enumeration"
    echo "9.  Nikto"
    echo "10. Run All Scans"
    echo "11. Change Domain/Port"
    echo "12. Check Dependencies"
    echo "0.  Exit"
    echo "=============================================="
}

# Function to get user selection
get_user_selection() {
    read -p "Enter your choice (0-12): " choice
    echo "$choice"
}

# Function to run selected scan
run_selected_scan() {
    local choice=$1
    
    case $choice in
        1)
            run_nmap_web_scan
            ;;
        2)
            run_nmap_ssl_scan
            ;;
        3)
            run_nmap_vulners_scan
            ;;
        4)
            run_extended_port_scan
            ;;
        5)
            run_sslscan
            ;;
        6)
            run_sslyze
            ;;
        7)
            run_heartbleed_test
            ;;
        8)
            run_dns_enumeration
            ;;
        9)
            run_nikto
            ;;
        10)
            print_status "Running all scans..."
            run_nmap_web_scan
            run_nmap_ssl_scan
            run_nmap_vulners_scan
            run_extended_port_scan
            run_sslscan
            run_sslyze
            run_heartbleed_test
            run_dns_enumeration
            run_nikto
            print_success "All scans completed!"
            ;;
        11)
            get_domain_and_port
            ;;
        12)
            check_dependencies
            ;;
        0)
            print_success "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            ;;
    esac
}

# Function to get domain and port from user
get_domain_and_port() {
    echo
    read -p "Enter domain to scan: " DOMAIN
    
    if [ -z "$DOMAIN" ]; then
        print_error "Domain cannot be empty!"
        return 1
    fi
    
    read -p "Enter port (default: 443): " port_input
    if [ -n "$port_input" ]; then
        PORT="$port_input"
    fi
    
    print_success "Target set to: $DOMAIN:$PORT"
}

# Main function
main() {
    echo "=============================================="
    echo "        Web Server Scanner - Shell Version"
    echo "=============================================="
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependency check failed. Exiting."
        exit 1
    fi
    
    # Get domain and port
    get_domain_and_port
    
    # Setup scan directory
    setup_scan_directory
    
    # Main loop
    while true; do
        show_menu
        choice=$(get_user_selection)
        run_selected_scan "$choice"
        
        echo
        read -p "Press Enter to continue..."
    done
}

# Check if script is run with arguments
if [ $# -eq 1 ]; then
    DOMAIN="$1"
    if [ $# -eq 2 ]; then
        PORT="$2"
    fi
    print_status "Using command line arguments: $DOMAIN:$PORT"
fi

# Run main function
main 