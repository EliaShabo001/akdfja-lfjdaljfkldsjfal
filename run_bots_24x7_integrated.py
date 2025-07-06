#!/usr/bin/env python3
"""
Integrated 24/7 Bot Runner (No subprocess, direct integration)
This script runs both bots in the same process with keep-alive HTTP server
"""

import os
import sys
import threading
import time
import requests
import signal
from datetime import datetime
from flask import Flask, jsonify

class IntegratedBot24x7:
    def __init__(self):
        self.teacher_bot = None
        self.student_bot = None
        self.teacher_thread = None
        self.student_thread = None
        self.flask_app = None
        self.running = True
        self.start_time = datetime.now()
        self.last_ping = datetime.now()
        self.ping_count = 0
        self.port = int(os.environ.get('PORT', 8080))
        self.teacher_running = False
        self.student_running = False
        
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
            
            return jsonify({
                "status": "healthy" if self.teacher_running and self.student_running else "partial",
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_formatted": str(uptime),
                "teacher_bot_running": self.teacher_running,
                "student_bot_running": self.student_running,
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
                "uptime": str(datetime.now() - self.start_time),
                "teacher_running": self.teacher_running,
                "student_running": self.student_running
            })
        
        @self.flask_app.route('/ping')
        def ping():
            return "pong"
    
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
    
    def start_teacher_bot_thread(self):
        """Start teacher bot in a separate thread"""
        def run_teacher():
            try:
                self.log("🎓 Starting Teacher Bot...")
                
                # Set environment for polling mode
                os.environ['ENVIRONMENT'] = 'local'
                
                # Import and start the teacher bot
                from TelegramBot import bot
                
                self.teacher_bot = bot
                self.teacher_running = True
                
                # Remove any webhook and start polling
                bot.remove_webhook()
                self.log("✅ Teacher Bot started successfully")
                bot.polling(none_stop=True, interval=1, timeout=20)
                
            except Exception as e:
                self.log(f"❌ Teacher Bot error: {e}")
                self.teacher_running = False
        
        self.teacher_thread = threading.Thread(target=run_teacher, daemon=True)
        self.teacher_thread.start()
        time.sleep(3)  # Give it time to start
    
    def start_student_bot_thread(self):
        """Start student bot in a separate thread"""
        def run_student():
            try:
                self.log("👨‍🎓 Starting Student Bot...")
                
                # Import and start the student bot
                from StudentBot import student_bot
                
                self.student_bot = student_bot
                self.student_running = True
                
                self.log("✅ Student Bot started successfully")
                student_bot.polling(none_stop=True, interval=1, timeout=20)
                
            except Exception as e:
                self.log(f"❌ Student Bot error: {e}")
                self.student_running = False
        
        self.student_thread = threading.Thread(target=run_student, daemon=True)
        self.student_thread.start()
        time.sleep(3)  # Give it time to start
    
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
        """Monitor bot health"""
        while self.running:
            try:
                # Check if threads are still alive
                teacher_alive = self.teacher_thread and self.teacher_thread.is_alive()
                student_alive = self.student_thread and self.student_thread.is_alive()
                
                if not teacher_alive and self.teacher_running:
                    self.log("💀 Teacher Bot thread died!")
                    self.teacher_running = False
                    self.restart_teacher_bot()
                
                if not student_alive and self.student_running:
                    self.log("💀 Student Bot thread died!")
                    self.student_running = False
                    self.restart_student_bot()
                
                if self.teacher_running and self.student_running:
                    uptime = datetime.now() - self.start_time
                    self.log(f"✅ Both bots healthy (uptime: {uptime})")
                
                # Check every 2 minutes
                time.sleep(120)
                
            except Exception as e:
                self.log(f"❌ Monitor error: {e}")
                time.sleep(60)
    
    def restart_teacher_bot(self):
        """Restart teacher bot"""
        self.log("🔄 Restarting Teacher Bot...")
        try:
            self.start_teacher_bot_thread()
        except Exception as e:
            self.log(f"❌ Failed to restart Teacher Bot: {e}")
    
    def restart_student_bot(self):
        """Restart student bot"""
        self.log("🔄 Restarting Student Bot...")
        try:
            self.start_student_bot_thread()
        except Exception as e:
            self.log(f"❌ Failed to restart Student Bot: {e}")
    
    def start(self):
        """Start the complete 24/7 system"""
        self.log("🚀 Starting Integrated 24/7 Telegram Bot System")
        self.log("=" * 60)
        self.log("This system will:")
        self.log("✅ Run both bots in the same process")
        self.log("✅ Prevent Google Cloud Run from shutting down")
        self.log("✅ Auto-restart bot threads if they die")
        self.log("✅ Provide HTTP endpoints for external monitoring")
        self.log("=" * 60)
        
        # Start HTTP server first
        self.start_flask_server()
        
        # Start both bots
        self.start_teacher_bot_thread()
        self.start_student_bot_thread()
        
        # Wait a bit for bots to start
        time.sleep(5)
        
        if self.teacher_running and self.student_running:
            self.log("🎉 System started successfully!")
            self.log("🎓 Teacher Bot: Running")
            self.log("👨‍🎓 Student Bot: Running")
            self.log(f"🌐 HTTP server: http://localhost:{self.port}")
            self.log("💬 Test by sending /start to your bots on Telegram")
            self.log("=" * 60)
        else:
            self.log("⚠️ Some bots may not have started properly")
            self.log(f"Teacher Bot: {'✅' if self.teacher_running else '❌'}")
            self.log(f"Student Bot: {'✅' if self.student_running else '❌'}")
        
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
        self.teacher_running = False
        self.student_running = False
        
        if self.teacher_bot:
            try:
                self.teacher_bot.stop_polling()
            except:
                pass
        
        if self.student_bot:
            try:
                self.student_bot.stop_polling()
            except:
                pass
        
        self.log("✅ All processes stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Received shutdown signal")
    if 'bot_system' in globals():
        bot_system.stop()
    sys.exit(0)

def main():
    """Main function"""
    global bot_system
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    bot_system = IntegratedBot24x7()
    
    try:
        if bot_system.start():
            # Keep main thread alive
            while True:
                time.sleep(60)
        else:
            print("❌ Failed to start the 24/7 system")
            sys.exit(1)
            
    except KeyboardInterrupt:
        bot_system.stop()
        print("👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        bot_system.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
