# 🔄 Polling + Keep-Alive Deployment Guide

This guide explains how to deploy your Telegram Quiz Bot using **polling with keep-alive** on Google Cloud Run. This approach combines the simplicity of polling with the cloud benefits of HTTP endpoints.

## 🎯 Why Polling + Keep-Alive?

### ✅ Benefits:
- **Simple setup** - No webhook configuration needed
- **Familiar polling** - Same bot logic as local development
- **Cloud Run compatible** - HTTP server prevents scale-to-zero
- **Cost effective** - Runs continuously but only uses resources when active
- **Easy monitoring** - Built-in health check endpoints

### ⚖️ Trade-offs:
- **Slightly higher cost** - Keeps one instance running (but minimal)
- **Resource usage** - Uses CPU for polling even when idle
- **Less efficient** - Not as optimal as pure webhooks for high traffic

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Cloud Run      │    │  Uptime Monitor │
│   Bot API       │◄──►│  ┌─────────────┐ │◄──►│  (UptimeRobot)  │
│                 │    │  │ Polling Bot │ │    │                 │
└─────────────────┘    │  └─────────────┘ │    └─────────────────┘
                       │  ┌─────────────┐ │
                       │  │ HTTP Server │ │
                       │  └─────────────┘ │
                       └──────────────────┘
```

## 🚀 Deployment Steps

### 1. Deploy to Cloud Run

```bash
# Deploy using the polling-specific configuration
gcloud builds submit --config cloudbuild-polling.yaml

# Or deploy manually
gcloud run deploy telegram-quiz-bot-polling \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEPLOYMENT_MODE=polling_keepalive \
  --min-instances 1 \
  --max-instances 1 \
  --cpu 1 \
  --memory 512Mi \
  --timeout 3600
```

### 2. Get Your Cloud Run URL

After deployment, you'll get a URL like:
```
https://telegram-quiz-bot-polling-[HASH]-uc.a.run.app
```

### 3. Test the Deployment

```bash
# Test health check
curl https://YOUR_CLOUD_RUN_URL/

# Test keep-alive endpoint
curl https://YOUR_CLOUD_RUN_URL/keep-alive

# Test detailed health check
curl https://YOUR_CLOUD_RUN_URL/health
```

### 4. Set Up Uptime Monitoring

#### Option A: UptimeRobot (Recommended)
1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Create a free account
3. Add a new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://YOUR_CLOUD_RUN_URL/keep-alive`
   - **Interval**: 5 minutes
   - **Name**: Telegram Quiz Bot Keep-Alive

#### Option B: Google Cloud Monitoring
```bash
# Create uptime check
gcloud alpha monitoring uptime create \
  --display-name="Telegram Bot Keep-Alive" \
  --http-check-path="/keep-alive" \
  --hostname="YOUR_CLOUD_RUN_URL" \
  --period=300
```

#### Option C: Cron Job (Simple)
```bash
# Add to your server's crontab
*/5 * * * * curl -s https://YOUR_CLOUD_RUN_URL/keep-alive > /dev/null
```

## 🧪 Local Testing

Test the polling + keep-alive mode locally:

```bash
# Run in polling + keep-alive mode
python run_polling_keepalive.py
```

This will:
- Start the bot with polling in a background thread
- Start HTTP server for keep-alive endpoints
- Simulate uptime monitoring pings
- Show you how it works before deploying

## 📊 Monitoring & Debugging

### Check Bot Status
```bash
# Health check with bot info
curl https://YOUR_CLOUD_RUN_URL/health
```

### View Logs
```bash
# View Cloud Run logs
gcloud run services logs read telegram-quiz-bot-polling --region us-central1

# Follow logs in real-time
gcloud run services logs tail telegram-quiz-bot-polling --region us-central1
```

### Monitor Resource Usage
- Visit Google Cloud Console → Cloud Run → telegram-quiz-bot-polling
- Check CPU and memory usage
- Monitor request patterns

## 💰 Cost Estimation

With polling + keep-alive on Cloud Run:

- **CPU**: ~0.1 vCPU continuously = ~$3-5/month
- **Memory**: 512Mi continuously = ~$1-2/month
- **Requests**: Keep-alive pings = minimal cost
- **Total**: ~$5-10/month for 24/7 operation

Compare to:
- **Pure webhooks**: $0 when idle, pay per request
- **Traditional VPS**: $5-20/month for basic server

## 🔧 Configuration Options

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DEPLOYMENT_MODE` | `polling_keepalive` | Enables polling + keep-alive mode |
| `PORT` | `8080` | HTTP server port (auto-set by Cloud Run) |

### Cloud Run Settings

```yaml
# Recommended settings for polling + keep-alive
min-instances: 1        # Keep at least 1 instance running
max-instances: 1        # Only need 1 instance for polling
cpu: 1                  # 1 vCPU is sufficient
memory: 512Mi          # 512MB memory is enough
timeout: 3600          # 1 hour timeout (max for Cloud Run)
```

## 🚨 Troubleshooting

### Bot Not Responding
1. Check if polling is working:
   ```bash
   curl https://YOUR_CLOUD_RUN_URL/health
   ```
2. View logs for polling errors:
   ```bash
   gcloud run services logs read telegram-quiz-bot-polling
   ```

### Keep-Alive Not Working
1. Test the endpoint:
   ```bash
   curl https://YOUR_CLOUD_RUN_URL/keep-alive
   ```
2. Check uptime monitoring service configuration
3. Verify Cloud Run min-instances is set to 1

### High Costs
1. Check if you have multiple instances running
2. Verify min-instances and max-instances are both set to 1
3. Monitor CPU and memory usage in Cloud Console

## 🔄 Switching Between Modes

### To Webhook Mode
```bash
# Deploy with webhook mode
gcloud run deploy telegram-quiz-bot \
  --source . \
  --set-env-vars DEPLOYMENT_MODE=webhook

# Set webhook
curl https://YOUR_NEW_URL/set_webhook
```

### To Polling + Keep-Alive Mode
```bash
# Deploy with polling + keep-alive mode
gcloud run deploy telegram-quiz-bot-polling \
  --source . \
  --set-env-vars DEPLOYMENT_MODE=polling_keepalive \
  --min-instances 1
```

## 📋 Production Checklist

- [ ] Bot deployed with `DEPLOYMENT_MODE=polling_keepalive`
- [ ] Min-instances set to 1
- [ ] Health check endpoint responds
- [ ] Keep-alive endpoint responds
- [ ] Uptime monitoring configured (5-minute intervals)
- [ ] Bot responds to Telegram messages
- [ ] Password protection works
- [ ] All quiz features functional
- [ ] Logs show successful polling
- [ ] Resource usage monitored

## 🎉 Success!

Your bot is now running 24/7 on Google Cloud Run with polling + keep-alive! 

- ✅ **Continuous operation** - Bot polls Telegram constantly
- ✅ **Cloud benefits** - Auto-scaling, monitoring, logging
- ✅ **Simple setup** - No webhook configuration needed
- ✅ **Cost effective** - Predictable monthly cost
- ✅ **Reliable** - Uptime monitoring keeps it alive

The bot will now work exactly like it does locally, but with the benefits of cloud deployment!
