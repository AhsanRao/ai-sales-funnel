# config.py
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

class ConversationState(Enum):
    INITIAL = "initial"
    EXPLAINING = "explaining"
    PRICING_DISCUSSED = "pricing_discussed"
    READY_TO_BUY = "ready_to_buy"
    HESITATING = "hesitating"
    FOLLOW_UP = "follow_up"

class Config:
    # API Keys and Credentials
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    
    # Campaign Configuration
    VALID_CAMPAIGN_IDS = ["987654321", "555555666", "777777888"]
    PRODUCT_PRICE = 2500
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Follow-up Configuration
    CALENDLY_LINK = os.getenv("CALENDLY_LINK")
    CHECKOUT_LINK_BASE = os.getenv("CHECKOUT_LINK_BASE")