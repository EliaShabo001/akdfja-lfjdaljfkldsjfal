# 🚀 Google Cloud Run 24/7 Deployment Guide

This guide will help you deploy your Telegram Quiz Bot to Google Cloud Run with **guaranteed 24/7 operation** and automatic restart capabilities.

## 🎯 What This Solution Provides

✅ **24/7 Operation** - Bot runs continuously without interruption  
✅ **Auto-Restart** - Automatically restarts if bots crash  
✅ **Keep-Alive System** - Prevents Google Cloud Run from scaling to zero  
✅ **Health Monitoring** - Built-in health checks and monitoring  
✅ **External Monitoring** - Optional external keep-alive service  
✅ **Cost Optimized** - Minimal resource usage while staying alive  

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed locally
3. **Project ID** in Google Cloud Console
4. **Bot tokens** configured in your code

## 🔧 Step 1: Prepare Your Project

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## 🚀 Step 2: Deploy to Google Cloud Run

### Option A: Using Cloud Build (Recommended)

```bash
# Deploy using the 24/7 optimized configuration
gcloud builds submit --config cloudbuild-24x7.yaml

# This will:
# 1. Build the Docker image with 24/7 optimizations
# 2. Push to Container Registry
# 3. Deploy to Cloud Run with keep-alive settings
# 4. Set min-instances to 1 (prevents scale-to-zero)
```

### Option B: Manual Deployment

```bash
# Build and push the container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/telegram-quiz-bot-24x7 -f Dockerfile.cloud24x7

# Deploy to Cloud Run with 24/7 settings
gcloud run deploy telegram-quiz-bot-24x7 \
  --image gcr.io/YOUR_PROJECT_ID/telegram-quiz-bot-24x7 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEPLOYMENT_MODE=cloud_run_24x7 \
  --min-instances 1 \
  --max-instances 2 \
  --cpu 1 \
  --memory 1Gi \
  --timeout 3600 \
  --port 8080
```

## 🔍 Step 3: Verify Deployment

After deployment, you'll get a URL like:
`https://telegram-quiz-bot-24x7-[HASH]-uc.a.run.app`

### Test the endpoints:

```bash
# Basic health check
curl https://YOUR_CLOUD_RUN_URL/

# Detailed health information
curl https://YOUR_CLOUD_RUN_URL/health

# Keep-alive endpoint
curl https://YOUR_CLOUD_RUN_URL/keep-alive

# Simple ping
curl https://YOUR_CLOUD_RUN_URL/ping
```

Expected responses:
- `/` → "🤖 Telegram Quiz Bot is running! 🎓"
- `/health` → JSON with uptime and status
- `/keep-alive` → JSON with ping count
- `/ping` → "pong"

## 🤖 Step 4: Test Your Bots

1. **Find your bots on Telegram**:
   - Teacher Bot: @QuizForCollegeBot (or your configured username)
   - Student Bot: @TestStudentCollegeBot

2. **Test Teacher Bot**:
   - Send `/start` - should prompt for password
   - Enter password: `jDQ&q9hjmeMIRbKstqZo!EsGREJ7M!YOSS#esY174rn@oI&f7T6VT7uNulQTWd2tgH6*uU3WgZPxt1Z#`
   - Send `/insertQuestions` to create a quiz

3. **Test Student Bot**:
   - Use the quiz link from teacher bot
   - Take the quiz and verify it works

## 🔄 Step 5: Set Up External Monitoring (Optional but Recommended)

### Option A: Using UptimeRobot (Free)

1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Create a free account
3. Add a new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://YOUR_CLOUD_RUN_URL/keep-alive`
   - **Interval**: 5 minutes
   - **Name**: Telegram Quiz Bot 24/7

### Option B: Using the External Monitor Script

```bash
# Run once to test
python external_keepalive_monitor.py https://YOUR_CLOUD_RUN_URL once

# Run continuously (every 5 minutes)
python external_keepalive_monitor.py https://YOUR_CLOUD_RUN_URL

# Run with custom interval (every 3 minutes)
python external_keepalive_monitor.py https://YOUR_CLOUD_RUN_URL continuous 3
```

### Option C: Cron Job

Add to your server's crontab:
```bash
# Keep-alive ping every 5 minutes
*/5 * * * * curl -s https://YOUR_CLOUD_RUN_URL/keep-alive > /dev/null

# Or use the Python script
*/5 * * * * /usr/bin/python3 /path/to/external_keepalive_monitor.py https://YOUR_CLOUD_RUN_URL once
```

## 📊 Step 6: Monitor Your Deployment

### View Logs
```bash
# View recent logs
gcloud run services logs read telegram-quiz-bot-24x7 --region us-central1

# Follow logs in real-time
gcloud run services logs tail telegram-quiz-bot-24x7 --region us-central1
```

### Check Service Status
```bash
# Get service details
gcloud run services describe telegram-quiz-bot-24x7 --region us-central1

# Check if service is receiving traffic
gcloud run services list --filter="metadata.name:telegram-quiz-bot-24x7"
```

### Monitor in Google Cloud Console
- Go to Cloud Run → telegram-quiz-bot-24x7
- Check metrics for CPU, memory, and requests
- Verify min-instances is set to 1

## 💰 Cost Optimization

### Expected Monthly Costs:
- **CPU**: ~$3-8/month (1 vCPU continuously)
- **Memory**: ~$1-3/month (1GB continuously)  
- **Requests**: ~$0.10/month (keep-alive pings)
- **Total**: ~$5-15/month for 24/7 operation

### Cost-Saving Tips:
1. **Use min-instances: 1** (prevents cold starts but costs more)
2. **Monitor resource usage** and adjust CPU/memory if needed
3. **Use external monitoring** instead of very frequent self-pings
4. **Set max-instances: 2** to prevent unexpected scaling costs

## 🚨 Troubleshooting

### Bot Not Responding
1. Check logs: `gcloud run services logs read telegram-quiz-bot-24x7`
2. Verify health endpoint: `curl https://YOUR_URL/health`
3. Check if min-instances is set to 1
4. Verify bot tokens are correct

### Service Scaling to Zero
1. Ensure min-instances is set to 1:
   ```bash
   gcloud run services update telegram-quiz-bot-24x7 --min-instances 1
   ```
2. Check if external monitoring is working
3. Verify keep-alive endpoints are being called

### High Costs
1. Check current resource allocation:
   ```bash
   gcloud run services describe telegram-quiz-bot-24x7
   ```
2. Reduce CPU/memory if usage is low:
   ```bash
   gcloud run services update telegram-quiz-bot-24x7 --cpu 0.5 --memory 512Mi
   ```

### Database Connection Issues
1. Verify Supabase credentials in your code
2. Check if Cloud Run can reach external services
3. Review logs for connection errors

## 🔄 Updates and Maintenance

### Update Your Bot
```bash
# Rebuild and redeploy
gcloud builds submit --config cloudbuild-24x7.yaml
```

### Change Configuration
```bash
# Update environment variables
gcloud run services update telegram-quiz-bot-24x7 \
  --set-env-vars NEW_VAR=value

# Update resource limits
gcloud run services update telegram-quiz-bot-24x7 \
  --cpu 1 --memory 1Gi
```

## ✅ Success Checklist

- [ ] Service deployed successfully
- [ ] Health endpoints respond correctly
- [ ] Both bots respond to Telegram messages
- [ ] Min-instances set to 1
- [ ] External monitoring configured
- [ ] Logs show both bots running
- [ ] Quiz creation and taking works
- [ ] Service stays alive for 24+ hours

## 🎉 You're Done!

Your Telegram Quiz Bot is now running 24/7 on Google Cloud Run with:

- ✅ **Continuous operation** - Never scales to zero
- ✅ **Auto-restart** - Recovers from crashes automatically  
- ✅ **Health monitoring** - Built-in status checks
- ✅ **External keep-alive** - Additional monitoring layer
- ✅ **Cost optimized** - Minimal resources for maximum uptime

Your bots will now work reliably around the clock! 🚀
