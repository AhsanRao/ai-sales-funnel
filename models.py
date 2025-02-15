# models.py
from datetime import datetime
from config import ConversationState
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    facebook_lead_id = Column(String, unique=True)
    campaign_id = Column(String)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    messenger_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="lead")

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    state = Column(Enum(ConversationState))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    content = Column(String)
    sender_type = Column(String)  # 'system' or 'user'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class PaymentStatus(Base):
    __tablename__ = 'payment_status'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    stripe_session_id = Column(String)
    amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FollowUp(Base):
    __tablename__ = 'follow_ups'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    type = Column(String)  # '24h' or '48h'
    status = Column(String)  # 'pending', 'sent', 'failed'
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime, nullable=True)