# app.py
from typing import Dict
from config import Config, ConversationState
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from models import Conversation, FollowUp, PaymentStatus
from services.conversation_manager import ConversationManager
from services.facebook_service import FacebookService
from services.ai_service import AIService
from services.payment_service import PaymentService
from services.follow_up_service import FollowUpService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
db = SQLAlchemy(app)

# Initialize services
facebook_service = FacebookService()
ai_service = AIService()
payment_service = PaymentService()
follow_up_service = FollowUpService()
conversation_manager = ConversationManager(ai_service, facebook_service)

# Initialize scheduler
scheduler = BackgroundScheduler()

def process_pending_follow_ups():
    """Process all pending follow-ups that are due."""
    try:
        now = datetime.utcnow()
        pending_follow_ups = FollowUp.query.filter(
            FollowUp.status == 'pending',
            FollowUp.scheduled_at <= now
        ).all()
        
        for follow_up in pending_follow_ups:
            follow_up_service.send_follow_up(follow_up)
            
    except Exception as e:
        logger.error(f"Error processing pending follow-ups: {str(e)}")

def check_abandoned_conversations():
    """Check for conversations that need follow-up."""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        abandoned_conversations = Conversation.query.filter(
            Conversation.updated_at <= cutoff_time,
            Conversation.state.in_([
                ConversationState.PRICING_DISCUSSED,
                ConversationState.HESITATING
            ])
        ).all()
        
        for conversation in abandoned_conversations:
            follow_up_service.schedule_follow_ups(conversation.lead.id)
            
    except Exception as e:
        logger.error(f"Error checking abandoned conversations: {str(e)}")

def clean_stale_sessions():
    """Clean up stale payment sessions."""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        stale_sessions = PaymentStatus.query.filter(
            PaymentStatus.status == 'pending',
            PaymentStatus.created_at <= cutoff_time
        ).all()
        
        for session in stale_sessions:
            payment_service.cancel_checkout_session(session.stripe_session_id)
            session.status = 'expired'
        
        db.session.commit()
    except Exception as e:
        logger.error(f"Error cleaning stale sessions: {str(e)}")

# Schedule automated tasks
scheduler.add_job(
    func=process_pending_follow_ups,
    trigger=IntervalTrigger(minutes=5),
    id='process_follow_ups',
    name='Process pending follow-ups'
)

scheduler.add_job(
    func=check_abandoned_conversations,
    trigger=CronTrigger(hour='*/1'),  # Every hour
    id='check_abandoned',
    name='Check abandoned conversations'
)

scheduler.add_job(
    func=clean_stale_sessions,
    trigger=CronTrigger(hour=0),  # Once per day at midnight
    id='clean_sessions',
    name='Clean stale payment sessions'
)

scheduler.add_job(
    func=conversation_manager.cleanup_inactive_conversations,
    trigger=IntervalTrigger(minutes=15),
    id='cleanup_conversations',
    name='Cleanup inactive conversations'
)

# Start the scheduler when the app starts
@app.before_first_request
def start_scheduler():
    scheduler.start()

@app.route('/webhook/facebook', methods=['POST'])
def facebook_webhook():
    """Handle Facebook lead webhook."""
    try:
        data = request.json
        
        if not facebook_service.validate_lead(data):
            return jsonify({'status': 'error', 'message': 'Invalid campaign ID'}), 400
        
        lead, conversation = facebook_service.process_lead(data)
        db.session.add(lead)
        db.session.add(conversation)
        db.session.commit()
        
        # Schedule follow-ups
        follow_up_service.schedule_follow_ups(lead.id)
        
        # Send initial message
        initial_message = ai_service.generate_response(
            ConversationState.INITIAL,
            {"intent": "initial_contact", "confidence": 1.0}
        )
        facebook_service.send_messenger_message(lead.messenger_id, initial_message)
        
        return jsonify({'status': 'success', 'lead_id': lead.id}), 200
    except Exception as e:
        logger.error(f"Error processing Facebook webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/webhook/messenger', methods=['POST'])
def messenger_webhook():
    """Handle Facebook Messenger webhook."""
    try:
        data = request.json
        messaging = data['entry'][0]['messaging'][0]
        sender_id = messaging['sender']['id']
        message = messaging.get('message', {}).get('text', '')
        
        # Use conversation manager to handle the message
        conversation_manager.handle_message(sender_id, message)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error processing Messenger webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook."""
    try:
        event_data = request.json
        signature = request.headers.get('Stripe-Signature')
        
        # Handle the webhook event
        if payment_service.handle_webhook(event_data):
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid event type'}), 400
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

