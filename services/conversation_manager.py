# services/conversation_manager.py
from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta
from models import Conversation, Message, Lead
from config import ConversationState
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, ai_service, facebook_service):
        self.ai_service = ai_service
        self.facebook_service = facebook_service
        self.active_conversations = {}
        self.context_window = timedelta(minutes=30)  # Context retention time
        
    def handle_message(self, messenger_id: str, message_text: str) -> bool:
        """Handle incoming message and maintain conversation context."""
        try:
            # Get or create conversation context
            conversation = self._get_active_conversation(messenger_id)
            if not conversation:
                conversation = self._load_conversation(messenger_id)
            
            # Store user message
            self._store_message(conversation.id, message_text, 'user')
            
            # Analyze intent with context
            context = self._get_conversation_context(conversation)
            intent = self.ai_service.analyze_intent_with_context(message_text, context)
            
            # Generate contextual response
            response = self.ai_service.generate_response(
                conversation.state,
                intent,
                context
            )
            
            # Store AI response
            self._store_message(conversation.id, response, 'system')
            
            # Update conversation state
            new_state = self._determine_new_state(conversation.state, intent)
            conversation.state = new_state
            conversation.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Send response
            self.facebook_service.send_messenger_message(messenger_id, response)
            
            # Update active conversations cache
            self._update_active_conversation(messenger_id, conversation)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return False
    
    def _get_active_conversation(self, messenger_id: str) -> Optional[Conversation]:
        """Get conversation from active cache if exists and not expired."""
        if messenger_id in self.active_conversations:
            conv_data = self.active_conversations[messenger_id]
            if datetime.utcnow() - conv_data['last_active'] <= self.context_window:
                return conv_data['conversation']
        return None
    
    def _load_conversation(self, messenger_id: str) -> Conversation:
        """Load conversation from database."""
        lead = Lead.query.filter_by(messenger_id=messenger_id).first()
        conversation = Conversation.query.filter_by(lead_id=lead.id)\
            .order_by(Conversation.created_at.desc())\
            .first()
        
        if not conversation:
            conversation = Conversation(
                lead_id=lead.id,
                state=ConversationState.INITIAL
            )
            db.session.add(conversation)
            db.session.commit()
        
        return conversation
    
    def _store_message(self, conversation_id: int, content: str, sender_type: str):
        """Store message in database."""
        message = Message(
            conversation_id=conversation_id,
            content=content,
            sender_type=sender_type
        )
        db.session.add(message)
        db.session.commit()
    
    def _get_conversation_context(self, conversation: Conversation) -> Dict[str, Any]:
        """Build conversation context from recent messages."""
        recent_messages = Message.query.filter_by(conversation_id=conversation.id)\
            .order_by(Message.created_at.desc())\
            .limit(5)\
            .all()
        
        return {
            'state': conversation.state.value,
            'recent_messages': [
                {
                    'content': msg.content,
                    'sender_type': msg.sender_type,
                    'timestamp': msg.created_at.isoformat()
                }
                for msg in reversed(recent_messages)
            ],
            'lead_info': {
                'name': conversation.lead.name,
                'interaction_count': Message.query.filter_by(
                    conversation_id=conversation.id
                ).count()
            }
        }
    
    def _update_active_conversation(self, messenger_id: str, conversation: Conversation):
        """Update active conversations cache."""
        self.active_conversations[messenger_id] = {
            'conversation': conversation,
            'last_active': datetime.utcnow()
        }
    
    def cleanup_inactive_conversations(self):
        """Remove expired conversations from cache."""
        current_time = datetime.utcnow()
        self.active_conversations = {
            messenger_id: data
            for messenger_id, data in self.active_conversations.items()
            if current_time - data['last_active'] <= self.context_window
        }