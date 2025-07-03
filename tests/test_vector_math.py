"""
Test suite for vector mathematics module (TDD - Tests First!)
Tests for src/models/vector_math.py user profile vector update system

Based on KÄYTTÄJÄPROFIILI_JA_PALAUTEMEKANISMIN_TOTEUTUS.md specifications
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from typing import Optional

# These imports will fail initially - that's the TDD Red phase!
try:
    from src.models.vector_math import (
        FeedbackType,
        WeightConfig, 
        UserProfileVectorManager,
        update_and_normalize_vector,
        project_vector,
        calculate_feedback_weight
    )
except ImportError:
    # Expected during TDD Red phase
    pass

pytest.skip("Legacy vector_math tests superseded by new projection tests", allow_module_level=True)

class TestFeedbackType:
    """Test FeedbackType enum - will fail until implemented"""
    
    def test_feedback_type_enum_values(self):
        """Test that all required feedback types exist"""
        from src.models.vector_math import FeedbackType
        
        assert FeedbackType.LIKE.value == "LIKE"
        assert FeedbackType.HIDE.value == "HIDE"
        assert FeedbackType.NOT_RELEVANT.value == "NOT_RELEVANT"
        assert FeedbackType.NOT_NOW.value == "NOT_NOW"
        assert FeedbackType.TOO_SUPERFICIAL.value == "TOO_SUPERFICIAL"
        assert FeedbackType.TOO_ADVANCED.value == "TOO_ADVANCED"


class TestWeightConfig:
    """Test WeightConfig dataclass"""
    
    def test_default_weights(self):
        """Test default weight values match specification"""
        config = WeightConfig()
        assert config.LIKE_WEIGHT == 0.10
        assert config.HIDE_WEIGHT == -0.15
        assert config.NOT_RELEVANT_WEIGHT == -0.15
        assert config.NOT_NOW_WEIGHT == -0.05
        assert config.TOO_SUPERFICIAL_WEIGHT == -0.08
        assert config.TOO_ADVANCED_WEIGHT == -0.08
    
    def test_custom_weights(self):
        """Test custom weight configuration"""
        config = WeightConfig(LIKE_WEIGHT=0.20, HIDE_WEIGHT=-0.25)
        assert config.LIKE_WEIGHT == 0.20
        assert config.HIDE_WEIGHT == -0.25


class TestUpdateAndNormalizeVector:
    """Test core vector update function: v_new = normalize(v_old + (w * v_content))"""
    
    def test_positive_weight_update(self):
        """Test vector update with positive weight (LIKE feedback)"""
        from src.models.vector_math import update_and_normalize_vector
        
        old_vector = np.array([0.6, 0.8])  # Normalized
        content_vector = np.array([1.0, 0.0])  # Normalized
        weight = 0.10
        
        result = update_and_normalize_vector(old_vector, content_vector, weight)
        
        # Result should be normalized
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6
        # Should move towards content vector
        assert result[0] > old_vector[0]  # First component should increase
    
    def test_negative_weight_update(self):
        """Test vector update with negative weight (HIDE feedback)"""
        old_vector = np.array([0.6, 0.8])
        content_vector = np.array([1.0, 0.0])
        weight = -0.15
        
        result = update_and_normalize_vector(old_vector, content_vector, weight)
        
        # Result should be normalized
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6
        # Should move away from content vector
        assert result[0] < old_vector[0]  # First component should decrease
    
    def test_zero_vector_handling(self):
        """Test handling of zero vectors after update"""
        old_vector = np.array([1.0, 0.0])
        content_vector = np.array([1.0, 0.0])
        weight = -1.0  # This creates zero vector: [1,0] + (-1)*[1,0] = [0,0]
        
        result = update_and_normalize_vector(old_vector, content_vector, weight)
        
        # Should return zero vector when norm is zero
        assert np.allclose(result, np.array([0.0, 0.0]))
    
    def test_dimension_compatibility(self):
        """Test that vectors must have same dimensions"""
        old_vector = np.array([0.6, 0.8])
        content_vector = np.array([1.0, 0.0, 0.0])  # Different dimension
        weight = 0.10
        
        with pytest.raises(ValueError):
            update_and_normalize_vector(old_vector, content_vector, weight)
    
    def test_input_type_conversion(self):
        """Test automatic conversion of input types to numpy arrays"""
        old_vector = [0.6, 0.8]  # Python list
        content_vector = (1.0, 0.0)  # Tuple
        weight = 0.10
        
        result = update_and_normalize_vector(old_vector, content_vector, weight)
        
        assert isinstance(result, np.ndarray)
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6


class TestProjectVector:
    """Test vector projection function for advanced feedback types"""
    
    def test_basic_projection(self):
        """Test basic vector projection"""
        v_to_project = np.array([2.0, 1.0])
        v_target = np.array([1.0, 0.0])
        
        result = project_vector(v_to_project, v_target)
        expected = np.array([2.0, 0.0])  # Projection onto x-axis
        
        assert np.allclose(result, expected)
    
    def test_orthogonal_projection(self):
        """Test projection of orthogonal vectors"""
        v_to_project = np.array([0.0, 1.0])
        v_target = np.array([1.0, 0.0])
        
        result = project_vector(v_to_project, v_target)
        expected = np.array([0.0, 0.0])  # Zero projection
        
        assert np.allclose(result, expected)
    
    def test_zero_target_vector(self):
        """Test projection onto zero vector should raise error"""
        v_to_project = np.array([1.0, 1.0])
        v_target = np.array([0.0, 0.0])
        
        with pytest.raises(ValueError):
            project_vector(v_to_project, v_target)


class TestCalculateFeedbackWeight:
    """Test feedback weight calculation function"""
    
    def test_standard_feedback_weights(self):
        """Test standard feedback type weights"""
        config = WeightConfig()
        
        assert calculate_feedback_weight(FeedbackType.LIKE, config) == 0.10
        assert calculate_feedback_weight(FeedbackType.HIDE, config) == -0.15
        assert calculate_feedback_weight(FeedbackType.NOT_RELEVANT, config) == -0.15
        assert calculate_feedback_weight(FeedbackType.NOT_NOW, config) == -0.05
        assert calculate_feedback_weight(FeedbackType.TOO_SUPERFICIAL, config) == -0.08
        assert calculate_feedback_weight(FeedbackType.TOO_ADVANCED, config) == -0.08


class TestUserProfileVectorManager:
    """Test main UserProfileVectorManager class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = UserProfileVectorManager()
        self.user_id = "test-user-123"
        self.content_id = "test-content-456"
        self.initial_vector = np.array([0.6, 0.8])
        self.content_vector = np.array([1.0, 0.0])
    
    def test_initialization(self):
        """Test manager initialization"""
        assert isinstance(self.manager.weight_config, WeightConfig)
        assert hasattr(self.manager, 'update_user_profile')
        assert hasattr(self.manager, 'process_feedback')
    
    @patch('src.models.vector_math.get_user_vector_from_db')
    @patch('src.models.vector_math.get_content_vector_from_db')
    @patch('src.models.vector_math.save_user_vector_to_db')
    def test_like_feedback_processing(self, mock_save, mock_get_content, mock_get_user):
        """Test LIKE feedback processing"""
        mock_get_user.return_value = self.initial_vector
        mock_get_content.return_value = self.content_vector
        
        result = self.manager.process_feedback(
            self.user_id, 
            self.content_id, 
            FeedbackType.LIKE
        )
        
        # Should call database functions
        mock_get_user.assert_called_once_with(self.user_id)
        mock_get_content.assert_called_once_with(self.content_id)
        mock_save.assert_called_once()
        
        # Result should be normalized and moved towards content
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6
        assert result[0] > self.initial_vector[0]
    
    @patch('src.models.vector_math.get_user_vector_from_db')
    @patch('src.models.vector_math.get_content_vector_from_db')
    @patch('src.models.vector_math.get_topic_prototype_vector')
    @patch('src.models.vector_math.save_user_vector_to_db')
    def test_too_superficial_feedback(self, mock_save, mock_prototype, mock_get_content, mock_get_user):
        """Test TOO_SUPERFICIAL feedback with vector projection"""
        mock_get_user.return_value = self.initial_vector
        mock_get_content.return_value = self.content_vector
        mock_prototype.return_value = np.array([0.8, 0.6])  # Prototype vector
        
        result = self.manager.process_feedback(
            self.user_id,
            self.content_id,
            FeedbackType.TOO_SUPERFICIAL
        )
        
        # Should use prototype vector for projection
        mock_prototype.assert_called_once_with(self.content_id)
        mock_save.assert_called_once()
        
        # Result should be normalized
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6
    
    @patch('src.models.vector_math.get_user_vector_from_db')
    @patch('src.models.vector_math.get_content_vector_from_db')
    @patch('src.models.vector_math.get_topic_prototype_vector')
    @patch('src.models.vector_math.save_user_vector_to_db')
    def test_too_advanced_feedback(self, mock_save, mock_prototype, mock_get_content, mock_get_user):
        """Test TOO_ADVANCED feedback with specific component reduction"""
        mock_get_user.return_value = self.initial_vector
        mock_get_content.return_value = self.content_vector
        mock_prototype.return_value = np.array([0.8, 0.6])
        
        result = self.manager.process_feedback(
            self.user_id,
            self.content_id,
            FeedbackType.TOO_ADVANCED
        )
        
        # Should calculate specific component (content - general)
        mock_prototype.assert_called_once_with(self.content_id)
        mock_save.assert_called_once()
        
        # Result should be normalized
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6
    
    def test_invalid_feedback_type(self):
        """Test handling of invalid feedback type"""
        with pytest.raises(ValueError):
            self.manager.process_feedback(
                self.user_id,
                self.content_id,
                "INVALID_TYPE"
            )
    
    @patch('src.models.vector_math.get_user_vector_from_db')
    def test_user_not_found(self, mock_get_user):
        """Test handling when user vector not found"""
        mock_get_user.return_value = None
        
        with pytest.raises(ValueError, match="User vector not found"):
            self.manager.process_feedback(
                "nonexistent-user",
                self.content_id,
                FeedbackType.LIKE
            )
    
    @patch('src.models.vector_math.get_user_vector_from_db')
    @patch('src.models.vector_math.get_content_vector_from_db')
    def test_content_not_found(self, mock_get_content, mock_get_user):
        """Test handling when content vector not found"""
        mock_get_user.return_value = self.initial_vector
        mock_get_content.return_value = None
        
        with pytest.raises(ValueError, match="Content vector not found"):
            self.manager.process_feedback(
                self.user_id,
                "nonexistent-content",
                FeedbackType.LIKE
            )


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_very_small_vectors(self):
        """Test handling of very small vectors near zero"""
        old_vector = np.array([1e-10, 1e-10])
        content_vector = np.array([1.0, 0.0])
        weight = 0.10
        
        result = update_and_normalize_vector(old_vector, content_vector, weight)
        
        # Should handle tiny vectors gracefully
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6
    
    def test_large_weight_values(self):
        """Test handling of unusually large weight values"""
        old_vector = np.array([0.6, 0.8])
        content_vector = np.array([1.0, 0.0])
        weight = 10.0  # Very large weight
        
        result = update_and_normalize_vector(old_vector, content_vector, weight)
        
        # Should still normalize correctly
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6
    
    def test_high_dimensional_vectors(self):
        """Test with high-dimensional vectors (e.g., 512-dim embeddings)"""
        dimensions = 512
        old_vector = np.random.rand(dimensions)
        old_vector = old_vector / np.linalg.norm(old_vector)
        
        content_vector = np.random.rand(dimensions)
        content_vector = content_vector / np.linalg.norm(content_vector)
        
        weight = 0.10
        
        result = update_and_normalize_vector(old_vector, content_vector, weight)
        
        # Should handle high dimensions
        assert len(result) == dimensions
        assert abs(np.linalg.norm(result) - 1.0) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 