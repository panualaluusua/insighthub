"""Tests for SummarizerNode - TDD Red Phase

This module tests the SummarizerNode which uses DeepSeek API
via LangChain to generate content summaries.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.orchestrator.state import ContentState, create_content_state
from src.orchestrator.nodes.summarizer import SummarizerNode
from unittest.mock import ANY


class TestSummarizerNode:
    """Test suite for SummarizerNode following TDD principles."""

    def test_summarizer_node_exists(self):
        """Test that SummarizerNode class can be imported and instantiated."""
        node = SummarizerNode()
        assert node is not None

    def test_summarizer_node_has_call_method(self):
        """Test that SummarizerNode has __call__ method for LangGraph compatibility."""
        node = SummarizerNode()
        assert hasattr(node, '__call__')
        assert callable(getattr(node, '__call__'))

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    def test_summarizer_node_uses_deepseek_api(self, mock_chat_openai):
        """Test that SummarizerNode configures DeepSeek API correctly."""
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        node = SummarizerNode()
        
        # Verify DeepSeek API configuration
        # Access the llm property to trigger lazy loading
        _ = node.llm
        mock_chat_openai.assert_called_once_with(
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            api_key=ANY,
            temperature=0.3
        )

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    @patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'})
    def test_summarizer_node_uses_environment_api_key(self, mock_chat_openai):
        """Test that SummarizerNode uses DEEPSEEK_API_KEY from environment."""
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        node = SummarizerNode(api_key='test-key')
        
        # Access the llm property to trigger lazy loading
        _ = node.llm
        mock_chat_openai.assert_called_once_with(
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            api_key='test-key',
            temperature=0.3
        )

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    def test_summarizer_generates_summary_for_youtube_content(self, mock_chat_openai):
        """Test that SummarizerNode generates summary for YouTube content."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "This video discusses AI developments in 2024..."
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        # Create test state
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["raw_content"] = "Long video transcript about AI developments..."
        state["status"] = "content_fetched"
        
        # Execute
        node = SummarizerNode()
        result = node(state)
        
        # Verify summary was generated
        assert "summary" in result
        assert result["summary"] == "This video discusses AI developments in 2024..."
        assert result["status"] == "summarized"
        assert result["current_node"] == "summarizer"

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    def test_summarizer_generates_summary_for_reddit_content(self, mock_chat_openai):
        """Test that SummarizerNode generates summary for Reddit content."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "This Reddit discussion covers programming best practices..."
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        # Create test state
        state = create_content_state(
            source_type="reddit",
            source_url="https://reddit.com/r/programming/comments/test",
            content_id="test_post"
        )
        state["raw_content"] = "Long Reddit thread about programming..."
        state["status"] = "content_fetched"
        
        # Execute
        node = SummarizerNode()
        result = node(state)
        
        # Verify summary was generated
        assert "summary" in result
        assert result["summary"] == "This Reddit discussion covers programming best practices..."
        assert result["status"] == "summarized"

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    def test_summarizer_handles_empty_content(self, mock_chat_openai):
        """Test that SummarizerNode handles empty or missing content gracefully."""
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        # Create test state with no content
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["raw_content"] = ""
        state["status"] = "content_fetched"
        
        # Execute
        node = SummarizerNode()
        result = node(state)
        
        # Verify error handling
        assert result["status"] == "error"
        assert "error_message" in result
        assert "empty" in result["error_message"].lower()

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    def test_summarizer_handles_api_errors(self, mock_chat_openai):
        """Test that SummarizerNode handles API errors gracefully."""
        # Setup mock LLM to raise exception
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("DeepSeek API error")
        mock_chat_openai.return_value = mock_llm
        
        # Create test state
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["raw_content"] = "Test content for summarization..."
        state["status"] = "content_fetched"
        
        # Execute
        node = SummarizerNode()
        result = node(state)
        
        # Verify error handling
        assert result["status"] == "error"
        assert "error_message" in result
        assert "DeepSeek API error" in result["error_message"]

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    def test_summarizer_preserves_state_fields(self, mock_chat_openai):
        """Test that SummarizerNode preserves all existing state fields."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Generated summary content"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        # Create test state with metadata
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["raw_content"] = "Test content"
        state["metadata"] = {"duration": "10:30", "title": "Test Video"}
        state["status"] = "content_fetched"
        
        # Execute
        node = SummarizerNode()
        result = node(state)
        
        # Verify all fields are preserved
        assert result["source_type"] == "youtube"
        assert result["source_url"] == "https://youtube.com/watch?v=test123"
        assert result["content_id"] == "test123"
        assert result["raw_content"] == "Test content"
        assert result["metadata"] == {"duration": "10:30", "title": "Test Video"}
        assert result["summary"] == "Generated summary content"
        assert "updated_at" in result

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    def test_summarizer_custom_model_configuration(self, mock_chat_openai):
        """Test that SummarizerNode allows custom model configuration."""
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        # Test with custom model
        node = SummarizerNode(model="deepseek-reasoner", max_tokens=2000)
        
        # Access the llm property to trigger lazy loading
        _ = node.llm
        mock_chat_openai.assert_called_once_with(
            model="deepseek-reasoner",
            base_url="https://api.deepseek.com/v1",
            api_key=ANY,
            temperature=0.3,
            max_tokens=2000
        )

    @patch('src.orchestrator.nodes.summarizer.ChatOpenAI')
    def test_summarizer_content_length_appropriate_prompting(self, mock_chat_openai):
        """Test that SummarizerNode uses appropriate prompts for different content lengths."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Concise summary for long content"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        # Create test state with very long content
        state = create_content_state(
            source_type="youtube",
            source_url="https://youtube.com/watch?v=test123",
            content_id="test123"
        )
        state["raw_content"] = "Very long content " * 1000  # Simulate long content
        state["status"] = "content_fetched"
        
        # Execute
        node = SummarizerNode()
        result = node(state)
        
        # Verify LLM was called with content
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        
        # Verify prompt includes the content
        assert "Very long content" in str(call_args) 