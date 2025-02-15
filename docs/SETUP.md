# AI Sales Funnel System - Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [API Keys and Credentials](#api-keys-and-credentials)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Testing Webhooks](#testing-webhooks)
- [Troubleshooting](#troubleshooting)

## Prerequisites
- Python 3.9 or higher
- PostgreSQL
- ngrok (for webhook testing)
- Git

## Local Development Setup

1. Clone the repository and create virtual environment:
```bash
git clone [repository_url]
cd ai-sales-funnel
python -m venv venv
```

2. Activate virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

## API Keys and Credentials

### OpenAI Setup
1. Visit https://platform.openai.com/
2. Create or login to your account
3. Navigate to API Keys section
4. Create new secret key
5. Copy key for `.env` file

### Facebook Setup
1. Go to https://developers.facebook.com/
2. Create new app or use existing one
3. Set up Facebook Lead Ads
4. Get required credentials:
   - Access Token (with leads_retrieval permission)
   - App ID
   - App Secret
   - Create a Verify Token (any random string)

### Stripe Setup
1. Visit https://dashboard.stripe.com/
2. Create or login to your account
3. Go to Developers section
4. Get API keys:
   - Publishable Key (starts with 'pk_test_')
   - Secret Key (starts with 'sk_test_')

### Twilio Setup
1. Go to https://www.twilio.com/
2. Create or login to your account
3. Get credentials from Dashboard:
   - Account SID
   - Auth Token
   - Phone number (if needed)

## Database Setup

1. Install PostgreSQL if not already installed

2. Create database:
```sql
psql -U postgres
CREATE DATABASE sales_funnel;
```

3. Initialize database with Flask:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Environment Configuration

Create a `.env` file in project root:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token

# Facebook Configuration
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_VERIFY_TOKEN=your_webhook_verify_token

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/sales_funnel
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password

# Application Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secure_secret_key
DEBUG=True

# Product Configuration
PRODUCT_PRICE=2500
CHECKOUT_LINK_BASE=http://localhost:5000/checkout
CALENDLY_LINK=your_calendly_link

# Local Testing Webhook URLs
FACEBOOK_WEBHOOK_URL=https://your_ngrok_url/webhook/facebook
STRIPE_WEBHOOK_URL=https://your_ngrok_url/webhook/stripe
MESSENGER_WEBHOOK_URL=https://your_ngrok_url/webhook/messenger
```

## Running the Application

1. Start ngrok for webhook testing:
```bash
ngrok http 5000
```

2. Update webhook URLs in `.env` with ngrok URL

3. Run the Flask application:
```bash
flask run
```

## Testing Webhooks

### Test Facebook Lead Webhook
```bash
curl -X POST http://localhost:5000/webhook/facebook \
-H "Content-Type: application/json" \
-d '{
  "id": "test_lead_id",
  "campaign_id": "987654321",
  "name": "Test User",
  "email": "test@example.com",
  "phone": "+1234567890",
  "messenger_id": "test_messenger_id"
}'
```

### Test Messenger Webhook
```bash
curl -X POST http://localhost:5000/webhook/messenger \
-H "Content-Type: application/json" \
-d '{
  "entry": [{
    "messaging": [{
      "sender": {
        "id": "test_messenger_id"
      },
      "message": {
        "text": "Hello, I am interested in your product"
      }
    }]
  }]
}'
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Webhook Testing Issues**
   - Verify ngrok is running and URL is current
   - Check webhook URLs in service dashboards
   - Verify API keys have correct permissions

3. **API Authentication Errors**
   - Verify all API keys are correctly set in `.env`
   - Check API key permissions in respective dashboards
   - Ensure you're using correct keys (test vs production)

### Getting Help

- Check application logs: `flask run --debug`
- Review service-specific documentation:
  - [OpenAI API Docs](https://platform.openai.com/docs/)
  - [Facebook Lead Ads Docs](https://developers.facebook.com/docs/marketing-api/guides/lead-ads/)
  - [Stripe API Docs](https://stripe.com/docs/api)
  - [Twilio API Docs](https://www.twilio.com/docs/)