# services/follow_up_service.py
from twilio.rest import Client
from datetime import datetime, timedelta
from typing import Dict, Any
from config import Config
from models import FollowUp
import logging

logger = logging.getLogger(__name__)

class FollowUpService:
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
    def schedule_follow_ups(self, lead_id: int) -> bool:
        """Schedule follow-up messages."""
        try:
            now = datetime.utcnow()
            
            # Schedule 24-hour follow-up
            follow_up_24h = FollowUp(
                lead_id=lead_id,
                type='24h',
                status='pending',
                scheduled_at=now + timedelta(hours=24)
            )
            
            # Schedule 48-hour follow-up
            follow_up_48h = FollowUp(
                lead_id=lead_id,
                type='48h',
                status='pending',
                scheduled_at=now + timedelta(hours=48)
            )
            
            db.session.add(follow_up_24h)
            db.session.add(follow_up_48h)
            db.session.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to schedule follow-ups: {str(e)}")
            return False

    def send_follow_up(self, follow_up: FollowUp) -> bool:
        """Send follow-up message via Twilio SMS."""
        try:
            lead = follow_up.lead
            message = self._get_follow_up_message(follow_up.type)
            
            # Send SMS
            self.client.messages.create(
                to=lead.phone,
                from_=Config.TWILIO_PHONE_NUMBER,
                body=message
            )
            
            # Update follow-up status
            follow_up.status = 'sent'
            follow_up.sent_at = datetime.utcnow()
            db.session.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to send follow-up: {str(e)}")
            follow_up.status = 'failed'
            db.session.commit()
            return False

    def _get_follow_up_message(self, follow_up_type: str) -> str:
        """Get appropriate follow-up message based on type."""
        if follow_up_type == '24h':
            return f"Follow up on your interest! Book a call here: {Config.CALENDLY_LINK}"
        elif follow_up_type == '48h':
            return f"Last chance! Complete your purchase here: {Config.CHECKOUT_LINK_BASE}"
        else:
            return "Thank you for your interest in our product."