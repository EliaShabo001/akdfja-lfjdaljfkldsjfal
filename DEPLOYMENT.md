# 🚀 Google Cloud Run Deployment Guide

This guide will help you deploy your Telegram Quiz Bot to Google Cloud Run using webhooks for optimal performance and cost efficiency.

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed locally
3. **Docker** installed (optional, Cloud Build will handle this)
4. **Project ID** in Google Cloud Console

## 🔧 Setup Steps

### 1. Initialize Google Cloud Project

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

### 2. Deploy to Cloud Run

#### Option A: Using Cloud Build (Recommended)

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Note: Update the WEBHOOK_URL in cloudbuild.yaml with your actual Cloud Run URL
```

#### Option B: Manual Deployment

```bash
# Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/telegram-quiz-bot

# Deploy to Cloud Run
gcloud run deploy telegram-quiz-bot \
  --image gcr.io/YOUR_PROJECT_ID/telegram-quiz-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars WEBHOOK_URL=https://YOUR_CLOUD_RUN_URL
```

### 3. Configure Webhook

After deployment, you'll get a Cloud Run URL like:
`https://telegram-quiz-bot-[HASH]-uc.a.run.app`

#### Set the webhook:

```bash
# Visit this URL in your browser to set the webhook
https://YOUR_CLOUD_RUN_URL/set_webhook
```

Or use curl:
```bash
curl https://YOUR_CLOUD_RUN_URL/set_webhook
```

#### Verify webhook:

```bash
# Check webhook status
curl https://YOUR_CLOUD_RUN_URL/webhook_info
```

## 🔍 Testing

### Health Check
```bash
curl https://YOUR_CLOUD_RUN_URL/
# Should return: "🤖 Telegram Quiz Bot is running! 🎓"
```

### Bot Testing
1. Find your bot on Telegram: `@YourBotUsername`
2. Send `/start` - should prompt for password
3. Enter the admin password
4. Test creating a quiz with `/insertQuestions`

## 📊 Monitoring

### View Logs
```bash
gcloud run services logs read telegram-quiz-bot --region us-central1
```

### Monitor Performance
- Visit Google Cloud Console → Cloud Run → telegram-quiz-bot
- Check metrics for requests, latency, and errors

## 💰 Cost Optimization

Cloud Run pricing is based on:
- **CPU and Memory usage** (only when processing requests)
- **Number of requests**
- **Networking**

Benefits of webhook approach:
- ✅ **Pay per use** - no cost when idle
- ✅ **Auto-scaling** - handles traffic spikes
- ✅ **Zero maintenance** - Google manages infrastructure
- ✅ **Global availability** - fast response times

## 🔧 Environment Variables

Set these in Cloud Run:

| Variable | Description | Example |
|----------|-------------|---------|
| `WEBHOOK_URL` | Your Cloud Run URL | `https://telegram-quiz-bot-abc123-uc.a.run.app` |
| `PORT` | Port number (auto-set by Cloud Run) | `8080` |
| `ENVIRONMENT` | Set to `production` | `production` |

## 🚨 Troubleshooting

### Common Issues:

1. **Webhook not working**
   - Check if `/set_webhook` was called
   - Verify WEBHOOK_URL environment variable
   - Check Cloud Run logs for errors

2. **Bot not responding**
   - Verify bot token is correct
   - Check if webhook is set properly
   - Review application logs

3. **Database connection issues**
   - Verify Supabase credentials
   - Check network connectivity from Cloud Run

### Debug Commands:

```bash
# Check webhook status
curl https://YOUR_CLOUD_RUN_URL/webhook_info

# View recent logs
gcloud run services logs read telegram-quiz-bot --region us-central1 --limit 50

# Check service status
gcloud run services describe telegram-quiz-bot --region us-central1
```

## 🔄 Updates

To update your bot:

```bash
# Rebuild and redeploy
gcloud builds submit --config cloudbuild.yaml
```

The new version will automatically replace the old one with zero downtime.

## 🎯 Production Checklist

- [ ] Bot token is secure and not exposed in code
- [ ] Webhook URL is correctly set
- [ ] Database credentials are configured
- [ ] Health check endpoint responds
- [ ] Bot responds to `/start` command
- [ ] Password protection works
- [ ] Quiz creation and taking functions work
- [ ] Monitoring and logging are set up

## 📞 Support

If you encounter issues:
1. Check the logs first: `gcloud run services logs read telegram-quiz-bot`
2. Verify webhook status: `curl YOUR_URL/webhook_info`
3. Test health endpoint: `curl YOUR_URL/`

Your bot is now running 24/7 on Google Cloud Run! 🎉
