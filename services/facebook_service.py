# services/facebook_service.py
import requests
from typing import Dict, Any
from models import Lead, Conversation
from config import Config, ConversationState
import logging

logger = logging.getLogger(__name__)

class FacebookService:
    def __init__(self):
        self.access_token = Config.FACEBOOK_ACCESS_TOKEN
        
    def validate_lead(self, lead_data: Dict[str, Any]) -> bool:
        """Validate incoming Facebook lead data."""
        campaign_id = lead_data.get('campaign_id')
        return campaign_id in Config.VALID_CAMPAIGN_IDS
    
    def process_lead(self, lead_data: Dict[str, Any]) -> Lead:
        """Process and store Facebook lead data."""
        lead = Lead(
            facebook_lead_id=lead_data['id'],
            campaign_id=lead_data['campaign_id'],
            name=lead_data['name'],
            email=lead_data['email'],
            phone=lead_data['phone'],
            messenger_id=lead_data['messenger_id']
        )
        
        # Initialize conversation
        conversation = Conversation(
            lead=lead,
            state=ConversationState.INITIAL
        )
        
        return lead, conversation

    def send_messenger_message(self, messenger_id: str, message: str) -> bool:
        """Send message through Facebook Messenger."""
        url = f"https://graph.facebook.com/v12.0/me/messages"
        payload = {
            "recipient": {"id": messenger_id},
            "message": {"text": message}
        }
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Messenger message: {str(e)}")
            return False