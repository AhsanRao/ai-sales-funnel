# tests/test_ai_service.py
import unittest
from unittest.mock import patch, MagicMock
from services.ai_service import AIService
from config import ConversationState

class TestAIService(unittest.TestCase):
    def setUp(self):
        self.service = AIService()
    
    @patch('openai.ChatCompletion.create')
    def test_analyze_intent(self, mock_create):
        """Test intent analysis."""
        mock_create.return_value.choices = [
            MagicMock(message={'content': 'ready_to_buy'})
        ]
        
        intent = self.service.analyze_intent('I want to buy')
        
        self.assertIn('intent', intent)
        self.assertIn('confidence', intent)
        mock_create.assert_called_once()