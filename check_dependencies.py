#!/usr/bin/env python3
"""
Dependency Checker for Web Server Scanner
Checks and installs all required tools based on the operating system
"""

import os
import sys
import subprocess
import platform
import shutil
from typing import List, Dict, Tuple

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class DependencyChecker:
    def __init__(self):
        self.os_type = self.detect_os()
        self.tools = {
            "nmap": {
                "description": "Network mapper for port scanning",
                "linux": {"apt": "nmap", "yum": "nmap", "dnf": "nmap"},
                "macos": {"brew": "nmap"},
                "windows": {"manual": "Download from https://nmap.org/"}
            },
            "sslscan": {
                "description": "SSL/TLS scanner",
                "linux": {"apt": "sslscan", "yum": "sslscan", "dnf": "sslscan"},
                "macos": {"brew": "sslscan"},
                "windows": {"manual": "Download from https://github.com/rbsec/sslscan"}
            },
            "nikto": {
                "description": "Web server scanner",
                "linux": {"apt": "nikto", "yum": "nikto", "dnf": "nikto"},
                "macos": {"brew": "nikto"},
                "windows": {"manual": "Download from https://github.com/sullo/nikto"}
            },
            "python3": {
                "description": "Python 3 interpreter",
                "linux": {"apt": "python3 python3-pip", "yum": "python3 python3-pip", "dnf": "python3 python3-pip"},
                "macos": {"brew": "python3"},
                "windows": {"manual": "Download from https://python.org/"}
            },
            "java": {
                "description": "Java Runtime Environment",
                "linux": {"apt": "openjdk-11-jdk", "yum": "java-11-openjdk", "dnf": "java-11-openjdk"},
                "macos": {"brew": "openjdk"},
                "windows": {"manual": "Download from https://adoptium.net/"}
            },
            "dig": {
                "description": "DNS lookup utility",
                "linux": {"apt": "dnsutils", "yum": "bind-utils", "dnf": "bind-utils"},
                "macos": {"brew": "bind"},
                "windows": {"manual": "Part of BIND or use nslookup"}
            },
            "sslyze": {
                "description": "SSL/TLS scanner (Python package)",
                "linux": {"pip": "sslyze"},
                "macos": {"pip": "sslyze"},
                "windows": {"pip": "sslyze"}
            }
        }
        
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
        
    def run_command(self, command: List[str]) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, and stderr"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
            
    def get_package_manager(self) -> str:
        """Get the available package manager for the current OS"""
        if self.os_type == "linux":
            if self.command_exists("apt-get"):
                return "apt"
            elif self.command_exists("yum"):
                return "yum"
            elif self.command_exists("dnf"):
                return "dnf"
            else:
                return "unknown"
        elif self.os_type == "macos":
            if self.command_exists("brew"):
                return "brew"
            else:
                return "unknown"
        else:
            return "unknown"
            
    def install_tool(self, tool: str) -> bool:
        """Install a tool"""
        if tool not in self.tools:
            self.print_error(f"Unknown tool: {tool}")
            return False
            
        tool_info = self.tools[tool]
        self.print_status(f"Installing {tool} ({tool_info['description']})...")
        
        if self.os_type not in tool_info:
            self.print_error(f"No installation method for {tool} on {self.os_type}")
            return False
            
        os_info = tool_info[self.os_type]
        
        if "pip" in os_info:
            # Install via pip
            cmd = ["pip3", "install", os_info["pip"]]
            exit_code, stdout, stderr = self.run_command(cmd)
            if exit_code == 0:
                self.print_success(f"{tool} installed successfully!")
                return True
            else:
                self.print_error(f"Failed to install {tool}: {stderr}")
                return False
                
        elif "manual" in os_info:
            self.print_warning(f"Manual installation required for {tool}")
            print(f"Please visit: {os_info['manual']}")
            return False
            
        else:
            # Use package manager
            pkg_mgr = self.get_package_manager()
            if pkg_mgr == "unknown":
                self.print_error("No supported package manager found")
                return False
                
            if pkg_mgr not in os_info:
                self.print_error(f"No installation method for {tool} using {pkg_mgr}")
                return False
                
            package = os_info[pkg_mgr]
            
            if pkg_mgr == "apt":
                cmd = ["sudo", "apt-get", "update"]
                exit_code, stdout, stderr = self.run_command(cmd)
                if exit_code != 0:
                    self.print_error(f"Failed to update package list: {stderr}")
                    return False
                    
                cmd = ["sudo", "apt-get", "install", "-y"] + package.split()
                exit_code, stdout, stderr = self.run_command(cmd)
                if exit_code == 0:
                    self.print_success(f"{tool} installed successfully!")
                    return True
                else:
                    self.print_error(f"Failed to install {tool}: {stderr}")
                    return False
                    
            elif pkg_mgr in ["yum", "dnf"]:
                cmd = ["sudo", pkg_mgr, "install", "-y"] + package.split()
                exit_code, stdout, stderr = self.run_command(cmd)
                if exit_code == 0:
                    self.print_success(f"{tool} installed successfully!")
                    return True
                else:
                    self.print_error(f"Failed to install {tool}: {stderr}")
                    return False
                    
            elif pkg_mgr == "brew":
                cmd = ["brew", "install"] + package.split()
                exit_code, stdout, stderr = self.run_command(cmd)
                if exit_code == 0:
                    self.print_success(f"{tool} installed successfully!")
                    return True
                else:
                    self.print_error(f"Failed to install {tool}: {stderr}")
                    return False
                    
        return False
        
    def check_tool(self, tool: str) -> bool:
        """Check if a tool is installed and working"""
        if tool == "sslyze":
            # Check Python package
            try:
                import sslyze
                return True
            except ImportError:
                return False
        else:
            return self.command_exists(tool)
            
    def check_all_dependencies(self) -> Dict[str, bool]:
        """Check all dependencies and return status"""
        results = {}
        
        self.print_status("Checking all dependencies...")
        print()
        
        for tool, info in self.tools.items():
            if self.check_tool(tool):
                self.print_success(f"{tool} ✓ ({info['description']})")
                results[tool] = True
            else:
                self.print_error(f"{tool} ✗ ({info['description']})")
                results[tool] = False
                
        return results
        
    def install_missing_dependencies(self, missing_tools: List[str]) -> bool:
        """Install missing dependencies"""
        if not missing_tools:
            return True
            
        print()
        self.print_warning(f"Missing tools: {', '.join(missing_tools)}")
        
        response = input("Would you like to install missing tools? (y/n): ").lower()
        if response != 'y':
            return False
            
        success_count = 0
        for tool in missing_tools:
            print()
            response = input(f"Install {tool}? (y/n): ").lower()
            if response == 'y':
                if self.install_tool(tool):
                    success_count += 1
                    
        self.print_status(f"Successfully installed {success_count}/{len(missing_tools)} tools")
        return success_count == len(missing_tools)
        
    def show_installation_guide(self):
        """Show installation guide for the current OS"""
        print("\n" + "=" * 60)
        print("           INSTALLATION GUIDE")
        print("=" * 60)
        print(f"Operating System: {self.os_type.upper()}")
        print(f"Package Manager: {self.get_package_manager().upper()}")
        print("=" * 60)
        
        for tool, info in self.tools.items():
            print(f"\n{tool.upper()}: {info['description']}")
            if self.os_type in info:
                os_info = info[self.os_type]
                if "manual" in os_info:
                    print(f"  Manual installation: {os_info['manual']}")
                else:
                    for method, package in os_info.items():
                        if method == "pip":
                            print(f"  pip3 install {package}")
                        else:
                            print(f"  {method}: {package}")
            else:
                print(f"  No installation method available for {self.os_type}")
                
    def main(self):
        """Main function"""
        print("=" * 60)
        print("        Web Server Scanner - Dependency Checker")
        print("=" * 60)
        print(f"Operating System: {self.os_type}")
        print(f"Package Manager: {self.get_package_manager()}")
        print("=" * 60)
        
        # Check all dependencies
        results = self.check_all_dependencies()
        
        # Find missing tools
        missing_tools = [tool for tool, installed in results.items() if not installed]
        
        if not missing_tools:
            self.print_success("All dependencies are installed and ready!")
            return True
        else:
            print()
            self.print_warning(f"Found {len(missing_tools)} missing tools")
            
            # Try to install missing tools
            if self.install_missing_dependencies(missing_tools):
                self.print_success("All dependencies are now installed!")
                return True
            else:
                self.print_error("Some dependencies could not be installed automatically")
                print()
                self.show_installation_guide()
                return False

def main():
    """Entry point"""
    checker = DependencyChecker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--guide":
        checker.show_installation_guide()
    else:
        success = checker.main()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 