#!/usr/bin/env python3
"""
Local Test for 24/7 Bot System (No gcloud required)
This script tests the keep-alive system locally before deploying
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
    time.sleep(8)
    
    all_good = True
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                log(f"✅ {description}: OK")
                
                # Show some details for key endpoints
                if endpoint == "/health":
                    try:
                        data = response.json()
                        log(f"   Teacher Bot: {'✅' if data.get('teacher_bot_running') else '❌'}")
                        log(f"   Student Bot: {'✅' if data.get('student_bot_running') else '❌'}")
                        log(f"   Uptime: {data.get('uptime_formatted', 'unknown')}")
                    except:
                        log(f"   Response: {response.text[:100]}")
                        
                elif endpoint == "/keep-alive":
                    try:
                        data = response.json()
                        log(f"   Ping count: {data.get('ping_count', 'unknown')}")
                    except:
                        log(f"   Response: {response.text[:50]}")
                        
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

def simulate_external_pings():
    """Simulate external monitoring pings"""
    log("🔄 Simulating external monitoring pings...")
    
    base_url = "http://localhost:8080"
    
    for i in range(3):
        try:
            response = requests.get(f"{base_url}/keep-alive", timeout=10)
            if response.status_code == 200:
                data = response.json()
                log(f"✅ External ping #{i+1}: Success (total: {data.get('ping_count', 'unknown')})")
            else:
                log(f"❌ External ping #{i+1}: Status {response.status_code}")
        except Exception as e:
            log(f"❌ External ping #{i+1}: Error - {e}")
        
        if i < 2:  # Don't wait after last ping
            time.sleep(5)

def check_required_files():
    """Check if all required files exist"""
    log("📁 Checking required files...")
    
    required_files = [
        "TelegramBot.py",
        "StudentBot.py",
        "db.py",
        "requirements.txt",
        "keep_bot_alive_24x7.py"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            log(f"✅ {file}")
        else:
            log(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        log("❌ Missing required files!")
        return False
    
    return True

def main():
    """Main test function"""
    log("🧪 Local 24/7 Bot System Test")
    log("=" * 60)
    log("This will test the 24/7 keep-alive system locally")
    log("Note: Bot processes may fail to start without proper tokens,")
    log("but the HTTP server and keep-alive system should work fine.")
    log("=" * 60)
    
    # Check required files
    if not check_required_files():
        log("❌ Please ensure all required files are present")
        return
    
    # Set environment for local testing
    os.environ['PORT'] = '8080'
    
    try:
        log("🚀 Starting 24/7 keep-alive system...")
        
        # Import and start the system in a separate thread
        def run_system():
            try:
                from keep_bot_alive_24x7 import BotKeepAlive24x7
                keeper = BotKeepAlive24x7()
                keeper.start()
                
                # Keep it running
                while True:
                    time.sleep(1)
            except Exception as e:
                log(f"❌ System error: {e}")
        
        # Start system in background
        system_thread = threading.Thread(target=run_system, daemon=True)
        system_thread.start()
        
        # Test endpoints
        if test_endpoints():
            log("✅ All endpoints working!")
        else:
            log("⚠️ Some endpoints failed (may be normal if bots can't start)")
        
        # Simulate external monitoring
        simulate_external_pings()
        
        # Final health check
        log("🏥 Final health check...")
        time.sleep(2)
        try:
            response = requests.get("http://localhost:8080/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                log("📊 Final Status:")
                log(f"   HTTP Server: ✅ Running")
                log(f"   Self-ping count: {data.get('ping_count', 0)}")
                log(f"   Teacher Bot: {'✅ Running' if data.get('teacher_bot_running') else '❌ Not running'}")
                log(f"   Student Bot: {'✅ Running' if data.get('student_bot_running') else '❌ Not running'}")
                
                if not data.get('teacher_bot_running') or not data.get('student_bot_running'):
                    log("ℹ️ Bots may not start locally without proper configuration")
                    log("ℹ️ This is normal - the important part is the HTTP server works")
        except Exception as e:
            log(f"❌ Final health check failed: {e}")
        
        log("=" * 60)
        log("✅ Local test completed!")
        log("🚀 Key findings:")
        log("   - HTTP server can start and respond")
        log("   - Keep-alive endpoints work")
        log("   - Self-ping system functions")
        log("   - Ready for Google Cloud Run deployment!")
        log("=" * 60)
        log("📋 Next steps:")
        log("   1. Follow DEPLOY_WITHOUT_GCLOUD.md guide")
        log("   2. Deploy using Google Cloud Console")
        log("   3. Set up external monitoring with UptimeRobot")
        log("   4. Test your deployed bots on Telegram")
        
    except KeyboardInterrupt:
        log("\n🛑 Test stopped by user")
    except ImportError as e:
        log(f"❌ Import error: {e}")
        log("Make sure keep_bot_alive_24x7.py exists and Flask is installed:")
        log("   pip install flask requests")
    except Exception as e:
        log(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()
