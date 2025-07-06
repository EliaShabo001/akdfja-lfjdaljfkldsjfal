#!/usr/bin/env python3
"""
Test the integrated 24/7 bot system
This will test both the HTTP server and the actual Telegram bots
"""

import os
import sys
import time
import requests
import threading
from datetime import datetime

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_endpoints():
    """Test all HTTP endpoints"""
    log("🧪 Testing HTTP endpoints...")
    
    base_url = "http://localhost:8080"
    endpoints = [
        ("/", "Home page"),
        ("/health", "Health check"),
        ("/keep-alive", "Keep-alive"),
        ("/ping", "Ping test")
    ]
    
    # Wait for server to start
    time.sleep(10)
    
    all_good = True
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                log(f"✅ {description}: OK")
                
                # Show details for health endpoint
                if endpoint == "/health":
                    try:
                        data = response.json()
                        log(f"   Teacher Bot: {'✅ Running' if data.get('teacher_bot_running') else '❌ Not running'}")
                        log(f"   Student Bot: {'✅ Running' if data.get('student_bot_running') else '❌ Not running'}")
                        log(f"   Uptime: {data.get('uptime_formatted', 'unknown')}")
                        log(f"   Status: {data.get('status', 'unknown')}")
                    except Exception as e:
                        log(f"   Could not parse JSON: {e}")
                        
                elif endpoint == "/keep-alive":
                    try:
                        data = response.json()
                        log(f"   Ping count: {data.get('ping_count', 'unknown')}")
                        log(f"   Teacher running: {data.get('teacher_running', 'unknown')}")
                        log(f"   Student running: {data.get('student_running', 'unknown')}")
                    except Exception as e:
                        log(f"   Could not parse JSON: {e}")
                        
            else:
                log(f"❌ {description}: Status {response.status_code}")
                all_good = False
                
        except requests.exceptions.ConnectionError:
            log(f"❌ {description}: Connection failed (server not ready?)")
            all_good = False
        except Exception as e:
            log(f"❌ {description}: Error - {e}")
            all_good = False
    
    return all_good

def monitor_system():
    """Monitor the system for a while"""
    log("👀 Monitoring system for 2 minutes...")
    
    base_url = "http://localhost:8080"
    
    for i in range(4):  # Check 4 times over 2 minutes
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                teacher_running = data.get('teacher_bot_running', False)
                student_running = data.get('student_bot_running', False)
                uptime = data.get('uptime_formatted', 'unknown')
                
                status = "✅ Healthy" if teacher_running and student_running else "⚠️ Partial"
                log(f"{status} - Teacher: {'✅' if teacher_running else '❌'}, Student: {'✅' if student_running else '❌'}, Uptime: {uptime}")
            else:
                log(f"❌ Health check failed with status {response.status_code}")
        except Exception as e:
            log(f"❌ Health check error: {e}")
        
        if i < 3:  # Don't wait after last check
            time.sleep(30)  # Wait 30 seconds between checks

def main():
    """Main test function"""
    log("🧪 Testing Integrated 24/7 Bot System")
    log("=" * 60)
    log("This will test the integrated bot system that runs both")
    log("Telegram bots and HTTP server in the same process.")
    log("=" * 60)
    
    # Check if required files exist
    required_files = ["TelegramBot.py", "StudentBot.py", "run_bots_24x7_integrated.py"]
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            log(f"✅ {file}")
        else:
            log(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        log("❌ Missing required files. Please ensure all files are present.")
        return
    
    # Set environment for testing
    os.environ['PORT'] = '8080'
    
    try:
        log("🚀 Starting integrated bot system...")
        
        # Start the system in a separate thread
        def run_system():
            try:
                from run_bots_24x7_integrated import IntegratedBot24x7
                bot_system = IntegratedBot24x7()
                bot_system.start()
                
                # Keep it running
                while True:
                    time.sleep(1)
            except Exception as e:
                log(f"❌ System error: {e}")
                import traceback
                traceback.print_exc()
        
        # Start system in background
        system_thread = threading.Thread(target=run_system, daemon=True)
        system_thread.start()
        
        # Test endpoints
        if test_endpoints():
            log("✅ All endpoints working!")
        else:
            log("⚠️ Some endpoints failed")
        
        # Monitor the system
        monitor_system()
        
        # Final status check
        log("🏥 Final status check...")
        try:
            response = requests.get("http://localhost:8080/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                teacher_running = data.get('teacher_bot_running', False)
                student_running = data.get('student_bot_running', False)
                
                log("📊 Final Results:")
                log(f"   HTTP Server: ✅ Running")
                log(f"   Teacher Bot: {'✅ Running' if teacher_running else '❌ Not running'}")
                log(f"   Student Bot: {'✅ Running' if student_running else '❌ Not running'}")
                log(f"   System Status: {'✅ Fully Operational' if teacher_running and student_running else '⚠️ Partial Operation'}")
                
                if teacher_running and student_running:
                    log("🎉 SUCCESS! Both bots are running!")
                    log("💬 You can now test by sending /start to your bots on Telegram")
                else:
                    log("⚠️ Some bots are not running. Check the logs above for errors.")
                    log("💡 Common issues:")
                    log("   - Bot tokens not configured")
                    log("   - Network connectivity issues")
                    log("   - Database connection problems")
        except Exception as e:
            log(f"❌ Final status check failed: {e}")
        
        log("=" * 60)
        log("✅ Test completed!")
        log("📋 Next steps:")
        log("   1. If bots are running, test them on Telegram")
        log("   2. If successful, deploy to Google Cloud Run")
        log("   3. Set up external monitoring")
        
    except KeyboardInterrupt:
        log("\n🛑 Test stopped by user")
    except Exception as e:
        log(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
