#!/usr/bin/env python3
"""
WebPaladin Launcher
Choose between shell script and Python versions

Author: Nestor Torres (@n3stortorres)
For questions or support, contact me on X (Twitter) @n3stortorres
or open an issue on GitHub.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("           WebPaladin Launcher")
    print("=" * 60)
    print("Author: Nestor Torres (@n3stortorres)")
    print("For support: X (Twitter) @n3stortorres or GitHub Issues")
    print("=" * 60)
    print("Choose your preferred version:")
    print("=" * 60)

def check_file_exists(filename):
    """Check if a file exists"""
    return os.path.exists(filename)

def run_shell_version(domain=None, port=None):
    """Run the shell script version"""
    cmd = ["./web_server_scan.sh"]
    if domain:
        cmd.append(domain)
        if port:
            cmd.append(port)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running shell script: {e}")
        return False
    except FileNotFoundError:
        print("Shell script not found or not executable")
        return False
    return True

def run_python_version(domain=None, port=None):
    """Run the Python version"""
    cmd = [sys.executable, "web_server_scan.py"]
    if domain:
        cmd.append(domain)
        if port:
            cmd.append(port)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Python script: {e}")
        return False
    except FileNotFoundError:
        print("Python script not found")
        return False
    return True

def main():
    """Main launcher function"""
    print_banner()
    
    # Check which versions are available
    shell_available = check_file_exists("web_server_scan.sh")
    python_available = check_file_exists("web_server_scan.py")
    
    if not shell_available and not python_available:
        print("❌ No scanner versions found!")
        print("Please ensure web_server_scan.sh or web_server_scan.py exists")
        sys.exit(1)
    
    print("Available versions:")
    if shell_available:
        print("1. Shell Script Version (web_server_scan.sh)")
    if python_available:
        print("2. Python Version (web_server_scan.py)")
    print("3. Check Dependencies")
    print("0. Exit")
    print("=" * 60)
    
    while True:
        choice = input("Enter your choice: ").strip()
        
        if choice == "0":
            print("Goodbye!")
            sys.exit(0)
        elif choice == "1" and shell_available:
            domain = input("Enter domain (optional): ").strip()
            port = None
            if domain:
                port = input("Enter port (optional, default 443): ").strip()
                if not port:
                    port = "443"
            run_shell_version(domain if domain else None, port)
            break
        elif choice == "2" and python_available:
            domain = input("Enter domain (optional): ").strip()
            port = None
            if domain:
                port = input("Enter port (optional, default 443): ").strip()
                if not port:
                    port = "443"
            run_python_version(domain if domain else None, port)
            break
        elif choice == "3":
            print("Checking dependencies...")
            try:
                subprocess.run([sys.executable, "check_dependencies.py"], check=True)
            except subprocess.CalledProcessError:
                print("Error running dependency checker")
            except FileNotFoundError:
                print("Dependency checker not found")
            print()
            print_banner()
            if shell_available:
                print("1. Shell Script Version (web_server_scan.sh)")
            if python_available:
                print("2. Python Version (web_server_scan.py)")
            print("3. Check Dependencies")
            print("0. Exit")
            print("=" * 60)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 