#!/usr/bin/env python3
"""
Simple External Pinger for Google Cloud Run Bot (No gcloud required)
This script pings your deployed bot every few minutes to keep it alive.
Run this from any computer with internet connection.
"""

import requests
import time
import sys
from datetime import datetime

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def ping_bot(url):
    """Send a ping to keep the bot alive"""
    try:
        response = requests.get(f"{url}/keep-alive", timeout=30)
        if response.status_code == 200:
            data = response.json()
            ping_count = data.get('ping_count', 'unknown')
            uptime = data.get('uptime', 'unknown')
            log(f"✅ Bot is alive! Ping #{ping_count}, Uptime: {uptime}")
            return True
        else:
            log(f"⚠️ Bot responded with status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        log("❌ Request timed out - bot might be starting up")
        return False
    except requests.exceptions.ConnectionError:
        log("❌ Could not connect to bot - check URL")
        return False
    except Exception as e:
        log(f"❌ Error: {e}")
        return False

def check_health(url):
    """Check bot health"""
    try:
        response = requests.get(f"{url}/health", timeout=15)
        if response.status_code == 200:
            data = response.json()
            teacher_running = data.get('teacher_bot_running', False)
            student_running = data.get('student_bot_running', False)
            uptime = data.get('uptime_formatted', 'unknown')
            restart_count = data.get('restart_count', 0)
            
            log(f"🏥 Health Check:")
            log(f"   Teacher Bot: {'✅ Running' if teacher_running else '❌ Down'}")
            log(f"   Student Bot: {'✅ Running' if student_running else '❌ Down'}")
            log(f"   Uptime: {uptime}")
            log(f"   Restarts: {restart_count}")
            
            return teacher_running and student_running
        else:
            log(f"⚠️ Health check returned status {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Health check error: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🤖 Simple External Pinger for Google Cloud Run Telegram Bot")
        print()
        print("Usage:")
        print("  python simple_external_pinger.py <BOT_URL> [interval_minutes]")
        print()
        print("Examples:")
        print("  # Ping every 5 minutes (default)")
        print("  python simple_external_pinger.py https://your-bot-url.run.app")
        print()
        print("  # Ping every 3 minutes")
        print("  python simple_external_pinger.py https://your-bot-url.run.app 3")
        print()
        print("  # Single ping test")
        print("  python simple_external_pinger.py https://your-bot-url.run.app 0")
        print()
        print("Replace 'your-bot-url.run.app' with your actual Google Cloud Run URL")
        sys.exit(1)
    
    bot_url = sys.argv[1].rstrip('/')
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    log("🚀 Starting External Bot Pinger")
    log(f"🎯 Target: {bot_url}")
    
    if interval == 0:
        # Single test
        log("🧪 Running single test...")
        health_ok = check_health(bot_url)
        ping_ok = ping_bot(bot_url)
        
        if health_ok and ping_ok:
            log("✅ Bot is healthy and responsive!")
            sys.exit(0)
        else:
            log("❌ Bot has issues")
            sys.exit(1)
    else:
        # Continuous pinging
        log(f"🔄 Will ping every {interval} minutes")
        log("🛑 Press Ctrl+C to stop")
        log("=" * 50)
        
        ping_count = 0
        success_count = 0
        
        try:
            while True:
                ping_count += 1
                log(f"🔢 Ping #{ping_count}")
                
                # Send keep-alive ping
                if ping_bot(bot_url):
                    success_count += 1
                
                # Every 6th ping (30 minutes with 5-min interval), check health
                if ping_count % 6 == 0:
                    check_health(bot_url)
                    success_rate = (success_count / ping_count) * 100
                    log(f"📊 Success rate: {success_rate:.1f}% ({success_count}/{ping_count})")
                    log("-" * 50)
                
                # Wait for next interval
                log(f"💤 Waiting {interval} minutes...")
                time.sleep(interval * 60)
                
        except KeyboardInterrupt:
            log("\n🛑 Pinger stopped by user")
            success_rate = (success_count / ping_count) * 100 if ping_count > 0 else 0
            log(f"📊 Final stats: {success_rate:.1f}% success rate ({success_count}/{ping_count})")
            log("👋 Goodbye!")

if __name__ == "__main__":
    main()
