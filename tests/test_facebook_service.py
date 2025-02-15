# tests/test_facebook_service.py
import unittest
from unittest.mock import patch, MagicMock
from services.facebook_service import FacebookService
from config import Config

class TestFacebookService(unittest.TestCase):
    def setUp(self):
        self.service = FacebookService()
        
    def test_validate_lead(self):
        """Test lead validation."""
        valid_lead = {'campaign_id': Config.VALID_CAMPAIGN_IDS[0]}
        invalid_lead = {'campaign_id': 'invalid_id'}
        
        self.assertTrue(self.service.validate_lead(valid_lead))
        self.assertFalse(self.service.validate_lead(invalid_lead))
    
    @patch('requests.post')
    def test_send_messenger_message(self, mock_post):
        """Test sending Messenger message."""
        mock_post.return_value.status_code = 200
        
        result = self.service.send_messenger_message(
            'test_messenger_id',
            'Test message'
        )
        
        self.assertTrue(result)
        mock_post.assert_called_once()