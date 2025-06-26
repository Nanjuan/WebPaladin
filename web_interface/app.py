#!/usr/bin/env python3
"""
WebPaladin Web Interface
Flask-based web interface for WebPaladin scanner

Author: Nestor Torres (@n3stortorres)
For questions or support, contact me on X (Twitter) @n3stortorres
or open an issue on GitHub.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import json
import threading
import time
from datetime import datetime
from pathlib import Path

# Create Flask app with correct template and static folder paths
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
CORS(app)

# Configuration
SCAN_RESULTS_DIR = "/app/scan_results"
LOGS_DIR = "/app/logs"

# Ensure directories exist
os.makedirs(SCAN_RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Global variable to track scan status
scan_status = {
    "running": False,
    "current_scan": None,
    "progress": 0,
    "message": ""
}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start a new scan"""
    global scan_status
    
    if scan_status["running"]:
        return jsonify({"error": "Scan already in progress"}), 400
    
    data = request.get_json()
    domain = data.get('domain', '').strip()
    port = data.get('port', '443').strip()
    scan_type = data.get('scan_type', 'all')
    
    if not domain:
        return jsonify({"error": "Domain is required"}), 400
    
    # Start scan in background thread
    scan_status["running"] = True
    scan_status["current_scan"] = {
        "domain": domain,
        "port": port,
        "scan_type": scan_type,
        "start_time": datetime.now().isoformat()
    }
    scan_status["progress"] = 0
    scan_status["message"] = "Starting scan..."
    
    thread = threading.Thread(target=run_scan_background, args=(domain, port, scan_type))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "message": "Scan started",
        "scan_id": scan_status["current_scan"]["start_time"]
    })

@app.route('/api/scan/status')
def get_scan_status():
    """Get current scan status"""
    return jsonify(scan_status)

@app.route('/api/results')
def get_results():
    """Get list of scan results"""
    try:
        results = []
        scan_dir = Path(SCAN_RESULTS_DIR)
        
        if scan_dir.exists():
            for file_path in scan_dir.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    results.append({
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": file_path.suffix
                    })
        
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/results/<filename>')
def get_result_file(filename):
    """Download a specific result file"""
    try:
        file_path = Path(SCAN_RESULTS_DIR) / filename
        if file_path.exists() and file_path.is_file():
            return send_from_directory(SCAN_RESULTS_DIR, filename)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_scan_background(domain, port, scan_type):
    """Run scan in background thread"""
    global scan_status
    
    try:
        scan_status["message"] = "Checking dependencies..."
        scan_status["progress"] = 10
        
        # Use the scanner wrapper instead of the original scanner
        scanner_path = "/app/web_interface/scanner_wrapper.py"
        if not os.path.exists(scanner_path):
            scan_status["message"] = "Scanner wrapper not found"
            scan_status["progress"] = 100
            scan_status["running"] = False
            return
        
        scan_status["message"] = f"Running {scan_type} scan on {domain}:{port}..."
        scan_status["progress"] = 30
        
        # Set up environment for non-interactive execution
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        env['TERM'] = 'dumb'  # Disable color output
        env['NONINTERACTIVE'] = '1'  # Custom flag for non-interactive mode
        
        # Run the scanner wrapper with proper environment setup
        cmd = ["python3", scanner_path, domain, port]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/app",
            env=env,
            stdin=subprocess.DEVNULL  # Prevent interactive prompts
        )
        
        scan_status["progress"] = 50
        scan_status["message"] = "Scan in progress..."
        
        # Wait for completion with timeout
        try:
            stdout, stderr = process.communicate(timeout=1800)  # 30 minute timeout
            
            if process.returncode == 0:
                scan_status["message"] = "Scan completed successfully"
                scan_status["progress"] = 100
            else:
                error_msg = stderr if stderr else stdout
                scan_status["message"] = f"Scan failed: {error_msg}"
                scan_status["progress"] = 100
                
        except subprocess.TimeoutExpired:
            process.kill()
            scan_status["message"] = "Scan timed out after 30 minutes"
            scan_status["progress"] = 100
            
    except Exception as e:
        scan_status["message"] = f"Error: {str(e)}"
        scan_status["progress"] = 100
    finally:
        scan_status["running"] = False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False) 