# services/ai_service.py
import openai
from typing import Dict, Any
from config import Config, ConversationState
import json
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        
    def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message intent using GPT-4."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Analyze the following message for sales conversation intent."},
                    {"role": "user", "content": message}
                ]
            )
            
            # Process and categorize the response
            analysis = self._categorize_intent(response.choices[0].message['content'])
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze intent: {str(e)}")
            return {"intent": "unknown", "confidence": 0.0}
        
    def analyze_intent_with_context(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user message intent with conversation context."""
        try:
            # Create a prompt that includes context
            context_prompt = f"""
            Conversation State: {context['state']}
            Recent Messages: {json.dumps(context['recent_messages'], indent=2)}
            Lead Info: {json.dumps(context['lead_info'], indent=2)}
            
            Analyze the intent of this message: {message}
            
            Categorize the intent into one of the following:
            - ready_to_buy: User expresses clear intention to purchase
            - price_inquiry: User asks about pricing
            - hesitation: User shows concerns or objections
            - needs_explanation: User needs more information
            - general_interest: User shows interest but no clear intent
            - unrelated: Message is not related to the sales conversation
            
            Also provide a confidence score between 0 and 1.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are analyzing user intent in a sales conversation."},
                    {"role": "user", "content": context_prompt}
                ]
            )
            
            # Process and categorize the response
            analysis = self._categorize_intent(response.choices[0].message['content'])
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze intent with context: {str(e)}")
            return {"intent": "unknown", "confidence": 0.0}
    
    def generate_response(self, state: ConversationState, intent: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Generate appropriate response based on conversation state and user intent."""
        try:
            prompt = self._create_prompt(state, intent, context)
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are an AI sales assistant helping with a $2,500 product.
                    Be professional, empathetic, and focused on addressing the customer's needs.
                    Keep responses concise but informative."""},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message['content']
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return self._get_fallback_response(state)

    def _categorize_intent(self, analysis: str) -> Dict[str, Any]:
        """Categorize the intent analysis into structured data."""
        try:
            # Extract intent and confidence from GPT response
            analysis_lower = analysis.lower()
            
            intent_types = {
                'ready_to_buy': ['ready to buy', 'want to purchase', 'take it', 'buy now'],
                'price_inquiry': ['price', 'cost', 'how much', 'pricing'],
                'hesitation': ['hesitant', 'concern', 'worry', 'think about', 'not sure'],
                'needs_explanation': ['explain', 'tell me more', 'what is', 'how does'],
                'general_interest': ['interested', 'tell me', 'learn more'],
                'unrelated': ['unrelated', 'off topic', 'not relevant']
            }
            
            # Determine intent
            determined_intent = 'unknown'
            for intent_type, keywords in intent_types.items():
                if any(keyword in analysis_lower for keyword in keywords):
                    determined_intent = intent_type
                    break
            
            # Extract confidence score
            confidence = 0.0
            if 'confidence' in analysis_lower:
                try:
                    confidence_text = analysis_lower.split('confidence')[1]
                    confidence = float(''.join(filter(lambda x: x.isdigit() or x == '.', confidence_text)))
                    confidence = min(max(confidence, 0.0), 1.0)
                except:
                    confidence = 0.7 if determined_intent != 'unknown' else 0.0
            
            return {
                'intent': determined_intent,
                'confidence': confidence,
                'raw_analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error categorizing intent: {str(e)}")
            return {'intent': 'unknown', 'confidence': 0.0}

    def _create_prompt(self, state: ConversationState, intent: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Create appropriate prompt based on conversation state and intent."""
        base_prompt = f"""
        Current conversation state: {state.value}
        Detected intent: {intent['intent']} (confidence: {intent['confidence']})
        """
        
        if context:
            base_prompt += f"""
            Recent conversation history:
            {json.dumps(context['recent_messages'], indent=2)}
            
            Customer name: {context['lead_info']['name']}
            Interaction count: {context['lead_info']['interaction_count']}
            """
        
        state_specific_prompts = {
            ConversationState.INITIAL: """
            This is a new conversation. Provide a friendly welcome and briefly introduce the product.
            Focus on understanding the customer's needs.
            """,
            
            ConversationState.EXPLAINING: """
            The customer needs more information. Explain the key benefits and features
            of the product. Address any specific questions from the conversation history.
            """,
            
            ConversationState.PRICING_DISCUSSED: """
            Price has been discussed. Focus on value proposition and ROI.
            Address any concerns and emphasize the benefits that justify the price.
            """,
            
            ConversationState.READY_TO_BUY: """
            Customer shows strong buying intent. Provide clear next steps for purchase
            and make it easy for them to proceed with the transaction.
            """,
            
            ConversationState.HESITATING: """
            Customer is hesitating. Address their concerns empathetically and provide
            reassurance. Offer to schedule a call if needed.
            """,
            
            ConversationState.FOLLOW_UP: """
            This is a follow-up message. Remind them of their interest and any previous
            positive interactions. Provide a clear call to action.
            """
        }
        
        return base_prompt + state_specific_prompts.get(state, "")

    def _get_fallback_response(self, state: ConversationState) -> str:
        """Get fallback response for error cases."""
        fallback_responses = {
            ConversationState.INITIAL: "I apologize for the confusion. How can I help you learn more about our product?",
            ConversationState.EXPLAINING: "I'd be happy to explain our product features. What specific aspects interest you most?",
            ConversationState.PRICING_DISCUSSED: "Our product offers great value for its price. Would you like to discuss any specific aspects?",
            ConversationState.READY_TO_BUY: "Great! I can help you complete your purchase. Would you like to proceed?",
            ConversationState.HESITATING: "I understand your concerns. Would you like to schedule a call to discuss them?",
            ConversationState.FOLLOW_UP: "Just checking in to see if you have any questions about our product."
        }
        
        return fallback_responses.get(state, "I apologize for the confusion. How can I assist you today?")