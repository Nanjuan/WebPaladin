#!/usr/bin/env python3
"""
WebPaladin - Python Version
Enhanced version with modular scanning options and dependency checking

Author: Nestor Torres (@n3stortorres)
For questions or support, contact me on X (Twitter) @n3stortorres
or open an issue on GitHub.

This tool provides comprehensive web server security scanning capabilities
with support for multiple operating systems and modular scanning options.
"""

import os
import sys
import subprocess
import platform
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
from datetime import datetime

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class WebPaladin:
    def __init__(self):
        self.domain = ""
        self.port = "443"
        self.scan_dir = "scan_results"
        self.tools_dir = "tools"
        self.os_type = self.detect_os()
        self.timestamp = datetime.now().strftime("%Y%m%d")
        
    def print_status(self, message: str):
        """Print status message with blue color"""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")
        
    def print_success(self, message: str):
        """Print success message with green color"""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
        
    def print_warning(self, message: str):
        """Print warning message with yellow color"""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
        
    def print_error(self, message: str):
        """Print error message with red color"""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
        
    def detect_os(self) -> str:
        """Detect the operating system"""
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"
            
    def command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        return shutil.which(command) is not None
        
    def run_command(self, command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, and stderr"""
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
            
    def run_command_with_timeout(self, command: List[str], timeout: int = 600, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command with custom timeout and return exit code, stdout, and stderr"""
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)
            
    def install_tool(self, tool: str) -> bool:
        """Install a tool based on the OS"""
        self.print_status(f"Installing {tool}...")
        
        if self.os_type == "linux":
            return self._install_tool_linux(tool)
        elif self.os_type == "macos":
            return self._install_tool_macos(tool)
        elif self.os_type == "windows":
            self.print_warning("Windows installation not automated. Please install tools manually.")
            return False
        else:
            self.print_error(f"Unsupported OS: {self.os_type}")
            return False
            
    def _install_tool_linux(self, tool: str) -> bool:
        """Install tool on Linux"""
        package_managers = [
            ("apt-get", ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y"]),
            ("yum", ["sudo", "yum", "install", "-y"]),
            ("dnf", ["sudo", "dnf", "install", "-y"])
        ]
        
        tool_packages = {
            "nmap": "nmap",
            "sslscan": "sslscan",
            "nikto": "nikto",
            "python3": "python3 python3-pip",
            "java": "openjdk-11-jdk"
        }
        
        for pm_name, pm_cmd in package_managers:
            if self.command_exists(pm_name):
                if tool in tool_packages:
                    cmd = pm_cmd + [tool_packages[tool]]
                    exit_code, stdout, stderr = self.run_command(cmd)
                    if exit_code == 0:
                        self.print_success(f"{tool} installed successfully!")
                        return True
                    else:
                        self.print_error(f"Failed to install {tool}: {stderr}")
                        return False
                elif tool == "sslyze":
                    # Install sslyze via pip
                    cmd = ["pip3", "install", "sslyze"]
                    exit_code, stdout, stderr = self.run_command(cmd)
                    if exit_code == 0:
                        self.print_success(f"{tool} installed successfully!")
                        return True
                    else:
                        self.print_error(f"Failed to install {tool}: {stderr}")
                        return False
                        
        self.print_error(f"Package manager not supported for {tool}")
        return False
        
    def _install_tool_macos(self, tool: str) -> bool:
        """Install tool on macOS"""
        if not self.command_exists("brew"):
            self.print_error("Homebrew not found. Please install Homebrew first: https://brew.sh/")
            return False
            
        tool_packages = {
            "nmap": "nmap",
            "sslscan": "sslscan",
            "nikto": "nikto",
            "python3": "python3",
            "java": "openjdk"
        }
        
        if tool in tool_packages:
            cmd = ["brew", "install", tool_packages[tool]]
            exit_code, stdout, stderr = self.run_command(cmd)
            if exit_code == 0:
                self.print_success(f"{tool} installed successfully!")
                return True
            else:
                self.print_error(f"Failed to install {tool}: {stderr}")
                return False
        elif tool == "sslyze":
            cmd = ["pip3", "install", "sslyze"]
            exit_code, stdout, stderr = self.run_command(cmd)
            if exit_code == 0:
                self.print_success(f"{tool} installed successfully!")
                return True
            else:
                self.print_error(f"Failed to install {tool}: {stderr}")
                return False
                
        return False
        
    def check_dependencies(self) -> bool:
        """Check and install dependencies"""
        self.print_status("Checking dependencies...")
        
        tools = ["nmap", "sslscan", "nikto", "python3", "dig", "java"]
        missing_tools = []
        
        for tool in tools:
            if self.command_exists(tool):
                self.print_success(f"{tool} is installed")
            else:
                missing_tools.append(tool)
                
        # Check for sslyze specifically
        try:
            import sslyze
            self.print_success("sslyze is installed")
        except ImportError:
            missing_tools.append("sslyze")
            
        if not missing_tools:
            self.print_success("All dependencies are installed!")
            return True
            
        self.print_warning(f"Missing tools: {', '.join(missing_tools)}")
        
        response = input("Would you like to install missing tools? (y/n): ").lower()
        if response == 'y':
            for tool in missing_tools:
                response = input(f"Install {tool}? (y/n): ").lower()
                if response == 'y':
                    if not self.install_tool(tool):
                        self.print_error(f"Failed to install {tool}")
                        return False
        else:
            self.print_error("Some tools are missing. Please install them manually.")
            return False
            
        return True
        
    def setup_scan_directory(self):
        """Create scan directory and change to it"""
        scan_path = Path(self.scan_dir)
        if not scan_path.exists():
            scan_path.mkdir(parents=True)
            self.print_success(f"Created scan directory: {self.scan_dir}")
            
        os.chdir(self.scan_dir)
        
    def run_nmap_web_scan(self):
        """Run NMap web server scan"""
        self.print_status("Starting NMap Web Server scan...")
        output_file = self.get_timestamped_filename("nmap-web-server")
        
        cmd = [
            "nmap", "-sC", "-sV", "-Pn", "-v1",
            "--script=banner,http-headers",
            "-oX", f"{output_file}.xml",
            "--stylesheet", "../Nmap-reports-files/nmap.xsl",
            self.domain
        ]
        
        exit_code, stdout, stderr = self.run_command(cmd)
        if exit_code == 0:
            # Try to convert XML to HTML with better error handling
            self._convert_xml_to_html(output_file)
            self.print_success(f"NMap web scan completed: {output_file}.xml")
        else:
            self.print_error(f"NMap web scan failed: {stderr}")
            
    def run_nmap_ssl_scan(self):
        """Run NMap SSL scan"""
        self.print_status("Starting NMap SSL scan...")
        output_file = self.get_timestamped_filename("nmap-ssl")
        
        cmd = [
            "nmap", "-v1", "-p", self.port,
            "--script=ssl-enum-ciphers",
            "-oX", f"{output_file}.xml",
            "--stylesheet", "../Nmap-reports-files/nmap.xsl",
            self.domain
        ]
        
        exit_code, stdout, stderr = self.run_command(cmd)
        if exit_code == 0:
            self._convert_xml_to_html(output_file)
            self.print_success(f"NMap SSL scan completed: {output_file}.xml")
        else:
            self.print_error(f"NMap SSL scan failed: {stderr}")
            
    def run_nmap_vulners_scan(self):
        """Run NMap Vulners scan"""
        self.print_status("Starting NMap Vulners scan...")
        output_file = self.get_timestamped_filename("nmap-vulners")
        
        cmd = [
            "nmap", "-sV", "-Pn", "-v1",
            "--script=vulners.nse",
            "-oX", f"{output_file}.xml",
            "--stylesheet", "../Nmap-reports-files/nmap.xsl",
            self.domain
        ]
        
        exit_code, stdout, stderr = self.run_command(cmd)
        if exit_code == 0:
            self._convert_xml_to_html(output_file)
            self.print_success(f"NMap Vulners scan completed: {output_file}.xml")
        else:
            self.print_error(f"NMap Vulners scan failed: {stderr}")
            
    def run_extended_port_scan(self):
        """Run extended port scan"""
        self.print_status("Starting extended port scan...")
        output_file = self.get_timestamped_filename("nmap-extended-ports")
        
        cmd = [
            "nmap", "-Pn", "-p-", "-vv",
            "-oX", f"{output_file}.xml",
            "--stylesheet", "../Nmap-reports-files/nmap.xsl",
            self.domain
        ]
        
        exit_code, stdout, stderr = self.run_command(cmd)
        if exit_code == 0:
            self._convert_xml_to_html(output_file)
            self.print_success(f"Extended port scan completed: {output_file}.xml")
        else:
            self.print_error(f"Extended port scan failed: {stderr}")
            
    def _convert_xml_to_html(self, output_file):
        """Convert XML to HTML with better error handling"""
        if not self.command_exists("java"):
            self.print_warning("Java not found. XML file created.")
            return
            
        # Try multiple approaches for XML to HTML conversion
        success = False
        
        # Method 1: Try with Xalan
        xalan_cmd = [
            "java", "-jar", "../Nmap-reports-files/xalan.jar",
            "-IN", f"{output_file}.xml",
            "-OUT", f"{output_file}.html"
        ]
        exit_code, stdout, stderr = self.run_command(xalan_cmd)
        if exit_code == 0:
            self.print_success(f"XML converted to HTML: {output_file}.html")
            success = True
        else:
            self.print_warning(f"Xalan conversion failed: {stderr}")
            
        # Method 2: Try with xsltproc if available
        if not success and self.command_exists("xsltproc"):
            xslt_cmd = [
                "xsltproc", "../Nmap-reports-files/nmap.xsl",
                f"{output_file}.xml"
            ]
            exit_code, stdout, stderr = self.run_command(xslt_cmd)
            if exit_code == 0:
                with open(f"{output_file}.html", 'w') as f:
                    f.write(stdout)
                self.print_success(f"XML converted to HTML using xsltproc: {output_file}.html")
                success = True
            else:
                self.print_warning(f"xsltproc conversion failed: {stderr}")
                
        # Method 3: Create a simple HTML report if all else fails
        if not success:
            self._create_simple_html_report(output_file)
            
    def _create_simple_html_report(self, output_file):
        """Create a simple HTML report from XML data"""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse the XML file
            tree = ET.parse(f"{output_file}.xml")
            root = tree.getroot()
            
            # Create simple HTML
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NMap Scan Results - {self.domain}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .port {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .open {{ background-color: #d4edda; }}
        .closed {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NMap Scan Results</h1>
        <p><strong>Target:</strong> {self.domain}</p>
        <p><strong>Scan Date:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
            
            # Extract port information
            for host in root.findall('.//host'):
                for port in host.findall('.//port'):
                    port_id = port.get('portid', 'Unknown')
                    protocol = port.get('protocol', 'Unknown')
                    state = port.find('state')
                    service = port.find('service')
                    
                    state_text = state.get('state', 'Unknown') if state is not None else 'Unknown'
                    service_name = service.get('name', 'Unknown') if service is not None else 'Unknown'
                    service_version = service.get('version', '') if service is not None else ''
                    
                    css_class = 'open' if state_text == 'open' else 'closed'
                    
                    html_content += f"""
    <div class="port {css_class}">
        <h3>Port {port_id}/{protocol}</h3>
        <p><strong>State:</strong> {state_text}</p>
        <p><strong>Service:</strong> {service_name}</p>
        {f'<p><strong>Version:</strong> {service_version}</p>' if service_version else ''}
    </div>
"""
            
            html_content += """
</body>
</html>
"""
            
            with open(f"{output_file}.html", 'w') as f:
                f.write(html_content)
                
            self.print_success(f"Simple HTML report created: {output_file}.html")
            
        except Exception as e:
            self.print_warning(f"Failed to create HTML report: {str(e)}")
            self.print_warning("XML file is available for manual processing.")
            
    def run_sslscan(self):
        """Run SSLScan"""
        self.print_status("Starting SSLScan...")
        output_file = f"{self.get_timestamped_filename('sslscan')}.txt"
        
        cmd = ["sslscan", "--no-failed", self.domain]
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            with open(output_file, 'w') as f:
                f.write(stdout)
            self.print_success(f"SSLScan completed: {output_file}")
        else:
            self.print_error(f"SSLScan failed: {stderr}")
            
    def run_sslyze(self):
        """Run SSLyze"""
        self.print_status("Starting SSLyze...")
        output_file = f"{self.get_timestamped_filename('sslyze')}.txt"
        
        # Use comprehensive SSL/TLS scan with specific flags
        cmd = [
            "python3", "-m", "sslyze",
            "--tlsv1_2", "--tlsv1_3", "--sslv3", "--tlsv1", "--tlsv1_1",
            "--heartbleed", "--certinfo", "--http_headers", "--reneg",
            "--openssl_ccs", "--robot", "--compression",
            f"{self.domain}:{self.port}"
        ]
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            with open(output_file, 'w') as f:
                f.write(stdout)
            self.print_success(f"SSLyze completed: {output_file}")
        else:
            self.print_error(f"SSLyze failed: {stderr}")
            
    def run_heartbleed_test(self):
        """Run Heartbleed test"""
        self.print_status("Starting Heartbleed test...")
        output_file = f"{self.get_timestamped_filename('nmap-ssl-heartbleed')}.txt"
        
        with open(output_file, 'w') as f:
            f.write("If vulnerable, you will see 'State: VULNERABLE' in the scan results\n")
            f.write("----------------------------------------------------------\n")
            
        cmd = ["nmap", "-p", "443", "--script", "ssl-heartbleed", self.domain]
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            with open(output_file, 'a') as f:
                f.write(stdout)
            self.print_success(f"Heartbleed test completed: {output_file}")
        else:
            self.print_error(f"Heartbleed test failed: {stderr}")
            
    def run_dns_enumeration(self):
        """Run DNS enumeration"""
        self.print_status("Starting DNS enumeration...")
        
        # Dig record types
        output_file = f"{self.get_timestamped_filename('dig-record-types')}.txt"
        with open(output_file, 'w') as f:
            f.write("View all the record types (A, MX, NS, etc.)\n")
            f.write("------------------------------------------------------\n")
            
        cmd = ["dig", self.domain, "-t", "any"]
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            with open(output_file, 'a') as f:
                f.write(stdout)
            self.print_success(f"DNS record types completed: {output_file}")
        else:
            self.print_error(f"DNS record types failed: {stderr}")
            
        # Zone transfer test
        zone_file = f"{self.get_timestamped_filename('dig-zone-transfer')}.txt"
        with open(zone_file, 'w') as f:
            f.write("Request to get a copy of the zone transfer from the primary server\n")
            f.write("(Transfer failed. means the application PASS the test)\n")
            f.write("-----------------------------------------------------\n")
            
        cmd = ["dig", self.domain, "-t", "axfr"]
        exit_code, stdout, stderr = self.run_command(cmd)
        
        if exit_code == 0:
            with open(zone_file, 'a') as f:
                f.write(stdout)
            self.print_success(f"Zone transfer test completed: {zone_file}")
        else:
            self.print_error(f"Zone transfer test failed: {stderr}")
            
        # DNS brute force
        self.print_status("Starting DNS brute force scan (this may take several minutes)...")
        brute_file = f"{self.get_timestamped_filename('nmap-DNS-brute')}.txt"
        with open(brute_file, 'w') as f:
            f.write("Nmap brute force subdomain enumeration\n")
            f.write("------------------------------------------------------\n")
            
        cmd = ["nmap", "--script", "dns-brute", self.domain]
        exit_code, stdout, stderr = self.run_command_with_timeout(cmd)
        
        if exit_code == 0:
            with open(brute_file, 'a') as f:
                f.write(stdout)
            self.print_success(f"DNS brute force completed: {brute_file}")
        else:
            self.print_error(f"DNS brute force failed: {stderr}")
            
        self.print_success("DNS enumeration completed! All three tests finished.")
            
    def run_nikto(self):
        """Run Nikto"""
        self.print_status("Starting Nikto...")
        output_file = f"{self.get_timestamped_filename('nikto')}.html"
        
        cmd = [
            "nikto", "-C", "all", "-ssl", self.port,
            "-Format", "HTML", "-output", output_file,
            "-Save", "niktosave", "-host", self.domain
        ]
        
        exit_code, stdout, stderr = self.run_command(cmd)
        if exit_code == 0:
            self.print_success(f"Nikto completed: {output_file}")
        else:
            self.print_error(f"Nikto failed: {stderr}")
            
    def show_menu(self):
        """Show the main menu"""
        print("\n" + "=" * 50)
        print("           WebPaladin Menu")
        print("=" * 50)
        print(f"Domain: {self.domain}")
        print(f"Port: {self.port}")
        print("=" * 50)
        print("1.  NMap Web Server Scan")
        print("2.  NMap SSL Scan")
        print("3.  NMap Vulners Scan")
        print("4.  Extended Port Scan")
        print("5.  SSLScan")
        print("6.  SSLyze")
        print("7.  Heartbleed Test")
        print("8.  DNS Enumeration")
        print("9.  Nikto")
        print("10. Run All Scans")
        print("11. Change Domain/Port")
        print("12. Check Dependencies")
        print("0.  Exit")
        print("=" * 50)
        
    def get_user_selection(self) -> str:
        """Get user selection from menu"""
        return input("Enter your choice (0-12): ").strip()
        
    def run_selected_scan(self, choice: str):
        """Run the selected scan based on user choice"""
        if choice == "1":
            self.run_nmap_web_scan()
        elif choice == "2":
            self.run_nmap_ssl_scan()
        elif choice == "3":
            self.run_nmap_vulners_scan()
        elif choice == "4":
            self.run_extended_port_scan()
        elif choice == "5":
            self.run_sslscan()
        elif choice == "6":
            self.run_sslyze()
        elif choice == "7":
            self.run_heartbleed_test()
        elif choice == "8":
            self.run_dns_enumeration()
        elif choice == "9":
            self.run_nikto()
        elif choice == "10":
            self.print_status("Running all scans...")
            self.run_nmap_web_scan()
            self.run_nmap_ssl_scan()
            self.run_nmap_vulners_scan()
            self.run_extended_port_scan()
            self.run_sslscan()
            self.run_sslyze()
            self.run_heartbleed_test()
            self.run_dns_enumeration()
            self.run_nikto()
            self.print_success("All scans completed!")
        elif choice == "11":
            self.get_domain_and_port()
        elif choice == "12":
            self.check_dependencies()
        elif choice == "0":
            self.print_success("Goodbye!")
            sys.exit(0)
        else:
            self.print_error("Invalid choice. Please try again.")
            
    def get_domain_and_port(self):
        """Get domain and port from user"""
        print()
        domain = input("Enter domain to scan: ").strip()
        
        if not domain:
            self.print_error("Domain cannot be empty!")
            return False
            
        port = input("Enter port (default: 443): ").strip()
        if port:
            self.port = port
            
        self.domain = domain
        self.print_success(f"Target set to: {self.domain}:{self.port}")
        return True
        
    def main(self):
        """Main function"""
        print("=" * 50)
        print("        WebPaladin - Python Version")
        print("=" * 50)
        print("Author: Nestor Torres (@n3stortorres)")
        print("For support: X (Twitter) @n3stortorres or GitHub Issues")
        print("=" * 50)
        
        # Check dependencies first
        if not self.check_dependencies():
            self.print_error("Dependency check failed. Exiting.")
            sys.exit(1)
            
        # Get domain and port
        if not self.get_domain_and_port():
            sys.exit(1)
            
        # Setup scan directory
        self.setup_scan_directory()
        
        # Main loop
        while True:
            self.show_menu()
            choice = self.get_user_selection()
            self.run_selected_scan(choice)
            
            print()
            input("Press Enter to continue...")

    def get_timestamped_filename(self, base_name: str) -> str:
        """Generate a filename with date prefix and numbering for duplicates"""
        counter = 0
        
        while True:
            filename = f"{self.timestamp}-{base_name}-{counter}"
            if not os.path.exists(f"{filename}.xml") and not os.path.exists(f"{filename}.txt") and not os.path.exists(f"{filename}.html"):
                return filename
            counter += 1

def main():
    """Entry point"""
    parser = argparse.ArgumentParser(description="Web Server Scanner")
    parser.add_argument("domain", nargs="?", help="Domain to scan")
    parser.add_argument("port", nargs="?", default="443", help="Port to scan (default: 443)")
    
    args = parser.parse_args()
    
    scanner = WebPaladin()
    
    if args.domain:
        scanner.domain = args.domain
        scanner.port = args.port
        scanner.print_status(f"Using command line arguments: {scanner.domain}:{scanner.port}")
        
        # Check dependencies first
        if not scanner.check_dependencies():
            scanner.print_error("Dependency check failed. Exiting.")
            sys.exit(1)
            
        # Setup scan directory
        scanner.setup_scan_directory()
        
        # Show menu directly without asking for domain again
        while True:
            scanner.show_menu()
            choice = scanner.get_user_selection()
            scanner.run_selected_scan(choice)
            
            print()
            input("Press Enter to continue...")
    else:
        # No command line arguments, run interactive mode
        scanner.main()

if __name__ == "__main__":
    main() 