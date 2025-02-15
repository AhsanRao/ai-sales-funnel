# AI Sales Funnel System

An automated sales funnel system that integrates Facebook leads with AI-powered conversations, payment processing, and automated follow-ups.

## Features

- 🤖 AI-Powered Conversation Management
- 📊 Facebook Lead Capture & Filtering
- 💬 Messenger Integration
- 💳 Stripe Payment Processing
- 📱 SMS Follow-up System
- 📅 Calendar Integration

## Tech Stack

- Python 3.8+
- Flask
- OpenAI GPT-4
- PostgreSQL/MongoDB
- Facebook Messenger API
- Stripe API
- Twilio API

## Prerequisites

- Python 3.8 or higher
- PostgreSQL or MongoDB
- API Keys for:
  - Facebook
  - OpenAI
  - Stripe
  - Twilio

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AhsanRao/ai-sales-funnel.git
cd ai-sales-funnel
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r deployment/requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

Create a `.env` file with the following variables (see env.example):
```
FB_PAGE_ACCESS_TOKEN=your_facebook_token
OPENAI_API_KEY=your_openai_key
STRIPE_SECRET_KEY=your_stripe_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_phone
DATABASE_URL=your_database_url
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Set up Facebook webhook:
- Use ngrok or similar for local development
- Configure webhook URL in Facebook Developer Console
- Set up webhook events for lead generation

3. Configure Stripe:
- Set up product in Stripe dashboard
- Update checkout link in configuration

## Project Structure

```
ai-sales-funnel/
├── app.py
├── config.py
├── models.py
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SETUP.md
├── services/
│   ├── ai_service.py
│   ├── conversation_manager.py
│   ├── facebook_service.py
│   ├── follow_up_service.py
│   └── payment_service.py
├── tests/
│   ├── test_ai_service.py
│   └── test_facebook_service.py
├── env.example
├── LICENSE
└── README.md
```

## Documentation

Detailed documentation can be found in the `docs` directory:
- `API.md` - API endpoints and usage
- `DEPLOYMENT.md` - Deployment instructions
- `SETUP.md` - Detailed setup guide

## Development

1. Create new branch:
```bash
git checkout -b feature/your-feature
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
```

## Deployment

For detailed deployment instructions, please refer to `docs/DEPLOYMENT.md`. The project includes Docker support with configuration files in the `deployment` directory.

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - see LICENSE file for details