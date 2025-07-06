# 🚀 Deploy Telegram Bot 24/7 on Google Cloud Run (No gcloud CLI Required)

This guide shows you how to deploy your Telegram bot to run 24/7 on Google Cloud Run using only the web interface - **no gcloud CLI installation needed!**

## 🎯 What This Solution Does

✅ **Keeps your bot running 24/7** - Never shuts down  
✅ **Auto-restarts if bots crash** - Built-in recovery  
✅ **Prevents Google Cloud Run shutdown** - Self-ping system  
✅ **No gcloud CLI needed** - Uses web interface only  
✅ **External monitoring support** - Keep-alive from anywhere  
✅ **Cost optimized** - ~$5-15/month for 24/7 operation  

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Web browser** (Chrome, Firefox, Safari, etc.)
3. **Your bot files** ready in this directory

## 🔧 Step 1: Prepare Your Files

Make sure you have these files in your project directory:

```
📂 Your Project Directory
├── 📄 TelegramBot.py           # Your teacher bot
├── 📄 StudentBot.py            # Your student bot
├── 📄 db.py                    # Database operations
├── 📄 requirements.txt         # Python dependencies
├── 📄 keep_bot_alive_24x7.py   # 24/7 keep-alive script (NEW)
├── 📄 Dockerfile.simple24x7    # Docker configuration (NEW)
└── 📄 (other files...)
```

## 🌐 Step 2: Deploy Using Google Cloud Console

### 2.1 Open Google Cloud Console
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Sign in with your Google account
3. Create a new project or select existing one

### 2.2 Enable Required APIs
1. Go to **APIs & Services** → **Library**
2. Search and enable these APIs:
   - **Cloud Run API**
   - **Cloud Build API**
   - **Container Registry API**

### 2.3 Upload Your Code
1. Go to **Cloud Shell** (terminal icon in top bar)
2. Click **Upload files** and upload all your project files
3. Or use **Cloud Source Repositories** to connect your GitHub

### 2.4 Build and Deploy
In Cloud Shell, run these commands:

```bash
# Navigate to your uploaded files
cd your-project-directory

# Build the Docker image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/telegram-bot-24x7 -f Dockerfile.simple24x7

# Deploy to Cloud Run
gcloud run deploy telegram-bot-24x7 \
  --image gcr.io/YOUR_PROJECT_ID/telegram-bot-24x7 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 2 \
  --cpu 1 \
  --memory 1Gi \
  --port 8080
```

**Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID**

## 🎯 Alternative: Use Cloud Run Web Interface

### Option A: Deploy from Source
1. Go to **Cloud Run** in Google Cloud Console
2. Click **Create Service**
3. Select **Deploy one revision from a source repository**
4. Connect your GitHub repository
5. Set these configurations:
   - **Port**: 8080
   - **CPU allocation**: CPU is always allocated
   - **Minimum instances**: 1
   - **Maximum instances**: 2
   - **Memory**: 1 GiB
   - **CPU**: 1

### Option B: Deploy from Container Image
1. First build your image using Cloud Build
2. Go to **Cloud Run** → **Create Service**
3. Select **Deploy one revision from an existing container image**
4. Choose your built image
5. Configure the same settings as above

## 🔍 Step 3: Get Your Service URL

After deployment, you'll get a URL like:
```
https://telegram-bot-24x7-[random-hash]-uc.a.run.app
```

**Save this URL - you'll need it for monitoring!**

## ✅ Step 4: Test Your Deployment

### 4.1 Test HTTP Endpoints
Open these URLs in your browser:

```
https://YOUR_SERVICE_URL/
https://YOUR_SERVICE_URL/health
https://YOUR_SERVICE_URL/keep-alive
https://YOUR_SERVICE_URL/ping
```

Expected responses:
- `/` → "🤖 Telegram Quiz Bot is running 24/7! 🎓"
- `/health` → JSON with bot status and uptime
- `/keep-alive` → JSON with ping count
- `/ping` → "pong"

### 4.2 Test Your Telegram Bots
1. **Teacher Bot**: Send `/start` and enter password
2. **Student Bot**: Test with a quiz link

## 🔄 Step 5: Set Up External Monitoring

To ensure your bot **never shuts down**, set up external monitoring:

### Option A: UptimeRobot (Recommended - Free)
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create free account
3. Add new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://YOUR_SERVICE_URL/keep-alive`
   - **Interval**: 5 minutes
   - **Name**: Telegram Bot 24/7

### Option B: Use the External Pinger Script
Run this from any computer with internet:

```bash
# Test once
python simple_external_pinger.py https://YOUR_SERVICE_URL 0

# Run continuously (every 5 minutes)
python simple_external_pinger.py https://YOUR_SERVICE_URL

# Custom interval (every 3 minutes)
python simple_external_pinger.py https://YOUR_SERVICE_URL 3
```

### Option C: Cron Job (Linux/Mac)
Add to crontab:
```bash
# Ping every 5 minutes
*/5 * * * * curl -s https://YOUR_SERVICE_URL/keep-alive > /dev/null
```

### Option D: Windows Task Scheduler
Create a task that runs every 5 minutes:
```cmd
curl -s https://YOUR_SERVICE_URL/keep-alive
```

## 📊 Step 6: Monitor Your Bot

### View Logs
1. Go to **Cloud Run** → **telegram-bot-24x7**
2. Click **Logs** tab
3. You should see:
   ```
   ✅ Teacher Bot started successfully
   ✅ Student Bot started successfully
   ✅ Self-ping successful
   ✅ Both bots healthy
   ```

### Check Metrics
1. Go to **Metrics** tab in Cloud Run
2. Monitor:
   - **Request count** (should show regular keep-alive pings)
   - **Instance count** (should stay at 1)
   - **CPU utilization**
   - **Memory utilization**

## 💰 Cost Estimation

With this 24/7 setup:
- **CPU**: ~$3-8/month (1 vCPU continuously)
- **Memory**: ~$1-3/month (1GB continuously)
- **Requests**: ~$0.10/month (keep-alive pings)
- **Total**: ~$5-15/month

## 🚨 Troubleshooting

### Bot Not Responding
1. Check logs in Cloud Run console
2. Verify health endpoint: `https://YOUR_URL/health`
3. Ensure min-instances is set to 1
4. Check bot tokens in your code

### Service Keeps Shutting Down
1. Verify min-instances is set to 1:
   - Go to Cloud Run → Service → Edit & Deploy New Revision
   - Set "Minimum number of instances" to 1
2. Check external monitoring is working
3. Verify keep-alive pings are being received

### High Costs
1. Check resource usage in Cloud Run metrics
2. Reduce CPU/memory if usage is low
3. Ensure max-instances is set to 2

## 🎉 Success Indicators

Your bot is working correctly when:
- ✅ Health endpoint shows both bots running
- ✅ Logs show regular "Both bots healthy" messages
- ✅ External pings are successful
- ✅ Telegram bots respond to messages
- ✅ Service stays running for 24+ hours
- ✅ Instance count stays at 1 in metrics

## 🔧 Advanced Configuration

### Update Environment Variables
1. Go to Cloud Run → Service → Edit & Deploy New Revision
2. Add environment variables:
   - `ENVIRONMENT=production`
   - `PORT=8080`

### Scale Settings
- **Min instances**: 1 (prevents shutdown)
- **Max instances**: 2 (prevents high costs)
- **CPU**: 1 vCPU
- **Memory**: 1 GiB
- **Request timeout**: 3600 seconds

## 🎯 Key Features of This Solution

1. **🔄 Self-Healing**: Automatically restarts crashed bots
2. **💓 Keep-Alive**: Self-pings every 5 minutes
3. **📊 Monitoring**: Built-in health checks
4. **🌐 HTTP Endpoints**: External monitoring support
5. **💰 Cost Optimized**: Minimal resources for 24/7 operation
6. **🛡️ Reliable**: Multiple backup systems

Your Telegram bot will now run 24/7 without interruption! 🚀

## 📞 Need Help?

If you encounter issues:
1. Check the logs in Cloud Run console
2. Test the health endpoint
3. Verify external monitoring is working
4. Ensure min-instances is set to 1

Your bot should now be running continuously on Google Cloud Run! 🎉
