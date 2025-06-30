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
import time
from pathlib import Path
from datetime import datetime

def get_timestamped_filename(base_name, extension):
    """Generate a filename with date prefix and numbering for duplicates"""
    timestamp = datetime.now().strftime("%Y%m%d")
    counter = 0
    
    while True:
        filename = f"{timestamp}-{base_name}-{counter}.{extension}"
        if not os.path.exists(filename):
            return filename
        counter += 1

def command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def run_command(cmd, capture_output=True, timeout=300):
    """Run a command and return exit code, stdout, and stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return -1, "", str(e)

def convert_xml_to_html(output_file, domain):
    """Convert XML to HTML with better error handling"""
    if not command_exists("java"):
        print("[WARNING] Java not found. XML file created.")
        return
        
    # Try multiple approaches for XML to HTML conversion
    success = False
    
    # Method 1: Try with Xalan
    xalan_cmd = [
        "java", "-jar", "../Nmap-reports-files/xalan.jar",
        "-IN", f"{output_file}.xml",
        "-OUT", f"{output_file}.html"
    ]
    exit_code, stdout, stderr = run_command(xalan_cmd)
    if exit_code == 0:
        print(f"[SUCCESS] XML converted to HTML: {output_file}.html")
        success = True
    else:
        print(f"[WARNING] Xalan conversion failed: {stderr}")
        
    # Method 2: Try with xsltproc if available
    if not success and command_exists("xsltproc"):
        xslt_cmd = [
            "xsltproc", "../Nmap-reports-files/nmap.xsl",
            f"{output_file}.xml"
        ]
        exit_code, stdout, stderr = run_command(xslt_cmd)
        if exit_code == 0:
            with open(f"{output_file}.html", 'w') as f:
                f.write(stdout)
            print(f"[SUCCESS] XML converted to HTML using xsltproc: {output_file}.html")
            success = True
        else:
            print(f"[WARNING] xsltproc conversion failed: {stderr}")
            
    # Method 3: Create a simple HTML report if all else fails
    if not success:
        create_simple_html_report(output_file, domain)

def create_simple_html_report(output_file, domain):
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
    <title>NMap Scan Results - {domain}</title>
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
        <p><strong>Target:</strong> {domain}</p>
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
            
        print(f"[SUCCESS] Simple HTML report created: {output_file}.html")
        
    except Exception as e:
        print(f"[WARNING] Failed to create HTML report: {str(e)}")
        print("[WARNING] XML file is available for manual processing.")

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
            output_file = get_timestamped_filename("nmap-web-server", "xml")
            # Remove the .xml extension for the base filename
            base_output_file = output_file.replace(".xml", "")
            
            cmd = [
                "nmap", "-sC", "-sV", "-Pn", "-v1",
                "--script=banner,http-headers",
                "-oX", output_file,
                "--stylesheet", "../Nmap-reports-files/nmap.xsl",
                domain
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"[SUCCESS] NMap scan completed: {output_file}")
                # Convert XML to HTML
                convert_xml_to_html(base_output_file, domain)
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
            output_file = get_timestamped_filename("sslscan", "txt")
            cmd = ["sslscan", "--no-failed", domain]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                with open(output_file, "w") as f:
                    f.write(result.stdout)
                print(f"[SUCCESS] SSLScan completed: {output_file}")
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
            output_file = get_timestamped_filename("nikto", "txt")
            cmd = ["nikto", "-h", domain, "-p", port, "-o", output_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"[SUCCESS] Nikto scan completed: {output_file}")
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
            output_file = get_timestamped_filename("sslyze", "txt")
            cmd = [
                "python3", "-m", "sslyze",
                "--tlsv1_2", "--tlsv1_3",
                "--heartbleed", "--certinfo", "--http_headers",
                f"{domain}:{port}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                with open(output_file, "w") as f:
                    f.write(result.stdout)
                print(f"[SUCCESS] SSLyze scan completed: {output_file}")
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