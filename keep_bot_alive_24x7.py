#!/usr/bin/env python3
"""
24/7 Bot Keep-Alive Script for Google Cloud Run (No gcloud required)
This script keeps your Telegram bot running continuously by:
1. Starting both teacher and student bots
2. Running an HTTP server to prevent Cloud Run shutdown
3. Self-pinging every 5 minutes to stay alive
4. Auto-restarting bots if they crash
5. External ping capability to prevent scale-to-zero
"""

import os
import sys
import threading
import time
import subprocess
import signal
import requests
from datetime import datetime
from flask import Flask, jsonify

class BotKeepAlive24x7:
    def __init__(self):
        self.teacher_process = None
        self.student_process = None
        self.flask_app = None
        self.running = True
        self.restart_count = 0
        self.start_time = datetime.now()
        self.last_ping = datetime.now()
        self.ping_count = 0
        self.port = int(os.environ.get('PORT', 8080))
        
        # Create Flask app
        self.create_flask_app()
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def create_flask_app(self):
        """Create Flask app with keep-alive endpoints"""
        self.flask_app = Flask(__name__)
        
        @self.flask_app.route('/')
        def home():
            return "🤖 Telegram Quiz Bot is running 24/7! 🎓"
        
        @self.flask_app.route('/health')
        def health():
            uptime = datetime.now() - self.start_time
            teacher_alive = self.teacher_process and self.teacher_process.poll() is None
            student_alive = self.student_process and self.student_process.poll() is None
            
            return jsonify({
                "status": "healthy" if teacher_alive and student_alive else "partial",
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_formatted": str(uptime),
                "teacher_bot_running": teacher_alive,
                "student_bot_running": student_alive,
                "restart_count": self.restart_count,
                "last_ping": self.last_ping.isoformat(),
                "ping_count": self.ping_count,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.flask_app.route('/keep-alive')
        def keep_alive():
            self.last_ping = datetime.now()
            self.ping_count += 1
            
            return jsonify({
                "status": "alive",
                "message": "Bot is running 24/7",
                "ping_count": self.ping_count,
                "timestamp": self.last_ping.isoformat(),
                "uptime": str(datetime.now() - self.start_time)
            })
        
        @self.flask_app.route('/ping')
        def ping():
            return "pong"
        
        @self.flask_app.route('/restart-bots')
        def restart_bots_endpoint():
            """Emergency restart endpoint"""
            success = self.restart_bots()
            return jsonify({
                "status": "success" if success else "failed",
                "message": "Bots restarted" if success else "Failed to restart bots",
                "restart_count": self.restart_count
            })
    
    def start_flask_server(self):
        """Start Flask server in a separate thread"""
        def run_flask():
            try:
                self.log(f"🌐 Starting HTTP server on port {self.port}")
                self.flask_app.run(
                    host='0.0.0.0', 
                    port=self.port, 
                    debug=False, 
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                self.log(f"❌ Flask server error: {e}")
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        time.sleep(2)  # Give server time to start
        self.log("✅ HTTP server started successfully")
    
    def kill_existing_bots(self):
        """Kill any existing bot processes"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                             capture_output=True, check=False)
            else:  # Linux/Unix (Google Cloud Run)
                subprocess.run(["pkill", "-f", "TelegramBot.py"], 
                             capture_output=True, check=False)
                subprocess.run(["pkill", "-f", "StudentBot.py"], 
                             capture_output=True, check=False)
            time.sleep(2)
            self.log("🔄 Cleared any existing bot processes")
        except Exception as e:
            self.log(f"⚠️ Could not kill existing processes: {e}")
    
    def start_teacher_bot(self):
        """Start the teacher bot"""
        try:
            self.log("🎓 Starting Teacher Bot...")

            env = os.environ.copy()
            env['DEPLOYMENT_MODE'] = 'polling_keepalive'
            env['ENVIRONMENT'] = 'production'

            self.teacher_process = subprocess.Popen(
                [sys.executable, "TelegramBot.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Give it time to start and check output
            time.sleep(5)

            if self.teacher_process.poll() is None:
                self.log("✅ Teacher Bot started successfully")
                # Start a thread to monitor its output
                self.start_output_monitor(self.teacher_process, "Teacher Bot")
                return True
            else:
                # Process died, get the error
                stdout, stderr = self.teacher_process.communicate()
                self.log("❌ Teacher Bot failed to start")
                if stdout:
                    self.log(f"   Output: {stdout}")
                if stderr:
                    self.log(f"   Error: {stderr}")
                return False

        except Exception as e:
            self.log(f"❌ Error starting Teacher Bot: {e}")
            return False

    def start_student_bot(self):
        """Start the student bot"""
        try:
            self.log("👨‍🎓 Starting Student Bot...")

            env = os.environ.copy()
            env['ENVIRONMENT'] = 'production'

            self.student_process = subprocess.Popen(
                [sys.executable, "StudentBot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Give it time to start
            time.sleep(5)

            if self.student_process.poll() is None:
                self.log("✅ Student Bot started successfully")
                # Start a thread to monitor its output
                self.start_output_monitor(self.student_process, "Student Bot")
                return True
            else:
                # Process died, get the error
                stdout, stderr = self.student_process.communicate()
                self.log("❌ Student Bot failed to start")
                if stdout:
                    self.log(f"   Output: {stdout}")
                if stderr:
                    self.log(f"   Error: {stderr}")
                return False

        except Exception as e:
            self.log(f"❌ Error starting Student Bot: {e}")
            return False

    def start_output_monitor(self, process, bot_name):
        """Monitor bot output in a separate thread"""
        def monitor():
            try:
                while process.poll() is None:
                    line = process.stdout.readline()
                    if line:
                        self.log(f"[{bot_name}] {line.strip()}")
            except Exception as e:
                self.log(f"❌ Output monitor error for {bot_name}: {e}")

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def check_bots_health(self):
        """Check if both bots are running"""
        teacher_alive = self.teacher_process and self.teacher_process.poll() is None
        student_alive = self.student_process and self.student_process.poll() is None
        return teacher_alive, student_alive
    
    def restart_bots(self):
        """Restart both bots"""
        self.restart_count += 1
        self.log(f"🔄 Restarting bots (restart #{self.restart_count})...")
        
        # Kill existing
        self.kill_existing_bots()
        
        # Start fresh
        teacher_ok = self.start_teacher_bot()
        student_ok = self.start_student_bot()
        
        if teacher_ok and student_ok:
            self.log("✅ Both bots restarted successfully")
            return True
        else:
            self.log("❌ Failed to restart one or both bots")
            return False
    
    def self_ping_loop(self):
        """Self-ping to keep the service alive"""
        time.sleep(10)  # Wait for server to start
        
        while self.running:
            try:
                response = requests.get(
                    f"http://localhost:{self.port}/keep-alive",
                    timeout=10
                )
                if response.status_code == 200:
                    self.log(f"✅ Self-ping successful (total: {self.ping_count})")
                else:
                    self.log(f"⚠️ Self-ping returned status {response.status_code}")
            except Exception as e:
                self.log(f"❌ Self-ping failed: {e}")
            
            # Wait 5 minutes before next ping
            time.sleep(300)
    
    def monitor_bots_loop(self):
        """Monitor bot health and restart if needed"""
        while self.running:
            try:
                teacher_alive, student_alive = self.check_bots_health()
                
                if not teacher_alive or not student_alive:
                    self.log("💀 One or both bots have died!")
                    self.log(f"Teacher Bot: {'✅ Running' if teacher_alive else '❌ Dead'}")
                    self.log(f"Student Bot: {'✅ Running' if student_alive else '❌ Dead'}")
                    
                    if not self.restart_bots():
                        self.log("❌ Failed to restart, will retry in 30 seconds...")
                        time.sleep(30)
                else:
                    uptime = datetime.now() - self.start_time
                    self.log(f"✅ Both bots healthy (uptime: {uptime})")
                
                # Check every 2 minutes
                time.sleep(120)
                
            except Exception as e:
                self.log(f"❌ Monitor error: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the complete 24/7 system"""
        self.log("🚀 Starting 24/7 Telegram Bot Keep-Alive System")
        self.log("=" * 60)
        self.log("This system will:")
        self.log("✅ Keep both bots running continuously")
        self.log("✅ Prevent Google Cloud Run from shutting down")
        self.log("✅ Auto-restart bots if they crash")
        self.log("✅ Provide HTTP endpoints for external monitoring")
        self.log("=" * 60)
        
        # Start HTTP server first
        self.start_flask_server()
        
        # Clear any existing bots
        self.kill_existing_bots()
        
        # Start both bots
        teacher_ok = self.start_teacher_bot()
        student_ok = self.start_student_bot()
        
        if not (teacher_ok and student_ok):
            self.log("❌ Failed to start one or both bots")
            return False
        
        self.log("🎉 System started successfully!")
        self.log("🎓 Teacher Bot: Running")
        self.log("👨‍🎓 Student Bot: Running")
        self.log(f"🌐 HTTP server: http://localhost:{self.port}")
        self.log("💬 Test by sending /start to your bots on Telegram")
        self.log("=" * 60)
        
        # Start self-ping in background
        ping_thread = threading.Thread(target=self.self_ping_loop, daemon=True)
        ping_thread.start()
        self.log("🔄 Self-ping system started (every 5 minutes)")
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_bots_loop, daemon=True)
        monitor_thread.start()
        self.log("👀 Bot health monitoring started")
        
        return True
    
    def stop(self):
        """Stop all processes"""
        self.log("🛑 Stopping all processes...")
        self.running = False
        
        if self.teacher_process:
            self.teacher_process.terminate()
        if self.student_process:
            self.student_process.terminate()
        
        self.log("✅ All processes stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Received shutdown signal")
    if 'keeper' in globals():
        keeper.stop()
    sys.exit(0)

def main():
    """Main function"""
    global keeper
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    keeper = BotKeepAlive24x7()
    
    try:
        if keeper.start():
            # Keep main thread alive
            while True:
                time.sleep(60)
        else:
            print("❌ Failed to start the 24/7 system")
            sys.exit(1)
            
    except KeyboardInterrupt:
        keeper.stop()
        print("👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        keeper.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
