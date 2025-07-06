#!/usr/bin/env python3
"""
External Keep-Alive Monitor for Google Cloud Run Telegram Bot
This script can be run from anywhere to keep your Cloud Run service alive
by sending periodic HTTP requests to prevent scale-to-zero.

Usage:
1. Deploy your bot to Google Cloud Run using the 24/7 configuration
2. Get your Cloud Run URL (e.g., https://telegram-quiz-bot-24x7-abc123-uc.a.run.app)
3. Run this script on any server/computer with: python external_keepalive_monitor.py
4. Or set up a cron job to run it every 5 minutes
"""

import requests
import time
import sys
from datetime import datetime
import json

class ExternalKeepAliveMonitor:
    def __init__(self, cloud_run_url):
        self.cloud_run_url = cloud_run_url.rstrip('/')
        self.ping_count = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def ping_service(self):
        """Send a keep-alive ping to the service"""
        try:
            self.ping_count += 1
            
            # Try the keep-alive endpoint first
            response = requests.get(
                f"{self.cloud_run_url}/keep-alive",
                timeout=30,
                headers={'User-Agent': 'External-KeepAlive-Monitor/1.0'}
            )
            
            if response.status_code == 200:
                self.success_count += 1
                data = response.json()
                self.log(f"✅ Keep-alive successful (ping #{data.get('ping_count', 'unknown')})")
                return True
            else:
                self.log(f"⚠️ Keep-alive returned status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.error_count += 1
            self.log("❌ Keep-alive request timed out")
            return False
        except requests.exceptions.ConnectionError:
            self.error_count += 1
            self.log("❌ Could not connect to service")
            return False
        except Exception as e:
            self.error_count += 1
            self.log(f"❌ Keep-alive error: {e}")
            return False
    
    def check_health(self):
        """Check the health of the service"""
        try:
            response = requests.get(
                f"{self.cloud_run_url}/health",
                timeout=15,
                headers={'User-Agent': 'External-KeepAlive-Monitor/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                uptime = data.get('uptime_formatted', 'unknown')
                self.log(f"🏥 Health check OK - Service uptime: {uptime}")
                return True
            else:
                self.log(f"⚠️ Health check returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {e}")
            return False
    
    def print_stats(self):
        """Print monitoring statistics"""
        runtime = datetime.now() - self.start_time
        success_rate = (self.success_count / self.ping_count * 100) if self.ping_count > 0 else 0
        
        self.log("📊 MONITORING STATISTICS:")
        self.log(f"   Runtime: {runtime}")
        self.log(f"   Total pings: {self.ping_count}")
        self.log(f"   Successful: {self.success_count}")
        self.log(f"   Errors: {self.error_count}")
        self.log(f"   Success rate: {success_rate:.1f}%")
        self.log("-" * 50)
    
    def run_once(self):
        """Run a single keep-alive check"""
        self.log("🔄 Running single keep-alive check...")
        
        # Check health first
        health_ok = self.check_health()
        
        # Send keep-alive ping
        ping_ok = self.ping_service()
        
        if health_ok and ping_ok:
            self.log("✅ Service is healthy and responsive")
            return True
        else:
            self.log("❌ Service has issues")
            return False
    
    def run_continuous(self, interval_minutes=5):
        """Run continuous monitoring"""
        self.log(f"🚀 Starting continuous monitoring (every {interval_minutes} minutes)")
        self.log(f"🎯 Target: {self.cloud_run_url}")
        self.log("🛑 Press Ctrl+C to stop")
        self.log("=" * 60)
        
        try:
            while True:
                # Send keep-alive ping
                self.ping_service()
                
                # Every 6th ping (30 minutes), also check health
                if self.ping_count % 6 == 0:
                    self.check_health()
                    self.print_stats()
                
                # Wait for next interval
                self.log(f"💤 Waiting {interval_minutes} minutes until next ping...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.log("\n🛑 Monitoring stopped by user")
            self.print_stats()
        except Exception as e:
            self.log(f"💥 Fatal error: {e}")
            self.print_stats()

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🤖 External Keep-Alive Monitor for Google Cloud Run Telegram Bot")
        print()
        print("Usage:")
        print("  python external_keepalive_monitor.py <CLOUD_RUN_URL> [mode] [interval]")
        print()
        print("Examples:")
        print("  # Single check")
        print("  python external_keepalive_monitor.py https://telegram-quiz-bot-24x7-abc123-uc.a.run.app once")
        print()
        print("  # Continuous monitoring every 5 minutes (default)")
        print("  python external_keepalive_monitor.py https://telegram-quiz-bot-24x7-abc123-uc.a.run.app")
        print()
        print("  # Continuous monitoring every 3 minutes")
        print("  python external_keepalive_monitor.py https://telegram-quiz-bot-24x7-abc123-uc.a.run.app continuous 3")
        print()
        print("For cron job (every 5 minutes):")
        print("  */5 * * * * /usr/bin/python3 /path/to/external_keepalive_monitor.py https://your-url.run.app once")
        sys.exit(1)
    
    cloud_run_url = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "continuous"
    interval = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    monitor = ExternalKeepAliveMonitor(cloud_run_url)
    
    if mode == "once":
        success = monitor.run_once()
        sys.exit(0 if success else 1)
    else:
        monitor.run_continuous(interval)

if __name__ == "__main__":
    main()
