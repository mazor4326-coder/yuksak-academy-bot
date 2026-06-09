import sys
import os
import threading
import time
import webview

# Add the directory containing this script to the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a dummy public IP to resolve local network IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# Import the Flask application
try:
    from app import app
except ImportError:
    # If app.py is not in current path, look for it in local path
    sys.path.append(os.path.join(current_dir, 'website'))
    from app import app

def run_flask_backend():
    """Runs the Flask web server in a silent production-like mode."""
    # Run Flask on all network interfaces to allow connections from mobile devices on local network
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    local_ip = get_local_ip()
    print("==================================================================")
    print("🚀 YUKSAK ACADEMY Cyber Control Center started!")
    print(f"💻 Desktop Local Admin Dashboard: http://127.0.0.1:5000/admin")
    print(f"📱 Mobile Local Connection URL:    http://{local_ip}:5000")
    print("==================================================================")

    # 1. Start the Flask application in a background daemon thread
    backend_thread = threading.Thread(target=run_flask_backend, daemon=True)
    backend_thread.start()
    
    # 2. Wait briefly to ensure the Flask server has bound to port 5000
    time.sleep(1.2)
    
    # 3. Create and launch the PyWebView window pointing directly to admin dashboard
    # Log in automatically using Basic Auth credentials
    webview.create_window(
        title='YUKSAK ACADEMY | Cyber Command Center',
        url='http://aziz67876578:67596854903876584@127.0.0.1:5000/admin',
        width=1280,
        height=800,
        min_size=(1024, 768),
        resizable=True,
        background_color='#020204'
    )
    
    # Start the GUI loop
    webview.start()

