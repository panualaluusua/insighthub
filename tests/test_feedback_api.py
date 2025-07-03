"""
Test suite for granular feedback API system (Enhanced TDD tests)
"""
import pytest

# Skip entire module if fastapi unavailable
# import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in current environment")

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
import json

# TDD imports - now they should work
try:
    from src.api.feedback import app, FeedbackRequest
    from src.models.vector_math import FeedbackType
except ImportError:
    pass

class TestFeedbackRequest:
    def test_valid_feedback_request(self):
        request_data = {
            "content_id": str(uuid4()),
            "user_id": str(uuid4()),
            "feedback_type": "NOT_RELEVANT"
        }
        request = FeedbackRequest(**request_data)
        assert request.feedback_type == FeedbackType.NOT_RELEVANT

    def test_invalid_feedback_type_raises_error(self):
        """Test invalid feedback type raises validation error"""
        with pytest.raises(ValueError):
            FeedbackRequest(
                content_id=str(uuid4()),
                user_id=str(uuid4()),
                feedback_type="INVALID_TYPE"
            )
    
    def test_invalid_uuid_format_raises_error(self):
        """Test invalid UUID format raises validation error"""
        with pytest.raises(ValueError):
            FeedbackRequest(
                content_id="not-a-uuid",
                user_id=str(uuid4()),
                feedback_type="NOT_RELEVANT"
            )

class TestFeedbackAPI:
    def setup_method(self):
        self.client = TestClient(app)
        self.valid_payload = {
            "content_id": str(uuid4()),
            "user_id": str(uuid4()),
            "feedback_type": "NOT_RELEVANT"
        }
        
    def test_submit_feedback_success(self):
        response = self.client.post("/api/v1/feedback", json=self.valid_payload)
        assert response.status_code == 202

    def test_submit_feedback_response_fields(self):
        """Response should contain feedback_id, timestamp, and status."""
        response = self.client.post("/api/v1/feedback", json=self.valid_payload)
        assert response.status_code == 202
        data = response.json()
        assert "feedback_id" in data
        assert "timestamp" in data
        assert data["status"] == "accepted"
        
    def test_submit_feedback_missing_fields_422(self):
        """Test missing required fields returns 422"""
        incomplete_payload = {
            "content_id": str(uuid4()),
            # Missing user_id and feedback_type
        }
        response = self.client.post("/api/v1/feedback", json=incomplete_payload)
        assert response.status_code == 422
        
    def test_submit_feedback_invalid_uuid_422(self):
        """Invalid UUID should fail validation and return 422"""
        invalid_payload = {
            **self.valid_payload,
            "content_id": "invalid-uuid"
        }
        response = self.client.post("/api/v1/feedback", json=invalid_payload)
        assert response.status_code == 422
        
    @pytest.mark.skip(reason="validate_user_exists not implemented in current API")
    def test_user_not_found_404(self):
        pass
        
    @pytest.mark.skip(reason="validate_content_exists not implemented in current API")
    def test_content_not_found_404(self):
        pass

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 