#!/usr/bin/env python3
"""
Setup Script for Google Cloud Run 24/7 Telegram Bot Deployment
This script helps you prepare and deploy your bot to Google Cloud Run
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command(command, description):
    """Run a command and return success status"""
    log(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log(f"✅ {description} completed successfully")
            return True
        else:
            log(f"❌ {description} failed:")
            log(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ {description} failed: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are installed"""
    log("🔍 Checking prerequisites...")
    
    checks = [
        ("gcloud --version", "Google Cloud SDK"),
        ("docker --version", "Docker"),
        ("python --version", "Python")
    ]
    
    all_good = True
    for command, name in checks:
        if not run_command(command, f"Checking {name}"):
            all_good = False
    
    return all_good

def check_gcloud_auth():
    """Check if user is authenticated with gcloud"""
    log("🔐 Checking Google Cloud authentication...")
    
    result = subprocess.run("gcloud auth list --filter=status:ACTIVE --format='value(account)'", 
                          shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        log(f"✅ Authenticated as: {result.stdout.strip()}")
        return True
    else:
        log("❌ Not authenticated with Google Cloud")
        log("   Run: gcloud auth login")
        return False

def get_project_id():
    """Get the current Google Cloud project ID"""
    result = subprocess.run("gcloud config get-value project", 
                          shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        project_id = result.stdout.strip()
        log(f"📋 Current project: {project_id}")
        return project_id
    else:
        log("❌ No project set")
        log("   Run: gcloud config set project YOUR_PROJECT_ID")
        return None

def enable_apis(project_id):
    """Enable required Google Cloud APIs"""
    log("🔧 Enabling required APIs...")
    
    apis = [
        "cloudbuild.googleapis.com",
        "run.googleapis.com", 
        "containerregistry.googleapis.com"
    ]
    
    for api in apis:
        if not run_command(f"gcloud services enable {api}", f"Enabling {api}"):
            return False
    
    return True

def check_required_files():
    """Check if all required files exist"""
    log("📁 Checking required files...")
    
    required_files = [
        "TelegramBot.py",
        "StudentBot.py", 
        "db.py",
        "requirements.txt",
        "run_cloud_24_7.py",
        "webserver.py",
        "Dockerfile.cloud24x7",
        "cloudbuild-24x7.yaml"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            log(f"✅ {file}")
        else:
            log(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        log("❌ Missing required files. Please ensure all files are present.")
        return False
    
    return True

def test_locally():
    """Test the system locally before deployment"""
    log("🧪 Testing system locally...")
    
    response = input("Do you want to run a local test first? (y/n): ")
    if response.lower() == 'y':
        return run_command("python test_24x7_locally.py", "Running local test")
    else:
        log("⏭️ Skipping local test")
        return True

def deploy_to_cloud_run(project_id):
    """Deploy to Google Cloud Run"""
    log("🚀 Deploying to Google Cloud Run...")
    
    # Build and deploy using Cloud Build
    success = run_command(
        "gcloud builds submit --config cloudbuild-24x7.yaml",
        "Building and deploying with Cloud Build"
    )
    
    if success:
        # Get the service URL
        result = subprocess.run(
            "gcloud run services describe telegram-quiz-bot-24x7 --region us-central1 --format='value(status.url)'",
            shell=True, capture_output=True, text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            service_url = result.stdout.strip()
            log(f"🎉 Deployment successful!")
            log(f"🌐 Service URL: {service_url}")
            log(f"🔗 Health check: {service_url}/health")
            log(f"💓 Keep-alive: {service_url}/keep-alive")
            return service_url
    
    return None

def setup_monitoring(service_url):
    """Provide monitoring setup instructions"""
    log("📊 Setting up monitoring...")
    
    print("\n" + "="*60)
    print("🔄 MONITORING SETUP")
    print("="*60)
    print(f"Your bot is deployed at: {service_url}")
    print()
    print("To keep it running 24/7, set up external monitoring:")
    print()
    print("Option 1: UptimeRobot (Recommended)")
    print("  1. Go to https://uptimerobot.com")
    print("  2. Create a free account")
    print("  3. Add HTTP(s) monitor:")
    print(f"     URL: {service_url}/keep-alive")
    print("     Interval: 5 minutes")
    print()
    print("Option 2: External Monitor Script")
    print(f"  python external_keepalive_monitor.py {service_url}")
    print()
    print("Option 3: Cron Job")
    print(f"  */5 * * * * curl -s {service_url}/keep-alive > /dev/null")
    print()
    print("="*60)

def main():
    """Main setup function"""
    print("🤖 Google Cloud Run 24/7 Telegram Bot Setup")
    print("=" * 60)
    print("This script will help you deploy your Telegram bot to Google Cloud Run")
    print("with 24/7 operation and automatic restart capabilities.")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        log("❌ Prerequisites check failed. Please install missing components.")
        return
    
    # Check authentication
    if not check_gcloud_auth():
        log("❌ Authentication check failed. Please authenticate with Google Cloud.")
        return
    
    # Get project ID
    project_id = get_project_id()
    if not project_id:
        log("❌ Project ID check failed. Please set your project ID.")
        return
    
    # Enable APIs
    if not enable_apis(project_id):
        log("❌ API enablement failed.")
        return
    
    # Check required files
    if not check_required_files():
        log("❌ Required files check failed.")
        return
    
    # Test locally (optional)
    if not test_locally():
        log("❌ Local test failed. Please fix issues before deploying.")
        return
    
    # Deploy to Cloud Run
    service_url = deploy_to_cloud_run(project_id)
    if not service_url:
        log("❌ Deployment failed.")
        return
    
    # Setup monitoring
    setup_monitoring(service_url)
    
    log("🎉 Setup completed successfully!")
    log("Your Telegram bot is now running 24/7 on Google Cloud Run!")

if __name__ == "__main__":
    main()
