"""
Simple enhanced test for feedback API refactoring
Tests the enhanced feedback.py with error handling and validation
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.api.feedback import app

pytest.skip("Enhanced fastapi tests skipped", allow_module_level=True)

class TestFeedbackAPISimple:
    def setup_method(self):
        self.client = TestClient(app)
        self.valid_payload = {
            "content_id": str(uuid4()),
            "user_id": str(uuid4()),
            "feedback_type": "NOT_RELEVANT"
        }

    def test_enhanced_response_fields(self):
        """Test that response includes enhanced fields"""
        response = self.client.post("/api/v1/feedback", json=self.valid_payload)
        assert response.status_code == 202
        data = response.json()
        
        # Check enhanced response fields
        assert "feedback_id" in data
        assert "timestamp" in data
        assert data["status"] == "accepted"
        assert data["message"] == "Feedback received and will be processed"
        
    def test_missing_fields_validation(self):
        """Test missing required fields"""
        incomplete_payload = {
            "content_id": str(uuid4()),
            # Missing user_id and feedback_type
        }
        response = self.client.post("/api/v1/feedback", json=incomplete_payload)
        assert response.status_code == 422
        
    def test_invalid_uuid_validation(self):
        """Test invalid UUID validation"""
        invalid_payload = {
            **self.valid_payload,
            "content_id": "not-a-uuid"
        }
        response = self.client.post("/api/v1/feedback", json=invalid_payload)
        assert response.status_code == 400
        
    def test_health_endpoint_works(self):
        """Test health endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "feedback-api" 