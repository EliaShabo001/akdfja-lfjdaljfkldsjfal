from flask import Flask, jsonify
from threading import Thread
import socket
import os
import time
import requests
from datetime import datetime

app = Flask(__name__)

# Global variables to track bot status
bot_start_time = datetime.now()
last_keepalive_ping = datetime.now()
keepalive_count = 0

@app.route('/')
def home():
    return "🤖 Telegram Quiz Bot is running! 🎓"

@app.route('/health')
def health():
    """Detailed health check endpoint"""
    uptime = datetime.now() - bot_start_time
    return jsonify({
        "status": "healthy",
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_formatted": str(uptime),
        "last_keepalive": last_keepalive_ping.isoformat(),
        "keepalive_count": keepalive_count,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/keep-alive')
def keep_alive_endpoint():
    """Keep-alive endpoint for external monitoring"""
    global last_keepalive_ping, keepalive_count
    last_keepalive_ping = datetime.now()
    keepalive_count += 1

    return jsonify({
        "status": "alive",
        "message": "Bot is running",
        "ping_count": keepalive_count,
        "timestamp": last_keepalive_ping.isoformat()
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return "pong"

def find_free_port():
    """Find a free port to use"""
    # For Cloud Run, use the PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    return port

def run():
    port = find_free_port()
    print(f"🌐 Webserver starting on http://0.0.0.0:{port}")
    print(f"🔗 Health check: http://localhost:{port}/health")
    print(f"💓 Keep-alive: http://localhost:{port}/keep-alive")
    app.run(host="0.0.0.0", port=port, debug=False)

def keep_alive():
    """Start the Flask webserver in a separate thread"""
    t = Thread(target=run, daemon=True)
    t.start()

def self_ping_loop():
    """Self-ping loop to keep the service alive"""
    global last_keepalive_ping

    # Wait a bit for the server to start
    time.sleep(10)

    port = find_free_port()
    base_url = f"http://localhost:{port}"

    while True:
        try:
            # Self-ping every 5 minutes
            response = requests.get(f"{base_url}/keep-alive", timeout=10)
            if response.status_code == 200:
                print(f"✅ Self-ping successful at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"⚠️ Self-ping returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Self-ping failed: {e}")

        # Wait 5 minutes before next ping
        time.sleep(300)

def start_self_ping():
    """Start self-ping in a separate thread"""
    t = Thread(target=self_ping_loop, daemon=True)
    t.start()
    print("🔄 Self-ping loop started (every 5 minutes)")