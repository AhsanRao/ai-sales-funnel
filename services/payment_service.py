# services/payment_service.py
import stripe
from typing import Dict, Any
from config import Config
from models import PaymentStatus
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        stripe.api_key = Config.STRIPE_SECRET_KEY
        
    def create_checkout_session(self, lead_id: int) -> Dict[str, Any]:
        """Create Stripe checkout session."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': Config.PRODUCT_PRICE * 100,
                        'product_data': {
                            'name': 'Product Name',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{Config.CHECKOUT_LINK_BASE}/success',
                cancel_url=f'{Config.CHECKOUT_LINK_BASE}/cancel',
                metadata={'lead_id': lead_id}
            )
            
            # Store payment status
            payment_status = PaymentStatus(
                lead_id=lead_id,
                stripe_session_id=session.id,
                amount=Config.PRODUCT_PRICE,
                status='pending'
            )
            
            return {
                'session_id': session.id,
                'checkout_url': session.url
            }
        except Exception as e:
            logger.error(f"Failed to create checkout session: {str(e)}")
            raise

    def handle_webhook(self, event_data: Dict[str, Any]) -> bool:
        """Handle Stripe webhook events."""
        try:
            event = stripe.Event.construct_from(event_data, stripe.api_key)
            
            if event.type == 'checkout.session.completed':
                session = event.data.object
                lead_id = session.metadata.get('lead_id')
                
                # Update payment status
                payment_status = PaymentStatus.query.filter_by(
                    stripe_session_id=session.id
                ).first()
                
                if payment_status:
                    payment_status.status = 'completed'
                    db.session.commit()
                
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to handle webhook: {str(e)}")
            raise