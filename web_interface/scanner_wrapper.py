#!/usr/bin/env python3
"""
WebPaladin Scanner Wrapper
Non-interactive wrapper for WebPaladin scanner

Author: Nestor Torres (@n3stortorres)
For questions or support, contact me on X (Twitter) @n3stortorres
or open an issue on GitHub.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies_noninteractive():
    """Check dependencies without interactive prompts"""
    tools = ["nmap", "sslscan", "nikto", "python3", "dig", "java"]
    missing_tools = []
    
    for tool in tools:
        if shutil.which(tool):
            print(f"[SUCCESS] {tool} is installed")
        else:
            missing_tools.append(tool)
            print(f"[WARNING] {tool} is missing")
    
    # Check for sslyze specifically
    try:
        import sslyze
        print("[SUCCESS] sslyze is installed")
    except ImportError:
        missing_tools.append("sslyze")
        print("[WARNING] sslyze is missing")
    
    if missing_tools:
        print(f"[WARNING] Missing tools: {', '.join(missing_tools)}")
        print("[INFO] Continuing with available tools...")
        return True
    
    print("[SUCCESS] All dependencies are installed!")
    return True

def run_basic_scans(domain, port):
    """Run basic scans that don't require missing tools"""
    print(f"[INFO] Running basic scans on {domain}:{port}")
    
    # Create scan directory
    scan_dir = Path("scan_results")
    scan_dir.mkdir(exist_ok=True)
    os.chdir(scan_dir)
    
    # Run NMap scan if available
    if shutil.which("nmap"):
        print("[INFO] Running NMap scan...")
        try:
            cmd = [
                "nmap", "-sC", "-sV", "-Pn", "-v1",
                "--script=banner,http-headers",
                "-oX", f"nmap-web-server.xml",
                domain
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print("[SUCCESS] NMap scan completed")
            else:
                print(f"[ERROR] NMap scan failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[ERROR] NMap scan timed out")
        except Exception as e:
            print(f"[ERROR] NMap scan error: {e}")
    
    # Run SSL scan if available
    if shutil.which("sslscan"):
        print("[INFO] Running SSLScan...")
        try:
            cmd = ["sslscan", "--no-failed", domain]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                with open("sslscan.txt", "w") as f:
                    f.write(result.stdout)
                print("[SUCCESS] SSLScan completed")
            else:
                print(f"[ERROR] SSLScan failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[ERROR] SSLScan timed out")
        except Exception as e:
            print(f"[ERROR] SSLScan error: {e}")
    
    # Run Nikto scan if available
    if shutil.which("nikto"):
        print("[INFO] Running Nikto scan...")
        try:
            cmd = ["nikto", "-h", domain, "-p", port, "-o", "nikto.txt"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print("[SUCCESS] Nikto scan completed")
            else:
                print(f"[ERROR] Nikto scan failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[ERROR] Nikto scan timed out")
        except Exception as e:
            print(f"[ERROR] Nikto scan error: {e}")
    
    # Run SSLyze if available
    try:
        import sslyze
        print("[INFO] Running SSLyze scan...")
        try:
            cmd = [
                "python3", "-m", "sslyze",
                "--tlsv1_2", "--tlsv1_3",
                "--heartbleed", "--certinfo", "--http_headers",
                f"{domain}:{port}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                with open("sslyze.txt", "w") as f:
                    f.write(result.stdout)
                print("[SUCCESS] SSLyze scan completed")
            else:
                print(f"[ERROR] SSLyze scan failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[ERROR] SSLyze scan timed out")
        except Exception as e:
            print(f"[ERROR] SSLyze scan error: {e}")
    except ImportError:
        print("[WARNING] SSLyze not available")
    
    print("[SUCCESS] Basic scans completed")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("[ERROR] Domain is required")
        print("Usage: python3 scanner_wrapper.py <domain> [port]")
        sys.exit(1)
    
    domain = sys.argv[1]
    port = sys.argv[2] if len(sys.argv) > 2 else "443"
    
    print(f"[INFO] Starting non-interactive scan of {domain}:{port}")
    
    # Check dependencies
    if not check_dependencies_noninteractive():
        print("[ERROR] Dependency check failed")
        sys.exit(1)
    
    # Run basic scans
    run_basic_scans(domain, port)
    
    print("[SUCCESS] Scan completed successfully")

if __name__ == "__main__":
    main() 