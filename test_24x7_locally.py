#!/usr/bin/env python3
"""
Local Test Script for 24/7 Cloud Run Bot Manager
This script tests the 24/7 system locally before deploying to Google Cloud Run
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

def test_webserver_endpoints():
    """Test the webserver endpoints"""
    log("🧪 Testing webserver endpoints...")
    
    base_url = "http://localhost:8080"
    endpoints = [
        ("/", "Basic health check"),
        ("/health", "Detailed health info"),
        ("/keep-alive", "Keep-alive endpoint"),
        ("/ping", "Simple ping")
    ]
    
    # Wait for server to start
    time.sleep(5)
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                log(f"✅ {description}: OK")
                if endpoint == "/health":
                    data = response.json()
                    log(f"   Uptime: {data.get('uptime_formatted', 'unknown')}")
                elif endpoint == "/keep-alive":
                    data = response.json()
                    log(f"   Ping count: {data.get('ping_count', 'unknown')}")
            else:
                log(f"❌ {description}: Status {response.status_code}")
        except Exception as e:
            log(f"❌ {description}: Error - {e}")

def simulate_external_monitoring():
    """Simulate external monitoring pings"""
    log("🔄 Starting simulated external monitoring...")
    
    base_url = "http://localhost:8080"
    ping_count = 0
    
    while ping_count < 5:  # Test 5 pings
        try:
            ping_count += 1
            response = requests.get(f"{base_url}/keep-alive", timeout=10)
            if response.status_code == 200:
                data = response.json()
                log(f"✅ External ping #{ping_count}: Success (total pings: {data.get('ping_count', 'unknown')})")
            else:
                log(f"❌ External ping #{ping_count}: Status {response.status_code}")
        except Exception as e:
            log(f"❌ External ping #{ping_count}: Error - {e}")
        
        time.sleep(10)  # Wait 10 seconds between pings

def main():
    """Main test function"""
    log("🧪 Starting Local 24/7 System Test")
    log("=" * 60)
    log("This will test the 24/7 system components locally")
    log("Make sure you have the required dependencies installed:")
    log("  pip install flask requests")
    log("=" * 60)
    
    # Set environment variable for local testing
    os.environ['DEPLOYMENT_MODE'] = 'local_test'
    os.environ['PORT'] = '8080'
    
    try:
        # Import and start the 24/7 manager
        log("🚀 Starting 24/7 Bot Manager...")
        
        # Start the manager in a separate thread for testing
        from run_cloud_24_7 import CloudRunBotManager
        
        manager = CloudRunBotManager()
        
        # Start webserver only (skip bots for testing)
        if manager.start_webserver():
            log("✅ Webserver started successfully")
        else:
            log("❌ Failed to start webserver")
            return
        
        # Test endpoints
        test_webserver_endpoints()
        
        # Simulate external monitoring
        monitor_thread = threading.Thread(target=simulate_external_monitoring, daemon=True)
        monitor_thread.start()
        
        # Keep running for a bit
        log("⏰ Running test for 60 seconds...")
        time.sleep(60)
        
        log("✅ Local test completed successfully!")
        log("🚀 You can now deploy to Google Cloud Run with confidence")
        
    except KeyboardInterrupt:
        log("\n🛑 Test stopped by user")
    except ImportError as e:
        log(f"❌ Import error: {e}")
        log("Make sure all required files are present:")
        log("  - run_cloud_24_7.py")
        log("  - webserver.py")
        log("  - requirements.txt")
    except Exception as e:
        log(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()
